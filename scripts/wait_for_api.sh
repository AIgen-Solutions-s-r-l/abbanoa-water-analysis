#!/bin/bash
# Wait for API to be ready with exponential backoff retry mechanism
# Usage: ./wait_for_api.sh [URL] [MAX_ATTEMPTS] [INITIAL_WAIT]

set -e

# Configuration with defaults
API_URL="${1:-http://localhost:8000/health}"
MAX_ATTEMPTS="${2:-30}"
INITIAL_WAIT="${3:-1}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if API is ready
check_api() {
    curl -sfL "$API_URL" > /dev/null 2>&1
    return $?
}

# Function to log with timestamp
log() {
    echo -e "[$(date '+%H:%M:%S')] $1"
}

# Main retry loop with exponential backoff
main() {
    log "${YELLOW}Waiting for API at ${API_URL}${NC}"
    
    attempt=1
    wait_time=$INITIAL_WAIT
    total_wait=0
    
    while [ $attempt -le $MAX_ATTEMPTS ]; do
        if check_api; then
            log "${GREEN}✓ API is ready after ${total_wait}s (attempt $attempt)${NC}"
            exit 0
        fi
        
        if [ $attempt -eq $MAX_ATTEMPTS ]; then
            log "${RED}✗ API failed to start after $MAX_ATTEMPTS attempts (${total_wait}s total)${NC}"
            
            # Try to get more info about the failure
            log "${YELLOW}Attempting to get API status...${NC}"
            curl -vL "$API_URL" 2>&1 | head -20 || true
            
            # Check if process is running
            if command -v lsof &> /dev/null; then
                log "${YELLOW}Checking if anything is listening on port 8000...${NC}"
                lsof -i :8000 || echo "No process found on port 8000"
            fi
            
            exit 1
        fi
        
        log "Attempt $attempt/$MAX_ATTEMPTS failed, waiting ${wait_time}s before retry..."
        sleep $wait_time
        
        # Update counters
        total_wait=$((total_wait + wait_time))
        attempt=$((attempt + 1))
        
        # Exponential backoff with max cap
        if [ $wait_time -lt 8 ]; then
            wait_time=$((wait_time * 2))
        fi
    done
}

# Handle interrupt gracefully
trap 'log "${RED}Interrupted${NC}"; exit 130' INT TERM

# Run main function
main