
from src.infrastructure.repositories.ml_repository import MLRepository
from src.schemas.ml import TrainAnomalyDetectorResponse, DetectAnomaliesResponse, PredictDemandResponse, MLDashboardSummary

class MLService:
    def __init__(self, ml_repository: MLRepository):
        self.ml_repository = ml_repository

    async def train_anomaly_detector(self, node_id: str, days: int) -> TrainAnomalyDetectorResponse:
        return await self.ml_repository.train_anomaly_detector(node_id, days)

    async def detect_anomalies(self, node_id: str, hours: int) -> DetectAnomaliesResponse:
        return await self.ml_repository.detect_anomalies(node_id, hours)

    async def predict_demand(self, district_id: str, hours_ahead: int) -> PredictDemandResponse:
        return await self.ml_repository.predict_demand(district_id, hours_ahead)

    async def ml_dashboard_summary(self) -> MLDashboardSummary:
        return await self.ml_repository.ml_dashboard_summary()
