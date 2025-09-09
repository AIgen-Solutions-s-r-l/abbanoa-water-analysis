# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🏗️ Stack Architecture & Deployment

### Software Stack
- **Backend**: Python 3.12 + FastAPI + SQLAlchemy + Pydantic
- **Frontend**: Next.js 15 + React 19 + TypeScript + Tailwind CSS
- **Databases**: 
  - PostgreSQL/TimescaleDB (transactional + time-series)
  - Google BigQuery (analytics warehouse)
  - Redis (caching & session management)
- **Infrastructure**:
  - PM2 (process management for local/VPS deployment)
  - Docker & Docker Compose (containerized deployment)
  - Nginx (reverse proxy)
  - Prometheus + Grafana (monitoring)

### Deployment Environments

#### 1. PM2 Configuration (Local/VPS)
Three PM2 configurations are available:

**ecosystem.config.js** (Main configuration):
- `abbanoa-frontend`: Next.js on port 3001
- `abbanoa-postgres-api`: SQLAlchemy server on port 8000

**pm2-backend.config.js**:
- Runs backend via `run-backend.sh` script
- Automatic restart with memory limits (1GB)
- Logs to `./logs/pm2-backend-*.log`

**pm2-frontend.config.js**:
- Next.js production on port 8502
- Backend URL: http://localhost:8000

#### 2. Docker Compose Environments

**Production Stack** (`docker-compose.prod.yml`):
```
Services:
├── postgres (TimescaleDB on port 5432)
├── redis (port 6379, 4GB max memory)
├── etl-scheduler (BigQuery → PostgreSQL sync)
├── etl-init (one-time data initialization)
├── api (FastAPI on port 8000)
├── frontend (Next.js on port 3000)
├── nginx (ports 80/443)
├── prometheus (port 9090)
└── grafana (port 3000)
```

**Development Stack** (`docker-compose.dev.yml`):
```
Hybrid setup:
├── postgres (TimescaleDB on port 5434)
├── redis (port 6379)
├── etl-scheduler (BigQuery sync)
├── etl-init (one-time setup)
└── nginx-dev (port 8080)
* Local FastAPI (port 8000) + Next.js (port 8502)
```

**API-Only Stack** (`docker-compose-api-only.yml`):
- Simplified setup for API development
- Uses Google Cloud application default credentials
- FastAPI on port 8000

**Processing Stack** (`docker-compose.processing.yml`):
- PostgreSQL/TimescaleDB (port 5434)
- Redis (port 6382)
- Dedicated processing service

### Service Components

#### Core Services
1. **API Server** (`src/presentation/api/app_postgres.py`)
   - Main FastAPI application
   - Endpoints: dashboard, anomalies, weather, network, forecasts, infrastructure, pressure zones
   - Real-time data from PostgreSQL/TimescaleDB

2. **SQLAlchemy Server** (`src/servers/sqlalchemy_server.py`)
   - Database-focused API server
   - Direct PostgreSQL/TimescaleDB integration

3. **Weather Server** (`src/servers/weather_server_prod.py`)
   - Dedicated weather data service
   - Production weather API integration

#### ETL & Processing
1. **ETL Scheduler** (`src/infrastructure/etl/etl_scheduler.py`)
   - Scheduled BigQuery → PostgreSQL synchronization
   - Runs as containerized service

2. **Cache Initializer** (`init_redis_cache.py`)
   - Pre-loads Redis cache with frequently accessed data
   - Runs during initialization phase

#### Monitoring & Observability
- **Prometheus**: Metrics collection (port 9090)
- **Grafana**: Visualization dashboards (port 3000)
- **Health Checks**: All services include health endpoints
- **Logging**: Centralized logging via PM2 or Docker logs

### Port Mapping
```
Local Development:
- 3001: Frontend (Next.js dev)
- 8000: Backend API (FastAPI)
- 5434: PostgreSQL/TimescaleDB
- 6379: Redis
- 8080: Nginx (dev proxy)

Production:
- 80/443: Nginx (public access)
- 3000: Frontend (internal)
- 8000: API (internal)
- 5432: PostgreSQL (internal)
- 6379: Redis (internal)
- 9090: Prometheus
- 3000: Grafana
```

## Commands

### Backend Development
```bash
# Install dependencies
poetry install

# Run API server (development)
uvicorn src.presentation.api.app_postgres:app --reload --host 0.0.0.0 --port 8000

# Run API server with PM2
pm2 start config/ecosystem.config.js

# Run tests
poetry run pytest                              # All tests
poetry run pytest tests/unit/                  # Unit tests only
poetry run pytest tests/integration/           # Integration tests only
poetry run pytest -k "test_specific"          # Run specific test by name
poetry run pytest --cov=src --cov-report=html # With coverage

# Code quality checks
poetry run black src tests                    # Format code
poetry run isort src tests                    # Sort imports
poetry run flake8 src tests                   # Lint code
poetry run mypy src                          # Type checking
poetry run bandit -r src                     # Security checks

# Combined quality check
make quality                                  # Runs format, lint, type-check, security, and tests
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev                                   # Runs on port 3001

# Build and run production
npm run build
npm run start:prod                           # Runs on port 8502

# Testing
npm run test                                 # Run all tests
npm run test:coverage                        # With coverage
npm run test:unit                           # Unit tests only

# Code quality
npm run lint                                # ESLint
npm run type-check                         # TypeScript checking
```

### Docker Operations
```bash
# Development environment
docker-compose -f docker/docker-compose.dev.yml up -d

# Production environment
docker-compose -f docker/docker-compose.prod.yml up -d

# API-only setup
docker-compose -f docker/docker-compose-api-only.yml up -d
```

## Architecture Overview

### Domain-Driven Design Structure
The backend follows DDD principles with clear separation of concerns:

- **src/core/**: Core domain entities and business logic
- **src/domain/**: Domain services and repository interfaces
- **src/application/**: Application services and use cases
- **src/infrastructure/**: External services, database implementations
- **src/presentation/**: Web interfaces (API endpoints, CLI tools)

### Key API Endpoints
The FastAPI application (`src/presentation/api/app_postgres.py`) serves the following routers:

- `/api/v1/dashboard/`: Dashboard data and analytics
- `/api/v1/anomalies/`: Anomaly detection and monitoring
- `/api/v1/weather/`: Weather data integration
- `/api/v1/network/`: Water network topology
- `/api/v1/forecasts/`: Consumption and demand forecasting
- `/api/v1/infrastructure/`: Infrastructure management
- `/api/v1/pressure/`: Pressure zones and monitoring

### Testing Strategy
The codebase uses mocked database connections for reliable testing:
- Integration tests mock database connections using pytest-mock
- Test data is provided via pytest fixtures in conftest.py
- CI/CD pipeline runs tests without external database dependencies
- Tests validate API logic, data transformation, and error handling

### Database Architecture
- **Primary**: PostgreSQL for transactional data
- **Analytics**: Google BigQuery for large-scale analytics
- **Caching**: Redis for session management and caching

### Frontend Architecture
Next.js 15 application with:
- TypeScript for type safety
- Tailwind CSS for styling
- React 19 with server components
- Leaflet for mapping features
- Recharts for data visualization

## Development Standards

### Code Quality Requirements
- **Coverage**: Minimum 80% test coverage (fails CI if below)
- **File Size**: Maximum 500 lines per file (soft limit: 300)
- **Testing**: Follow AAA pattern (Arrange-Act-Assert)
- **Commits**: Use conventional commits format

### Python Standards
- Use Poetry for dependency management
- Black for formatting (88 char line length)
- Type hints required (enforced by mypy)
- Follow PEP 8 conventions

### TypeScript/React Standards
- Functional components with hooks
- TypeScript strict mode enabled
- ESLint with Next.js configuration
- Test files: `*.spec.tsx` (unit), `*.int.tsx` (integration)

## Environment Configuration

### Required Environment Variables
```bash
# API Configuration
API_BASE=http://localhost:8000/api/v1

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379

# Google Cloud (for BigQuery)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GCP_PROJECT_ID=your-project-id
```

## Deployment Commands

### PM2 Operations
```bash
# Start all services
pm2 start config/ecosystem.config.js

# Start specific configurations
pm2 start config/pm2-backend.config.js
pm2 start config/pm2-frontend.config.js

# Management commands
pm2 list                    # Show running processes
pm2 logs [name]            # View logs
pm2 restart all            # Restart all processes
pm2 reload all             # Zero-downtime reload
pm2 stop all               # Stop all processes
pm2 delete all             # Remove all processes
pm2 monit                  # Real-time monitoring
```

### Docker Operations
```bash
# Development environment
docker-compose -f docker/docker-compose.dev.yml up -d
docker-compose -f docker/docker-compose.dev.yml logs -f [service]

# Production deployment
docker-compose -f docker/docker-compose.prod.yml up -d
docker-compose -f docker/docker-compose.prod.yml ps

# Service-specific operations
docker-compose -f docker/docker-compose.prod.yml restart api
docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U abbanoa_user
docker-compose -f docker/docker-compose.prod.yml exec redis redis-cli

# ETL initialization (one-time)
docker-compose -f docker/docker-compose.prod.yml run --rm etl-init
```

## Common Development Tasks

### Adding New API Endpoint
1. Create router in `src/presentation/api/endpoints/`
2. Implement database queries using asyncpg
3. Register router in `app_postgres.py`
4. Write integration tests in `tests/integration/`
5. Update API documentation

### Running Integration Tests Locally
```bash
# Run integration tests (with mocked database connections)
poetry run pytest tests/integration/

# Run with coverage
poetry run pytest tests/integration/ --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/integration/test_dashboard_and_anomalies.int.py -v
```

### Database Migrations
SQL scripts are in `sql/` directory. Apply migrations:
```bash
psql -U username -d database -f sql/migration_file.sql
```

## CI/CD Pipeline

### GitHub Actions Workflows
- **api-integration.yml**: Runs API integration tests with mock data
- **frontend-ci.yml**: Frontend build, lint, and tests
- **ci-efficiency.yml**: Full CI pipeline with quality gates

### Pre-commit Hooks
Install pre-commit hooks:
```bash
pre-commit install
```

Hooks run: black, isort, flake8, mypy, and tests before commits.

## Troubleshooting

### Common Issues
1. **Port conflicts**: Check if ports 8000 (API) or 3001 (frontend) are in use
2. **Poetry issues**: Run `poetry lock --no-update` if dependencies conflict
3. **Test failures**: Integration tests use mocked database connections - check mock configuration
4. **TypeScript errors**: Run `npm run type-check` in frontend directory

### PM2 Management
```bash
pm2 list                    # Show running processes
pm2 logs                    # View logs
pm2 restart all            # Restart all processes
pm2 stop all               # Stop all processes
```