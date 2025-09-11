#!/bin/bash
# Setup script for scheduled jobs system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="/root/abbanoa-water-analysis"

echo -e "${BLUE}Setting up Abbanoa Water Analysis Scheduled Jobs System${NC}"
echo "=================================================="

# Create logs directory
echo -e "${YELLOW}Creating logs directory...${NC}"
mkdir -p "$PROJECT_ROOT/logs"
chmod 755 "$PROJECT_ROOT/logs"

# Test database connectivity
echo -e "${YELLOW}Testing database connectivity...${NC}"
cd "$PROJECT_ROOT"
if python3 src/jobs/job_cli.py test; then
    echo -e "${GREEN}✓ Database connectivity test passed${NC}"
else
    echo -e "${RED}✗ Database connectivity test failed${NC}"
    echo "Please check your database configuration and try again."
    exit 1
fi

# Install crontab
echo -e "${YELLOW}Installing crontab jobs...${NC}"
if crontab "$PROJECT_ROOT/config/crontab.jobs"; then
    echo -e "${GREEN}✓ Crontab jobs installed${NC}"
else
    echo -e "${RED}✗ Failed to install crontab jobs${NC}"
    exit 1
fi

# Verify crontab installation
echo -e "${YELLOW}Verifying crontab installation...${NC}"
echo "Current crontab:"
crontab -l | grep -E "(reconciliation|batch_prediction|cleanup|monitor|health_check)" || true

# Run initial health check
echo -e "${YELLOW}Running initial system health check...${NC}"
cd "$PROJECT_ROOT"
if python3 src/jobs/job_cli.py run health_check --verbose; then
    echo -e "${GREEN}✓ Initial health check passed${NC}"
else
    echo -e "${RED}✗ Initial health check failed${NC}"
    echo "System may have issues that need to be addressed."
fi

# Set up log rotation
echo -e "${YELLOW}Setting up log rotation...${NC}"
# Copy logrotate config to system directory (requires sudo)
if sudo cp "$PROJECT_ROOT/config/logrotate.conf" /etc/logrotate.d/abbanoa-jobs; then
    echo -e "${GREEN}✓ Log rotation configured${NC}"
else
    echo -e "${YELLOW}⚠ Could not set up system log rotation (requires sudo)${NC}"
    echo "You can set up log rotation manually later."
fi

echo
echo -e "${GREEN}Setup completed successfully!${NC}"
echo
echo "Available commands:"
echo "  python3 src/jobs/job_cli.py list           - List all available jobs"
echo "  python3 src/jobs/job_cli.py status         - Check job execution status"  
echo "  python3 src/jobs/job_cli.py run <job>      - Run a specific job manually"
echo "  python3 src/jobs/job_cli.py run-all        - Run all jobs in sequence"
echo
echo "Jobs are now scheduled to run automatically via cron:"
echo "  • Reconciliation: Every hour"
echo "  • Batch Prediction: Every 6 hours"  
echo "  • Daily Cleanup: Daily at 2:00 AM"
echo "  • Monitoring: Every 15 minutes"
echo "  • Health Check: Every 4 hours"
echo
echo "Logs are written to: $PROJECT_ROOT/logs/"
echo "View crontab: crontab -l"