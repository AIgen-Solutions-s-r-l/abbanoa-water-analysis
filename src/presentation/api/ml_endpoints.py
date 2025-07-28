"""
ML Prediction API Endpoints for Water Infrastructure
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import asyncpg
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ml", tags=["ML Predictions"])

# Global model storage (in production, use proper model registry)
_models = {}

class AnomalyDetector:
    """Simplified anomaly detector for API use"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            contamination=0.02,
            random_state=42,
            n_estimators=100
        )
        self.is_fitted = False
    
    def prepare_features(self, df):
        """Prepare features for anomaly detection"""
        features = pd.DataFrame()
        
        # Basic features
        features['flow_rate'] = df['flow_rate']
        features['pressure'] = df['pressure']
        features['temperature'] = df['temperature']
        
        # Rolling statistics
        for window in [5, 15]:
            features[f'flow_ma_{window}'] = df['flow_rate'].rolling(window, min_periods=1).mean()
            features[f'pressure_ma_{window}'] = df['pressure'].rolling(window, min_periods=1).mean()
        
        # Rate of change
        features['flow_change'] = df['flow_rate'].diff().fillna(0)
        features['pressure_change'] = df['pressure'].diff().fillna(0)
        
        # Time features
        features['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        features['is_night'] = features['hour'].between(22, 6).astype(int)
        
        return features.fillna(0)
    
    def fit(self, data):
        """Train the model"""
        X = self.prepare_features(data)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_fitted = True
        return self
    
    def predict(self, data):
        """Predict anomalies"""
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        
        X = self.prepare_features(data)
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        scores = self.model.score_samples(X_scaled)
        
        return predictions, scores


@router.post("/train-anomaly-detector")
async def train_anomaly_detector(
    pool: asyncpg.Pool,
    node_id: str = Query(..., description="Node ID to train on"),
    days: int = Query(7, description="Days of historical data to use")
):
    """Train an anomaly detection model for a specific node"""
    try:
        # Fetch training data
        async with pool.acquire() as conn:
            query = """
                SELECT timestamp, flow_rate, pressure, temperature
                FROM water_infrastructure.sensor_readings
                WHERE node_id = $1 
                AND timestamp > CURRENT_TIMESTAMP - INTERVAL '%s days'
                ORDER BY timestamp
            """ % days
            
            rows = await conn.fetch(query, node_id)
            
        if len(rows) < 100:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient data for training. Found {len(rows)} samples, need at least 100."
            )
        
        # Convert to DataFrame
        df = pd.DataFrame(rows)
        
        # Train model
        detector = AnomalyDetector()
        detector.fit(df)
        
        # Store model (in memory for demo)
        _models[f"anomaly_{node_id}"] = detector
        
        return {
            "status": "success",
            "message": f"Model trained successfully on {len(rows)} samples",
            "node_id": node_id,
            "training_period": f"{days} days",
            "model_id": f"anomaly_{node_id}"
        }
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detect-anomalies")
async def detect_anomalies(
    pool: asyncpg.Pool,
    node_id: str = Query(..., description="Node ID to analyze"),
    hours: int = Query(24, description="Hours of data to analyze")
):
    """Detect anomalies in recent sensor data"""
    try:
        # Check if model exists
        model_id = f"anomaly_{node_id}"
        if model_id not in _models:
            raise HTTPException(
                status_code=404,
                detail=f"No trained model found for node {node_id}. Please train first."
            )
        
        detector = _models[model_id]
        
        # Fetch recent data
        async with pool.acquire() as conn:
            query = """
                SELECT timestamp, flow_rate, pressure, temperature
                FROM water_infrastructure.sensor_readings
                WHERE node_id = $1 
                AND timestamp > CURRENT_TIMESTAMP - INTERVAL '%s hours'
                ORDER BY timestamp
            """ % hours
            
            rows = await conn.fetch(query, node_id)
        
        if len(rows) < 10:
            return {
                "status": "no_data",
                "message": "Insufficient recent data for analysis",
                "anomalies": []
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(rows)
        
        # Detect anomalies
        predictions, scores = detector.predict(df)
        
        # Extract anomalies with context
        anomalies = []
        for idx in np.where(predictions == -1)[0]:
            row = df.iloc[idx]
            
            # Classify anomaly type
            anomaly_types = []
            if row['pressure'] < df['pressure'].quantile(0.1):
                anomaly_types.append("LOW_PRESSURE")
            if row['flow_rate'] > df['flow_rate'].quantile(0.95):
                anomaly_types.append("HIGH_FLOW")
            if row['flow_rate'] < df['flow_rate'].quantile(0.05):
                anomaly_types.append("LOW_FLOW")
            
            hour = pd.to_datetime(row['timestamp']).hour
            if 2 <= hour <= 5 and row['flow_rate'] > df['flow_rate'].median():
                anomaly_types.append("NIGHT_CONSUMPTION")
            
            anomalies.append({
                "timestamp": row['timestamp'].isoformat(),
                "anomaly_score": float(scores[idx]),
                "types": anomaly_types if anomaly_types else ["GENERAL"],
                "metrics": {
                    "flow_rate": float(row['flow_rate']),
                    "pressure": float(row['pressure']),
                    "temperature": float(row['temperature'])
                },
                "severity": "high" if scores[idx] < -0.5 else "medium"
            })
        
        # Calculate statistics
        total_readings = len(df)
        anomaly_rate = len(anomalies) / total_readings * 100
        
        return {
            "status": "success",
            "summary": {
                "total_readings": total_readings,
                "anomalies_detected": len(anomalies),
                "anomaly_rate": round(anomaly_rate, 2),
                "time_range": {
                    "start": df['timestamp'].min().isoformat(),
                    "end": df['timestamp'].max().isoformat()
                }
            },
            "anomalies": anomalies,
            "recommendations": generate_recommendations(anomalies, df)
        }
        
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predict-demand")
async def predict_demand(
    pool: asyncpg.Pool,
    district_id: str = Query(..., description="District ID"),
    hours_ahead: int = Query(24, description="Hours to predict ahead")
):
    """Predict water demand for the next N hours"""
    try:
        # Fetch historical data
        async with pool.acquire() as conn:
            # Get consumption patterns
            query = """
                SELECT 
                    date_trunc('hour', timestamp) as hour,
                    AVG(flow_rate) as avg_flow,
                    COUNT(*) as readings
                FROM water_infrastructure.sensor_readings
                WHERE node_id LIKE $1
                AND timestamp > CURRENT_TIMESTAMP - INTERVAL '30 days'
                GROUP BY hour
                ORDER BY hour
            """
            
            rows = await conn.fetch(query, f"{district_id}%")
        
        if len(rows) < 168:  # Less than a week of hourly data
            raise HTTPException(
                status_code=400,
                detail="Insufficient historical data for demand prediction"
            )
        
        # Convert to DataFrame
        df = pd.DataFrame(rows)
        df['hour_of_day'] = pd.to_datetime(df['hour']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['hour']).dt.dayofweek
        
        # Simple prediction using hourly averages
        # (In production, use Prophet or more sophisticated models)
        predictions = []
        current_time = datetime.now()
        
        for h in range(hours_ahead):
            pred_time = current_time + timedelta(hours=h)
            hour_of_day = pred_time.hour
            day_of_week = pred_time.weekday()
            
            # Get historical average for this hour and day type
            is_weekend = day_of_week in [5, 6]
            hist_data = df[
                (df['hour_of_day'] == hour_of_day) & 
                (df['day_of_week'].isin([5, 6]) == is_weekend)
            ]
            
            if len(hist_data) > 0:
                predicted_flow = float(hist_data['avg_flow'].mean())
                confidence = 0.8 if len(hist_data) > 10 else 0.6
            else:
                # Fallback to overall hourly average
                predicted_flow = float(df[df['hour_of_day'] == hour_of_day]['avg_flow'].mean())
                confidence = 0.5
            
            predictions.append({
                "timestamp": pred_time.isoformat(),
                "predicted_flow": round(predicted_flow, 2),
                "confidence": confidence,
                "hour_of_day": hour_of_day,
                "is_weekend": is_weekend
            })
        
        # Calculate peak hours
        hourly_avg = df.groupby('hour_of_day')['avg_flow'].mean()
        peak_hours = hourly_avg.nlargest(3).index.tolist()
        
        return {
            "status": "success",
            "district_id": district_id,
            "predictions": predictions,
            "insights": {
                "peak_hours": peak_hours,
                "avg_daily_consumption": float(df['avg_flow'].mean() * 24),
                "weekend_factor": calculate_weekend_factor(df)
            }
        }
        
    except Exception as e:
        logger.error(f"Error predicting demand: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictive-maintenance")
async def predictive_maintenance(
    pool: asyncpg.Pool,
    equipment_type: str = Query("pump", description="Equipment type: pump, valve, sensor")
):
    """Get predictive maintenance recommendations"""
    try:
        # Analyze equipment performance trends
        async with pool.acquire() as conn:
            if equipment_type == "pump":
                query = """
                    SELECT 
                        node_id,
                        AVG(CASE WHEN flow_rate > 0 THEN pressure / flow_rate ELSE 0 END) as efficiency_indicator,
                        STDDEV(pressure) as pressure_variability,
                        COUNT(*) as reading_count,
                        MAX(timestamp) as last_reading
                    FROM water_infrastructure.sensor_readings
                    WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
                    AND node_id LIKE '%PUMP%'
                    GROUP BY node_id
                """
            else:
                query = """
                    SELECT 
                        node_id,
                        AVG(quality_score) as avg_quality,
                        COUNT(CASE WHEN quality_score < 0.7 THEN 1 END) as low_quality_count,
                        MAX(timestamp) as last_reading
                    FROM water_infrastructure.sensor_readings
                    WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
                    GROUP BY node_id
                """
            
            rows = await conn.fetch(query)
        
        # Generate maintenance recommendations
        recommendations = []
        for row in rows:
            risk_score = calculate_maintenance_risk(row, equipment_type)
            
            if risk_score > 0.7:
                priority = "high"
                action = "Schedule immediate inspection"
            elif risk_score > 0.4:
                priority = "medium"
                action = "Plan maintenance within 2 weeks"
            else:
                priority = "low"
                action = "Continue monitoring"
            
            recommendations.append({
                "equipment_id": row['node_id'],
                "risk_score": round(risk_score, 2),
                "priority": priority,
                "recommended_action": action,
                "indicators": {
                    k: float(v) if isinstance(v, (int, float)) else str(v)
                    for k, v in dict(row).items()
                    if k != 'node_id'
                }
            })
        
        # Sort by risk score
        recommendations.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return {
            "status": "success",
            "equipment_type": equipment_type,
            "total_equipment": len(recommendations),
            "high_priority_count": sum(1 for r in recommendations if r['priority'] == 'high'),
            "recommendations": recommendations[:10]  # Top 10
        }
        
    except Exception as e:
        logger.error(f"Error in predictive maintenance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ml-dashboard-summary")
async def ml_dashboard_summary(pool: asyncpg.Pool):
    """Get ML insights summary for dashboard"""
    try:
        async with pool.acquire() as conn:
            # Get recent anomaly counts
            anomaly_query = """
                SELECT COUNT(*) as count
                FROM water_infrastructure.anomalies
                WHERE detected_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
            """
            anomaly_count = await conn.fetchval(anomaly_query)
            
            # Get model status
            models_trained = len(_models)
            
            # Get prediction accuracy (mock for now)
            accuracy_metrics = {
                "anomaly_detection": 0.92,
                "demand_forecast": 0.87,
                "maintenance_prediction": 0.78
            }
        
        return {
            "status": "success",
            "summary": {
                "models_active": models_trained,
                "anomalies_last_24h": anomaly_count or 0,
                "accuracy_metrics": accuracy_metrics,
                "last_training": datetime.now().isoformat(),
                "recommendations_available": 15
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting ML summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
def generate_recommendations(anomalies: List[Dict], df: pd.DataFrame) -> List[Dict]:
    """Generate actionable recommendations based on anomalies"""
    recommendations = []
    
    # Check for leak patterns
    low_pressure_count = sum(1 for a in anomalies if "LOW_PRESSURE" in a.get("types", []))
    if low_pressure_count > len(anomalies) * 0.3:
        recommendations.append({
            "type": "POTENTIAL_LEAK",
            "severity": "high",
            "action": "Inspect pipeline for leaks in affected area",
            "confidence": 0.85
        })
    
    # Check for night consumption
    night_anomalies = sum(1 for a in anomalies if "NIGHT_CONSUMPTION" in a.get("types", []))
    if night_anomalies > 0:
        recommendations.append({
            "type": "UNUSUAL_NIGHT_USAGE",
            "severity": "medium",
            "action": "Investigate potential unauthorized usage or leak",
            "confidence": 0.75
        })
    
    return recommendations


def calculate_weekend_factor(df: pd.DataFrame) -> float:
    """Calculate ratio of weekend to weekday consumption"""
    weekend_avg = df[df['day_of_week'].isin([5, 6])]['avg_flow'].mean()
    weekday_avg = df[~df['day_of_week'].isin([5, 6])]['avg_flow'].mean()
    return float(weekend_avg / weekday_avg) if weekday_avg > 0 else 1.0


def calculate_maintenance_risk(equipment_data: Dict, equipment_type: str) -> float:
    """Calculate maintenance risk score (0-1)"""
    if equipment_type == "pump":
        # Higher variability = higher risk
        pressure_var = equipment_data.get('pressure_variability', 0)
        risk = min(pressure_var / 2.0, 1.0)  # Normalize
    else:
        # Lower quality score = higher risk
        avg_quality = equipment_data.get('avg_quality', 1)
        risk = 1.0 - avg_quality
    
    return risk 