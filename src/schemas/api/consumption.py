"""
Pydantic models for Consumption Patterns API responses.

These models define the structure of JSON responses returned by the consumption
endpoints, providing type validation and automatic API documentation.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ConsumptionMetrics(BaseModel):
    """Consumption metrics for a time period."""
    
    total_consumption_m3: float = Field(..., description="Total consumption in m³")
    avg_consumption_rate: float = Field(..., description="Average consumption rate in L/s")
    peak_consumption_rate: float = Field(..., description="Peak consumption rate in L/s")
    peak_hour: str = Field(..., description="Hour with peak consumption")
    min_consumption_rate: float = Field(..., description="Minimum consumption rate in L/s")
    min_hour: str = Field(..., description="Hour with minimum consumption")
    consumption_variability: float = Field(..., description="Consumption variability coefficient")
    night_consumption_avg: float = Field(..., description="Average night consumption in L/s")
    day_consumption_avg: float = Field(..., description="Average day consumption in L/s")


class HourlyPattern(BaseModel):
    """Hourly consumption pattern data."""
    
    hour: int = Field(..., description="Hour of day (0-23)")
    avg_consumption: float = Field(..., description="Average consumption for this hour in L/s")
    peak_consumption: float = Field(..., description="Peak consumption for this hour in L/s")
    min_consumption: float = Field(..., description="Minimum consumption for this hour in L/s")
    consumption_factor: float = Field(..., description="Consumption factor relative to daily average")
    data_points: int = Field(..., description="Number of data points used")


class DailyTrend(BaseModel):
    """Daily consumption trend data."""
    
    date: str = Field(..., description="Date in ISO format")
    total_consumption: float = Field(..., description="Total consumption for the day in m³")
    avg_consumption: float = Field(..., description="Average consumption rate for the day in L/s")
    peak_consumption: float = Field(..., description="Peak consumption rate for the day in L/s")
    night_consumption: float = Field(..., description="Night consumption average in L/s")
    day_consumption: float = Field(..., description="Day consumption average in L/s")
    consumption_efficiency: float = Field(..., description="Consumption efficiency score")


class NodeConsumption(BaseModel):
    """Individual node consumption data."""
    
    node_id: str = Field(..., description="Unique node identifier")
    node_name: str = Field(..., description="Human-readable node name")
    total_consumption: float = Field(..., description="Total consumption in m³")
    avg_consumption_rate: float = Field(..., description="Average consumption rate in L/s")
    peak_consumption_rate: float = Field(..., description="Peak consumption rate in L/s")
    consumption_percentage: float = Field(..., description="Percentage of total network consumption")
    efficiency_score: float = Field(..., description="Node efficiency score")
    uptime_percentage: float = Field(..., description="Node uptime percentage")
    data_quality_score: float = Field(..., description="Data quality score (0-1)")


class ConsumptionHeatmapData(BaseModel):
    """Consumption heatmap data point."""
    
    hour: int = Field(..., description="Hour of day (0-23)")
    day_of_week: int = Field(..., description="Day of week (0=Monday, 6=Sunday)")
    consumption_intensity: float = Field(..., description="Consumption intensity (0-1 normalized)")
    actual_consumption: float = Field(..., description="Actual consumption in L/s")
    data_points: int = Field(..., description="Number of data points")


class ConsumptionInsights(BaseModel):
    """Consumption pattern insights."""
    
    insight_type: str = Field(..., description="Type of insight (e.g., 'peak_pattern', 'efficiency')")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed insight description")
    priority: str = Field(..., description="Priority level (high/medium/low)")
    recommended_action: Optional[str] = Field(None, description="Recommended action")
    impact_score: float = Field(..., description="Impact score (0-100)")


class ConsumptionResponse(BaseModel):
    """Complete consumption patterns response."""
    
    time_range: str = Field(..., description="Time range analyzed")
    period_start: str = Field(..., description="Start of analysis period")
    period_end: str = Field(..., description="End of analysis period")
    metrics: ConsumptionMetrics = Field(..., description="Consumption metrics")
    hourly_patterns: List[HourlyPattern] = Field(..., description="Hourly consumption patterns")
    daily_trends: List[DailyTrend] = Field(..., description="Daily consumption trends")
    node_consumption: List[NodeConsumption] = Field(..., description="Per-node consumption data")
    heatmap_data: List[ConsumptionHeatmapData] = Field(..., description="Consumption heatmap data")
    insights: List[ConsumptionInsights] = Field(..., description="Consumption insights")
    generated_at: str = Field(..., description="Response generation timestamp")


class ConsumptionComparison(BaseModel):
    """Consumption comparison between periods."""
    
    current_period: ConsumptionMetrics = Field(..., description="Current period metrics")
    previous_period: ConsumptionMetrics = Field(..., description="Previous period metrics")
    percentage_change: float = Field(..., description="Percentage change from previous period")
    trend_direction: str = Field(..., description="Trend direction (increasing/decreasing/stable)")
    significant_changes: List[str] = Field(..., description="List of significant changes")


class ConsumptionForecast(BaseModel):
    """Consumption forecast data."""
    
    forecast_hour: int = Field(..., description="Hour being forecasted (0-23)")
    predicted_consumption: float = Field(..., description="Predicted consumption in L/s")
    confidence_interval_lower: float = Field(..., description="Lower confidence interval")
    confidence_interval_upper: float = Field(..., description="Upper confidence interval")
    confidence_score: float = Field(..., description="Confidence score (0-1)")
    factors: List[str] = Field(..., description="Factors influencing the forecast")


class ConsumptionAnomalyDetection(BaseModel):
    """Consumption anomaly detection result."""
    
    timestamp: str = Field(..., description="Timestamp of anomaly")
    node_id: str = Field(..., description="Node where anomaly was detected")
    anomaly_type: str = Field(..., description="Type of anomaly")
    severity: str = Field(..., description="Severity level (low/medium/high)")
    expected_consumption: float = Field(..., description="Expected consumption in L/s")
    actual_consumption: float = Field(..., description="Actual consumption in L/s")
    deviation_percentage: float = Field(..., description="Deviation percentage")
    description: str = Field(..., description="Anomaly description")
    
    
class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details") 