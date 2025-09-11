"""Base class for scheduled jobs"""

import asyncio
import sys
import os
import logging
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncpg
import json

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.repositories.tracking_repository_extension import TrackingRepositoryExtension

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/abbanoa-water-analysis/logs/jobs.log'),
        logging.StreamHandler()
    ]
)


class JobStatus:
    """Job status constants"""
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class BaseJob(ABC):
    """Base class for all scheduled jobs"""
    
    def __init__(self, job_name: str, timeout_minutes: int = 60):
        """Initialize base job
        
        Args:
            job_name: Name of the job
            timeout_minutes: Job timeout in minutes
        """
        self.job_name = job_name
        self.timeout_minutes = timeout_minutes
        self.logger = logging.getLogger(f"jobs.{job_name}")
        self.start_time = None
        self.end_time = None
        self.status = None
        self.error_message = None
        
        # Database configuration
        self.db_config = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", 5432)),
            "database": os.getenv("POSTGRES_DB", "abbanoa_processing"),
            "user": os.getenv("POSTGRES_USER", "abbanoa_user"),
            "password": os.getenv("POSTGRES_PASSWORD", "abbanoa_secure_pass"),
        }
    
    async def create_db_pool(self) -> asyncpg.Pool:
        """Create database connection pool"""
        return await asyncpg.create_pool(**self.db_config)
    
    async def log_job_execution(
        self, 
        pool: asyncpg.Pool, 
        status: str, 
        result: Optional[Dict] = None, 
        error: Optional[str] = None
    ):
        """Log job execution to database
        
        Args:
            pool: Database connection pool
            status: Job status
            result: Job result data
            error: Error message if failed
        """
        # Create job_executions table if not exists
        create_table = """
            CREATE TABLE IF NOT EXISTS water_infrastructure.job_executions (
                execution_id SERIAL PRIMARY KEY,
                job_name VARCHAR(100),
                started_at TIMESTAMP WITH TIME ZONE,
                completed_at TIMESTAMP WITH TIME ZONE,
                status VARCHAR(20),
                duration_seconds INTEGER,
                result JSONB,
                error_message TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_job_executions_job_time 
            ON water_infrastructure.job_executions(job_name, started_at DESC);
        """
        
        insert_query = """
            INSERT INTO water_infrastructure.job_executions 
            (job_name, started_at, completed_at, status, duration_seconds, result, error_message)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """
        
        duration = None
        if self.start_time and self.end_time:
            duration = int((self.end_time - self.start_time).total_seconds())
        
        async with pool.acquire() as conn:
            await conn.execute(create_table)
            await conn.execute(
                insert_query,
                self.job_name,
                self.start_time,
                self.end_time,
                status,
                duration,
                json.dumps(result) if result else None,
                error
            )
    
    async def send_alert(self, message: str, severity: str = "warning"):
        """Send alert for job failures
        
        Args:
            message: Alert message
            severity: Alert severity level
        """
        self.logger.error(f"ALERT [{severity.upper()}]: {message}")
        
        # In production, integrate with:
        # - Email notifications
        # - Slack/Teams webhooks  
        # - SMS alerts
        # - Monitoring systems (Grafana, etc)
    
    @abstractmethod
    async def execute(self, pool: asyncpg.Pool) -> Dict[str, Any]:
        """Execute the job logic
        
        Args:
            pool: Database connection pool
            
        Returns:
            Job execution result
        """
        pass
    
    async def run(self) -> bool:
        """Run the job with error handling and logging
        
        Returns:
            True if successful, False if failed
        """
        self.start_time = datetime.now()
        self.status = JobStatus.RUNNING
        
        self.logger.info(f"Starting job: {self.job_name}")
        
        pool = None
        try:
            # Create database connection
            pool = await self.create_db_pool()
            
            # Execute with timeout
            result = await asyncio.wait_for(
                self.execute(pool),
                timeout=self.timeout_minutes * 60
            )
            
            self.end_time = datetime.now()
            self.status = JobStatus.SUCCESS
            
            # Log success
            await self.log_job_execution(pool, self.status, result)
            
            self.logger.info(f"Job completed successfully: {self.job_name}")
            self.logger.info(f"Result: {result}")
            
            return True
            
        except asyncio.TimeoutError:
            self.end_time = datetime.now()
            self.status = JobStatus.TIMEOUT
            self.error_message = f"Job timed out after {self.timeout_minutes} minutes"
            
            self.logger.error(f"Job timed out: {self.job_name}")
            await self.send_alert(f"Job {self.job_name} timed out", "critical")
            
            if pool:
                await self.log_job_execution(pool, self.status, error=self.error_message)
            
            return False
            
        except Exception as e:
            self.end_time = datetime.now()
            self.status = JobStatus.FAILED
            self.error_message = str(e)
            
            self.logger.error(f"Job failed: {self.job_name} - {e}", exc_info=True)
            await self.send_alert(f"Job {self.job_name} failed: {e}", "critical")
            
            if pool:
                await self.log_job_execution(pool, self.status, error=self.error_message)
            
            return False
            
        finally:
            if pool:
                await pool.close()
    
    async def get_last_execution(self, pool: asyncpg.Pool) -> Optional[Dict]:
        """Get last execution details for this job
        
        Args:
            pool: Database connection pool
            
        Returns:
            Last execution details or None
        """
        query = """
            SELECT * FROM water_infrastructure.job_executions
            WHERE job_name = $1
            ORDER BY started_at DESC
            LIMIT 1
        """
        
        async with pool.acquire() as conn:
            try:
                row = await conn.fetchrow(query, self.job_name)
                return dict(row) if row else None
            except:
                # Table might not exist yet
                return None
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get job status summary
        
        Returns:
            Status summary dictionary
        """
        return {
            "job_name": self.job_name,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": int((self.end_time - self.start_time).total_seconds()) 
                               if self.start_time and self.end_time else None,
            "error_message": self.error_message
        }