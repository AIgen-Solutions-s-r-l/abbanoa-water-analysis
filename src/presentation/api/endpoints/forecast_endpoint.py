"""Forecast API endpoint implementation."""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.application.use_cases.forecast_consumption import ForecastConsumption
from src.infrastructure.clients.async_bigquery_client import AsyncBigQueryClient
from src.infrastructure.repositories.bigquery_forecast_repository import (
    BigQueryForecastRepository,
)
from src.infrastructure.services.forecast_calculation_service import (
    ForecastCalculationService,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/forecasts", tags=["forecasts"])


# Request/Response models
class ForecastResponse(BaseModel):
    """Forecast API response model."""

    district_id: str = Field(..., description="District identifier")
    metric: str = Field(..., description="Metric type")
    horizon: int = Field(..., description="Forecast horizon in days")
    forecast_data: List[Dict] = Field(..., description="Forecast time series data")
    historical_data: Optional[List[Dict]] = Field(
        None, description="Historical time series data"
    )
    metrics: Optional[Dict] = Field(
        None, description="Calculated metrics and statistics"
    )
    metadata: Dict = Field(..., description="Response metadata")


class ForecastDataPoint(BaseModel):
    """Individual forecast data point."""

    timestamp: datetime
    value: float
    lower_bound: float
    upper_bound: float
    confidence_level: float = 0.8


# Dependency injection
async def get_forecast_use_case() -> ForecastConsumption:
    """Get forecast use case with dependencies."""
    # Initialize BigQuery client with configurable timeouts
    import os

    query_timeout = int(os.getenv("BIGQUERY_QUERY_TIMEOUT_MS", "30000"))  # 30s default
    conn_timeout = int(
        os.getenv("BIGQUERY_CONNECTION_TIMEOUT_MS", "60000")
    )  # 60s default

    async_client = AsyncBigQueryClient(
        project_id="abbanoa-464816",
        dataset_id="water_infrastructure",
        query_timeout_ms=query_timeout,
        connection_timeout_ms=conn_timeout,
    )

    # Create repository and calculation service
    forecast_repository = BigQueryForecastRepository(async_client)
    calculation_service = ForecastCalculationService(async_client)

    # Create use case
    return ForecastConsumption(
        forecast_repository=forecast_repository,
        forecast_calculation_service=calculation_service,
        logger=logger,
    )


@router.get("/{district_id}/{metric}")
async def get_forecast(
    district_id: str,
    metric: str,
    horizon: int = Query(7, ge=1, le=30, description="Forecast horizon in days"),
    include_historical: bool = Query(True, description="Include historical data"),
    historical_days: int = Query(
        30, ge=0, le=120, description="Days of historical data"
    ),
    use_case: ForecastConsumption = Depends(get_forecast_use_case),
) -> ForecastResponse:
    """
    Get forecast for a specific district and metric.

    Args:
        district_id: District identifier (e.g., 'DIST_001', 'DIST_002')
        metric: Metric type ('flow_rate', 'pressure', 'reservoir_level')
        horizon: Forecast horizon in days (1-30, default: 7)
        include_historical: Whether to include historical data (default: True)
        historical_days: Number of historical days to include (7-90, default: 30)

    Returns:
        ForecastResponse with predictions, historical data, and metrics

    Raises:
        400: Invalid request parameters
        404: District or metric not found
        500: Internal server error
    """
    try:
        logger.info(
            f"Forecast request: district={district_id}, metric={metric}, "
            f"horizon={horizon}, include_historical={include_historical}"
        )

        # Validate inputs
        valid_districts = [
            "node-serbatoio",
            "node-seneca",
            "node-santanna",
            "DIST_001",
            "DIST_002",
        ]
        valid_metrics = ["flow_rate", "pressure", "temperature"]

        if district_id not in valid_districts:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid district_id. Must be one of: {valid_districts}",
            )

        if metric not in valid_metrics:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid metric. Must be one of: {valid_metrics}",
            )

        # Get forecast with calculations
        results = await use_case.get_forecast_with_calculations(
            district_id=district_id,
            metric=metric,
            horizon=horizon,
            include_historical=include_historical,
            historical_days=historical_days,
        )

        # Format forecast data
        forecast_data = []
        if "forecast" in results and not results["forecast"].empty:
            for _, row in results["forecast"].iterrows():
                forecast_data.append(
                    {
                        "timestamp": row["timestamp"].isoformat(),
                        "value": float(row.get("forecast_value", row.get("value", 0))),
                        "lower_bound": float(row.get("lower_bound", 0)),
                        "upper_bound": float(row.get("upper_bound", 0)),
                        "confidence_level": float(row.get("confidence_level", 0.8)),
                    }
                )

        # Format historical data if included
        historical_data = None
        if (
            include_historical
            and "historical" in results
            and not results["historical"].empty
        ):
            historical_data = []
            for _, row in results["historical"].iterrows():
                historical_data.append(
                    {
                        "timestamp": row["timestamp"].isoformat(),
                        "value": float(row["value"]),
                        "ma_7": float(row.get("ma_7", row["value"])),
                        "ma_30": float(row.get("ma_30", row["value"])),
                    }
                )

        # Extract metrics
        metrics = results.get("metrics", {})

        # Prepare metadata
        metadata = results.get("metadata", {})
        metadata.update(
            {
                "requested_at": datetime.utcnow().isoformat(),
                "horizon_days": horizon,
                "historical_days": historical_days if include_historical else 0,
                "total_forecast_points": len(forecast_data),
                "total_historical_points": (
                    len(historical_data) if historical_data else 0
                ),
            }
        )

        return ForecastResponse(
            district_id=district_id,
            metric=metric,
            horizon=horizon,
            forecast_data=forecast_data,
            historical_data=historical_data,
            metrics=metrics,
            metadata=metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing forecast request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{district_id}/{metric}/latest")
async def get_latest_forecast(
    district_id: str,
    metric: str,
    use_case: ForecastConsumption = Depends(get_forecast_use_case),
) -> Dict:
    """
    Get the latest cached forecast for a district and metric.

    This endpoint returns the most recently generated forecast without
    triggering a new calculation, useful for quick dashboard updates.

    Args:
        district_id: District identifier
        metric: Metric type

    Returns:
        Latest forecast data if available

    Raises:
        404: No cached forecast found
    """
    try:
        # For now, generate a fresh 7-day forecast
        # In production, this would retrieve from cache
        results = await use_case.get_forecast_with_calculations(
            district_id=district_id,
            metric=metric,
            horizon=7,
            include_historical=False,
            historical_days=0,
        )

        if "forecast" not in results or results["forecast"].empty:
            raise HTTPException(
                status_code=404, detail=f"No forecast found for {district_id}/{metric}"
            )

        # Return simplified response
        forecast_df = results["forecast"]
        return {
            "district_id": district_id,
            "metric": metric,
            "latest_timestamp": forecast_df["timestamp"].max().isoformat(),
            "next_value": (
                float(forecast_df.iloc[0]["value"]) if len(forecast_df) > 0 else None
            ),
            "generated_at": results.get("metadata", {}).get(
                "generated_at", datetime.utcnow().isoformat()
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest forecast: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/status")
async def get_models_status() -> Dict:
    """
    Get status of all forecast models.

    Returns:
        Dictionary with model status information
    """
    try:
        # Model configuration
        models = [
            {"district": "DIST_001", "metric": "flow_rate"},
            {"district": "DIST_001", "metric": "pressure"},
            {"district": "DIST_001", "metric": "reservoir_level"},
            {"district": "DIST_002", "metric": "flow_rate"},
            {"district": "DIST_002", "metric": "pressure"},
            {"district": "DIST_002", "metric": "reservoir_level"},
        ]

        model_status = []
        for model in models:
            model_name = f"arima_{model['district'].lower()}_{model['metric']}"
            model_status.append(
                {
                    "model_name": model_name,
                    "district": model["district"],
                    "metric": model["metric"],
                    "status": "active",  # In production, check actual model status
                    "last_trained": "2024-01-15T00:00:00Z",  # Placeholder
                    "accuracy_mape": 12.5,  # Placeholder
                }
            )

        return {
            "total_models": len(model_status),
            "active_models": len([m for m in model_status if m["status"] == "active"]),
            "models": model_status,
            "last_updated": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting model status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
