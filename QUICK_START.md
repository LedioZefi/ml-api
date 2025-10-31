# Quick Start Guide - ml-api Production Features

## What's New

✅ **Structured Logging** - JSON logs with request ID tracking  
✅ **Batch Predictions** - `/predict-batch` endpoint for multiple samples  
✅ **Prometheus Metrics** - `/metrics` endpoint for monitoring  
✅ **Rate Limiting** - 10 requests/minute per endpoint  
✅ **CI/CD Pipeline** - GitHub Actions for testing and Docker image publishing  
✅ **Load Testing** - Locust scaffold for performance testing  

## Quick Test (Local)

```bash
# 1. Build Docker image
docker build -t ml-api:latest ./app -f app/Dockerfile

# 2. Run container
docker run -d -p 8000:8000 --name ml-api ml-api:latest

# 3. Test single prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'

# 4. Test batch prediction
curl -X POST http://localhost:8000/predict-batch \
  -H "Content-Type: application/json" \
  -d '{"items": [{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}]}'

# 5. Check metrics
curl http://localhost:8000/metrics

# 6. Stop container
docker stop ml-api && docker rm ml-api
```

## Test Results

```
✅ 20/20 tests passing
✅ Ruff linting clean
✅ Docker build successful
```

## File Changes Summary

| File | Status | Changes |
|------|--------|---------|
| app/main.py | Modified | +logging, +batch endpoint, +metrics, +rate limiting |
| app/logging_config.py | Created | Structured logging with request IDs |
| app/schemas/predict_schema.py | Modified | +IrisBatchRequest, +IrisBatchResponse |
| app/requirements.txt | Modified | +prometheus-client, +slowapi |
| .github/workflows/ci.yml | Created | GitHub Actions CI/CD pipeline |
| tests/test_predict.py | Modified | +9 new tests for batch/metrics |
| load_test/locustfile.py | Created | Load testing scaffold |
| load_test/README.md | Created | Load testing documentation |

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /health | GET | Health check |
| /predict | POST | Single prediction |
| /predict-batch | POST | Batch predictions |
| /metrics | GET | Prometheus metrics |
| /docs | GET | OpenAPI documentation |

## Rate Limits

- `/predict`: 10 requests/minute
- `/predict-batch`: 10 requests/minute
- Returns 429 when exceeded

## Deployment to GHCR

```bash
# Tag and push to GitHub Container Registry
git tag v1.0.0
git push origin v1.0.0
# GitHub Actions will automatically build and push to ghcr.io
```

## See Also

- `PRODUCTION_FEATURES_SUMMARY.md` - Detailed implementation notes
- `README.md` - Full documentation
- `load_test/README.md` - Load testing guide
