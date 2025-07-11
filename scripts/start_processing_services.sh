#!/bin/bash

# Script to start the processing services with Docker Compose

set -e

echo "🚀 Starting Abbanoa Processing Services..."

# Check if .env.processing exists
if [ ! -f .env.processing ]; then
    echo "⚠️  .env.processing not found. Creating from example..."
    cp .env.processing.example .env.processing
    echo "📝 Please edit .env.processing with your configuration"
    exit 1
fi

# Load environment variables
export $(cat .env.processing | grep -v '^#' | xargs)

# Check if BigQuery credentials exist or using application default
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "📝 Using application default credentials (gcloud auth)"
    # Check if gcloud is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
        echo "❌ No active gcloud authentication found"
        echo "Please run: gcloud auth application-default login"
        exit 1
    fi
elif [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "❌ BigQuery credentials not found at: $GOOGLE_APPLICATION_CREDENTIALS"
    echo "Please set GOOGLE_APPLICATION_CREDENTIALS in .env.processing"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs/processing models

# Build and start services
echo "🔨 Building Docker images..."
docker compose -f docker-compose.processing.yml build

echo "🚀 Starting services..."
docker compose -f docker-compose.processing.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
docker compose -f docker-compose.processing.yml ps

# Show logs
echo "📋 Recent logs:"
docker compose -f docker-compose.processing.yml logs --tail=20

echo "✅ Processing services started!"
echo ""
echo "📊 Service URLs:"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - PostgreSQL: localhost:5434"
echo "  - Redis: localhost:6382"
echo "  - Nginx: http://localhost:8080"
echo ""
echo "🛠️  Useful commands:"
echo "  - View logs: docker compose -f docker-compose.processing.yml logs -f"
echo "  - Stop services: docker compose -f docker-compose.processing.yml down"
echo "  - View status: docker compose -f docker-compose.processing.yml ps"