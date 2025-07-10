#!/bin/bash

# Script to monitor the processing services

echo "📊 Abbanoa Processing Services Monitor"
echo "====================================="
echo ""

# Check if services are running
if ! docker-compose -f docker-compose.processing.yml ps | grep -q "Up"; then
    echo "❌ Services are not running. Start them with: ./scripts/start_processing_services.sh"
    exit 1
fi

# Function to check service health
check_health() {
    local service=$1
    local url=$2
    local response=$(curl -s -o /dev/null -w "%{http_code}" $url 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo "✅ $service: Healthy"
    else
        echo "❌ $service: Unhealthy (HTTP $response)"
    fi
}

echo "🔍 Service Health:"
check_health "API" "http://localhost:8000/health"
echo ""

# Check PostgreSQL
echo "🗄️  PostgreSQL Status:"
docker exec abbanoa-postgres-processing pg_isready -U abbanoa_user -d abbanoa_processing || echo "❌ PostgreSQL not ready"
echo ""

# Check Redis
echo "📦 Redis Status:"
docker exec abbanoa-redis-processing redis-cli ping || echo "❌ Redis not responding"
echo ""

# Show recent processing jobs
echo "⚙️  Recent Processing Jobs:"
docker exec abbanoa-postgres-processing psql -U abbanoa_user -d abbanoa_processing -c \
    "SELECT job_type, status, created_at, completed_at 
     FROM water_infrastructure.processing_jobs 
     ORDER BY created_at DESC LIMIT 5;" 2>/dev/null || echo "No job data available yet"
echo ""

# Show active ML models
echo "🤖 Active ML Models:"
docker exec abbanoa-postgres-processing psql -U abbanoa_user -d abbanoa_processing -c \
    "SELECT model_type, version, status, created_at 
     FROM water_infrastructure.ml_models 
     WHERE is_active = TRUE;" 2>/dev/null || echo "No active models yet"
echo ""

# Show container resource usage
echo "💻 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
    abbanoa-processing abbanoa-api abbanoa-postgres-processing abbanoa-redis-processing

echo ""
echo "📋 For detailed logs, run:"
echo "  docker-compose -f docker-compose.processing.yml logs -f [service_name]"