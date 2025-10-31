"""Pytest configuration and fixtures."""
from pathlib import Path

import joblib
import pytest
from fastapi.testclient import TestClient
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import app.main as main_module


@pytest.fixture(scope="session", autouse=True)
def train_model():
    """Train and save model before running tests."""
    model_dir = Path(__file__).parent.parent / "app" / "model"
    model_path = model_dir / "model.pkl"

    # Only train if model doesn't exist
    if not model_path.exists():
        model_dir.mkdir(parents=True, exist_ok=True)
        X, y = load_iris(return_X_y=True)
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=500))
        ])
        pipe.fit(X, y)
        joblib.dump(pipe, model_path)

    # Load model into app for testing
    main_module.sk_model = joblib.load(model_path)


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app."""
    return TestClient(main_module.app)

