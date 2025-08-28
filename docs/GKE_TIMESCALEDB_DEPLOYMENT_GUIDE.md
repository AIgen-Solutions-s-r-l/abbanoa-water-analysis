# GKE TimescaleDB Deployment Guide

Since Google Cloud SQL doesn't support TimescaleDB, we'll deploy PostgreSQL with TimescaleDB on Google Kubernetes Engine (GKE).

## Prerequisites

1. GKE cluster with sufficient resources
2. kubectl configured to access your cluster
3. Google Cloud Storage buckets created:
   - `abbanoa-db-exports` (for initial import)
   - `abbanoa-db-backups` (for ongoing backups)

## Deployment Steps

### 1. Upload Database Export to GCS

First, upload your database export to Google Cloud Storage:

```bash
# Create bucket if needed
gsutil mb -l EU gs://abbanoa-db-exports

# Upload the export file
gsutil cp ./database_exports/abbanoa_db_export_20250718_100153.sql \
  gs://abbanoa-db-exports/
```

### 2. Deploy PostgreSQL/TimescaleDB

Apply all Kubernetes configurations:

```bash
# Create namespace and configs
kubectl apply -f k8s/namespace-and-config.yaml

# IMPORTANT: Edit the secret file first to set secure passwords!
# Edit k8s/namespace-and-config.yaml and change the passwords

# Create storage
kubectl apply -f k8s/storage.yaml

# Deploy PostgreSQL StatefulSet
kubectl apply -f k8s/postgres-statefulset.yaml

# Create services
kubectl apply -f k8s/postgres-service.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres-timescaledb -n abbanoa-data --timeout=300s
```

### 3. Import Database

Edit the import job configuration first:

```bash
# Edit k8s/database-import-job.yaml
# Update GCS_BUCKET and EXPORT_TIMESTAMP to match your export

# Run the import job
kubectl apply -f k8s/database-import-job.yaml

# Monitor the import
kubectl logs -f job/database-import -n abbanoa-data
```

### 4. Set Up Automated Backups

```bash
# Edit k8s/backup-cronjob.yaml
# Update GCS_BACKUP_BUCKET to your backup bucket

# Create backup CronJob
kubectl apply -f k8s/backup-cronjob.yaml
```

### 5. Configure Application Access

#### Option A: Internal Access (Recommended)

For applications running in the same GKE cluster:

```env
POSTGRES_HOST=postgres-service.abbanoa-data.svc.cluster.local
POSTGRES_PORT=5432
POSTGRES_DB=abbanoa_processing
POSTGRES_USER=abbanoa_user
POSTGRES_PASSWORD=<your-secure-password>
```

#### Option B: External Access

If you need external access:

```bash
# Get the external IP
kubectl get service postgres-external -n abbanoa-data

# Use the EXTERNAL-IP in your connection string
```

## Monitoring and Maintenance

### Check Database Status

```bash
# Check pod status
kubectl get pods -n abbanoa-data

# Check logs
kubectl logs -f postgres-timescaledb-0 -n abbanoa-data

# Connect to database
kubectl exec -it postgres-timescaledb-0 -n abbanoa-data -- psql -U abbanoa_user -d abbanoa_processing
```

### Verify TimescaleDB

```sql
-- Check TimescaleDB version
SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';

-- List hypertables
SELECT * FROM timescaledb_information.hypertables;

-- Check continuous aggregates
SELECT * FROM timescaledb_information.continuous_aggregates;

-- Check compression status
SELECT * FROM timescaledb_information.compressed_chunks;
```

### Scaling Storage

If you need more storage:

```bash
# Edit the PVC size in k8s/storage.yaml
# Then apply the patch
kubectl patch pvc postgres-data-pvc -n abbanoa-data -p '{"spec":{"resources":{"requests":{"storage":"200Gi"}}}}'
```

## Security Considerations

1. **Passwords**: Always use strong passwords and consider using Kubernetes secrets management
2. **Network Policy**: Consider implementing network policies to restrict access
3. **TLS**: For production, enable TLS for PostgreSQL connections
4. **RBAC**: Implement proper RBAC for database access

## High Availability Options

For production environments, consider:

1. **Patroni**: PostgreSQL HA solution for Kubernetes
2. **CloudNativePG**: Kubernetes operator for PostgreSQL
3. **Zalando PostgreSQL Operator**: Another popular option

## Backup and Recovery

### Manual Backup

```bash
kubectl create job --from=cronjob/postgres-backup manual-backup-$(date +%Y%m%d) -n abbanoa-data
```

### Restore from Backup

```bash
# Download backup from GCS
gsutil cp gs://abbanoa-db-backups/backups/abbanoa_backup_TIMESTAMP.sql.gz /tmp/

# Restore
gunzip -c /tmp/abbanoa_backup_TIMESTAMP.sql.gz | \
  kubectl exec -i postgres-timescaledb-0 -n abbanoa-data -- \
  psql -U abbanoa_user -d abbanoa_processing
```

## Cost Optimization

1. Use preemptible nodes for non-critical workloads
2. Consider using SSD persistent disks only for data volumes
3. Set appropriate resource requests/limits
4. Use node auto-scaling

## Troubleshooting

### Pod not starting
- Check events: `kubectl describe pod postgres-timescaledb-0 -n abbanoa-data`
- Check PVC binding: `kubectl get pvc -n abbanoa-data`

### Connection issues
- Verify service endpoints: `kubectl get endpoints -n abbanoa-data`
- Check network policies if implemented

### Performance issues
- Monitor resource usage: `kubectl top pod -n abbanoa-data`
- Check PostgreSQL logs for slow queries
- Verify TimescaleDB background workers are running