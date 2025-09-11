"""API endpoints for ML-based predictions."""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.application.prediction_service import PredictionService
from src.presentation.api.app_postgres import pool as db_pool

logger = logging.getLogger(__name__)
router = APIRouter()


class EnergyTariffs(BaseModel):
    """Energy tariff structure for optimization."""

    peak: List[int]
    off_peak: List[int]
    rates: Dict[str, float]


class OptimizeEnergyRequest(BaseModel):
    """Request model for energy optimization."""

    zone_id: int
    tariffs: EnergyTariffs


@router.get("/peak-demand")
async def predict_peak_demand(
    zone_id: int = Query(..., description="Zone ID"),
    days: int = Query(7, ge=1, le=30, description="Days to forecast"),
) -> Dict[str, Any]:
    """Predict peak water demand for next N days."""
    try:
        if not db_pool:
            raise HTTPException(status_code=503, detail="Database not available")
        async with db_pool.acquire() as conn:
            # Fetch historical consumption data (last 30 days)
            query = """
                SELECT hour, consumption 
                FROM consumption_patterns 
                WHERE zone_id = $1 
                AND timestamp >= NOW() - INTERVAL '30 days'
                ORDER BY timestamp
            """
            rows = await conn.fetch(query, zone_id)

            if not rows:
                raise HTTPException(
                    status_code=404, detail=f"No data found for zone {zone_id}"
                )

            # Convert to numpy array
            historical_data = np.array([row["consumption"] for row in rows])

            # Get predictions
            service = PredictionService()
            predictions = service.predict_peak_demand(historical_data, days=days)

            return predictions

    except Exception as e:
        logger.error(f"Error predicting peak demand: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-energy")
async def optimize_energy_schedule(
    request: OptimizeEnergyRequest,
) -> Dict[str, Any]:
    """Optimize pump scheduling for energy cost reduction."""
    try:
        if not db_pool:
            raise HTTPException(status_code=503, detail="Database not available")
        async with db_pool.acquire() as conn:
            # Fetch demand forecast for next 24 hours
            query = """
                SELECT hour, consumption 
                FROM consumption_patterns 
                WHERE zone_id = $1 
                AND timestamp >= NOW() - INTERVAL '7 days'
                AND EXTRACT(hour FROM timestamp) < 24
                ORDER BY timestamp DESC
                LIMIT 168
            """
            rows = await conn.fetch(query, request.zone_id)

            if not rows:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for zone {request.zone_id}",
                )

            # Average consumption by hour
            hourly_avg = np.zeros(24)
            for row in rows:
                hour = row["hour"]
                hourly_avg[hour % 24] += row["consumption"]
            hourly_avg = hourly_avg / 7  # Average over 7 days

            # Optimize schedule
            service = PredictionService()
            optimization = service.optimize_energy_cost(
                hourly_avg, request.tariffs.dict()
            )

            return optimization

    except Exception as e:
        logger.error(f"Error optimizing energy schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/maintenance")
async def predict_maintenance(
    equipment_id: str = Query(..., description="Equipment ID"),
) -> Dict[str, Any]:
    """Predict maintenance needs for equipment."""
    try:
        if not db_pool:
            raise HTTPException(status_code=503, detail="Database not available")
        async with db_pool.acquire() as conn:
            # Fetch sensor history
            query = """
                SELECT timestamp, pressure, vibration, temperature 
                FROM sensor_readings 
                WHERE equipment_id = $1 
                AND timestamp >= NOW() - INTERVAL '30 days'
                ORDER BY timestamp
            """
            rows = await conn.fetch(query, equipment_id)

            if not rows:
                # Return low risk for unknown equipment
                return {
                    "risk_score": "low",
                    "days_to_maintenance": 90,
                    "failure_probability": 0.1,
                    "confidence": 0.5,
                    "recommendations": ["Continue routine maintenance schedule"],
                }

            # Prepare sensor data
            sensor_history = {
                "pressure": np.array([row["pressure"] for row in rows]),
                "vibration": np.array(
                    [row["vibration"] for row in rows if row["vibration"]]
                ),
                "temperature": np.array(
                    [row["temperature"] for row in rows if row["temperature"]]
                ),
            }

            # Get equipment age
            age_query = """
                SELECT installation_date 
                FROM equipment 
                WHERE equipment_id = $1
            """
            age_row = await conn.fetchone(age_query, equipment_id)
            if age_row and age_row["installation_date"]:
                from datetime import datetime

                age_days = (datetime.now() - age_row["installation_date"]).days
                sensor_history["equipment_age_days"] = age_days

            # Get predictions
            service = PredictionService()
            predictions = service.predict_maintenance(sensor_history)

            return predictions

    except Exception as e:
        logger.error(f"Error predicting maintenance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/water-loss")
async def predict_water_loss(
    zone_id: int = Query(..., description="Zone ID"),
) -> Dict[str, Any]:
    """Predict water loss and potential leaks."""
    try:
        if not db_pool:
            raise HTTPException(status_code=503, detail="Database not available")
        async with db_pool.acquire() as conn:
            # Fetch flow data
            query = """
                SELECT flow_in, flow_out, pressure, night_flow 
                FROM flow_measurements 
                WHERE zone_id = $1 
                AND timestamp >= NOW() - INTERVAL '24 hours'
                ORDER BY timestamp
            """
            rows = await conn.fetch(query, zone_id)

            if not rows:
                return {
                    "current_loss_percentage": 0,
                    "predicted_loss_trend": "unknown",
                    "leak_probability": 0,
                    "recommended_actions": ["Install flow meters for monitoring"],
                }

            # Prepare flow data
            flow_data = {
                "flow_in": np.array([row["flow_in"] for row in rows]),
                "flow_out": np.array([row["flow_out"] for row in rows]),
                "pressure": np.array([row["pressure"] for row in rows]),
                "night_flow": np.array(
                    [row["night_flow"] for row in rows if row["night_flow"]]
                ),
            }

            # Get predictions
            service = PredictionService()
            predictions = service.predict_water_loss(flow_data)

            return predictions

    except Exception as e:
        logger.error(f"Error predicting water loss: {e}")
        raise HTTPException(status_code=500, detail=str(e))