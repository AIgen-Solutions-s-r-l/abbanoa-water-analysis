
from src.infrastructure.repositories.consumption_repository import ConsumptionRepository
from src.schemas.consumption import ConsumptionAnalytics, ConsumptionForecast, ConsumptionAnomaly
from typing import List, Optional

class ConsumptionService:
    def __init__(self, consumption_repository: ConsumptionRepository):
        self.consumption_repository = consumption_repository

    async def get_consumption_analytics(self) -> Optional[ConsumptionAnalytics]:
        return await self.consumption_repository.get_consumption_analytics()

    async def get_consumption_forecast(self, district_id: str) -> Optional[ConsumptionForecast]:
        return await self.consumption_repository.get_consumption_forecast(district_id)

    async def get_consumption_anomalies(self) -> List[ConsumptionAnomaly]:
        return await self.consumption_repository.get_consumption_anomalies()
