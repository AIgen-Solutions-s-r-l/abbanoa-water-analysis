"""
Unit tests for ReportsService.

Tests all report generation business logic including PDF generation,
data aggregation, and custom report creation.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from typing import Dict, Any, List

from src.api.services.reports_service import ReportsService
from src.schemas.api.reports import (
    ReportGeneration, ReportTemplate, ReportSchedule, ReportAnalytics,
    CustomReport, ReportMetadata, ReportConfiguration
)


@pytest.mark.unit
@pytest.mark.reports
class TestReportsService:
    """Test suite for ReportsService."""

    @pytest.fixture
    def reports_service(self):
        """Provide ReportsService instance."""
        return ReportsService()

    @pytest.fixture
    def mock_hybrid_service(self):
        """Provide mocked HybridDataService."""
        mock = AsyncMock()
        mock.get_consumption_data.return_value = [
            {
                "node_id": "NODE_001",
                "timestamp": "2024-01-01T10:00:00",
                "consumption_value": 150.0,
                "region": "North"
            }
        ]
        return mock

    @pytest.mark.asyncio
    async def test_generate_consumption_report_success(
        self, reports_service, mock_hybrid_service, test_date_range
    ):
        """Test successful consumption report generation."""
        result = await reports_service.generate_consumption_report(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"],
            report_format="pdf"
        )

        assert isinstance(result, ReportGeneration)
        assert hasattr(result, 'report_id')
        assert hasattr(result, 'download_url')
        assert hasattr(result, 'report_format')

    @pytest.mark.asyncio
    async def test_generate_quality_report_success(
        self, reports_service, mock_hybrid_service, test_date_range
    ):
        """Test successful quality report generation."""
        result = await reports_service.generate_quality_report(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"],
            report_format="excel"
        )

        assert isinstance(result, ReportGeneration)
        assert result.report_format == "excel"

    @pytest.mark.asyncio
    async def test_generate_kpi_report_success(
        self, reports_service, mock_hybrid_service, test_date_range
    ):
        """Test successful KPI report generation."""
        result = await reports_service.generate_kpi_report(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"],
            report_format="json"
        )

        assert isinstance(result, ReportGeneration)
        assert result.report_format == "json"

    @pytest.mark.asyncio
    async def test_create_custom_report_success(
        self, reports_service, mock_hybrid_service, test_date_range
    ):
        """Test successful custom report creation."""
        custom_config = {
            "title": "Custom Water Analysis Report",
            "sections": ["consumption", "quality", "kpis"],
            "metrics": ["total_consumption", "compliance_rate"],
            "charts": ["time_series", "bar_chart"],
            "format": "pdf"
        }

        result = await reports_service.create_custom_report(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"],
            custom_config
        )

        assert isinstance(result, CustomReport)
        assert hasattr(result, 'report_id')
        assert hasattr(result, 'sections')

    @pytest.mark.asyncio
    async def test_schedule_report_success(
        self, reports_service, mock_hybrid_service
    ):
        """Test successful report scheduling."""
        schedule_config = {
            "report_type": "consumption",
            "frequency": "weekly",
            "recipients": ["admin@example.com"],
            "format": "pdf"
        }

        result = await reports_service.schedule_report(
            mock_hybrid_service,
            schedule_config
        )

        assert isinstance(result, ReportSchedule)
        assert hasattr(result, 'schedule_id')
        assert hasattr(result, 'next_run_date')

    def test_pdf_generation(self, reports_service):
        """Test PDF generation functionality."""
        sample_data = {
            "title": "Test Report",
            "sections": [
                {"title": "Summary", "content": "This is a test report"},
                {"title": "Data", "content": "Sample data content"}
            ],
            "charts": [
                {"type": "bar", "data": [1, 2, 3, 4, 5]},
                {"type": "line", "data": [10, 20, 30, 40, 50]}
            ]
        }

        with patch('src.api.services.reports_service.generate_pdf') as mock_pdf:
            mock_pdf.return_value = b"PDF content"
            
            pdf_content = reports_service._generate_pdf_report(sample_data)
            assert isinstance(pdf_content, bytes)
            mock_pdf.assert_called_once()

    def test_excel_generation(self, reports_service):
        """Test Excel generation functionality."""
        sample_data = {
            "sheets": [
                {
                    "name": "Consumption Data",
                    "data": [
                        {"node_id": "NODE_001", "value": 100},
                        {"node_id": "NODE_002", "value": 200}
                    ]
                },
                {
                    "name": "Quality Data", 
                    "data": [
                        {"sensor_id": "SENSOR_001", "ph": 7.2},
                        {"sensor_id": "SENSOR_002", "ph": 7.1}
                    ]
                }
            ]
        }

        with patch('src.api.services.reports_service.generate_excel') as mock_excel:
            mock_excel.return_value = b"Excel content"
            
            excel_content = reports_service._generate_excel_report(sample_data)
            assert isinstance(excel_content, bytes)
            mock_excel.assert_called_once()

    def test_chart_generation(self, reports_service):
        """Test chart generation for reports."""
        # Test line chart
        line_data = {
            "type": "line",
            "data": [10, 20, 30, 40, 50],
            "labels": ["Jan", "Feb", "Mar", "Apr", "May"]
        }
        
        line_chart = reports_service._generate_chart(line_data)
        assert "chart_data" in line_chart
        assert line_chart["type"] == "line"

        # Test bar chart
        bar_data = {
            "type": "bar",
            "data": [100, 200, 150, 300],
            "labels": ["Q1", "Q2", "Q3", "Q4"]
        }
        
        bar_chart = reports_service._generate_chart(bar_data)
        assert "chart_data" in bar_chart
        assert bar_chart["type"] == "bar"

    def test_data_aggregation(self, reports_service):
        """Test data aggregation for reports."""
        sample_data = [
            {"node_id": "NODE_001", "value": 100, "region": "North"},
            {"node_id": "NODE_002", "value": 200, "region": "North"},
            {"node_id": "NODE_003", "value": 150, "region": "South"}
        ]

        # Test aggregation by region
        aggregated = reports_service._aggregate_data(sample_data, "region")
        assert "North" in aggregated
        assert "South" in aggregated
        assert aggregated["North"]["total"] == 300
        assert aggregated["South"]["total"] == 150

    def test_report_template_management(self, reports_service):
        """Test report template management."""
        template_config = {
            "name": "Monthly Summary",
            "sections": ["header", "consumption", "quality", "footer"],
            "styling": {"primary_color": "#1f77b4", "font": "Arial"},
            "charts": ["consumption_trend", "quality_overview"]
        }

        template = reports_service._create_template(template_config)
        assert template["name"] == "Monthly Summary"
        assert len(template["sections"]) == 4
        assert "styling" in template

    def test_report_validation(self, reports_service):
        """Test report configuration validation."""
        # Valid configuration
        valid_config = {
            "title": "Test Report",
            "sections": ["consumption", "quality"],
            "format": "pdf",
            "date_range": {"start": "2024-01-01", "end": "2024-01-31"}
        }
        assert reports_service._validate_report_config(valid_config) is True

        # Invalid configuration - missing title
        invalid_config = {
            "sections": ["consumption"],
            "format": "pdf"
        }
        assert reports_service._validate_report_config(invalid_config) is False

    def test_report_metadata_generation(self, reports_service):
        """Test report metadata generation."""
        report_config = {
            "title": "Monthly Report",
            "format": "pdf",
            "sections": ["consumption", "quality"]
        }

        metadata = reports_service._generate_metadata(report_config)
        assert "report_id" in metadata
        assert "created_at" in metadata
        assert "title" in metadata
        assert "format" in metadata

    @pytest.mark.parametrize("format_type", ["pdf", "excel", "json", "csv"])
    def test_multiple_report_formats(self, reports_service, format_type):
        """Test generation of multiple report formats."""
        sample_data = {
            "title": "Test Report",
            "data": [{"key": "value1"}, {"key": "value2"}]
        }

        if format_type == "pdf":
            with patch('src.api.services.reports_service.generate_pdf') as mock_gen:
                mock_gen.return_value = b"PDF content"
                result = reports_service._generate_report_by_format(sample_data, format_type)
                assert isinstance(result, bytes)
        
        elif format_type == "excel":
            with patch('src.api.services.reports_service.generate_excel') as mock_gen:
                mock_gen.return_value = b"Excel content"
                result = reports_service._generate_report_by_format(sample_data, format_type)
                assert isinstance(result, bytes)
        
        elif format_type == "json":
            result = reports_service._generate_report_by_format(sample_data, format_type)
            assert isinstance(result, str)
        
        elif format_type == "csv":
            result = reports_service._generate_report_by_format(sample_data, format_type)
            assert isinstance(result, str)

    def test_report_performance_optimization(self, reports_service):
        """Test report performance optimization."""
        large_dataset = [
            {"node_id": f"NODE_{i:03d}", "value": i * 10}
            for i in range(10000)
        ]

        # Test data sampling for large datasets
        sampled_data = reports_service._optimize_data_for_reporting(large_dataset)
        assert len(sampled_data) <= 1000  # Should be reduced for performance

    def test_report_caching(self, reports_service):
        """Test report caching mechanism."""
        cache_key = "report_consumption_2024_01"
        report_data = {"title": "Cached Report", "data": [1, 2, 3]}

        # Test cache storage
        reports_service._cache_report(cache_key, report_data)
        
        # Test cache retrieval
        cached_data = reports_service._get_cached_report(cache_key)
        assert cached_data == report_data

    def test_error_handling_in_report_generation(self, reports_service):
        """Test error handling during report generation."""
        # Test handling of corrupted data
        corrupted_data = {"invalid": None, "data": []}
        
        with pytest.raises(Exception):
            reports_service._generate_pdf_report(corrupted_data)

        # Test handling of missing templates
        with pytest.raises(Exception):
            reports_service._apply_template({"data": []}, "non_existent_template") 