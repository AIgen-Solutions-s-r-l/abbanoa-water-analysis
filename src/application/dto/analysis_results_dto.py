"""Data Transfer Objects for analysis results."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID


@dataclass
class TimeSeriesAnalysisResultDTO:
    """DTO for time series analysis results."""

    node_id: UUID
    analysis_period_start: datetime
    analysis_period_end: datetime
    trend_component: List[float]
    seasonal_component: List[float]
    residual_component: List[float]
    anomalies_detected: int
    quality_score: float
    patterns_identified: List[str]


@dataclass
class NetworkEfficiencyResultDTO:
    """DTO for network efficiency calculation results."""

    network_id: UUID
    period_start: datetime
    period_end: datetime
    efficiency_percentage: float
    total_input_volume: float
    total_output_volume: float
    loss_volume: float
    loss_percentage: float
    node_contributions: Dict[str, Dict[str, float]]


@dataclass
class AnomalyDetectionResultDTO:
    """DTO for anomaly detection results."""

    node_id: UUID
    timestamp: datetime
    anomaly_type: str
    severity: str
    measurement_type: str
    actual_value: float
    expected_range: tuple[float, float]
    deviation_percentage: float
    description: str


@dataclass
class DataQualityReportDTO:
    """DTO for data quality report."""

    node_id: UUID
    report_date: datetime
    period_start: datetime
    period_end: datetime
    total_expected_readings: int
    actual_readings: int
    coverage_percentage: float
    missing_values_count: int
    anomaly_count: int
    quality_score: float
    issues: List[str]
    recommendations: List[str]


@dataclass
class ConsumptionPatternDTO:
    """DTO for water consumption patterns."""

    node_id: UUID
    pattern_type: str  # "hourly", "daily", "weekly", "monthly"
    average_consumption: Dict[str, float]  # e.g., {"00:00": 150.5, "01:00": 120.3}
    peak_hours: List[str]
    off_peak_hours: List[str]
    variability_coefficient: float
