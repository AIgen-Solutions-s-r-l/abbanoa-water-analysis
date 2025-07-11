#!/bin/bash
# Run the Streamlit dashboard using API backend

# Set environment variables
export API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
export PYTHONPATH="${PYTHONPATH}:/home/alessio/Customers/Abbanoa"

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

# Run Streamlit with the API-based app
echo "Starting Streamlit dashboard..."
streamlit run src/presentation/streamlit/app_api.py \
    --server.port "${STREAMLIT_PORT:-8501}" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.serverAddress localhost \
    --browser.gatherUsageStats false