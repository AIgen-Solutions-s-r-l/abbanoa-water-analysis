"""Report utility functions for scheduling, exporting, and templates."""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import asyncpg
import json
import csv
import io
import uuid


async def track_report_status(
    conn: asyncpg.Connection,
    job_id: str,
    status: str,
    progress: int
) -> None:
    """Track report generation status in database."""
    
    # Create reports table if not exists
    create_table_query = """
        CREATE TABLE IF NOT EXISTS report_jobs (
            job_id VARCHAR(50) PRIMARY KEY,
            status VARCHAR(20),
            progress INTEGER,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """
    await conn.execute(create_table_query)
    
    # Update or insert status
    upsert_query = """
        INSERT INTO report_jobs (job_id, status, progress, updated_at)
        VALUES ($1, $2, $3, NOW())
        ON CONFLICT (job_id) DO UPDATE 
        SET status = $2, progress = $3, updated_at = NOW()
    """
    await conn.execute(upsert_query, job_id, status, progress)


async def export_report(
    report_data: Dict[str, Any],
    format: str = 'json'
) -> Any:
    """Export report in specified format."""
    
    if format == 'json':
        return json.dumps(report_data, indent=2)
    
    elif format == 'csv':
        # Flatten report data for CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers and values
        for key, value in report_data.items():
            if not isinstance(value, (list, dict)):
                writer.writerow([key, value])
        
        return output.getvalue()
    
    elif format == 'pdf':
        # For PDF, return mock bytes (real implementation would use reportlab)
        pdf_content = f"PDF Report\n{json.dumps(report_data, indent=2)}".encode()
        return pdf_content
    
    else:
        return json.dumps(report_data, indent=2)


async def apply_template(
    conn: asyncpg.Connection,
    template: str,
    **kwargs
) -> Dict[str, Any]:
    """Apply report template."""
    
    from .report_generators import generate_consumption_report, generate_efficiency_report
    
    templates = {
        'daily_consumption': {
            'report_type': 'daily_consumption',
            'sections': {
                'summary': 'Daily consumption overview',
                'hourly_breakdown': 'Hour-by-hour consumption',
                'peak_usage': 'Peak usage periods',
                'node_performance': 'Node-level metrics'
            }
        },
        'monthly_summary': {
            'report_type': 'monthly_summary',
            'sections': {
                'consumption_trends': 'Monthly consumption trends',
                'efficiency_metrics': 'System efficiency analysis',
                'cost_analysis': 'Cost breakdown',
                'anomaly_summary': 'Detected issues',
                'recommendations': 'Optimization recommendations'
            }
        },
        'weekly_quality': {
            'report_type': 'weekly_quality',
            'sections': {
                'compliance_summary': 'Quality compliance overview',
                'parameter_trends': 'Parameter trend analysis',
                'violations': 'Quality violations',
                'sampling_coverage': 'Sampling coverage map'
            }
        }
    }
    
    template_config = templates.get(template, templates['daily_consumption'])
    
    # Add dynamic data based on template
    if template == 'daily_consumption' and 'date' in kwargs:
        date = kwargs['date']
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        
        # Get actual data for the day
        consumption_data = await generate_consumption_report(conn, start, end)
        template_config['data'] = consumption_data
    
    elif template == 'monthly_summary' and 'year' in kwargs and 'month' in kwargs:
        year = kwargs['year']
        month = kwargs['month']
        start = datetime(year, month, 1)
        # Calculate last day of month
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # Get multiple report types for monthly summary
        consumption = await generate_consumption_report(conn, start, end)
        efficiency = await generate_efficiency_report(conn, start, end)
        template_config['data'] = {
            'consumption': consumption,
            'efficiency': efficiency
        }
    
    return template_config


async def create_report_schedule(
    conn: asyncpg.Connection,
    report_type: str,
    frequency: str,
    recipients: List[str]
) -> Dict[str, Any]:
    """Create a scheduled report."""
    
    schedule_id = f"SCH_{uuid.uuid4().hex[:8].upper()}"
    
    # Create schedules table if not exists
    create_table_query = """
        CREATE TABLE IF NOT EXISTS report_schedules (
            schedule_id VARCHAR(50) PRIMARY KEY,
            report_type VARCHAR(50),
            frequency VARCHAR(20),
            recipients TEXT[],
            active BOOLEAN DEFAULT TRUE,
            last_run TIMESTAMP,
            next_run TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """
    await conn.execute(create_table_query)
    
    # Calculate next run time
    next_run = datetime.now()
    if frequency == 'daily':
        next_run += timedelta(days=1)
    elif frequency == 'weekly':
        next_run += timedelta(weeks=1)
    elif frequency == 'monthly':
        next_run += timedelta(days=30)
    
    # Insert schedule
    insert_query = """
        INSERT INTO report_schedules (schedule_id, report_type, frequency, recipients, next_run)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING schedule_id, active
    """
    
    result = await conn.fetchrow(
        insert_query,
        schedule_id,
        report_type,
        frequency,
        recipients,
        next_run
    )
    
    return {
        'schedule_id': result['schedule_id'],
        'report_type': report_type,
        'frequency': frequency,
        'recipients': recipients,
        'active': result['active'],
        'next_run': next_run.isoformat()
    }


async def execute_scheduled_reports(
    conn: asyncpg.Connection
) -> List[Dict[str, Any]]:
    """Execute all due scheduled reports."""
    
    from .report_generators import (
        generate_consumption_report,
        generate_quality_report,
        generate_efficiency_report
    )
    
    # Get due schedules
    schedules_query = """
        SELECT * FROM report_schedules
        WHERE active = TRUE
            AND (next_run IS NULL OR next_run <= NOW())
    """
    
    schedules = await conn.fetch(schedules_query)
    
    results = []
    for schedule in schedules:
        # Generate report based on type
        end_date = datetime.now()
        if schedule['frequency'] == 'daily':
            start_date = end_date - timedelta(days=1)
        elif schedule['frequency'] == 'weekly':
            start_date = end_date - timedelta(weeks=1)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Generate appropriate report
        if 'consumption' in schedule['report_type']:
            report = await generate_consumption_report(conn, start_date, end_date)
        elif 'quality' in schedule['report_type']:
            report = await generate_quality_report(conn, start_date, end_date)
        elif 'efficiency' in schedule['report_type']:
            report = await generate_efficiency_report(conn, start_date, end_date)
        else:
            report = await generate_consumption_report(conn, start_date, end_date)
        
        # Update last run and next run
        if schedule['frequency'] == 'daily':
            next_run = datetime.now() + timedelta(days=1)
        elif schedule['frequency'] == 'weekly':
            next_run = datetime.now() + timedelta(weeks=1)
        else:
            next_run = datetime.now() + timedelta(days=30)
        
        update_query = """
            UPDATE report_schedules
            SET last_run = NOW(), next_run = $2
            WHERE schedule_id = $1
        """
        await conn.execute(update_query, schedule['schedule_id'], next_run)
        
        results.append({
            'schedule_id': schedule['schedule_id'],
            'report_type': schedule['report_type'],
            'report': report,
            'recipients': schedule['recipients']
        })
    
    return results