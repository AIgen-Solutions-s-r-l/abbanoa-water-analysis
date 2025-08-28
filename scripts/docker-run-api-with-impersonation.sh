#!/bin/bash
# Run API with user impersonation (no service account key needed)

# Check if user is authenticated
if ! gcloud auth list --filter="status:ACTIVE" --format="value(account)" | grep -q "@"; then
    echo "Error: Not authenticated with gcloud"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Check if gcloud config directory exists
if [ ! -d ~/.config/gcloud ]; then
    echo "Error: gcloud config directory not found"
    echo "Please run: gcloud auth application-default login"
    exit 1
fi

# Stop and remove existing container
docker stop abbanoa-api 2>/dev/null || true
docker rm abbanoa-api 2>/dev/null || true

# Set impersonation (optional - can be set globally)
echo "Setting up service account impersonation..."
gcloud config set auth/impersonate_service_account bigquery-service-account@abbanoa-464816.iam.gserviceaccount.com

echo "Starting API with user impersonation..."
docker run -d \
    --name abbanoa-api \
    -p 8000:8000 \
    -v ~/.config/gcloud:/home/apiuser/.config/gcloud:ro \
    -e GOOGLE_APPLICATION_CREDENTIALS=/home/apiuser/.config/gcloud/application_default_credentials.json \
    -e GOOGLE_CLOUD_PROJECT=abbanoa-464816 \
    -e BIGQUERY_PROJECT_ID=abbanoa-464816 \
    -e BIGQUERY_DATASET_ID=water_infrastructure \
    -e LOG_LEVEL=INFO \
    -e BIGQUERY_QUERY_TIMEOUT_MS=30000 \
    -e BIGQUERY_CONNECTION_TIMEOUT_MS=60000 \
    abbanoa-api:latest

echo "✅ API started with user impersonation (no service account key needed)"
echo ""
echo "Access at: http://localhost:8000"
echo "Docs at: http://localhost:8000/docs"
echo "Health check: curl http://localhost:8000/health"
echo ""
echo "View logs: docker logs -f abbanoa-api"
echo ""
echo "This method:"
echo "- ✅ No service account keys needed"
echo "- ✅ Uses your user credentials with impersonation"
echo "- ✅ More secure than permanent keys"
echo "- ⚠️  Requires you to be authenticated with gcloud"