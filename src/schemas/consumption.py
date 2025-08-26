
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ConsumptionSummary(BaseModel):
    total_daily_consumption: int
    total_monthly_consumption: int
    total_users: int
    avg_consumption_per_user: float
    system_efficiency: float
    water_loss_percentage: int

class DistrictConsumption(BaseModel):
    district_id: str
    district_name: str
    total_users: int
    daily_consumption_liters: int
    monthly_consumption_liters: int
    avg_per_user_daily: float
    peak_hour: int
    efficiency_score: float

class ConsumptionTimeline(BaseModel):
    timestamp: str
    consumption_liters: int
    forecast_consumption: int

class UserSegment(BaseModel):
    segment: str
    user_count: int
    percentage: int
    avg_daily_consumption: int
    trend: str

class PeakDemand(BaseModel):
    daily_peak_time: str
    daily_peak_consumption: int
    weekly_peak_day: str
    monthly_peak_date: str
    seasonal_peak_month: str

class ConservationOpportunity(BaseModel):
    opportunity: str
    potential_savings_liters_daily: int
    potential_savings_percentage: int
    implementation_cost: str
    roi_months: int

class ConsumptionAnalytics(BaseModel):
    summary: ConsumptionSummary
    district_consumption: List[DistrictConsumption]
    consumption_timeline: List[ConsumptionTimeline]
    user_segments: List[UserSegment]
    peak_demand: PeakDemand
    conservation_opportunities: List[ConservationOpportunity]

class ForecastData(BaseModel):
    date: str
    forecast: int
    lower_bound: int
    upper_bound: int
    confidence: float
    components: Dict[str, Any]

class ForecastInsight(BaseModel):
    average_daily_forecast: int
    peak_day: str
    peak_consumption: int
    lowest_day: str
    lowest_consumption: int
    weekend_impact: int
    temperature_sensitivity: float

class ConsumptionForecast(BaseModel):
    district_id: str
    forecast_horizon_days: int
    forecast_method: str
    model_accuracy: float
    forecast_data: List[ForecastData]
    insights: ForecastInsight
    last_updated: str

class ConsumptionAnomaly(BaseModel):
    anomaly_id: str
    type: str
    severity: str
    district: str
    user_id: str
    detected_at: str
    consumption_spike: Optional[int] = None
    normal_range: Optional[str] = None
    actual_consumption: Optional[str] = None
    potential_cause: str
    days_zero_consumption: Optional[int] = None
    pattern_description: Optional[str] = None
