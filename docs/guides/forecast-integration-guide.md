# Forecast Integration Guide

## Quick Start

This guide shows how to integrate the Forecast Consumption use case into your application.

### 1. Basic Setup

```python
import asyncio
from src.application.use_cases.forecast_consumption import ForecastConsumption
from src.infrastructure.repositories.bigquery_forecast_repository import BigQueryForecastRepository
from src.infrastructure.clients.async_bigquery_client import AsyncBigQueryClient

async def setup_forecast_service():
    # Initialize BigQuery client
    client = AsyncBigQueryClient(
        project_id="abbanoa-464816",
        dataset_id="water_infrastructure",
        ml_dataset_id="ml_models",
        query_timeout_ms=250
    )
    await client.initialize()
    
    # Create repository
    repository = BigQueryForecastRepository(client)
    
    # Create use case
    forecast_service = ForecastConsumption(repository)
    
    return forecast_service, client

# Usage
async def main():
    forecast_service, client = await setup_forecast_service()
    
    try:
        # Get forecast
        df = await forecast_service.get_forecast(
            district_id="DIST_001",
            metric="flow_rate",
            horizon=7
        )
        print(df)
    finally:
        await client.close()

# Run
asyncio.run(main())
```

### 2. FastAPI Integration

```python
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
import pandas as pd

# Global instances
forecast_service = None
bigquery_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global forecast_service, bigquery_client
    forecast_service, bigquery_client = await setup_forecast_service()
    yield
    # Shutdown
    await bigquery_client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/api/v1/forecasts/{district_id}/{metric}")
async def get_forecast(
    district_id: str,
    metric: str,
    horizon: int = 7
):
    """Get forecast for a specific district and metric."""
    try:
        df = await forecast_service.get_forecast(
            district_id=district_id,
            metric=metric,
            horizon=horizon
        )
        
        # Convert to API response
        return {
            "district_id": district_id,
            "metric": metric,
            "horizon": horizon,
            "forecast_count": len(df),
            "forecasts": df.to_dict(orient="records"),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except InvalidForecastRequestException as e:
        raise HTTPException(status_code=400, detail={
            "error": "Invalid request",
            "message": str(e),
            "field": e.field,
            "value": e.value
        })
    except ForecastNotFoundException as e:
        raise HTTPException(status_code=404, detail={
            "error": "Forecast not found",
            "message": str(e)
        })
    except ForecastTimeoutException as e:
        raise HTTPException(status_code=504, detail={
            "error": "Request timeout",
            "message": str(e),
            "timeout_ms": e.timeout_ms
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        })
```

### 3. Streamlit Dashboard Integration

```python
import streamlit as st
import asyncio
import pandas as pd
import plotly.graph_objects as go

# Cache the service setup
@st.cache_resource
def get_forecast_service():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    service, client = loop.run_until_complete(setup_forecast_service())
    return service, client, loop

# Streamlit app
st.title("Water Infrastructure Forecast Dashboard")

# Get service
forecast_service, client, loop = get_forecast_service()

# User inputs
col1, col2, col3 = st.columns(3)

with col1:
    district = st.selectbox(
        "District",
        ["DIST_001", "DIST_002"],
        help="Select the district for forecast"
    )

with col2:
    metric = st.selectbox(
        "Metric",
        ["flow_rate", "pressure", "reservoir_level"],
        help="Select the metric to forecast"
    )

with col3:
    horizon = st.slider(
        "Forecast Horizon (days)",
        min_value=1,
        max_value=7,
        value=7,
        help="Number of days to forecast"
    )

# Get forecast button
if st.button("Generate Forecast"):
    with st.spinner("Generating forecast..."):
        try:
            # Run async function
            df = loop.run_until_complete(
                forecast_service.get_forecast(district, metric, horizon)
            )
            
            # Display results
            st.success(f"Forecast generated for {district} - {metric}")
            
            # Plot forecast
            fig = go.Figure()
            
            # Add forecast line
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['forecast_value'],
                mode='lines+markers',
                name='Forecast',
                line=dict(color='blue', width=2)
            ))
            
            # Add confidence interval
            fig.add_trace(go.Scatter(
                x=df['timestamp'].tolist() + df['timestamp'].tolist()[::-1],
                y=df['upper_bound'].tolist() + df['lower_bound'].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(0,100,255,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False,
                name='95% Confidence Interval'
            ))
            
            # Update layout
            fig.update_layout(
                title=f"{metric.replace('_', ' ').title()} Forecast - {district}",
                xaxis_title="Date",
                yaxis_title=get_unit_for_metric(metric),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show data table
            with st.expander("View Forecast Data"):
                st.dataframe(df)
                
        except Exception as e:
            st.error(f"Error generating forecast: {str(e)}")

def get_unit_for_metric(metric):
    units = {
        "flow_rate": "L/s",
        "pressure": "bar",
        "reservoir_level": "m"
    }
    return units.get(metric, "units")
```

### 4. CLI Integration

```python
import click
import asyncio
import pandas as pd
from tabulate import tabulate

@click.command()
@click.option('--district', '-d', required=True, help='District ID (e.g., DIST_001)')
@click.option('--metric', '-m', required=True, 
              type=click.Choice(['flow_rate', 'pressure', 'reservoir_level']))
@click.option('--horizon', '-h', default=7, type=int, help='Forecast horizon (1-7 days)')
@click.option('--format', '-f', default='table',
              type=click.Choice(['table', 'csv', 'json']))
def forecast_cli(district, metric, horizon, format):
    """Get water infrastructure forecasts from the command line."""
    
    async def get_forecast_async():
        service, client = await setup_forecast_service()
        try:
            return await service.get_forecast(district, metric, horizon)
        finally:
            await client.close()
    
    # Run async function
    df = asyncio.run(get_forecast_async())
    
    # Format output
    if format == 'table':
        print(f"\nForecast for {district} - {metric} ({horizon} days)")
        print("=" * 60)
        print(tabulate(df, headers='keys', tablefmt='grid', floatfmt='.2f'))
    elif format == 'csv':
        print(df.to_csv(index=False))
    elif format == 'json':
        print(df.to_json(orient='records', date_format='iso'))

if __name__ == '__main__':
    forecast_cli()
```

### 5. Batch Processing

```python
import asyncio
from typing import List, Tuple
import pandas as pd

async def get_multiple_forecasts(
    forecast_service: ForecastConsumption,
    requests: List[Tuple[str, str, int]]
) -> List[pd.DataFrame]:
    """Get multiple forecasts concurrently."""
    
    tasks = [
        forecast_service.get_forecast(district, metric, horizon)
        for district, metric, horizon in requests
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle results
    successful_forecasts = []
    errors = []
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append((requests[i], result))
        else:
            successful_forecasts.append(result)
    
    if errors:
        print(f"Failed forecasts: {len(errors)}")
        for request, error in errors:
            print(f"  {request}: {error}")
    
    return successful_forecasts

# Example usage
async def batch_example():
    service, client = await setup_forecast_service()
    
    # Define batch requests
    requests = [
        ("DIST_001", "flow_rate", 7),
        ("DIST_001", "pressure", 7),
        ("DIST_001", "reservoir_level", 7),
        ("DIST_002", "flow_rate", 7),
        ("DIST_002", "pressure", 7),
        ("DIST_002", "reservoir_level", 7),
    ]
    
    try:
        forecasts = await get_multiple_forecasts(service, requests)
        
        # Combine all forecasts
        combined_df = pd.concat(forecasts, ignore_index=True)
        print(f"Generated {len(combined_df)} forecast points")
        
    finally:
        await client.close()

# Run
asyncio.run(batch_example())
```

### 6. Error Handling Best Practices

```python
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ForecastServiceWrapper:
    """Wrapper with comprehensive error handling and fallback strategies."""
    
    def __init__(self, forecast_service: ForecastConsumption):
        self.service = forecast_service
        self.cache = {}  # Simple in-memory cache
        
    async def get_forecast_with_fallback(
        self,
        district_id: str,
        metric: str,
        horizon: int
    ) -> Optional[pd.DataFrame]:
        """Get forecast with fallback to cache on error."""
        
        cache_key = f"{district_id}:{metric}:{horizon}"
        
        try:
            # Try to get fresh forecast
            df = await self.service.get_forecast(district_id, metric, horizon)
            
            # Update cache
            self.cache[cache_key] = df.copy()
            
            return df
            
        except ForecastTimeoutException:
            logger.warning(f"Timeout for {cache_key}, checking cache")
            
            # Return cached result if available
            if cache_key in self.cache:
                cached_df = self.cache[cache_key].copy()
                logger.info(f"Returning cached forecast for {cache_key}")
                return cached_df
            else:
                raise
                
        except ForecastNotFoundException as e:
            logger.error(f"Forecast not found: {e}")
            
            # Could return a simple statistical forecast as fallback
            # For example, last known value repeated
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
```

### 7. Performance Optimization Tips

```python
# 1. Connection Pool Tuning
client = AsyncBigQueryClient(
    project_id="abbanoa-464816",
    dataset_id="water_infrastructure",
    max_pool_size=20,  # Increase for high concurrency
    min_pool_size=5,   # Maintain minimum connections
    query_timeout_ms=200,  # Tight timeout for SLA
    enable_cache=True  # Enable query caching
)

# 2. Request Batching
async def optimized_batch_forecasts(service, districts, metrics):
    """Batch requests by metric for better cache hits."""
    
    results = {}
    
    # Group by metric for better cache performance
    for metric in metrics:
        metric_tasks = [
            service.get_forecast(district, metric, 7)
            for district in districts
        ]
        
        metric_results = await asyncio.gather(*metric_tasks)
        
        for district, df in zip(districts, metric_results):
            results[(district, metric)] = df
    
    return results

# 3. Preemptive Caching
async def warm_cache(service, common_requests):
    """Warm up cache with common requests."""
    
    tasks = [
        service.get_forecast(d, m, h)
        for d, m, h in common_requests
    ]
    
    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("Cache warmed up")
```

### 8. Monitoring Integration

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
forecast_requests = Counter(
    'forecast_requests_total',
    'Total forecast requests',
    ['district', 'metric', 'horizon']
)

forecast_latency = Histogram(
    'forecast_latency_seconds',
    'Forecast request latency',
    buckets=[0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.5, 1.0]
)

forecast_errors = Counter(
    'forecast_errors_total',
    'Total forecast errors',
    ['error_type']
)

# Monitored wrapper
class MonitoredForecastService:
    def __init__(self, service: ForecastConsumption):
        self.service = service
    
    async def get_forecast(self, district_id, metric, horizon):
        # Record request
        forecast_requests.labels(
            district=district_id,
            metric=metric,
            horizon=str(horizon)
        ).inc()
        
        # Time the request
        start_time = time.time()
        
        try:
            result = await self.service.get_forecast(
                district_id, metric, horizon
            )
            
            # Record success latency
            forecast_latency.observe(time.time() - start_time)
            
            return result
            
        except Exception as e:
            # Record error
            forecast_errors.labels(
                error_type=type(e).__name__
            ).inc()
            
            # Still record latency for errors
            forecast_latency.observe(time.time() - start_time)
            
            raise
```

## Next Steps

1. Review the [API Documentation](../api/forecast-consumption-api.md)
2. Run the tests: `pytest tests/unit/application/use_cases/test_forecast_consumption.py`
3. Check performance: `pytest tests/performance/test_forecast_latency.py -v`
4. Deploy to your environment

For questions or issues, contact the Data Engineering team.