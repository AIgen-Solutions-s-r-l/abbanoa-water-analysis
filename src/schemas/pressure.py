
from pydantic import BaseModel
from typing import List

class PressureZone(BaseModel):
    zone: str
    zoneName: str
    minPressure: float
    avgPressure: float
    maxPressure: float
    nodeCount: int
    readingCount: int
    status: str

class TimeRange(BaseModel):
    start: str
    end: str

class PressureSummary(BaseModel):
    totalZones: int
    optimalZones: int
    warningZones: int
    criticalZones: int

class PressureZoneResponse(BaseModel):
    zones: List[PressureZone]
    timeRange: TimeRange
    summary: PressureSummary
