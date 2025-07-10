# Hybrid Data Architecture Documentation

## Overview

The Abbanoa Water Infrastructure system uses a sophisticated three-tier hybrid data architecture that combines BigQuery, PostgreSQL/TimescaleDB, and Redis to provide optimal performance, cost-efficiency, and scalability.

## Architecture Diagram

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│   Data Sources      │     │   Processing Layer   │     │   Presentation      │
├─────────────────────┤     ├──────────────────────┤     ├─────────────────────┤
│                     │     │                      │     │                     │
│  CSV Files ────────►│     │  ETL Pipeline        │     │  Streamlit          │
│                     │     │  - Daily sync        │     │  Dashboard          │
│  IoT Sensors ──────►│────►│  - Real-time sync    │────►│                     │
│                     │     │  - Data validation   │     │  - Overview         │
│  Manual Entry ─────►│     │  - Quality checks    │     │  - Anomalies        │
│                     │     │                      │     │  - Forecasts        │
└─────────────────────┘     └──────────────────────┘     └─────────────────────┘
                                      │
                                      ▼
        ┌──────────────────────────────────────────────────────────┐
        │                    Data Storage Tiers                     │
        ├──────────────────────────────────────────────────────────┤
        │                                                           │
        │  ┌─────────────┐   ┌──────────────────┐   ┌────────────┐│
        │  │   Redis     │   │   PostgreSQL/    │   │  BigQuery  ││
        │  │   (Hot)     │   │   TimescaleDB    │   │   (Cold)   ││
        │  │             │◄──│     (Warm)       │◄──│            ││
        │  │ Last 24h    │   │   Last 90 days   │   │ Historical ││
        │  │ Real-time   │   │   Operational    │   │  Archive   ││
        │  │ <100ms      │   │   <500ms         │   │  <5s       ││
        │  └─────────────┘   └──────────────────┘   └────────────┘│
        │         ▲                   ▲                     ▲       │
        └─────────┼───────────────────┼─────────────────────┼───────┘
                  │                   │                     │
                  └───────────────────┴─────────────────────┘
                           Hybrid Data Service
```

## Three-Tier Storage Strategy

### 1. Hot Tier - Redis (In-Memory Cache)
- **Purpose**: Real-time data access and dashboard performance
- **Data Age**: Last 24 hours
- **Response Time**: <100ms
- **Use Cases**:
  - Current sensor readings
  - Active alerts and anomalies
  - Pre-computed dashboard metrics
  - User session data
  - Real-time WebSocket updates

### 2. Warm Tier - PostgreSQL/TimescaleDB
- **Purpose**: Operational data and analytics
- **Data Age**: Last 90 days
- **Response Time**: <500ms
- **Use Cases**:
  - Time-series queries
  - Aggregated metrics
  - ML model results
  - Anomaly history
  - Report generation

### 3. Cold Tier - BigQuery
- **Purpose**: Historical archive and batch analytics
- **Data Age**: All historical data
- **Response Time**: <5 seconds
- **Use Cases**:
  - Long-term trends
  - ML model training
  - Compliance reporting
  - Data export

## Data Flow Patterns

### Write-Through Cache Pattern
```python
New Sensor Reading
    ↓
Redis (Immediate)
    ↓
Write Buffer
    ↓
PostgreSQL (Batch every 5 min)
    ↓
BigQuery (Daily ETL)
```

### Read Pattern (Tiered Fallback)
```python
Query Request
    ↓
Check Redis → Found? Return
    ↓ Not Found
Check PostgreSQL → Found? Cache in Redis & Return
    ↓ Not Found
Query BigQuery → Cache in Redis & Return
```

## Key Components

### 1. PostgreSQL Schema (`postgres_schema.sql`)
- **Hypertables**: Time-series optimized tables
- **Continuous Aggregates**: Pre-computed 5min, hourly, daily views
- **Compression**: 10:1 ratio for data >7 days old
- **Retention Policies**: Automatic data lifecycle management

### 2. Hybrid Data Service (`hybrid_data_service.py`)
- **Intelligent Routing**: Automatically selects optimal data tier
- **Write Buffer**: Batches writes for efficiency
- **Cache Management**: Handles TTL and invalidation
- **Anomaly Detection**: Real-time processing

### 3. ETL Pipeline (`bigquery_to_postgres_etl.py`)
- **Daily Sync**: Full data synchronization at 2 AM
- **Real-time Sync**: Every 5 minutes for recent data
- **Parallel Processing**: Multi-threaded node synchronization
- **Error Handling**: Automatic retry and logging

### 4. ETL Scheduler (`etl_scheduler.py`)
- **Scheduled Jobs**:
  - Daily sync (2 AM)
  - Real-time sync (every 5 min)
  - Cache refresh (hourly)
  - Anomaly detection (every 15 min)
  - Data quality checks (daily)
  - Cleanup (weekly)

## Performance Optimization

### Query Performance
| Data Age | Storage Tier | Response Time | Query Cost |
|----------|-------------|---------------|------------|
| <24h | Redis | <100ms | Free |
| <90d | PostgreSQL | <500ms | Minimal |
| >90d | BigQuery | <5s | $5/TB |

### Continuous Aggregates
```sql
-- Pre-computed 5-minute aggregates
CREATE MATERIALIZED VIEW sensor_readings_5min
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('5 minutes', timestamp) AS bucket,
    node_id,
    AVG(flow_rate) as avg_flow_rate,
    AVG(pressure) as avg_pressure
FROM sensor_readings
GROUP BY bucket, node_id;
```

### Compression Policy
```sql
-- Compress data older than 7 days
ALTER TABLE sensor_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'node_id'
);
```

## Dashboard Integration

### Cache Initialization
```python
# On dashboard startup
if "initialized" not in st.session_state:
    # Initialize Redis cache (non-blocking)
    asyncio.create_task(
        initialize_cache_on_startup(force_refresh=False)
    )
```

### Conditional Component Loading
```python
# Use Redis-based components when cache is ready
if st.session_state.get("cache_initialized", False):
    from components.overview_tab_redis import OverviewTab
else:
    from components.overview_tab import OverviewTab
```

## Deployment Configuration

### Environment Variables
```bash
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=abbanoa
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Cache Settings
CACHE_TTL_HOURS=24
CACHE_REFRESH_HOURS=6

# BigQuery Configuration
BIGQUERY_PROJECT_ID=abbanoa-464816
BIGQUERY_DATASET_ID=water_infrastructure
BIGQUERY_LOCATION=EU
```

### Docker Compose
```yaml
version: '3.8'
services:
  postgres:
    image: timescale/timescaledb:latest-pg14
    environment:
      POSTGRES_DB: abbanoa
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  streamlit:
    build: .
    depends_on:
      - postgres
      - redis
    environment:
      - POSTGRES_HOST=postgres
      - REDIS_HOST=redis
    ports:
      - "8501:8501"
```

## Monitoring and Maintenance

### Health Checks
```python
# Check system health
async def health_check():
    return {
        "redis": await check_redis_connection(),
        "postgres": await check_postgres_connection(),
        "bigquery": await check_bigquery_connection(),
        "etl_jobs": await get_etl_job_status()
    }
```

### Performance Metrics
- Cache hit rate (target: >90%)
- Query response times
- ETL job success rate
- Data freshness

### Maintenance Tasks
1. **Daily**: Monitor ETL job logs
2. **Weekly**: Check data quality reports
3. **Monthly**: Review storage usage and costs
4. **Quarterly**: Optimize queries and indexes

## Cost Analysis

### Monthly Costs (Estimated)
- **BigQuery Storage**: $10 (1TB archived data)
- **PostgreSQL Instance**: $50 (small cloud instance)
- **Redis Instance**: $20 (2GB memory)
- **Total**: ~$80/month

### Cost Savings
- **Before**: ~$200/month (continuous BigQuery queries)
- **After**: ~$80/month (60% reduction)
- **Performance**: 100x faster dashboard response

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```bash
   # Check Redis is running
   redis-cli ping
   # Should return: PONG
   ```

2. **PostgreSQL Slow Queries**
   ```sql
   -- Check missing indexes
   SELECT * FROM pg_stat_user_tables WHERE seq_scan > 1000;
   ```

3. **ETL Job Failures**
   ```sql
   -- Check job logs
   SELECT * FROM etl_jobs 
   WHERE status = 'failed' 
   ORDER BY started_at DESC;
   ```

## Best Practices

1. **Data Ingestion**
   - Always write to Redis first
   - Use batch inserts for PostgreSQL
   - Schedule BigQuery loads during off-peak

2. **Query Optimization**
   - Use continuous aggregates for time-series
   - Implement proper indexes
   - Monitor slow query logs

3. **Cache Management**
   - Set appropriate TTLs
   - Implement cache warming
   - Monitor memory usage

4. **Error Handling**
   - Implement retry logic
   - Log all failures
   - Set up alerts for critical errors

## Future Enhancements

1. **Redis Cluster**: For high availability
2. **PostgreSQL Replication**: Read replicas for scaling
3. **ML Pipeline Integration**: Real-time predictions
4. **GraphQL API**: For external integrations
5. **Kafka Integration**: For streaming data ingestion