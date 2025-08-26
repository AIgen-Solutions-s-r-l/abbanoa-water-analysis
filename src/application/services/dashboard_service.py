
from src.infrastructure.repositories.dashboard_repository import DashboardRepository
from src.schemas.dashboard import DashboardSummary

class DashboardService:
    def __init__(self, dashboard_repository: DashboardRepository):
        self.dashboard_repository = dashboard_repository

    async def get_summary(self) -> DashboardSummary:
        return await self.dashboard_repository.get_summary()
