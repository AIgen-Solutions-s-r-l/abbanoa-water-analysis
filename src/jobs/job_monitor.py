"""Job monitoring and alerting system"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.jobs.base_job import BaseJob


class JobMonitor(BaseJob):
    """Monitor job health and send alerts for failures or performance issues"""
    
    def __init__(self):
        super().__init__(
            job_name="job_monitor",
            timeout_minutes=10
        )
        # Monitoring thresholds
        self.max_failure_rate = 0.2  # 20% failure rate triggers alert
        self.max_avg_duration_multiplier = 2.0  # 2x average duration triggers alert
        self.stale_job_threshold_hours = 25  # Job not run in 25 hours is stale (for daily jobs)
        
        # Expected job schedules (in hours)
        self.expected_schedules = {
            "prediction_reconciliation": 1,  # Every hour
            "batch_prediction": 6,  # Every 6 hours  
            "daily_cleanup": 24  # Daily
        }
    
    async def execute(self, pool) -> Dict[str, Any]:
        """Monitor all jobs and generate alerts"""
        self.logger.info("Starting job monitoring")
        
        monitoring_results = {}
        alerts_sent = 0
        
        # Get job execution statistics
        job_stats = await self._get_job_statistics(pool)
        monitoring_results["job_statistics"] = job_stats
        
        # Check for job failures
        failure_alerts = await self._check_job_failures(job_stats)
        monitoring_results["failure_alerts"] = failure_alerts
        alerts_sent += len(failure_alerts)
        
        # Check for performance degradation
        performance_alerts = await self._check_performance_issues(job_stats)
        monitoring_results["performance_alerts"] = performance_alerts  
        alerts_sent += len(performance_alerts)
        
        # Check for stale jobs (jobs that should have run but didn't)
        stale_alerts = await self._check_stale_jobs(job_stats)
        monitoring_results["stale_alerts"] = stale_alerts
        alerts_sent += len(stale_alerts)
        
        # Check database health
        db_health = await self._check_database_health(pool)
        monitoring_results["database_health"] = db_health
        
        # Generate summary report
        health_summary = self._generate_health_summary(monitoring_results)
        monitoring_results["health_summary"] = health_summary
        
        self.logger.info(f"Monitoring completed: {alerts_sent} alerts sent, overall status: {health_summary['status']}")
        
        return {
            "status": "success",
            "alerts_sent": alerts_sent,
            "monitoring_results": monitoring_results
        }
    
    async def _get_job_statistics(self, pool) -> Dict[str, Any]:
        """Get job execution statistics for the last 24 hours"""
        stats_query = """
            SELECT 
                job_name,
                COUNT(*) as total_executions,
                COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_executions,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_executions,
                COUNT(CASE WHEN status = 'timeout' THEN 1 END) as timeout_executions,
                AVG(duration_seconds) as avg_duration_seconds,
                MAX(duration_seconds) as max_duration_seconds,
                MAX(started_at) as last_execution,
                MIN(started_at) as first_execution
            FROM water_infrastructure.job_executions 
            WHERE started_at > NOW() - INTERVAL '24 hours'
            GROUP BY job_name
        """
        
        async with pool.acquire() as conn:
            try:
                rows = await conn.fetch(stats_query)
                stats = {}
                
                for row in rows:
                    job_name = row['job_name']
                    total = row['total_executions']
                    failed = row['failed_executions'] + row['timeout_executions']
                    
                    stats[job_name] = {
                        "total_executions": total,
                        "successful_executions": row['successful_executions'],
                        "failed_executions": failed,
                        "failure_rate": failed / total if total > 0 else 0,
                        "avg_duration_seconds": float(row['avg_duration_seconds']) if row['avg_duration_seconds'] else 0,
                        "max_duration_seconds": row['max_duration_seconds'],
                        "last_execution": row['last_execution'],
                        "first_execution": row['first_execution']
                    }
                
                return stats
                
            except Exception as e:
                self.logger.error(f"Failed to get job statistics: {e}")
                return {}
    
    async def _check_job_failures(self, job_stats: Dict[str, Any]) -> List[str]:
        """Check for jobs with high failure rates"""
        alerts = []
        
        for job_name, stats in job_stats.items():
            failure_rate = stats.get("failure_rate", 0)
            
            if failure_rate > self.max_failure_rate:
                message = (
                    f"Job {job_name} has high failure rate: {failure_rate:.1%} "
                    f"({stats['failed_executions']}/{stats['total_executions']} failed)"
                )
                
                await self.send_alert(message, severity="critical")
                alerts.append(message)
                
        return alerts
    
    async def _check_performance_issues(self, job_stats: Dict[str, Any]) -> List[str]:
        """Check for jobs with performance degradation"""
        alerts = []
        
        # Get historical averages for comparison
        historical_averages = await self._get_historical_averages()
        
        for job_name, stats in job_stats.items():
            current_avg = stats.get("avg_duration_seconds", 0)
            historical_avg = historical_averages.get(job_name, current_avg)
            
            if historical_avg > 0 and current_avg > historical_avg * self.max_avg_duration_multiplier:
                message = (
                    f"Job {job_name} performance degraded: "
                    f"current avg {current_avg:.0f}s vs historical {historical_avg:.0f}s "
                    f"({current_avg/historical_avg:.1f}x slower)"
                )
                
                await self.send_alert(message, severity="warning")
                alerts.append(message)
                
        return alerts
    
    async def _check_stale_jobs(self, job_stats: Dict[str, Any]) -> List[str]:
        """Check for jobs that should have run but didn't"""
        alerts = []
        now = datetime.now()
        
        for job_name, expected_interval_hours in self.expected_schedules.items():
            if job_name not in job_stats:
                # Job never executed
                message = f"Job {job_name} has never been executed"
                await self.send_alert(message, severity="critical")
                alerts.append(message)
                continue
            
            last_execution = job_stats[job_name].get("last_execution")
            if not last_execution:
                continue
                
            hours_since_last = (now - last_execution).total_seconds() / 3600
            
            # Allow some buffer (1.5x the expected interval)
            max_allowed_hours = expected_interval_hours * 1.5
            
            if hours_since_last > max_allowed_hours:
                message = (
                    f"Job {job_name} is stale: last run {hours_since_last:.1f} hours ago "
                    f"(expected every {expected_interval_hours} hours)"
                )
                
                await self.send_alert(message, severity="warning")
                alerts.append(message)
                
        return alerts
    
    async def _get_historical_averages(self) -> Dict[str, float]:
        """Get historical average durations for jobs (last 7 days, excluding last 24 hours)"""
        try:
            historical_query = """
                SELECT 
                    job_name,
                    AVG(duration_seconds) as historical_avg
                FROM water_infrastructure.job_executions 
                WHERE started_at BETWEEN NOW() - INTERVAL '7 days' AND NOW() - INTERVAL '24 hours'
                AND status = 'success'
                AND duration_seconds IS NOT NULL
                GROUP BY job_name
            """
            
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(historical_query)
                return {
                    row['job_name']: float(row['historical_avg'])
                    for row in rows
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get historical averages: {e}")
            return {}
    
    async def _check_database_health(self, pool) -> Dict[str, Any]:
        """Check database health and connection pool status"""
        health = {
            "connection_pool_size": pool.get_size(),
            "available_connections": pool.get_size() - pool.get_idle_size(),
            "table_sizes": {},
            "last_vacuum": {}
        }
        
        try:
            # Check table sizes
            size_query = """
                SELECT 
                    tablename,
                    pg_size_pretty(pg_total_relation_size('water_infrastructure.'||tablename)) as size
                FROM pg_tables 
                WHERE schemaname = 'water_infrastructure'
                AND tablename IN ('ml_predictions', 'job_executions', 'sensor_readings')
            """
            
            async with pool.acquire() as conn:
                rows = await conn.fetch(size_query)
                health["table_sizes"] = {row['tablename']: row['size'] for row in rows}
                
        except Exception as e:
            self.logger.error(f"Failed to check database health: {e}")
            health["error"] = str(e)
            
        return health
    
    def _generate_health_summary(self, monitoring_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall health summary"""
        total_alerts = (
            len(monitoring_results.get("failure_alerts", [])) +
            len(monitoring_results.get("performance_alerts", [])) +
            len(monitoring_results.get("stale_alerts", []))
        )
        
        if total_alerts == 0:
            status = "healthy"
        elif total_alerts <= 2:
            status = "warning"
        else:
            status = "critical"
            
        return {
            "status": status,
            "total_alerts": total_alerts,
            "monitored_jobs": len(monitoring_results.get("job_statistics", {})),
            "timestamp": datetime.now().isoformat()
        }


async def main():
    """Run job monitoring"""
    monitor = JobMonitor()
    success = await monitor.run()
    
    if not success:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())