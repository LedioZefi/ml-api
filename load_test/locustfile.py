"""Load testing script for ml-api using Locust."""
from locust import HttpUser, task, between


class IrisAPIUser(HttpUser):
    """Simulated user for load testing the Iris API."""

    wait_time = between(1, 3)

    @task(3)
    def predict_single(self):
        """Test single prediction endpoint."""
        payload = {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        }
        self.client.post("/predict", json=payload)

    @task(1)
    def predict_batch(self):
        """Test batch prediction endpoint."""
        payloads = [
            {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2,
            },
            {
                "sepal_length": 7.0,
                "sepal_width": 3.2,
                "petal_length": 4.7,
                "petal_width": 1.4,
            },
            {
                "sepal_length": 6.3,
                "sepal_width": 3.3,
                "petal_length": 6.0,
                "petal_width": 2.5,
            },
        ]
        self.client.post("/predict-batch", json=payloads)

    @task(1)
    def health_check(self):
        """Test health endpoint."""
        self.client.get("/health")

    @task(1)
    def metrics(self):
        """Test metrics endpoint."""
        self.client.get("/metrics")

