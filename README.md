# Abbanoa Water Infrastructure Analytics Platform

Enterprise-grade water infrastructure monitoring and analytics platform for Abbanoa, featuring real-time sensor data processing, ML-powered forecasting, and comprehensive dashboards.

## 🚀 Latest Release: v2.0.0

### Major Architecture Evolution
- **Containerized Microservices**: Docker-based deployment with service isolation
- **ML Management Service**: Automated model lifecycle management
- **Three-Tier Storage**: Redis (hot) → PostgreSQL (warm) → BigQuery (cold)
- **FastAPI Service**: High-performance REST API with sub-50ms response times
- **Processing Services**: Background ETL and ML pipeline automation

## 📚 Documentation

Comprehensive documentation is available in the [docs](./docs/) directory:

- **[Architecture Overview](./docs/architecture/ARCHITECTURE.md)** - System design and components
- **[Quick Start Guide](./docs/guides/QUICK_START.md)** - Get up and running quickly
- **[Technical Documentation](./docs/technical/)** - Implementation details
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)

## 🎯 Key Features

### Real-Time Monitoring
- Live sensor data from thousands of monitoring nodes
- 30-minute data refresh cycles
- Interactive Streamlit dashboard
- Mobile-responsive design

### Network Efficiency ETL Pipeline
- **Live Data Processing**: Meter data collection every 5 minutes
- **Historical Backfill**: 90-day data backfill capabilities
- **Multi-Source Integration**: BigQuery, CSV files, and backup data
- **Schema Validation**: Automated data quality and schema validation
- **Materialized Views**: Optimized hourly/daily aggregations

### Machine Learning Integration
- Automated anomaly detection
- Time-series forecasting (7-day predictions)
- Self-training models with performance tracking
- Multiple algorithms: Prophet, ARIMA, LSTM

### Three-Tier Storage Architecture
- **Hot Tier (Redis)**: Real-time data, <50ms access
- **Warm Tier (PostgreSQL)**: 6-12 months operational data with TimescaleDB
- **Cold Tier (BigQuery)**: Complete historical archive

### Enterprise Features
- JWT-based authentication
- Role-based access control
- Comprehensive audit logging
- High availability design

## 🏗️ System Architecture

The platform follows Domain-Driven Design principles with containerized microservices:

### Service Components
- **Streamlit Dashboard**: Interactive web interface
- **FastAPI Service**: RESTful API for data access
- **Processing Service**: ETL and ML pipeline automation
- **ML Management**: Model training and deployment

### Data Flow
1. **Ingestion**: CSV sensor data → Processing Service
2. **Storage**: Three-tier distribution based on access patterns
3. **Processing**: ML analysis for patterns and anomalies
4. **API**: Unified access through FastAPI
5. **Visualization**: Real-time dashboards via Streamlit

## 🔧 ETL Operations

### Network Efficiency ETL
The platform includes a comprehensive ETL pipeline for network efficiency data:

#### Live Data Collection
```bash
# Run meter data collection (every 5 minutes via cron)
python jobs/etl_collect_meter.py

# Collection is automatically scheduled via:
# 1. cron.yaml - Google Cloud Scheduler
# 2. ETL Scheduler - Python-based scheduling
```

#### Historical Backfill
```bash
# Backfill last 90 days
python jobs/backfill.py --days=90

# Backfill specific date range
python jobs/backfill.py --start-date=2024-01-01 --end-date=2024-03-31

# Force refresh existing data
python jobs/backfill.py --days=30 --force-refresh
```

#### Schema Validation
```bash
# Validate database schema and data integrity
python jobs/validate_schema.py --verbose

# Attempt to fix issues automatically
python jobs/validate_schema.py --fix-issues
```

## 🚦 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- Google Cloud SDK (for BigQuery access)

### Running with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/abbanoa/water-infrastructure.git
   cd water-infrastructure
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start all services:
   ```bash
   docker-compose up -d
   ```

4. Access the platform:
   - Dashboard: http://localhost:8501
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Development Setup

For local development without Docker:

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Configure Google Cloud:
   ```bash
   gcloud auth application-default login
   gcloud config set project abbanoa-464816
   ```

3. Run services:
   ```bash
   # Terminal 1: API Service
   poetry run uvicorn src.api.main:app --reload

   # Terminal 2: Processing Service
   poetry run python src/processing/service/main.py

   # Terminal 3: Dashboard (use one of these methods)
   ./run_dashboard.sh                    # Recommended: handles PYTHONPATH automatically
   # OR
   poetry run python run_streamlit.py    # Alternative Python launcher
   ```

## 🚨 Troubleshooting

### ModuleNotFoundError: No module named 'src'
If you encounter this error when running the Streamlit dashboard:

1. **Use the provided run script:**
   ```bash
   ./run_dashboard.sh
   ```

2. **Or set PYTHONPATH manually:**
   ```bash
   export PYTHONPATH=/path/to/abbanoa-water-analysis:$PYTHONPATH
   poetry run streamlit run src/presentation/streamlit/app.py
   ```

3. **Or use the Python launcher:**
   ```bash
   poetry run python run_streamlit.py
   ```

The error occurs because Python needs to know where to find the project's modules. The provided scripts handle this automatically.

## 📊 Performance Metrics

- **API Response Time**: <50ms (p95)
- **Dashboard Load**: <2 seconds
- **Data Processing**: 5-minute latency
- **System Availability**: 99.9% target
- **Cost Reduction**: 75% vs. previous architecture

## 🛠️ Technology Stack

### Core Technologies
- **Languages**: Python 3.11+
- **Frameworks**: FastAPI, Streamlit, Pandas
- **Databases**: PostgreSQL 15+, Redis 7+, BigQuery
- **ML Libraries**: Scikit-learn, Prophet, TensorFlow
- **Infrastructure**: Docker, Docker Compose

### Development Tools
- **Package Management**: Poetry
- **Code Quality**: Black, Ruff, MyPy
- **Testing**: Pytest, Coverage
- **CI/CD**: GitHub Actions

## 📈 Data Sources

- **Selargius Network**: 30-minute interval sensor readings
- **Teatinos Network**: 10-minute interval readings (when available)
- **Coverage**: November 2024 - Present
- **Metrics**: Flow rate, pressure, temperature, consumption

## 🔧 Configuration

### Environment Variables
Key configuration options (see `.env.example` for full list):

- `BIGQUERY_PROJECT_ID`: Google Cloud project ID
- `BIGQUERY_DATASET_ID`: BigQuery dataset name
- `POSTGRES_CONNECTION_STRING`: PostgreSQL connection
- `REDIS_URL`: Redis connection string
- `JWT_SECRET_KEY`: Authentication secret

### Service Configuration
- Processing intervals: Configurable (default 30 minutes)
- Data retention: Configurable per tier
- ML training schedule: Daily (configurable)

## 🧪 Testing

Run the test suite:

```bash
# Unit tests
poetry run pytest tests/unit/

# Integration tests
poetry run pytest tests/integration/

# Full test suite with coverage
poetry run pytest --cov=src --cov-report=html
```

## 🚀 Deployment

### Production Deployment

The platform is designed for cloud deployment:

1. **Google Cloud Run**: Containerized services
2. **Cloud SQL**: Managed PostgreSQL
3. **Memorystore**: Managed Redis
4. **BigQuery**: Native integration

See [Deployment Guide](./docs/guides/DEPLOYMENT.md) for detailed instructions.

### Monitoring

- Application metrics via OpenTelemetry
- Infrastructure monitoring with Cloud Monitoring
- Custom dashboards for business metrics
- Automated alerting for anomalies

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details on:

- Code style and standards
- Testing requirements
- Pull request process
- Documentation standards

## 📝 License

This project is proprietary software owned by Abbanoa S.p.A. All rights reserved.

## 🆘 Support

- **Documentation**: See [docs](./docs/) directory
- **Issues**: Use GitHub Issues for bug reports
- **Contact**: tech-support@abbanoa.it
- **Emergency**: +39 xxx xxx xxxx (24/7 on-call)

---

**Version**: 2.0.0  
**Status**: Production Ready  
**Last Updated**: July 2025