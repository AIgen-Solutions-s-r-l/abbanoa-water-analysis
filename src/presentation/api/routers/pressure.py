
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from src.application.services.pressure_service import PressureService
from src.presentation.api.dependencies import get_pressure_service
from src.schemas.pressure import PressureZoneResponse

router = APIRouter()

@router.get("/pressure/zones", response_model=PressureZoneResponse)
async def get_pressure_zones(
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    pressure_service: PressureService = Depends(get_pressure_service)
):
    try:
        return await pressure_service.get_pressure_zones(start_time, end_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
