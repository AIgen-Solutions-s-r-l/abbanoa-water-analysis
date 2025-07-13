"""
KPI Utilities Module.

This module contains common utility functions for KPI calculations and processing.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from statistics import mean, median, stdev

from src.schemas.api.kpis import (
    TrendDirection,
    AlertLevel,
    GoalStatus,
    KPIMetric,
    KPIAlert,
    KPIGoal,
    KPIBenchmark,
    BenchmarkType
)

logger = logging.getLogger(__name__)


def calculate_system_health(kpi_categories: List[Any]) -> float:
    """Calculate overall system health score."""
    scores = []
    for category in kpi_categories:
        if hasattr(category, 'performance_score'):
            scores.append(category.performance_score)
        elif hasattr(category, 'overall_efficiency_score'):
            scores.append(category.overall_efficiency_score)
        elif hasattr(category, 'quality_score'):
            scores.append(category.quality_score)
        elif hasattr(category, 'maintenance_efficiency_score'):
            scores.append(category.maintenance_efficiency_score)
        elif hasattr(category, 'operational_efficiency_score'):
            scores.append(category.operational_efficiency_score)
        elif hasattr(category, 'financial_efficiency_score'):
            scores.append(category.financial_efficiency_score)
        elif hasattr(category, 'compliance_efficiency_score'):
            scores.append(category.compliance_efficiency_score)
    
    return mean(scores) if scores else 0.0


def calculate_performance_score(
    uptime: float, response_time: float, throughput: float, error_rate: float
) -> float:
    """Calculate overall performance score."""
    # Weighted scoring algorithm
    uptime_score = uptime
    response_score = max(0, 100 - (response_time / 10))
    throughput_score = min(100, throughput / 10)
    error_score = max(0, 100 - (error_rate * 10))
    
    return (uptime_score * 0.3 + response_score * 0.2 + 
            throughput_score * 0.2 + error_score * 0.3)


def calculate_overall_efficiency_score(
    water_loss: float, pressure_eff: float, flow_eff: float,
    energy_eff: float, distribution_eff: float
) -> float:
    """Calculate overall efficiency score."""
    # Weighted scoring algorithm
    water_loss_score = max(0, 100 - water_loss)
    
    return (water_loss_score * 0.3 + pressure_eff * 0.2 + 
            flow_eff * 0.2 + energy_eff * 0.15 + distribution_eff * 0.15)


def calculate_quality_score(
    quality_compliance: float, contamination_incidents: int,
    temperature_compliance: float, pressure_compliance: float,
    flow_rate_compliance: float
) -> float:
    """Calculate overall quality score."""
    incident_penalty = contamination_incidents * 5
    base_score = (quality_compliance + temperature_compliance + 
                  pressure_compliance + flow_rate_compliance) / 4
    return max(0, base_score - incident_penalty)


def calculate_maintenance_efficiency_score(
    preventive_percentage: float,
    mean_time_to_repair: float,
    mean_time_between_failures: float,
    scheduled_completion: float,
    equipment_reliability: float
) -> float:
    """Calculate maintenance efficiency score."""
    # Weighted scoring algorithm
    preventive_score = preventive_percentage
    repair_score = max(0, 100 - (mean_time_to_repair / 24 * 100))
    reliability_score = equipment_reliability
    completion_score = scheduled_completion
    
    return (preventive_score * 0.3 + repair_score * 0.2 + 
            reliability_score * 0.3 + completion_score * 0.2)


def calculate_operational_efficiency_score(
    service_availability: float,
    customer_satisfaction: float,
    response_time: float,
    resource_utilization: float,
    process_efficiency: float,
    capacity_utilization: float
) -> float:
    """Calculate operational efficiency score."""
    # Weighted scoring algorithm
    availability_score = service_availability
    satisfaction_score = customer_satisfaction * 20  # Convert to 100 scale
    response_score = max(0, 100 - (response_time / 60 * 100))
    
    return (availability_score * 0.25 + satisfaction_score * 0.2 + 
            response_score * 0.15 + resource_utilization * 0.15 + 
            process_efficiency * 0.15 + capacity_utilization * 0.1)


def calculate_financial_efficiency_score(
    operational_cost: float,
    energy_cost: float,
    maintenance_cost_percentage: float,
    revenue: float,
    cost_savings: float,
    roi: float
) -> float:
    """Calculate financial efficiency score."""
    # Cost efficiency (lower is better)
    cost_efficiency = max(0, 100 - ((operational_cost + energy_cost) / 200 * 100))
    
    # Revenue efficiency
    revenue_efficiency = min(100, revenue / 100 * 100)
    
    # Savings and ROI
    savings_score = min(100, cost_savings * 10)
    roi_score = min(100, roi * 8)
    
    return (cost_efficiency * 0.3 + revenue_efficiency * 0.2 + 
            savings_score * 0.25 + roi_score * 0.25)


def calculate_compliance_efficiency_score(
    regulatory_compliance: float,
    safety_compliance: float,
    environmental_compliance: float,
    reporting_compliance: float,
    audit_score: float,
    violations_count: int
) -> float:
    """Calculate compliance efficiency score."""
    # Average compliance scores
    avg_compliance = (regulatory_compliance + safety_compliance + 
                     environmental_compliance + reporting_compliance) / 4
    
    # Violation penalty
    violation_penalty = violations_count * 10
    
    # Overall score
    base_score = (avg_compliance * 0.6 + audit_score * 0.4)
    
    return max(0, base_score - violation_penalty)


def generate_time_points(start_time: datetime, end_time: datetime, resolution: str) -> List[datetime]:
    """Generate time points based on resolution."""
    time_points = []
    current_time = start_time
    
    if resolution == "hourly":
        delta = timedelta(hours=1)
    elif resolution == "daily":
        delta = timedelta(days=1)
    elif resolution == "weekly":
        delta = timedelta(weeks=1)
    elif resolution == "monthly":
        delta = timedelta(days=30)
    else:
        delta = timedelta(days=1)
    
    while current_time <= end_time:
        time_points.append(current_time)
        current_time += delta
    
    return time_points


def calculate_trend_direction(trend_data: List[Dict[str, Any]]) -> TrendDirection:
    """Calculate trend direction from trend data."""
    if len(trend_data) < 2:
        return TrendDirection.stable
    
    first_value = trend_data[0]["value"]
    last_value = trend_data[-1]["value"]
    
    change_percentage = ((last_value - first_value) / first_value) * 100
    
    if change_percentage > 2:
        return TrendDirection.increasing
    elif change_percentage < -2:
        return TrendDirection.decreasing
    else:
        return TrendDirection.stable


def calculate_change_percentage(trend_data: List[Dict[str, Any]]) -> float:
    """Calculate percentage change from trend data."""
    if len(trend_data) < 2:
        return 0.0
    
    first_value = trend_data[0]["value"]
    last_value = trend_data[-1]["value"]
    
    return ((last_value - first_value) / first_value) * 100


def determine_health_status(health_score: float) -> str:
    """Determine health status based on score."""
    if health_score >= 90:
        return "excellent"
    elif health_score >= 80:
        return "good"
    elif health_score >= 70:
        return "fair"
    elif health_score >= 60:
        return "poor"
    else:
        return "critical"


def calculate_data_quality_score(dashboard) -> float:
    """Calculate data quality score."""
    # Mock calculation based on completeness and accuracy
    return 92.5


def calculate_component_health(dashboard) -> Dict[str, float]:
    """Calculate component health scores."""
    return {
        "system": dashboard.system_performance.performance_score,
        "network": dashboard.network_efficiency.overall_efficiency_score,
        "quality": dashboard.quality_metrics.quality_score,
        "maintenance": dashboard.maintenance_metrics.maintenance_efficiency_score,
        "operational": dashboard.operational_metrics.operational_efficiency_score,
        "financial": dashboard.financial_metrics.financial_efficiency_score,
        "compliance": dashboard.compliance_metrics.compliance_efficiency_score
    }


def calculate_kpi_improvements(dashboard1, dashboard2) -> List[str]:
    """Calculate KPI improvements between periods."""
    improvements = []
    
    # Compare system performance
    if dashboard2.system_performance.uptime_percentage > dashboard1.system_performance.uptime_percentage:
        improvements.append("System uptime improved")
    
    # Compare network efficiency
    if dashboard2.network_efficiency.water_loss_percentage < dashboard1.network_efficiency.water_loss_percentage:
        improvements.append("Water loss reduced")
    
    # Compare quality metrics
    if dashboard2.quality_metrics.quality_compliance_percentage > dashboard1.quality_metrics.quality_compliance_percentage:
        improvements.append("Quality compliance improved")
    
    return improvements


def calculate_kpi_regressions(dashboard1, dashboard2) -> List[str]:
    """Calculate KPI regressions between periods."""
    regressions = []
    
    # Compare system performance
    if dashboard2.system_performance.uptime_percentage < dashboard1.system_performance.uptime_percentage:
        regressions.append("System uptime declined")
    
    # Compare network efficiency
    if dashboard2.network_efficiency.water_loss_percentage > dashboard1.network_efficiency.water_loss_percentage:
        regressions.append("Water loss increased")
    
    # Compare quality metrics
    if dashboard2.quality_metrics.quality_compliance_percentage < dashboard1.quality_metrics.quality_compliance_percentage:
        regressions.append("Quality compliance declined")
    
    return regressions


def calculate_overall_change_percentage(dashboard1, dashboard2) -> float:
    """Calculate overall change percentage between periods."""
    return ((dashboard2.system_health - dashboard1.system_health) / dashboard1.system_health) * 100


def generate_period_comparison_insights(
    dashboard1, dashboard2, improvements: List[str], regressions: List[str]
) -> List[str]:
    """Generate insights from period comparison."""
    insights = []
    
    if len(improvements) > len(regressions):
        insights.append("Overall performance shows positive trend")
    elif len(regressions) > len(improvements):
        insights.append("Overall performance shows declining trend")
    else:
        insights.append("Overall performance remains stable")
    
    if improvements:
        insights.append(f"Key improvements: {', '.join(improvements)}")
    
    if regressions:
        insights.append(f"Areas needing attention: {', '.join(regressions)}")
    
    return insights


def generate_health_insights(dashboard, component_health: Dict[str, float]) -> List[str]:
    """Generate health insights."""
    insights = []
    
    # Find best and worst performing components
    best_component = max(component_health.items(), key=lambda x: x[1])
    worst_component = min(component_health.items(), key=lambda x: x[1])
    
    insights.append(f"Best performing area: {best_component[0]} ({best_component[1]:.1f})")
    insights.append(f"Area needing attention: {worst_component[0]} ({worst_component[1]:.1f})")
    
    # Overall health assessment
    if dashboard.system_health >= 90:
        insights.append("System is operating at optimal levels")
    elif dashboard.system_health >= 80:
        insights.append("System is performing well with minor optimization opportunities")
    elif dashboard.system_health >= 70:
        insights.append("System performance is acceptable but improvements needed")
    else:
        insights.append("System requires immediate attention and optimization")
    
    return insights


def create_kpi_alert(
    category: str,
    metric_name: str,
    message: str,
    severity: AlertLevel,
    threshold: float,
    current_value: float
) -> KPIAlert:
    """Create a KPI alert."""
    return KPIAlert(
        category=category,
        metric_name=metric_name,
        message=message,
        severity=severity,
        threshold=threshold,
        current_value=current_value,
        timestamp=datetime.now()
    )


def create_kpi_goal(
    category: str,
    metric_name: str,
    target_value: float,
    current_value: float,
    description: str,
    target_date: datetime
) -> KPIGoal:
    """Create a KPI goal."""
    progress_percentage = (current_value / target_value) * 100
    status = GoalStatus.on_track if progress_percentage >= 80 else GoalStatus.at_risk
    
    return KPIGoal(
        category=category,
        metric_name=metric_name,
        target_value=target_value,
        current_value=current_value,
        progress_percentage=progress_percentage,
        status=status,
        target_date=target_date,
        description=description
    )


def create_kpi_benchmark(
    category: str,
    metric_name: str,
    current_value: float,
    benchmark_value: float,
    benchmark_type: BenchmarkType
) -> KPIBenchmark:
    """Create a KPI benchmark."""
    difference_percentage = current_value - benchmark_value
    status = "above" if difference_percentage > 0 else "below"
    
    return KPIBenchmark(
        category=category,
        metric_name=metric_name,
        current_value=current_value,
        benchmark_value=benchmark_value,
        benchmark_type=benchmark_type,
        difference_percentage=difference_percentage,
        status=status
    ) 