
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.application.services.anomaly_service import AnomalyService
from src.presentation.api.dependencies import get_anomaly_service
from src.schemas.anomaly import Anomaly

router = APIRouter()

@router.get("/anomalies", response_model=List[Anomaly])
async def get_anomalies(anomaly_service: AnomalyService = Depends(get_anomaly_service)):
    try:
        return await anomaly_service.get_anomalies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
