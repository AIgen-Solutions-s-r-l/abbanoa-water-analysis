
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from src.application.services.efficiency_service import EfficiencyService
from src.presentation.api.dependencies import get_efficiency_service
from src.schemas.efficiency import EfficiencyTrend

router = APIRouter()

@router.get("/efficiency/trends", response_model=List[EfficiencyTrend])
async def get_efficiency_trends(
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    aggregation: str = Query("weekly", description="Aggregation level: daily, weekly, monthly"),
    efficiency_service: EfficiencyService = Depends(get_efficiency_service)
):
    try:
        return await efficiency_service.get_efficiency_trends(start_time, end_time, aggregation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
