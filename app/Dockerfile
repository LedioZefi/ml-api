# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends tini && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . ./app

# Build-time training to create app/model/model.pkl
RUN python - <<'PY'
from pathlib import Path
import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_iris(return_X_y=True)
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=500))
])
pipe.fit(X, y)
out = Path("app/model")
out.mkdir(parents=True, exist_ok=True)
joblib.dump(pipe, out / "model.pkl")
print("Saved: app/model/model.pkl")
PY

EXPOSE 8000
CMD ["/usr/bin/tini","--","uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
