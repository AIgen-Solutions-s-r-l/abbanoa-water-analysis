#!/bin/bash
# Lightweight wait-for-api script optimized for CI environments
# Exits successfully when API is ready or fails after timeout

API_URL="${1:-http://localhost:8000/health}"
MAX_WAIT="${2:-30}"

echo "⏳ Waiting for API at $API_URL (max ${MAX_WAIT}s)"

elapsed=0
while [ $elapsed -lt $MAX_WAIT ]; do
    if curl -sf "$API_URL" > /dev/null 2>&1; then
        echo "✅ API ready after ${elapsed}s"
        exit 0
    fi
    
    # Progressive wait: faster initially, slower later
    if [ $elapsed -lt 5 ]; then
        sleep 0.5
        elapsed=$((elapsed + 1))  # Count as 1s for simplicity
    elif [ $elapsed -lt 10 ]; then
        sleep 1
        elapsed=$((elapsed + 1))
    else
        sleep 2
        elapsed=$((elapsed + 2))
    fi
    
    echo -n "."
done

echo ""
echo "❌ API not ready after ${MAX_WAIT}s"

# Try to provide diagnostic info
echo "Diagnostic info:"
curl -v "$API_URL" 2>&1 | head -10 || true
ps aux | grep -E "(uvicorn|fastapi|python.*app)" | grep -v grep || true

exit 1