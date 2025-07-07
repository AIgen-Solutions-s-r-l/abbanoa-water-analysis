#!/bin/bash

# Script to run the API in Docker

echo "🚀 Starting Abbanoa API in Docker..."

# Build the Docker image
echo "Building Docker image..."
docker build -f Dockerfile.api -t abbanoa-api:latest .

# Check if container is already running
if [ "$(docker ps -q -f name=abbanoa-api)" ]; then
    echo "Stopping existing container..."
    docker stop abbanoa-api
    docker rm abbanoa-api
fi

# Run the container
echo "Starting API container..."
docker run -d \
    --name abbanoa-api \
    -p 8000:8000 \
    -e GOOGLE_CLOUD_PROJECT=abbanoa-464816 \
    -e BIGQUERY_PROJECT_ID=abbanoa-464816 \
    -e BIGQUERY_DATASET_ID=water_infrastructure \
    -v ~/.config/gcloud:/home/apiuser/.config/gcloud:ro \
    abbanoa-api:latest

# Wait for container to be healthy
echo "Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/ > /dev/null; then
        echo "✅ API is ready at http://localhost:8000"
        echo ""
        echo "📊 View logs: docker logs -f abbanoa-api"
        echo "🛑 Stop API: docker stop abbanoa-api"
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo ""
echo "❌ API failed to start. Check logs: docker logs abbanoa-api"
exit 1