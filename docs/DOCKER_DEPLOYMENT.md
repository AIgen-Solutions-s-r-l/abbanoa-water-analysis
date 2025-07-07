# Docker Deployment Guide

## Quick Start

### Run API with Docker Compose (Recommended)

```bash
# Start the API service
docker-compose -f docker-compose-api-only.yml up -d

# View logs
docker-compose -f docker-compose-api-only.yml logs -f

# Stop the service
docker-compose -f docker-compose-api-only.yml down
```

### Run with Shell Script

```bash
# Make script executable
chmod +x docker-run-api.sh

# Run the API
./docker-run-api.sh
```

## Docker Images

### API Image (`Dockerfile.api`)
- Base: Python 3.12-slim
- Multi-stage build for smaller image
- Non-root user for security
- Health checks included
- Auto-restart on failure

### Dashboard Image (`Dockerfile.dashboard`)
- Base: Python 3.12-slim  
- Includes Streamlit configuration
- Can connect to API container

## Environment Variables

### Required
- `GOOGLE_CLOUD_PROJECT`: GCP project ID (default: abbanoa-464816)
- `BIGQUERY_PROJECT_ID`: BigQuery project (default: abbanoa-464816)
- `BIGQUERY_DATASET_ID`: Dataset name (default: water_infrastructure)

### Optional
- `LOG_LEVEL`: Logging level (default: INFO)
- `PORT`: API port (default: 8000)
- `BIGQUERY_LOCATION`: BigQuery location (default: EU)

## Google Cloud Authentication

The Docker setup supports multiple authentication methods:

### 1. Application Default Credentials (Recommended for Development)
```bash
# Login with gcloud
gcloud auth application-default login

# The container will use ~/.config/gcloud
```

### 2. Service Account (Recommended for Production)
```bash
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Run with mounted credentials
docker run -v $GOOGLE_APPLICATION_CREDENTIALS:/app/credentials.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  abbanoa-api:latest
```

### 3. Workload Identity (GKE/Cloud Run)
No configuration needed - handled automatically by GCP

## Deployment to Google Cloud Run

### Prerequisites
```bash
# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Set default project
gcloud config set project abbanoa-464816
```

### Deploy with Cloud Build
```bash
# Submit build and deploy
gcloud builds submit --config cloudbuild.yaml

# Or deploy manually
gcloud run deploy abbanoa-api \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated
```

### View Deployed Service
```bash
# Get service URL
gcloud run services describe abbanoa-api --region europe-west1 --format 'value(status.url)'

# View logs
gcloud run logs read --service abbanoa-api --region europe-west1
```

## Docker Commands Reference

### Build Images
```bash
# Build API image
docker build -f Dockerfile.api -t abbanoa-api:latest .

# Build dashboard image
docker build -f Dockerfile.dashboard -t abbanoa-dashboard:latest .
```

### Run Containers
```bash
# Run API only
docker run -d -p 8000:8000 --name abbanoa-api \
  -v ~/.config/gcloud:/home/apiuser/.config/gcloud:ro \
  abbanoa-api:latest

# Run with custom environment
docker run -d -p 8000:8000 --name abbanoa-api \
  -e LOG_LEVEL=DEBUG \
  -e BIGQUERY_LOCATION=US \
  abbanoa-api:latest
```

### Container Management
```bash
# View running containers
docker ps

# View logs
docker logs -f abbanoa-api

# Stop container
docker stop abbanoa-api

# Remove container
docker rm abbanoa-api

# Clean up images
docker image prune -a
```

## Production Considerations

### 1. Security
- Always use non-root users in containers ✓
- Mount credentials as read-only ✓
- Use secrets management for sensitive data
- Enable Cloud Run authentication for production

### 2. Performance
- Set appropriate resource limits
- Use connection pooling ✓
- Enable caching where appropriate
- Monitor container metrics

### 3. Monitoring
- Health checks configured at `/health` ✓
- Structured logging enabled ✓
- Integrate with Cloud Logging
- Set up alerts for failures

### 4. Scaling
- Cloud Run auto-scales based on traffic
- Set min/max instances appropriately
- Configure concurrency limits
- Use Cloud Load Balancing for multiple regions

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs abbanoa-api

# Check health
curl http://localhost:8000/health
```

### Authentication errors
```bash
# Verify credentials are mounted
docker exec abbanoa-api ls -la /home/apiuser/.config/gcloud

# Test authentication
docker exec abbanoa-api gcloud auth list
```

### Connection issues
```bash
# Check container network
docker network ls
docker network inspect bridge

# Test from inside container
docker exec abbanoa-api curl http://localhost:8000/
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Build and push to GCR
  run: |
    gcloud builds submit --config cloudbuild.yaml
```

### GitLab CI
```yaml
deploy:
  stage: deploy
  script:
    - gcloud builds submit --config cloudbuild.yaml
```

## Load Testing

```bash
# Simple load test
ab -n 1000 -c 10 http://localhost:8000/health

# More realistic test
hey -z 30s -c 50 http://localhost:8000/api/v1/forecasts/DIST_001/flow_rate
```