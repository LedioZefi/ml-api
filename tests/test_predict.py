"""Tests for /predict endpoint."""


class TestPredictEndpoint:
    """Test suite for /predict endpoint."""

    def test_predict_valid_setosa(self, client):
        """Test prediction for Iris setosa."""
        payload = {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["predicted_class"] == "setosa"
        assert data["class_index"] == 0
        assert 0 <= data["confidence"] <= 1
        assert "probabilities" in data
        assert len(data["probabilities"]) == 3

    def test_predict_valid_versicolor(self, client):
        """Test prediction for Iris versicolor."""
        payload = {
            "sepal_length": 5.9,
            "sepal_width": 3.0,
            "petal_length": 4.2,
            "petal_width": 1.5,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["predicted_class"] == "versicolor"
        assert data["class_index"] == 1
        assert 0 <= data["confidence"] <= 1

    def test_predict_valid_virginica(self, client):
        """Test prediction for Iris virginica."""
        payload = {
            "sepal_length": 6.3,
            "sepal_width": 3.3,
            "petal_length": 6.0,
            "petal_width": 2.5,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["predicted_class"] == "virginica"
        assert data["class_index"] == 2
        assert 0 <= data["confidence"] <= 1

    def test_predict_response_structure(self, client):
        """Test that /predict response has expected structure."""
        payload = {
            "sepal_length": 5.5,
            "sepal_width": 3.0,
            "petal_length": 1.3,
            "petal_width": 0.2,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "predicted_class" in data
        assert "class_index" in data
        assert "confidence" in data
        assert "probabilities" in data
        assert isinstance(data["predicted_class"], str)
        assert isinstance(data["class_index"], int)
        assert isinstance(data["confidence"], float)
        assert isinstance(data["probabilities"], dict)

    def test_predict_probabilities_sum_to_one(self, client):
        """Test that probabilities sum to approximately 1.0."""
        payload = {
            "sepal_length": 5.8,
            "sepal_width": 2.7,
            "petal_length": 5.1,
            "petal_width": 1.9,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        prob_sum = sum(data["probabilities"].values())
        assert abs(prob_sum - 1.0) < 0.01

    def test_predict_missing_field(self, client):
        """Test that missing required field returns 422."""
        payload = {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            # missing petal_width
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422

    def test_predict_invalid_type(self, client):
        """Test that invalid type returns 422."""
        payload = {
            "sepal_length": "not_a_number",
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422

    def test_predict_negative_value(self, client):
        """Test that negative value returns 422 (gt=0 validation)."""
        payload = {
            "sepal_length": -5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422

    def test_predict_zero_value(self, client):
        """Test that zero value returns 422 (gt=0 validation)."""
        payload = {
            "sepal_length": 0.0,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422

    def test_predict_out_of_range_length(self, client):
        """Test that out-of-range length returns 422."""
        payload = {
            "sepal_length": 15.0,  # > 10 cm
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422

    def test_predict_out_of_range_width(self, client):
        """Test that out-of-range width returns 422."""
        payload = {
            "sepal_length": 5.1,
            "sepal_width": 0.05,  # < 0.1 cm
            "petal_length": 1.4,
            "petal_width": 0.2,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422

    def test_predict_all_classes_have_probabilities(self, client):
        """Test that all three classes have probabilities."""
        payload = {
            "sepal_length": 5.5,
            "sepal_width": 3.0,
            "petal_length": 1.3,
            "petal_width": 0.2,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "setosa" in data["probabilities"]
        assert "versicolor" in data["probabilities"]
        assert "virginica" in data["probabilities"]

    def test_predict_request_id_header(self, client):
        """Test that X-Request-ID header is returned."""
        payload = {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers


class TestPredictBatchEndpoint:
    """Test suite for /predict-batch endpoint."""

    def test_predict_batch_valid(self, client):
        """Test batch prediction with multiple samples."""
        batch = {
            "items": [
                {
                    "sepal_length": 5.1,
                    "sepal_width": 3.5,
                    "petal_length": 1.4,
                    "petal_width": 0.2,
                },
                {
                    "sepal_length": 5.9,
                    "sepal_width": 3.0,
                    "petal_length": 4.2,
                    "petal_width": 1.5,
                },
                {
                    "sepal_length": 6.3,
                    "sepal_width": 3.3,
                    "petal_length": 6.0,
                    "petal_width": 2.5,
                },
            ]
        }
        response = client.post("/predict-batch", json=batch)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "count" in data
        assert data["count"] == 3
        assert len(data["items"]) == 3
        assert data["items"][0]["predicted_class"] == "setosa"
        assert data["items"][1]["predicted_class"] == "versicolor"
        assert data["items"][2]["predicted_class"] == "virginica"

    def test_predict_batch_empty_list(self, client):
        """Test batch prediction with empty list."""
        batch = {"items": []}
        response = client.post("/predict-batch", json=batch)
        assert response.status_code == 400
        data = response.json()
        assert "Empty list not allowed" in data["detail"]

    def test_predict_batch_single_item(self, client):
        """Test batch prediction with single item."""
        batch = {
            "items": [
                {
                    "sepal_length": 5.1,
                    "sepal_width": 3.5,
                    "petal_length": 1.4,
                    "petal_width": 0.2,
                }
            ]
        }
        response = client.post("/predict-batch", json=batch)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["items"]) == 1

    def test_predict_batch_response_structure(self, client):
        """Test batch response structure."""
        batch = {
            "items": [
                {
                    "sepal_length": 5.1,
                    "sepal_width": 3.5,
                    "petal_length": 1.4,
                    "petal_width": 0.2,
                }
            ]
        }
        response = client.post("/predict-batch", json=batch)
        assert response.status_code == 200
        data = response.json()
        item = data["items"][0]
        assert "predicted_class" in item
        assert "class_index" in item
        assert "confidence" in item
        assert "probabilities" in item


class TestMetricsEndpoint:
    """Test suite for /metrics endpoint."""

    def test_metrics_endpoint_returns_prometheus_format(self, client):
        """Test that /metrics returns Prometheus format."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")
        content = response.text
        assert "pred_requests_total" in content
        assert "HELP" in content or "TYPE" in content

