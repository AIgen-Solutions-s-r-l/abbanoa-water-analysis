#!/bin/bash
cd /home/alessio/Customers/Abbanoa
export PYTHONPATH=/home/alessio/Customers/Abbanoa:$PYTHONPATH

# Set API environment variables
export API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

# Check if API is available
echo "Checking API availability at $API_BASE_URL..."
if curl -s -f "$API_BASE_URL/health" > /dev/null; then
    echo "✅ API is healthy"
else
    echo "❌ API is not available at $API_BASE_URL"
    echo "Please ensure the processing services are running:"
    echo "  docker compose -f docker-compose.processing.yml up -d"
    exit 1
fi

# Use poetry environment with dependencies installed
echo "Using poetry environment..."
echo "Starting Streamlit dashboard (API mode)..."
poetry run streamlit run src/presentation/streamlit/app_api.py --server.port 8502 --server.address 127.0.0.1 --theme.base="light"
