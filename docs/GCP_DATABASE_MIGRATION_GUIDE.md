# Google Cloud SQL PostgreSQL Migration Guide

## Database Export Completed

The database has been successfully exported with the following details:

- **Export Date**: 2025-01-18 10:01:53
- **Database Name**: abbanoa_processing
- **PostgreSQL Version**: 16 (TimescaleDB)
- **Export Files**:
  - SQL dump: `./database_exports/abbanoa_db_export_20250718_100153.sql` (2.9M)
  - Compressed: `./database_exports/abbanoa_db_export_20250718_100153.sql.gz` (430K)

## Prerequisites for Google Cloud SQL

1. **PostgreSQL Version**: Ensure your Cloud SQL instance uses PostgreSQL 16 or compatible
2. **Extensions Required**:
   - TimescaleDB (for time-series data)
   - pg_stat_statements (for query performance monitoring)
3. **Storage**: At least 10GB recommended for growth
4. **Machine Type**: Minimum db-f1-micro for testing, db-n1-standard-1 for production

## Import Steps

### 1. Create Cloud SQL Instance

```bash
gcloud sql instances create abbanoa-postgres \
  --database-version=POSTGRES_16 \
  --tier=db-n1-standard-1 \
  --region=europe-west1 \
  --network=default \
  --database-flags=shared_preload_libraries=timescaledb
```

### 2. Create Database and User

```bash
# Create database
gcloud sql databases create abbanoa_processing \
  --instance=abbanoa-postgres

# Create user
gcloud sql users create abbanoa_user \
  --instance=abbanoa-postgres \
  --password=<secure-password>
```

### 3. Upload Export to Cloud Storage

```bash
# Create bucket if needed
gsutil mb -l EU gs://abbanoa-db-exports

# Upload the SQL file
gsutil cp ./database_exports/abbanoa_db_export_20250718_100153.sql \
  gs://abbanoa-db-exports/
```

### 4. Import Database

```bash
gcloud sql import sql abbanoa-postgres \
  gs://abbanoa-db-exports/abbanoa_db_export_20250718_100153.sql \
  --database=abbanoa_processing
```

### 5. Enable Required Extensions

Connect to the instance and run:

```sql
-- These should already be created by the import, but verify:
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

## Connection Configuration

Update your `.env` file with the new Cloud SQL connection details:

```env
# Google Cloud SQL Configuration
POSTGRES_HOST=<CLOUD_SQL_PUBLIC_IP>
POSTGRES_PORT=5432
POSTGRES_DB=abbanoa_processing
POSTGRES_USER=abbanoa_user
POSTGRES_PASSWORD=<secure-password>

# For private IP or Cloud SQL Proxy:
# POSTGRES_HOST=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME
```

## Important Considerations

1. **Network Security**:
   - Configure authorized networks for public IP access
   - Or use Cloud SQL Proxy for secure connections
   - Consider using Private IP for production

2. **TimescaleDB Specific**:
   - The export includes TimescaleDB hypertables and continuous aggregates
   - Compression settings are preserved
   - Background jobs will need to be re-enabled after import

3. **Performance Tuning**:
   - Adjust Cloud SQL flags based on workload
   - Monitor with Cloud Monitoring
   - Consider read replicas for scaling

4. **Backup Strategy**:
   - Enable automated backups
   - Set appropriate retention period
   - Test restore procedures

## Verification Steps

After import, verify the database:

```sql
-- Check TimescaleDB version
SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';

-- Verify hypertables
SELECT * FROM timescaledb_information.hypertables;

-- Check data
SELECT COUNT(*) FROM water_infrastructure.sensor_readings;
SELECT COUNT(*) FROM water_infrastructure.nodes;

-- Verify continuous aggregates
SELECT * FROM timescaledb_information.continuous_aggregates;
```

## Troubleshooting

- **Extension Issues**: Install TimescaleDB extension before import if needed
- **Permission Errors**: Ensure user has proper grants
- **Size Limitations**: For large databases, consider using parallel import
- **Circular Dependencies**: The warnings about circular foreign keys in TimescaleDB catalog tables are normal

## Next Steps

1. Update application connection strings
2. Test application connectivity
3. Set up monitoring and alerting
4. Configure backup policies
5. Plan for high availability if needed