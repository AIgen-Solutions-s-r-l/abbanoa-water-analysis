"""API endpoints for anomaly prediction system"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np

from src.application.services.anomaly_predictor import (
    AnomalyPredictor,
    AnomalyPrediction,
    AnomalyAlert
)


router = APIRouter(
    prefix="/predictions",
    tags=["Anomaly Predictions"],
    responses={404: {"description": "Not found"}},
)

# Initialize predictor (in production, this would be a singleton)
predictor = AnomalyPredictor()


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


@router.post("/predict", response_model=PredictionResponse)
async def predict_anomaly(request: PredictionRequest) -> PredictionResponse:
    """Predict anomaly for a single node
    
    Args:
        request: Prediction request with node ID and sensor data
        
    Returns:
        Prediction with probability, timing, and risk factors
    """
    try:
        # Convert sensor readings to DataFrame
        data_dict = {
            'timestamp': [r.timestamp for r in request.sensor_data],
            'pressure': [r.pressure for r in request.sensor_data],
            'flow_rate': [r.flow_rate for r in request.sensor_data]
        }
        sensor_df = pd.DataFrame(data_dict)
        
        # Get prediction
        prediction = predictor.predict(request.node_id, sensor_df)
        
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
async def predict_batch(request: BatchPredictionRequest) -> List[PredictionResponse]:
    """Predict anomalies for multiple nodes
    
    Args:
        request: Batch prediction request
        
    Returns:
        List of predictions for all nodes
    """
    try:
        # Prepare data for batch prediction
        nodes_data = {}
        for node_req in request.nodes:
            data_dict = {
                'timestamp': [r.timestamp for r in node_req.sensor_data],
                'pressure': [r.pressure for r in node_req.sensor_data],
                'flow_rate': [r.flow_rate for r in node_req.sensor_data]
            }
            nodes_data[node_req.node_id] = pd.DataFrame(data_dict)
        
        # Get batch predictions
        predictions = predictor.predict_batch(nodes_data)
        
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
    # In production, this would query real sensor data
    # For demo, we'll generate synthetic data
    demo_nodes = ['NODE_001', 'NODE_002', 'NODE_003', 'NODE_004', 'NODE_005']
    high_risk_predictions = []
    
    for node_id in demo_nodes:
        # Generate synthetic sensor data
        timestamps = pd.date_range(end=datetime.now(), periods=24, freq='H')
        sensor_df = pd.DataFrame({
            'timestamp': timestamps,
            'pressure': np.random.normal(5.0, 0.5, 24),
            'flow_rate': np.random.normal(100, 10, 24)
        })
        
        # Add some anomalous patterns randomly
        if np.random.random() > 0.7:
            sensor_df.loc[20:, 'pressure'] *= 1.3  # Pressure spike
        
        prediction = predictor.predict(node_id, sensor_df)
        
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
async def train_model(request: TrainingRequest) -> Dict:
    """Train or update the prediction model
    
    Args:
        request: Training configuration
        
    Returns:
        Training status and metrics
    """
    try:
        # In production, this would fetch real historical data
        # For demo, generate synthetic training data
        days = request.historical_days
        timestamps = pd.date_range(end=datetime.now(), periods=days*24, freq='H')
        
        training_data = pd.DataFrame({
            'timestamp': timestamps,
            'node_id': 'TRAINING_NODE',
            'pressure': np.random.normal(5.0, 0.5, len(timestamps)),
            'flow_rate': np.random.normal(100, 10, len(timestamps)),
            'anomaly_occurred': np.random.choice([False, True], 
                                                size=len(timestamps), 
                                                p=[0.95, 0.05])
        })
        
        # Train the model
        predictor.train(training_data)
        
        # Evaluate performance
        metrics = predictor.evaluate(training_data)
        
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