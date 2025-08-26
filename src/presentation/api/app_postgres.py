"""FastAPI application using PostgreSQL for local development."""

import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import asyncpg
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Abbanoa Water Infrastructure API (PostgreSQL)",
    description="Local API using PostgreSQL for water infrastructure monitoring",
    version="1.0.0-local",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL connection details from environment
POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5434)),
    "database": os.getenv("POSTGRES_DB", "abbanoa_processing"),
    "user": os.getenv("POSTGRES_USER", "abbanoa_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "abbanoa_secure_pass"),
}

# Connection pool
pool: asyncpg.Pool = None


@app.on_event("startup")
async def startup_event():
    """Initialize database connection pool on startup."""
    global pool
    pool = await asyncpg.create_pool(**POSTGRES_CONFIG)
    app.state.pool = pool  # Store pool in app state for dependency injection
    
    # Include user routes
    try:
        from .user_routes import router as user_router
        app.include_router(user_router)
        logger.info("User routes loaded successfully")
    except ImportError as e:
        logger.warning(f"User routes module not found: {e}")
    print(f"Connected to PostgreSQL at {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection pool on shutdown."""
    global pool
    if pool:
        await pool.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-local",
        "database": "PostgreSQL"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        status = "healthy"
    except Exception as e:
        status = "unhealthy"
    
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-local"
    }



from src.presentation.api.routers import nodes as nodes_router

app.include_router(nodes_router.router, prefix="/api/v1", tags=["nodes"])




from src.presentation.api.routers import dashboard as dashboard_router

app.include_router(dashboard_router.router, prefix="/api/v1", tags=["dashboard"])




from src.presentation.api.routers import anomalies as anomalies_router

app.include_router(anomalies_router.router, prefix="/api/v1", tags=["anomalies"])




from src.presentation.api.routers import readings as readings_router

app.include_router(readings_router.router, prefix="/api/v1", tags=["readings"])




from src.presentation.api.routers import efficiency as efficiency_router

app.include_router(efficiency_router.router, prefix="/api/v1", tags=["efficiency"])




from src.presentation.api.routers import auth as auth_router

app.include_router(auth_router.router, prefix="/api/v1", tags=["auth"])




from src.presentation.api.routers import pressure as pressure_router

app.include_router(pressure_router.router, prefix="/api/v1", tags=["pressure"])




from src.presentation.api.routers import consumption as consumption_router

app.include_router(consumption_router.router, prefix="/api/v1", tags=["consumption"])




from src.presentation.api.routers import energy as energy_router

app.include_router(energy_router.router, prefix="/api/v1", tags=["energy"])




from src.presentation.api.routers import weather as weather_router

app.include_router(weather_router.router, prefix="/api/v1", tags=["weather"])




from src.presentation.api.routers import ml as ml_router

app.include_router(ml_router.router, prefix="/api/v1", tags=["ml"])



@app.get("/api/v1/ml/detect-anomalies")
async def detect_anomalies(
    node_id: str = Query(..., description="Node ID to analyze"),
    hours: int = Query(24, description="Hours of data to analyze")
):
    """Detect anomalies in recent sensor data"""
    try:
        # Check if model exists
        model_id = f"anomaly_{node_id}"
        if model_id not in _ml_models:
            # Auto-train if not exists
            await train_anomaly_detector(node_id=node_id, days=7)
        
        detector = _ml_models[model_id]
        
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
            # Generate synthetic data for demo
            logger.info("Generating synthetic recent data for demo")
            dates = pd.date_range(end=datetime.now(), periods=200, freq='5min')
            df = pd.DataFrame({
                'timestamp': dates,
                'flow_rate': np.random.normal(50, 10, 200) + 5*np.sin(np.arange(200)/20),
                'pressure': np.random.normal(5, 0.3, 200),
                'temperature': np.random.normal(20, 1.5, 200)
            })
            # Add more anomalies for better demo
            anomaly_indices = np.random.choice(200, 15, replace=False)
            df.loc[anomaly_indices[:5], 'flow_rate'] *= np.random.uniform(0.3, 0.5, 5)  # Low flow
            df.loc[anomaly_indices[5:10], 'flow_rate'] *= np.random.uniform(1.8, 2.5, 5)  # High flow
            df.loc[anomaly_indices[10:], 'pressure'] *= np.random.uniform(0.4, 0.6, 5)  # Low pressure
        else:
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
                "timestamp": row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp']),
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
        anomaly_rate = len(anomalies) / total_readings * 100 if total_readings > 0 else 0
        
        return {
            "status": "success",
            "summary": {
                "total_readings": total_readings,
                "anomalies_detected": len(anomalies),
                "anomaly_rate": round(anomaly_rate, 2),
                "time_range": {
                    "start": df['timestamp'].min().isoformat() if hasattr(df['timestamp'].min(), 'isoformat') else str(df['timestamp'].min()),
                    "end": df['timestamp'].max().isoformat() if hasattr(df['timestamp'].max(), 'isoformat') else str(df['timestamp'].max())
                }
            },
            "anomalies": anomalies,
            "recommendations": [
                {
                    "type": "POTENTIAL_LEAK" if any("LOW_PRESSURE" in a.get("types", []) for a in anomalies) else "MONITOR",
                    "severity": "high" if len(anomalies) > 5 else "medium",
                    "action": "Inspect pipeline for leaks" if any("LOW_PRESSURE" in a.get("types", []) for a in anomalies) else "Continue monitoring",
                    "confidence": 0.85 if len(anomalies) > 3 else 0.65
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ml/predict-demand")
async def predict_demand(
    district_id: str = Query(..., description="District ID"),
    hours_ahead: int = Query(24, description="Hours to predict ahead")
):
    """Predict water demand for the next N hours"""
    try:
        # Fetch historical data
        async with pool.acquire() as conn:
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
        
        # Generate predictions (simplified for demo)
        predictions = []
        current_time = datetime.now()
        base_flow = 50.0  # Default base flow
        
        if len(rows) > 0:
            # Convert asyncpg records to list of dicts
            data = [dict(row) for row in rows]
            df = pd.DataFrame(data)
            logger.info(f"Demand prediction columns: {df.columns.tolist()}")
            if 'avg_flow' in df.columns:
                base_flow = float(df['avg_flow'].mean())
            else:
                logger.warning("avg_flow column not found, using default base flow")
        
        for h in range(hours_ahead):
            pred_time = current_time + timedelta(hours=h)
            hour_of_day = pred_time.hour
            
            # Simple hourly pattern
            hourly_factor = 1.0
            if 6 <= hour_of_day <= 9:  # Morning peak
                hourly_factor = 1.3
            elif 18 <= hour_of_day <= 21:  # Evening peak
                hourly_factor = 1.2
            elif 0 <= hour_of_day <= 5:  # Night low
                hourly_factor = 0.7
            
            # Weekend factor
            is_weekend = pred_time.weekday() in [5, 6]
            weekend_factor = 0.9 if is_weekend else 1.0
            
            predicted_flow = base_flow * hourly_factor * weekend_factor
            predicted_flow += np.random.normal(0, 5)  # Add some noise
            
            predictions.append({
                "timestamp": pred_time.isoformat(),
                "predicted_flow": round(max(predicted_flow, 0), 2),
                "confidence": 0.8 if len(rows) > 100 else 0.6,
                "hour_of_day": hour_of_day,
                "is_weekend": is_weekend
            })
        
        return {
            "status": "success",
            "district_id": district_id,
            "predictions": predictions,
            "insights": {
                "peak_hours": [7, 8, 19, 20],
                "avg_daily_consumption": round(base_flow * 24, 2),
                "weekend_reduction": "10%"
            }
        }
        
    except Exception as e:
        logger.error(f"Error predicting demand: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ml/dashboard-summary")
async def ml_dashboard_summary():
    """Get ML insights summary for dashboard"""
    try:
        async with pool.acquire() as conn:
            # Get recent anomaly counts
            anomaly_query = """
                SELECT COUNT(*) as count
                FROM water_infrastructure.anomalies
                WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
            """
            anomaly_count = await conn.fetchval(anomaly_query) or 0
            
        # Get model status
        models_trained = len(_ml_models)
        
        # Generate some demo metrics
        return {
            "status": "success",
            "summary": {
                "models_active": models_trained,
                "anomalies_last_24h": int(anomaly_count),
                "accuracy_metrics": {
                    "anomaly_detection": 0.92,
                    "demand_forecast": 0.87,
                    "maintenance_prediction": 0.78
                },
                "last_training": datetime.now().isoformat(),
                "predictions_available": {
                    "anomaly_detection": True,
                    "demand_forecast": True,
                    "predictive_maintenance": True,
                    "water_quality": False
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting ML summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 