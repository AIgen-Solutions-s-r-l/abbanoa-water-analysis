# Dashboard API Mode

The Abbanoa Water Infrastructure Dashboard has been updated to use the REST API instead of direct BigQuery connections. This provides better security, performance, and scalability.

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌───────────────┐
│   Streamlit     │────▶│   REST API   │────▶│  PostgreSQL   │
│   Dashboard     │     │  (FastAPI)   │     │ TimescaleDB   │
└─────────────────┘     └──────────────┘     └───────────────┘
                                │                     ▲
                                ▼                     │
                        ┌──────────────┐     ┌───────────────┐
                        │    Redis     │     │  Processing   │
                        │    Cache     │     │   Service     │
                        └──────────────┘     └───────────────┘
                                                      │
                                                      ▼
                                              ┌───────────────┐
                                              │   BigQuery    │
                                              └───────────────┘
```

## Benefits

1. **No BigQuery Authentication Required**: The dashboard no longer needs Google Cloud credentials
2. **Better Performance**: Data is cached in Redis and served from PostgreSQL
3. **Real-time Updates**: The processing service continuously updates the data
4. **Scalability**: API can handle multiple dashboard instances

## Running the Dashboard

### Prerequisites

1. Ensure the processing services are running:
```bash
docker compose -f docker-compose.processing.yml up -d
```

2. Verify the API is healthy:
```bash
curl http://localhost:8000/health
```

### Start the Dashboard

```bash
./run_dashboard.sh
```

Or manually:
```bash
export API_BASE_URL=http://localhost:8000
poetry run streamlit run src/presentation/streamlit/app_api.py
```

## Configuration

### Environment Variables

- `API_BASE_URL`: API endpoint (default: `http://localhost:8000`)
- `STREAMLIT_PORT`: Dashboard port (default: `8502`)

### API Endpoints Used

- `GET /health` - System health check
- `GET /api/v1/nodes` - List all nodes
- `GET /api/v1/nodes/{node_id}/metrics` - Node metrics
- `GET /api/v1/nodes/{node_id}/history` - Historical data
- `GET /api/v1/network/metrics` - Network-wide metrics
- `GET /api/v1/network/efficiency` - Efficiency calculations
- `GET /api/v1/predictions/{node_id}` - ML predictions
- `GET /api/v1/anomalies` - Detected anomalies
- `GET /api/v1/dashboard/summary` - Dashboard summary
- `GET /api/v1/status` - System status

## Features

### Network Overview
- Real-time network status
- Active nodes monitoring
- Total flow and pressure metrics
- Anomaly counts

### Node Details
- Individual node metrics
- Historical trends
- Real-time updates
- Performance indicators

### Anomaly Detection
- Real-time anomaly alerts
- Historical anomaly patterns
- Severity classification
- Trend analysis

### Forecasting
- ML-based predictions
- Consumption patterns
- Trend visualization
- Confidence intervals

### System Status
- Service health monitoring
- Processing job status
- Data freshness indicators
- Performance metrics

## Troubleshooting

### Dashboard shows "No data available"
1. Check if the API is running: `curl http://localhost:8000/health`
2. Check if data is being processed: `docker logs abbanoa-processing`
3. Verify PostgreSQL has data: `docker exec abbanoa-postgres-processing psql -U abbanoa_user -d abbanoa_processing -c "SELECT COUNT(*) FROM water_infrastructure.sensor_readings;"`

### API Connection Error
1. Verify the API URL in environment: `echo $API_BASE_URL`
2. Check if the API container is running: `docker ps | grep abbanoa-api`
3. Check API logs: `docker logs abbanoa-api`

### Performance Issues
1. Check Redis cache: `docker exec abbanoa-redis-processing redis-cli ping`
2. Monitor API response times in the System Status tab
3. Check PostgreSQL performance: `docker exec abbanoa-postgres-processing pg_isready`

## Development

To modify the dashboard:

1. Edit `src/presentation/streamlit/app_api.py`
2. Components are in `src/presentation/streamlit/components/`
3. API client is in `src/presentation/streamlit/utils/api_client.py`
4. Data fetcher is in `src/presentation/streamlit/utils/data_fetcher.py`

No BigQuery credentials or authentication setup required!