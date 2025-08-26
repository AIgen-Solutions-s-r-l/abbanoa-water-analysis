
from pydantic import BaseModel
from typing import List

class HourlyEnergy(BaseModel):
    hour: int
    flow_rate: float
    pressure: float
    power_kw: float
    energy_cost: float
    is_peak: bool
    rate_eur_kwh: float

class DailyStatistics(BaseModel):
    total_energy_kwh: float
    total_cost_eur: float
    peak_demand_kw: float
    average_power_kw: float
    peak_hours_cost: float
    off_peak_cost: float

class OptimizationOpportunity(BaseModel):
    type: str
    title: str
    description: str
    annual_savings_eur: float
    implementation: str
    investment_eur: int
    roi_months: int

class EnergyOptimization(BaseModel):
    current_energy_profile: List[HourlyEnergy]
    daily_statistics: DailyStatistics
    optimization_opportunities: List[OptimizationOpportunity]
    projected_annual_savings: float
