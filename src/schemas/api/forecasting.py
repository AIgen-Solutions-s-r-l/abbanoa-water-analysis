"""
Pydantic models for Advanced Forecasting API responses.

These models define the structure of JSON responses returned by the forecasting
endpoints, providing type validation and automatic API documentation.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ForecastPoint(BaseModel):
    """Individual forecast data point."""
    
    timestamp: str = Field(..., description="Forecast timestamp")
    predicted_value: float = Field(..., description="Predicted value")
    confidence_interval_lower: float = Field(..., description="Lower confidence interval")
    confidence_interval_upper: float = Field(..., description="Upper confidence interval")
    confidence_score: float = Field(..., description="Confidence score (0-1)")
    prediction_interval: float = Field(..., description="Prediction interval width")


class SeasonalPattern(BaseModel):
    """Seasonal pattern data."""
    
    pattern_type: str = Field(..., description="Type of pattern (daily/weekly/monthly)")
    amplitude: float = Field(..., description="Pattern amplitude")
    phase: float = Field(..., description="Pattern phase")
    strength: float = Field(..., description="Pattern strength (0-1)")
    significance: float = Field(..., description="Statistical significance")


class ForecastModel(BaseModel):
    """Forecast model information."""
    
    model_name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Model type (ARIMA/LSTM/Prophet/etc)")
    training_period: str = Field(..., description="Training period")
    accuracy_metrics: Dict[str, float] = Field(..., description="Model accuracy metrics")
    parameters: Dict[str, Any] = Field(..., description="Model parameters")
    last_updated: str = Field(..., description="Last model update timestamp")


class ForecastScenario(BaseModel):
    """Forecast scenario data."""
    
    scenario_name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    probability: float = Field(..., description="Scenario probability (0-1)")
    forecast_points: List[ForecastPoint] = Field(..., description="Forecast points for scenario")
    key_assumptions: List[str] = Field(..., description="Key assumptions for scenario")


class ForecastValidation(BaseModel):
    """Forecast validation metrics."""
    
    validation_period: str = Field(..., description="Validation period")
    mae: float = Field(..., description="Mean Absolute Error")
    mape: float = Field(..., description="Mean Absolute Percentage Error")
    rmse: float = Field(..., description="Root Mean Square Error")
    accuracy_score: float = Field(..., description="Overall accuracy score (0-100)")
    prediction_intervals_coverage: float = Field(..., description="Prediction intervals coverage percentage")


class AnomalyForecast(BaseModel):
    """Anomaly forecast data."""
    
    timestamp: str = Field(..., description="Forecast timestamp")
    anomaly_probability: float = Field(..., description="Anomaly probability (0-1)")
    anomaly_type: str = Field(..., description="Predicted anomaly type")
    severity_level: str = Field(..., description="Predicted severity level")
    confidence: float = Field(..., description="Confidence in anomaly prediction")
    contributing_factors: List[str] = Field(..., description="Contributing factors to anomaly")


class ForecastAlert(BaseModel):
    """Forecast-based alert."""
    
    alert_id: str = Field(..., description="Alert identifier")
    timestamp: str = Field(..., description="Alert timestamp")
    alert_type: str = Field(..., description="Type of forecast alert")
    severity: str = Field(..., description="Alert severity")
    description: str = Field(..., description="Alert description")
    predicted_value: float = Field(..., description="Predicted value triggering alert")
    threshold: float = Field(..., description="Threshold value")
    probability: float = Field(..., description="Probability of occurrence")
    recommended_action: str = Field(..., description="Recommended action")


class ForecastInfluencer(BaseModel):
    """Forecast influencing factor."""
    
    factor_name: str = Field(..., description="Factor name")
    factor_type: str = Field(..., description="Factor type (internal/external)")
    impact_score: float = Field(..., description="Impact score on forecast (-1 to 1)")
    confidence: float = Field(..., description="Confidence in factor impact")
    description: str = Field(..., description="Factor description")


class ForecastResponse(BaseModel):
    """Complete forecast response."""
    
    node_id: str = Field(..., description="Node identifier")
    node_name: str = Field(..., description="Node name")
    metric_type: str = Field(..., description="Metric being forecasted")
    forecast_horizon: str = Field(..., description="Forecast horizon")
    forecast_points: List[ForecastPoint] = Field(..., description="Forecast data points")
    seasonal_patterns: List[SeasonalPattern] = Field(..., description="Detected seasonal patterns")
    model_info: ForecastModel = Field(..., description="Model information")
    scenarios: List[ForecastScenario] = Field(..., description="Forecast scenarios")
    validation_metrics: ForecastValidation = Field(..., description="Validation metrics")
    anomaly_forecasts: List[AnomalyForecast] = Field(..., description="Anomaly forecasts")
    alerts: List[ForecastAlert] = Field(..., description="Forecast alerts")
    influencing_factors: List[ForecastInfluencer] = Field(..., description="Influencing factors")
    generated_at: str = Field(..., description="Response generation timestamp")


class NetworkForecast(BaseModel):
    """Network-wide forecast data."""
    
    metric_type: str = Field(..., description="Metric being forecasted")
    forecast_horizon: str = Field(..., description="Forecast horizon")
    network_forecast: List[ForecastPoint] = Field(..., description="Network-wide forecast")
    node_forecasts: List[ForecastResponse] = Field(..., description="Individual node forecasts")
    correlation_matrix: Dict[str, Dict[str, float]] = Field(..., description="Node correlation matrix")
    system_risks: List[str] = Field(..., description="System-wide risks")
    capacity_utilization: float = Field(..., description="Predicted capacity utilization")


class ForecastComparison(BaseModel):
    """Forecast comparison data."""
    
    metric_type: str = Field(..., description="Metric being compared")
    current_forecast: List[ForecastPoint] = Field(..., description="Current forecast")
    previous_forecast: List[ForecastPoint] = Field(..., description="Previous forecast")
    accuracy_improvement: float = Field(..., description="Accuracy improvement percentage")
    key_changes: List[str] = Field(..., description="Key changes in forecast")
    revision_reason: str = Field(..., description="Reason for forecast revision")


class ForecastPerformance(BaseModel):
    """Forecast performance metrics."""
    
    model_name: str = Field(..., description="Model name")
    evaluation_period: str = Field(..., description="Evaluation period")
    accuracy_metrics: Dict[str, float] = Field(..., description="Accuracy metrics")
    performance_trend: str = Field(..., description="Performance trend")
    benchmark_comparison: Dict[str, float] = Field(..., description="Benchmark comparison")
    recommendations: List[str] = Field(..., description="Performance improvement recommendations")


class ForecastCalibration(BaseModel):
    """Forecast calibration data."""
    
    calibration_date: str = Field(..., description="Calibration date")
    calibration_score: float = Field(..., description="Calibration score (0-1)")
    reliability_diagram: Dict[str, Any] = Field(..., description="Reliability diagram data")
    confidence_intervals_validity: float = Field(..., description="Confidence intervals validity")
    over_confidence_score: float = Field(..., description="Over-confidence score")
    under_confidence_score: float = Field(..., description="Under-confidence score")


class ForecastExplanation(BaseModel):
    """Forecast explanation and interpretability."""
    
    explanation_type: str = Field(..., description="Type of explanation")
    feature_importance: Dict[str, float] = Field(..., description="Feature importance scores")
    decision_rules: List[str] = Field(..., description="Decision rules")
    counterfactual_analysis: Dict[str, Any] = Field(..., description="Counterfactual analysis")
    sensitivity_analysis: Dict[str, float] = Field(..., description="Sensitivity analysis")
    
    
class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details") 