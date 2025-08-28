# Water Infrastructure Analysis API

A comprehensive water infrastructure monitoring and analysis system built with FastAPI, Next.js, and modern data processing technologies.

## 🏗️ Project Structure

```
abbanoa-water-analysis/
├── src/                    # Main application source code
│   ├── api/               # API endpoints and routing
│   ├── application/       # Application services and use cases
│   ├── core/              # Core domain entities and business logic
│   ├── domain/            # Domain services and repositories
│   ├── infrastructure/    # External services, database, and infrastructure
│   ├── presentation/      # Web interfaces and CLI
│   ├── processing/        # Data processing and analytics
│   ├── routes/            # API route definitions
│   ├── schemas/           # Pydantic models and data validation
│   ├── servers/           # Standalone server implementations
│   ├── shared/            # Shared utilities and constants
│   └── utils/             # Utility scripts and helpers
├── frontend/              # Next.js frontend application
├── tests/                 # Test suite and test utilities
│   ├── legacy/            # Legacy test files
│   └── mock-backend/      # Mock authentication backend for testing
├── docs/                  # Documentation and guides
│   ├── releases/          # Release documentation
│   └── legacy/            # Legacy code reference
├── docker/                # Docker configurations and compose files
├── scripts/               # Utility and deployment scripts
├── config/                # Configuration files (PM2, cron, etc.)
├── sql/                   # SQL queries and database scripts
├── nginx/                 # Nginx configuration files
├── notebooks/             # Jupyter notebooks for analysis
├── jobs/                  # Background job definitions
├── k8s/                   # Kubernetes manifests
├── dbt/                   # Data build tool configurations
├── database_exports/      # Database export files
├── credentials/           # Credential templates (not tracked)
├── DATA/                  # Data files and exports
├── logs/                  # Application logs
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration
├── pytest.ini           # Test configuration
├── Makefile              # Build and deployment commands
├── cloudbuild.yaml       # Google Cloud Build configuration
├── .dockerignore         # Docker ignore rules
├── .gitignore           # Git ignore rules
├── PROTOCOL.yaml        # Development protocol and standards
├── CHANGELOG.md         # Project changelog
└── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+

### Backend Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the backend server:**
   ```bash
   # Using PM2 (recommended)
   pm2 start config/ecosystem.config.js
   
   # Or using uvicorn directly
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

### Docker Setup

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Or start specific services
docker-compose -f docker/docker-compose.dev.yml up -d
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

## 📚 Documentation

- **API Documentation:** Available at `/docs` when the server is running
- **Architecture:** See `docs/` directory for detailed architecture documentation
- **Releases:** Check `docs/releases/` for release notes and migration guides
- **Legacy Code:** Reference `docs/legacy/` for migration information

## 🔧 Development

This project follows strict development protocols defined in `PROTOCOL.yaml`:

- **Code Standards:** Maximum 500 lines per file, modular design
- **Testing:** 90% coverage requirement, TDD approach
- **Quality Gates:** Linting, type checking, mutation testing
- **Git Workflow:** Conventional commits, feature branches

## 🚀 Deployment

### Production

```bash
# Using Docker
docker-compose -f docker/docker-compose.prod.yml up -d

# Using PM2
pm2 start config/ecosystem.config.js --env production
```

### Google Cloud Platform

```bash
# Deploy using Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

## 📊 Features

- **Real-time Monitoring:** Live water consumption and flow rate monitoring
- **Anomaly Detection:** ML-powered anomaly detection and alerting
- **Weather Integration:** Real-time weather data and impact analysis
- **Data Analytics:** Comprehensive analytics and reporting
- **User Management:** Multi-tenant authentication and authorization
- **API-First Design:** RESTful API with comprehensive documentation

## 🤝 Contributing

1. Follow the development protocol in `PROTOCOL.yaml`
2. Create feature branches: `git checkout -b feature/your-feature`
3. Write tests for all new functionality
4. Ensure all quality gates pass
5. Submit a pull request

## 📄 License

This project is proprietary software for water infrastructure analysis.