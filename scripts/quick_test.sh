#!/bin/bash
# Quick test script for hybrid architecture

echo "🚀 Abbanoa Hybrid Architecture - Quick Test"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service
check_service() {
    local service=$1
    local port=$2
    local name=$3
    
    echo -n "Checking $name... "
    
    if nc -z localhost $port 2>/dev/null; then
        echo -e "${GREEN}✅ Running on port $port${NC}"
        return 0
    else
        echo -e "${RED}❌ Not running${NC}"
        return 1
    fi
}

# Function to test Redis
test_redis() {
    echo -e "\n${YELLOW}Testing Redis...${NC}"
    
    if command -v redis-cli &> /dev/null; then
        # Test connection
        if redis-cli ping > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Redis connection successful${NC}"
            
            # Test basic operations
            redis-cli set test:key "test_value" > /dev/null
            value=$(redis-cli get test:key)
            redis-cli del test:key > /dev/null
            
            if [ "$value" == "test_value" ]; then
                echo -e "${GREEN}✅ Redis read/write test passed${NC}"
            else
                echo -e "${RED}❌ Redis read/write test failed${NC}"
            fi
            
            # Check memory usage
            memory=$(redis-cli info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
            echo "   Memory usage: $memory"
        else
            echo -e "${RED}❌ Redis connection failed${NC}"
            echo "   Start Redis with: docker run -d -p 6379:6379 redis:7-alpine"
        fi
    else
        echo -e "${YELLOW}⚠️  redis-cli not found, skipping Redis tests${NC}"
    fi
}

# Function to test PostgreSQL
test_postgres() {
    echo -e "\n${YELLOW}Testing PostgreSQL...${NC}"
    
    if command -v psql &> /dev/null; then
        # Test connection and TimescaleDB
        result=$(PGPASSWORD=${POSTGRES_PASSWORD:-postgres} psql -h localhost -U postgres -d abbanoa -t -c "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb');" 2>/dev/null)
        
        if [ "$result" == " t" ]; then
            echo -e "${GREEN}✅ PostgreSQL connection successful${NC}"
            echo -e "${GREEN}✅ TimescaleDB extension found${NC}"
            
            # Check data
            count=$(PGPASSWORD=${POSTGRES_PASSWORD:-postgres} psql -h localhost -U postgres -d abbanoa -t -c "SELECT COUNT(*) FROM water_infrastructure.sensor_readings WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours';" 2>/dev/null | tr -d ' ')
            
            if [ -n "$count" ]; then
                echo "   Recent readings: $count (last 24h)"
            fi
        else
            echo -e "${RED}❌ PostgreSQL connection failed or TimescaleDB not installed${NC}"
            echo "   Start PostgreSQL with: docker-compose up -d postgres"
            echo "   Initialize schema: docker exec -i abbanoa-postgres psql -U postgres < src/infrastructure/database/postgres_schema.sql"
        fi
    else
        echo -e "${YELLOW}⚠️  psql not found, skipping PostgreSQL tests${NC}"
    fi
}

# Function to check Python environment
check_python_env() {
    echo -e "\n${YELLOW}Checking Python environment...${NC}"
    
    # Check if in Poetry environment
    if [ -n "$POETRY_ACTIVE" ]; then
        echo -e "${GREEN}✅ Poetry environment active${NC}"
    else
        echo -e "${YELLOW}⚠️  Not in Poetry environment${NC}"
        echo "   Activate with: poetry shell"
    fi
    
    # Check key packages
    python -c "import redis" 2>/dev/null && echo -e "${GREEN}✅ redis package installed${NC}" || echo -e "${RED}❌ redis package missing${NC}"
    python -c "import asyncpg" 2>/dev/null && echo -e "${GREEN}✅ asyncpg package installed${NC}" || echo -e "${RED}❌ asyncpg package missing${NC}"
    python -c "import google.cloud.bigquery" 2>/dev/null && echo -e "${GREEN}✅ google-cloud-bigquery installed${NC}" || echo -e "${RED}❌ google-cloud-bigquery missing${NC}"
}

# Main execution
echo -e "\n${YELLOW}1. Checking Services${NC}"
echo "===================="

# Check services
redis_running=false
postgres_running=false
dashboard_running=false

check_service "redis" 6379 "Redis" && redis_running=true
check_service "postgres" 5432 "PostgreSQL" && postgres_running=true
check_service "streamlit" 8501 "Dashboard" && dashboard_running=true

# Detailed tests if services are running
if $redis_running; then
    test_redis
fi

if $postgres_running; then
    test_postgres
fi

# Check Python environment
check_python_env

# Check BigQuery credentials
echo -e "\n${YELLOW}2. Checking BigQuery Access${NC}"
echo "==========================="

if [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    if [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
        echo -e "${GREEN}✅ Service account key found${NC}"
    else
        echo -e "${RED}❌ Service account key file not found${NC}"
    fi
else
    # Check for application default credentials
    if gcloud auth application-default print-access-token &> /dev/null; then
        echo -e "${GREEN}✅ Application default credentials found${NC}"
    else
        echo -e "${YELLOW}⚠️  No Google Cloud credentials configured${NC}"
        echo "   Run: gcloud auth application-default login"
    fi
fi

# Summary and recommendations
echo -e "\n${YELLOW}3. Summary${NC}"
echo "=========="

all_good=true

if ! $redis_running; then
    all_good=false
    echo -e "${RED}❌ Redis is not running${NC}"
    echo "   Quick fix: docker run -d -p 6379:6379 redis:7-alpine"
fi

if ! $postgres_running; then
    all_good=false
    echo -e "${RED}❌ PostgreSQL is not running${NC}"
    echo "   Quick fix: docker-compose up -d postgres"
fi

if $all_good; then
    echo -e "\n${GREEN}✅ Core services are running!${NC}"
    
    if ! $dashboard_running; then
        echo -e "\n${YELLOW}To start the dashboard:${NC}"
        echo "   poetry run streamlit run src/presentation/streamlit/app.py"
    fi
    
    echo -e "\n${YELLOW}To run comprehensive tests:${NC}"
    echo "   poetry run python test_hybrid_architecture.py"
    
    echo -e "\n${YELLOW}To initialize data:${NC}"
    echo "   poetry run python init_redis_cache.py --force"
    echo "   poetry run python -m src.infrastructure.etl.bigquery_to_postgres_etl"
else
    echo -e "\n${RED}⚠️  Some services are not running.${NC}"
    echo -e "\n${YELLOW}Quick start with Docker:${NC}"
    echo "   docker-compose up -d"
    echo "   docker exec -i abbanoa-postgres psql -U postgres < src/infrastructure/database/postgres_schema.sql"
    echo "   poetry run python init_redis_cache.py --force"
fi

echo -e "\n${YELLOW}For detailed setup instructions, see:${NC}"
echo "   docs/SETUP_GUIDE.md"