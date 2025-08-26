
from fastapi import APIRouter, Depends, HTTPException, Query
from src.application.services.ml_service import MLService
from src.presentation.api.dependencies import get_ml_service
from src.schemas.ml import TrainAnomalyDetectorResponse, DetectAnomaliesResponse, PredictDemandResponse, MLDashboardSummary

router = APIRouter()

@router.post("/ml/train-anomaly-detector", response_model=TrainAnomalyDetectorResponse)
async def train_anomaly_detector(
    node_id: str = Query(..., description="Node ID to train on"),
    days: int = Query(7, description="Days of historical data to use"),
    ml_service: MLService = Depends(get_ml_service)
):
    try:
        return await ml_service.train_anomaly_detector(node_id, days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ml/detect-anomalies", response_model=DetectAnomaliesResponse)
async def detect_anomalies(
    node_id: str = Query(..., description="Node ID to analyze"),
    hours: int = Query(24, description="Hours of data to analyze"),
    ml_service: MLService = Depends(get_ml_service)
):
    try:
        return await ml_service.detect_anomalies(node_id, hours)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ml/predict-demand", response_model=PredictDemandResponse)
async def predict_demand(
    district_id: str = Query(..., description="District ID"),
    hours_ahead: int = Query(24, description="Hours to predict ahead"),
    ml_service: MLService = Depends(get_ml_service)
):
    try:
        return await ml_service.predict_demand(district_id, hours_ahead)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ml/dashboard-summary", response_model=MLDashboardSummary)
async def ml_dashboard_summary(ml_service: MLService = Depends(get_ml_service)):
    try:
        return await ml_service.ml_dashboard_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
