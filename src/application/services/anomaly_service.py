
from typing import List
from src.infrastructure.repositories.anomaly_repository import AnomalyRepository
from src.schemas.anomaly import Anomaly

class AnomalyService:
    def __init__(self, anomaly_repository: AnomalyRepository):
        self.anomaly_repository = anomaly_repository

    async def get_anomalies(self) -> List[Anomaly]:
        return await self.anomaly_repository.get_anomalies()
