# PM2 Configuration for Roccavina Water Analysis

This project includes PM2 configuration files to keep the backend and frontend services running reliably.

## Prerequisites

Install PM2 globally if you haven't already:
```bash
npm install -g pm2
```

## Available Configurations

### 1. Backend Only (`pm2-backend.config.js`)
Runs only the FastAPI backend with uvicorn in reload mode.

### 2. Full Stack (`ecosystem.config.js`)
Runs both backend and frontend services.

## Quick Start

### Start Backend Only
```bash
./start-backend.sh
```

### Start Both Frontend and Backend
```bash
./start-all.sh
```

## Manual PM2 Commands

### Start services
```bash
# Backend only
pm2 start pm2-backend.config.js

# Both frontend and backend
pm2 start ecosystem.config.js
```

### View logs
```bash
# All logs
pm2 logs

# Backend logs only
pm2 logs roccavina-backend

# Frontend logs only
pm2 logs roccavina-frontend

# Follow logs in real-time
pm2 logs --lines 100
```

### Service management
```bash
# Check status
pm2 status

# Restart services
pm2 restart all
pm2 restart roccavina-backend
pm2 restart roccavina-frontend

# Stop services
pm2 stop all
pm2 stop roccavina-backend

# Remove from PM2
pm2 delete all
pm2 delete roccavina-backend
```

### Save PM2 configuration
```bash
# Save current process list
pm2 save

# Setup startup script
pm2 startup
```

## Environment Variables

The PM2 configs include environment settings:
- `PYTHONUNBUFFERED=1` - Ensures Python output is not buffered
- `NODE_ENV=development` - Sets Node environment (change to 'production' for production)

## Logs Location

All logs are stored in the `./logs` directory:
- Backend logs: `logs/pm2-backend-*.log`
- Frontend logs: `logs/pm2-frontend-*.log`

## Production Deployment

For production, you can:
1. Set `NODE_ENV=production` in the config
2. Remove the `--reload` flag from uvicorn args
3. Consider using multiple instances with `instances: 'max'`
4. Set up PM2 to start on system boot with `pm2 startup`

## Troubleshooting

### Backend not starting
- Check if poetry is installed and accessible
- Ensure PostgreSQL is running
- Check logs: `pm2 logs roccavina-backend --lines 100`

### Port already in use
- The start scripts automatically kill existing processes
- Or manually: `pm2 stop all` then `pm2 delete all`

### Memory issues
- The configs set `max_memory_restart: '1G'`
- Adjust this value in the config files if needed 