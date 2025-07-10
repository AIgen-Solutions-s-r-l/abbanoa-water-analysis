# Operations Guide - Hybrid Data Architecture

This guide provides operational procedures for maintaining and troubleshooting the Abbanoa Water Infrastructure hybrid data system.

## System Overview

### Architecture Components
- **BigQuery**: Historical data archive (cold storage)
- **PostgreSQL/TimescaleDB**: Operational data (warm storage, 90 days)
- **Redis**: Real-time cache (hot storage, 24 hours)
- **ETL Pipeline**: Automated data synchronization
- **Streamlit Dashboard**: User interface

## Daily Operations

### Morning Checklist (9 AM)

1. **Check ETL Job Status**
   ```sql
   -- Connect to PostgreSQL
   psql -h localhost -U postgres -d abbanoa
   
   -- Check overnight sync status
   SELECT job_name, status, started_at, completed_at, records_processed 
   FROM water_infrastructure.etl_jobs 
   WHERE started_at > CURRENT_DATE - INTERVAL '1 day'
   ORDER BY started_at DESC;
   ```

2. **Verify Data Freshness**
   ```sql
   -- Check latest sensor readings
   SELECT node_id, MAX(timestamp) as last_reading 
   FROM water_infrastructure.sensor_readings 
   GROUP BY node_id 
   HAVING MAX(timestamp) < CURRENT_TIMESTAMP - INTERVAL '2 hours';
   ```

3. **Check System Alerts**
   ```sql
   -- Unresolved anomalies
   SELECT COUNT(*), severity 
   FROM water_infrastructure.anomalies 
   WHERE resolved_at IS NULL 
   GROUP BY severity;
   ```

4. **Monitor Cache Health**
   ```bash
   # Redis memory usage
   redis-cli info memory | grep used_memory_human
   
   # Cache hit rate
   redis-cli info stats | grep keyspace_hits
   ```

### Hourly Checks

1. **Real-time Sync Status**
   ```bash
   # Check ETL scheduler logs
   tail -n 100 logs/etl_scheduler.log | grep "Real-time sync"
   ```

2. **Dashboard Performance**
   ```python
   # Check response times in dashboard
   # Navigate to Performance Monitor tab
   # Look for queries >1s
   ```

## Common Operational Tasks

### 1. Manual Data Sync

**Scenario**: Data is missing or ETL job failed

```python
# Run manual sync for specific time range
from src.infrastructure.etl.bigquery_to_postgres_etl import BigQueryToPostgresETL
import asyncio

async def manual_sync():
    etl = BigQueryToPostgresETL()
    await etl.initialize()
    
    # Sync last 48 hours
    stats = await etl.sync_recent_data(hours_back=48, force_refresh=True)
    print(f"Synced {stats['processed_records']} records")

asyncio.run(manual_sync())
```

### 2. Cache Refresh

**Scenario**: Dashboard showing stale data

```bash
# Force cache refresh
python init_redis_cache.py --force --stats

# Or clear specific keys
redis-cli DEL "system:metrics:*"
redis-cli DEL "node:*:latest"
```

### 3. Add New Sensor Node

**Step 1**: Add node to database
```sql
INSERT INTO water_infrastructure.nodes 
(node_id, node_name, node_type, location_name, is_active)
VALUES 
('NEW_NODE_001', 'New Monitoring Station', 'sensor', 'Cagliari', true);
```

**Step 2**: Update node mappings
```python
# Edit src/presentation/streamlit/utils/node_mappings.py
NEW_NODES = {
    # ... existing nodes ...
    "New Monitoring Station": "NEW_NODE_001",
}
```

**Step 3**: Sync historical data
```python
# Sync specific node data
await etl.sync_historical_data(
    start_date=datetime(2024, 1, 1),
    end_date=datetime.now(),
    node_ids=['NEW_NODE_001']
)
```

### 4. Resolve Anomalies

**Step 1**: Review anomaly
```sql
-- Get anomaly details
SELECT * FROM water_infrastructure.anomalies 
WHERE anomaly_id = 12345;
```

**Step 2**: Investigate
```sql
-- Check sensor readings around anomaly time
SELECT * FROM water_infrastructure.sensor_readings
WHERE node_id = 'NODE_001'
AND timestamp BETWEEN '2024-01-15 10:00:00' AND '2024-01-15 12:00:00'
ORDER BY timestamp;
```

**Step 3**: Resolve if false positive
```sql
UPDATE water_infrastructure.anomalies
SET resolved_at = CURRENT_TIMESTAMP,
    metadata = jsonb_set(metadata, '{resolution}', '"False positive - maintenance"')
WHERE anomaly_id = 12345;
```

## Performance Optimization

### 1. Slow Dashboard Queries

**Identify slow queries**:
```sql
-- PostgreSQL slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- queries >1s
ORDER BY mean_exec_time DESC;
```

**Solutions**:
- Check if continuous aggregates need refresh
- Add missing indexes
- Increase cache TTL for slow queries

### 2. High Memory Usage

**Redis memory optimization**:
```bash
# Check memory usage by key pattern
redis-cli --bigkeys

# Set memory limits
redis-cli CONFIG SET maxmemory 4gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

**PostgreSQL memory tuning**:
```sql
-- Adjust work memory for complex queries
ALTER SYSTEM SET work_mem = '256MB';
SELECT pg_reload_conf();
```

### 3. ETL Performance Issues

**Increase parallelism**:
```python
# Edit ETL configuration
ETL_MAX_WORKERS=8  # Increase from 4
ETL_BATCH_SIZE=20000  # Increase from 10000
```

**Optimize BigQuery queries**:
```sql
-- Use partitioning
WHERE DATE(timestamp) = CURRENT_DATE()
-- Instead of
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
```

## Troubleshooting Guide

### Issue: Dashboard Shows "No Data"

1. **Check Redis connection**:
   ```python
   from src.infrastructure.cache.redis_cache_manager import RedisCacheManager
   manager = RedisCacheManager()
   print(manager.redis_client.ping())  # Should return True
   ```

2. **Check PostgreSQL data**:
   ```sql
   SELECT COUNT(*), MAX(timestamp) 
   FROM water_infrastructure.sensor_readings
   WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '1 hour';
   ```

3. **Force cache initialization**:
   ```bash
   python init_redis_cache.py --force
   ```

### Issue: ETL Job Stuck

1. **Check running jobs**:
   ```sql
   SELECT pid, query, state, wait_event_type, wait_event
   FROM pg_stat_activity
   WHERE datname = 'abbanoa' AND state != 'idle';
   ```

2. **Kill stuck queries**:
   ```sql
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE pid = <stuck_pid>;
   ```

3. **Restart ETL scheduler**:
   ```bash
   # Find process
   ps aux | grep etl_scheduler
   
   # Kill and restart
   kill <pid>
   python -m src.infrastructure.etl.etl_scheduler
   ```

### Issue: Anomaly Detection Not Working

1. **Check anomaly detection job**:
   ```python
   from src.infrastructure.etl.etl_scheduler import get_etl_scheduler
   scheduler = await get_etl_scheduler()
   status = scheduler.get_job_status()
   print(status['jobs'])  # Check 'anomaly_detection' job
   ```

2. **Run manual detection**:
   ```python
   await scheduler.trigger_job('anomaly_detection')
   ```

3. **Check detection thresholds**:
   ```sql
   -- Review recent data statistics
   SELECT node_id,
          AVG(flow_rate) as avg_flow,
          STDDEV(flow_rate) as std_flow
   FROM water_infrastructure.sensor_readings
   WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
   GROUP BY node_id;
   ```

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Data Pipeline Health**
   - ETL job success rate (target: >95%)
   - Data latency (target: <30 minutes)
   - Records processed per hour

2. **System Performance**
   - Dashboard response time (target: <1s)
   - Cache hit rate (target: >90%)
   - Database query time (target: <500ms)

3. **Data Quality**
   - Missing data percentage (target: <5%)
   - Anomaly rate (baseline: establish normal)
   - Sensor reading validity

### Setting Up Alerts

**Email alerts for critical issues**:
```python
# Add to ETL scheduler
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = f"[Abbanoa Alert] {subject}"
    msg['From'] = "alerts@abbanoa.it"
    msg['To'] = "ops-team@abbanoa.it"
    
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
```

**Slack integration**:
```python
import requests

def send_slack_alert(message):
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    requests.post(webhook_url, json={"text": message})
```

## Backup and Recovery

### Daily Backups

**PostgreSQL backup**:
```bash
#!/bin/bash
# backup_postgres.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"

pg_dump -h localhost -U postgres abbanoa | \
  gzip > "$BACKUP_DIR/abbanoa_$DATE.sql.gz"

# Keep only last 7 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
```

**Redis backup**:
```bash
# Redis automatically saves to dump.rdb
# Copy to backup location
cp /var/lib/redis/dump.rdb /backups/redis/dump_$(date +%Y%m%d).rdb
```

### Recovery Procedures

**PostgreSQL recovery**:
```bash
# Restore from backup
gunzip < backup.sql.gz | psql -h localhost -U postgres abbanoa
```

**Redis recovery**:
```bash
# Stop Redis
systemctl stop redis

# Copy backup
cp /backups/redis/dump_20240115.rdb /var/lib/redis/dump.rdb

# Start Redis
systemctl start redis
```

## Maintenance Windows

### Weekly Maintenance (Sunday 3-4 AM)

1. **Update continuous aggregates**:
   ```sql
   CALL refresh_continuous_aggregate('sensor_readings_daily', 
     CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE);
   ```

2. **Vacuum and analyze**:
   ```sql
   VACUUM ANALYZE water_infrastructure.sensor_readings;
   ```

3. **Clear old cache data**:
   ```bash
   redis-cli EVAL "
   local keys = redis.call('keys', 'node:*:timeseries')
   for i,k in ipairs(keys) do
     redis.call('zremrangebyscore', k, 0, os.time() - 86400)
   end
   " 0
   ```

### Monthly Maintenance

1. **Review and optimize indexes**:
   ```sql
   -- Find unused indexes
   SELECT schemaname, tablename, indexname, idx_scan
   FROM pg_stat_user_indexes
   WHERE idx_scan = 0;
   ```

2. **Archive old ETL logs**:
   ```sql
   -- Move old logs to archive table
   INSERT INTO water_infrastructure.etl_jobs_archive
   SELECT * FROM water_infrastructure.etl_jobs
   WHERE started_at < CURRENT_DATE - INTERVAL '30 days';
   
   DELETE FROM water_infrastructure.etl_jobs
   WHERE started_at < CURRENT_DATE - INTERVAL '30 days';
   ```

## Emergency Procedures

### System Down - Recovery Steps

1. **Check all services**:
   ```bash
   systemctl status postgresql
   systemctl status redis
   docker ps  # If using Docker
   ```

2. **Start services in order**:
   ```bash
   # 1. PostgreSQL (must be first)
   systemctl start postgresql
   
   # 2. Redis
   systemctl start redis
   
   # 3. ETL Scheduler
   python -m src.infrastructure.etl.etl_scheduler &
   
   # 4. Dashboard
   streamlit run src/presentation/streamlit/app.py
   ```

3. **Verify data flow**:
   ```bash
   # Check recent data
   psql -c "SELECT MAX(timestamp) FROM sensor_readings"
   
   # Check cache
   redis-cli get "system:metrics:1h"
   ```

### Data Corruption Recovery

1. **Identify corrupted data**:
   ```sql
   -- Check for invalid readings
   SELECT * FROM sensor_readings
   WHERE flow_rate < 0 
      OR flow_rate > 10000
      OR pressure < 0 
      OR pressure > 50;
   ```

2. **Restore from BigQuery**:
   ```python
   # Re-sync affected time period
   await etl.sync_historical_data(
     start_date=datetime(2024, 1, 15),
     end_date=datetime(2024, 1, 16),
     node_ids=['affected_node_id']
   )
   ```

## Contact Information

### Escalation Path

1. **Level 1**: Operations Team
   - Email: ops@abbanoa.it
   - Slack: #ops-alerts

2. **Level 2**: Database Administrator
   - Email: dba@abbanoa.it
   - Phone: +39 XXX XXX XXXX

3. **Level 3**: Development Team
   - Email: dev@abbanoa.it
   - On-call: Use PagerDuty

### External Support

- **Google Cloud Support**: [BigQuery issues]
- **TimescaleDB Support**: [PostgreSQL/TimescaleDB issues]
- **Redis Support**: [Redis/caching issues]