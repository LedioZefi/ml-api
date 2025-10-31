# ml-api — Production-Ready ML Model Deployment

[![CI/CD](https://github.com/LedioZefi/ml-api/actions/workflows/ci.yml/badge.svg)](https://github.com/LedioZefi/ml-api/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A production-ready FastAPI service for deploying machine learning models. This project demonstrates best practices for ML model serving with structured logging, batch inference, Prometheus metrics, rate limiting, and comprehensive testing.

**Tech Stack**: FastAPI • scikit-learn • Docker • Prometheus • Pydantic v2

## Features

✨ **Single & Batch Predictions** — Serve one prediction or hundreds at once  
📊 **Prometheus Metrics** — Monitor API usage and performance  
🔐 **Rate Limiting** — Protect your API (10 req/min per endpoint)  
📝 **Structured Logging** — JSON logs with request ID tracking for debugging  
✅ **Comprehensive Tests** — 20 tests covering all endpoints and edge cases  
🚀 **CI/CD Pipeline** — Automated testing and Docker image publishing  
⚡ **Load Testing** — Locust scaffold for performance validation  

## Quick Start

### Prerequisites
- WSL 2 with Python 3.11+ (or any Linux environment)
- Docker Desktop
- Git

### Get Running in 5 Minutes

```bash
# Clone and enter the project
git clone https://github.com/LedioZefi/ml-api.git
cd ml-api

# Install dependencies
make dev-install

# Run tests (should see 20/20 passing)
make test

# Build Docker image
make build

# Start the API
make run

# In another terminal, make a prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":6.1,"sepal_width":2.8,"petal_length":4.7,"petal_width":1.2}'

# Check metrics
curl http://localhost:8000/metrics

# Stop the container
make stop
```

## API Endpoints

### GET /health
Quick health check. Tells you if the model is loaded and ready.

```bash
curl http://localhost:8000/health
```

### POST /predict
Make a single prediction. Send iris measurements, get back the predicted class and confidence.

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":6.1,"sepal_width":2.8,"petal_length":4.7,"petal_width":1.2}'
```

Response:
```json
{
  "predicted_class": "versicolor",
  "class_index": 1,
  "confidence": 0.92,
  "probabilities": {"setosa": 0.01, "versicolor": 0.92, "virginica": 0.07}
}
```

### POST /predict-batch
Make multiple predictions in one request. Great for batch processing.

```bash
curl -X POST http://localhost:8000/predict-batch \
  -H "Content-Type: application/json" \
  -d '{"items": [
    {"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2},
    {"sepal_length":7.0,"sepal_width":3.2,"petal_length":4.7,"petal_width":1.4}
  ]}'
```

Response:
```json
{
  "items": [
    {"predicted_class": "setosa", "class_index": 0, "confidence": 0.98, ...},
    {"predicted_class": "versicolor", "class_index": 1, "confidence": 0.85, ...}
  ],
  "count": 2
}
```

### GET /metrics
Prometheus metrics for monitoring. Scrape this endpoint with Prometheus.

```bash
curl http://localhost:8000/metrics
```

## Project Structure

```
ml-api/
├── .github/workflows/ci.yml    # Automated testing & Docker publishing
├── app/
│   ├── main.py                 # FastAPI app (logging, metrics, rate limiting)
│   ├── logging_config.py       # JSON logging & request ID tracking
│   ├── requirements.txt         # Dependencies
│   ├── Dockerfile              # Multi-stage build with model training
│   ├── model/                  # Trained model (auto-generated)
│   └── schemas/predict_schema.py # Pydantic v2 validation
├── tests/
│   ├── test_health.py          # Health endpoint tests
│   ├── test_predict.py         # Prediction endpoint tests (20 total)
│   └── conftest.py             # Pytest fixtures
├── load_test/
│   ├── locustfile.py           # Load testing scenarios
│   └── README.md               # Load testing guide
├── Makefile                    # Quick commands
├── pyproject.toml              # Project config & ruff linting
├── predict_demo.py             # Demo script
└── README.md                   # This file
```

## Development

### Makefile Commands

```bash
make help          # Show all commands
make install       # Install dependencies
make dev-install   # Install + dev tools (pytest, ruff)
make build         # Build Docker image
make run           # Run container on port 8000
make stop          # Stop and remove container
make lint          # Run ruff linter
make fmt           # Format code with ruff
make test          # Run pytest tests
make clean         # Remove cache files
```

### Running Tests Locally

```bash
source .venv/bin/activate
pytest tests/ -v
```

### Code Quality

```bash
ruff check app/ tests/ predict_demo.py
ruff format app/ tests/ predict_demo.py
```

## Docker

### Build Image
```bash
docker build -t ml-api:latest ./app -f app/Dockerfile
```

### Run Container
```bash
docker run -d -p 8000:8000 --name ml-api ml-api:latest
```

### View Logs
```bash
docker logs -f ml-api
```

## Deployment

### GitHub Container Registry (GHCR)

Tag a release and push to automatically build and publish:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will automatically:
- Run tests
- Build Docker image
- Push to `ghcr.io/LedioZefi/ml-api:v1.0.0` and `latest`

Pull the image:
```bash
docker pull ghcr.io/LedioZefi/ml-api:v1.0.0
```

## Load Testing

Use Locust to simulate realistic load:

```bash
pip install locust
locust -f load_test/locustfile.py --host=http://localhost:8000
# Open http://localhost:8089 in your browser
```

## Rate Limiting

- **Limit**: 10 requests per minute per client IP
- **Applies to**: `/predict` and `/predict-batch`
- **Exceeding**: Returns 429 Too Many Requests

## Monitoring

### Request ID Tracking

All requests get a unique ID for tracing:

```bash
curl -X POST http://localhost:8000/predict \
  -H "X-Request-ID: my-custom-id" \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":6.1,"sepal_width":2.8,"petal_length":4.7,"petal_width":1.2}'
```

Response includes the ID:
```
X-Request-ID: my-custom-id
```

### Structured Logging

Logs are JSON-formatted for easy parsing:

```json
{"timestamp": "2024-01-15 10:30:45,123", "level": "INFO", "logger": "app.request", "message": "POST /predict 200"}
```

## Contributing

Found a bug or have an idea? Feel free to open an issue or submit a PR!

## License

MIT License — see LICENSE file for details

## Questions?

Check out the [PRODUCTION_FEATURES_SUMMARY.md](PRODUCTION_FEATURES_SUMMARY.md) for detailed implementation notes.

