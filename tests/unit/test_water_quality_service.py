"""
Unit tests for WaterQualityService.

Tests all water quality monitoring business logic including compliance tracking,
contamination detection, and quality analytics.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from typing import Dict, Any, List

from src.api.services.water_quality_service import WaterQualityService
from src.schemas.api.water_quality import (
    WaterQualityReading, QualityAnalytics, ComplianceReport,
    ContaminationEvent, QualityTrend, SensorCalibration
)


@pytest.mark.unit
@pytest.mark.quality
class TestWaterQualityService:
    """Test suite for WaterQualityService."""

    @pytest.fixture
    def quality_service(self):
        """Provide WaterQualityService instance."""
        return WaterQualityService()

    @pytest.fixture
    def mock_hybrid_service(self):
        """Provide mocked HybridDataService."""
        mock = AsyncMock()
        mock.get_quality_data.return_value = [
            {
                "sensor_id": "SENSOR_001",
                "timestamp": "2024-01-01T10:00:00",
                "ph_level": 7.2,
                "temperature": 22.5,
                "turbidity": 1.2,
                "dissolved_oxygen": 8.5,
                "conductivity": 450,
                "compliance_status": "compliant"
            }
        ]
        return mock

    @pytest.mark.asyncio
    async def test_get_quality_readings_success(
        self, quality_service, mock_hybrid_service, test_date_range
    ):
        """Test successful quality readings retrieval."""
        result = await quality_service.get_quality_readings(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], WaterQualityReading)
        assert result[0].sensor_id == "SENSOR_001"
        assert result[0].ph_level == 7.2

    @pytest.mark.asyncio
    async def test_get_quality_analytics_success(
        self, quality_service, mock_hybrid_service, test_date_range
    ):
        """Test successful quality analytics generation."""
        result = await quality_service.get_quality_analytics(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        assert isinstance(result, QualityAnalytics)
        assert hasattr(result, 'overall_compliance_rate')
        assert hasattr(result, 'parameter_averages')
        assert hasattr(result, 'trend_analysis')

    @pytest.mark.asyncio
    async def test_get_compliance_report_success(
        self, quality_service, mock_hybrid_service, test_date_range
    ):
        """Test successful compliance report generation."""
        result = await quality_service.get_compliance_report(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        assert isinstance(result, ComplianceReport)
        assert hasattr(result, 'compliance_percentage')
        assert hasattr(result, 'violations')
        assert hasattr(result, 'recommendations')

    @pytest.mark.asyncio
    async def test_detect_contamination_events_success(
        self, quality_service, mock_hybrid_service, test_date_range
    ):
        """Test successful contamination event detection."""
        # Mock data with contamination indicators
        mock_hybrid_service.get_quality_data.return_value = [
            {
                "sensor_id": "SENSOR_001",
                "timestamp": "2024-01-01T10:00:00",
                "ph_level": 5.0,  # Below safe range
                "temperature": 22.5,
                "turbidity": 5.0,  # High turbidity
                "dissolved_oxygen": 4.0,  # Low oxygen
                "conductivity": 450,
                "compliance_status": "non_compliant"
            }
        ]

        result = await quality_service.detect_contamination_events(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        assert isinstance(result, list)
        assert all(isinstance(item, ContaminationEvent) for item in result)

    def test_quality_parameter_validation(self, quality_service):
        """Test quality parameter validation."""
        # Test valid parameters
        valid_reading = {
            "ph_level": 7.2,
            "temperature": 22.5,
            "turbidity": 1.2,
            "dissolved_oxygen": 8.5,
            "conductivity": 450
        }
        assert quality_service._validate_quality_parameters(valid_reading) is True

        # Test invalid pH
        invalid_ph = valid_reading.copy()
        invalid_ph["ph_level"] = 15.0  # Impossible pH
        assert quality_service._validate_quality_parameters(invalid_ph) is False

    def test_compliance_assessment(self, quality_service):
        """Test compliance assessment logic."""
        compliant_data = {
            "ph_level": 7.2,
            "temperature": 22.5,
            "turbidity": 1.2,
            "dissolved_oxygen": 8.5
        }
        
        compliance = quality_service._assess_compliance(compliant_data)
        assert compliance["status"] == "compliant"
        assert compliance["violations"] == []

        non_compliant_data = {
            "ph_level": 5.0,  # Too low
            "temperature": 35.0,  # Too high
            "turbidity": 10.0,  # Too high
            "dissolved_oxygen": 3.0  # Too low
        }
        
        compliance = quality_service._assess_compliance(non_compliant_data)
        assert compliance["status"] == "non_compliant"
        assert len(compliance["violations"]) > 0

    def test_contamination_detection_algorithms(self, quality_service):
        """Test contamination detection algorithms."""
        # Test bacterial contamination indicators
        bacterial_indicators = {
            "ph_level": 8.5,
            "temperature": 30.0,
            "turbidity": 8.0,
            "dissolved_oxygen": 2.0
        }
        
        contamination_type = quality_service._detect_contamination_type(bacterial_indicators)
        assert contamination_type in ["bacterial", "chemical", "physical", "none"]

        # Test chemical contamination indicators
        chemical_indicators = {
            "ph_level": 4.0,
            "conductivity": 2000,
            "temperature": 25.0
        }
        
        contamination_type = quality_service._detect_contamination_type(chemical_indicators)
        assert contamination_type in ["bacterial", "chemical", "physical", "none"]

    @pytest.mark.parametrize("parameter", ["ph_level", "temperature", "turbidity", "dissolved_oxygen"])
    def test_individual_parameter_analysis(self, quality_service, parameter):
        """Test individual parameter analysis."""
        sample_data = [
            {parameter: 7.0 + i * 0.1, "timestamp": f"2024-01-{i:02d}T10:00:00"}
            for i in range(1, 11)
        ]
        
        analysis = quality_service._analyze_parameter_trend(sample_data, parameter)
        assert "trend" in analysis
        assert "average" in analysis
        assert "min_value" in analysis
        assert "max_value" in analysis

    def test_quality_trend_calculation(self, quality_service):
        """Test quality trend calculation."""
        trending_data = [
            {
                "ph_level": 7.0 + i * 0.1,
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat()
            }
            for i in range(10)
        ]
        
        trend = quality_service._calculate_quality_trend(trending_data, "ph_level")
        assert trend["direction"] in ["increasing", "decreasing", "stable"]
        assert isinstance(trend["slope"], float)
        assert isinstance(trend["confidence"], float)

    def test_sensor_calibration_check(self, quality_service):
        """Test sensor calibration checking."""
        # Test normal sensor readings
        normal_readings = [
            {"ph_level": 7.0 + i * 0.01, "timestamp": f"2024-01-{i:02d}T10:00:00"}
            for i in range(1, 11)
        ]
        
        calibration_status = quality_service._check_sensor_calibration(normal_readings, "SENSOR_001")
        assert calibration_status["needs_calibration"] is False

        # Test erratic sensor readings
        erratic_readings = [
            {"ph_level": 7.0 if i % 2 == 0 else 9.0, "timestamp": f"2024-01-{i:02d}T10:00:00"}
            for i in range(1, 11)
        ]
        
        calibration_status = quality_service._check_sensor_calibration(erratic_readings, "SENSOR_001")
        assert calibration_status["needs_calibration"] is True 