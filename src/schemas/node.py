
from pydantic import BaseModel
from typing import Optional, Dict, Any

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class Location(BaseModel):
    site_name: str
    area: str
    coordinates: Coordinates

class Node(BaseModel):
    id: str
    name: str
    location: Location
    node_type: str
    status: str
    description: Optional[str] = None
