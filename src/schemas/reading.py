
from pydantic import BaseModel
from typing import Optional

class Reading(BaseModel):
    timestamp: str
    flow_rate: Optional[float] = None
    pressure: Optional[float] = None
    temperature: Optional[float] = None
