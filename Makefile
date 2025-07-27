# Makefile for MCP Moodle Course Creator

.PHONY: help install install-dev test test-unit test-integration test-e2e test-coverage test-html lint format clean run-server

# Default target
help:
	@echo "Available commands:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-e2e         Run end-to-end tests only"
	@echo "  test-coverage    Run tests with coverage report"
	@echo "  test-html        Run tests with HTML report"
	@echo "  test-fast        Run tests (skip slow ones)"
	@echo "  lint             Run code linting"
	@echo "  format           Format code with black and isort"
	@echo "  clean            Clean up generated files"
	@echo "  run-server       Run the MCP server"

# Installation
install:
	uv sync

install-dev: install
	uv pip install -r requirements-test.txt

# Testing
test:
	python test_runner.py

test-unit:
	python test_runner.py --unit

test-integration:
	python test_runner.py --integration

test-e2e:
	python test_runner.py --e2e

test-coverage:
	python test_runner.py --coverage

test-html:
	python test_runner.py --html --coverage

test-fast:
	python test_runner.py --fast

test-parallel:
	python test_runner.py --parallel

# Code quality
lint:
	@echo "Running flake8..."
	python -m flake8 --max-line-length=100 --ignore=E203,W503 .
	@echo "Running mypy..."
	python -m mypy --ignore-missing-imports .

format:
	@echo "Running black..."
	python -m black --line-length=100 .
	@echo "Running isort..."
	python -m isort --profile black .

# Utilities
clean:
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf test-reports/
	rm -rf .coverage
	rm -rf .mypy_cache/
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +

run-server:
	.venv/bin/python mcp_server.py

# Development workflow
dev-setup: install-dev
	@echo "Development environment ready!"
	@echo "Run 'make test' to run all tests"
	@echo "Run 'make run-server' to start the MCP server"

# CI/CD targets
ci-test: install-dev
	python test_runner.py --coverage --html --parallel

# Docker targets (if needed later)
docker-build:
	docker build -t mcp-moodle-server .

docker-test:
	docker run --rm mcp-moodle-server python test_runner.py