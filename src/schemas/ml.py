
from pydantic import BaseModel
from typing import List, Dict, Any

class TrainAnomalyDetectorResponse(BaseModel):
    status: str
    message: str
    node_id: str
    training_period: str
    model_id: str

class Anomaly(BaseModel):
    timestamp: str
    anomaly_score: float
    types: List[str]
    metrics: Dict[str, float]
    severity: str

class AnomalySummary(BaseModel):
    total_readings: int
    anomalies_detected: int
    anomaly_rate: float
    time_range: Dict[str, str]

class AnomalyRecommendation(BaseModel):
    type: str
    severity: str
    action: str
    confidence: float

class DetectAnomaliesResponse(BaseModel):
    status: str
    summary: AnomalySummary
    anomalies: List[Anomaly]
    recommendations: List[AnomalyRecommendation]

class DemandPrediction(BaseModel):
    timestamp: str
    predicted_flow: float
    confidence: float
    hour_of_day: int
    is_weekend: bool

class DemandInsight(BaseModel):
    peak_hours: List[int]
    avg_daily_consumption: float
    weekend_reduction: str

class PredictDemandResponse(BaseModel):
    status: str
    district_id: str
    predictions: List[DemandPrediction]
    insights: DemandInsight

class AccuracyMetrics(BaseModel):
    anomaly_detection: float
    demand_forecast: float
    predictive_maintenance: float

class PredictionsAvailable(BaseModel):
    anomaly_detection: bool
    demand_forecast: bool
    predictive_maintenance: bool
    water_quality: bool

class MLDashboard(BaseModel):
    models_active: int
    anomalies_last_24h: int
    accuracy_metrics: AccuracyMetrics
    last_training: str
    predictions_available: PredictionsAvailable

class MLDashboardSummary(BaseModel):
    status: str
    summary: MLDashboard
