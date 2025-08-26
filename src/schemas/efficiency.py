
from pydantic import BaseModel

class EfficiencyTrend(BaseModel):
    timestamp: str
    energyEfficiency: float
    waterLoss: float
    pumpEfficiency: float
    operationalCost: float
