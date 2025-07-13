"""
Pydantic models for Reports API responses.

These models define the structure of JSON responses returned by the reports
endpoints, providing type validation and automatic API documentation.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ReportMetadata(BaseModel):
    """Report metadata information."""
    
    report_id: str = Field(..., description="Unique report identifier")
    report_type: str = Field(..., description="Type of report")
    title: str = Field(..., description="Report title")
    description: str = Field(..., description="Report description")
    generated_at: str = Field(..., description="Report generation timestamp")
    generated_by: str = Field(..., description="Report generator (user/system)")
    version: str = Field(..., description="Report version")
    format: str = Field(..., description="Report format (JSON/PDF/HTML)")
    language: str = Field(..., description="Report language")
    
    
class ReportPeriod(BaseModel):
    """Report period information."""
    
    start_date: str = Field(..., description="Report period start date")
    end_date: str = Field(..., description="Report period end date")
    duration: str = Field(..., description="Report period duration")
    frequency: str = Field(..., description="Report frequency (daily/weekly/monthly)")
    timezone: str = Field(..., description="Report timezone")


class ExecutiveSummary(BaseModel):
    """Executive summary data."""
    
    key_metrics: Dict[str, Any] = Field(..., description="Key performance metrics")
    major_findings: List[str] = Field(..., description="Major findings")
    recommendations: List[str] = Field(..., description="Key recommendations")
    alerts: List[str] = Field(..., description="Critical alerts")
    overall_status: str = Field(..., description="Overall system status")
    performance_score: float = Field(..., description="Overall performance score")


class PerformanceMetrics(BaseModel):
    """Performance metrics section."""
    
    system_availability: float = Field(..., description="System availability percentage")
    data_quality_score: float = Field(..., description="Data quality score")
    efficiency_score: float = Field(..., description="Network efficiency score")
    response_time: float = Field(..., description="Average response time")
    throughput: float = Field(..., description="System throughput")
    error_rate: float = Field(..., description="Error rate percentage")


class NetworkAnalysis(BaseModel):
    """Network analysis section."""
    
    total_nodes: int = Field(..., description="Total number of nodes")
    active_nodes: int = Field(..., description="Number of active nodes")
    node_availability: float = Field(..., description="Node availability percentage")
    network_coverage: float = Field(..., description="Network coverage percentage")
    capacity_utilization: float = Field(..., description="Capacity utilization percentage")
    peak_load: float = Field(..., description="Peak load registered")


class QualityAssessment(BaseModel):
    """Quality assessment section."""
    
    overall_quality_grade: str = Field(..., description="Overall quality grade")
    water_quality_score: float = Field(..., description="Water quality score")
    temperature_compliance: float = Field(..., description="Temperature compliance percentage")
    pressure_stability: float = Field(..., description="Pressure stability score")
    flow_consistency: float = Field(..., description="Flow consistency score")
    contamination_incidents: int = Field(..., description="Number of contamination incidents")


class AnomalyReport(BaseModel):
    """Anomaly report section."""
    
    total_anomalies: int = Field(..., description="Total number of anomalies")
    critical_anomalies: int = Field(..., description="Number of critical anomalies")
    resolved_anomalies: int = Field(..., description="Number of resolved anomalies")
    false_positives: int = Field(..., description="Number of false positives")
    detection_accuracy: float = Field(..., description="Anomaly detection accuracy")
    mean_time_to_resolution: float = Field(..., description="Mean time to resolution in hours")


class ComplianceReport(BaseModel):
    """Compliance report section."""
    
    regulatory_compliance: float = Field(..., description="Regulatory compliance percentage")
    safety_compliance: float = Field(..., description="Safety compliance percentage")
    environmental_compliance: float = Field(..., description="Environmental compliance percentage")
    violations: List[str] = Field(..., description="List of violations")
    corrective_actions: List[str] = Field(..., description="Corrective actions taken")
    compliance_trend: str = Field(..., description="Compliance trend")


class FinancialImpact(BaseModel):
    """Financial impact section."""
    
    operational_costs: float = Field(..., description="Operational costs")
    maintenance_costs: float = Field(..., description="Maintenance costs")
    efficiency_savings: float = Field(..., description="Efficiency savings")
    downtime_costs: float = Field(..., description="Downtime costs")
    roi_metrics: Dict[str, float] = Field(..., description="ROI metrics")
    cost_per_unit: float = Field(..., description="Cost per unit")


class MaintenanceReport(BaseModel):
    """Maintenance report section."""
    
    scheduled_maintenance: int = Field(..., description="Scheduled maintenance activities")
    emergency_repairs: int = Field(..., description="Emergency repairs")
    maintenance_efficiency: float = Field(..., description="Maintenance efficiency score")
    equipment_reliability: float = Field(..., description="Equipment reliability score")
    maintenance_costs: float = Field(..., description="Total maintenance costs")
    next_maintenance_schedule: List[str] = Field(..., description="Next maintenance schedule")


class TrendAnalysis(BaseModel):
    """Trend analysis section."""
    
    performance_trends: Dict[str, str] = Field(..., description="Performance trends")
    seasonal_patterns: List[str] = Field(..., description="Seasonal patterns")
    growth_metrics: Dict[str, float] = Field(..., description="Growth metrics")
    forecast_indicators: List[str] = Field(..., description="Forecast indicators")
    trend_confidence: float = Field(..., description="Trend confidence score")


class RecommendationAction(BaseModel):
    """Individual recommendation action."""
    
    action_id: str = Field(..., description="Action identifier")
    category: str = Field(..., description="Action category")
    title: str = Field(..., description="Action title")
    description: str = Field(..., description="Action description")
    priority: str = Field(..., description="Priority level")
    estimated_impact: str = Field(..., description="Estimated impact")
    implementation_cost: Optional[float] = Field(None, description="Implementation cost")
    timeline: str = Field(..., description="Implementation timeline")
    responsible_party: str = Field(..., description="Responsible party")


class ReportRecommendations(BaseModel):
    """Recommendations section."""
    
    immediate_actions: List[RecommendationAction] = Field(..., description="Immediate actions")
    short_term_actions: List[RecommendationAction] = Field(..., description="Short-term actions")
    long_term_actions: List[RecommendationAction] = Field(..., description="Long-term actions")
    preventive_measures: List[str] = Field(..., description="Preventive measures")
    optimization_opportunities: List[str] = Field(..., description="Optimization opportunities")


class ReportAppendix(BaseModel):
    """Report appendix data."""
    
    data_sources: List[str] = Field(..., description="Data sources used")
    methodology: str = Field(..., description="Analysis methodology")
    assumptions: List[str] = Field(..., description="Key assumptions")
    limitations: List[str] = Field(..., description="Analysis limitations")
    technical_details: Dict[str, Any] = Field(..., description="Technical details")
    references: List[str] = Field(..., description="References")


class ComprehensiveReport(BaseModel):
    """Complete comprehensive report."""
    
    metadata: ReportMetadata = Field(..., description="Report metadata")
    period: ReportPeriod = Field(..., description="Report period")
    executive_summary: ExecutiveSummary = Field(..., description="Executive summary")
    performance_metrics: PerformanceMetrics = Field(..., description="Performance metrics")
    network_analysis: NetworkAnalysis = Field(..., description="Network analysis")
    quality_assessment: QualityAssessment = Field(..., description="Quality assessment")
    anomaly_report: AnomalyReport = Field(..., description="Anomaly report")
    compliance_report: ComplianceReport = Field(..., description="Compliance report")
    financial_impact: FinancialImpact = Field(..., description="Financial impact")
    maintenance_report: MaintenanceReport = Field(..., description="Maintenance report")
    trend_analysis: TrendAnalysis = Field(..., description="Trend analysis")
    recommendations: ReportRecommendations = Field(..., description="Recommendations")
    appendix: ReportAppendix = Field(..., description="Report appendix")


class ReportTemplate(BaseModel):
    """Report template configuration."""
    
    template_id: str = Field(..., description="Template identifier")
    template_name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    report_type: str = Field(..., description="Report type")
    sections: List[str] = Field(..., description="Report sections")
    default_parameters: Dict[str, Any] = Field(..., description="Default parameters")
    customizable_fields: List[str] = Field(..., description="Customizable fields")


class ReportGeneration(BaseModel):
    """Report generation request."""
    
    template_id: str = Field(..., description="Template to use")
    report_type: str = Field(..., description="Type of report to generate")
    period_start: str = Field(..., description="Report period start")
    period_end: str = Field(..., description="Report period end")
    include_sections: List[str] = Field(..., description="Sections to include")
    parameters: Dict[str, Any] = Field(..., description="Report parameters")
    format: str = Field(..., description="Output format")
    delivery_method: str = Field(..., description="Delivery method")


class ReportSchedule(BaseModel):
    """Report schedule configuration."""
    
    schedule_id: str = Field(..., description="Schedule identifier")
    report_template: str = Field(..., description="Report template to use")
    frequency: str = Field(..., description="Schedule frequency")
    recipients: List[str] = Field(..., description="Report recipients")
    delivery_method: str = Field(..., description="Delivery method")
    next_run: str = Field(..., description="Next scheduled run")
    active: bool = Field(..., description="Whether schedule is active")


class ReportHistory(BaseModel):
    """Report history entry."""
    
    report_id: str = Field(..., description="Report identifier")
    generated_at: str = Field(..., description="Generation timestamp")
    report_type: str = Field(..., description="Report type")
    period_covered: str = Field(..., description="Period covered")
    file_size: int = Field(..., description="File size in bytes")
    status: str = Field(..., description="Generation status")
    download_url: Optional[str] = Field(None, description="Download URL")
    
    
class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details") 