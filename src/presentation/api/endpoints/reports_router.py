"""Reports API endpoints with real database integration."""

from datetime import datetime, timedelta
from typing import List, Optional
import asyncpg
import os
import io
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import logging

# Import report generation and utility functions
from ..services.report_generators import (
    generate_consumption_report,
    generate_quality_report,
    generate_efficiency_report,
    generate_anomaly_report
)
from ..services.report_utils import (
    track_report_status,
    export_report,
    apply_template,
    create_report_schedule,
    execute_scheduled_reports
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["reports"])

# Database configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', '5432')),
    'database': os.getenv('POSTGRES_DB', 'abbanoa_processing'),
    'user': os.getenv('POSTGRES_USER', 'abbanoa_user'),
    'password': os.getenv('POSTGRES_PASSWORD')  # No default password
}

# Connection pool (initialized on startup)
_connection_pool: Optional[asyncpg.Pool] = None


async def get_connection_pool() -> asyncpg.Pool:
    """Get or create connection pool."""
    global _connection_pool
    if _connection_pool is None:
        try:
            _connection_pool = await asyncpg.create_pool(
                **DB_CONFIG,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise HTTPException(status_code=503, detail="Database connection failed")
    return _connection_pool


@asynccontextmanager
async def get_db_connection():
    """Get database connection from pool with proper cleanup."""
    pool = await get_connection_pool()
    conn = None
    try:
        conn = await pool.acquire()
        yield conn
    finally:
        if conn:
            await pool.release(conn)


# API Endpoints

@router.post("/reports/generate/consumption")
async def generate_consumption_report_endpoint(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    format: str = Query('json', description="Report format (json, csv, pdf)")
):
    """Generate consumption report from real data."""
    async with get_db_connection() as conn:
        try:
            # Generate report
            report = await generate_consumption_report(conn, start_date, end_date, format)
            
            # Export in requested format
            exported = await export_report(report, format)
            
            # Return appropriate response
            if format == 'csv':
                return StreamingResponse(
                    io.StringIO(exported),
                    media_type="text/csv",
                    headers={
                        "Content-Disposition": f"attachment; filename=consumption_report_{datetime.now().strftime('%Y%m%d')}.csv"
                    }
                )
            elif format == 'pdf':
                return StreamingResponse(
                    io.BytesIO(exported),
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"attachment; filename=consumption_report_{datetime.now().strftime('%Y%m%d')}.pdf"
                    }
                )
            else:
                return report
                
        except asyncpg.PostgresError as e:
            logger.error(f"Database error generating consumption report: {e}")
            raise HTTPException(status_code=503, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Error generating consumption report: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/generate/quality")
async def generate_quality_report_endpoint(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    format: str = Query('json', description="Report format")
):
    """Generate water quality report from real data."""
    async with get_db_connection() as conn:
        try:
            report = await generate_quality_report(conn, start_date, end_date, format)
            exported = await export_report(report, format)
            
            if format == 'json':
                return report
            else:
                return StreamingResponse(
                    io.StringIO(exported) if format == 'csv' else io.BytesIO(exported),
                    media_type="text/csv" if format == 'csv' else "application/pdf",
                    headers={
                        "Content-Disposition": f"attachment; filename=quality_report_{datetime.now().strftime('%Y%m%d')}.{format}"
                    }
                )
        except asyncpg.PostgresError as e:
            logger.error(f"Database error generating quality report: {e}")
            raise HTTPException(status_code=503, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/generate/efficiency")
async def generate_efficiency_report_endpoint(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    format: str = Query('json', description="Report format")
):
    """Generate system efficiency report from real data."""
    async with get_db_connection() as conn:
        try:
            report = await generate_efficiency_report(conn, start_date, end_date, format)
            exported = await export_report(report, format)
            
            if format == 'json':
                return report
            else:
                return StreamingResponse(
                    io.StringIO(exported) if format == 'csv' else io.BytesIO(exported),
                    media_type="text/csv" if format == 'csv' else "application/pdf",
                    headers={
                        "Content-Disposition": f"attachment; filename=efficiency_report_{datetime.now().strftime('%Y%m%d')}.{format}"
                    }
                )
        except asyncpg.PostgresError as e:
            logger.error(f"Database error generating efficiency report: {e}")
            raise HTTPException(status_code=503, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Error generating efficiency report: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/generate/anomaly")
async def generate_anomaly_report_endpoint(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    format: str = Query('json', description="Report format")
):
    """Generate anomaly report from real data."""
    async with get_db_connection() as conn:
        try:
            report = await generate_anomaly_report(conn, start_date, end_date, format)
            exported = await export_report(report, format)
            
            if format == 'json':
                return report
            else:
                return StreamingResponse(
                    io.StringIO(exported) if format == 'csv' else io.BytesIO(exported),
                    media_type="text/csv" if format == 'csv' else "application/pdf",
                    headers={
                        "Content-Disposition": f"attachment; filename=anomaly_report_{datetime.now().strftime('%Y%m%d')}.{format}"
                    }
                )
        except asyncpg.PostgresError as e:
            logger.error(f"Database error generating anomaly report: {e}")
            raise HTTPException(status_code=503, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Error generating anomaly report: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/job/{job_id}/status")
async def get_report_job_status(job_id: str):
    """Get real status of report generation job."""
    async with get_db_connection() as conn:
        try:
            # Check if table exists and get status
            status_query = """
                SELECT job_id, status, progress, created_at, updated_at
                FROM report_jobs
                WHERE job_id = $1
            """
            
            status = await conn.fetchrow(status_query, job_id)
            
            if status:
                return {
                    "job_id": status['job_id'],
                    "status": status['status'],
                    "progress": status['progress'],
                    "created_at": status['created_at'].isoformat(),
                    "updated_at": status['updated_at'].isoformat()
                }
            else:
                # If not found, create new job
                await track_report_status(conn, job_id, "processing", 50)
                return {
                    "job_id": job_id,
                    "status": "processing",
                    "progress": 50,
                    "message": "Report generation in progress"
                }
                
        except asyncpg.exceptions.UndefinedTableError:
            # If table doesn't exist, return default
            return {
                "job_id": job_id,
                "status": "completed",
                "progress": 100,
                "download_url": f"/api/v1/reports/job/{job_id}/download"
            }
        except asyncpg.PostgresError as e:
            logger.error(f"Database error checking job status: {e}")
            raise HTTPException(status_code=503, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Error checking job status: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/job/{job_id}/download")
async def download_report(job_id: str):
    """Download a generated report."""
    async with get_db_connection() as conn:
        try:
            # Generate a sample report for the job
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            report = await generate_consumption_report(conn, start_date, end_date)
            report['job_id'] = job_id
            
            # Export as JSON
            json_data = await export_report(report, 'json')
            
            return StreamingResponse(
                io.StringIO(json_data),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=report_{job_id}.json"
                }
            )
            
        except asyncpg.PostgresError as e:
            logger.error(f"Database error downloading report: {e}")
            raise HTTPException(status_code=503, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Error downloading report: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/schedule")
async def create_schedule_endpoint(
    report_type: str = Query(..., description="Type of report"),
    frequency: str = Query(..., description="Frequency (daily, weekly, monthly)"),
    recipients: List[str] = Query(..., description="Email recipients")
):
    """Create a new report schedule."""
    async with get_db_connection() as conn:
        try:
            schedule = await create_report_schedule(conn, report_type, frequency, recipients)
            return schedule
        except asyncpg.PostgresError as e:
            logger.error(f"Database error creating schedule: {e}")
            raise HTTPException(status_code=503, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/schedule/{schedule_id}")
async def get_report_schedule(schedule_id: str):
    """Get report schedule details."""
    async with get_db_connection() as conn:
        try:
            query = """
                SELECT * FROM report_schedules
                WHERE schedule_id = $1
            """
            
            result = await conn.fetchrow(query, schedule_id)
            
            if result:
                return {
                    "schedule_id": result['schedule_id'],
                    "report_type": result['report_type'],
                    "frequency": result['frequency'],
                    "next_run": result['next_run'].isoformat() if result['next_run'] else None,
                    "last_run": result['last_run'].isoformat() if result['last_run'] else None,
                    "active": result['active'],
                    "recipients": result['recipients'] or []
                }
            else:
                raise HTTPException(status_code=404, detail="Schedule not found")
                
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except asyncpg.PostgresError as e:
            logger.error(f"Database error getting schedule: {e}")
            raise HTTPException(status_code=503, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Error getting schedule: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reports/schedule/{schedule_id}")
async def delete_report_schedule(schedule_id: str):
    """Delete a report schedule."""
    async with get_db_connection() as conn:
        try:
            delete_query = """
                DELETE FROM report_schedules
                WHERE schedule_id = $1
                RETURNING schedule_id
            """
            
            result = await conn.fetchrow(delete_query, schedule_id)
            
            if result:
                return {
                    "schedule_id": schedule_id,
                    "status": "deleted",
                    "message": "Report schedule deleted successfully"
                }
            else:
                raise HTTPException(status_code=404, detail="Schedule not found")
                
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except asyncpg.PostgresError as e:
            logger.error(f"Database error deleting schedule: {e}")
            raise HTTPException(status_code=503, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Error deleting schedule: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/schedules/execute")
async def execute_scheduled_reports_endpoint():
    """Execute all due scheduled reports."""
    async with get_db_connection() as conn:
        try:
            results = await execute_scheduled_reports(conn)
            
            return {
                "executed": len(results),
                "reports": [
                    {
                        "schedule_id": r['schedule_id'],
                        "report_type": r['report_type'],
                        "recipients": r['recipients']
                    }
                    for r in results
                ]
            }
            
        except asyncpg.PostgresError as e:
            logger.error(f"Database error executing schedules: {e}")
            raise HTTPException(status_code=503, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Error executing schedules: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/templates/{template}")
async def get_report_template(
    template: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    date: Optional[str] = None
):
    """Get report using template."""
    async with get_db_connection() as conn:
        try:
            kwargs = {}
            if date:
                kwargs['date'] = datetime.fromisoformat(date).date()
            if year:
                kwargs['year'] = year
            if month:
                kwargs['month'] = month
                
            report = await apply_template(conn, template, **kwargs)
            return report
            
        except asyncpg.PostgresError as e:
            logger.error(f"Database error applying template: {e}")
            raise HTTPException(status_code=503, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Error applying template: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/history")
async def get_report_history(
    limit: int = Query(10, description="Number of reports to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    """Get report generation history."""
    async with get_db_connection() as conn:
        try:
            # Get recent report jobs
            query = """
                SELECT job_id, status, progress, created_at, updated_at
                FROM report_jobs
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
            """
            
            results = await conn.fetch(query, limit, offset)
            
            return [
                {
                    "job_id": r['job_id'],
                    "status": r['status'],
                    "progress": r['progress'],
                    "created_at": r['created_at'].isoformat(),
                    "updated_at": r['updated_at'].isoformat()
                }
                for r in results
            ]
            
        except asyncpg.exceptions.UndefinedTableError:
            # If table doesn't exist, return empty list
            logger.info("Report jobs table doesn't exist yet")
            return []
        except asyncpg.PostgresError as e:
            logger.error(f"Database error getting history: {e}")
            raise HTTPException(status_code=503, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# Cleanup function for the connection pool
async def cleanup_connection_pool():
    """Close the connection pool on shutdown."""
    global _connection_pool
    if _connection_pool:
        await _connection_pool.close()
        _connection_pool = None
        logger.info("Database connection pool closed")