"""
Consumption Patterns API Router.

This router provides comprehensive endpoints for consumption patterns analysis,
replicating all functionality from the Streamlit consumption tab.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import asyncio
from fastapi import APIRouter, Query, HTTPException
import numpy as np
import pandas as pd

from src.schemas.api.consumption import (
    ConsumptionResponse, 
    ConsumptionMetrics, 
    HourlyPattern,
    DailyTrend,
    NodeConsumption,
    ConsumptionHeatmapData,
    ConsumptionInsights,
    ConsumptionComparison,
    ConsumptionForecast,
    ConsumptionAnomalyDetection,
    ErrorResponse
)
from src.infrastructure.data.hybrid_data_service import get_hybrid_data_service
from src.api.services.consumption_service import (
    get_consumption_data,
    calculate_consumption_metrics,
    generate_hourly_patterns,
    generate_daily_trends,
    generate_node_consumption,
    generate_heatmap_data,
    generate_consumption_insights
)

router = APIRouter(prefix="/api/v1/consumption", tags=["consumption"])


@router.get("/patterns", response_model=ConsumptionResponse)
async def get_consumption_patterns(
    time_range: str = Query("7d", description="Time range: 1h, 6h, 24h, 3d, 7d, 30d, 90d, 365d"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    include_insights: bool = Query(True, description="Include AI-generated insights"),
    include_heatmap: bool = Query(True, description="Include heatmap data")
):
    """
    Get comprehensive consumption patterns analysis.
    
    This endpoint replicates the functionality from the Streamlit consumption tab,
    providing detailed analysis of consumption patterns across the network.
    """
    try:
        # Get hybrid data service
        hybrid_service = await get_hybrid_data_service()
        
        # Parse time range
        start_time, end_time = _parse_time_range(time_range)
        
        # Get consumption data
        consumption_data = await get_consumption_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if consumption_data is None or consumption_data.empty:
            raise HTTPException(status_code=404, detail="No consumption data found")
        
        # Calculate metrics
        metrics = calculate_consumption_metrics(consumption_data)
        
        # Generate hourly patterns
        hourly_patterns = generate_hourly_patterns(consumption_data)
        
        # Generate daily trends
        daily_trends = generate_daily_trends(consumption_data)
        
        # Generate node consumption data
        node_consumption = generate_node_consumption(consumption_data)
        
        # Generate heatmap data if requested
        heatmap_data = []
        if include_heatmap:
            heatmap_data = generate_heatmap_data(consumption_data)
        
        # Generate insights if requested
        insights = []
        if include_insights:
            insights = generate_consumption_insights(consumption_data, metrics)
        
        return ConsumptionResponse(
            time_range=time_range,
            period_start=start_time.isoformat(),
            period_end=end_time.isoformat(),
            metrics=metrics,
            hourly_patterns=hourly_patterns,
            daily_trends=daily_trends,
            node_consumption=node_consumption,
            heatmap_data=heatmap_data,
            insights=insights,
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=ConsumptionMetrics)
async def get_consumption_metrics(
    time_range: str = Query("24h", description="Time range for metrics calculation"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get consumption metrics for the specified time range."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        consumption_data = await get_consumption_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if consumption_data is None or consumption_data.empty:
            raise HTTPException(status_code=404, detail="No consumption data found")
        
        return calculate_consumption_metrics(consumption_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hourly-patterns", response_model=List[HourlyPattern])
async def get_hourly_patterns(
    time_range: str = Query("7d", description="Time range for pattern analysis"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get hourly consumption patterns."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        consumption_data = await get_consumption_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if consumption_data is None or consumption_data.empty:
            raise HTTPException(status_code=404, detail="No consumption data found")
        
        return generate_hourly_patterns(consumption_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily-trends", response_model=List[DailyTrend])
async def get_daily_trends(
    time_range: str = Query("30d", description="Time range for trend analysis"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get daily consumption trends."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        consumption_data = await get_consumption_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if consumption_data is None or consumption_data.empty:
            raise HTTPException(status_code=404, detail="No consumption data found")
        
        return generate_daily_trends(consumption_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/node-comparison", response_model=List[NodeConsumption])
async def get_node_comparison(
    time_range: str = Query("24h", description="Time range for comparison"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get consumption comparison between nodes."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        consumption_data = await get_consumption_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if consumption_data is None or consumption_data.empty:
            raise HTTPException(status_code=404, detail="No consumption data found")
        
        return generate_node_consumption(consumption_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heatmap", response_model=List[ConsumptionHeatmapData])
async def get_consumption_heatmap(
    time_range: str = Query("7d", description="Time range for heatmap"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get consumption heatmap data."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        consumption_data = await get_consumption_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if consumption_data is None or consumption_data.empty:
            raise HTTPException(status_code=404, detail="No consumption data found")
        
        return generate_heatmap_data(consumption_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights", response_model=List[ConsumptionInsights])
async def get_consumption_insights(
    time_range: str = Query("7d", description="Time range for insights"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get AI-generated consumption insights."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        consumption_data = await get_consumption_data(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        if consumption_data is None or consumption_data.empty:
            raise HTTPException(status_code=404, detail="No consumption data found")
        
        metrics = calculate_consumption_metrics(consumption_data)
        return generate_consumption_insights(consumption_data, metrics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison", response_model=ConsumptionComparison)
async def get_consumption_comparison(
    current_period: str = Query("7d", description="Current period time range"),
    comparison_period: str = Query("7d", description="Comparison period time range"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Compare consumption between two periods."""
    try:
        hybrid_service = await get_hybrid_data_service()
        
        # Get current period data
        current_start, current_end = _parse_time_range(current_period)
        current_data = await get_consumption_data(
            hybrid_service, current_start, current_end, selected_nodes
        )
        
        # Get comparison period data (offset by the period duration)
        period_duration = current_end - current_start
        comparison_start = current_start - period_duration
        comparison_end = current_start
        
        comparison_data = await get_consumption_data(
            hybrid_service, comparison_start, comparison_end, selected_nodes
        )
        
        if current_data is None or comparison_data is None:
            raise HTTPException(status_code=404, detail="Insufficient data for comparison")
        
        current_metrics = calculate_consumption_metrics(current_data)
        previous_metrics = calculate_consumption_metrics(comparison_data)
        
        # Calculate percentage change
        percentage_change = ((current_metrics.total_consumption_m3 - 
                            previous_metrics.total_consumption_m3) / 
                           previous_metrics.total_consumption_m3) * 100
        
        # Determine trend direction
        if percentage_change > 5:
            trend_direction = "increasing"
        elif percentage_change < -5:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        
        # Generate significant changes
        significant_changes = []
        if abs(percentage_change) > 10:
            significant_changes.append(f"Total consumption changed by {percentage_change:.1f}%")
        
        return ConsumptionComparison(
            current_period=current_metrics,
            previous_period=previous_metrics,
            percentage_change=percentage_change,
            trend_direction=trend_direction,
            significant_changes=significant_changes
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