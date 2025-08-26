
# GEMINI.md

## Project Overview

This project is a comprehensive water infrastructure monitoring and analysis system for Abbanoa S.p.A. It is designed to collect, process, and visualize data from various sources to provide insights into water consumption, detect anomalies, and monitor the overall health of the water network.

The system is built with a service-oriented architecture and leverages a modern technology stack:

*   **Backend:** The backend is developed in Python, using FastAPI for the API and a separate service for data processing. It utilizes Poetry for dependency management and follows Domain-Driven Design (DDD) principles.
*   **Frontend:** The user-facing dashboard is a Next.js (React) application, providing an interactive interface for data visualization and analysis.
*   **Database:** The primary database is PostgreSQL, likely with the TimescaleDB extension for handling time-series data. Redis is used for caching to improve performance.
*   **Infrastructure:** The entire system is containerized using Docker, with separate configurations for development, production, and individual services. It is designed for deployment on the Google Cloud Platform (GCP), with support for Google Kubernetes Engine (GKE) and BigQuery for large-scale data analysis.

## Building and Running

### Prerequisites

*   Docker
*   Docker Compose
*   Python 3.12+
*   Node.js (for frontend development)
*   Poetry (for Python dependency management)

### Backend

**Running the API:**

```bash
# Start the API using Docker Compose
docker-compose -f docker-compose.api-only.yml up -d
```

**Running the Processing Service:**

```bash
# Start the processing service using Docker Compose
docker-compose -f docker-compose.processing.yml up -d
```

### Frontend

**Running the Dashboard:**

```bash
# Start the dashboard using Docker Compose
docker-compose -f docker-compose.dev.yml up -d
```

Or, for local development:

```bash
cd frontend
npm install
npm run dev
```

### Testing

**Running Backend Tests:**

```bash
# Run the backend tests using poetry
poetry run pytest
```

**Running Frontend Tests:**

```bash
cd frontend
npm test
```

## Development Conventions

*   **Code Style:** The Python code follows the Black code style, with isort for import sorting.
*   **Type Checking:** Mypy is used for static type checking in the Python codebase.
*   **Linting:** Pylint and flake8 are used for linting the Python code.
*   **Pre-commit Hooks:** The project uses pre-commit hooks to enforce code quality standards before committing code.
*   **API Documentation:** The API is documented using the OpenAPI standard, and the documentation can be accessed at `/docs` when the API is running.
*   **Contribution Guidelines:** (TODO: Add information on contribution guidelines if available)
