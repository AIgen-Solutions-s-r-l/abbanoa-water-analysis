
from typing import Optional
from src.infrastructure.repositories.pressure_repository import PressureRepository
from src.schemas.pressure import PressureZoneResponse

class PressureService:
    def __init__(self, pressure_repository: PressureRepository):
        self.pressure_repository = pressure_repository

    async def get_pressure_zones(self, start_time: Optional[str], end_time: Optional[str]) -> PressureZoneResponse:
        return await self.pressure_repository.get_pressure_zones(start_time, end_time)
