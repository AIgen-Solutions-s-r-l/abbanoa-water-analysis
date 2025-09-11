#!/bin/bash
# Cleanup script for API processes
# Ensures no orphaned uvicorn processes are left running

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to log with timestamp
log() {
    echo -e "[$(date '+%H:%M:%S')] $1"
}

# Function to check if process exists
process_exists() {
    kill -0 "$1" 2>/dev/null
}

# Function to terminate process gracefully
terminate_process() {
    local pid=$1
    local name=${2:-"Process"}
    
    if [ -z "$pid" ]; then
        log "${YELLOW}No PID provided for $name${NC}"
        return 1
    fi
    
    if process_exists "$pid"; then
        log "${YELLOW}Terminating $name (PID: $pid)${NC}"
        
        # Try graceful shutdown first (SIGTERM)
        if kill -TERM "$pid" 2>/dev/null; then
            log "Sent TERM signal to $name"
            
            # Wait up to 5 seconds for graceful shutdown
            local count=0
            while [ $count -lt 5 ] && process_exists "$pid"; do
                sleep 1
                count=$((count + 1))
                echo -n "."
            done
            echo ""
            
            # If still running, force kill
            if process_exists "$pid"; then
                log "${YELLOW}Process still running, sending KILL signal${NC}"
                kill -KILL "$pid" 2>/dev/null || true
                sleep 1
            fi
            
            if ! process_exists "$pid"; then
                log "${GREEN}✓ $name terminated successfully${NC}"
                return 0
            else
                log "${RED}✗ Failed to terminate $name${NC}"
                return 1
            fi
        else
            log "${YELLOW}$name already terminated${NC}"
            return 0
        fi
    else
        log "${YELLOW}$name (PID: $pid) not found or already terminated${NC}"
        return 0
    fi
}

# Main cleanup function
cleanup_api() {
    log "${YELLOW}🧹 Starting API cleanup${NC}"
    
    local api_pid=""
    local cleanup_success=true
    
    # 1. Try to get PID from file
    if [ -f "api.pid" ]; then
        api_pid=$(cat api.pid)
        log "Found API PID from file: $api_pid"
    fi
    
    # 2. Try environment variable if no PID file
    if [ -z "$api_pid" ] && [ ! -z "$API_PID" ]; then
        api_pid=$API_PID
        log "Found API PID from environment: $api_pid"
    fi
    
    # 3. Try to find uvicorn process if no PID
    if [ -z "$api_pid" ]; then
        log "${YELLOW}No PID found, searching for uvicorn processes${NC}"
        api_pid=$(pgrep -f "uvicorn.*app_postgres:app" | head -1)
        
        if [ ! -z "$api_pid" ]; then
            log "Found uvicorn process: $api_pid"
        fi
    fi
    
    # 4. Terminate the API process
    if [ ! -z "$api_pid" ]; then
        terminate_process "$api_pid" "API Server" || cleanup_success=false
    else
        log "${YELLOW}No API process found to terminate${NC}"
    fi
    
    # 5. Clean up any remaining uvicorn processes
    local remaining_pids=$(pgrep -f "uvicorn.*app_postgres:app" || true)
    if [ ! -z "$remaining_pids" ]; then
        log "${YELLOW}Found remaining uvicorn processes, cleaning up${NC}"
        for pid in $remaining_pids; do
            terminate_process "$pid" "Uvicorn worker" || true
        done
    fi
    
    # 6. Clean up PID file
    if [ -f "api.pid" ]; then
        rm -f api.pid
        log "Removed PID file"
    fi
    
    # 7. Check for any port 8000 listeners
    if command -v lsof &> /dev/null; then
        local port_users=$(lsof -ti:8000 || true)
        if [ ! -z "$port_users" ]; then
            log "${YELLOW}⚠️ Port 8000 still in use by PIDs: $port_users${NC}"
            for pid in $port_users; do
                local process_name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
                if [[ "$process_name" == *"python"* ]] || [[ "$process_name" == *"uvicorn"* ]]; then
                    log "Terminating $process_name on port 8000"
                    terminate_process "$pid" "Port 8000 listener" || true
                fi
            done
        else
            log "${GREEN}✓ Port 8000 is free${NC}"
        fi
    fi
    
    # 8. Final verification
    local final_check=$(pgrep -f "uvicorn.*app_postgres:app" || true)
    if [ -z "$final_check" ]; then
        log "${GREEN}✅ API cleanup complete - no uvicorn processes found${NC}"
    else
        log "${RED}⚠️ Warning: Some uvicorn processes may still be running${NC}"
        cleanup_success=false
    fi
    
    if $cleanup_success; then
        exit 0
    else
        exit 1
    fi
}

# Handle interrupt signals
trap 'log "${RED}Cleanup interrupted${NC}"; exit 130' INT TERM

# Run cleanup
cleanup_api