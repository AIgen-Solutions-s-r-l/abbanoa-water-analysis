"""Extension methods for prediction tracking in the repository"""

import asyncpg
from typing import Dict, Optional, List
from datetime import datetime
import pandas as pd
import json
import logging

logger = logging.getLogger(__name__)


class TrackingRepositoryExtension:
    """Repository extension for prediction tracking functionality"""
    
    def __init__(self, pool: asyncpg.Pool):
        """Initialize with database pool
        
        Args:
            pool: AsyncPG connection pool
        """
        self.pool = pool
    
    async def get_prediction(self, prediction_id: int) -> Optional[Dict]:
        """Get a specific prediction by ID
        
        Args:
            prediction_id: Prediction ID
            
        Returns:
            Prediction data or None
        """
        query = """SELECT * FROM water_infrastructure.ml_predictions WHERE prediction_id = $1"""
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, prediction_id)
            return dict(row) if row else None
    
    async def update_prediction_outcome(
        self,
        prediction_id: int,
        actual_occurred: bool,
        feedback_source: str = "automatic"
    ):
        """Update prediction with actual outcome
        
        Args:
            prediction_id: Prediction ID
            actual_occurred: Whether anomaly actually occurred
            feedback_source: Source of feedback
        """
        # First add columns if they don't exist
        alter_query = """
            ALTER TABLE water_infrastructure.ml_predictions 
            ADD COLUMN IF NOT EXISTS feedback_source VARCHAR(50);
            
            ALTER TABLE water_infrastructure.ml_predictions
            ADD COLUMN IF NOT EXISTS outcome_timestamp TIMESTAMP WITH TIME ZONE;
        """
        
        update_query = """
            UPDATE water_infrastructure.ml_predictions
            SET actual_occurred = $2,
                feedback_at = NOW(),
                outcome_timestamp = NOW(),
                feedback_source = $3
            WHERE prediction_id = $1
        """
        
        async with self.pool.acquire() as conn:
            await conn.execute(alter_query)
            await conn.execute(update_query, prediction_id, actual_occurred, feedback_source)
            logger.info(f"Updated prediction {prediction_id} outcome: {actual_occurred}")
    
    async def get_unreconciled_predictions(self) -> pd.DataFrame:
        """Get predictions that haven't been reconciled
        
        Returns:
            DataFrame of unreconciled predictions
        """
        query = """
            SELECT * FROM water_infrastructure.ml_predictions
            WHERE actual_occurred IS NULL
                AND predicted_timestamp < NOW()
                AND predicted_timestamp > NOW() - INTERVAL '7 days'
            ORDER BY predicted_timestamp
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            if not rows:
                return pd.DataFrame()
            return pd.DataFrame([dict(row) for row in rows])
    
    async def get_actual_anomalies(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> pd.DataFrame:
        """Get actual anomalies in time range
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            DataFrame of anomalies
        """
        query = """
            SELECT * FROM water_infrastructure.anomalies
            WHERE timestamp BETWEEN $1 AND $2
            ORDER BY timestamp
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, start_time, end_time)
            if not rows:
                return pd.DataFrame()
            return pd.DataFrame([dict(row) for row in rows])
    
    async def get_prediction_outcomes(self, days_back: int) -> pd.DataFrame:
        """Get prediction outcomes for metrics calculation
        
        Args:
            days_back: Days of history
            
        Returns:
            DataFrame with predicted and actual values
        """
        query = """
            SELECT 
                CASE WHEN probability > 0.7 THEN true ELSE false END as predicted,
                COALESCE(actual_occurred, false) as actual
            FROM water_infrastructure.ml_predictions
            WHERE created_at > NOW() - INTERVAL '%s days'
                AND feedback_at IS NOT NULL
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query % days_back)
            if not rows:
                return pd.DataFrame()
            return pd.DataFrame([dict(row) for row in rows])
    
    async def get_node_predictions(self, node_id: str) -> pd.DataFrame:
        """Get predictions for specific node
        
        Args:
            node_id: Node identifier
            
        Returns:
            DataFrame of predictions
        """
        query = """
            SELECT * FROM water_infrastructure.ml_predictions
            WHERE node_id = $1
                AND predicted_timestamp > NOW() - INTERVAL '7 days'
            ORDER BY predicted_timestamp DESC
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, node_id)
            if not rows:
                return pd.DataFrame()
            return pd.DataFrame([dict(row) for row in rows])
    
    async def get_node_anomalies(self, node_id: str) -> pd.DataFrame:
        """Get anomalies for specific node
        
        Args:
            node_id: Node identifier
            
        Returns:
            DataFrame of anomalies
        """
        query = """
            SELECT * FROM water_infrastructure.anomalies
            WHERE node_id = $1
                AND timestamp > NOW() - INTERVAL '7 days'
            ORDER BY timestamp DESC
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, node_id)
            if not rows:
                return pd.DataFrame()
            return pd.DataFrame([dict(row) for row in rows])
    
    async def save_performance_metrics(
        self,
        metrics,
        model_version: str,
        timestamp: datetime
    ):
        """Save performance metrics to database
        
        Args:
            metrics: Performance metrics object
            model_version: Model version
            timestamp: Calculation timestamp
        """
        # Create table if not exists
        create_table = """
            CREATE TABLE IF NOT EXISTS water_infrastructure.model_performance_metrics (
                metric_id SERIAL PRIMARY KEY,
                calculated_at TIMESTAMP WITH TIME ZONE,
                model_version VARCHAR(20),
                time_window INTERVAL DEFAULT '7 days',
                precision NUMERIC(4,3),
                recall NUMERIC(4,3),
                f1_score NUMERIC(4,3),
                accuracy NUMERIC(4,3),
                true_positives INT,
                false_positives INT,
                true_negatives INT,
                false_negatives INT
            );
            
            CREATE INDEX IF NOT EXISTS idx_performance_metrics_time 
            ON water_infrastructure.model_performance_metrics(calculated_at DESC);
        """
        
        insert_query = """
            INSERT INTO water_infrastructure.model_performance_metrics (
                calculated_at, model_version, precision, recall, f1_score, accuracy,
                true_positives, false_positives, true_negatives, false_negatives
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """
        
        async with self.pool.acquire() as conn:
            await conn.execute(create_table)
            await conn.execute(
                insert_query,
                timestamp,
                model_version,
                metrics.precision,
                metrics.recall,
                metrics.f1_score,
                metrics.accuracy,
                metrics.true_positives,
                metrics.false_positives,
                metrics.true_negatives,
                metrics.false_negatives
            )
            logger.info(f"Saved performance metrics for {model_version}")
    
    async def delete_old_predictions(self, retention_days: int) -> int:
        """Delete predictions older than retention period
        
        Args:
            retention_days: Days to retain
            
        Returns:
            Number of deleted records
        """
        query = """
            DELETE FROM water_infrastructure.ml_predictions
            WHERE created_at < NOW() - INTERVAL '%s days'
            RETURNING prediction_id
        """
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query % retention_days)
            deleted_count = len(rows)
            logger.info(f"Deleted {deleted_count} old predictions")
            return deleted_count
    
    async def save_operator_feedback(self, feedback: Dict):
        """Save detailed operator feedback
        
        Args:
            feedback: Feedback data from operator
        """
        # Create feedback table if not exists
        create_table = """
            CREATE TABLE IF NOT EXISTS water_infrastructure.operator_feedback (
                feedback_id SERIAL PRIMARY KEY,
                prediction_id INT REFERENCES water_infrastructure.ml_predictions(prediction_id),
                operator_id VARCHAR(50),
                feedback_type VARCHAR(50),
                notes TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_operator_feedback_prediction 
            ON water_infrastructure.operator_feedback(prediction_id);
        """
        
        insert_query = """
            INSERT INTO water_infrastructure.operator_feedback 
            (prediction_id, operator_id, feedback_type, notes)
            VALUES ($1, $2, $3, $4)
        """
        
        async with self.pool.acquire() as conn:
            await conn.execute(create_table)
            await conn.execute(
                insert_query,
                feedback['prediction_id'],
                feedback.get('operator_id', 'unknown'),
                feedback['feedback'],
                feedback.get('notes', '')
            )
    
    async def get_feedback_count(self, days: int = 1) -> int:
        """Get count of recent operator feedback
        
        Args:
            days: Days to look back
            
        Returns:
            Count of feedback entries
        """
        query = """
            SELECT COUNT(*) as count
            FROM water_infrastructure.operator_feedback
            WHERE created_at > NOW() - INTERVAL '%s days'
        """
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query % days)
            return row['count'] if row else 0
    
    async def log_alert(self, alert_type: str, details: Dict):
        """Log performance alerts
        
        Args:
            alert_type: Type of alert
            details: Alert details
        """
        # Create alerts table if not exists
        create_table = """
            CREATE TABLE IF NOT EXISTS water_infrastructure.performance_alerts (
                alert_id SERIAL PRIMARY KEY,
                alert_type VARCHAR(50),
                details JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """
        
        insert_query = """
            INSERT INTO water_infrastructure.performance_alerts (alert_type, details)
            VALUES ($1, $2)
        """
        
        async with self.pool.acquire() as conn:
            await conn.execute(create_table)
            await conn.execute(insert_query, alert_type, json.dumps(details))
            logger.warning(f"Performance alert: {alert_type} - {details}")