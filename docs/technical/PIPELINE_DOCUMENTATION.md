# ETL Pipeline Documentation v2.0.0

## Overview

The v2.0.0 ETL pipeline implements a sophisticated three-stage architecture that processes water infrastructure data from raw sensor readings to actionable insights. The system features:

- **Containerized Services**: Fully dockerized processing pipeline
- **Three-Tier Storage**: BigQuery → PostgreSQL → Redis
- **ML Integration**: Automated anomaly detection and predictions
- **Real-time Processing**: 30-minute update cycles
- **Data Quality Management**: Automated validation and monitoring

## Pipeline Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────┐
│   BigQuery  │ →   │  Processing  │ →   │ PostgreSQL  │ →   │   Redis    │
│  Raw Data   │     │   Service    │     │  Computed   │     │   Cache    │
└─────────────┘     └──────────────┘     └─────────────┘     └────────────┘
      ↓                     ↓                     ↓                  ↓
  Historical           ML Models            Time-series         Real-time
   Storage            & Analytics           Aggregations          Access
```

## Core Components

### 1. **Processing Service** (`src/processing/service/main.py`)

The heart of the ETL pipeline that runs continuously:
- **Scheduling**: Executes every 30 minutes via ProcessingScheduler
- **Data Processing**: Multi-threaded processing with DataProcessor
- **ML Management**: Automated model training and deployment
- **Quality Checks**: Continuous data quality monitoring

```python
class ProcessingService:
    async def _process_cycle(self):
        # Check for new data in BigQuery
        new_data = await self._check_for_new_data()
        
        # Process with parallel execution
        results = await self.data_processor.process_new_data(
            start_timestamp=new_data['min_timestamp'],
            end_timestamp=new_data['max_timestamp']
        )
        
        # Trigger ML predictions
        await self.ml_manager.generate_predictions(
            nodes=results['processed_nodes']
        )
```

### 2. **Data Processor** (`src/processing/service/data_processor.py`)

Handles the actual data transformation:
- **Parallel Processing**: ThreadPoolExecutor for node-level parallelism
- **Aggregation Windows**: 5min, 1hour, 1day pre-computed metrics
- **Anomaly Detection**: Statistical and ML-based detection
- **Network Efficiency**: Zone-based efficiency calculations

### 3. **ML Manager** (`src/processing/service/ml_manager.py`)

Manages machine learning models:
- **Model Types**: Flow prediction, anomaly detection, efficiency optimization
- **Auto-retraining**: Weekly model updates based on new data
- **Model Versioning**: Tracks and manages multiple model versions
- **Performance Monitoring**: Continuous model evaluation

## Deployment Guide

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/abbanoa/water-infrastructure
cd water-infrastructure

# Create environment file
cp .env.example .env.processing

# Edit configuration
nano .env.processing
# Set:
# - GOOGLE_APPLICATION_CREDENTIALS
# - BIGQUERY_PROJECT_ID
# - POSTGRES_PASSWORD
# - Processing intervals
```

### 2. Service Deployment

```bash
# Build and start all services
docker-compose -f docker-compose.processing.yml up -d

# Verify services are healthy
docker-compose -f docker-compose.processing.yml ps

# Check logs
docker-compose -f docker-compose.processing.yml logs -f

# Monitor processing cycles
./scripts/monitor_processing.sh
```

### 3. Initial Data Load

```bash
# For initial historical data load
docker exec -it abbanoa-processing python -m scripts.initial_data_load \
  --start-date "2024-01-01" \
  --end-date "2024-12-31" \
  --batch-size 10000
```

## Data Schema

### BigQuery Tables (Raw Data)

**sensor_readings_ml**
| Field | Type | Description |
|-------|------|-------------|
| timestamp | TIMESTAMP | Measurement timestamp |
| node_id | STRING | Unique node identifier |
| node_name | STRING | Human-readable node name |
| flow_rate | FLOAT64 | Instantaneous flow (L/s) |
| pressure | FLOAT64 | Pressure (bar) |
| temperature | FLOAT64 | Temperature (°C) |
| volume | FLOAT64 | Total volume (m³) |
| quality_score | FLOAT64 | Data quality indicator |

### PostgreSQL Tables (Computed Data)

**computed_metrics** (TimescaleDB Hypertable)
| Field | Type | Description |
|-------|------|-------------|
| node_id | TEXT | Node identifier |
| time_window | TEXT | Aggregation window (5min/1hour/1day) |
| window_start | TIMESTAMPTZ | Window start time |
| window_end | TIMESTAMPTZ | Window end time |
| avg_flow_rate | NUMERIC | Average flow rate |
| min_flow_rate | NUMERIC | Minimum flow rate |
| max_flow_rate | NUMERIC | Maximum flow rate |
| avg_pressure | NUMERIC | Average pressure |
| anomaly_count | INTEGER | Anomalies detected |
| quality_score | NUMERIC | Data quality (0-1) |

**ml_predictions_cache**
| Field | Type | Description |
|-------|------|-------------|
| prediction_id | UUID | Unique prediction ID |
| model_id | UUID | Model identifier |
| node_id | TEXT | Node identifier |
| prediction_timestamp | TIMESTAMPTZ | When predicted |
| target_timestamp | TIMESTAMPTZ | Prediction target time |
| predicted_flow_rate | NUMERIC | Predicted flow |
| confidence_score | NUMERIC | Prediction confidence |

## Monitoring & Operations

### Processing Job Monitoring
```sql
-- Check recent processing jobs
SELECT 
  job_id,
  job_type,
  status,
  started_at,
  completed_at,
  duration_seconds,
  result_summary
FROM water_infrastructure.processing_jobs
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- Monitor data freshness
SELECT 
  node_id,
  MAX(window_end) as latest_data,
  NOW() - MAX(window_end) as data_lag
FROM water_infrastructure.computed_metrics
GROUP BY node_id
HAVING NOW() - MAX(window_end) > INTERVAL '1 hour';
```

### API Monitoring
```bash
# Check processing service health
curl http://localhost:8000/api/v1/status

# Monitor active ML models
curl http://localhost:8000/api/v1/models/status

# View recent anomalies
curl http://localhost:8000/api/v1/anomalies?hours=24
```

### Performance Metrics
```bash
# PostgreSQL performance
docker exec abbanoa-postgres-processing psql -U abbanoa_user -c "
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'water_infrastructure'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Redis memory usage
docker exec abbanoa-redis-processing redis-cli info memory
```

## Automation & Scheduling

### Built-in Scheduler
The processing service includes an integrated scheduler that manages:

```python
# Data processing every 30 minutes
scheduler.add_job(
    self._process_cycle,
    'interval',
    minutes=30,
    name='Data Processing Cycle'
)

# ML model evaluation daily at 2 AM
scheduler.add_job(
    self.ml_manager.evaluate_models,
    'cron',
    hour=2,
    name='ML Model Evaluation'
)

# Weekly model retraining on Sundays
scheduler.add_job(
    self.ml_manager.retrain_models,
    'cron',
    day_of_week=0,
    hour=3,
    name='ML Model Retraining'
)
```

### External Integration

#### Apache Airflow DAG
```python
from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator

dag = DAG('abbanoa_processing',
          schedule_interval='*/30 * * * *')

trigger_processing = SimpleHttpOperator(
    task_id='trigger_processing',
    http_conn_id='abbanoa_api',
    endpoint='/api/v1/processing/trigger',
    method='POST',
    dag=dag
)
```

#### Kubernetes CronJob
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: abbanoa-processing-trigger
spec:
  schedule: "*/30 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: trigger
            image: curlimages/curl
            command:
            - curl
            - -X
            - POST
            - http://abbanoa-api:8000/api/v1/processing/trigger
```

## Troubleshooting

### Common Issues

#### Processing Service Not Starting
```bash
# Check logs
docker-compose -f docker-compose.processing.yml logs processing

# Verify BigQuery credentials
docker exec -it abbanoa-processing \
  python -c "from google.cloud import bigquery; client = bigquery.Client(); print('Connected')"

# Check PostgreSQL connection
docker exec -it abbanoa-processing \
  python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://abbanoa_user:password@postgres:5432/abbanoa_processing'))"
```

#### Data Not Updating
```bash
# Check last processing job
curl http://localhost:8000/api/v1/status | jq '.processing_service'

# Verify BigQuery has new data
docker exec -it abbanoa-processing python -m scripts.check_bigquery_data

# Force processing cycle
curl -X POST http://localhost:8000/api/v1/processing/trigger
```

#### High Memory Usage
```bash
# Check container stats
docker stats

# Adjust memory limits in docker-compose
# services:
#   processing:
#     mem_limit: 2g
#     memswap_limit: 2g
```

#### ML Model Failures
```bash
# Check model status
curl http://localhost:8000/api/v1/models/status

# View model logs
docker exec -it abbanoa-processing tail -f /app/logs/ml_manager.log

# Force model retraining
docker exec -it abbanoa-processing python -m scripts.retrain_models
```

## Production Best Practices

### 1. Monitoring Setup
- **Prometheus**: Export metrics from all services
- **Grafana**: Create dashboards for key metrics
- **AlertManager**: Set up alerts for failures

### 2. Backup Strategy
- **PostgreSQL**: Daily backups with pg_dump
- **ML Models**: Version control in cloud storage
- **Configuration**: Store in encrypted secrets manager

### 3. Security
- **API Authentication**: Implement OAuth2/JWT
- **Network Isolation**: Use private subnets
- **Secrets Management**: Use Docker secrets or Kubernetes secrets

### 4. Scaling
- **Horizontal Scaling**: Add more API/processing instances
- **Database Replication**: Set up read replicas
- **Load Balancing**: Use Nginx or cloud load balancer

## Support

For technical support or feature requests:
- **GitHub Issues**: https://github.com/abbanoa/water-infrastructure/issues
- **API Documentation**: http://localhost:8000/docs
- **Team Contact**: data-engineering@abbanoa.it