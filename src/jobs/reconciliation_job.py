"""Hourly reconciliation job for prediction tracking"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any
import pytz

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.jobs.base_job import BaseJob
from src.application.services.prediction_tracker import PredictionTracker
from src.infrastructure.repositories.tracking_repository_extension import TrackingRepositoryExtension


class ReconciliationJob(BaseJob):
    """Hourly job to reconcile ML predictions with actual anomalies"""
    
    def __init__(self):
        super().__init__(
            job_name="prediction_reconciliation",
            timeout_minutes=30
        )
        self.min_reconciliation_interval_hours = 1
    
    async def execute(self, pool) -> Dict[str, Any]:
        """Execute reconciliation for all unreconciled predictions"""
        self.logger.info("Starting prediction reconciliation")
        
        # Initialize services
        repo = TrackingRepositoryExtension(pool)
        tracker = PredictionTracker(repository=repo)
        
        # Check if enough time has passed since last reconciliation
        last_execution = await self.get_last_execution(pool)
        if last_execution and self._should_skip_execution(last_execution):
            self.logger.info("Skipping reconciliation - too soon since last run")
            return {
                "status": "skipped",
                "reason": "minimum_interval_not_reached",
                "last_run": last_execution["started_at"].isoformat() if last_execution["started_at"] else None
            }
        
        # Get unreconciled predictions to check count
        unreconciled_predictions = await repo.get_unreconciled_predictions()
        unreconciled_count = len(unreconciled_predictions)
        
        if unreconciled_count == 0:
            self.logger.info("No unreconciled predictions found")
            return {
                "status": "success",
                "message": "No predictions to reconcile",
                "unreconciled_count": 0
            }
        
        self.logger.info(f"Found {unreconciled_count} predictions to reconcile")
        
        # Perform reconciliation
        try:
            result = await tracker.reconcile_predictions()
            
            # Log reconciliation results
            self.logger.info(
                f"Reconciliation completed: {result.reconciled_count}/{result.total_predictions} predictions processed"
            )
            self.logger.info(
                f"Results - TP: {result.true_positives}, FP: {result.false_positives}, "
                f"TN: {result.true_negatives}, FN: {result.false_negatives}"
            )
            
            # Check if performance is degraded and alert
            await self._check_performance_and_alert(tracker)
            
            return {
                "status": "success",
                "total_predictions": result.total_predictions,
                "reconciled_count": result.reconciled_count,
                "true_positives": result.true_positives,
                "false_positives": result.false_positives,
                "true_negatives": result.true_negatives,
                "false_negatives": result.false_negatives,
                "timestamp": result.timestamp.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Reconciliation failed: {e}")
            await self.send_alert(
                f"Prediction reconciliation failed: {str(e)}", 
                severity="critical"
            )
            raise
    
    def _should_skip_execution(self, last_execution: Dict) -> bool:
        """Check if we should skip execution based on last run time"""
        if not last_execution or not last_execution.get("started_at"):
            return False
        
        last_run = last_execution["started_at"]
        
        # Ensure both datetimes are timezone-aware for comparison
        if last_run.tzinfo is None:
            last_run = pytz.UTC.localize(last_run)
        
        now = datetime.now(pytz.UTC)
        time_since_last = now - last_run
        min_interval = timedelta(hours=self.min_reconciliation_interval_hours)
        
        return time_since_last < min_interval
    
    async def _check_performance_and_alert(self, tracker: PredictionTracker):
        """Check model performance and send alerts if degraded"""
        try:
            # Check performance with F1 threshold of 0.7
            is_degraded = await tracker.check_performance_degradation(threshold_f1=0.7)
            
            if is_degraded:
                metrics = await tracker.calculate_metrics(days_back=7)
                await self.send_alert(
                    f"Model performance degraded! Current F1: {metrics.f1_score:.3f} (threshold: 0.7). "
                    f"Precision: {metrics.precision:.3f}, Recall: {metrics.recall:.3f}",
                    severity="warning"
                )
                
                self.logger.warning(f"Performance degradation detected - F1: {metrics.f1_score:.3f}")
            
        except Exception as e:
            self.logger.error(f"Performance check failed: {e}")


async def main():
    """Run reconciliation job"""
    job = ReconciliationJob()
    success = await job.run()
    
    if not success:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())