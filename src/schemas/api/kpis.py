"""
Pydantic models for KPIs API responses.

These models define the structure of JSON responses returned by the KPIs
endpoints, providing type validation and automatic API documentation.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class AlertLevel(str, Enum):
    """Alert severity levels."""
    
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ReportFormat(str, Enum):
    """Report format options."""
    
    json = "json"
    pdf = "pdf"
    excel = "excel"
    csv = "csv"
    html = "html"


class BenchmarkType(str, Enum):
    """Benchmark type values."""
    
    industry = "industry"
    internal = "internal"
    historical = "historical"
    target = "target"
    best_practice = "best_practice"


class GoalStatus(str, Enum):
    """Goal status values."""
    
    not_started = "not_started"
    in_progress = "in_progress"
    achieved = "achieved"
    failed = "failed"
    paused = "paused"


class TrendDirection(str, Enum):
    """Trend direction values."""
    
    increasing = "increasing"
    decreasing = "decreasing"
    stable = "stable"
    volatile = "volatile"


class KPIMetric(BaseModel):
    """Individual KPI metric."""
    
    metric_id: str = Field(..., description="Unique metric identifier")
    metric_name: str = Field(..., description="Metric name")
    category: str = Field(..., description="KPI category")
    current_value: float = Field(..., description="Current metric value")
    target_value: Optional[float] = Field(None, description="Target value")
    unit: str = Field(..., description="Unit of measurement")
    performance_percentage: float = Field(..., description="Performance as percentage of target")
    trend: str = Field(..., description="Trend direction (up/down/stable)")
    status: str = Field(..., description="Status (good/warning/critical)")
    last_updated: str = Field(..., description="Last update timestamp")


class KPICard(BaseModel):
    """KPI card display data."""
    
    card_id: str = Field(..., description="Card identifier")
    title: str = Field(..., description="Card title")
    subtitle: str = Field(..., description="Card subtitle")
    primary_metric: KPIMetric = Field(..., description="Primary metric")
    secondary_metrics: List[KPIMetric] = Field(..., description="Secondary metrics")
    sparkline_data: List[float] = Field(..., description="Sparkline data points")
    alert_level: str = Field(..., description="Alert level (none/low/medium/high)")
    color_scheme: str = Field(..., description="Color scheme for display")


class SystemPerformanceKPIs(BaseModel):
    """System performance KPIs."""
    
    system_uptime: float = Field(..., description="System uptime percentage")
    response_time: float = Field(..., description="Average response time in ms")
    throughput: float = Field(..., description="System throughput")
    error_rate: float = Field(..., description="Error rate percentage")
    availability: float = Field(..., description="System availability percentage")
    reliability_score: float = Field(..., description="Reliability score")


class NetworkEfficiencyKPIs(BaseModel):
    """Network efficiency KPIs."""
    
    overall_efficiency: float = Field(..., description="Overall network efficiency percentage")
    flow_efficiency: float = Field(..., description="Flow efficiency percentage")
    pressure_efficiency: float = Field(..., description="Pressure efficiency percentage")
    energy_efficiency: float = Field(..., description="Energy efficiency percentage")
    water_loss_rate: float = Field(..., description="Water loss rate percentage")
    distribution_efficiency: float = Field(..., description="Distribution efficiency percentage")


class QualityKPIs(BaseModel):
    """Quality KPIs."""
    
    overall_quality_score: float = Field(..., description="Overall quality score")
    water_quality_index: float = Field(..., description="Water quality index")
    temperature_compliance: float = Field(..., description="Temperature compliance percentage")
    pressure_stability: float = Field(..., description="Pressure stability score")
    contamination_rate: float = Field(..., description="Contamination rate")
    quality_consistency: float = Field(..., description="Quality consistency score")


class MaintenanceKPIs(BaseModel):
    """Maintenance KPIs."""
    
    preventive_maintenance_rate: float = Field(..., description="Preventive maintenance rate percentage")
    mean_time_to_repair: float = Field(..., description="Mean time to repair in hours")
    equipment_reliability: float = Field(..., description="Equipment reliability score")
    maintenance_cost_efficiency: float = Field(..., description="Maintenance cost efficiency")
    scheduled_maintenance_compliance: float = Field(..., description="Scheduled maintenance compliance percentage")
    emergency_repair_rate: float = Field(..., description="Emergency repair rate percentage")


class OperationalKPIs(BaseModel):
    """Operational KPIs."""
    
    operational_efficiency: float = Field(..., description="Operational efficiency percentage")
    capacity_utilization: float = Field(..., description="Capacity utilization percentage")
    resource_utilization: float = Field(..., description="Resource utilization percentage")
    cost_per_unit: float = Field(..., description="Cost per unit")
    productivity_index: float = Field(..., description="Productivity index")
    service_level: float = Field(..., description="Service level percentage")


class FinancialKPIs(BaseModel):
    """Financial KPIs."""
    
    operational_costs: float = Field(..., description="Operational costs")
    maintenance_costs: float = Field(..., description="Maintenance costs")
    cost_efficiency: float = Field(..., description="Cost efficiency ratio")
    roi: float = Field(..., description="Return on investment percentage")
    cost_savings: float = Field(..., description="Cost savings achieved")
    budget_variance: float = Field(..., description="Budget variance percentage")


class ComplianceKPIs(BaseModel):
    """Compliance KPIs."""
    
    regulatory_compliance: float = Field(..., description="Regulatory compliance percentage")
    safety_compliance: float = Field(..., description="Safety compliance percentage")
    environmental_compliance: float = Field(..., description="Environmental compliance percentage")
    audit_score: float = Field(..., description="Audit score")
    violation_rate: float = Field(..., description="Violation rate percentage")
    corrective_action_completion: float = Field(..., description="Corrective action completion rate")


class KPITrend(BaseModel):
    """KPI trend data."""
    
    timestamp: str = Field(..., description="Timestamp")
    metric_values: Dict[str, float] = Field(..., description="Metric values at timestamp")
    performance_scores: Dict[str, float] = Field(..., description="Performance scores")
    trend_indicators: Dict[str, str] = Field(..., description="Trend indicators")


class KPIBenchmark(BaseModel):
    """KPI benchmark data."""
    
    benchmark_type: str = Field(..., description="Benchmark type (industry/historical/target)")
    benchmark_value: float = Field(..., description="Benchmark value")
    current_value: float = Field(..., description="Current value")
    performance_gap: float = Field(..., description="Performance gap")
    percentile_rank: float = Field(..., description="Percentile rank")
    comparison_period: str = Field(..., description="Comparison period")


class KPIAlert(BaseModel):
    """KPI alert data."""
    
    alert_id: str = Field(..., description="Alert identifier")
    metric_id: str = Field(..., description="Metric identifier")
    alert_type: str = Field(..., description="Alert type")
    severity: str = Field(..., description="Alert severity")
    threshold_value: float = Field(..., description="Threshold value")
    current_value: float = Field(..., description="Current value")
    message: str = Field(..., description="Alert message")
    timestamp: str = Field(..., description="Alert timestamp")
    status: str = Field(..., description="Alert status")


class KPIGoal(BaseModel):
    """KPI goal data."""
    
    goal_id: str = Field(..., description="Goal identifier")
    metric_id: str = Field(..., description="Metric identifier")
    goal_type: str = Field(..., description="Goal type (target/threshold)")
    target_value: float = Field(..., description="Target value")
    current_progress: float = Field(..., description="Current progress percentage")
    target_date: str = Field(..., description="Target achievement date")
    achievement_probability: float = Field(..., description="Achievement probability")
    required_improvement_rate: float = Field(..., description="Required improvement rate")


class KPIDashboard(BaseModel):
    """Complete KPI dashboard."""
    
    dashboard_id: str = Field(..., description="Dashboard identifier")
    title: str = Field(..., description="Dashboard title")
    last_updated: str = Field(..., description="Last update timestamp")
    system_performance: SystemPerformanceKPIs = Field(..., description="System performance KPIs")
    network_efficiency: NetworkEfficiencyKPIs = Field(..., description="Network efficiency KPIs")
    quality: QualityKPIs = Field(..., description="Quality KPIs")
    maintenance: MaintenanceKPIs = Field(..., description="Maintenance KPIs")
    operational: OperationalKPIs = Field(..., description="Operational KPIs")
    financial: FinancialKPIs = Field(..., description="Financial KPIs")
    compliance: ComplianceKPIs = Field(..., description="Compliance KPIs")
    kpi_cards: List[KPICard] = Field(..., description="KPI cards for display")
    active_alerts: List[KPIAlert] = Field(..., description="Active KPI alerts")
    top_performing_metrics: List[str] = Field(..., description="Top performing metrics")
    improvement_needed: List[str] = Field(..., description="Metrics needing improvement")


class KPIReport(BaseModel):
    """KPI report data."""
    
    report_id: str = Field(..., description="Report identifier")
    report_period: str = Field(..., description="Report period")
    generated_at: str = Field(..., description="Generation timestamp")
    executive_summary: str = Field(..., description="Executive summary")
    key_achievements: List[str] = Field(..., description="Key achievements")
    areas_for_improvement: List[str] = Field(..., description="Areas for improvement")
    kpi_performance: Dict[str, float] = Field(..., description="KPI performance summary")
    trend_analysis: Dict[str, str] = Field(..., description="Trend analysis")
    recommendations: List[str] = Field(..., description="Recommendations")


class KPIComparison(BaseModel):
    """KPI comparison data."""
    
    comparison_type: str = Field(..., description="Comparison type (period/benchmark)")
    current_kpis: KPIDashboard = Field(..., description="Current KPIs")
    comparison_kpis: KPIDashboard = Field(..., description="Comparison KPIs")
    improvement_metrics: List[str] = Field(..., description="Improved metrics")
    declining_metrics: List[str] = Field(..., description="Declining metrics")
    overall_performance_change: float = Field(..., description="Overall performance change percentage")


class KPIConfiguration(BaseModel):
    """KPI configuration data."""
    
    metric_definitions: List[Dict[str, Any]] = Field(..., description="Metric definitions")
    thresholds: Dict[str, Dict[str, float]] = Field(..., description="KPI thresholds")
    targets: Dict[str, float] = Field(..., description="KPI targets")
    refresh_intervals: Dict[str, int] = Field(..., description="Refresh intervals in seconds")
    alert_rules: List[Dict[str, Any]] = Field(..., description="Alert rules")
    dashboard_layout: Dict[str, Any] = Field(..., description="Dashboard layout configuration")


class KPIHealth(BaseModel):
    """KPI system health data."""
    
    data_freshness: Dict[str, str] = Field(..., description="Data freshness status")
    calculation_status: Dict[str, str] = Field(..., description="Calculation status")
    error_rates: Dict[str, float] = Field(..., description="Error rates by metric")
    performance_metrics: Dict[str, float] = Field(..., description="System performance metrics")
    last_successful_update: str = Field(..., description="Last successful update timestamp")
    
    
class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details") 