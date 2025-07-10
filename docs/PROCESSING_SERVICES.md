# Processing Services Architecture

## Overview

The Abbanoa Processing Services provide a containerized, scalable solution for processing water infrastructure data. The architecture separates computation from presentation, enabling efficient data processing and serving.

## Architecture Components

### 1. **PostgreSQL with TimescaleDB** (Port: 5433)
- Dedicated database for processed results
- TimescaleDB extensions for time-series optimization
- Stores computed metrics, ML models, and predictions
- Isolated from the main application database

### 2. **Redis Cache** (Port: 6380)
- High-performance cache for API responses
- Temporary storage for processing queues
- Session management

### 3. **Processing Service**
- Runs every 30 minutes to check for new data
- Multi-threaded data processing
- ML model training and management
- Automated anomaly detection

### 4. **REST API** (Port: 8000)
- FastAPI-based REST API
- Serves pre-computed metrics
- No heavy calculations on request
- OpenAPI documentation at `/docs`

### 5. **Nginx** (Port: 8080)
- Reverse proxy for API
- Load balancing (when scaled)
- SSL termination (in production)

## Quick Start

### Prerequisites
- Docker and Docker Compose
- BigQuery service account credentials
- At least 4GB RAM available

### Setup

1. **Configure environment:**
   ```bash
   cp .env.processing.example .env.processing
   # Edit .env.processing with your settings
   ```

2. **Start services:**
   ```bash
   ./scripts/start_processing_services.sh
   ```

3. **Monitor services:**
   ```bash
   ./scripts/monitor_processing.sh
   ```

## Service Endpoints

### API Endpoints

- `GET /health` - Health check
- `GET /api/v1/nodes` - List all nodes
- `GET /api/v1/nodes/{node_id}/metrics` - Get node metrics
- `GET /api/v1/nodes/{node_id}/history` - Get historical data
- `GET /api/v1/network/metrics` - Network-wide metrics
- `GET /api/v1/network/efficiency` - Efficiency calculations
- `GET /api/v1/predictions/{node_id}` - ML predictions
- `GET /api/v1/quality/{node_id}` - Data quality metrics
- `GET /api/v1/anomalies` - Recent anomalies
- `GET /api/v1/status` - System status
- `GET /api/v1/dashboard/summary` - Dashboard summary data

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it abbanoa-postgres-processing psql -U abbanoa_user -d abbanoa_processing

# Connect to Redis
docker exec -it abbanoa-redis-processing redis-cli
```

## Data Flow

```
BigQuery (Raw Data)
    ↓
Processing Service (Every 30 min)
    ├─→ Compute Metrics (Multi-threaded)
    ├─→ Train ML Models (Weekly)
    ├─→ Detect Anomalies
    └─→ Store in PostgreSQL
         ↓
      REST API
         ├─→ Redis Cache
         └─→ Dashboard/Clients
```

## ML Model Management

### Model Types
1. **Flow Prediction** - Predicts future flow rates
2. **Anomaly Detection** - Identifies unusual patterns
3. **Efficiency Optimization** - Optimizes network efficiency

### Training Strategy
- **Hybrid Data Approach:**
  - Last 180 days: 100% data
  - 180-365 days: 50% sampling
  - >365 days: 10% sampling
- **Retraining Triggers:**
  - Weekly scheduled retraining
  - Performance degradation >20%
  - Data drift detection

### Model Deployment
1. New models deployed in shadow mode
2. 24-hour monitoring period
3. Automatic promotion if performance improves
4. Automatic rollback on degradation

## Monitoring

### Logs
```bash
# All services
docker-compose -f docker-compose.processing.yml logs -f

# Specific service
docker-compose -f docker-compose.processing.yml logs -f processing
```

### Metrics
- Processing job status in `processing_jobs` table
- Model performance in `model_performance` table
- Data quality in `data_quality_metrics` table

### Alerts (TODO)
- Failed processing jobs
- Model performance degradation
- Data quality issues
- Service health checks

## Scaling

### Horizontal Scaling
```yaml
# In docker-compose.processing.yml
processing:
  scale: 3  # Run 3 processing instances
```

### Vertical Scaling
Adjust in docker-compose:
- `POSTGRES_MAX_CONNECTIONS`
- `REDIS_MAXMEMORY`
- Container memory limits

## Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose -f docker-compose.processing.yml logs postgres

# Verify credentials
echo $GOOGLE_APPLICATION_CREDENTIALS
```

### Processing not running
```bash
# Check job status
docker exec abbanoa-postgres-processing psql -U abbanoa_user -d abbanoa_processing \
  -c "SELECT * FROM water_infrastructure.processing_jobs ORDER BY created_at DESC LIMIT 5;"
```

### API errors
```bash
# Check API logs
docker logs abbanoa-api

# Test API health
curl http://localhost:8000/health
```

## Development

### Running locally
```bash
# Install dependencies
pip install -r requirements-processing.txt
pip install -r requirements-api.txt

# Set environment
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5433
export REDIS_HOST=localhost
export REDIS_PORT=6380

# Run services
python -m src.processing.service.main
python -m src.api.main
```

### Testing
```bash
# Run tests
pytest tests/processing/
pytest tests/api/
```

## Production Deployment

### Security Considerations
1. Use strong passwords in production
2. Enable SSL for PostgreSQL
3. Configure Redis authentication
4. Use HTTPS for API
5. Implement rate limiting
6. Add authentication to API endpoints

### Performance Tuning
1. Adjust PostgreSQL configuration based on workload
2. Configure Redis maxmemory policy
3. Optimize chunk_time_interval for TimescaleDB
4. Tune processing batch sizes
5. Configure appropriate retention policies

## Maintenance

### Backup
```bash
# Backup PostgreSQL
docker exec abbanoa-postgres-processing pg_dump -U abbanoa_user abbanoa_processing > backup.sql

# Backup Redis
docker exec abbanoa-redis-processing redis-cli BGSAVE
```

### Updates
```bash
# Stop services
docker-compose -f docker-compose.processing.yml down

# Update code
git pull

# Rebuild and start
docker-compose -f docker-compose.processing.yml build
docker-compose -f docker-compose.processing.yml up -d
```

### Data Retention
- Computed metrics: 90 days (configurable)
- ML predictions: 30 days
- Processing logs: 7 days
- Anomalies: Until resolved + 30 days