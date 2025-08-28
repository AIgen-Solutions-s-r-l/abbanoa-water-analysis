#!/bin/bash

# Kill any existing processes
echo "Stopping any existing processes..."
pkill -f "uvicorn presentation.api.app_postgres:app" || true
pkill -f "next dev" || true

# Start all services with PM2
echo "Starting Roccavina services with PM2..."
pm2 start ecosystem.config.js

# Show status
pm2 status

echo ""
echo "All services started! Use these commands to manage them:"
echo "  pm2 status        - Check status of all services"
echo "  pm2 logs          - View all logs"
echo "  pm2 logs roccavina-backend  - View backend logs only"
echo "  pm2 logs roccavina-frontend - View frontend logs only"
echo "  pm2 restart all   - Restart all services"
echo "  pm2 stop all      - Stop all services"
echo "  pm2 delete all    - Remove all from PM2"
echo ""
echo "Services running at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000" 