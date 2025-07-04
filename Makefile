.PHONY: help install test lint format type-check security clean run-dashboard docs pre-commit setup-dev

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install dependencies with poetry
	poetry install

setup-dev: install  ## Setup development environment
	pre-commit install
	poetry run python -m pip install --upgrade pip

test:  ## Run all tests
	poetry run pytest

test-unit:  ## Run unit tests only
	poetry run pytest tests/unit -v

test-integration:  ## Run integration tests only
	poetry run pytest tests/integration -v

test-e2e:  ## Run end-to-end tests only
	poetry run pytest tests/e2e -v

test-coverage:  ## Run tests with coverage report
	poetry run pytest --cov=src --cov-report=html --cov-report=term

lint:  ## Run all linters
	poetry run flake8 src tests
	poetry run pylint src
	poetry run bandit -r src

format:  ## Format code with black and isort
	poetry run black src tests
	poetry run isort src tests

format-check:  ## Check code formatting without changes
	poetry run black --check src tests
	poetry run isort --check-only src tests

type-check:  ## Run type checking with mypy
	poetry run mypy src

security:  ## Run security checks
	poetry run bandit -r src
	poetry run safety check

clean:  ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

run-dashboard:  ## Run Streamlit dashboard
	poetry run streamlit run src/presentation/web/dashboard.py

docs:  ## Generate documentation
	poetry run sphinx-build -b html docs docs/_build/html

docs-serve:  ## Serve documentation locally
	cd docs/_build/html && python -m http.server

pre-commit:  ## Run pre-commit hooks on all files
	poetry run pre-commit run --all-files

update-deps:  ## Update dependencies
	poetry update

check-deps:  ## Check for dependency vulnerabilities
	poetry run safety check

build:  ## Build distribution packages
	poetry build

docker-build:  ## Build Docker image
	docker build -t abbanoa-water-infrastructure:latest .

docker-run:  ## Run Docker container
	docker run -p 8501:8501 abbanoa-water-infrastructure:latest

quality: format lint type-check security test  ## Run all quality checks

ci: quality  ## Run CI pipeline locally