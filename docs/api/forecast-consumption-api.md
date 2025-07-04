# Forecast Consumption API Documentation

## Overview

The Forecast Consumption use case provides asynchronous access to ML-generated forecasts with sub-300ms latency at the 99th percentile. This API follows clean architecture principles and provides a domain-driven interface for retrieving water infrastructure forecasts.

## Use Case: ForecastConsumption

### Purpose
Retrieve 7-day forecasts for water infrastructure metrics (flow rate, pressure, reservoir level) from BigQuery ML ARIMA_PLUS models.

### Interface

```python
class ForecastConsumption:
    async def get_forecast(
        self,
        district_id: str,
        metric: str,
        horizon: int
    ) -> pd.DataFrame
```

### Parameters

| Parameter | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| `district_id` | str | Yes | District identifier | Must match pattern `DIST_[0-9]{3}` (e.g., DIST_001) |
| `metric` | str | Yes | Metric type | Must be one of: `flow_rate`, `reservoir_level`, `pressure` |
| `horizon` | int | Yes | Forecast horizon in days | Must be between 1 and 7 |

### Response

Returns a pandas DataFrame with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | datetime64[ns, UTC] | Forecast timestamp (timezone-aware UTC) |
| `district_id` | str | District identifier |
| `metric` | str | Metric type |
| `forecast_value` | float64 | Predicted value |
| `lower_bound` | float64 | 95% prediction interval lower bound |
| `upper_bound` | float64 | 95% prediction interval upper bound |
| `confidence_level` | float64 | Confidence level (default 0.95) |

### Example Usage

```python
from src.application.use_cases.forecast_consumption import ForecastConsumption
from src.infrastructure.repositories.bigquery_forecast_repository import BigQueryForecastRepository
from src.infrastructure.clients.async_bigquery_client import AsyncBigQueryClient

# Initialize dependencies
client = AsyncBigQueryClient(
    project_id="abbanoa-464816",
    dataset_id="water_infrastructure",
    query_timeout_ms=250
)
await client.initialize()

repository = BigQueryForecastRepository(client)
forecast_use_case = ForecastConsumption(repository)

# Get 7-day forecast for DIST_001 flow rate
forecast_df = await forecast_use_case.get_forecast(
    district_id="DIST_001",
    metric="flow_rate",
    horizon=7
)

print(forecast_df.head())
# Output:
#                  timestamp district_id    metric  forecast_value  lower_bound  upper_bound  confidence_level
# 0 2025-07-05 00:00:00+00:00    DIST_001  flow_rate          112.58       103.32       121.84              0.95
# 1 2025-07-06 00:00:00+00:00    DIST_001  flow_rate          111.13       101.08       121.19              0.95
# ...
```

## Error Handling

### Exception Types

| Exception | HTTP Equivalent | Description | Example |
|-----------|----------------|-------------|---------|
| `InvalidForecastRequestException` | 400 Bad Request | Invalid input parameters | Invalid district_id format |
| `ForecastNotFoundException` | 404 Not Found | Model or forecast not available | Model doesn't exist |
| `ForecastServiceException` | 503 Service Unavailable | Service-level error | BigQuery connection failed |
| `ForecastTimeoutException` | 504 Gateway Timeout | Request exceeded timeout | Query took >300ms |

### Error Response Structure

```python
{
    "error": "InvalidForecastRequestException",
    "message": "Invalid district_id 'INVALID'. Must match pattern DIST_XXX where XXX is a 3-digit number.",
    "details": {
        "field": "district_id",
        "value": "INVALID",
        "error": "validation_error"
    }
}
```

## Performance Characteristics

### Latency SLA

| Percentile | Cold Start | Warm Start | Requirement |
|------------|------------|------------|-------------|
| P50 | ~80ms | ~25ms | - |
| P90 | ~150ms | ~40ms | - |
| P95 | ~200ms | ~60ms | - |
| P99 | ~280ms | ~100ms | ≤ 300ms |

### Optimization Features

1. **Connection Pooling**: Reuses BigQuery client connections (min: 2, max: 10)
2. **Query Caching**: In-memory cache for repeated queries
3. **Async Throughout**: Non-blocking I/O operations
4. **Retry Logic**: Exponential backoff for transient failures

## Integration Guide

### REST API Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ForecastRequest(BaseModel):
    district_id: str
    metric: str
    horizon: int

@app.get("/api/v1/forecasts")
async def get_forecast(request: ForecastRequest):
    try:
        df = await forecast_use_case.get_forecast(
            district_id=request.district_id,
            metric=request.metric,
            horizon=request.horizon
        )
        
        # Convert DataFrame to JSON response
        return {
            "district_id": request.district_id,
            "metric": request.metric,
            "horizon": request.horizon,
            "forecasts": df.to_dict(orient="records")
        }
        
    except InvalidForecastRequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ForecastNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForecastTimeoutException as e:
        raise HTTPException(status_code=504, detail=str(e))
    except ForecastServiceException as e:
        raise HTTPException(status_code=503, detail=str(e))
```

### Configuration

```python
# Environment variables
BIGQUERY_PROJECT_ID = "abbanoa-464816"
BIGQUERY_DATASET_ID = "water_infrastructure"
ML_MODELS_DATASET_ID = "ml_models"

# Performance tuning
QUERY_TIMEOUT_MS = 250  # Leave buffer for 300ms SLA
CONNECTION_POOL_SIZE = 10
CACHE_ENABLED = True
MAX_RETRY_ATTEMPTS = 3
```

### Dependency Injection

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    bigquery_client = providers.Singleton(
        AsyncBigQueryClient,
        project_id=config.bigquery.project_id,
        dataset_id=config.bigquery.dataset_id,
        query_timeout_ms=config.performance.query_timeout_ms
    )
    
    forecast_repository = providers.Factory(
        BigQueryForecastRepository,
        client=bigquery_client,
        ml_dataset_id=config.bigquery.ml_dataset_id
    )
    
    forecast_use_case = providers.Factory(
        ForecastConsumption,
        forecast_repository=forecast_repository
    )
```

## Monitoring and Observability

### Metrics

The use case automatically collects the following metrics:

| Metric | Type | Tags | Description |
|--------|------|------|-------------|
| `forecast_requests` | Counter | district, metric | Total number of forecast requests |
| `forecast_retrieval` | Histogram | - | Latency distribution in milliseconds |
| `forecast_errors` | Counter | error_type | Error count by type |
| `cache_hit_ratio` | Gauge | - | Percentage of cached responses |

### Logging

Structured logging with correlation IDs:

```json
{
    "timestamp": "2025-07-04T10:30:45.123Z",
    "level": "INFO",
    "message": "Processing forecast request",
    "request_id": "DIST_001_flow_rate_7_1720089045",
    "district_id": "DIST_001",
    "metric": "flow_rate",
    "horizon": 7,
    "latency_ms": 156.78
}
```

### Health Checks

```python
@app.get("/health/forecast")
async def health_check():
    try:
        # Test minimal forecast request
        df = await forecast_use_case.get_forecast(
            district_id="DIST_001",
            metric="flow_rate",
            horizon=1
        )
        
        return {
            "status": "healthy",
            "service": "forecast_consumption",
            "latency_ms": df.attrs.get("latency_ms", 0)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "forecast_consumption",
            "error": str(e)
        }
```

## Testing

### Unit Tests

```bash
pytest tests/unit/application/use_cases/test_forecast_consumption.py -v
```

### Integration Tests

```bash
pytest tests/integration/infrastructure/test_bigquery_forecast_repository.py -v
```

### Performance Tests

```bash
pytest tests/performance/test_forecast_latency.py -v -s
```

## Troubleshooting

### Common Issues

1. **High Latency**
   - Check BigQuery slot availability
   - Verify connection pool health
   - Review query complexity
   - Check network latency

2. **Model Not Found**
   - Verify model exists: `bq ls --model ml_models`
   - Check model naming convention
   - Ensure ML dataset permissions

3. **Timeout Errors**
   - Increase query timeout (max 250ms for SLA)
   - Check BigQuery job status
   - Review concurrent request load

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger("src.application.use_cases").setLevel(logging.DEBUG)
logging.getLogger("src.infrastructure").setLevel(logging.DEBUG)
```

## API Versioning

Current version: v1

Future versions will maintain backward compatibility or provide migration guides.

## Security Considerations

1. **Authentication**: Implement OAuth2/JWT for API access
2. **Authorization**: Role-based access to districts/metrics
3. **Rate Limiting**: Prevent abuse (suggested: 100 req/min)
4. **Input Validation**: Strict parameter validation
5. **Audit Logging**: Track all forecast requests

---

For additional support, contact the Data Engineering team.