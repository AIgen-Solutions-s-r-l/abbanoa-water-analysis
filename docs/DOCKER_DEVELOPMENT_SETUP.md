# Docker Development Setup Guide
## Complete Local Development Environment

This guide explains how to run the entire Abbanoa Water Analysis system locally using Docker, with no external dependencies required.

---

## Prerequisites

### Required Software
- **Docker Desktop** 4.0+ (includes Docker Engine and Docker Compose)
  - [Download for Windows/Mac](https://www.docker.com/products/docker-desktop)
  - [Install on Linux](https://docs.docker.com/engine/install/)
- **Git** (for cloning the repository)
- **8GB RAM minimum** (16GB recommended)
- **10GB free disk space**

### Optional
- **Google Cloud SDK** (only if connecting to BigQuery)
- **GCP Service Account Key** (only if using BigQuery features)

---

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd abbanoa-water-analysis
```

### 2. Create Environment File
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred settings (optional)
# Default values will work for local development
```

### 3. Start All Services
```bash
# Start everything with one command
docker-compose -f docker-compose.full-dev.yml up -d

# This will start:
# - PostgreSQL with TimescaleDB (port 5432)
# - Redis Cache (port 6379)
# - FastAPI Backend (port 8000)
# - Next.js Frontend (port 3000)
# - Mock Auth Backend (port 3002)
```

### 4. Initialize Sample Data (First Time Only)
```bash
# Load sample data and initialize cache
docker-compose -f docker-compose.full-dev.yml --profile init up data-init
```

### 5. Access the Applications
- **Next.js Dashboard:** http://localhost:3000
- **FastAPI Docs:** http://localhost:8000/docs
- **Mock Auth API:** http://localhost:3002

---

## Detailed Setup Options

### Basic Services Only
```bash
# Start only core services (DB, Cache, API, Frontend)
docker-compose -f docker-compose.full-dev.yml up -d postgres redis api frontend
```

### With ETL Services (BigQuery Integration)
```bash
# First, add your GCP credentials
mkdir -p credentials
cp /path/to/your/gcp-key.json credentials/gcp-key.json

# Start with ETL services
docker-compose -f docker-compose.full-dev.yml --profile with-etl up -d
```

### With Nginx Proxy (Production-like)
```bash
# Start with Nginx reverse proxy
docker-compose -f docker-compose.full-dev.yml --profile with-nginx up -d

# Access via Nginx: http://localhost
```

### Development Tools Container
```bash
# Start an interactive container with all development tools
docker-compose -f docker-compose.full-dev.yml --profile tools run --rm dev-tools

# Inside the container, you can:
# - Run Python scripts
# - Access databases directly
# - Run tests
# - Use debugging tools
```

---

## Service Details

### PostgreSQL + TimescaleDB
- **Port:** 5432
- **Database:** abbanoa_processing
- **Username:** abbanoa_user
- **Password:** abbanoa_dev_pass
- **Connection String:** `postgresql://abbanoa_user:abbanoa_dev_pass@localhost:5432/abbanoa_processing`

### Redis Cache
- **Port:** 6379
- **No authentication in dev mode**
- **Max Memory:** 1GB (configurable)

### FastAPI Backend
- **Port:** 8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Hot Reload:** Enabled (changes to `/src` are auto-reloaded)

### Next.js Frontend
- **Port:** 3000
- **Hot Reload:** Enabled
- **API Proxy:** Configured to forward `/api` to backend

---

## Common Development Tasks

### View Logs
```bash
# All services
docker-compose -f docker-compose.full-dev.yml logs -f

# Specific service
docker-compose -f docker-compose.full-dev.yml logs -f api
docker-compose -f docker-compose.full-dev.yml logs -f frontend
```

### Restart a Service
```bash
# Restart API after code changes
docker-compose -f docker-compose.full-dev.yml restart api

# Rebuild and restart (after dependency changes)
docker-compose -f docker-compose.full-dev.yml up -d --build api
```

### Access Database
```bash
# PostgreSQL CLI
docker-compose -f docker-compose.full-dev.yml exec postgres psql -U abbanoa_user -d abbanoa_processing

# Redis CLI
docker-compose -f docker-compose.full-dev.yml exec redis redis-cli
```

### Run Tests
```bash
# Run backend tests
docker-compose -f docker-compose.full-dev.yml exec api pytest tests/

# Run frontend tests
docker-compose -f docker-compose.full-dev.yml exec frontend npm test
```

### Load Sample Data
```bash
# Generate 30 days of sample data
docker-compose -f docker-compose.full-dev.yml exec api python scripts/generate_consumption_dataset.py --days 30

# Force refresh Redis cache
docker-compose -f docker-compose.full-dev.yml exec api python init_redis_cache.py --force
```

---

## Troubleshooting

### Port Conflicts
If you get "port already in use" errors:

```bash
# Check what's using the ports
lsof -i :3000  # Frontend
lsof -i :8000  # API
lsof -i :5432  # PostgreSQL

# Use alternative ports by editing .env:
API_PORT=8001
FRONTEND_PORT=3001
POSTGRES_PORT=5433
```

### Database Connection Issues
```bash
# Check if PostgreSQL is ready
docker-compose -f docker-compose.full-dev.yml exec postgres pg_isready

# Reset database
docker-compose -f docker-compose.full-dev.yml down -v
docker-compose -f docker-compose.full-dev.yml up -d postgres
# Wait for health check, then restart other services
```

### Memory Issues
If containers are crashing due to memory:

```bash
# Check Docker Desktop memory allocation
# Increase to at least 4GB in Docker Desktop settings

# Or reduce service memory usage in docker-compose.full-dev.yml
# Adjust Redis maxmemory, PostgreSQL shared_buffers, etc.
```

### Build Failures
```bash
# Clean rebuild
docker-compose -f docker-compose.full-dev.yml down
docker-compose -f docker-compose.full-dev.yml build --no-cache
docker-compose -f docker-compose.full-dev.yml up -d
```

---

## Data Persistence

### Volumes
Data is persisted in Docker volumes:
- `postgres-dev-data`: PostgreSQL database files
- `redis-dev-data`: Redis persistence files

### Backup Data
```bash
# Backup PostgreSQL
docker-compose -f docker-compose.full-dev.yml exec postgres pg_dump -U abbanoa_user abbanoa_processing > backup.sql

# Backup Redis
docker-compose -f docker-compose.full-dev.yml exec redis redis-cli SAVE
docker cp abbanoa-redis-dev:/data/dump.rdb ./redis-backup.rdb
```

### Restore Data
```bash
# Restore PostgreSQL
docker-compose -f docker-compose.full-dev.yml exec -T postgres psql -U abbanoa_user abbanoa_processing < backup.sql

# Restore Redis
docker cp ./redis-backup.rdb abbanoa-redis-dev:/data/dump.rdb
docker-compose -f docker-compose.full-dev.yml restart redis
```

### Clean Everything
```bash
# Stop and remove all containers, networks, volumes
docker-compose -f docker-compose.full-dev.yml down -v

# Remove all images too
docker-compose -f docker-compose.full-dev.yml down -v --rmi all
```

---

## Development Workflow

### 1. Backend Development (Python/FastAPI)
```bash
# Code changes in /src are auto-reloaded
# Edit files locally, changes reflect immediately

# View API logs
docker-compose -f docker-compose.full-dev.yml logs -f api

# Run specific Python scripts
docker-compose -f docker-compose.full-dev.yml exec api python scripts/your_script.py
```

### 2. Frontend Development (Next.js)
```bash
# Code changes in /frontend/src are hot-reloaded
# Edit files locally, browser auto-refreshes

# View frontend logs
docker-compose -f docker-compose.full-dev.yml logs -f frontend

# Install new npm packages
docker-compose -f docker-compose.full-dev.yml exec frontend npm install <package-name>
```

### 3. Database Development
```bash
# Connect to PostgreSQL
docker-compose -f docker-compose.full-dev.yml exec postgres psql -U abbanoa_user -d abbanoa_processing

# Run SQL migrations
docker-compose -f docker-compose.full-dev.yml exec api python -m src.infrastructure.database.postgres_manager

# View TimescaleDB hypertables
docker-compose -f docker-compose.full-dev.yml exec postgres psql -U abbanoa_user -d abbanoa_processing -c "\dx"
```

---

## Performance Optimization

### For Faster Startup
```bash
# Pull all images first
docker-compose -f docker-compose.full-dev.yml pull

# Build images in parallel
docker-compose -f docker-compose.full-dev.yml build --parallel
```

### For Better Performance
1. **Increase Docker Desktop Resources:**
   - CPUs: 4+ cores
   - Memory: 8GB+
   - Swap: 2GB+
   - Disk image size: 64GB+

2. **Use Docker BuildKit:**
```bash
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
```

3. **Enable Docker Compose V2:**
   - Check "Use Docker Compose V2" in Docker Desktop settings

---

## Integration with IDEs

### VS Code
1. Install "Remote - Containers" extension
2. Open project folder
3. Click "Reopen in Container" when prompted
4. Select the service to develop in (api, frontend, etc.)

### PyCharm
1. Configure Docker as remote Python interpreter
2. Set up path mappings: `/app` → project root
3. Configure database connection to `localhost:5432`

### WebStorm
1. Configure Node.js remote interpreter via Docker
2. Set up port forwarding for debugging
3. Enable ESLint/Prettier integration

---

## Production Considerations

This setup is for **development only**. For production:

1. **Use docker-compose.prod.yml** instead
2. **Set secure passwords** in environment variables
3. **Enable SSL/TLS** for all services
4. **Configure proper logging** and monitoring
5. **Set resource limits** for containers
6. **Use managed databases** (Cloud SQL, RDS, etc.)
7. **Implement proper backup** strategies
8. **Configure health checks** and auto-restart policies

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Project Architecture Guide](./architecture/ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/docs)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)

---

## Support

For issues or questions:
1. Check the logs: `docker-compose -f docker-compose.full-dev.yml logs`
2. Review this guide's troubleshooting section
3. Check project documentation in `/docs`
4. Open an issue on GitHub

---

**Last Updated:** 2025-08-06  
**Version:** 1.0.0