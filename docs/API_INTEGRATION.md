# Dashboard API Integration

## Overview

The Abbanoa dashboard now supports two modes of operation:
1. **API Mode** (Recommended) - Uses pre-computed data from Processing Services
2. **Direct Mode** (Fallback) - Performs calculations in the dashboard

## Benefits of API Mode

### Performance Improvements
- **10-100x faster page loads** - No calculations on request
- **No loading spinners** - Data is pre-computed
- **Consistent response times** - Regardless of data volume
- **Lower memory usage** - Dashboard doesn't process large datasets

### Feature Enhancements
- **ML Predictions** - Access to flow predictions from trained models
- **Historical Aggregations** - Pre-computed metrics at multiple time windows
- **Advanced Anomaly Detection** - ML-based anomaly detection results
- **Network Efficiency Metrics** - Complex calculations done server-side

## How It Works

```
User Request → Dashboard → API → Pre-computed Data → Response
                   ↑                      ↑
                   └── Fallback ──────────┘
                       (if API unavailable)
```

## Setup

1. **Start Processing Services**
   ```bash
   ./scripts/start_processing_services.sh
   ```

2. **Start Dashboard**
   ```bash
   poetry run streamlit run src/presentation/streamlit/app.py
   ```

3. **Verify API Mode**
   - Look for "🚀 Using Processing Services API" in the footer
   - Check console for API health check

## API Endpoints Used

### Overview Tab
- `GET /api/v1/nodes` - List of nodes
- `GET /api/v1/network/metrics` - Network-wide metrics
- `GET /api/v1/dashboard/summary` - Optimized summary data

### Anomaly Tab
- `GET /api/v1/anomalies` - Recent anomalies with filtering
- `GET /api/v1/quality/{node_id}` - Data quality metrics

### Efficiency Tab
- `GET /api/v1/network/efficiency` - Efficiency calculations
- `GET /api/v1/network/metrics` - Performance metrics

### Additional Features
- `GET /api/v1/predictions/{node_id}` - ML predictions
- `GET /api/v1/status` - System health status

## Configuration

### Environment Variables
```bash
# API endpoint (optional - defaults to localhost)
API_BASE_URL=http://localhost:8000

# Cache settings (in Streamlit)
# Most API calls are cached for 30-300 seconds
```

### Dashboard Detection
The dashboard automatically detects if the API is available:
```python
api_client = get_api_client()
use_api = api_client.health_check()

if use_api:
    # Use API-based components
else:
    # Use direct calculation components
```

## Monitoring

### API Status
Check API health:
```bash
curl http://localhost:8000/health
```

### Performance Metrics
View in Performance Monitor tab:
- API response times
- Cache hit rates
- Data freshness

### Logs
```bash
# API logs
docker logs abbanoa-api

# Processing service logs
docker logs abbanoa-processing
```

## Troubleshooting

### Dashboard Shows "Cannot connect to API"
1. Check services are running:
   ```bash
   docker-compose -f docker-compose.processing.yml ps
   ```

2. Test API directly:
   ```bash
   python test_api_integration.py
   ```

### Slow Performance
1. Check Redis cache:
   ```bash
   docker exec abbanoa-redis-processing redis-cli info stats
   ```

2. Verify processing is running:
   ```bash
   ./scripts/monitor_processing.sh
   ```

### Missing Data
1. Check last processing time:
   ```sql
   SELECT * FROM processing_jobs ORDER BY created_at DESC LIMIT 5;
   ```

2. Trigger manual processing:
   ```bash
   docker exec abbanoa-processing python -c "
   from src.processing.service.main import ProcessingService
   import asyncio
   service = ProcessingService()
   asyncio.run(service._process_cycle())
   "
   ```

## Development

### Adding New API Endpoints

1. Add endpoint to `src/api/main.py`:
   ```python
   @app.get("/api/v1/new-endpoint")
   async def new_endpoint():
       # Implementation
   ```

2. Update API client:
   ```python
   def get_new_data(self):
       return self._make_request("GET", "/api/v1/new-endpoint")
   ```

3. Use in dashboard component:
   ```python
   data = self.api_client.get_new_data()
   ```

### Testing API Integration
```python
# Unit tests
pytest tests/api/

# Integration tests
pytest tests/integration/test_dashboard_api.py
```

## Performance Comparison

### Before (Direct Calculation)
- Overview tab load: 5-10 seconds
- Anomaly detection: 8-15 seconds
- Efficiency calculation: 10-20 seconds
- Memory usage: 500MB-2GB

### After (API Mode)
- Overview tab load: <0.5 seconds
- Anomaly detection: <0.3 seconds
- Efficiency calculation: <0.2 seconds
- Memory usage: 50-100MB

## Best Practices

1. **Always start processing services first**
   - Dashboard will fallback gracefully if API is unavailable
   - But performance will be significantly degraded

2. **Monitor data freshness**
   - Processing runs every 30 minutes
   - Check system status in dashboard footer

3. **Use appropriate cache times**
   - Critical data: 10-30 seconds
   - Summary data: 1-5 minutes
   - Historical data: 5-30 minutes

4. **Handle API errors gracefully**
   - Dashboard components show appropriate messages
   - Fallback to direct mode if needed