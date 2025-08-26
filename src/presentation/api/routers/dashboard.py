
from fastapi import APIRouter, Depends, HTTPException
from src.application.services.dashboard_service import DashboardService
from src.presentation.api.dependencies import get_dashboard_service
from src.schemas.dashboard import DashboardSummary

router = APIRouter()

@router.get("/dashboard/summary", response_model=DashboardSummary)
async def get_dashboard_summary(dashboard_service: DashboardService = Depends(get_dashboard_service)):
    try:
        return await dashboard_service.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
