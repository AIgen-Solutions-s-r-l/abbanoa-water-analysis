"""FastAPI application for water infrastructure monitoring."""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.application.dto.analysis_results_dto import (
    AnomalyDetectionResultDTO,
    ConsumptionPatternDTO,
    NetworkEfficiencyResultDTO,
)
from src.infrastructure.di_container import Container
from src.presentation.api.endpoints.forecast_endpoint import router as forecast_router
from src.presentation.api.middleware.error_handler import ErrorHandlerMiddleware, register_error_handlers


# API models
class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime
    version: str


class AnomalyDetectionRequest(BaseModel):
    """Request for anomaly detection."""

    node_ids: Optional[List[UUID]] = None
    time_window_hours: int = 24
    notify_on_critical: bool = True


class ConsumptionAnalysisRequest(BaseModel):
    """Request for consumption analysis."""

    node_id: UUID
    start_date: datetime
    end_date: datetime
    pattern_type: str = "daily"


class EfficiencyCalculationRequest(BaseModel):
    """Request for efficiency calculation."""

    network_id: UUID
    start_date: datetime
    end_date: datetime
    include_node_details: bool = True


# Initialize FastAPI app
app = FastAPI(
    title="Abbanoa Water Infrastructure API",
    description="API for water infrastructure monitoring and analysis",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handler middleware
app.add_middleware(ErrorHandlerMiddleware)

# Register error handlers
register_error_handlers(app)

# Initialize DI container
container = Container()
container.config.bigquery.project_id.from_env(
    "BIGQUERY_PROJECT_ID", default="abbanoa-464816"
)
container.config.bigquery.dataset_id.from_env(
    "BIGQUERY_DATASET_ID", default="water_infrastructure"
)
container.config.bigquery.location.from_env("BIGQUERY_LOCATION", default="EU")
container.config.anomaly_detection.z_score_threshold.from_env(
    "ANOMALY_Z_SCORE", default=3.0
)
container.config.anomaly_detection.min_data_points.from_env(
    "ANOMALY_MIN_POINTS", default=10
)
container.config.anomaly_detection.rolling_window_hours.from_env(
    "ANOMALY_WINDOW_HOURS", default=24
)

# Include routers
app.include_router(forecast_router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    import logging
    from src.infrastructure.logging.forecast_logger import configure_application_logging
    
    # Configure logging
    configure_application_logging(log_level="INFO")
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Abbanoa Water Infrastructure API...")
    
    # Wire the container
    container.wire(
        modules=[
            "src.presentation.api.app",
            "src.application.use_cases.analyze_consumption_patterns",
            "src.application.use_cases.detect_network_anomalies",
            "src.application.use_cases.calculate_network_efficiency",
            "src.application.use_cases.forecast_consumption",
        ]
    )
    
    logger.info("Dependency injection container wired successfully")
    logger.info(f"API ready with forecast endpoint at /api/v1/forecasts")


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", timestamp=datetime.now(), version="1.0.0")


@app.post("/api/v1/anomalies/detect")
async def detect_anomalies(request: AnomalyDetectionRequest) -> List[dict]:
    """Detect anomalies in sensor readings."""
    try:
        use_case = container.detect_network_anomalies_use_case()

        anomalies = await use_case.execute(
            node_ids=request.node_ids,
            time_window_hours=request.time_window_hours,
            notify_on_critical=request.notify_on_critical,
        )

        return [
            {
                "node_id": str(a.node_id),
                "timestamp": a.timestamp.isoformat(),
                "anomaly_type": a.anomaly_type,
                "severity": a.severity,
                "measurement_type": a.measurement_type,
                "actual_value": a.actual_value,
                "expected_range": a.expected_range,
                "deviation_percentage": a.deviation_percentage,
                "description": a.description,
            }
            for a in anomalies
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/consumption/analyze")
async def analyze_consumption(request: ConsumptionAnalysisRequest) -> dict:
    """Analyze water consumption patterns."""
    try:
        use_case = container.analyze_consumption_patterns_use_case()

        result = await use_case.execute(
            node_id=request.node_id,
            start_date=request.start_date,
            end_date=request.end_date,
            pattern_type=request.pattern_type,
        )

        return {
            "node_id": str(result.node_id),
            "pattern_type": result.pattern_type,
            "average_consumption": result.average_consumption,
            "peak_hours": result.peak_hours,
            "off_peak_hours": result.off_peak_hours,
            "variability_coefficient": result.variability_coefficient,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/efficiency/calculate")
async def calculate_efficiency(request: EfficiencyCalculationRequest) -> dict:
    """Calculate network efficiency metrics."""
    try:
        use_case = container.calculate_network_efficiency_use_case()

        result = await use_case.execute(
            network_id=request.network_id,
            start_date=request.start_date,
            end_date=request.end_date,
            include_node_details=request.include_node_details,
        )

        return {
            "network_id": str(result.network_id),
            "period_start": result.period_start.isoformat(),
            "period_end": result.period_end.isoformat(),
            "efficiency_percentage": result.efficiency_percentage,
            "total_input_volume": result.total_input_volume,
            "total_output_volume": result.total_output_volume,
            "loss_volume": result.loss_volume,
            "loss_percentage": result.loss_percentage,
            "node_contributions": result.node_contributions,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/nodes")
async def list_nodes(
    active_only: bool = Query(False, description="Filter only active nodes"),
    node_type: Optional[str] = Query(None, description="Filter by node type"),
    location: Optional[str] = Query(None, description="Filter by location"),
) -> List[dict]:
    """List monitoring nodes."""
    try:
        repository = container.monitoring_node_repository()

        nodes = await repository.get_all(
            active_only=active_only, node_type=node_type, location=location
        )

        return [
            {
                "id": str(node.id),
                "name": node.name,
                "location": node.location.to_dict(),
                "node_type": node.node_type,
                "status": node.status.value,
                "description": node.description,
            }
            for node in nodes
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/nodes/{node_id}")
async def get_node(node_id: UUID) -> dict:
    """Get details of a specific node."""
    try:
        repository = container.monitoring_node_repository()

        node = await repository.get_by_id(node_id)

        if not node:
            raise HTTPException(status_code=404, detail="Node not found")

        return {
            "id": str(node.id),
            "name": node.name,
            "location": node.location.to_dict(),
            "node_type": node.node_type,
            "status": node.status.value,
            "description": node.description,
            "created_at": node.created_at.isoformat(),
            "updated_at": node.updated_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/nodes/{node_id}/readings")
async def get_node_readings(
    node_id: UUID,
    start_time: Optional[datetime] = Query(None, description="Start time for readings"),
    end_time: Optional[datetime] = Query(None, description="End time for readings"),
    limit: int = Query(100, description="Maximum number of readings to return"),
) -> List[dict]:
    """Get sensor readings for a specific node."""
    try:
        repository = container.sensor_reading_repository()

        readings = await repository.get_by_node_id(
            node_id=node_id, start_time=start_time, end_time=end_time, limit=limit
        )

        return [
            {
                "id": str(reading.id),
                "node_id": str(reading.node_id),
                "sensor_type": reading.sensor_type.value,
                "timestamp": reading.timestamp.isoformat(),
                "temperature": (
                    reading.temperature.value if reading.temperature else None
                ),
                "flow_rate": reading.flow_rate.value if reading.flow_rate else None,
                "pressure": reading.pressure.value if reading.pressure else None,
                "volume": reading.volume.value if reading.volume else None,
            }
            for reading in readings
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/networks")
async def list_networks() -> List[dict]:
    """List water networks."""
    try:
        repository = container.water_network_repository()

        networks = await repository.get_all()

        return [
            {
                "id": str(network.id),
                "name": network.name,
                "region": network.region,
                "description": network.description,
                "node_count": network.node_count,
                "active_node_count": network.active_node_count,
            }
            for network in networks
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
