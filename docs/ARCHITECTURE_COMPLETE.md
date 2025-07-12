# Abbanoa Water Infrastructure Analytics Platform - Complete Architecture Guide

## Overview

The Abbanoa Water Infrastructure Analytics Platform is an enterprise-grade monitoring and analytics system built using Domain-Driven Design (DDD) principles. It processes real-time sensor data from water distribution networks, provides ML-powered insights, and offers comprehensive dashboards for operational monitoring.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│  Processing     │───▶│  Presentation   │
│                 │    │   Services      │    │    Layer        │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • CSV Files     │    │ • ETL Pipeline  │    │ • Streamlit UI  │
│ • Sensor Data   │    │ • ML Processing │    │ • FastAPI       │
│ • Hidroconta    │    │ • Anomaly Det.  │    │ • RESTful API   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │  Storage Tiers  │              │
         │              ├─────────────────┤              │
         └──────────────│ • Redis (Hot)   │──────────────┘
                        │ • PostgreSQL    │
                        │ • BigQuery      │
                        └─────────────────┘
```

### Three-Tier Storage Architecture

#### 1. Hot Tier (Redis)
- **Purpose**: Real-time data access
- **Retention**: 24-48 hours
- **Performance**: <50ms response time
- **Data**: Latest sensor readings, cached API responses
- **Use Cases**: Dashboard real-time updates, API caching

#### 2. Warm Tier (PostgreSQL + TimescaleDB)
- **Purpose**: Operational data for analytics
- **Retention**: 6-12 months
- **Performance**: Sub-second queries
- **Data**: Aggregated metrics, computed KPIs, ML predictions
- **Use Cases**: Dashboard analytics, reporting, ML training

#### 3. Cold Tier (BigQuery)
- **Purpose**: Complete historical archive
- **Retention**: Unlimited
- **Performance**: Seconds to minutes
- **Data**: Raw sensor data, complete audit trail
- **Use Cases**: Historical analysis, compliance reporting, ML training

## Domain-Driven Design Structure

### Core Domain

```
src/domain/
├── entities/                     # Core business entities
│   ├── monitoring_node.py        # Physical monitoring points
│   ├── sensor_reading.py         # Time-stamped measurements
│   └── water_network.py          # Network topology
├── value_objects/                # Immutable domain objects
│   ├── measurements.py           # Measurement types (flow, pressure, temp)
│   ├── location.py               # Geographic coordinates
│   └── quality_metrics.py        # Data quality scores
├── services/                     # Domain services
│   ├── anomaly_detection_service.py  # ML-powered anomaly detection
│   └── network_efficiency_service.py # Performance calculations
└── events/                       # Domain events
    ├── sensor_events.py          # Sensor-related events
    └── network_events.py         # Network-level events
```

### Key Domain Entities

#### MonitoringNode
```python
class MonitoringNode:
    id: NodeId
    location: NodeLocation
    status: NodeStatus
    sensor_types: List[SensorType]
    last_reading: Optional[datetime]
```

#### SensorReading
```python
class SensorReading:
    node_id: NodeId
    timestamp: datetime
    flow_rate: FlowRate
    pressure: Pressure
    temperature: Temperature
    total_flow: Volume
    quality_score: QualityScore
```

## Application Layer

### Use Cases

```
src/application/use_cases/
├── analyze_consumption_patterns.py    # Time-series analysis
├── detect_network_anomalies.py        # ML-powered detection
├── calculate_network_efficiency.py    # Performance metrics
└── forecast_consumption.py            # 7-day predictions
```

### Data Transfer Objects (DTOs)

```
src/application/dto/
├── sensor_reading_dto.py               # Standardized sensor data
└── analysis_results_dto.py            # Aggregated results
```

## Infrastructure Layer

### Repository Pattern

```
src/infrastructure/repositories/
├── sensor_data_repository.py          # BigQuery sensor data access
├── monitoring_node_repository.py      # Node metadata management  
├── bigquery_forecast_repository.py    # ML predictions storage
└── water_network_repository.py        # Network topology
```

### External Services

```
src/infrastructure/external_services/
├── bigquery_service.py                # Google BigQuery client
├── event_bus.py                       # Event publishing
└── notification_service.py            # Alerts and notifications
```

### ETL Pipeline

```
src/infrastructure/etl/
├── bigquery_to_postgres_etl.py        # Data synchronization
└── etl_scheduler.py                   # Pipeline orchestration
```

## Processing Services

### Background Services

```
src/processing/service/
├── main.py                            # Service orchestrator
├── data_processor.py                  # ETL operations
├── ml_manager.py                      # ML model lifecycle
└── scheduler.py                       # Job scheduling
```

### ML Pipeline

- **Automated Training**: Daily model retraining
- **Multiple Algorithms**: Prophet, ARIMA, LSTM
- **Performance Tracking**: Model accuracy monitoring
- **A/B Testing**: Model comparison and selection

## Presentation Layer

### Streamlit Dashboard

```
src/presentation/streamlit/
├── app.py                             # Main application
├── components/                        # UI components
│   ├── forecast_tab.py                # ML predictions
│   ├── overview_tab.py                # System overview
│   ├── anomaly_tab.py                 # Anomaly monitoring
│   ├── efficiency_tab.py              # Network efficiency
│   ├── consumption_tab.py             # Consumption analysis
│   ├── water_quality_tab.py           # Quality monitoring
│   └── sidebar_filters.py             # Dynamic filtering
└── utils/                             # UI utilities
    ├── enhanced_data_fetcher.py       # Data retrieval
    ├── plot_builder.py                # Plotly visualizations
    └── api_client.py                  # API integration
```

### FastAPI Service

```
src/api/
└── main.py                            # REST API endpoints
```

#### Key API Endpoints

- `GET /api/v1/nodes` - Node management
- `GET /api/v1/network/metrics` - Network-wide metrics
- `GET /api/v1/predictions/{node_id}` - ML predictions
- `GET /api/v1/anomalies` - Anomaly detection
- `GET /api/v1/status` - System health

## Data Flow

### Real-Time Processing

```
1. CSV Files (RAWDATA/) 
   ↓
2. Processing Service (validation, normalization)
   ↓
3. Three-Tier Distribution:
   - Redis (real-time access)
   - PostgreSQL (operational analytics)
   - BigQuery (historical archive)
   ↓
4. ML Processing (anomaly detection, forecasting)
   ↓
5. Dashboard Updates (real-time visualization)
```

### Batch Processing

```
1. Scheduled ETL Jobs (30-minute intervals)
   ↓
2. Data Quality Validation
   ↓
3. Feature Engineering for ML
   ↓
4. Model Training and Evaluation
   ↓
5. Prediction Generation
   ↓
6. Cache Warm-up (Redis)
```

## Technology Stack

### Core Technologies
- **Language**: Python 3.12+
- **Frameworks**: FastAPI, Streamlit, Pandas, NumPy
- **Databases**: PostgreSQL 15+ (TimescaleDB), Redis 7+, BigQuery
- **ML Libraries**: Scikit-learn, Prophet, TensorFlow
- **Infrastructure**: Docker, Docker Compose

### Development Tools
- **Package Management**: Poetry
- **Code Quality**: Black, Ruff, MyPy, Flake8, isort
- **Security**: Bandit, Safety
- **Testing**: Pytest, Coverage, factory-boy
- **Documentation**: Sphinx with RTD theme

### Dependencies
Key Python dependencies from pyproject.toml:
- `pandas ^2.0.0` - Data manipulation
- `google-cloud-bigquery ^3.11.0` - BigQuery client
- `streamlit ^1.28.0` - Dashboard framework
- `plotly ^5.18.0` - Interactive visualizations
- `prophet ^1.1.5` - Time-series forecasting
- `redis ^5.0.0` - Caching layer
- `asyncpg ^0.29.0` - PostgreSQL async client
- `dependency-injector ^4.41.0` - IoC container

## Deployment Architecture

### Containerization

```
docker-compose.yml
├── dashboard (Streamlit)              # Port 8501
├── api (FastAPI)                      # Port 8000  
├── processing (Background services)   # Internal
├── redis (Cache)                      # Port 6379
└── postgres (TimescaleDB)             # Port 5432
```

### Service Configuration

#### Environment Variables
- `BIGQUERY_PROJECT_ID`: Google Cloud project
- `BIGQUERY_DATASET_ID`: BigQuery dataset name
- `POSTGRES_CONNECTION_STRING`: PostgreSQL connection
- `REDIS_URL`: Redis connection string
- `JWT_SECRET_KEY`: Authentication secret

#### Docker Images
- `Dockerfile.dashboard` - Streamlit application
- `Dockerfile.api` - FastAPI service
- `docker/processing/Dockerfile` - Background services

### Production Deployment

- **Google Cloud Run**: Containerized service deployment
- **Cloud SQL**: Managed PostgreSQL with TimescaleDB
- **Memorystore**: Managed Redis
- **BigQuery**: Native integration
- **Cloud Build**: CI/CD pipeline

## Monitoring and Observability

### Performance Metrics
- **API Response Time**: <50ms (p95)
- **Dashboard Load**: <2 seconds
- **Data Processing**: 5-minute latency
- **System Availability**: 99.9% target

### Health Monitoring
- **Application Metrics**: Response times, error rates
- **Infrastructure Metrics**: CPU, memory, disk usage
- **Business Metrics**: Data quality, prediction accuracy
- **Custom Dashboards**: Operational insights

### Logging
- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation**: Daily rotation with 30-day retention
- **Centralized Logging**: Cloud Logging integration

## Security Architecture

### Authentication & Authorization
- **JWT Tokens**: Stateless authentication
- **Role-Based Access**: User permission management
- **API Keys**: Service-to-service authentication
- **Session Management**: Secure session handling

### Data Security
- **Encryption at Rest**: All stored data encrypted
- **Encryption in Transit**: TLS 1.3 for all communications
- **Data Anonymization**: PII protection in analytics
- **Audit Logging**: Complete action audit trail

### Network Security
- **HTTPS Only**: All web traffic encrypted
- **VPC Networks**: Isolated network segments
- **Firewall Rules**: Restrictive access policies
- **Private Endpoints**: Internal service communication

## Testing Strategy

### Test Types
```
tests/
├── unit/                              # Unit tests (domain logic)
├── integration/                       # Integration tests (services)
├── e2e/                              # End-to-end tests (full flow)
├── performance/                       # Load and performance tests
└── sql/                              # Database tests
```

### Testing Tools
- **pytest**: Test framework
- **pytest-cov**: Coverage reporting
- **factory-boy**: Test data generation
- **pytest-mock**: Mocking framework
- **pytest-asyncio**: Async test support

### Quality Gates
- **Code Coverage**: >85% coverage required
- **Performance Tests**: Response time validation
- **Security Tests**: Bandit static analysis
- **Dependency Tests**: Safety vulnerability scanning

## Development Workflow

### Code Quality
1. **Pre-commit Hooks**: Automated code formatting
2. **Static Analysis**: MyPy, Flake8, Bandit
3. **Code Review**: Mandatory peer review
4. **Automated Testing**: CI/CD pipeline validation

### Git Workflow
- **Feature Branches**: `feature/description`
- **Documentation Branches**: `docs/description`
- **Hotfix Branches**: `hotfix/description`
- **Release Branches**: `release/version`

### CI/CD Pipeline
1. **Code Quality Checks**: Linting, formatting, security
2. **Test Execution**: Unit, integration, performance
3. **Build Validation**: Docker image creation
4. **Deployment**: Staging and production deployment

## Operational Procedures

### Data Management
- **Backup Strategy**: Daily automated backups
- **Retention Policies**: Tier-specific retention
- **Data Migration**: Automated tier migration
- **Disaster Recovery**: RTO: 4 hours, RPO: 1 hour

### Monitoring and Alerting
- **Anomaly Detection**: ML-powered system monitoring
- **Threshold Alerts**: Performance and error rate alerts
- **Escalation Procedures**: On-call rotation
- **Incident Response**: Defined response procedures

### Maintenance
- **Scheduled Maintenance**: Monthly maintenance windows
- **Security Updates**: Automated security patching
- **Performance Optimization**: Quarterly performance reviews
- **Capacity Planning**: Proactive resource scaling

---

*This document represents the current architecture as of version 1.2.3.14. For the latest updates, see the [CHANGELOG.md](../CHANGELOG.md).*