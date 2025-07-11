#!/bin/bash

# Get the absolute path of the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Set PYTHONPATH to include the project root
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Set API environment variables
export API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

# Check if API is available
echo "Checking API availability at $API_BASE_URL..."
if curl -s -f "$API_BASE_URL/health" > /dev/null 2>&1; then
    echo "✅ API is healthy"
    USE_API_MODE=true
else
    echo "⚠️  API is not available at $API_BASE_URL"
    echo "Running in standalone mode (without API)..."
    USE_API_MODE=false
fi

# Use poetry environment with dependencies installed
echo "Using poetry environment..."
echo "Working directory: $SCRIPT_DIR"
echo "Python path: $PYTHONPATH"

if [ "$USE_API_MODE" = true ]; then
    echo "Starting Streamlit dashboard (API mode)..."
    poetry run streamlit run src/presentation/streamlit/app_api.py --server.port 8502 --server.address 127.0.0.1 --theme.base="light"
else
    echo "Starting Streamlit dashboard (standalone mode)..."
    poetry run streamlit run src/presentation/streamlit/app.py --server.port 8502 --server.address 127.0.0.1 --theme.base="light"
fi
