#!/bin/bash

# Kill any existing uvicorn processes
echo "Stopping any existing uvicorn processes..."
pkill -f "uvicorn presentation.api.app_postgres:app" || true

# Start backend with PM2
echo "Starting Abbanoa backend with PM2..."
pm2 start pm2-backend.config.js

# Show status
pm2 status abbanoa-backend

echo ""
echo "Backend started! Use these commands to manage it:"
echo "  pm2 status        - Check status"
echo "  pm2 logs abbanoa-backend  - View logs"
echo "  pm2 restart abbanoa-backend  - Restart"
echo "  pm2 stop abbanoa-backend  - Stop"
echo "  pm2 delete abbanoa-backend  - Remove from PM2" 