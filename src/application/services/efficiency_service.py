
from typing import List, Optional
from src.infrastructure.repositories.efficiency_repository import EfficiencyRepository
from src.schemas.efficiency import EfficiencyTrend

class EfficiencyService:
    def __init__(self, efficiency_repository: EfficiencyRepository):
        self.efficiency_repository = efficiency_repository

    async def get_efficiency_trends(self, start_time: Optional[str], end_time: Optional[str], aggregation: str) -> List[EfficiencyTrend]:
        return await self.efficiency_repository.get_efficiency_trends(start_time, end_time, aggregation)
