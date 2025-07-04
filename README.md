# Abbanoa Water Infrastructure Management System

## Overview
Enterprise-grade water infrastructure monitoring and analytics platform for Abbanoa, featuring real-time sensor data processing, ML-powered forecasting, and integrated dashboards. Built with **Domain-Driven Design (DDD)** architecture for scalability and maintainability.

### 🚀 Latest Release: v1.0.0
- **DDD Architecture**: Complete restructure with clean architecture principles
- **Integrated Dashboard**: Unified Streamlit dashboard with real-time monitoring
- **BigQuery Integration**: Direct connection to production data warehouse
- **No Synthetic Data**: Pure real-data visualization (November 2024 - March 2025)
- **Multi-layer Architecture**: Presentation, Application, Domain, and Infrastructure layers

## System Architecture

### Domain-Driven Design Structure
```
src/
├── domain/                    # Core business logic
│   ├── entities/             # Business entities
│   ├── value_objects/        # Immutable value objects
│   ├── events/              # Domain events
│   └── services/            # Domain services
├── application/              # Use cases and DTOs
│   ├── use_cases/           # Application services
│   ├── dto/                 # Data transfer objects
│   └── interfaces/          # Repository interfaces
├── infrastructure/           # External services
│   ├── repositories/        # Data access implementations
│   ├── external_services/   # Third-party integrations
│   └── persistence/         # Database configurations
└── presentation/            # User interfaces
    ├── streamlit/          # Web dashboard
    ├── api/                # REST API
    └── cli/                # Command-line interface
```

### C4 System Context Diagram
```mermaid
C4Context
    title System Context - Abbanoa Water Infrastructure Platform

    Person(operators, "Water Facility<br/>Operators", "Monitor real-time<br/>infrastructure status")
    Person(analysts, "Data Analysts", "Analyze patterns and<br/>generate forecasts")
    Person(managers, "Operations<br/>Managers", "Strategic planning<br/>and KPI monitoring")

    System_Boundary(abbanoa, "Abbanoa Platform") {
        System(platform, "Water Infrastructure<br/>Management System", "DDD-based monitoring<br/>and analytics platform")
    }

    System_Ext(sensors, "Sensor Networks", "Selargius & Teatinos<br/>monitoring nodes")
    System_Ext(bigquery, "Google BigQuery", "Time-series data<br/>warehouse")
    System_Ext(ml_platform, "Vertex AI", "ML model training<br/>and serving")

    Rel(sensors, platform, "Sensor data", "CSV/API")
    Rel(platform, bigquery, "Normalized data", "BigQuery API")
    Rel(platform, ml_platform, "Training data", "Vertex AI API")
    Rel(ml_platform, platform, "Predictions", "REST API")
    
    Rel(operators, platform, "Monitor & control")
    Rel(analysts, platform, "Analyze & forecast")
    Rel(managers, platform, "View dashboards")
```

### Container Diagram - DDD Architecture
```mermaid
C4Container
    title Container Diagram - DDD Architecture

    Person(users, "Users", "Operators, Analysts,<br/>Managers")

    System_Boundary(platform, "Abbanoa Platform") {
        Container(web_ui, "Streamlit Dashboard", "Python/Streamlit", "Interactive web<br/>dashboard")
        Container(api, "REST API", "FastAPI", "External system<br/>integration")
        Container(cli, "CLI Tool", "Python/Click", "Command-line<br/>operations")
        
        Container(use_cases, "Application Layer", "Python", "Business use cases<br/>and orchestration")
        Container(domain, "Domain Layer", "Python", "Core business logic<br/>and entities")
        
        Container(repos, "Repositories", "Python", "Data access<br/>abstraction")
        Container(services, "External Services", "Python", "Third-party<br/>integrations")
        
        ContainerDb(cache, "Redis Cache", "Redis", "Performance<br/>optimization")
    }

    ContainerDb(bigquery_db, "BigQuery", "Data Warehouse", "Time-series<br/>sensor data")
    System_Ext(ml_models, "ML Models", "ARIMA_PLUS<br/>forecasting")

    Rel(users, web_ui, "Uses", "HTTPS")
    Rel(users, api, "Integrates", "REST/JSON")
    Rel(users, cli, "Operates", "Terminal")
    
    Rel(web_ui, use_cases, "Invokes")
    Rel(api, use_cases, "Invokes")
    Rel(cli, use_cases, "Invokes")
    
    Rel(use_cases, domain, "Uses")
    Rel(use_cases, repos, "Queries")
    
    Rel(repos, bigquery_db, "Reads/Writes", "BigQuery API")
    Rel(repos, cache, "Caches", "Redis Protocol")
    
    Rel(services, ml_models, "Gets predictions")
    Rel(use_cases, services, "Uses")
```

### Data Flow Architecture
```mermaid
flowchart TD
    subgraph "Data Sources"
        A1[Selargius Sensors<br/>30-min aggregates]
        A2[Teatinos Sensors<br/>10-min readings]
    end
    
    subgraph "Infrastructure Layer"
        B1[CSV Data Ingestion]
        B2[BigQuery Repository<br/>sensor_data table]
        B3[Static Node Repository<br/>monitoring_nodes]
    end
    
    subgraph "Domain Layer"
        C1[MonitoringNode Entity]
        C2[SensorReading Entity]
        C3[Anomaly Detection Service]
        C4[Network Efficiency Service]
    end
    
    subgraph "Application Layer"
        D1[Analyze Consumption<br/>Use Case]
        D2[Detect Anomalies<br/>Use Case]
        D3[Calculate Efficiency<br/>Use Case]
        D4[Forecast Consumption<br/>Use Case]
    end
    
    subgraph "Presentation Layer"
        E1[Streamlit Dashboard<br/>📊 6 Integrated Tabs]
        E2[REST API<br/>🔌 External Integration]
        E3[CLI Interface<br/>⚡ Admin Operations]
    end
    
    A1 --> B1
    A2 --> B1
    B1 --> B2
    B2 --> C2
    B3 --> C1
    C1 --> C3
    C2 --> C3
    C1 --> C4
    C2 --> C4
    C3 --> D2
    C4 --> D3
    C2 --> D1
    C2 --> D4
    D1 --> E1
    D2 --> E1
    D3 --> E1
    D4 --> E1
    D1 --> E2
    D2 --> E3
```

## Key Features

### 🏗️ **Domain-Driven Design**
- Clean architecture with clear separation of concerns
- Domain entities: MonitoringNode, SensorReading, WaterNetwork
- Value objects: Location, Measurements, NodeStatus
- Rich domain services for business logic

### 📊 **Integrated Dashboard**
- **6 Main Tabs**: Overview, Forecast, Anomaly Detection, Consumption, Efficiency, Reports
- **Real-time Monitoring**: Live sensor data visualization
- **No Synthetic Data**: Shows only actual BigQuery data
- **Responsive Design**: Mobile-friendly interface

### 🤖 **Machine Learning Integration**
- ARIMA_PLUS models for 7-day forecasting
- Multiple metrics: flow rate, pressure, consumption
- <15% MAPE accuracy across districts
- Automated daily predictions

### 🔄 **Data Processing**
- Direct BigQuery integration
- Normalized view for sensor readings
- Support for multiple monitoring nodes
- Real-time data streaming capabilities

### 🎯 **Use Cases**
1. **Analyze Consumption Patterns**: Historical analysis and trends
2. **Detect Network Anomalies**: Real-time anomaly detection
3. **Calculate Network Efficiency**: Performance metrics and KPIs
4. **Forecast Consumption**: ML-powered predictions
5. **Generate Reports**: Automated reporting

## Technical Specifications

### Technology Stack
- **Backend**: Python 3.12, Poetry
- **Framework**: Domain-Driven Design, Clean Architecture
- **Database**: Google BigQuery (Data Warehouse)
- **ML Platform**: Vertex AI, ARIMA_PLUS
- **Dashboard**: Streamlit 1.40+
- **API**: FastAPI
- **Cache**: Redis (optional)
- **Container**: Dependency Injector

### Data Sources
| Source | Format | Frequency | Time Range |
|--------|--------|-----------|------------|
| Selargius CSV | UTF-8, Comma | 30-min | Nov 2024 - Mar 2025 |
| BigQuery Views | Normalized | Real-time | Historical + Live |

### Performance Metrics
- **Dashboard Load**: <2 seconds
- **Query Response**: <500ms (cached)
- **ML Predictions**: <30 seconds for 7-day forecast
- **Data Freshness**: 30-minute lag maximum

## Getting Started

### Prerequisites
```bash
# Required software
- Python 3.12+
- Poetry (dependency management)
- Google Cloud SDK
- Git

# Environment variables
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
export BIGQUERY_PROJECT_ID="abbanoa-464816"
export BIGQUERY_DATASET_ID="water_infrastructure"
```

### Installation
```bash
# Clone repository
git clone https://github.com/abbanoa/water-infrastructure.git
cd water-infrastructure

# Install dependencies
poetry install

# Configure GCP
gcloud auth login
gcloud config set project abbanoa-464816
```

### Running the Dashboard
```bash
# Using the convenience script
./run_dashboard.sh

# Or directly with streamlit
poetry run streamlit run src/presentation/streamlit/app.py

# Access at http://localhost:8502
```

### Running Tests
```bash
# Unit tests
poetry run pytest tests/unit/

# Integration tests
poetry run pytest tests/integration/

# All tests with coverage
poetry run pytest --cov=src --cov-report=html
```

## Dashboard Features

### Overview Tab
- Real-time metrics: Active nodes, flow rates, pressure, efficiency
- System status monitoring
- Alert notifications

### Forecast Tab
- 7-day predictions with confidence intervals
- Interactive charts for different metrics
- Model performance statistics
- District selection

### Anomaly Detection Tab
- Real-time anomaly alerts
- Pattern analysis
- Historical anomaly trends
- Severity classification

### Consumption Patterns Tab
- Daily/weekly/monthly trends
- Peak usage analysis
- Comparative analytics
- Heatmap visualizations

### Network Efficiency Tab
- Efficiency metrics and KPIs
- Component performance
- Loss distribution analysis
- Energy consumption tracking

### Reports Tab
- Automated report generation
- Custom date ranges
- Multiple export formats
- Scheduled reports

## API Documentation

### REST API Endpoints
```python
# Health check
GET /api/v1/health

# Sensor readings
GET /api/v1/readings/{node_id}
GET /api/v1/readings/{node_id}/latest

# Monitoring nodes
GET /api/v1/nodes
GET /api/v1/nodes/{node_id}

# Analytics
POST /api/v1/analytics/consumption
POST /api/v1/analytics/anomalies
POST /api/v1/analytics/efficiency

# Forecasts
GET /api/v1/forecasts/{district_id}/{metric}
```

### CLI Commands
```bash
# Data operations
poetry run abbanoa data ingest --source selargius
poetry run abbanoa data validate --date 2024-11-13

# Analysis
poetry run abbanoa analyze consumption --district DIST_001
poetry run abbanoa analyze anomalies --hours 24

# Reports
poetry run abbanoa report generate --type daily
poetry run abbanoa report export --format pdf
```

## Development

### Project Structure
```
├── src/                      # Source code (DDD layers)
├── tests/                    # Test suites
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
├── RAWDATA/                  # Raw data files
├── pyproject.toml           # Poetry configuration
├── .env.example             # Environment template
├── CLAUDE.md                # AI assistant context
└── run_dashboard.sh         # Dashboard launcher
```

### Contributing
1. Follow DDD principles and clean architecture
2. Write tests for new features
3. Update documentation
4. Use conventional commits
5. Run linters before committing

### Code Style
- Black for formatting
- Ruff for linting
- MyPy for type checking
- 100% type hints required

## Deployment

### Production Deployment
```bash
# Build Docker image
docker build -t abbanoa-platform:latest .

# Deploy to Cloud Run
gcloud run deploy abbanoa-platform \
  --image gcr.io/abbanoa-464816/abbanoa-platform:latest \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated
```

### Environment Configuration
- Development: `.env.development`
- Staging: `.env.staging`
- Production: `.env.production`

## Monitoring & Maintenance

### Health Checks
- Dashboard availability
- BigQuery connectivity
- ML model performance
- Data freshness validation

### Alerting
- System errors and exceptions
- Data quality issues
- Performance degradation
- Anomaly detection alerts

### Maintenance
- **Daily**: Automated health checks
- **Weekly**: Performance review
- **Monthly**: ML model retraining
- **Quarterly**: Architecture review

## Support

### Documentation
- Architecture: This README
- API Reference: `/docs/api/`
- User Guide: `/docs/user-guide/`
- ML Models: `/docs/ml-models/`

### Contact
- Technical Support: tech@abbanoa.it
- GitHub Issues: [Report Issue](https://github.com/abbanoa/water-infrastructure/issues)

---

*Version: 1.0.0*  
*Release Date: July 2025*  
*Status: Production Ready* 🚀