# Abbanoa Water Infrastructure Analytics Platform - Architecture

## Overview

The Abbanoa Water Infrastructure Analytics Platform is a comprehensive data analytics solution designed to monitor, analyze, and predict water distribution patterns across Sardinia's water infrastructure network. Built with a modern Domain-Driven Design (DDD) approach, the platform processes real-time sensor data from thousands of monitoring nodes to provide actionable insights for water resource management.

## System Architecture

### High-Level Architecture

The platform follows a three-tier architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Presentation Layer                           │
│                    (Streamlit Dashboard)                            │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │
┌─────────────────────────────────────┴───────────────────────────────┐
│                         Application Layer                            │
│              (FastAPI REST Service + Processing Services)           │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │
┌─────────────────────────────────────┴───────────────────────────────┐
│                           Data Layer                                 │
│        (BigQuery + PostgreSQL + Redis + Cloud Storage)              │
└─────────────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Data Ingestion Pipeline
- **Raw Data Processing**: Handles CSV files with semicolon delimiters and Italian date formats
- **Batch Processing**: Processes 30-minute interval sensor readings
- **Real-time Streaming**: Supports near real-time data ingestion for critical monitoring points

#### 2. Storage Architecture (Three-Tier Strategy)

##### Cold Storage (BigQuery)
- **Purpose**: Long-term historical data storage and analytics
- **Data Retention**: All historical data (years of sensor readings)
- **Use Cases**: 
  - Historical trend analysis
  - Machine learning model training
  - Regulatory compliance reporting

##### Warm Storage (PostgreSQL)
- **Purpose**: Recent operational data and frequently accessed records
- **Data Retention**: 6-12 months of recent data
- **Use Cases**:
  - Operational dashboards
  - Daily/weekly reporting
  - Quick data retrieval for analysis

##### Hot Storage (Redis)
- **Purpose**: Real-time caching and immediate access
- **Data Retention**: 24-48 hours of latest readings
- **Use Cases**:
  - Real-time monitoring dashboards
  - Alert thresholds checking
  - API response caching

#### 3. Processing Services

##### ML Management Service
- **Model Lifecycle**: Automated training, validation, and deployment
- **Supported Models**:
  - Anomaly detection (Isolation Forest, LSTM Autoencoders)
  - Time-series forecasting (Prophet, ARIMA, LSTM)
  - Pattern recognition for leak detection
- **Model Registry**: Tracks model versions, performance metrics, and deployment status

##### Data Processing Service
- **ETL Operations**: Extract, Transform, Load pipelines
- **Data Quality**: Automated validation and cleansing
- **Aggregation**: Multi-level aggregations (node, zone, district)

##### API Service (FastAPI)
- **RESTful Endpoints**: Standardized API for all data access
- **Authentication**: JWT-based authentication
- **Rate Limiting**: Configurable rate limits per client
- **OpenAPI Documentation**: Auto-generated API documentation

#### 4. User Interface

##### Streamlit Dashboard
- **Real-time Monitoring**: Live sensor data visualization
- **Analytics Views**: 
  - Time-series analysis
  - Geographical distribution maps
  - Anomaly alerts dashboard
  - Predictive maintenance forecasts
- **Interactive Filters**: Dynamic filtering by location, time range, sensor type

### Domain-Driven Design

The platform is organized around key business domains:

1. **Sensor Domain**: Management of physical sensors and their configurations
2. **Measurement Domain**: Processing and validation of sensor readings
3. **Analytics Domain**: Statistical analysis and pattern detection
4. **Prediction Domain**: ML-based forecasting and anomaly detection
5. **Alert Domain**: Threshold monitoring and notification management

### Infrastructure

#### Containerization (Docker)
- **Service Isolation**: Each service runs in its own container
- **Scalability**: Horizontal scaling through container orchestration
- **Development Parity**: Consistent environments across dev/staging/prod

#### Deployment Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit     │     │    FastAPI      │     │   Processing    │
│   Container     │     │   Container     │     │   Services      │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                         │
         └───────────────────────┴─────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │   Shared Network        │
                    └────────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌────────┴────────┐     ┌────────┴────────┐    ┌────────┴────────┐
│   PostgreSQL    │     │     Redis       │    │   BigQuery      │
│   Container     │     │   Container     │    │  (External)     │
└─────────────────┘     └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **Ingestion**: Raw CSV files → Data Processing Service
2. **Validation**: Data quality checks and cleansing
3. **Storage**: Distributed across three-tier storage based on access patterns
4. **Processing**: ML models analyze data for patterns and anomalies
5. **API Access**: FastAPI service provides unified data access
6. **Visualization**: Streamlit dashboard presents insights to users

### Security Architecture

#### Authentication & Authorization
- **JWT Tokens**: Stateless authentication for API access
- **Role-Based Access Control (RBAC)**: Fine-grained permissions
- **API Key Management**: Secure key rotation and management

#### Data Security
- **Encryption at Rest**: All stored data is encrypted
- **Encryption in Transit**: TLS 1.3 for all communications
- **Data Anonymization**: PII removal for analytics datasets

#### Network Security
- **Private Networks**: Service-to-service communication on private networks
- **Firewall Rules**: Restrictive ingress/egress rules
- **Rate Limiting**: Protection against DDoS and abuse

### Monitoring & Observability

#### Metrics Collection
- **Application Metrics**: Response times, error rates, throughput
- **Infrastructure Metrics**: CPU, memory, disk usage
- **Business Metrics**: Data processing volumes, model accuracy

#### Logging Strategy
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Centralized Collection**: All logs aggregated for analysis
- **Log Retention**: 30-day retention for operational logs

#### Alerting
- **Threshold-based Alerts**: Configurable thresholds for all metrics
- **Anomaly-based Alerts**: ML-driven anomaly detection
- **Escalation Policies**: Multi-tier notification system

### Scalability Considerations

#### Horizontal Scaling
- **Processing Services**: Scale based on queue depth
- **API Services**: Scale based on request volume
- **Dashboard**: CDN integration for static assets

#### Data Partitioning
- **Time-based Partitioning**: Daily partitions for sensor data
- **Geographic Partitioning**: Regional data isolation
- **Sensor-based Sharding**: Distribution by sensor ID

### Disaster Recovery

#### Backup Strategy
- **Automated Backups**: Daily snapshots of all databases
- **Geographic Redundancy**: Backups stored in multiple regions
- **Point-in-Time Recovery**: Ability to restore to any point within 30 days

#### High Availability
- **Service Redundancy**: Multiple instances of critical services
- **Load Balancing**: Traffic distribution across healthy instances
- **Failover Mechanisms**: Automatic failover for database services

### Future Architecture Considerations

1. **Kubernetes Migration**: Container orchestration for improved scaling
2. **Event-Driven Architecture**: Apache Kafka for real-time event streaming
3. **Microservices Expansion**: Further service decomposition
4. **Edge Computing**: Processing at sensor locations for reduced latency
5. **Advanced ML Pipeline**: MLOps platform for model lifecycle automation

## Technology Stack

### Core Technologies
- **Languages**: Python 3.11+, SQL
- **Frameworks**: FastAPI, Streamlit, Pandas, NumPy
- **Databases**: PostgreSQL 15+, Redis 7+, Google BigQuery
- **ML Libraries**: Scikit-learn, TensorFlow, Prophet
- **Infrastructure**: Docker, Docker Compose, Google Cloud Platform

### Development Tools
- **Version Control**: Git
- **CI/CD**: GitHub Actions
- **Code Quality**: Black, Flake8, MyPy
- **Testing**: Pytest, Coverage.py
- **Documentation**: Sphinx, OpenAPI

## Conclusion

The Abbanoa Water Infrastructure Analytics Platform represents a modern, scalable solution for water resource management. By combining real-time data processing, advanced analytics, and machine learning capabilities, the platform enables proactive management of water infrastructure, reducing waste and improving service reliability across Sardinia's water network.