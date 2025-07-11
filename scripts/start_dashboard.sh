#!/bin/bash
# Start script for Abbanoa Dashboard (API Mode)

# Change to project directory
cd /home/alessio/Customers/Abbanoa

# Set environment
export PYTHONPATH=/home/alessio/Customers/Abbanoa:$PYTHONPATH
export API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

# Stop any existing dashboard
echo "Stopping any existing dashboard..."
pkill -f "streamlit.*app.py.*8502" || true
pkill -f "streamlit.*app_api.py.*8502" || true
sleep 2

# Check if API is available
echo "Checking API availability at $API_BASE_URL..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s -f "$API_BASE_URL/health" > /dev/null; then
        echo "✅ API is healthy"
        break
    else
        echo "⏳ Waiting for API... (attempt $((attempt+1))/$max_attempts)"
        sleep 5
        attempt=$((attempt+1))
    fi
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ API is not available after $max_attempts attempts"
    echo "Please ensure the processing services are running:"
    echo "  docker compose -f docker-compose.processing.yml up -d"
    exit 1
fi

# Start the dashboard
echo "Starting Streamlit dashboard (API mode) on port 8502..."
nohup /home/alessio/.cache/pypoetry/virtualenvs/abbanoa-water-infrastructure-RTCwCU-i-py3.12/bin/streamlit run \
    src/presentation/streamlit/app_api.py \
    --server.port 8502 \
    --server.address 127.0.0.1 \
    --theme.base=light \
    > /home/alessio/Customers/Abbanoa/logs/dashboard.log 2>&1 &

echo "Dashboard PID: $!"
echo "Dashboard started. Logs: /home/alessio/Customers/Abbanoa/logs/dashboard.log"
echo "Access at: https://curator.aigensolutions.it"