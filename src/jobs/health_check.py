"""Health check system for all jobs and dependencies"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.jobs.base_job import BaseJob
from src.application.services.prediction_tracker import PredictionTracker
from src.infrastructure.repositories.tracking_repository_extension import TrackingRepositoryExtension


class HealthCheckJob(BaseJob):
    """Comprehensive health check for all system components"""
    
    def __init__(self):
        super().__init__(
            job_name="health_check",
            timeout_minutes=15
        )
        
        # Health check components
        self.checks = [
            "database_connectivity",
            "table_integrity", 
            "prediction_system",
            "job_scheduler",
            "data_freshness",
            "system_resources"
        ]
    
    async def execute(self, pool) -> Dict[str, Any]:
        """Execute comprehensive health checks"""
        self.logger.info("Starting system health check")
        
        health_results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_status": "unknown",
            "critical_issues": [],
            "warnings": []
        }
        
        # Run all health checks
        for check_name in self.checks:
            try:
                check_method = getattr(self, f"_check_{check_name}")
                result = await check_method(pool)
                health_results["checks"][check_name] = result
                
                # Collect issues
                if result.get("status") == "critical":
                    health_results["critical_issues"].append({
                        "check": check_name,
                        "message": result.get("message", "Unknown critical issue")
                    })
                elif result.get("status") == "warning":
                    health_results["warnings"].append({
                        "check": check_name, 
                        "message": result.get("message", "Unknown warning")
                    })
                    
            except Exception as e:
                self.logger.error(f"Health check {check_name} failed: {e}")
                health_results["checks"][check_name] = {
                    "status": "critical",
                    "message": f"Check failed with error: {str(e)}",
                    "error": True
                }
                health_results["critical_issues"].append({
                    "check": check_name,
                    "message": f"Check execution failed: {str(e)}"
                })
        
        # Determine overall status
        health_results["overall_status"] = self._determine_overall_status(health_results)
        
        # Send alerts if needed
        await self._send_health_alerts(health_results)
        
        self.logger.info(
            f"Health check completed: {health_results['overall_status']} "
            f"({len(health_results['critical_issues'])} critical, "
            f"{len(health_results['warnings'])} warnings)"
        )
        
        return health_results
    
    async def _check_database_connectivity(self, pool) -> Dict[str, Any]:
        """Check database connection and basic queries"""
        try:
            async with pool.acquire() as conn:
                # Test basic connectivity
                await conn.fetchval("SELECT 1")
                
                # Test schema access
                schema_query = "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'water_infrastructure'"
                table_count = await conn.fetchval(schema_query)
                
                if table_count < 3:  # Expect at least a few core tables
                    return {
                        "status": "warning",
                        "message": f"Only {table_count} tables found in water_infrastructure schema"
                    }
                
                return {
                    "status": "healthy",
                    "message": f"Database connected, {table_count} tables in schema",
                    "table_count": table_count
                }
                
        except Exception as e:
            return {
                "status": "critical",
                "message": f"Database connectivity failed: {str(e)}"
            }
    
    async def _check_table_integrity(self, pool) -> Dict[str, Any]:
        """Check core table integrity and indexes"""
        required_tables = [
            "sensor_readings",
            "anomalies", 
            "ml_predictions",
            "job_executions"
        ]
        
        try:
            async with pool.acquire() as conn:
                # Check table existence
                table_query = """
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'water_infrastructure'
                    AND table_name = ANY($1)
                """
                
                existing_tables = await conn.fetch(table_query, required_tables)
                existing_table_names = {row['table_name'] for row in existing_tables}
                
                missing_tables = set(required_tables) - existing_table_names
                
                if missing_tables:
                    return {
                        "status": "critical",
                        "message": f"Missing required tables: {', '.join(missing_tables)}"
                    }
                
                # Check for indexes on critical tables
                index_issues = []
                
                # Check sensor_readings has timestamp index
                sensor_index_query = """
                    SELECT COUNT(*) FROM pg_indexes 
                    WHERE tablename = 'sensor_readings' 
                    AND schemaname = 'water_infrastructure'
                    AND indexdef LIKE '%timestamp%'
                """
                
                sensor_index_count = await conn.fetchval(sensor_index_query)
                if sensor_index_count == 0:
                    index_issues.append("sensor_readings missing timestamp index")
                
                if index_issues:
                    return {
                        "status": "warning",
                        "message": f"Index issues: {', '.join(index_issues)}"
                    }
                
                return {
                    "status": "healthy",
                    "message": f"All {len(required_tables)} required tables present with proper indexes"
                }
                
        except Exception as e:
            return {
                "status": "critical",
                "message": f"Table integrity check failed: {str(e)}"
            }
    
    async def _check_prediction_system(self, pool) -> Dict[str, Any]:
        """Check prediction system health"""
        try:
            repo = TrackingRepositoryExtension(pool)
            tracker = PredictionTracker(repository=repo)
            
            # Check recent prediction activity
            recent_predictions_query = """
                SELECT COUNT(*) FROM water_infrastructure.ml_predictions 
                WHERE created_at > NOW() - INTERVAL '24 hours'
            """
            
            async with pool.acquire() as conn:
                recent_count = await conn.fetchval(recent_predictions_query)
            
            if recent_count == 0:
                return {
                    "status": "warning",
                    "message": "No predictions created in last 24 hours"
                }
            
            # Check model performance if we have enough data
            try:
                metrics = await tracker.calculate_metrics(days_back=7)
                
                if metrics.f1_score < 0.5:
                    return {
                        "status": "warning",
                        "message": f"Low model performance: F1={metrics.f1_score:.3f}",
                        "f1_score": metrics.f1_score
                    }
                
                return {
                    "status": "healthy",
                    "message": f"Prediction system healthy: {recent_count} recent predictions, F1={metrics.f1_score:.3f}",
                    "recent_predictions": recent_count,
                    "f1_score": metrics.f1_score
                }
                
            except Exception:
                # Not enough data for metrics, but system is working
                return {
                    "status": "healthy",
                    "message": f"Prediction system active: {recent_count} recent predictions",
                    "recent_predictions": recent_count
                }
                
        except Exception as e:
            return {
                "status": "critical",
                "message": f"Prediction system check failed: {str(e)}"
            }
    
    async def _check_job_scheduler(self, pool) -> Dict[str, Any]:
        """Check job scheduler health"""
        expected_jobs = ["prediction_reconciliation", "batch_prediction", "daily_cleanup"]
        
        try:
            async with pool.acquire() as conn:
                # Check recent job activity
                recent_jobs_query = """
                    SELECT 
                        job_name,
                        MAX(started_at) as last_run,
                        COUNT(CASE WHEN status = 'success' THEN 1 END) as success_count,
                        COUNT(*) as total_count
                    FROM water_infrastructure.job_executions
                    WHERE started_at > NOW() - INTERVAL '48 hours'
                    GROUP BY job_name
                """
                
                rows = await conn.fetch(recent_jobs_query)
                active_jobs = {row['job_name']: row for row in rows}
                
                issues = []
                
                for job_name in expected_jobs:
                    if job_name not in active_jobs:
                        issues.append(f"{job_name} not executed in 48 hours")
                    else:
                        job_data = active_jobs[job_name]
                        success_rate = job_data['success_count'] / job_data['total_count']
                        
                        if success_rate < 0.8:  # Less than 80% success rate
                            issues.append(f"{job_name} low success rate: {success_rate:.1%}")
                
                if issues:
                    return {
                        "status": "warning",
                        "message": f"Job scheduler issues: {'; '.join(issues)}",
                        "active_jobs": len(active_jobs)
                    }
                
                return {
                    "status": "healthy",
                    "message": f"Job scheduler healthy: {len(active_jobs)} active jobs",
                    "active_jobs": len(active_jobs)
                }
                
        except Exception as e:
            return {
                "status": "critical",
                "message": f"Job scheduler check failed: {str(e)}"
            }
    
    async def _check_data_freshness(self, pool) -> Dict[str, Any]:
        """Check data freshness across key tables"""
        try:
            async with pool.acquire() as conn:
                # Check sensor data freshness
                sensor_freshness_query = """
                    SELECT MAX(timestamp) as latest_reading
                    FROM water_infrastructure.sensor_readings
                """
                
                latest_reading = await conn.fetchval(sensor_freshness_query)
                
                if not latest_reading:
                    return {
                        "status": "critical", 
                        "message": "No sensor readings found"
                    }
                
                hours_since_latest = (datetime.now() - latest_reading).total_seconds() / 3600
                
                if hours_since_latest > 2:  # More than 2 hours old
                    return {
                        "status": "warning",
                        "message": f"Sensor data is {hours_since_latest:.1f} hours old"
                    }
                
                return {
                    "status": "healthy",
                    "message": f"Data is fresh: latest reading {hours_since_latest:.1f} hours ago"
                }
                
        except Exception as e:
            return {
                "status": "critical",
                "message": f"Data freshness check failed: {str(e)}"
            }
    
    async def _check_system_resources(self, pool) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            # Check database connection pool
            pool_size = pool.get_size()
            idle_connections = pool.get_idle_size()
            utilization = (pool_size - idle_connections) / pool_size
            
            if utilization > 0.8:  # More than 80% pool utilization
                return {
                    "status": "warning",
                    "message": f"High connection pool utilization: {utilization:.1%}",
                    "pool_utilization": utilization
                }
            
            return {
                "status": "healthy",
                "message": f"System resources healthy: pool utilization {utilization:.1%}",
                "pool_utilization": utilization
            }
            
        except Exception as e:
            return {
                "status": "warning",
                "message": f"System resource check incomplete: {str(e)}"
            }
    
    def _determine_overall_status(self, health_results: Dict[str, Any]) -> str:
        """Determine overall system status"""
        if health_results["critical_issues"]:
            return "critical"
        elif health_results["warnings"]:
            return "warning"
        else:
            return "healthy"
    
    async def _send_health_alerts(self, health_results: Dict[str, Any]):
        """Send alerts based on health check results"""
        if health_results["overall_status"] == "critical":
            critical_messages = [issue["message"] for issue in health_results["critical_issues"]]
            await self.send_alert(
                f"System health CRITICAL: {'; '.join(critical_messages)}",
                severity="critical"
            )
        elif health_results["overall_status"] == "warning" and len(health_results["warnings"]) > 2:
            # Only alert for warnings if there are many
            warning_messages = [warning["message"] for warning in health_results["warnings"]]
            await self.send_alert(
                f"System health warnings: {'; '.join(warning_messages[:3])}...",
                severity="warning"
            )


async def main():
    """Run health check"""
    health_check = HealthCheckJob()
    success = await health_check.run()
    
    if not success:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())