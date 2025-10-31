import logging
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import numpy as np
from fastapi import Body, FastAPI, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.logging_config import add_request_id_middleware, configure_logging
from app.schemas.predict_schema import (
    IrisBatchRequest,
    IrisBatchResponse,
    IrisRequest,
    IrisResponse,
)

# Configure logging before app initialization
configure_logging()
logger = logging.getLogger(__name__)

APP_ROOT = Path(__file__).resolve().parent
MODEL_PATH = APP_ROOT / "model" / "model.pkl"

# Prometheus metrics
PRED_REQUESTS = Counter(
    "pred_requests_total",
    "Total number of /predict requests",
    ["endpoint"],
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


class ModelBundle(BaseModel):
    model_version: str
    target_names: list[str]


sk_model = None
meta = ModelBundle.model_validate({
    "model_version": "iris-logreg-v1",
    "target_names": ["setosa", "versicolor", "virginica"],
})

@asynccontextmanager
async def lifespan(app: FastAPI):
    global sk_model
    try:
        sk_model = joblib.load(MODEL_PATH)
        logger.info("Model loaded successfully at startup")
    except Exception as e:
        logger.error(f"Failed to load model at startup: {e}")
        raise RuntimeError(f"Failed to load model at startup: {e}") from e
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title="Iris ML Model Deployment API",
    description="FastAPI service that serves a scikit-learn Iris classifier.",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Add request ID middleware
app.middleware("http")(add_request_id_middleware)

@app.get("/health")
async def health():
    if sk_model is None:
        return {"status": "degraded", "detail": "model not loaded"}
    return {"status": "ok", "model_version": meta.model_version}


@app.get("/metrics")
async def metrics():
    """Return Prometheus metrics in text format."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def _predict_single(payload: IrisRequest) -> IrisResponse:
    """Helper function to predict on a single sample."""
    if sk_model is None:
        raise HTTPException(status_code=503, detail="Model not ready")
    try:
        X = np.array(
            [
                [
                    payload.sepal_length,
                    payload.sepal_width,
                    payload.petal_length,
                    payload.petal_width,
                ]
            ],
            dtype=float,
        )
        proba = sk_model.predict_proba(X)[0]
        idx = int(np.argmax(proba))
        return IrisResponse(
            predicted_class=meta.target_names[idx],
            class_index=idx,
            confidence=float(proba[idx]),
            probabilities={
                name: float(p)
                for name, p in zip(meta.target_names, proba, strict=True)
            },
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {e}") from e


@app.post("/predict", response_model=IrisResponse)
@limiter.limit("10/minute")
async def predict(
    request: Request, payload: IrisRequest = Body(...)  # noqa: B008
):
    """Predict Iris class for a single sample."""
    PRED_REQUESTS.labels(endpoint="predict").inc()
    return _predict_single(payload)


@app.post("/predict-batch", response_model=IrisBatchResponse)
@limiter.limit("10/minute")
async def predict_batch(
    request: Request, batch: IrisBatchRequest = Body(...)  # noqa: B008
):
    """Predict Iris class for multiple samples in batch."""
    payloads = batch.items
    if not payloads:
        raise HTTPException(status_code=400, detail="Empty list not allowed")
    if len(payloads) > 1000:
        raise HTTPException(
            status_code=400, detail="Batch size exceeds maximum of 1000"
        )

    PRED_REQUESTS.labels(endpoint="predict-batch").inc()
    results = [_predict_single(payload) for payload in payloads]
    return IrisBatchResponse(items=results, count=len(results))
