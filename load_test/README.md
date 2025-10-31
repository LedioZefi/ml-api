# Load Testing with Locust

This directory contains load testing scripts for the ml-api using [Locust](https://locust.io/).

## Installation

Install Locust:

```bash
pip install locust>=2.0
```

## Running Load Tests

### Start the API

First, ensure the API is running:

```bash
# Using Docker
make run

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Run Locust

In another terminal, run Locust:

```bash
# Web UI (recommended)
locust -f load_test/locustfile.py -H http://127.0.0.1:8000

# Then open http://127.0.0.1:8089 in your browser
```

Or run headless:

```bash
# Headless mode: 10 users, spawn rate 2/sec, run for 60 seconds
locust -f load_test/locustfile.py -H http://127.0.0.1:8000 \
  --headless -u 10 -r 2 -t 60s
```

## Test Scenarios

The `locustfile.py` defines:

- **predict_single** (3x weight): Single prediction requests
- **predict_batch** (1x weight): Batch prediction requests (3 samples)
- **health_check** (1x weight): Health endpoint checks
- **metrics** (1x weight): Metrics endpoint checks

## Example Output

```
Type     Name                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|--------------------------------------------------------------|------------|---------|--------|--------|--------|--------|---------|----------
POST     /predict                                                         300        0 |     45      12     120     42 |   5.00        0.00
POST     /predict-batch                                                   100        0 |     52      15     140     48 |   1.67        0.00
GET      /health                                                          100        0 |     8       2      25      7  |   1.67        0.00
GET      /metrics                                                         100        0 |     12      3      35      10 |   1.67        0.00
--------|--------------------------------------------------------------|------------|---------|--------|--------|--------|--------|---------|----------
         Aggregated                                                       600        0 |     38      2      140     35 |  10.00        0.00
```

## Notes

- Adjust `-u` (number of users) and `-r` (spawn rate) based on your testing needs
- The rate limiter is set to 10 requests/minute per client, so distributed load testing may trigger 429 responses
- For production testing, consider using a load balancer or multiple API instances

