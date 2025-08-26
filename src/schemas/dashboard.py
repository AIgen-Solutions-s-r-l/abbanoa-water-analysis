
from pydantic import BaseModel
from typing import List, Optional

class EnergyConsumption(BaseModel):
    current_power_kw: float
    daily_consumption_kwh: float
    monthly_consumption_kwh: float
    daily_cost_eur: float
    monthly_cost_eur: float
    pump_efficiency_percent: float
    cost_per_cubic_meter: float

class KPIs(BaseModel):
    total_flow: float
    average_pressure: float
    system_efficiency: float
    active_alerts: int
    water_quality_index: float
    energy_consumption: EnergyConsumption

class NodeSummary(BaseModel):
    id: str
    name: str
    flow_rate: float
    pressure: float
    reservoir_level: float
    power_consumption_kw: float
    last_update: Optional[str] = None

class EnergyAnalysis(BaseModel):
    node_id: str
    node_name: str
    flow_rate: float
    pressure: float
    power_kw: float
    energy_cost_per_hour: float

class DashboardSummary(BaseModel):
    kpis: KPIs
    nodes: List[NodeSummary]
    energy_analysis: List[EnergyAnalysis]
