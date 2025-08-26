
from fastapi import APIRouter, Depends, HTTPException, Response, status
from src.application.services.consumption_service import ConsumptionService
from src.schemas.consumption import ConsumptionAnalytics, ConsumptionForecast, ConsumptionAnomaly
from src.presentation.api.dependencies import get_consumption_service
from typing import List, Optional

router = APIRouter()

@router.get("/consumption/analytics", response_model=Optional[ConsumptionAnalytics])
async def get_consumption_analytics(
    response: Response,
    consumption_service: ConsumptionService = Depends(get_consumption_service)
):
    try:
        result = await consumption_service.get_consumption_analytics()
        if result is None:
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/consumption/forecast/{district_id}", response_model=Optional[ConsumptionForecast])
async def get_consumption_forecast(
    district_id: str,
    response: Response,
    consumption_service: ConsumptionService = Depends(get_consumption_service)
):
    try:
        result = await consumption_service.get_consumption_forecast(district_id)
        if result is None:
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/consumption/anomalies", response_model=List[ConsumptionAnomaly])
async def get_consumption_anomalies(consumption_service: ConsumptionService = Depends(get_consumption_service)):
    try:
        return await consumption_service.get_consumption_anomalies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
