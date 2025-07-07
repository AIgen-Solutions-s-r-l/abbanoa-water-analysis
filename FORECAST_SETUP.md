# Forecast Feature Setup Guide

## Quick Start

To use the forecast functionality, you need to run both the API server and the Streamlit dashboard:

### 1. Start the API Server (Required for Forecast)

In a terminal, run:
```bash
./run_api.sh
```

This will start the API server on http://localhost:8000

You should see output like:
```
Starting Abbanoa Water Infrastructure API...
Starting API server on http://localhost:8000
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Start the Streamlit Dashboard

In another terminal, run:
```bash
./run_dashboard.sh
```

This will start the dashboard on http://localhost:8502

### 3. Use the Forecast Feature

1. Navigate to the **Forecast** tab in the dashboard
2. Click the **"Load Forecast Data"** button
3. The forecast chart will appear with:
   - 7-day predictions
   - Historical context (last 30 days)
   - 80% confidence intervals

## Troubleshooting

### "No forecast data available"
- **Cause**: The API server is not running
- **Solution**: Start the API server with `./run_api.sh`

### "API error" or connection errors
- **Cause**: Network issues or BigQuery permissions
- **Solution**: 
  - Check that you have Google Cloud credentials set up
  - Verify the API is running on port 8000
  - Check API logs for specific errors

### Empty forecasts
- **Cause**: No ML models trained or data issues
- **Solution**: 
  - Verify ARIMA models exist in BigQuery ML
  - Check that historical data is available
  - The system will fall back to simple moving average if ML fails

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Streamlit     │────▶│   FastAPI       │────▶│   BigQuery   │
│   Dashboard     │     │   Server        │     │   ML Models  │
│  (Port 8502)    │     │  (Port 8000)    │     │              │
└─────────────────┘     └─────────────────┘     └──────────────┘
        │                        │                       │
        │                        │                       │
        ▼                        ▼                       ▼
   DataFetcher            Forecast Service         ARIMA Models
                        Calculation Service
```

## API Endpoints

- `GET /api/v1/forecasts/{district_id}/{metric}` - Get forecast data
- `GET /api/v1/forecasts/models/status` - Check model status

### Example API Call
```bash
curl http://localhost:8000/api/v1/forecasts/DIST_001/flow_rate?horizon=7
```

## Development Tips

1. **Logs**: Check API logs in the terminal running `run_api.sh`
2. **Testing**: Use `scripts/validate_forecast.py` to test the system
3. **Debugging**: Set `LOG_LEVEL=DEBUG` for detailed logs

## Required Environment

- Python 3.12+
- Poetry installed
- Google Cloud credentials configured
- BigQuery access to project `abbanoa-464816`