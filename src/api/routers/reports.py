"""
Reports Generation API Router.

This router provides comprehensive endpoints for report generation and management,
supporting various report types and formats.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import asyncio
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import io
import json

from src.schemas.api.reports import (
    ComprehensiveReport,
    ReportTemplate,
    ReportGeneration,
    ReportSchedule,
    ReportHistory,
    ReportMetadata,
    ReportPeriod,
    ExecutiveSummary,
    PerformanceMetrics,
    NetworkAnalysis,
    QualityAssessment,
    AnomalyReport,
    ComplianceReport,
    FinancialImpact,
    MaintenanceReport,
    TrendAnalysis,
    ReportRecommendations,
    ReportAppendix,
    ErrorResponse
)
from src.infrastructure.data.hybrid_data_service import get_hybrid_data_service
from src.api.services.reports_service import (
    generate_comprehensive_report,
    generate_executive_summary,
    generate_performance_metrics,
    generate_network_analysis,
    generate_quality_assessment,
    generate_anomaly_report,
    generate_compliance_report,
    generate_financial_impact,
    generate_maintenance_report,
    generate_trend_analysis,
    generate_recommendations,
    generate_report_appendix,
    get_report_templates,
    create_report_schedule,
    get_report_history,
    export_report_to_format
)

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/comprehensive", response_model=ComprehensiveReport)
async def generate_comprehensive_report_endpoint(
    report_type: str = Query("system_overview", description="Type of report: system_overview, performance, quality, compliance"),
    period_start: str = Query(None, description="Report period start (ISO format)"),
    period_end: str = Query(None, description="Report period end (ISO format)"),
    time_range: str = Query("7d", description="Time range: 1d, 7d, 30d, 90d, 365d"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    include_recommendations: bool = Query(True, description="Include recommendations"),
    include_appendix: bool = Query(False, description="Include technical appendix"),
    format: str = Query("json", description="Report format: json, pdf, html")
):
    """
    Generate a comprehensive report with all sections.
    
    This endpoint creates detailed reports including executive summary,
    performance metrics, network analysis, and recommendations.
    """
    try:
        # Get hybrid data service
        hybrid_service = await get_hybrid_data_service()
        
        # Parse time period
        if period_start and period_end:
            start_time = datetime.fromisoformat(period_start)
            end_time = datetime.fromisoformat(period_end)
        else:
            start_time, end_time = _parse_time_range(time_range)
        
        # Generate comprehensive report
        report = await generate_comprehensive_report(
            hybrid_service=hybrid_service,
            report_type=report_type,
            start_time=start_time,
            end_time=end_time,
            selected_nodes=selected_nodes,
            include_recommendations=include_recommendations,
            include_appendix=include_appendix
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executive-summary", response_model=ExecutiveSummary)
async def get_executive_summary(
    time_range: str = Query("7d", description="Time range for summary"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get executive summary for the specified period."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        summary = await generate_executive_summary(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance-metrics", response_model=PerformanceMetrics)
async def get_performance_metrics(
    time_range: str = Query("7d", description="Time range for metrics"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get performance metrics for the specified period."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        metrics = await generate_performance_metrics(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network-analysis", response_model=NetworkAnalysis)
async def get_network_analysis(
    time_range: str = Query("7d", description="Time range for analysis"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get network analysis for the specified period."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        analysis = await generate_network_analysis(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality-assessment", response_model=QualityAssessment)
async def get_quality_assessment(
    time_range: str = Query("7d", description="Time range for assessment"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get quality assessment for the specified period."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        assessment = await generate_quality_assessment(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return assessment
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomaly-report", response_model=AnomalyReport)
async def get_anomaly_report(
    time_range: str = Query("7d", description="Time range for anomaly report"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get anomaly report for the specified period."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        report = await generate_anomaly_report(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance-report", response_model=ComplianceReport)
async def get_compliance_report(
    time_range: str = Query("30d", description="Time range for compliance report"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get compliance report for the specified period."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        report = await generate_compliance_report(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/financial-impact", response_model=FinancialImpact)
async def get_financial_impact(
    time_range: str = Query("30d", description="Time range for financial analysis"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get financial impact analysis for the specified period."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        impact = await generate_financial_impact(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return impact
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/maintenance-report", response_model=MaintenanceReport)
async def get_maintenance_report(
    time_range: str = Query("30d", description="Time range for maintenance report"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get maintenance report for the specified period."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        report = await generate_maintenance_report(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend-analysis", response_model=TrendAnalysis)
async def get_trend_analysis(
    time_range: str = Query("90d", description="Time range for trend analysis"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Get trend analysis for the specified period."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        analysis = await generate_trend_analysis(
            hybrid_service, start_time, end_time, selected_nodes
        )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations", response_model=ReportRecommendations)
async def get_recommendations(
    time_range: str = Query("7d", description="Time range for recommendations"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs"),
    priority_filter: Optional[str] = Query(None, description="Filter by priority: high, medium, low")
):
    """Get AI-generated recommendations based on system analysis."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        recommendations = await generate_recommendations(
            hybrid_service, start_time, end_time, selected_nodes, priority_filter
        )
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates", response_model=List[ReportTemplate])
async def get_report_templates():
    """Get available report templates."""
    try:
        templates = get_report_templates()
        return templates
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=Dict[str, str])
async def generate_report_async(
    background_tasks: BackgroundTasks,
    report_request: ReportGeneration
):
    """
    Generate a report asynchronously.
    
    This endpoint starts report generation in the background and returns
    a job ID that can be used to check status and download the report.
    """
    try:
        # Generate job ID
        job_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Start background task
        background_tasks.add_task(
            _generate_report_background,
            job_id,
            report_request
        )
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": "Report generation started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/job/{job_id}/status")
async def get_report_job_status(job_id: str):
    """Get the status of a report generation job."""
    try:
        # This would typically check a job queue or database
        # For now, return a mock status
        return {
            "job_id": job_id,
            "status": "completed",
            "progress": 100,
            "download_url": f"/api/v1/reports/job/{job_id}/download"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/job/{job_id}/download")
async def download_report(job_id: str):
    """Download a generated report."""
    try:
        # This would typically retrieve the report from storage
        # For now, return a mock JSON report
        mock_report = {
            "job_id": job_id,
            "generated_at": datetime.now().isoformat(),
            "report_type": "comprehensive",
            "data": "Mock report data"
        }
        
        # Convert to JSON string
        json_data = json.dumps(mock_report, indent=2)
        
        # Create streaming response
        return StreamingResponse(
            io.StringIO(json_data),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=report_{job_id}.json"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{report_type}")
async def export_report(
    report_type: str,
    format: str = Query("pdf", description="Export format: pdf, html, excel, csv"),
    time_range: str = Query("7d", description="Time range for report"),
    selected_nodes: Optional[List[str]] = Query(None, description="Selected node IDs")
):
    """Export a report in the specified format."""
    try:
        hybrid_service = await get_hybrid_data_service()
        start_time, end_time = _parse_time_range(time_range)
        
        # Generate report data
        report_data = await generate_comprehensive_report(
            hybrid_service=hybrid_service,
            report_type=report_type,
            start_time=start_time,
            end_time=end_time,
            selected_nodes=selected_nodes,
            include_recommendations=True,
            include_appendix=False
        )
        
        # Export to specified format
        exported_data = export_report_to_format(report_data, format)
        
        # Determine media type
        media_types = {
            "pdf": "application/pdf",
            "html": "text/html",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "csv": "text/csv"
        }
        
        media_type = media_types.get(format, "application/octet-stream")
        
        return StreamingResponse(
            io.BytesIO(exported_data),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename=report_{report_type}.{format}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule", response_model=Dict[str, str])
async def create_report_schedule_endpoint(schedule_request: ReportSchedule):
    """Create a scheduled report."""
    try:
        schedule_id = create_report_schedule(schedule_request)
        
        return {
            "schedule_id": schedule_id,
            "status": "created",
            "message": "Report schedule created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedule/{schedule_id}")
async def get_report_schedule(schedule_id: str):
    """Get report schedule details."""
    try:
        # This would typically retrieve from database
        # For now, return a mock schedule
        schedule = {
            "schedule_id": schedule_id,
            "report_template": "system_overview",
            "frequency": "weekly",
            "next_run": (datetime.now() + timedelta(days=7)).isoformat(),
            "active": True,
            "recipients": ["admin@company.com"],
            "delivery_method": "email"
        }
        
        return schedule
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/schedule/{schedule_id}")
async def delete_report_schedule(schedule_id: str):
    """Delete a report schedule."""
    try:
        # This would typically delete from database
        return {
            "schedule_id": schedule_id,
            "status": "deleted",
            "message": "Report schedule deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[ReportHistory])
async def get_report_history(
    limit: int = Query(10, description="Number of reports to return"),
    offset: int = Query(0, description="Offset for pagination"),
    report_type: Optional[str] = Query(None, description="Filter by report type")
):
    """Get report generation history."""
    try:
        history = get_report_history(limit, offset, report_type)
        return history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{report_id}")
async def get_report_details(report_id: str):
    """Get details of a specific report."""
    try:
        # This would typically retrieve from database
        # For now, return mock details
        details = {
            "report_id": report_id,
            "generated_at": datetime.now().isoformat(),
            "report_type": "comprehensive",
            "period_covered": "2024-01-01 to 2024-01-07",
            "file_size": 1024000,
            "status": "completed",
            "download_url": f"/api/v1/reports/job/{report_id}/download"
        }
        
        return details
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
def _parse_time_range(time_range: str) -> tuple:
    """Parse time range string to start and end datetime objects."""
    now = datetime.now()
    
    time_mappings = {
        "1d": timedelta(days=1),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "90d": timedelta(days=90),
        "365d": timedelta(days=365)
    }
    
    if time_range not in time_mappings:
        raise HTTPException(status_code=400, detail=f"Invalid time range: {time_range}")
    
    delta = time_mappings[time_range]
    start_time = now - delta
    
    return start_time, now


async def _generate_report_background(job_id: str, report_request: ReportGeneration):
    """Background task to generate report."""
    try:
        # This would typically generate the actual report
        # For now, simulate report generation
        await asyncio.sleep(5)  # Simulate processing time
        
        # In a real implementation, this would:
        # 1. Generate the report data
        # 2. Export to requested format
        # 3. Store in file system or cloud storage
        # 4. Update job status in database
        # 5. Send notification if configured
        
        print(f"Report {job_id} generated successfully")
        
    except Exception as e:
        print(f"Error generating report {job_id}: {e}")
        # Update job status to failed in database 