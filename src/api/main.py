"""
FastAPI REST API for Abbanoa Water Infrastructure.

This API provides access to pre-computed metrics, ML predictions,
and system status without requiring direct database access.
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from src.infrastructure.database.postgres_manager import get_postgres_manager
from src.infrastructure.cache.redis_cache_manager import RedisCacheManager


# Pydantic models for API responses
class NodeMetrics(BaseModel):
    """Node metrics response model."""
    node_id: str
    node_name: str
    timestamp: datetime
    flow_rate: float = Field(description="Flow rate in L/s")
    pressure: float = Field(description="Pressure in bar")
    temperature: float = Field(description="Temperature in °C")
    efficiency: float = Field(description="Efficiency percentage")
    anomaly_count: int = Field(description="Number of anomalies detected")
    
    
class NetworkMetrics(BaseModel):
    """Network-wide metrics response model."""
    timestamp: datetime
    active_nodes: int
    total_flow: float = Field(description="Total network flow in L/s")
    avg_pressure: float = Field(description="Average pressure in bar")
    total_volume: float = Field(description="Total volume in m³")
    efficiency_percentage: float
    anomaly_count: int
    

class MLPrediction(BaseModel):
    """ML prediction response model."""
    node_id: str
    prediction_timestamp: datetime
    target_timestamp: datetime
    predicted_value: float
    lower_bound: float
    upper_bound: float
    confidence_score: float
    model_type: str
    

class DataQuality(BaseModel):
    """Data quality metrics response model."""
    node_id: str
    check_timestamp: datetime
    completeness_score: float
    validity_score: float
    consistency_score: float
    overall_quality_score: float
    issues: List[Dict[str, Any]]
    

class SystemStatus(BaseModel):
    """System status response model."""
    status: str = Field(description="Overall system status")
    processing_service: Dict[str, Any]
    active_models: Dict[str, Any]
    data_freshness: Dict[str, Any]
    redis_status: Dict[str, Any]
    

# Lifespan manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    app.state.postgres = await get_postgres_manager()
    app.state.redis = RedisCacheManager()
    yield
    # Shutdown
    await app.state.postgres.close()


# Create FastAPI app
app = FastAPI(
    title="Abbanoa Water Infrastructure API",
    description="REST API for accessing water infrastructure metrics and predictions",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now()}


# Node endpoints
@app.get("/api/v1/nodes", response_model=List[Dict[str, Any]])
async def get_nodes():
    """Get list of all active nodes."""
    try:
        nodes = await app.state.postgres.get_all_nodes()
        return nodes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/nodes/{node_id}/metrics", response_model=NodeMetrics)
async def get_node_metrics(
    node_id: str,
    time_window: str = Query("1hour", description="Time window: 5min, 1hour, 1day")
):
    """Get latest metrics for a specific node."""
    try:
        async with app.state.postgres.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT 
                    cm.node_id,
                    n.node_name,
                    cm.window_end as timestamp,
                    cm.avg_flow_rate as flow_rate,
                    cm.avg_pressure as pressure,
                    cm.avg_temperature as temperature,
                    COALESCE(cm.quality_score * 100, 95.0) as efficiency,
                    cm.anomaly_count
                FROM water_infrastructure.computed_metrics cm
                JOIN water_infrastructure.nodes n ON cm.node_id = n.node_id
                WHERE cm.node_id = $1 
                AND cm.time_window = $2
                ORDER BY cm.window_end DESC
                LIMIT 1
            """, node_id, time_window)
            
        if not result:
            raise HTTPException(status_code=404, detail="Node metrics not found")
            
        return NodeMetrics(**dict(result))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/nodes/{node_id}/history")
async def get_node_history(
    node_id: str,
    start_time: Optional[datetime] = Query(None, description="Start time for history"),
    end_time: Optional[datetime] = Query(None, description="End time for history"),
    time_window: str = Query("1hour", description="Time window: 5min, 1hour, 1day")
):
    """Get historical metrics for a node."""
    try:
        # Default time range if not specified
        if not end_time:
            end_time = datetime.now()
        if not start_time:
            start_time = end_time - timedelta(days=7)
            
        async with app.state.postgres.acquire() as conn:
            results = await conn.fetch("""
                SELECT 
                    window_start,
                    window_end,
                    avg_flow_rate,
                    avg_pressure,
                    avg_temperature,
                    total_volume,
                    anomaly_count,
                    quality_score
                FROM water_infrastructure.computed_metrics
                WHERE node_id = $1 
                AND time_window = $2
                AND window_start >= $3
                AND window_end <= $4
                ORDER BY window_start
            """, node_id, time_window, start_time, end_time)
            
        return [dict(r) for r in results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Network metrics endpoints
@app.get("/api/v1/network/metrics", response_model=NetworkMetrics)
async def get_network_metrics(
    time_range: str = Query("24h", description="Time range: 1h, 6h, 24h, 3d, 7d, 30d")
):
    """Get network-wide metrics."""
    try:
        # Try Redis cache first
        cache_key = f"system:metrics:{time_range}"
        cached = app.state.redis.redis_client.hgetall(cache_key)
        
        if cached:
            return NetworkMetrics(
                timestamp=datetime.now(),
                active_nodes=int(cached.get(b'active_nodes', 0)),
                total_flow=float(cached.get(b'total_flow', 0)),
                avg_pressure=float(cached.get(b'avg_pressure', 0)),
                total_volume=float(cached.get(b'total_volume', 0)),
                efficiency_percentage=95.0,  # Placeholder
                anomaly_count=int(cached.get(b'anomaly_count', 0))
            )
            
        # Fallback to database
        interval_map = {
            "1h": "1 hour",
            "6h": "6 hours",
            "24h": "24 hours",
            "3d": "3 days",
            "7d": "7 days",
            "30d": "30 days"
        }
        interval = interval_map.get(time_range, "24 hours")
        
        metrics = await app.state.postgres.get_system_metrics(interval)
        
        return NetworkMetrics(
            timestamp=datetime.now(),
            active_nodes=metrics.get('active_nodes', 0),
            total_flow=metrics.get('total_flow', 0),
            avg_pressure=metrics.get('avg_pressure', 0),
            total_volume=metrics.get('total_volume_m3', 0),
            efficiency_percentage=95.0,
            anomaly_count=metrics.get('anomaly_count', 0)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/network/efficiency")
async def get_network_efficiency(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None)
):
    """Get network efficiency metrics."""
    try:
        if not end_time:
            end_time = datetime.now()
        if not start_time:
            start_time = end_time - timedelta(days=1)
            
        async with app.state.postgres.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT 
                    computation_timestamp,
                    total_input_volume,
                    total_output_volume,
                    efficiency_percentage,
                    active_nodes,
                    total_anomalies,
                    zone_metrics
                FROM water_infrastructure.network_efficiency
                WHERE window_start >= $1 AND window_end <= $2
                ORDER BY computation_timestamp DESC
                LIMIT 1
            """, start_time, end_time)
            
        if not result:
            raise HTTPException(status_code=404, detail="No efficiency data found")
            
        return dict(result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ML predictions endpoints
@app.get("/api/v1/predictions/{node_id}", response_model=List[MLPrediction])
async def get_predictions(
    node_id: str,
    model_type: str = Query("flow_prediction", description="Model type"),
    horizon_hours: int = Query(24, description="Prediction horizon in hours")
):
    """Get ML predictions for a node."""
    try:
        async with app.state.postgres.acquire() as conn:
            results = await conn.fetch("""
                SELECT 
                    p.node_id,
                    p.prediction_timestamp,
                    p.target_timestamp,
                    p.predicted_flow_rate as predicted_value,
                    p.flow_rate_lower as lower_bound,
                    p.flow_rate_upper as upper_bound,
                    p.confidence_score,
                    m.model_type
                FROM water_infrastructure.ml_predictions_cache p
                JOIN water_infrastructure.ml_models m ON p.model_id = m.model_id
                WHERE p.node_id = $1
                AND m.model_type = $2
                AND p.target_timestamp <= CURRENT_TIMESTAMP + INTERVAL '%s hours'
                AND p.target_timestamp > CURRENT_TIMESTAMP
                ORDER BY p.target_timestamp
            """ % horizon_hours, node_id, model_type)
            
        return [MLPrediction(**dict(r)) for r in results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Data quality endpoints
@app.get("/api/v1/quality/{node_id}", response_model=DataQuality)
async def get_data_quality(node_id: str):
    """Get data quality metrics for a node."""
    try:
        async with app.state.postgres.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT 
                    node_id,
                    check_timestamp,
                    completeness_score,
                    validity_score,
                    consistency_score,
                    overall_quality_score,
                    quality_issues as issues
                FROM water_infrastructure.data_quality_metrics
                WHERE node_id = $1
                ORDER BY check_timestamp DESC
                LIMIT 1
            """, node_id)
            
        if not result:
            # Return default quality metrics
            return DataQuality(
                node_id=node_id,
                check_timestamp=datetime.now(),
                completeness_score=1.0,
                validity_score=1.0,
                consistency_score=1.0,
                overall_quality_score=1.0,
                issues=[]
            )
            
        return DataQuality(**dict(result))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# System status endpoints
@app.get("/api/v1/status", response_model=SystemStatus)
async def get_system_status():
    """Get overall system status."""
    try:
        # Check processing service status
        async with app.state.postgres.acquire() as conn:
            last_job = await conn.fetchrow("""
                SELECT status, completed_at
                FROM water_infrastructure.processing_jobs
                WHERE job_type = 'data_processing'
                ORDER BY created_at DESC
                LIMIT 1
            """)
            
            # Get active models
            active_models = await conn.fetch("""
                SELECT model_type, version, created_at, metrics
                FROM water_infrastructure.ml_models
                WHERE is_active = TRUE
            """)
            
            # Get data freshness
            freshness = await conn.fetchrow("""
                SELECT 
                    MAX(window_end) as latest_data,
                    COUNT(DISTINCT node_id) as nodes_with_data
                FROM water_infrastructure.computed_metrics
                WHERE window_end > CURRENT_TIMESTAMP - INTERVAL '1 hour'
            """)
            
        # Check Redis status
        redis_info = app.state.redis.redis_client.info()
        redis_status = {
            "connected": True,
            "memory_used": redis_info.get("used_memory_human", "Unknown"),
            "keys": app.state.redis.redis_client.dbsize()
        }
        
        processing_status = "healthy"
        if last_job:
            if last_job['status'] == 'failed':
                processing_status = "degraded"
            elif (datetime.now() - last_job['completed_at']).seconds > 3600:
                processing_status = "stale"
                
        return SystemStatus(
            status=processing_status,
            processing_service={
                "last_run": last_job['completed_at'] if last_job else None,
                "status": last_job['status'] if last_job else "unknown"
            },
            active_models={
                model['model_type']: {
                    "version": model['version'],
                    "created_at": model['created_at'],
                    "performance": model['metrics']
                }
                for model in active_models
            },
            data_freshness={
                "latest_data": freshness['latest_data'] if freshness else None,
                "nodes_reporting": freshness['nodes_with_data'] if freshness else 0
            },
            redis_status=redis_status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Anomaly endpoints
@app.get("/api/v1/anomalies")
async def get_anomalies(
    hours: int = Query(24, description="Hours to look back"),
    node_id: Optional[str] = Query(None, description="Filter by node ID"),
    severity: Optional[str] = Query(None, description="Filter by severity")
):
    """Get recent anomalies."""
    try:
        query = """
            SELECT 
                a.*, 
                n.node_name
            FROM water_infrastructure.anomalies a
            JOIN water_infrastructure.nodes n ON a.node_id = n.node_id
            WHERE a.timestamp > CURRENT_TIMESTAMP - INTERVAL '%s hours'
            AND a.resolved_at IS NULL
        """ % hours
        
        params = []
        
        if node_id:
            params.append(node_id)
            query += f" AND a.node_id = ${len(params)}"
            
        if severity:
            params.append(severity)
            query += f" AND a.severity = ${len(params)}"
            
        query += " ORDER BY a.timestamp DESC LIMIT 100"
        
        async with app.state.postgres.acquire() as conn:
            results = await conn.fetch(query, *params)
            
        return [dict(r) for r in results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Dashboard summary endpoint
@app.get("/api/v1/dashboard/summary")
async def get_dashboard_summary():
    """Get summary data for dashboard display."""
    try:
        # This endpoint aggregates data for efficient dashboard loading
        async with app.state.postgres.acquire() as conn:
            # Get node summary
            nodes = await conn.fetch("""
                SELECT 
                    n.node_id,
                    n.node_name,
                    cm.avg_flow_rate as flow_rate,
                    cm.avg_pressure as pressure,
                    cm.anomaly_count,
                    cm.quality_score
                FROM water_infrastructure.nodes n
                LEFT JOIN LATERAL (
                    SELECT *
                    FROM water_infrastructure.computed_metrics
                    WHERE node_id = n.node_id
                    AND time_window = '1hour'
                    ORDER BY window_end DESC
                    LIMIT 1
                ) cm ON TRUE
                WHERE n.is_active = TRUE
            """)
            
            # Get network metrics
            network = await conn.fetchrow("""
                SELECT * FROM water_infrastructure.get_system_metrics(INTERVAL '24 hours')
            """)
            
            # Get recent anomalies count
            anomalies = await conn.fetchval("""
                SELECT COUNT(*)
                FROM water_infrastructure.anomalies
                WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
                AND resolved_at IS NULL
            """)
            
        return {
            "nodes": [dict(n) for n in nodes],
            "network": dict(network) if network else {},
            "recent_anomalies": anomalies,
            "last_update": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )