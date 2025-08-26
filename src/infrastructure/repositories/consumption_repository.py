import asyncpg
from typing import List
from src.schemas.consumption import (
    ConsumptionAnalytics, ConsumptionForecast, ConsumptionAnomaly,
    DistrictConsumption, ConsumptionTimeline, UserSegment, PeakDemand,
    ConservationOpportunity, ForecastData, ForecastInsight, ConsumptionSummary
)
from datetime import datetime, timedelta
import random
import numpy as np
import pandas as pd

class ConsumptionRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_consumption_analytics(self) -> ConsumptionAnalytics:
        """Fetch consumption analytics from the database."""
        try:
            async with self.pool.acquire() as conn:
                # Check if we have consumption data in the database
                # First, let's check what tables exist
                tables_query = """
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'water_infrastructure'
                    AND tablename LIKE '%consumption%'
                """
                tables = await conn.fetch(tables_query)
                
                # If no consumption-related tables exist, return None
                if not tables:
                    return None
                
                # Try to fetch actual consumption data
                # This is a placeholder query - adjust based on actual table structure
                consumption_query = """
                    SELECT 
                        node_id,
                        SUM(flow_rate) as total_consumption,
                        AVG(flow_rate) as avg_consumption,
                        COUNT(DISTINCT DATE(timestamp)) as days_monitored
                    FROM water_infrastructure.sensor_readings
                    WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY node_id
                """
                
                consumption_data = await conn.fetch(consumption_query)
                
                # If no data is found, return None
                if not consumption_data:
                    return None
                
                # Process the data into the expected format
                # This is a simplified version - expand based on actual data structure
                district_consumption = []
                total_consumption = 0
                
                for row in consumption_data:
                    total_consumption += float(row['total_consumption'] or 0)
                
                # If we have no meaningful data, return None
                if total_consumption == 0:
                    return None
                
                # Create a minimal response with actual data
                summary = ConsumptionSummary(
                    total_daily_consumption=round(total_consumption / 30),
                    total_monthly_consumption=round(total_consumption),
                    total_users=len(consumption_data),
                    avg_consumption_per_user=round(total_consumption / max(len(consumption_data), 1), 2),
                    system_efficiency=0.0,  # Cannot calculate without more data
                    water_loss_percentage=0.0  # Cannot calculate without more data
                )
                
                # Return None when we have minimal data
                # The frontend will handle this properly
                return None
                
        except Exception as e:
            # Log the error and return None
            print(f"Error fetching consumption analytics: {e}")
            return None

    async def get_consumption_forecast(self, district_id: str) -> ConsumptionForecast:
        """Fetch consumption forecast from the database or ML models."""
        try:
            async with self.pool.acquire() as conn:
                # Check if we have forecast data or models available
                forecast_query = """
                    SELECT 1 
                    FROM pg_tables 
                    WHERE schemaname = 'water_infrastructure'
                    AND tablename = 'consumption_forecasts'
                    LIMIT 1
                """
                has_forecast_table = await conn.fetchval(forecast_query)
                
                if not has_forecast_table:
                    return None
                
                # Try to fetch actual forecast data
                # This is a placeholder - adjust based on actual implementation
                return None
                
        except Exception as e:
            print(f"Error fetching consumption forecast: {e}")
            return None

    async def get_consumption_anomalies(self) -> List[ConsumptionAnomaly]:
        """Fetch consumption anomalies from the database."""
        try:
            async with self.pool.acquire() as conn:
                # Check if we have anomaly detection data
                anomaly_query = """
                    SELECT 1 
                    FROM pg_tables 
                    WHERE schemaname = 'water_infrastructure'
                    AND tablename = 'consumption_anomalies'
                    LIMIT 1
                """
                has_anomaly_table = await conn.fetchval(anomaly_query)
                
                if not has_anomaly_table:
                    return []
                
                # Try to fetch actual anomaly data
                # This is a placeholder - adjust based on actual implementation
                return []
                
        except Exception as e:
            print(f"Error fetching consumption anomalies: {e}")
            return []
