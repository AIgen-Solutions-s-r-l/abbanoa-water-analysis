
from pydantic import BaseModel
from typing import Optional, List

class Anomaly(BaseModel):
    id: str
    node_id: str
    node_name: str
    timestamp: Optional[str] = None
    anomaly_type: str
    severity: str
    measurement_type: Optional[str] = None
    actual_value: Optional[float] = None
    expected_range: Optional[List[float]] = None
    deviation_percentage: Optional[float] = None
    description: Optional[str] = None
    resolved_at: Optional[str] = None
