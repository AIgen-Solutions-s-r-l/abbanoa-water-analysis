"""
Water Quality Monitoring API Router.

This router provides comprehensive endpoints for water quality monitoring,
replicating all functionality from the Streamlit water quality tab.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import asyncio
from fastapi import APIRouter, Query, HTTPException
import numpy as np
import pandas as pd

from src.schemas.api.water_quality import (
    WaterQualityResponse,
    WaterQualityMetrics,
    TemperatureAnalysis,
    FlowVelocityAnalysis,
    PressureGradientAnalysis,
    QualityAlert,
    ContaminationIndicator,
    QualityTrend,
    NodeQualityProfile,
    QualityPrediction,
    QualityComparison,
    QualityReport,
    ErrorResponse
)
from src.infrastructure.data.hybrid_data_service import get_hybrid_data_service
from src.api.services.water_quality_service import (
    get_water_quality_data,
    calculate_quality_metrics,
    generate_temperature_analysis,
    generate_flow_velocity_analysis,
    generate_pressure_gradient_analysis,
    generate_quality_alerts,
    generate_contamination_indicators,
    generate_quality_trends,
    generate_node_quality_profiles,
    generate_quality_predictions
)

router = APIRouter(prefix="/api/v1/water-quality", tags=["water-quality"])


@router.get("/overview", response_model=WaterQualityResponse)
async def get_water_quality_overview(
    time_range: str = Query("24h", description="Time range: 1h, 6h, 24h, 3d, 7d, 30d"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    include_predictions: bool = Query(False, description="Include quality predictions"),
    include_alerts: bool = Query(True, description="Include quality alerts")
):
    """
    Get comprehensive water quality overview.
    
    This endpoint replicates the functionality from the Streamlit water quality tab,
    providing detailed analysis of water quality across the network.
    """
    try:
        # Get hybrid data service
        hybrid_service = await get_hybrid_data_service()
        
        # Parse time range
        start_time, end_time = _parse_time_range(time_range)
        
        # Get water quality data
        quality_data = await get_water_quality_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if quality_data is None or quality_data.empty:
            raise HTTPException(status_code=404, detail="No water quality data found")
        
        # Calculate metrics
        metrics = calculate_quality_metrics(quality_data)
        
        # Generate analysis components
        temperature_analysis = generate_temperature_analysis(quality_data)
        flow_velocity_analysis = generate_flow_velocity_analysis(quality_data)
        pressure_gradient_analysis = generate_pressure_gradient_analysis(quality_data)
        
        # Generate alerts if requested
        quality_alerts = []
        if include_alerts:
            quality_alerts = generate_quality_alerts(quality_data, metrics)
        
        # Generate contamination indicators
        contamination_indicators = generate_contamination_indicators(quality_data)
        
        # Generate quality trends
        quality_trends = generate_quality_trends(quality_data)
        
        # Generate node profiles
        node_profiles = generate_node_quality_profiles(quality_data)
        
        # Generate predictions if requested
        predictions = []
        if include_predictions:
            predictions = generate_quality_predictions(quality_data)
        
        return WaterQualityResponse(
            time_range=time_range,
            period_start=start_time.isoformat(),
            period_end=end_time.isoformat(),
            metrics=metrics,
            temperature_analysis=temperature_analysis,
            flow_velocity_analysis=flow_velocity_analysis,
            pressure_gradient_analysis=pressure_gradient_analysis,
            quality_alerts=quality_alerts,
            contamination_indicators=contamination_indicators,
            quality_trends=quality_trends,
            node_profiles=node_profiles,
            predictions=predictions,
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=WaterQualityMetrics)
async def get_quality_metrics(
    time_range: str = Query("24h", description="Time range for metrics calculation"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get water quality metrics for the specified time range."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        quality_data = await get_water_quality_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if quality_data is None or quality_data.empty:
            raise HTTPException(status_code=404, detail="No water quality data found")
        
        return calculate_quality_metrics(quality_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/temperature-analysis", response_model=List[TemperatureAnalysis])
async def get_temperature_analysis(
    time_range: str = Query("24h", description="Time range for temperature analysis"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get temperature analysis data."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        quality_data = await get_water_quality_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if quality_data is None or quality_data.empty:
            raise HTTPException(status_code=404, detail="No water quality data found")
        
        return generate_temperature_analysis(quality_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flow-velocity-analysis", response_model=List[FlowVelocityAnalysis])
async def get_flow_velocity_analysis(
    time_range: str = Query("24h", description="Time range for flow analysis"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get flow velocity analysis data."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        quality_data = await get_water_quality_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if quality_data is None or quality_data.empty:
            raise HTTPException(status_code=404, detail="No water quality data found")
        
        return generate_flow_velocity_analysis(quality_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pressure-gradient-analysis", response_model=List[PressureGradientAnalysis])
async def get_pressure_gradient_analysis(
    time_range: str = Query("24h", description="Time range for pressure analysis"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get pressure gradient analysis data."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        quality_data = await get_water_quality_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if quality_data is None or quality_data.empty:
            raise HTTPException(status_code=404, detail="No water quality data found")
        
        return generate_pressure_gradient_analysis(quality_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=List[QualityAlert])
async def get_quality_alerts(
    time_range: str = Query("24h", description="Time range for alerts"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    severity: Optional[str] = Query(None, description="Filter by severity")
):
    """Get water quality alerts."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        quality_data = await get_water_quality_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if quality_data is None or quality_data.empty:
            raise HTTPException(status_code=404, detail="No water quality data found")
        
        metrics = calculate_quality_metrics(quality_data)
        alerts = generate_quality_alerts(quality_data, metrics)
        
        # Filter alerts if specified
        if alert_type:
            alerts = [alert for alert in alerts if alert.alert_type == alert_type]
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        return alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contamination-indicators", response_model=List[ContaminationIndicator])
async def get_contamination_indicators(
    time_range: str = Query("24h", description="Time range for contamination analysis"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level")
):
    """Get contamination indicators."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        quality_data = await get_water_quality_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if quality_data is None or quality_data.empty:
            raise HTTPException(status_code=404, detail="No water quality data found")
        
        indicators = generate_contamination_indicators(quality_data)
        
        # Filter by risk level if specified
        if risk_level:
            indicators = [ind for ind in indicators if ind.risk_level == risk_level]
        
        return indicators
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality-trends", response_model=List[QualityTrend])
async def get_quality_trends(
    time_range: str = Query("7d", description="Time range for trend analysis"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get water quality trends."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        quality_data = await get_water_quality_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if quality_data is None or quality_data.empty:
            raise HTTPException(status_code=404, detail="No water quality data found")
        
        return generate_quality_trends(quality_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/node-profiles", response_model=List[NodeQualityProfile])
async def get_node_quality_profiles(
    time_range: str = Query("24h", description="Time range for profile analysis"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get node quality profiles."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        quality_data = await get_water_quality_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if quality_data is None or quality_data.empty:
            raise HTTPException(status_code=404, detail="No water quality data found")
        
        return generate_node_quality_profiles(quality_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions", response_model=List[QualityPrediction])
async def get_quality_predictions(
    time_range: str = Query("24h", description="Time range for prediction analysis"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    prediction_horizon: int = Query(24, description="Prediction horizon in hours")
):
    """Get water quality predictions."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        quality_data = await get_water_quality_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if quality_data is None or quality_data.empty:
            raise HTTPException(status_code=404, detail="No water quality data found")
        
        return generate_quality_predictions(quality_data, prediction_horizon)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison", response_model=QualityComparison)
async def get_quality_comparison(
    current_period: str = Query("24h", description="Current period time range"),
    comparison_period: str = Query("24h", description="Comparison period time range"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Compare water quality between two periods."""
    try:
        hybrid_service = await get_hybrid_data_service()
        
        # Get current period data
        current_start, current_end = _parse_time_range(current_period)
        current_data = await get_water_quality_data(
            hybrid_service, current_start, current_end, selected_nodes
        )
        
        # Get comparison period data (offset by the period duration)
        period_duration = current_end - current_start
        comparison_start = current_start - period_duration
        comparison_end = current_start
        
        comparison_data = await get_water_quality_data(
            hybrid_service, comparison_start, comparison_end, selected_nodes
        )
        
        if current_data is None or comparison_data is None:
            raise HTTPException(status_code=404, detail="Insufficient data for comparison")
        
        current_metrics = calculate_quality_metrics(current_data)
        previous_metrics = calculate_quality_metrics(comparison_data)
        
        # Analyze improvements and degradations
        improvement_areas = []
        degradation_areas = []
        
        if current_metrics.overall_quality_score > previous_metrics.overall_quality_score:
            improvement_areas.append("Overall Quality Score")
        else:
            degradation_areas.append("Overall Quality Score")
        
        if current_metrics.temperature_compliance > previous_metrics.temperature_compliance:
            improvement_areas.append("Temperature Compliance")
        else:
            degradation_areas.append("Temperature Compliance")
        
        if current_metrics.contamination_alerts < previous_metrics.contamination_alerts:
            improvement_areas.append("Contamination Alerts")
        else:
            degradation_areas.append("Contamination Alerts")
        
        # Determine overall trend
        score_change = current_metrics.overall_quality_score - previous_metrics.overall_quality_score
        if score_change > 5:
            overall_trend = "improving"
        elif score_change < -5:
            overall_trend = "declining"
        else:
            overall_trend = "stable"
        
        # Generate recommendations
        recommendations = []
        if degradation_areas:
            recommendations.append(f"Focus on improving: {', '.join(degradation_areas)}")
        if current_metrics.contamination_alerts > 0:
            recommendations.append("Investigate contamination sources")
        if current_metrics.temperature_compliance < 90:
            recommendations.append("Review temperature control systems")
        
        return QualityComparison(
            current_metrics=current_metrics,
            previous_metrics=previous_metrics,
            improvement_areas=improvement_areas,
            degradation_areas=degradation_areas,
            overall_trend=overall_trend,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
def _parse_time_range(time_range: str) -> tuple:
    """Parse time range string to start and end datetime objects."""
    now = datetime.now()
    
    time_mappings = {
        "1h": timedelta(hours=1),
        "6h": timedelta(hours=6),
        "24h": timedelta(hours=24),
        "3d": timedelta(days=3),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "90d": timedelta(days=90),
        "365d": timedelta(days=365)
    }
    
    if time_range not in time_mappings:
        raise HTTPException(status_code=400, detail=f"Invalid time range: {time_range}")
    
    delta = time_mappings[time_range]
    start_time = now - delta
    
    return start_time, now 