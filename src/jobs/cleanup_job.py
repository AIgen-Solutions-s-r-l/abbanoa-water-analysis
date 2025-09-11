"""Daily cleanup job for old predictions and job executions"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.jobs.base_job import BaseJob
from src.application.services.prediction_tracker import PredictionTracker
from src.infrastructure.repositories.tracking_repository_extension import TrackingRepositoryExtension


class CleanupJob(BaseJob):
    """Daily job to clean up old predictions and job execution records"""
    
    def __init__(self):
        super().__init__(
            job_name="daily_cleanup",
            timeout_minutes=20
        )
        # Retention periods in days
        self.prediction_retention_days = 90
        self.job_execution_retention_days = 30
        self.performance_metrics_retention_days = 365
    
    async def execute(self, pool) -> Dict[str, Any]:
        """Execute cleanup for old records"""
        self.logger.info("Starting daily cleanup")
        
        cleanup_results = {}
        
        # Clean up old predictions
        try:
            repo = TrackingRepositoryExtension(pool)
            tracker = PredictionTracker(repository=repo)
            
            predictions_deleted = await tracker.cleanup_old_predictions(
                retention_days=self.prediction_retention_days
            )
            cleanup_results["predictions_deleted"] = predictions_deleted
            
            self.logger.info(f"Deleted {predictions_deleted} old predictions")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup predictions: {e}")
            cleanup_results["predictions_error"] = str(e)
        
        # Clean up old job execution records
        try:
            job_executions_deleted = await self._cleanup_job_executions(pool)
            cleanup_results["job_executions_deleted"] = job_executions_deleted
            
            self.logger.info(f"Deleted {job_executions_deleted} old job execution records")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup job executions: {e}")
            cleanup_results["job_executions_error"] = str(e)
        
        # Clean up old performance metrics
        try:
            metrics_deleted = await self._cleanup_performance_metrics(pool)
            cleanup_results["performance_metrics_deleted"] = metrics_deleted
            
            self.logger.info(f"Deleted {metrics_deleted} old performance metric records")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup performance metrics: {e}")
            cleanup_results["performance_metrics_error"] = str(e)
        
        # Vacuum analyze the cleaned tables for better performance
        try:
            await self._vacuum_tables(pool)
            cleanup_results["vacuum_completed"] = True
            self.logger.info("Database vacuum completed")
            
        except Exception as e:
            self.logger.error(f"Failed to vacuum tables: {e}")
            cleanup_results["vacuum_error"] = str(e)
        
        # Calculate total space reclaimed estimate
        total_deleted = sum([
            cleanup_results.get("predictions_deleted", 0),
            cleanup_results.get("job_executions_deleted", 0),
            cleanup_results.get("performance_metrics_deleted", 0)
        ])
        
        self.logger.info(f"Cleanup completed: {total_deleted} total records deleted")
        
        # Alert if cleanup failed for any component
        errors = [k for k in cleanup_results.keys() if k.endswith("_error")]
        if errors:
            await self.send_alert(
                f"Cleanup job had {len(errors)} errors: {', '.join(errors)}",
                severity="warning"
            )
        
        return {
            "status": "success",
            "total_records_deleted": total_deleted,
            "retention_periods": {
                "predictions_days": self.prediction_retention_days,
                "job_executions_days": self.job_execution_retention_days,
                "performance_metrics_days": self.performance_metrics_retention_days
            },
            "cleanup_results": cleanup_results
        }
    
    async def _cleanup_job_executions(self, pool) -> int:
        """Clean up old job execution records"""
        cutoff_date = datetime.now() - timedelta(days=self.job_execution_retention_days)
        
        query = """
            DELETE FROM water_infrastructure.job_executions 
            WHERE started_at < $1
        """
        
        async with pool.acquire() as conn:
            result = await conn.execute(query, cutoff_date)
            # Extract the number from the result string like "DELETE 42"
            return int(result.split()[-1]) if result.split() else 0
    
    async def _cleanup_performance_metrics(self, pool) -> int:
        """Clean up old performance metrics records"""
        cutoff_date = datetime.now() - timedelta(days=self.performance_metrics_retention_days)
        
        query = """
            DELETE FROM water_infrastructure.model_performance_metrics 
            WHERE calculated_at < $1
        """
        
        async with pool.acquire() as conn:
            try:
                result = await conn.execute(query, cutoff_date)
                return int(result.split()[-1]) if result.split() else 0
            except Exception:
                # Table might not exist yet
                return 0
    
    async def _vacuum_tables(self, pool):
        """Run vacuum analyze on cleaned tables to reclaim space and update statistics"""
        tables_to_vacuum = [
            "water_infrastructure.ml_predictions",
            "water_infrastructure.job_executions",
            "water_infrastructure.model_performance_metrics"
        ]
        
        async with pool.acquire() as conn:
            for table in tables_to_vacuum:
                try:
                    await conn.execute(f"VACUUM ANALYZE {table}")
                    self.logger.debug(f"Vacuumed table: {table}")
                except Exception as e:
                    # Table might not exist, continue with others
                    self.logger.debug(f"Could not vacuum {table}: {e}")
    
    async def _analyze_disk_usage(self, pool) -> Dict[str, Any]:
        """Analyze disk usage of key tables"""
        usage_query = """
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
            FROM pg_tables 
            WHERE schemaname = 'water_infrastructure'
            AND tablename IN ('ml_predictions', 'job_executions', 'model_performance_metrics')
            ORDER BY size_bytes DESC
        """
        
        async with pool.acquire() as conn:
            try:
                rows = await conn.fetch(usage_query)
                return {
                    row['tablename']: {
                        "size": row['size'],
                        "size_bytes": row['size_bytes']
                    }
                    for row in rows
                }
            except Exception:
                return {}


async def main():
    """Run cleanup job"""
    job = CleanupJob()
    success = await job.run()
    
    if not success:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())