#!/bin/bash
# Run API with permanent GCP authentication

# Check if service account key exists
KEY_FILE="bigquery-service-account-key.json"
if [ ! -f "$KEY_FILE" ]; then
    echo "Error: Service account key not found: $KEY_FILE"
    echo "Please run: ./scripts/setup-gcp-auth.sh first"
    exit 1
fi

# Stop and remove existing container
docker stop abbanoa-api 2>/dev/null || true
docker rm abbanoa-api 2>/dev/null || true

# Run with service account authentication
echo "Starting API with BigQuery authentication..."
docker run -d \
    --name abbanoa-api \
    -p 8000:8000 \
    -v "$(pwd)/${KEY_FILE}:/app/credentials.json:ro" \
    -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
    -e GOOGLE_CLOUD_PROJECT=abbanoa-464816 \
    -e BIGQUERY_PROJECT_ID=abbanoa-464816 \
    -e BIGQUERY_DATASET_ID=water_infrastructure \
    -e LOG_LEVEL=INFO \
    abbanoa-api:latest

echo "API started with permanent authentication"
echo "Access at: http://localhost:8000"
echo "Docs at: http://localhost:8000/docs"
echo ""
echo "View logs: docker logs -f abbanoa-api"