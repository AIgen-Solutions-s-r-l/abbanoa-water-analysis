"""Repository for anomaly predictions using real PostgreSQL data"""

import asyncpg
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AnomalyTrainingData:
    """Training data for anomaly prediction model"""
    sensor_data: pd.DataFrame
    anomaly_labels: pd.DataFrame
    node_info: Dict


class AnomalyPredictionRepository:
    """Repository for accessing real sensor and anomaly data from PostgreSQL"""
    
    def __init__(self, pool: asyncpg.Pool):
        """Initialize repository with database connection pool
        
        Args:
            pool: AsyncPG connection pool
        """
        self.pool = pool
    
    async def get_sensor_data_for_node(
        self, 
        node_id: str, 
        hours_back: int = 24
    ) -> pd.DataFrame:
        """Fetch real sensor data for a specific node
        
        Args:
            node_id: Node identifier
            hours_back: Hours of historical data to fetch
            
        Returns:
            DataFrame with sensor readings
        """
        query = """
            SELECT 
                timestamp,
                node_id,
                pressure,
                flow_rate,
                temperature,
                quality_score
            FROM water_infrastructure.sensor_readings
            WHERE node_id = $1
                AND timestamp > NOW() - INTERVAL '%s hours'
            ORDER BY timestamp DESC
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query % hours_back, node_id)
            
            if not rows:
                logger.warning(f"No sensor data found for node {node_id}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = pd.DataFrame([dict(row) for row in rows])
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            
            # Ensure numeric types
            numeric_cols = ['pressure', 'flow_rate', 'temperature', 'quality_score']
            for col in numeric_cols:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
            
            return data
    
    async def get_recent_sensor_data_all_nodes(
        self, 
        hours_back: int = 6
    ) -> Dict[str, pd.DataFrame]:
        """Fetch recent sensor data for all active nodes
        
        Args:
            hours_back: Hours of historical data
            
        Returns:
            Dictionary mapping node_id to sensor data DataFrame
        """
        query = """
            SELECT 
                timestamp,
                node_id,
                pressure,
                flow_rate,
                temperature,
                quality_score
            FROM water_infrastructure.sensor_readings
            WHERE timestamp > NOW() - INTERVAL '%s hours'
            ORDER BY node_id, timestamp DESC
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query % hours_back)
            
            if not rows:
                logger.warning("No recent sensor data found")
                return {}
            
            # Group by node_id
            df = pd.DataFrame([dict(row) for row in rows])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Convert numeric columns
            numeric_cols = ['pressure', 'flow_rate', 'temperature', 'quality_score']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Split by node
            node_data = {}
            for node_id in df['node_id'].unique():
                node_df = df[df['node_id'] == node_id].copy()
                node_df = node_df.sort_values('timestamp')
                node_data[node_id] = node_df
            
            return node_data
    
    async def get_historical_anomalies(
        self, 
        days_back: int = 30,
        node_id: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch historical anomalies for training
        
        Args:
            days_back: Days of historical anomalies
            node_id: Optional filter by node
            
        Returns:
            DataFrame with anomaly records
        """
        query = """
            SELECT 
                anomaly_id,
                timestamp,
                node_id,
                anomaly_type,
                severity,
                measurement_type,
                actual_value,
                expected_value,
                deviation_percentage,
                detection_method,
                is_confirmed,
                resolved_at,
                metadata
            FROM water_infrastructure.anomalies
            WHERE timestamp > NOW() - INTERVAL '%s days'
        """
        
        if node_id:
            query += f" AND node_id = '{node_id}'"
        
        query += " ORDER BY timestamp DESC"
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query % days_back)
            
            if not rows:
                logger.info(f"No historical anomalies found for last {days_back} days")
                return pd.DataFrame()
            
            # Convert to DataFrame
            anomalies = pd.DataFrame([dict(row) for row in rows])
            anomalies['timestamp'] = pd.to_datetime(anomalies['timestamp'])
            
            # Convert numeric columns
            numeric_cols = ['actual_value', 'expected_value', 'deviation_percentage']
            for col in numeric_cols:
                if col in anomalies.columns:
                    anomalies[col] = pd.to_numeric(anomalies[col], errors='coerce')
            
            return anomalies
    
    async def get_training_data(
        self,
        days_back: int = 30,
        node_id: Optional[str] = None
    ) -> AnomalyTrainingData:
        """Prepare training data combining sensors and anomalies
        
        Args:
            days_back: Days of historical data
            node_id: Optional filter by node
            
        Returns:
            AnomalyTrainingData with aligned sensor readings and labels
        """
        # Get historical anomalies
        anomalies = await self.get_historical_anomalies(days_back, node_id)
        
        # Build query for sensor data
        sensor_query = """
            SELECT 
                timestamp,
                node_id,
                pressure,
                flow_rate,
                temperature,
                quality_score
            FROM water_infrastructure.sensor_readings
            WHERE timestamp > NOW() - INTERVAL '%s days'
        """
        
        if node_id:
            sensor_query += f" AND node_id = '{node_id}'"
        
        sensor_query += " ORDER BY timestamp"
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sensor_query % days_back)
            
            if not rows:
                logger.warning("No sensor data found for training")
                return AnomalyTrainingData(
                    sensor_data=pd.DataFrame(),
                    anomaly_labels=pd.DataFrame(),
                    node_info={}
                )
            
            # Convert to DataFrame
            sensors = pd.DataFrame([dict(row) for row in rows])
            sensors['timestamp'] = pd.to_datetime(sensors['timestamp'])
            
            # Convert numeric columns
            numeric_cols = ['pressure', 'flow_rate', 'temperature', 'quality_score']
            for col in numeric_cols:
                if col in sensors.columns:
                    sensors[col] = pd.to_numeric(sensors[col], errors='coerce')
            
            # Create labels: 1 if anomaly occurred within next 6 hours
            sensors['has_anomaly'] = False
            
            if not anomalies.empty:
                for _, anomaly in anomalies.iterrows():
                    # Find sensor readings 1-6 hours before this anomaly
                    anomaly_time = anomaly['timestamp']
                    node = anomaly['node_id']
                    
                    # Mark sensor readings that preceded this anomaly
                    mask = (
                        (sensors['node_id'] == node) &
                        (sensors['timestamp'] >= anomaly_time - timedelta(hours=6)) &
                        (sensors['timestamp'] <= anomaly_time)
                    )
                    sensors.loc[mask, 'has_anomaly'] = True
            
            # Get node information
            node_query = """
                SELECT node_id, node_name, latitude, longitude, node_type
                FROM water_infrastructure.nodes
                WHERE is_active = true
            """
            node_rows = await conn.fetch(node_query)
            node_info = {row['node_id']: dict(row) for row in node_rows}
            
            return AnomalyTrainingData(
                sensor_data=sensors,
                anomaly_labels=anomalies,
                node_info=node_info
            )
    
    async def save_prediction(
        self,
        node_id: str,
        probability: float,
        predicted_time: datetime,
        confidence: str,
        risk_factors: List[str],
        model_version: str = "v1.0"
    ) -> int:
        """Save anomaly prediction to database
        
        Args:
            node_id: Node identifier
            probability: Anomaly probability (0-1)
            predicted_time: When anomaly is predicted to occur
            confidence: Confidence level (LOW/MEDIUM/HIGH)
            risk_factors: List of identified risk factors
            model_version: Version of the prediction model
            
        Returns:
            Prediction ID
        """
        # First check if ml_predictions table exists, if not create it
        create_table_query = """
            CREATE TABLE IF NOT EXISTS water_infrastructure.ml_predictions (
                prediction_id SERIAL PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                node_id VARCHAR(100),
                prediction_type VARCHAR(50) DEFAULT 'anomaly',
                probability NUMERIC(4,3),
                predicted_timestamp TIMESTAMP WITH TIME ZONE,
                confidence VARCHAR(20),
                risk_factors TEXT[],
                model_version VARCHAR(20),
                metadata JSONB,
                actual_occurred BOOLEAN,
                feedback_at TIMESTAMP WITH TIME ZONE
            );
            
            CREATE INDEX IF NOT EXISTS idx_ml_predictions_node_time 
            ON water_infrastructure.ml_predictions(node_id, predicted_timestamp);
        """
        
        insert_query = """
            INSERT INTO water_infrastructure.ml_predictions (
                node_id, probability, predicted_timestamp, confidence, 
                risk_factors, model_version, metadata
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING prediction_id
        """
        
        async with self.pool.acquire() as conn:
            # Ensure table exists
            await conn.execute(create_table_query)
            
            # Insert prediction
            import json
            metadata = json.dumps({
                'risk_factors_detail': risk_factors,
                'prediction_timestamp': datetime.now().isoformat()
            })
            
            row = await conn.fetchrow(
                insert_query,
                node_id,
                probability,
                predicted_time,
                confidence,
                risk_factors,
                model_version,
                metadata
            )
            
            prediction_id = row['prediction_id']
            logger.info(f"Saved prediction {prediction_id} for node {node_id}")
            
            return prediction_id
    
    async def get_node_statistics(self, node_id: str) -> Dict:
        """Get statistical summary for a node (for feature engineering)
        
        Args:
            node_id: Node identifier
            
        Returns:
            Dictionary with statistical metrics
        """
        query = """
            WITH recent_data AS (
                SELECT 
                    pressure,
                    flow_rate,
                    quality_score
                FROM water_infrastructure.sensor_readings
                WHERE node_id = $1
                    AND timestamp > NOW() - INTERVAL '7 days'
            ),
            anomaly_stats AS (
                SELECT 
                    COUNT(*) as anomaly_count,
                    MAX(timestamp) as last_anomaly
                FROM water_infrastructure.anomalies
                WHERE node_id = $1
                    AND timestamp > NOW() - INTERVAL '30 days'
            )
            SELECT 
                AVG(rd.pressure) as avg_pressure,
                STDDEV(rd.pressure) as std_pressure,
                AVG(rd.flow_rate) as avg_flow,
                STDDEV(rd.flow_rate) as std_flow,
                MIN(rd.quality_score) as min_quality,
                as_data.anomaly_count,
                as_data.last_anomaly
            FROM recent_data rd, anomaly_stats as_data
            GROUP BY as_data.anomaly_count, as_data.last_anomaly
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, node_id)
            
            if not row:
                return {}
            
            return {
                'avg_pressure': float(row['avg_pressure']) if row['avg_pressure'] else 0,
                'std_pressure': float(row['std_pressure']) if row['std_pressure'] else 0,
                'avg_flow': float(row['avg_flow']) if row['avg_flow'] else 0,
                'std_flow': float(row['std_flow']) if row['std_flow'] else 0,
                'min_quality': float(row['min_quality']) if row['min_quality'] else 0,
                'recent_anomalies': int(row['anomaly_count']) if row['anomaly_count'] else 0,
                'last_anomaly': row['last_anomaly']
            }
    
    async def get_active_nodes(self) -> List[str]:
        """Get list of all active nodes
        
        Returns:
            List of node IDs
        """
        query = """
            SELECT DISTINCT node_id 
            FROM water_infrastructure.sensor_readings
            WHERE timestamp > NOW() - INTERVAL '30 days'
            ORDER BY node_id
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [row['node_id'] for row in rows]