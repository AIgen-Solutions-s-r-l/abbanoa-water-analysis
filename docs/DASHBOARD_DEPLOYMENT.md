# Dashboard Deployment Guide

This guide explains how to deploy and manage the Abbanoa Water Infrastructure Dashboard in production.

## Current Setup

The dashboard is deployed at: https://curator.aigensolutions.it

- **Port**: 8502 (proxied through Nginx)
- **Mode**: API-based (no BigQuery authentication required)
- **User**: alessio

## Starting the Dashboard

### Quick Start

```bash
cd /home/alessio/Customers/Abbanoa
./scripts/start_dashboard.sh
```

This script will:
1. Stop any existing dashboard instance
2. Wait for the API to be available
3. Start the new API-based dashboard
4. Log output to `logs/dashboard.log`

### Manual Start

```bash
cd /home/alessio/Customers/Abbanoa
export API_BASE_URL=http://localhost:8000
poetry run streamlit run src/presentation/streamlit/app_api.py --server.port 8502 --server.address 127.0.0.1
```

## Stopping the Dashboard

```bash
pkill -f "streamlit.*app_api.py.*8502"
```

## Checking Status

### Check if running:
```bash
ps aux | grep streamlit | grep 8502
```

### Check logs:
```bash
tail -f /home/alessio/Customers/Abbanoa/logs/dashboard.log
```

### Check API health:
```bash
curl http://localhost:8000/health
```

## Systemd Service (Optional)

To set up as a system service:

```bash
# Copy service file
sudo cp scripts/abbanoa-dashboard.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable abbanoa-dashboard
sudo systemctl start abbanoa-dashboard

# Check status
sudo systemctl status abbanoa-dashboard
```

## Nginx Configuration

The dashboard is reverse-proxied through Nginx:

- Config file: `/etc/nginx/sites-available/curator.aigensolutions.it`
- SSL certificates: Managed by Let's Encrypt/Certbot
- Proxy pass: `http://127.0.0.1:8502`

## Troubleshooting

### Dashboard shows authentication error

If you see `google.auth.exceptions.DefaultCredentialsError`:
- The old `app.py` is running instead of `app_api.py`
- Solution: Stop all streamlit processes and restart with `start_dashboard.sh`

### Dashboard shows no data

1. Check API is running:
   ```bash
   docker compose -f docker-compose.processing.yml ps
   ```

2. Check API logs:
   ```bash
   docker logs abbanoa-api
   ```

3. Verify processing service:
   ```bash
   docker logs abbanoa-processing
   ```

### Port 8502 already in use

```bash
# Find and kill the process
lsof -i :8502
kill <PID>
```

### SSL Certificate Issues

```bash
# Renew certificates
sudo certbot renew
sudo nginx -s reload
```

## Updates and Maintenance

### Updating the Dashboard

1. Pull latest changes:
   ```bash
   cd /home/alessio/Customers/Abbanoa
   git pull
   ```

2. Update dependencies:
   ```bash
   poetry install
   ```

3. Restart dashboard:
   ```bash
   ./scripts/start_dashboard.sh
   ```

### Updating Processing Services

```bash
# Rebuild and restart all services
docker compose -f docker-compose.processing.yml down
docker compose -f docker-compose.processing.yml build
docker compose -f docker-compose.processing.yml up -d
```

## Monitoring

### Check Dashboard Access Logs
```bash
sudo tail -f /var/log/nginx/access.log | grep curator
```

### Check Error Logs
```bash
sudo tail -f /var/log/nginx/error.log
```

### Monitor Resource Usage
```bash
# Dashboard memory/CPU
ps aux | grep streamlit

# Docker containers
docker stats
```

## Backup

Important files to backup:
- `/home/alessio/Customers/Abbanoa/.env`
- `/home/alessio/Customers/Abbanoa/.env.processing`
- `/home/alessio/Customers/Abbanoa/bigquery-service-account-key.json`
- PostgreSQL data: `docker volume backup abbanoa-postgres-processing-data`

## Security Notes

1. The dashboard runs on localhost only (127.0.0.1)
2. SSL/TLS is handled by Nginx
3. No BigQuery credentials needed on the server
4. API authentication can be added if needed