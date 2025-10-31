.PHONY: help build run stop lint fmt test clean install dev-install

help:
	@echo "ml-api — FastAPI Iris Classifier"
	@echo ""
	@echo "Available targets:"
	@echo "  make install       Install dependencies from requirements.txt"
	@echo "  make dev-install   Install dependencies + dev tools (pytest, ruff)"
	@echo "  make build         Build Docker image (ml-api:latest)"
	@echo "  make run           Run Docker container on port 8000"
	@echo "  make stop          Stop and remove running container"
	@echo "  make lint          Run ruff linter"
	@echo "  make fmt           Format code with ruff"
	@echo "  make test          Run pytest tests"
	@echo "  make clean         Remove __pycache__, .pytest_cache, *.pyc"
	@echo ""
	@echo "Quick start (WSL):"
	@echo "  make dev-install && make test && make build && make run"
	@echo "  Then: curl -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' \\"
	@echo "        -d '{\"sepal_length\":6.1,\"sepal_width\":2.8,\"petal_length\":4.7,\"petal_width\":1.2}'"

install:
	pip install --upgrade pip
	pip install -r app/requirements.txt

dev-install: install
	pip install pytest pytest-asyncio httpx ruff

build:
	docker build -t ml-api:latest ./app -f app/Dockerfile

run:
	docker run --rm -p 8000:8000 --name ml-api-container ml-api:latest

stop:
	docker stop ml-api-container 2>/dev/null || true
	docker rm ml-api-container 2>/dev/null || true

lint:
	ruff check app/ tests/ predict_demo.py

fmt:
	ruff format app/ tests/ predict_demo.py
	ruff check --fix app/ tests/ predict_demo.py

test:
	pytest tests/ -v --tb=short

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .ruff_cache

