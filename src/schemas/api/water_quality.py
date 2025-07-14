"""
Pydantic models for Water Quality API responses.

These models define the structure of JSON responses returned by the water quality
endpoints, providing type validation and automatic API documentation.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class WaterQualityReading(BaseModel):
    """Water quality reading data."""
    
    sensor_id: str = Field(..., description="Sensor identifier")
    timestamp: str = Field(..., description="Timestamp in ISO format")
    ph_level: float = Field(..., description="pH level")
    temperature: float = Field(..., description="Temperature in °C")
    turbidity: float = Field(..., description="Turbidity in NTU")
    dissolved_oxygen: float = Field(..., description="Dissolved oxygen in mg/L")
    conductivity: float = Field(..., description="Conductivity in μS/cm")


class QualityAnalytics(BaseModel):
    """Quality analytics data."""
    
    overall_compliance_rate: float = Field(..., description="Overall compliance rate")
    parameter_averages: Dict[str, float] = Field(default_factory=dict, description="Parameter averages")
    trend_analysis: Dict[str, Any] = Field(default_factory=dict, description="Trend analysis")
    violations_count: int = Field(default=0, description="Number of violations")


class ComplianceReport(BaseModel):
    """Compliance report data."""
    
    compliance_percentage: float = Field(..., description="Compliance percentage")
    violations: List[str] = Field(default_factory=list, description="List of violations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    period: str = Field(..., description="Report period")


class ContaminationEvent(BaseModel):
    """Contamination event data."""
    
    event_id: str = Field(..., description="Event identifier")
    timestamp: str = Field(..., description="Event timestamp")
    contamination_type: str = Field(..., description="Type of contamination")
    severity: str = Field(..., description="Severity level")
    location: str = Field(..., description="Event location")
    description: str = Field(..., description="Event description")


class QualityTrendData(BaseModel):
    """Quality trend data."""
    
    parameter: str = Field(..., description="Parameter name")
    trend_direction: str = Field(..., description="Trend direction")
    change_rate: float = Field(..., description="Change rate")
    confidence: float = Field(..., description="Confidence level")


class SensorCalibration(BaseModel):
    """Sensor calibration data."""
    
    sensor_id: str = Field(..., description="Sensor identifier")
    calibration_date: str = Field(..., description="Calibration date")
    needs_calibration: bool = Field(..., description="Whether sensor needs calibration")
    calibration_status: str = Field(..., description="Calibration status")
    accuracy: float = Field(..., description="Sensor accuracy")


class WaterQualityMetrics(BaseModel):
    """Water quality metrics for a time period."""
    
    overall_quality_score: float = Field(..., description="Overall quality score (0-100)")
    temperature_compliance: float = Field(..., description="Temperature compliance percentage")
    flow_consistency: float = Field(..., description="Flow consistency score (0-100)")
    pressure_stability: float = Field(..., description="Pressure stability score (0-100)")
    quality_grade: str = Field(..., description="Quality grade (A-F)")
    contamination_alerts: int = Field(..., description="Number of contamination alerts")
    avg_temperature: float = Field(..., description="Average temperature in °C")
    avg_flow_velocity: float = Field(..., description="Average flow velocity in m/s")
    avg_pressure: float = Field(..., description="Average pressure in bar")


class TemperatureAnalysis(BaseModel):
    """Temperature analysis data."""
    
    timestamp: str = Field(..., description="Timestamp of measurement")
    node_id: str = Field(..., description="Node identifier")
    temperature: float = Field(..., description="Temperature in °C")
    is_within_normal_range: bool = Field(..., description="Whether temperature is within normal range")
    deviation_from_average: float = Field(..., description="Deviation from average temperature")
    trend: str = Field(..., description="Temperature trend (increasing/decreasing/stable)")


class FlowVelocityAnalysis(BaseModel):
    """Flow velocity analysis data."""
    
    node_id: str = Field(..., description="Node identifier")
    node_name: str = Field(..., description="Node name")
    avg_velocity: float = Field(..., description="Average velocity in m/s")
    max_velocity: float = Field(..., description="Maximum velocity in m/s")
    min_velocity: float = Field(..., description="Minimum velocity in m/s")
    velocity_classification: str = Field(..., description="Velocity classification (Low/Normal/High)")
    flow_efficiency: float = Field(..., description="Flow efficiency score (0-100)")
    turbulence_indicator: float = Field(..., description="Turbulence indicator (0-1)")


class PressureGradientAnalysis(BaseModel):
    """Pressure gradient analysis data."""
    
    node_id: str = Field(..., description="Node identifier")
    node_name: str = Field(..., description="Node name")
    avg_pressure: float = Field(..., description="Average pressure in bar")
    pressure_gradient: float = Field(..., description="Pressure gradient in bar/km")
    gradient_classification: str = Field(..., description="Gradient classification (Low/Normal/High)")
    stability_score: float = Field(..., description="Pressure stability score (0-100)")
    anomaly_detected: bool = Field(..., description="Whether pressure anomaly was detected")


class QualityAlert(BaseModel):
    """Quality alert data."""
    
    alert_id: str = Field(..., description="Unique alert identifier")
    timestamp: str = Field(..., description="Alert timestamp")
    node_id: str = Field(..., description="Node identifier")
    alert_type: str = Field(..., description="Type of alert (temperature/pressure/flow/contamination)")
    severity: str = Field(..., description="Alert severity (low/medium/high/critical)")
    description: str = Field(..., description="Alert description")
    current_value: float = Field(..., description="Current measured value")
    threshold_value: float = Field(..., description="Threshold value exceeded")
    recommended_action: str = Field(..., description="Recommended action")
    status: str = Field(..., description="Alert status (active/resolved)")


class ContaminationIndicator(BaseModel):
    """Contamination indicator data."""
    
    node_id: str = Field(..., description="Node identifier")
    indicator_type: str = Field(..., description="Type of contamination indicator")
    risk_level: str = Field(..., description="Risk level (low/medium/high)")
    probability: float = Field(..., description="Contamination probability (0-1)")
    contributing_factors: List[str] = Field(..., description="Contributing factors")
    detection_method: str = Field(..., description="Detection method used")
    confidence_score: float = Field(..., description="Confidence score (0-1)")


class QualityTrend(BaseModel):
    """Quality trend data."""
    
    timestamp: str = Field(..., description="Timestamp")
    overall_quality: float = Field(..., description="Overall quality score")
    temperature_score: float = Field(..., description="Temperature quality score")
    flow_score: float = Field(..., description="Flow quality score")
    pressure_score: float = Field(..., description="Pressure quality score")
    contamination_risk: float = Field(..., description="Contamination risk score")
    data_completeness: float = Field(..., description="Data completeness score")


class NodeQualityProfile(BaseModel):
    """Individual node quality profile."""
    
    node_id: str = Field(..., description="Node identifier")
    node_name: str = Field(..., description="Node name")
    node_type: str = Field(..., description="Node type")
    overall_score: float = Field(..., description="Overall quality score")
    temperature_profile: Dict[str, Any] = Field(..., description="Temperature profile data")
    flow_profile: Dict[str, Any] = Field(..., description="Flow profile data")
    pressure_profile: Dict[str, Any] = Field(..., description="Pressure profile data")
    quality_grade: str = Field(..., description="Quality grade")
    last_maintenance: Optional[str] = Field(None, description="Last maintenance timestamp")
    next_maintenance_due: Optional[str] = Field(None, description="Next maintenance due")


class QualityPrediction(BaseModel):
    """Quality prediction data."""
    
    timestamp: str = Field(..., description="Prediction timestamp")
    node_id: str = Field(..., description="Node identifier")
    predicted_quality: float = Field(..., description="Predicted quality score")
    confidence_interval_lower: float = Field(..., description="Lower confidence interval")
    confidence_interval_upper: float = Field(..., description="Upper confidence interval")
    risk_factors: List[str] = Field(..., description="Risk factors affecting quality")
    maintenance_recommendations: List[str] = Field(..., description="Maintenance recommendations")


class WaterQualityResponse(BaseModel):
    """Complete water quality response."""
    
    time_range: str = Field(..., description="Time range analyzed")
    period_start: str = Field(..., description="Start of analysis period")
    period_end: str = Field(..., description="End of analysis period")
    metrics: WaterQualityMetrics = Field(..., description="Quality metrics")
    temperature_analysis: List[TemperatureAnalysis] = Field(..., description="Temperature analysis")
    flow_velocity_analysis: List[FlowVelocityAnalysis] = Field(..., description="Flow velocity analysis")
    pressure_gradient_analysis: List[PressureGradientAnalysis] = Field(..., description="Pressure gradient analysis")
    quality_alerts: List[QualityAlert] = Field(..., description="Quality alerts")
    contamination_indicators: List[ContaminationIndicator] = Field(..., description="Contamination indicators")
    quality_trends: List[QualityTrend] = Field(..., description="Quality trends")
    node_profiles: List[NodeQualityProfile] = Field(..., description="Node quality profiles")
    predictions: List[QualityPrediction] = Field(..., description="Quality predictions")
    generated_at: str = Field(..., description="Response generation timestamp")


class QualityComparison(BaseModel):
    """Quality comparison between periods."""
    
    current_metrics: WaterQualityMetrics = Field(..., description="Current period metrics")
    previous_metrics: WaterQualityMetrics = Field(..., description="Previous period metrics")
    improvement_areas: List[str] = Field(..., description="Areas showing improvement")
    degradation_areas: List[str] = Field(..., description="Areas showing degradation")
    overall_trend: str = Field(..., description="Overall quality trend")
    recommendations: List[str] = Field(..., description="Recommendations for improvement")


class QualityReport(BaseModel):
    """Quality report data."""
    
    report_id: str = Field(..., description="Unique report identifier")
    report_type: str = Field(..., description="Type of report")
    generated_at: str = Field(..., description="Report generation timestamp")
    period_covered: str = Field(..., description="Period covered by report")
    executive_summary: str = Field(..., description="Executive summary")
    key_findings: List[str] = Field(..., description="Key findings")
    recommendations: List[str] = Field(..., description="Recommendations")
    quality_score: float = Field(..., description="Overall quality score")
    compliance_status: str = Field(..., description="Compliance status")
    
    
class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details") 