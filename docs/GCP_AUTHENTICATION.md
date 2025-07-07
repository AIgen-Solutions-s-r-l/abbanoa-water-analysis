# GCP Authentication Guide for BigQuery

This guide explains how to set up permanent authentication for BigQuery access that doesn't require daily refresh.

## Quick Start

### 1. Create Service Account (One-time setup)

```bash
# Run the setup script
./scripts/setup-gcp-auth.sh
```

This will:
- Create a service account named `bigquery-service-account`
- Grant necessary BigQuery permissions
- Download a key file: `bigquery-service-account-key.json`

### 2. Run API with Authentication

```bash
# Using convenience script
./docker-run-api-with-auth.sh

# Or using Docker Compose
docker-compose -f docker-compose-api-auth.yml up -d
```

## Authentication Methods

### Method 1: Service Account Key (Recommended for Docker)

**Pros:**
- ✅ Never expires (permanent)
- ✅ Works anywhere (on-premises, any cloud)
- ✅ Simple to implement
- ✅ No internet connectivity required after download

**Cons:**
- ⚠️ Security risk if key is exposed
- ⚠️ Requires secure key management
- ⚠️ Manual rotation recommended

**Setup:**
```bash
# Create service account
gcloud iam service-accounts create bigquery-service-account \
    --display-name="BigQuery Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding abbanoa-464816 \
    --member="serviceAccount:bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

# Create key
gcloud iam service-accounts keys create bigquery-key.json \
    --iam-account=bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com
```

**Docker Usage:**
```bash
docker run -v $(pwd)/bigquery-key.json:/app/credentials.json:ro \
    -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
    abbanoa-api:latest
```

### Method 2: Workload Identity Federation (For Production)

**Pros:**
- ✅ Most secure - no keys to manage
- ✅ Automatic token rotation
- ✅ Works with GitHub Actions, AWS, Azure
- ✅ Full audit trail

**Cons:**
- ❌ More complex setup
- ❌ Requires internet connectivity
- ❌ Not suitable for local development

**GitHub Actions Example:**
```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: 'projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github'
    service_account: 'bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com'
```

### Method 3: Cloud Run Native Authentication

**Pros:**
- ✅ Zero configuration
- ✅ Automatic credential management
- ✅ Most secure for GCP deployments
- ✅ Integrated with GCP IAM

**Cons:**
- ❌ Only works on Google Cloud
- ❌ Not suitable for local development

**Deployment:**
```bash
gcloud run deploy abbanoa-api \
    --image gcr.io/abbanoa-464816/abbanoa-api:latest \
    --service-account bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com \
    --region europe-west1
```

## Security Best Practices

### 1. Key Management
```bash
# Set restrictive permissions
chmod 600 bigquery-service-account-key.json

# Store in secure location
mkdir -p ~/.gcp/keys
mv bigquery-service-account-key.json ~/.gcp/keys/
```

### 2. Key Rotation
```bash
# List existing keys
gcloud iam service-accounts keys list \
    --iam-account=bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com

# Delete old key
gcloud iam service-accounts keys delete KEY_ID \
    --iam-account=bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com
```

### 3. Least Privilege

Grant only necessary permissions:
- `roles/bigquery.dataViewer` - Read-only access
- `roles/bigquery.dataEditor` - Read/write access
- `roles/bigquery.jobUser` - Run queries
- `roles/bigquery.user` - Full BigQuery access

### 4. Environment-Specific Accounts

Create separate service accounts for each environment:
```bash
# Development
gcloud iam service-accounts create bigquery-dev

# Staging
gcloud iam service-accounts create bigquery-staging

# Production
gcloud iam service-accounts create bigquery-prod
```

## Troubleshooting

### Check Authentication
```bash
# Test with gcloud
gcloud auth activate-service-account --key-file=bigquery-service-account-key.json
gcloud auth list

# Test with Python
python3 -c "
from google.cloud import bigquery
client = bigquery.Client()
print('Authentication successful!')
print(f'Project: {client.project}')
"
```

### Common Issues

1. **"Permission denied" errors**
   - Check service account has correct roles
   - Verify project ID is correct
   - Ensure dataset exists

2. **"Could not load the default credentials"**
   - Check GOOGLE_APPLICATION_CREDENTIALS path
   - Verify JSON file is valid
   - Ensure file permissions allow reading

3. **"Timeout" errors**
   - Increase timeout values in configuration
   - Check network connectivity
   - Verify BigQuery API is enabled

### Debug Authentication
```python
import os
from google.auth import default
from google.cloud import bigquery

# Check which credentials are being used
credentials, project = default()
print(f"Using project: {project}")
print(f"Credentials type: {type(credentials)}")

# Test BigQuery access
client = bigquery.Client(credentials=credentials, project=project)
datasets = list(client.list_datasets())
print(f"Found {len(datasets)} datasets")
```

## Configuration Options

### Environment Variables
```bash
# Required
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
export GOOGLE_CLOUD_PROJECT=abbanoa-464816

# Optional - for increased timeouts
export BIGQUERY_QUERY_TIMEOUT_MS=30000
export BIGQUERY_CONNECTION_TIMEOUT_MS=60000

# Optional - for proxy environments
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### Docker Environment File (.env)
```env
# Create .env file for Docker
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
GOOGLE_CLOUD_PROJECT=abbanoa-464816
BIGQUERY_PROJECT_ID=abbanoa-464816
BIGQUERY_DATASET_ID=water_infrastructure
BIGQUERY_QUERY_TIMEOUT_MS=30000
LOG_LEVEL=INFO
```

### Python Configuration
```python
# Custom timeout configuration
from google.cloud import bigquery

client = bigquery.Client(
    project="abbanoa-464816",
    credentials=credentials,
    client_options={
        "api_endpoint": "https://bigquery.googleapis.com"
    }
)

# Set query job config
job_config = bigquery.QueryJobConfig(
    use_query_cache=True,
    timeout_ms=30000,  # 30 seconds
    maximum_bytes_billed=10 * 1024 * 1024 * 1024  # 10GB limit
)
```

## Production Deployment

### 1. Google Cloud Run (Recommended)
```bash
# Build and push image
docker build -f Dockerfile.api -t gcr.io/abbanoa-464816/abbanoa-api:latest .
docker push gcr.io/abbanoa-464816/abbanoa-api:latest

# Deploy with service account
gcloud run deploy abbanoa-api \
    --image gcr.io/abbanoa-464816/abbanoa-api:latest \
    --service-account bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com \
    --set-env-vars BIGQUERY_DATASET_ID=water_infrastructure \
    --region europe-west1 \
    --allow-unauthenticated
```

### 2. Kubernetes with Workload Identity
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: bigquery-ksa
  annotations:
    iam.gke.io/gcp-service-account: bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: abbanoa-api
spec:
  template:
    spec:
      serviceAccountName: bigquery-ksa
      containers:
      - name: api
        image: gcr.io/abbanoa-464816/abbanoa-api:latest
        env:
        - name: BIGQUERY_DATASET_ID
          value: water_infrastructure
```

### 3. Docker Swarm/Compose
```yaml
version: '3.8'
services:
  api:
    image: abbanoa-api:latest
    secrets:
      - bigquery_key
    environment:
      GOOGLE_APPLICATION_CREDENTIALS: /run/secrets/bigquery_key
    deploy:
      replicas: 3

secrets:
  bigquery_key:
    file: ./bigquery-service-account-key.json
```

## Monitoring Authentication

### Enable Audit Logs
```bash
# Enable data access logs
gcloud projects add-iam-policy-binding abbanoa-464816 \
    --member="serviceAccount:bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataViewer" \
    --condition=None
```

### Monitor Key Usage
```bash
# View recent authentications
gcloud logging read \
    'resource.type="service_account"
     protoPayload.authenticationInfo.principalEmail="bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com"' \
    --limit 50 \
    --format json
```

### Set Up Alerts
```bash
# Alert on authentication failures
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="BigQuery Auth Failures" \
    --condition-display-name="Auth Failure Rate" \
    --condition-expression='
      resource.type = "bigquery_project"
      AND metric.type = "bigquery.googleapis.com/job/num_failed_jobs"
      AND metric.label.error_type = "auth"
    '
```

## Summary

For your Docker-based deployment, use **Service Account Keys** with the provided scripts:

1. Run `./scripts/setup-gcp-auth.sh` once to create the service account
2. Use `./docker-run-api-with-auth.sh` to run the API with authentication
3. Keep the key file secure and never commit it to version control
4. Rotate keys every 90 days for security

For production on Google Cloud, migrate to **Cloud Run** or **GKE with Workload Identity** for better security and automatic credential management.