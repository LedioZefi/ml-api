"""Tests for /health endpoint."""


def test_health_endpoint_ok(client):
    """Test that /health returns 200 with model loaded."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_version" in data
    assert data["model_version"] == "iris-logreg-v1"


def test_health_endpoint_structure(client):
    """Test that /health response has expected structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
    assert isinstance(data["status"], str)

