"""Batch prediction job for generating ML predictions for all active nodes"""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.jobs.base_job import BaseJob


class BatchPredictionJob(BaseJob):
    """Job to generate predictions for all active nodes in the network"""
    
    def __init__(self):
        super().__init__(
            job_name="batch_prediction",
            timeout_minutes=45
        )
        self.prediction_horizon_hours = 6  # Predict 6 hours ahead
        self.min_confidence_threshold = 0.3  # Only save predictions above this confidence
    
    async def execute(self, pool) -> Dict[str, Any]:
        """Execute batch prediction for all active nodes"""
        self.logger.info("Starting batch prediction generation")
        
        # We'll implement a simple prediction logic here
        # In a full implementation, this would use a trained ML model
        
        # Get all active nodes
        active_nodes = await self._get_active_nodes(pool)
        
        if not active_nodes:
            self.logger.warning("No active nodes found for prediction")
            return {
                "status": "success", 
                "message": "No active nodes to process",
                "nodes_processed": 0,
                "predictions_created": 0
            }
        
        self.logger.info(f"Found {len(active_nodes)} active nodes for prediction")
        
        # Process nodes in batches to avoid overwhelming the system
        batch_size = 10
        total_predictions = 0
        successful_nodes = 0
        failed_nodes = []
        
        for i in range(0, len(active_nodes), batch_size):
            batch = active_nodes[i:i + batch_size]
            batch_results = await self._process_node_batch(batch, pool)
            
            for node_id, result in batch_results.items():
                if result["success"]:
                    successful_nodes += 1
                    total_predictions += result["predictions_created"]
                else:
                    failed_nodes.append(node_id)
                    self.logger.error(f"Failed to process node {node_id}: {result['error']}")
        
        # Log summary
        self.logger.info(
            f"Batch prediction completed: {successful_nodes}/{len(active_nodes)} nodes successful, "
            f"{total_predictions} predictions created"
        )
        
        # Alert if too many failures
        failure_rate = len(failed_nodes) / len(active_nodes) if active_nodes else 0
        if failure_rate > 0.2:  # More than 20% failures
            await self.send_alert(
                f"High failure rate in batch prediction: {len(failed_nodes)}/{len(active_nodes)} nodes failed",
                severity="warning"
            )
        
        return {
            "status": "success",
            "nodes_processed": len(active_nodes),
            "successful_nodes": successful_nodes,
            "failed_nodes": len(failed_nodes),
            "failed_node_ids": failed_nodes,
            "predictions_created": total_predictions,
            "failure_rate": failure_rate
        }
    
    async def _get_active_nodes(self, pool) -> List[str]:
        """Get all active nodes that have recent sensor data"""
        query = """
            SELECT DISTINCT node_id 
            FROM water_infrastructure.sensor_readings 
            WHERE timestamp > NOW() - INTERVAL '24 hours'
            AND value IS NOT NULL
            ORDER BY node_id
        """
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [row['node_id'] for row in rows]
    
    async def _process_node_batch(
        self, 
        node_batch: List[str], 
        pool
    ) -> Dict[str, Dict[str, Any]]:
        """Process a batch of nodes for prediction"""
        results = {}
        
        # Process nodes concurrently within the batch
        tasks = [
            self._generate_node_predictions(node_id, pool)
            for node_id in node_batch
        ]
        
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for node_id, result in zip(node_batch, batch_results):
            if isinstance(result, Exception):
                results[node_id] = {
                    "success": False,
                    "error": str(result),
                    "predictions_created": 0
                }
            else:
                results[node_id] = result
        
        return results
    
    async def _generate_node_predictions(
        self, 
        node_id: str, 
        pool
    ) -> Dict[str, Any]:
        """Generate predictions for a single node"""
        try:
            # Get recent sensor data for the node
            recent_data = await self._get_node_recent_data(node_id, pool)
            
            if not recent_data:
                return {
                    "success": True,
                    "message": "No recent data available",
                    "predictions_created": 0
                }
            
            # Simple prediction logic based on statistical anomalies
            # In production, this would use a trained ML model
            prediction_time = datetime.now() + timedelta(hours=self.prediction_horizon_hours)
            
            # Basic anomaly detection based on standard deviation
            avg_value = recent_data.get("avg_value", 0)
            std_value = recent_data.get("std_value", 0)
            max_value = recent_data.get("max_value", 0)
            
            # Simple rule-based prediction
            if std_value > 0 and max_value > avg_value + 2 * std_value:
                probability = min(0.8, (max_value - avg_value) / (3 * std_value))
                confidence = 0.7
            else:
                probability = 0.1
                confidence = 0.5
            
            # Only save if confidence is above threshold
            if confidence < self.min_confidence_threshold:
                return {
                    "success": True,
                    "message": "Low confidence prediction skipped",
                    "predictions_created": 0
                }
            
            # Save prediction to database
            await self._save_prediction(pool, node_id, prediction_time, probability, confidence)
            
            self.logger.debug(
                f"Created prediction for {node_id}: "
                f"probability={probability:.3f}, confidence={confidence:.3f}"
            )
            
            return {
                "success": True,
                "predictions_created": 1,
                "probability": probability,
                "confidence": confidence
            }
            
        except Exception as e:
            self.logger.error(f"Error generating prediction for node {node_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "predictions_created": 0
            }
    
    async def _get_node_recent_data(self, node_id: str, pool) -> Dict[str, Any]:
        """Get recent sensor data for feature engineering"""
        query = """
            SELECT 
                AVG(value) as avg_value,
                STDDEV(value) as std_value,
                MIN(value) as min_value,
                MAX(value) as max_value,
                COUNT(*) as reading_count
            FROM water_infrastructure.sensor_readings 
            WHERE node_id = $1 
            AND timestamp > NOW() - INTERVAL '4 hours'
            AND value IS NOT NULL
        """
        
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, node_id)
            
            if not row or row['reading_count'] == 0:
                return {}
            
            return {
                "avg_value": float(row['avg_value']) if row['avg_value'] else 0.0,
                "std_value": float(row['std_value']) if row['std_value'] else 0.0,
                "min_value": float(row['min_value']) if row['min_value'] else 0.0,
                "max_value": float(row['max_value']) if row['max_value'] else 0.0,
                "reading_count": int(row['reading_count']),
                "node_id": node_id
            }
    
    async def _save_prediction(self, pool, node_id: str, prediction_time: datetime, probability: float, confidence: float):
        """Save prediction to database"""
        query = """
            INSERT INTO water_infrastructure.ml_predictions 
            (node_id, probability, predicted_timestamp, confidence, risk_factors, model_version, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """
        
        # Convert confidence to risk level
        if confidence > 0.8:
            confidence_level = 'VERY_HIGH'
        elif confidence > 0.6:
            confidence_level = 'HIGH'
        elif confidence > 0.4:
            confidence_level = 'MEDIUM'
        else:
            confidence_level = 'LOW'
        
        risk_factors = ['statistical_anomaly'] if probability > 0.5 else ['normal_variation']
        metadata = json.dumps({
            "job": "batch_prediction",
            "algorithm": "statistical_threshold", 
            "timestamp": datetime.now().isoformat()
        })
        
        async with pool.acquire() as conn:
            await conn.execute(
                query,
                node_id,
                probability,
                prediction_time,
                confidence_level,
                risk_factors,
                'batch_v1.0',
                metadata
            )


async def main():
    """Run batch prediction job"""
    job = BatchPredictionJob()
    success = await job.run()
    
    if not success:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())