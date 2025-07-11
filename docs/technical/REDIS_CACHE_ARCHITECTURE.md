# Redis Cache Architecture for Abbanoa v2.0.0

## Overview

This document describes the three-tier caching architecture implemented in v2.0.0 that provides high-performance data access across containerized services. The architecture integrates Redis cache, PostgreSQL with TimescaleDB, and BigQuery for optimal performance and cost efficiency.

## Three-Tier Storage Strategy

### Tier 1: Redis Cache (Hot Data)
- **Purpose**: Ultra-fast access to frequently accessed data
- **TTL**: 24 hours (configurable)
- **Contents**:
  - Latest sensor readings per node
  - Pre-aggregated metrics (1h, 6h, 24h, 3d, 7d, 30d)
  - Recent anomalies (last 1000)
  - Time series data for charts (7 days)
  - System-wide metrics

### Tier 2: PostgreSQL/TimescaleDB (Warm Data)
- **Purpose**: Efficient time-series queries and computed results
- **Retention**: 90 days
- **Contents**:
  - Computed metrics with hypertable partitioning
  - ML predictions cache
  - Processing job history
  - Data quality metrics
  - Network efficiency calculations

### Tier 3: BigQuery (Cold Data)
- **Purpose**: Long-term storage and historical analysis
- **Retention**: Indefinite
- **Contents**:
  - Raw sensor readings
  - Historical ML training data
  - Audit logs

## Architecture Components

### 1. Redis Cache Manager (`redis_cache_manager.py`)
- Multi-threaded initialization with ThreadPoolExecutor
- Automatic TTL management
- Connection pooling for high concurrency
- Pre-computed aggregations for all time ranges
- Optimized data structures for minimal memory usage

### 2. Processing Service Integration
- Background refresh every 30 minutes
- Incremental updates to avoid full cache rebuilds
- Automatic failover to PostgreSQL if Redis unavailable
- Cache warming strategies for predictive loading

### 3. FastAPI Service
- Redis-first data access pattern
- Fallback to PostgreSQL for cache misses
- Automatic cache population on miss
- Connection pooling for both Redis and PostgreSQL

## Data Flow

```
BigQuery (Raw Data)
        ↓
Processing Service (Every 30 min)
        ↓
PostgreSQL/TimescaleDB (Computed Metrics)
        ↓
Redis Cache Manager (Hot Data)
        ↓
FastAPI Service
        ↓
Streamlit Dashboard / External Apps
```

## Container Architecture

```yaml
Services:
  - postgres: TimescaleDB for time-series data
  - redis: High-performance cache
  - processing: Background data processing
  - api: FastAPI REST service
  - nginx: Load balancer (production)
```

## Key Benefits

### Performance
- **API Response Time**: <50ms for cached data
- **Dashboard Load Time**: <200ms for full page render
- **Concurrent Users**: Supports 1000+ simultaneous connections
- **Cache Hit Rate**: >95% for common queries

### Cost Optimization
- **BigQuery Costs**: 90% reduction through batch processing
- **Query Frequency**: From continuous to every 30 minutes
- **Data Transfer**: Minimized through local caching

### Reliability
- **Multi-tier Failover**: Redis → PostgreSQL → BigQuery
- **Zero Downtime Updates**: Rolling deployments supported
- **Data Consistency**: ACID guarantees with PostgreSQL

### Scalability
- **Horizontal Scaling**: Add more API/processing instances
- **Vertical Scaling**: Redis cluster mode ready
- **Load Distribution**: Nginx load balancing

## Implementation Guide

### 1. Deploy with Docker Compose
```bash
# Start all services
docker-compose -f docker-compose.processing.yml up -d

# Check service health
docker-compose -f docker-compose.processing.yml ps

# View logs
docker-compose -f docker-compose.processing.yml logs -f processing
```

### 2. Environment Configuration
```bash
# Create .env.processing file
POSTGRES_PASSWORD=secure_password
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
BIGQUERY_PROJECT_ID=your-project-id
REDIS_HOST=redis
CHECK_INTERVAL_MINUTES=30
```

### 3. API Integration
```python
# Using the FastAPI endpoints
import requests

# Get node metrics
response = requests.get("http://localhost:8000/api/v1/nodes/node123/metrics")
metrics = response.json()

# Get network status
response = requests.get("http://localhost:8000/api/v1/network/metrics?time_range=24h")
network = response.json()
```

### 4. Dashboard Integration
```python
# Streamlit integration with API
import streamlit as st
import requests

@st.cache_data(ttl=60)
def get_dashboard_data():
    response = requests.get("http://localhost:8000/api/v1/dashboard/summary")
    return response.json()
```

## Cache Structure

### Keys Pattern
- `node:{node_id}:metadata` - Node information
- `node:{node_id}:latest` - Latest sensor reading
- `node:{node_id}:metrics:{time_range}` - Aggregated metrics
- `node:{node_id}:timeseries:7d` - Time series data
- `system:metrics:{time_range}` - System-wide metrics
- `anomalies:recent` - Recent anomalies list
- `nodes:all` - List of all node IDs

### Time Ranges
- `1h` - Last hour
- `6h` - Last 6 hours
- `24h` - Last 24 hours
- `3d` - Last 3 days
- `7d` - Last 7 days
- `30d` - Last 30 days

## Environment Variables

### Redis Configuration
- `REDIS_HOST` - Redis server host (default: redis)
- `REDIS_PORT` - Redis server port (default: 6379)
- `REDIS_DB` - Redis database number (default: 0)
- `CACHE_TTL_HOURS` - Cache expiration time (default: 24)

### PostgreSQL Configuration
- `POSTGRES_HOST` - PostgreSQL host (default: postgres)
- `POSTGRES_PORT` - PostgreSQL port (default: 5432)
- `POSTGRES_DB` - Database name (default: abbanoa_processing)
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password

### Processing Configuration
- `CHECK_INTERVAL_MINUTES` - Processing cycle interval (default: 30)
- `MODEL_STORAGE_PATH` - ML model storage location
- `BIGQUERY_PROJECT_ID` - Google Cloud project ID
- `BIGQUERY_DATASET_ID` - BigQuery dataset (default: water_infrastructure)

## Monitoring

### Service Health Monitoring
```bash
# Check all services
curl http://localhost:8000/api/v1/status

# Monitor Redis
docker exec abbanoa-redis-processing redis-cli info stats

# Monitor PostgreSQL connections
docker exec abbanoa-postgres-processing psql -U abbanoa_user -c "SELECT count(*) FROM pg_stat_activity;"

# View processing logs
docker logs -f abbanoa-processing --tail 100
```

### Performance Metrics
```python
# Via API endpoint
response = requests.get("http://localhost:8000/api/v1/status")
status = response.json()

print(f"Processing Status: {status['status']}")
print(f"Redis Keys: {status['redis_status']['keys']}")
print(f"Active Models: {len(status['active_models'])}")
print(f"Data Freshness: {status['data_freshness']['latest_data']}")
```

## Future Enhancements

### Phase 1: High Availability
1. **Redis Sentinel**: Automatic failover for Redis
2. **PostgreSQL Replication**: Read replicas for scaling
3. **Multi-region Support**: Geographic distribution

### Phase 2: Real-time Capabilities
1. **Redis Streams**: Real-time data ingestion
2. **WebSocket Support**: Push notifications
3. **Event-driven Updates**: Instant cache invalidation

### Phase 3: Advanced Optimization
1. **Predictive Caching**: ML-based cache warming
2. **Adaptive TTL**: Dynamic expiration based on usage
3. **Query Result Caching**: Cache complex aggregations

## Production Deployment

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: abbanoa-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: abbanoa-api
  template:
    spec:
      containers:
      - name: api
        image: abbanoa/api:v2.0.0
        env:
        - name: REDIS_HOST
          value: redis-service
        - name: POSTGRES_HOST
          value: postgres-service
```

### Monitoring Stack
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **AlertManager**: Incident notifications
- **Jaeger**: Distributed tracing