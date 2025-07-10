# Hybrid Architecture Setup Guide

This guide walks you through setting up the complete hybrid data architecture for the Abbanoa Water Infrastructure system.

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Google Cloud SDK (for BigQuery access)
- PostgreSQL client tools
- Redis client tools

## Quick Start

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone https://github.com/your-org/abbanoa-water-infrastructure.git
cd abbanoa-water-infrastructure

# Install Python dependencies
poetry install
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# BigQuery Configuration
BIGQUERY_PROJECT_ID=abbanoa-464816
BIGQUERY_DATASET_ID=water_infrastructure
BIGQUERY_LOCATION=EU
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=abbanoa
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Cache Configuration
CACHE_TTL_HOURS=24
CACHE_REFRESH_HOURS=6

# ETL Configuration
ETL_BATCH_SIZE=10000
ETL_MAX_WORKERS=4
```

### 3. Start Infrastructure Services

```bash
# Start PostgreSQL and Redis using Docker Compose
docker-compose up -d postgres redis

# Wait for services to be ready
docker-compose ps
```

### 4. Initialize PostgreSQL Database

```bash
# Create database and schema
docker exec -i abbanoa-postgres psql -U postgres < src/infrastructure/database/postgres_schema.sql

# Verify tables were created
docker exec -it abbanoa-postgres psql -U postgres -d abbanoa -c "\dt water_infrastructure.*"
```

### 5. Run Initial Data Sync

```bash
# Activate Poetry environment
poetry shell

# Run historical data sync (last 90 days)
python -m src.infrastructure.etl.bigquery_to_postgres_etl

# This will:
# - Sync node metadata
# - Import sensor readings
# - Create continuous aggregates
# - Build initial cache
```

### 6. Initialize Redis Cache

```bash
# Run cache initialization
python init_redis_cache.py --stats

# Expected output:
# ✅ Redis connection successful
# Starting cache initialization...
# ✅ Cache initialization completed in X.XX seconds
# 
# Cache Statistics:
# Status: connected
# Total keys: XXX
# Memory used: XX MB
# Cached nodes: 9
```

### 7. Start ETL Scheduler

```bash
# Run in a separate terminal or as a service
python -m src.infrastructure.etl.etl_scheduler

# This starts scheduled jobs:
# - Daily sync at 2 AM
# - Real-time sync every 5 minutes
# - Cache refresh every hour
# - Anomaly detection every 15 minutes
```

### 8. Launch Dashboard

```bash
# Start Streamlit dashboard
streamlit run src/presentation/streamlit/app.py

# Dashboard will be available at http://localhost:8501
```

## Detailed Setup Steps

### PostgreSQL/TimescaleDB Setup

#### Option 1: Docker (Recommended)

```bash
# Pull TimescaleDB image
docker pull timescale/timescaledb:latest-pg14

# Run with custom configuration
docker run -d \
  --name abbanoa-postgres \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=abbanoa \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  timescale/timescaledb:latest-pg14
```

#### Option 2: Native Installation

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-14 postgresql-contrib-14
sudo apt-get install postgresql-14-timescaledb

# Enable TimescaleDB
sudo -u postgres psql -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
```

### Redis Setup

#### Option 1: Docker (Recommended)

```bash
# Run Redis with persistence
docker run -d \
  --name abbanoa-redis \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:7-alpine \
  redis-server --appendonly yes
```

#### Option 2: Native Installation

```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# Configure for production
sudo sed -i 's/# maxmemory <bytes>/maxmemory 2gb/' /etc/redis/redis.conf
sudo sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
sudo systemctl restart redis-server
```

### BigQuery Configuration

1. **Create Service Account**
   ```bash
   # Using gcloud CLI
   gcloud iam service-accounts create abbanoa-data-service \
     --display-name="Abbanoa Data Service"
   
   # Grant necessary permissions
   gcloud projects add-iam-policy-binding abbanoa-464816 \
     --member="serviceAccount:abbanoa-data-service@abbanoa-464816.iam.gserviceaccount.com" \
     --role="roles/bigquery.dataViewer"
   ```

2. **Download Credentials**
   ```bash
   gcloud iam service-accounts keys create \
     ./credentials/gcp-key.json \
     --iam-account=abbanoa-data-service@abbanoa-464816.iam.gserviceaccount.com
   ```

3. **Set Environment Variable**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials/gcp-key.json"
   ```

## Verification Steps

### 1. Verify PostgreSQL

```sql
-- Connect to database
psql -h localhost -U postgres -d abbanoa

-- Check hypertables
SELECT hypertable_name, num_chunks 
FROM timescaledb_information.hypertables;

-- Check continuous aggregates
SELECT view_name, refresh_lag 
FROM timescaledb_information.continuous_aggregates;

-- Check data
SELECT COUNT(*) FROM water_infrastructure.sensor_readings;
```

### 2. Verify Redis

```bash
# Check connection
redis-cli ping

# Check keys
redis-cli keys "node:*"

# Check system metrics
redis-cli get "system:metrics:24h"
```

### 3. Verify ETL Jobs

```sql
-- Check recent ETL jobs
SELECT job_name, status, started_at, records_processed 
FROM water_infrastructure.etl_jobs 
ORDER BY started_at DESC 
LIMIT 10;
```

## Production Deployment

### 1. Use Docker Compose

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale streamlit=3
```

### 2. Configure Nginx

```nginx
upstream streamlit_backend {
    server streamlit1:8501;
    server streamlit2:8501;
    server streamlit3:8501;
}

server {
    listen 80;
    server_name dashboard.abbanoa.it;
    
    location / {
        proxy_pass http://streamlit_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 3. Set Up Monitoring

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:9187']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### 4. Configure Backups

```bash
# PostgreSQL backup
pg_dump -h localhost -U postgres abbanoa | gzip > backup_$(date +%Y%m%d).sql.gz

# Redis backup
redis-cli BGSAVE
```

## Troubleshooting

### Issue: Redis Connection Refused

```bash
# Check if Redis is running
docker ps | grep redis

# Check Redis logs
docker logs abbanoa-redis

# Test connection
redis-cli -h localhost -p 6379 ping
```

### Issue: PostgreSQL Slow Queries

```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();

-- Check slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

### Issue: ETL Job Failures

```python
# Check ETL logs
tail -f logs/etl_scheduler.log

# Manually trigger sync
from src.infrastructure.etl.etl_scheduler import get_etl_scheduler
scheduler = await get_etl_scheduler()
scheduler.trigger_job('daily_sync')
```

### Issue: Dashboard Not Loading

```bash
# Check Streamlit logs
streamlit run src/presentation/streamlit/app.py --logger.level=debug

# Verify cache initialization
python init_redis_cache.py --stats
```

## Performance Tuning

### PostgreSQL Optimization

```sql
-- Increase shared buffers
ALTER SYSTEM SET shared_buffers = '256MB';

-- Optimize for TimescaleDB
ALTER SYSTEM SET max_worker_processes = 16;
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;

-- Reload configuration
SELECT pg_reload_conf();
```

### Redis Optimization

```bash
# Configure memory policy
redis-cli CONFIG SET maxmemory 4gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Enable RDB snapshots
redis-cli CONFIG SET save "900 1 300 10 60 10000"
```

## Security Considerations

### 1. Network Security

```yaml
# docker-compose.yml
services:
  postgres:
    networks:
      - backend
    expose:
      - "5432"  # Don't expose to host
  
  redis:
    networks:
      - backend
    expose:
      - "6379"  # Don't expose to host

networks:
  backend:
    driver: bridge
```

### 2. Authentication

```bash
# PostgreSQL - Use strong passwords
ALTER USER postgres PASSWORD 'very_secure_password';

# Redis - Enable authentication
redis-cli CONFIG SET requirepass "redis_secure_password"
```

### 3. Encryption

```bash
# Enable SSL for PostgreSQL
openssl req -new -x509 -days 365 -nodes -text \
  -out server.crt -keyout server.key -subj "/CN=postgres"
```

## Maintenance Schedule

### Daily Tasks
- Monitor ETL job status
- Check error logs
- Verify data freshness

### Weekly Tasks
- Review slow query logs
- Check disk usage
- Update continuous aggregates

### Monthly Tasks
- Analyze query performance
- Review cost metrics
- Update documentation

### Quarterly Tasks
- Update dependencies
- Review security patches
- Optimize indexes

## Support

For issues or questions:
1. Check the [troubleshooting guide](#troubleshooting)
2. Review logs in `/logs` directory
3. Contact the development team

## Next Steps

1. Set up monitoring dashboards (Grafana)
2. Configure alerting (PagerDuty/Slack)
3. Implement automated backups
4. Set up CI/CD pipeline
5. Configure load balancing