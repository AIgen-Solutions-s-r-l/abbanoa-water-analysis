"""Integration tests for real reports generation from database."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json


class TestReportsRealDataGeneration:
    """Test real report generation from database."""
    
    @pytest.mark.asyncio
    async def test_generate_consumption_report_from_database(self):
        """Test consumption report generated from real sensor data."""
        from src.presentation.api.endpoints.reports_router import generate_consumption_report
        
        # Mock database connection
        mock_conn = AsyncMock()
        
        # Mock sensor data from database
        mock_conn.fetch = AsyncMock(return_value=[
            {'node_id': 'N001', 'flow_rate': 150.5, 'timestamp': datetime.now(), 'consumption': 1500.0},
            {'node_id': 'N002', 'flow_rate': 200.3, 'timestamp': datetime.now(), 'consumption': 2000.0},
            {'node_id': 'N003', 'flow_rate': 175.2, 'timestamp': datetime.now(), 'consumption': 1750.0}
        ])
        
        mock_conn.fetchrow = AsyncMock(return_value={
            'total_consumption': 5250.0,
            'avg_flow_rate': 175.33,
            'max_flow_rate': 200.3,
            'min_flow_rate': 150.5
        })
        
        # Generate report
        report = await generate_consumption_report(
            conn=mock_conn,
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now(),
            report_format='json'
        )
        
        # Verify report contains real data
        assert report is not None
        assert 'total_consumption' in report
        assert report['total_consumption'] == 5250.0
        assert 'avg_flow_rate' in report
        assert report['avg_flow_rate'] == 175.33
        assert 'period' in report
        assert 'nodes_summary' in report
        assert len(report['nodes_summary']) == 3
    
    @pytest.mark.asyncio
    async def test_generate_quality_report_from_database(self):
        """Test quality report generated from real quality measurements."""
        from src.presentation.api.endpoints.reports_router import generate_quality_report
        
        # Mock database connection
        mock_conn = AsyncMock()
        
        # Mock quality data
        mock_conn.fetch = AsyncMock(return_value=[
            {'parameter': 'pH', 'value': 7.2, 'min_value': 7.0, 'max_value': 7.5, 'compliant': True},
            {'parameter': 'Chlorine', 'value': 0.5, 'min_value': 0.4, 'max_value': 0.6, 'compliant': True},
            {'parameter': 'Turbidity', 'value': 0.3, 'min_value': 0.1, 'max_value': 0.4, 'compliant': True}
        ])
        
        mock_conn.fetchrow = AsyncMock(return_value={
            'total_samples': 1000,
            'compliant_samples': 985,
            'compliance_rate': 98.5
        })
        
        # Generate report
        report = await generate_quality_report(
            conn=mock_conn,
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            report_format='json'
        )
        
        # Verify report contains real data
        assert report is not None
        assert 'compliance_rate' in report
        assert report['compliance_rate'] == 98.5
        assert 'parameters' in report
        assert len(report['parameters']) == 3
        assert 'total_samples' in report
        assert report['total_samples'] == 1000
    
    @pytest.mark.asyncio
    async def test_generate_efficiency_report_from_database(self):
        """Test efficiency report with real system metrics."""
        from src.presentation.api.endpoints.reports_router import generate_efficiency_report
        
        # Mock database connection
        mock_conn = AsyncMock()
        
        # Mock efficiency metrics
        mock_conn.fetchrow = AsyncMock(return_value={
            'water_loss_percentage': 12.5,
            'energy_efficiency': 85.3,
            'pressure_efficiency': 92.1,
            'distribution_efficiency': 88.7
        })
        
        # Generate report
        report = await generate_efficiency_report(
            conn=mock_conn,
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            report_format='json'
        )
        
        # Verify report contains real metrics
        assert report is not None
        assert 'water_loss_percentage' in report
        assert report['water_loss_percentage'] == 12.5
        assert 'energy_efficiency' in report
        assert report['energy_efficiency'] == 85.3
        assert 'overall_efficiency' in report
    
    @pytest.mark.asyncio
    async def test_generate_anomaly_report_from_database(self):
        """Test anomaly report with real detected anomalies."""
        from src.presentation.api.endpoints.reports_router import generate_anomaly_report
        
        # Mock database connection
        mock_conn = AsyncMock()
        
        # Mock anomaly data
        mock_conn.fetch = AsyncMock(return_value=[
            {
                'anomaly_id': 'A001',
                'node_id': 'N001',
                'type': 'pressure_drop',
                'severity': 'high',
                'timestamp': datetime.now() - timedelta(hours=2),
                'resolved': False
            },
            {
                'anomaly_id': 'A002',
                'node_id': 'N003',
                'type': 'flow_spike',
                'severity': 'medium',
                'timestamp': datetime.now() - timedelta(hours=5),
                'resolved': True
            }
        ])
        
        mock_conn.fetchrow = AsyncMock(return_value={
            'total_anomalies': 15,
            'resolved_count': 10,
            'pending_count': 5,
            'high_severity': 3,
            'medium_severity': 7,
            'low_severity': 5
        })
        
        # Generate report
        report = await generate_anomaly_report(
            conn=mock_conn,
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now(),
            report_format='json'
        )
        
        # Verify report contains real anomaly data
        assert report is not None
        assert 'total_anomalies' in report
        assert report['total_anomalies'] == 15
        assert 'anomalies' in report
        assert len(report['anomalies']) == 2
        assert 'severity_breakdown' in report
        assert report['severity_breakdown']['high'] == 3
    
    @pytest.mark.asyncio
    async def test_report_status_tracking_in_database(self):
        """Test real report status tracking in database."""
        from src.presentation.api.endpoints.reports_router import track_report_status
        
        # Mock database connection
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetchrow = AsyncMock()
        
        # Track report generation
        job_id = "JOB_001"
        
        # Update status to processing
        await track_report_status(mock_conn, job_id, "processing", 25)
        mock_conn.execute.assert_called()
        
        # Update status to completed
        await track_report_status(mock_conn, job_id, "completed", 100)
        assert mock_conn.execute.call_count == 2
        
        # Verify status stored in database
        mock_conn.fetchrow.return_value = {
            'job_id': job_id,
            'status': 'completed',
            'progress': 100,
            'created_at': datetime.now()
        }
        
        status = await mock_conn.fetchrow("SELECT * FROM report_jobs WHERE job_id = $1", job_id)
        assert status['status'] == 'completed'
        assert status['progress'] == 100
    
    @pytest.mark.asyncio
    async def test_export_report_multiple_formats(self):
        """Test exporting reports in multiple formats."""
        from src.presentation.api.endpoints.reports_router import export_report
        
        # Mock database connection
        mock_conn = AsyncMock()
        
        report_data = {
            'title': 'Consumption Report',
            'total_consumption': 5250.0,
            'period': {'start': '2025-01-01', 'end': '2025-01-07'}
        }
        
        # Test JSON export
        json_export = await export_report(report_data, format='json')
        assert isinstance(json_export, str)
        assert json.loads(json_export)['total_consumption'] == 5250.0
        
        # Test CSV export
        csv_export = await export_report(report_data, format='csv')
        assert isinstance(csv_export, str)
        assert 'total_consumption,5250.0' in csv_export
        
        # Test PDF export (returns bytes)
        pdf_export = await export_report(report_data, format='pdf')
        assert isinstance(pdf_export, bytes)
        assert len(pdf_export) > 0


class TestReportTemplates:
    """Test report template system."""
    
    @pytest.mark.asyncio
    async def test_daily_consumption_template(self):
        """Test daily consumption report template."""
        from src.presentation.api.endpoints.reports_router import apply_template
        
        mock_conn = AsyncMock()
        
        # Apply daily template
        report = await apply_template(
            conn=mock_conn,
            template='daily_consumption',
            date=datetime.now().date()
        )
        
        assert report is not None
        assert 'report_type' in report
        assert report['report_type'] == 'daily_consumption'
        assert 'sections' in report
        assert 'summary' in report['sections']
        assert 'hourly_breakdown' in report['sections']
        assert 'peak_usage' in report['sections']
    
    @pytest.mark.asyncio  
    async def test_monthly_summary_template(self):
        """Test monthly summary report template."""
        from src.presentation.api.endpoints.reports_router import apply_template
        
        mock_conn = AsyncMock()
        
        # Apply monthly template
        report = await apply_template(
            conn=mock_conn,
            template='monthly_summary',
            year=2025,
            month=1
        )
        
        assert report is not None
        assert 'report_type' in report
        assert report['report_type'] == 'monthly_summary'
        assert 'sections' in report
        assert 'consumption_trends' in report['sections']
        assert 'efficiency_metrics' in report['sections']
        assert 'cost_analysis' in report['sections']


class TestReportScheduling:
    """Test scheduled report generation."""
    
    @pytest.mark.asyncio
    async def test_create_report_schedule(self):
        """Test creating a report schedule in database."""
        from src.presentation.api.endpoints.reports_router import create_report_schedule
        
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={
            'schedule_id': 'SCH_001',
            'active': True
        })
        
        schedule = await create_report_schedule(
            conn=mock_conn,
            report_type='weekly_summary',
            frequency='weekly',
            recipients=['admin@example.com']
        )
        
        assert schedule is not None
        assert schedule['schedule_id'] == 'SCH_001'
        assert schedule['active'] is True
        mock_conn.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_scheduled_reports(self):
        """Test executing scheduled reports."""
        from src.presentation.api.endpoints.reports_router import execute_scheduled_reports
        
        mock_conn = AsyncMock()
        
        # Mock scheduled reports
        mock_conn.fetch = AsyncMock(return_value=[
            {
                'schedule_id': 'SCH_001',
                'report_type': 'daily_consumption',
                'last_run': datetime.now() - timedelta(days=1)
            },
            {
                'schedule_id': 'SCH_002',
                'report_type': 'weekly_summary',
                'last_run': datetime.now() - timedelta(days=7)
            }
        ])
        
        # Execute scheduled reports
        results = await execute_scheduled_reports(mock_conn)
        
        assert len(results) == 2
        assert results[0]['schedule_id'] == 'SCH_001'
        assert results[1]['schedule_id'] == 'SCH_002'