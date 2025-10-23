# NS.Gifts API Client - Development Makefile

.PHONY: help install dev-install test lint format clean docker-build docker-run docker-clean

help:
	@echo "Available commands:"
	@echo "  install       - Install package dependencies"
	@echo "  dev-install   - Install development dependencies"
	@echo "  test          - Run tests"
	@echo "  lint          - Run linting checks"
	@echo "  format        - Format code with black and isort"
	@echo "  clean         - Clean build artifacts"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-run    - Run Docker container"
	@echo "  docker-clean  - Clean Docker images and containers"

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	flake8 nsgifts_api/ tests/
	isort --check-only nsgifts_api/ tests/

format:
	black nsgifts_api/ tests/
	isort nsgifts_api/ tests/

clean:
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker build -t nsgifts-api .

docker-run:
	docker run --rm -it nsgifts-api

docker-clean:
	docker rmi nsgifts-api 2>/dev/null || true
	docker system prune -f
