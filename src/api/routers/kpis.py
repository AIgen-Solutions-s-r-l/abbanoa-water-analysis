"""
KPI Dashboard API Router.

This router provides comprehensive endpoints for KPI monitoring and dashboard management,
supporting real-time metrics, alerts, and performance tracking.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import asyncio
from fastapi import APIRouter, Query, HTTPException

from src.schemas.api.kpis import (
    KPIDashboard,
    KPIMetric,
    KPICard,
    SystemPerformanceKPIs,
    NetworkEfficiencyKPIs,
    QualityKPIs,
    MaintenanceKPIs,
    OperationalKPIs,
    FinancialKPIs,
    ComplianceKPIs,
    KPITrend,
    KPIBenchmark,
    KPIAlert,
    KPIGoal,
    KPIReport,
    KPIComparison,
    KPIConfiguration,
    KPIHealth,
    ErrorResponse
)
from src.infrastructure.data.hybrid_data_service import get_hybrid_data_service
from src.api.services.kpis_service import (
    generate_kpi_dashboard,
    calculate_system_performance_kpis,
    calculate_network_efficiency_kpis,
    calculate_quality_kpis,
    calculate_maintenance_kpis,
    calculate_operational_kpis,
    calculate_financial_kpis,
    calculate_compliance_kpis,
    generate_kpi_cards,
    generate_kpi_trends,
    generate_kpi_benchmarks,
    generate_kpi_alerts,
    generate_kpi_goals,
    generate_kpi_report,
    compare_kpi_periods,
    get_kpi_configuration,
    get_kpi_health
)

router = APIRouter(prefix="/api/v1/kpis", tags=["kpis"])


@router.get("/dashboard", response_model=KPIDashboard)
async def get_kpi_dashboard(
    time_range: str = Query("24h", description="Time range: 1h, 6h, 24h, 7d, 30d"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    include_alerts: bool = Query(True, description="Include active alerts"),
    include_trends: bool = Query(False, description="Include trend analysis"),
    dashboard_type: str = Query("operational", description="Dashboard type: operational, executive, technical")
):
    """
    Get comprehensive KPI dashboard.
    
    This endpoint provides a complete KPI dashboard with all key performance
    indicators organized by category.
    """
    try:
        # Get hybrid data service
        hybrid_service = await get_hybrid_data_service()
        
        # Parse time range
        start_time, end_time = _parse_time_range(time_range)
        
        # Generate comprehensive KPI dashboard
        dashboard = await generate_kpi_dashboard(
            hybrid_service=hybrid_service,
            start_time=start_time,
            end_time=end_time,
            selected_nodes=selected_nodes,
            include_alerts=include_alerts,
            include_trends=include_trends,
            dashboard_type=dashboard_type
        )
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-performance", response_model=SystemPerformanceKPIs)
async def get_system_performance_kpis(
    time_range: str = Query("24h", description="Time range for KPI calculation"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get system performance KPIs."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        kpis = await calculate_system_performance_kpis(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return kpis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network-efficiency", response_model=NetworkEfficiencyKPIs)
async def get_network_efficiency_kpis(
    time_range: str = Query("24h", description="Time range for KPI calculation"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get network efficiency KPIs."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        kpis = await calculate_network_efficiency_kpis(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return kpis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality", response_model=QualityKPIs)
async def get_quality_kpis(
    time_range: str = Query("24h", description="Time range for KPI calculation"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get quality KPIs."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        kpis = await calculate_quality_kpis(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return kpis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/maintenance", response_model=MaintenanceKPIs)
async def get_maintenance_kpis(
    time_range: str = Query("30d", description="Time range for maintenance KPIs"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get maintenance KPIs."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        kpis = await calculate_maintenance_kpis(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return kpis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/operational", response_model=OperationalKPIs)
async def get_operational_kpis(
    time_range: str = Query("24h", description="Time range for operational KPIs"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get operational KPIs."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        kpis = await calculate_operational_kpis(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return kpis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/financial", response_model=FinancialKPIs)
async def get_financial_kpis(
    time_range: str = Query("30d", description="Time range for financial KPIs"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get financial KPIs."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        kpis = await calculate_financial_kpis(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return kpis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance", response_model=ComplianceKPIs)
async def get_compliance_kpis(
    time_range: str = Query("30d", description="Time range for compliance KPIs"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get compliance KPIs."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        kpis = await calculate_compliance_kpis(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return kpis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cards", response_model=List[KPICard])
async def get_kpi_cards(
    time_range: str = Query("24h", description="Time range for KPI cards"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    card_type: str = Query("summary", description="Card type: summary, detailed, executive"),
    limit: int = Query(10, description="Maximum number of cards to return")
):
    """Get KPI cards for dashboard display."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        cards = await generate_kpi_cards(
            hybrid_service, start_time, end_time, selected_nodes, card_type, limit
        )
        
        return cards
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends", response_model=List[KPITrend])
async def get_kpi_trends(
    time_range: str = Query("7d", description="Time range for trend analysis"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    kpi_categories: Optional[List[str]] = Query(None, description="KPI categories to include"),
    resolution: str = Query("hour", description="Trend resolution: hour, day, week")
):
    """Get KPI trends over time."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        trends = await generate_kpi_trends(
            hybrid_service, start_time, end_time, selected_nodes, kpi_categories, resolution
        )
        
        return trends
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks", response_model=List[KPIBenchmark])
async def get_kpi_benchmarks(
    time_range: str = Query("30d", description="Time range for benchmark calculation"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    benchmark_type: str = Query("industry", description="Benchmark type: industry, historical, target")
):
    """Get KPI benchmarks for comparison."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        benchmarks = await generate_kpi_benchmarks(
            hybrid_service, start_time, end_time, selected_nodes, benchmark_type
        )
        
        return benchmarks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=List[KPIAlert])
async def get_kpi_alerts(
    time_range: str = Query("24h", description="Time range for alerts"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    severity: Optional[str] = Query(None, description="Filter by severity: low, medium, high, critical"),
    status: Optional[str] = Query(None, description="Filter by status: active, resolved, acknowledged")
):
    """Get KPI alerts."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        alerts = await generate_kpi_alerts(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        # Filter alerts if specified
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        if status:
            alerts = [alert for alert in alerts if alert.status == status]
        
        return alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/goals", response_model=List[KPIGoal])
async def get_kpi_goals(
    time_range: str = Query("30d", description="Time range for goal tracking"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    goal_type: Optional[str] = Query(None, description="Filter by goal type: target, threshold")
):
    """Get KPI goals and progress tracking."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        goals = await generate_kpi_goals(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        # Filter by goal type if specified
        if goal_type:
            goals = [goal for goal in goals if goal.goal_type == goal_type]
        
        return goals
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report", response_model=KPIReport)
async def get_kpi_report(
    time_range: str = Query("30d", description="Time range for KPI report"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    report_format: str = Query("summary", description="Report format: summary, detailed, executive")
):
    """Get comprehensive KPI report."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        report = await generate_kpi_report(
            hybrid_service, start_time, end_time, selected_nodes, report_format
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison", response_model=KPIComparison)
async def get_kpi_comparison(
    current_period: str = Query("30d", description="Current period time range"),
    comparison_period: str = Query("30d", description="Comparison period time range"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    comparison_type: str = Query("period", description="Comparison type: period, benchmark, target")
):
    """Compare KPIs between periods or against benchmarks."""
    try:
        hybrid_service = await get_hybrid_data_service()
        
        # Parse current period
        current_start, current_end = _parse_time_range(current_period)
        
        # Parse comparison period (offset by period duration)
        period_duration = current_end - current_start
        comparison_start = current_start - period_duration
        comparison_end = current_start
        
        comparison = await compare_kpi_periods(
            hybrid_service=hybrid_service,
            current_start=current_start,
            current_end=current_end,
            comparison_start=comparison_start,
            comparison_end=comparison_end,
            selected_nodes=selected_nodes,
            comparison_type=comparison_type
        )
        
        return comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configuration", response_model=KPIConfiguration)
async def get_kpi_configuration():
    """Get KPI configuration and settings."""
    try:
        configuration = get_kpi_configuration()
        return configuration
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/configuration")
async def update_kpi_configuration(configuration: KPIConfiguration):
    """Update KPI configuration and settings."""
    try:
        # In real implementation, this would update the configuration in database
        return {
            "status": "success",
            "message": "KPI configuration updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=KPIHealth)
async def get_kpi_health():
    """Get KPI system health status."""
    try:
        health = get_kpi_health()
        return health
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/{metric_id}", response_model=KPIMetric)
async def get_specific_kpi_metric(
    metric_id: str,
    time_range: str = Query("24h", description="Time range for metric calculation"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get a specific KPI metric by ID."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        # This would typically fetch the specific metric from the KPI service
        # For now, return a mock metric
        metric = KPIMetric(
            metric_id=metric_id,
            metric_name="Mock Metric",
            category="system",
            current_value=85.5,
            target_value=90.0,
            unit="%",
            performance_percentage=95.0,
            trend="stable",
            status="good",
            last_updated=datetime.now().isoformat()
        )
        
        return metric
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metrics/{metric_id}/threshold")
async def set_kpi_threshold(
    metric_id: str,
    threshold_value: float,
    threshold_type: str = Query("warning", description="Threshold type: warning, critical, target")
):
    """Set threshold for a specific KPI metric."""
    try:
        # In real implementation, this would update the threshold in database
        return {
            "metric_id": metric_id,
            "threshold_value": threshold_value,
            "threshold_type": threshold_type,
            "status": "success",
            "message": "Threshold set successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_kpi_alert(alert_id: str):
    """Acknowledge a KPI alert."""
    try:
        # In real implementation, this would update the alert status in database
        return {
            "alert_id": alert_id,
            "status": "acknowledged",
            "acknowledged_at": datetime.now().isoformat(),
            "message": "Alert acknowledged successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/real-time")
async def get_real_time_kpis(
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    refresh_interval: int = Query(30, description="Refresh interval in seconds")
):
    """Get real-time KPI updates."""
    try:
        # In real implementation, this would establish a WebSocket connection
        # or use server-sent events for real-time updates
        return {
            "status": "real_time_kpis_available",
            "websocket_url": "/ws/kpis",
            "refresh_interval": refresh_interval,
            "message": "Use WebSocket endpoint for real-time updates"
        }
        
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