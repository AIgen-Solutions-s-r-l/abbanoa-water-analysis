"""API endpoints for anomaly prediction system"""

from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
import asyncpg
import logging

from src.application.services.anomaly_predictor import (
    AnomalyPredictor,
    AnomalyPrediction,
    AnomalyAlert
)
from src.infrastructure.repositories.anomaly_prediction_repository import (
    AnomalyPredictionRepository
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/predictions",
    tags=["Anomaly Predictions"],
    responses={404: {"description": "Not found"}},
)

# Predictor will be initialized with database connection
predictor: Optional[AnomalyPredictor] = None
repository: Optional[AnomalyPredictionRepository] = None


class SensorReading(BaseModel):
    """Single sensor reading"""
    timestamp: datetime
    pressure: float = Field(ge=0, le=10, description="Pressure in bar")
    flow_rate: float = Field(ge=0, description="Flow rate in L/s")


class PredictionRequest(BaseModel):
    """Request for anomaly prediction"""
    node_id: str = Field(..., description="Infrastructure node identifier")
    sensor_data: List[SensorReading] = Field(..., description="Recent sensor readings")
    lookback_hours: Optional[int] = Field(24, description="Hours of data to consider")


class PredictionResponse(BaseModel):
    """Anomaly prediction response"""
    node_id: str
    probability: float = Field(ge=0, le=1)
    predicted_time: datetime
    confidence: str
    risk_factors: List[str]
    alert: Optional[Dict] = None


class BatchPredictionRequest(BaseModel):
    """Request for batch predictions"""
    nodes: List[PredictionRequest]


class TrainingRequest(BaseModel):
    """Request to train/update model"""
    historical_days: int = Field(30, ge=7, le=365)
    node_filter: Optional[List[str]] = None


@router.on_event("startup")
async def startup_event():
    """Initialize predictor with database connection on startup"""
    global predictor, repository
    # This will be set by the main app
    pass


@router.post("/predict", response_model=PredictionResponse)
async def predict_anomaly(request: PredictionRequest, req: Request) -> PredictionResponse:
    """Predict anomaly for a single node
    
    Args:
        request: Prediction request with node ID and sensor data
        
    Returns:
        Prediction with probability, timing, and risk factors
    """
    try:
        # Get database pool from app state
        pool = req.app.state.pool if hasattr(req.app.state, 'pool') else None
        if not pool:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Initialize repository and predictor if needed
        global predictor, repository
        if not repository:
            repository = AnomalyPredictionRepository(pool)
        if not predictor:
            predictor = AnomalyPredictor(repository=repository)
        
        # Use real database data for prediction
        prediction = await predictor.predict_from_database(request.node_id)
        
        # Generate alert if high risk
        alert_dict = None
        if prediction.probability >= 0.7:
            alert = predictor.generate_alert(prediction)
            alert_dict = {
                'severity': alert.severity,
                'time_to_event_hours': alert.time_to_event_hours,
                'description': alert.description,
                'recommended_actions': alert.recommended_actions
            }
        
        return PredictionResponse(
            node_id=prediction.node_id,
            probability=prediction.probability,
            predicted_time=prediction.predicted_time,
            confidence=prediction.confidence,
            risk_factors=prediction.risk_factors,
            alert=alert_dict
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/predict/batch", response_model=List[PredictionResponse])
async def predict_batch(request: BatchPredictionRequest, req: Request) -> List[PredictionResponse]:
    """Predict anomalies for multiple nodes
    
    Args:
        request: Batch prediction request
        
    Returns:
        List of predictions for all nodes
    """
    try:
        # Get database pool
        pool = req.app.state.pool if hasattr(req.app.state, 'pool') else None
        if not pool:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Initialize if needed
        global predictor, repository
        if not repository:
            repository = AnomalyPredictionRepository(pool)
        if not predictor:
            predictor = AnomalyPredictor(repository=repository)
        
        # Get predictions for each node using real data
        predictions = []
        for node_req in request.nodes:
            pred = await predictor.predict_from_database(node_req.node_id)
            predictions.append(pred)
        
        # Convert to response format
        responses = []
        for pred in predictions:
            alert_dict = None
            if pred.probability >= 0.7:
                alert = predictor.generate_alert(pred)
                alert_dict = {
                    'severity': alert.severity,
                    'time_to_event_hours': alert.time_to_event_hours,
                    'description': alert.description,
                    'recommended_actions': alert.recommended_actions
                }
            
            responses.append(PredictionResponse(
                node_id=pred.node_id,
                probability=pred.probability,
                predicted_time=pred.predicted_time,
                confidence=pred.confidence,
                risk_factors=pred.risk_factors,
                alert=alert_dict
            ))
        
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@router.get("/high-risk", response_model=List[PredictionResponse])
async def get_high_risk_nodes(
    req: Request,
    threshold: float = Query(0.7, ge=0.5, le=1.0, description="Risk threshold"),
    hours_ahead: int = Query(6, ge=1, le=24, description="Prediction horizon")
) -> List[PredictionResponse]:
    """Get all nodes with high anomaly risk
    
    Args:
        threshold: Minimum probability threshold
        hours_ahead: How many hours ahead to predict
        
    Returns:
        List of high-risk predictions
    """
    # Get database pool
    pool = req.app.state.pool if hasattr(req.app.state, 'pool') else None
    if not pool:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    # Initialize if needed
    global predictor, repository
    if not repository:
        repository = AnomalyPredictionRepository(pool)
    if not predictor:
        predictor = AnomalyPredictor(repository=repository)
    
    # Get list of active nodes from database
    active_nodes = await repository.get_active_nodes()
    high_risk_predictions = []
    
    logger.info(f"Checking {len(active_nodes)} active nodes for high risk anomalies")
    
    for node_id in active_nodes:
        prediction = await predictor.predict_from_database(node_id)
        
        if prediction.probability >= threshold:
            alert = predictor.generate_alert(prediction)
            alert_dict = {
                'severity': alert.severity,
                'time_to_event_hours': alert.time_to_event_hours,
                'description': alert.description,
                'recommended_actions': alert.recommended_actions
            }
            
            high_risk_predictions.append(PredictionResponse(
                node_id=prediction.node_id,
                probability=prediction.probability,
                predicted_time=prediction.predicted_time,
                confidence=prediction.confidence,
                risk_factors=prediction.risk_factors,
                alert=alert_dict
            ))
    
    return high_risk_predictions


@router.post("/train")
async def train_model(request: TrainingRequest, req: Request) -> Dict:
    """Train or update the prediction model
    
    Args:
        request: Training configuration
        
    Returns:
        Training status and metrics
    """
    try:
        # Get database pool
        pool = req.app.state.pool if hasattr(req.app.state, 'pool') else None
        if not pool:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Initialize if needed
        global predictor, repository
        if not repository:
            repository = AnomalyPredictionRepository(pool)
        if not predictor:
            predictor = AnomalyPredictor(repository=repository)
        
        # Train model with real historical data from database
        await predictor.train_from_database(
            days_back=request.historical_days,
            node_id=request.node_filter[0] if request.node_filter else None
        )
        
        # Get training statistics
        training_stats = await repository.get_training_data(
            days_back=request.historical_days
        )
        
        metrics = {
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0
        }
        
        if not training_stats.sensor_data.empty:
            # Calculate basic metrics
            total_samples = len(training_stats.sensor_data)
            anomaly_samples = training_stats.sensor_data['has_anomaly'].sum() if 'has_anomaly' in training_stats.sensor_data else 0
            metrics['total_samples'] = total_samples
            metrics['anomaly_samples'] = int(anomaly_samples)
            metrics['anomaly_rate'] = float(anomaly_samples / total_samples) if total_samples > 0 else 0
        
        return {
            'status': 'success',
            'training_samples': len(training_data),
            'training_time': predictor.training_time.isoformat(),
            'metrics': metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.get("/model/status")
async def get_model_status() -> Dict:
    """Get current model status and configuration
    
    Returns:
        Model status, parameters, and last update time
    """
    return {
        'is_trained': predictor.is_trained,
        'training_time': predictor.training_time.isoformat() if predictor.training_time else None,
        'last_update': predictor.last_update_time.isoformat() if predictor.last_update_time else None,
        'data_points_processed': predictor.data_points_processed,
        'parameters': predictor.get_params()
    }