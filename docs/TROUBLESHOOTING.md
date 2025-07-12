# Troubleshooting Guide

This guide helps resolve common issues encountered while using the Abbanoa Water Infrastructure Analytics Platform.

## Quick Diagnostics

Before diving into specific issues, run these quick diagnostic commands:

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs --tail=50 dashboard
docker-compose logs --tail=50 api
docker-compose logs --tail=50 processing

# Test API connectivity
curl http://localhost:8000/health

# Test database connectivity
python -c "from src.infrastructure.database.postgres_manager import PostgresManager; print('DB OK')"
```

## Common Issues

### 1. ModuleNotFoundError: No module named 'src'

**Problem**: Python can't find the project modules when running Streamlit or other scripts.

**Symptoms**:
```
ModuleNotFoundError: No module named 'src'
ModuleNotFoundError: No module named 'src.presentation'
```

**Solutions**:

#### Option 1: Use the provided run script (Recommended)
```bash
./run_dashboard.sh
```

#### Option 2: Set PYTHONPATH manually
```bash
export PYTHONPATH=/path/to/abbanoa-water-analysis:$PYTHONPATH
poetry run streamlit run src/presentation/streamlit/app.py
```

#### Option 3: Use the Python launcher
```bash
poetry run python run_streamlit.py
```

**Root Cause**: Python needs to know where to find the project modules. The provided scripts handle this automatically.

### 2. Docker Container Issues

#### Container Won't Start

**Check container status**:
```bash
docker-compose ps
docker-compose logs [service_name]
```

**Common fixes**:
```bash
# Stop all containers
docker-compose down

# Remove containers and rebuild
docker-compose down --volumes
docker-compose build --no-cache
docker-compose up -d

# Check resource usage
docker system df
docker system prune  # If low on space
```

#### Port Already in Use

**Symptoms**:
```
ERROR: for dashboard  Cannot start service dashboard: 
Ports are not available: listen tcp 0.0.0.0:8501: bind: address already in use
```

**Solutions**:
```bash
# Find process using the port
lsof -i :8501
sudo netstat -tulpn | grep :8501

# Kill the process
kill -9 [PID]

# Or change port in docker-compose.yml
```

### 3. Database Connection Issues

#### PostgreSQL Connection Failed

**Symptoms**:
```
psycopg2.OperationalError: could not connect to server
Connection refused
```

**Solutions**:

1. **Check PostgreSQL container**:
   ```bash
   docker-compose logs postgres
   ```

2. **Verify connection string**:
   ```bash
   echo $POSTGRES_CONNECTION_STRING
   ```

3. **Test connection manually**:
   ```bash
   psql "postgresql://user:password@localhost:5432/abbanoa_db"
   ```

4. **Reset database**:
   ```bash
   docker-compose down postgres
   docker volume rm abbanoa_postgres_data
   docker-compose up -d postgres
   ```

#### BigQuery Authentication Issues

**Symptoms**:
```
google.auth.exceptions.DefaultCredentialsError
403 Forbidden: Access denied
```

**Solutions**:

1. **Check authentication**:
   ```bash
   gcloud auth list
   gcloud auth application-default login
   ```

2. **Verify project ID**:
   ```bash
   gcloud config get-value project
   echo $BIGQUERY_PROJECT_ID
   ```

3. **Check service account**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
   ```

### 4. Dashboard Loading Issues

#### Dashboard Loads Slowly

**Symptoms**: Dashboard takes >10 seconds to load

**Solutions**:

1. **Check cache status**:
   ```bash
   redis-cli ping
   redis-cli info memory
   ```

2. **Monitor API response times**:
   ```bash
   curl -w "@curl-format.txt" http://localhost:8000/api/v1/nodes
   ```

3. **Check data volume**:
   ```bash
   # Check BigQuery table size
   bq query "SELECT COUNT(*) FROM water_infrastructure.sensor_readings"
   ```

#### Dashboard Shows No Data

**Symptoms**: Dashboard loads but shows "No data available"

**Solutions**:

1. **Check data in BigQuery**:
   ```bash
   bq query "SELECT * FROM water_infrastructure.sensor_readings LIMIT 5"
   ```

2. **Verify ETL process**:
   ```bash
   docker-compose logs processing
   python scripts/diagnose_data_issues.py
   ```

3. **Check date filters**: Ensure selected date range contains data

### 5. API Issues

#### API Returns 500 Internal Server Error

**Check API logs**:
```bash
docker-compose logs api
```

**Common causes**:
- Database connection issues
- BigQuery authentication problems
- Missing environment variables
- Invalid data in requests

#### API Authentication Failed

**Symptoms**:
```
401 Unauthorized
403 Forbidden
```

**Solutions**:
```bash
# Check JWT token validity
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/status

# Generate new token
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"
```

### 6. Data Processing Issues

#### ETL Pipeline Fails

**Check processing logs**:
```bash
docker-compose logs processing
tail -f logs/processing/processing_service.log
```

**Common issues**:
- Invalid CSV format in RAWDATA directory
- Insufficient disk space
- Database connection timeout
- Memory exhaustion

**Solutions**:
```bash
# Check disk space
df -h

# Check memory usage
free -m
docker stats

# Restart processing service
docker-compose restart processing
```

#### Data Quality Issues

**Symptoms**: Low quality scores or missing sensor readings

**Diagnostic commands**:
```bash
# Run data quality analysis
python scripts/diagnose_data_issues.py

# Check recent data quality
python -c "
from src.infrastructure.database.postgres_manager import PostgresManager
pm = PostgresManager()
result = pm.execute_query('SELECT * FROM data_quality_metrics ORDER BY timestamp DESC LIMIT 5')
print(result)
"
```

### 7. Performance Issues

#### High Memory Usage

**Monitor memory**:
```bash
docker stats
htop  # If installed
```

**Solutions**:
```bash
# Reduce processing batch size
export BATCH_SIZE=100

# Increase Docker memory limit
# Edit docker-compose.yml to add memory limits

# Clean up unused data
redis-cli FLUSHDB  # Clear cache
```

#### Slow Query Performance

**Check slow queries**:
```bash
# PostgreSQL slow query log
docker-compose exec postgres psql -U username -d dbname -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"
```

**Optimize performance**:
```bash
# Rebuild TimescaleDB indexes
psql -c "REINDEX DATABASE abbanoa_db;"

# Update table statistics
psql -c "ANALYZE;"
```

### 8. Security Issues

#### SSL/TLS Certificate Errors

**Symptoms**:
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions**:
```bash
# Update certificates
pip install --upgrade certifi

# For development, temporarily disable SSL verification
export PYTHONHTTPSVERIFY=0  # NOT for production
```

#### Permission Denied Errors

**Check file permissions**:
```bash
ls -la logs/
chmod 755 logs/
chown $USER:$USER logs/
```

### 9. Environment-Specific Issues

#### Development Environment

**Poetry issues**:
```bash
# Reinstall dependencies
poetry install --no-cache

# Update poetry
poetry self update

# Clear poetry cache
poetry cache clear --all .
```

#### Production Environment

**Docker production issues**:
```bash
# Check production configuration
docker-compose -f docker-compose.prod.yml config

# Monitor production logs
docker-compose -f docker-compose.prod.yml logs -f

# Health check all services
curl https://api.curator.aigensolutions.it/health
```

### 10. Data Migration Issues

#### Migration Script Fails

**Check migration status**:
```bash
python test_migration.py
python scripts/diagnose_data_issues.py
```

**Common solutions**:
```bash
# Reset migration state
rm -rf migrations/versions/*  # Backup first!
alembic stamp head

# Run migration manually
alembic upgrade head
```

## Advanced Debugging

### Enable Debug Logging

1. **For Dashboard**:
   ```python
   # In app.py, add:
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **For API**:
   ```bash
   export LOG_LEVEL=DEBUG
   docker-compose restart api
   ```

3. **For Processing Service**:
   ```bash
   export PROCESSING_LOG_LEVEL=DEBUG
   docker-compose restart processing
   ```

### Performance Profiling

**Profile Python code**:
```bash
# Install profiling tools
pip install py-spy

# Profile running process
py-spy top --pid [PID]
py-spy record -o profile.svg --pid [PID]
```

**Profile database queries**:
```sql
-- Enable query statistics
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- View slow queries
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
```

### Memory Debugging

**Check for memory leaks**:
```bash
# Monitor memory over time
while true; do
  docker stats --no-stream | grep dashboard
  sleep 60
done
```

**Profile memory usage**:
```python
# Add to Python code
import tracemalloc
tracemalloc.start()

# Your code here

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
```

## Getting Help

### Log Collection

When reporting issues, collect these logs:

```bash
# Create debug bundle
mkdir debug_bundle_$(date +%Y%m%d_%H%M%S)
cd debug_bundle_*

# System info
docker --version > system_info.txt
docker-compose --version >> system_info.txt
python --version >> system_info.txt

# Service logs
docker-compose logs > docker_logs.txt
cp logs/dashboard.log .
cp logs/processing/processing_service.log .

# Configuration
docker-compose config > docker_config.yml
env | grep -E "(BIGQUERY|POSTGRES|REDIS)" > env_vars.txt

# Database status
psql -c "\dt" > db_tables.txt
redis-cli info > redis_info.txt
```

### Contact Information

- **Technical Support**: tech-support@abbanoa.it
- **GitHub Issues**: [Create an issue](https://github.com/abbanoa/water-infrastructure/issues)
- **Emergency Support**: +39 xxx xxx xxxx (24/7 on-call)

### Before Contacting Support

1. **Check this troubleshooting guide**
2. **Review recent logs** for error messages
3. **Try basic fixes** (restart services, check connections)
4. **Collect debug information** as described above
5. **Include specific error messages** and steps to reproduce

---

*This guide is updated regularly. Last updated: July 2025*