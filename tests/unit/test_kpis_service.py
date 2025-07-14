"""
Unit tests for KPIOrchestrator and KPI services.

Tests KPI calculation, dashboard generation, and performance monitoring.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from typing import Dict, Any, List

from src.api.services.kpis.kpis_orchestrator import KPIOrchestrator
from src.api.services.kpis.system_performance_service import SystemPerformanceService
from src.api.services.kpis.network_efficiency_service import NetworkEfficiencyService
from src.api.services.kpis.quality_service import QualityService
from src.api.services.kpis.dashboard_service import DashboardService
from src.schemas.api.kpis import (
    KPIDashboard, KPICard, KPITrend, KPIBenchmark, KPIAlert, KPIGoal,
    KPIReport, KPIComparison, KPIConfiguration, KPIHealth
)


@pytest.mark.unit
@pytest.mark.kpis
class TestKPIOrchestrator:
    """Test suite for KPIOrchestrator."""

    @pytest.fixture
    def kpi_orchestrator(self):
        """Provide KPIOrchestrator instance."""
        return KPIOrchestrator()

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
        mock.get_quality_data.return_value = [
            {
                "sensor_id": "SENSOR_001",
                "timestamp": "2024-01-01T10:00:00",
                "ph_level": 7.2,
                "compliance_status": "compliant"
            }
        ]
        return mock

    @pytest.mark.asyncio
    async def test_generate_kpi_dashboard_success(
        self, kpi_orchestrator, mock_hybrid_service, test_date_range
    ):
        """Test successful KPI dashboard generation."""
        result = await kpi_orchestrator.generate_kpi_dashboard(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        assert isinstance(result, KPIDashboard)
        assert hasattr(result, 'system_performance')
        assert hasattr(result, 'network_efficiency')
        assert hasattr(result, 'quality_metrics')
        assert hasattr(result, 'overall_health_score')

    @pytest.mark.asyncio
    async def test_generate_kpi_cards_success(
        self, kpi_orchestrator, mock_hybrid_service, test_date_range
    ):
        """Test successful KPI cards generation."""
        result = await kpi_orchestrator.generate_kpi_cards(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        assert isinstance(result, list)
        assert all(isinstance(card, KPICard) for card in result)

    @pytest.mark.asyncio
    async def test_generate_kpi_trends_success(
        self, kpi_orchestrator, mock_hybrid_service, test_date_range
    ):
        """Test successful KPI trends generation."""
        result = await kpi_orchestrator.generate_kpi_trends(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        assert isinstance(result, list)
        assert all(isinstance(trend, KPITrend) for trend in result)

    @pytest.mark.asyncio
    async def test_generate_kpi_alerts_success(
        self, kpi_orchestrator, mock_hybrid_service, test_date_range
    ):
        """Test successful KPI alerts generation."""
        result = await kpi_orchestrator.generate_kpi_alerts(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        assert isinstance(result, list)
        assert all(isinstance(alert, KPIAlert) for alert in result)

    @pytest.mark.asyncio
    async def test_get_kpi_health_success(
        self, kpi_orchestrator, mock_hybrid_service, test_date_range
    ):
        """Test successful KPI health assessment."""
        result = await kpi_orchestrator.get_kpi_health(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        assert isinstance(result, KPIHealth)
        assert hasattr(result, 'overall_health_score')
        assert hasattr(result, 'system_status')
        assert hasattr(result, 'critical_issues')


@pytest.mark.unit
@pytest.mark.kpis
class TestSystemPerformanceService:
    """Test suite for SystemPerformanceService."""

    @pytest.fixture
    def system_service(self):
        """Provide SystemPerformanceService instance."""
        return SystemPerformanceService()

    def test_calculate_uptime_percentage(self, system_service):
        """Test uptime percentage calculation."""
        # Test with no downtime
        uptime_data = [
            {"timestamp": "2024-01-01T10:00:00", "status": "online"},
            {"timestamp": "2024-01-01T11:00:00", "status": "online"},
            {"timestamp": "2024-01-01T12:00:00", "status": "online"}
        ]
        
        uptime = system_service._calculate_uptime_percentage(uptime_data)
        assert uptime == 100.0

        # Test with some downtime
        downtime_data = [
            {"timestamp": "2024-01-01T10:00:00", "status": "online"},
            {"timestamp": "2024-01-01T11:00:00", "status": "offline"},
            {"timestamp": "2024-01-01T12:00:00", "status": "online"}
        ]
        
        uptime = system_service._calculate_uptime_percentage(downtime_data)
        assert 0.0 <= uptime <= 100.0

    def test_calculate_response_time_metrics(self, system_service):
        """Test response time metrics calculation."""
        response_times = [100, 150, 200, 120, 180, 90, 300]
        
        metrics = system_service._calculate_response_time_metrics(response_times)
        assert "average" in metrics
        assert "median" in metrics
        assert "p95" in metrics
        assert "p99" in metrics

    def test_calculate_throughput(self, system_service):
        """Test throughput calculation."""
        request_data = [
            {"timestamp": "2024-01-01T10:00:00", "requests": 100},
            {"timestamp": "2024-01-01T10:01:00", "requests": 120},
            {"timestamp": "2024-01-01T10:02:00", "requests": 90}
        ]
        
        throughput = system_service._calculate_throughput(request_data)
        assert throughput > 0


@pytest.mark.unit
@pytest.mark.kpis  
class TestNetworkEfficiencyService:
    """Test suite for NetworkEfficiencyService."""

    @pytest.fixture
    def network_service(self):
        """Provide NetworkEfficiencyService instance."""
        return NetworkEfficiencyService()

    def test_calculate_water_loss_percentage(self, network_service):
        """Test water loss percentage calculation."""
        flow_data = [
            {"node_id": "SOURCE", "flow_rate": 1000, "type": "input"},
            {"node_id": "DIST_001", "flow_rate": 950, "type": "output"},
            {"node_id": "DIST_002", "flow_rate": 920, "type": "output"}
        ]
        
        water_loss = network_service._calculate_water_loss_percentage(flow_data)
        assert 0.0 <= water_loss <= 100.0

    def test_calculate_pressure_efficiency(self, network_service):
        """Test pressure efficiency calculation."""
        pressure_data = [
            {"node_id": "NODE_001", "pressure": 45, "target_pressure": 50},
            {"node_id": "NODE_002", "pressure": 48, "target_pressure": 50},
            {"node_id": "NODE_003", "pressure": 52, "target_pressure": 50}
        ]
        
        efficiency = network_service._calculate_pressure_efficiency(pressure_data)
        assert 0.0 <= efficiency <= 100.0

    def test_calculate_energy_efficiency(self, network_service):
        """Test energy efficiency calculation."""
        energy_data = [
            {"pump_id": "PUMP_001", "energy_consumed": 100, "water_delivered": 1000},
            {"pump_id": "PUMP_002", "energy_consumed": 120, "water_delivered": 1200}
        ]
        
        efficiency = network_service._calculate_energy_efficiency(energy_data)
        assert efficiency > 0


@pytest.mark.unit
@pytest.mark.kpis
class TestQualityService:
    """Test suite for QualityService."""

    @pytest.fixture
    def quality_service(self):
        """Provide QualityService instance."""
        return QualityService()

    def test_calculate_compliance_rate(self, quality_service):
        """Test compliance rate calculation."""
        quality_data = [
            {"sensor_id": "SENSOR_001", "compliance_status": "compliant"},
            {"sensor_id": "SENSOR_002", "compliance_status": "compliant"},
            {"sensor_id": "SENSOR_003", "compliance_status": "non_compliant"}
        ]
        
        compliance_rate = quality_service._calculate_compliance_rate(quality_data)
        assert 0.0 <= compliance_rate <= 100.0

    def test_calculate_contamination_incidents(self, quality_service):
        """Test contamination incidents calculation."""
        incident_data = [
            {"incident_id": "INC_001", "severity": "high", "resolved": True},
            {"incident_id": "INC_002", "severity": "medium", "resolved": False},
            {"incident_id": "INC_003", "severity": "low", "resolved": True}
        ]
        
        incidents = quality_service._calculate_contamination_incidents(incident_data)
        assert "total_incidents" in incidents
        assert "unresolved_incidents" in incidents
        assert "severity_breakdown" in incidents

    def test_calculate_parameter_averages(self, quality_service):
        """Test parameter averages calculation."""
        parameter_data = [
            {"ph_level": 7.2, "temperature": 22.5, "turbidity": 1.2},
            {"ph_level": 7.1, "temperature": 23.0, "turbidity": 1.4},
            {"ph_level": 7.3, "temperature": 21.8, "turbidity": 1.1}
        ]
        
        averages = quality_service._calculate_parameter_averages(parameter_data)
        assert "ph_level" in averages
        assert "temperature" in averages
        assert "turbidity" in averages


@pytest.mark.unit
@pytest.mark.kpis
class TestDashboardService:
    """Test suite for DashboardService."""

    @pytest.fixture
    def dashboard_service(self):
        """Provide DashboardService instance."""
        return DashboardService()

    def test_aggregate_kpi_data(self, dashboard_service):
        """Test KPI data aggregation."""
        kpi_data = {
            "system_performance": {"uptime": 99.5, "response_time": 150},
            "network_efficiency": {"water_loss": 12.3, "pressure_efficiency": 85.2},
            "quality_metrics": {"compliance_rate": 98.7, "incidents": 2}
        }
        
        aggregated = dashboard_service._aggregate_kpi_data(kpi_data)
        assert "overall_health_score" in aggregated
        assert "category_scores" in aggregated

    def test_generate_kpi_cards_data(self, dashboard_service):
        """Test KPI cards data generation."""
        sample_kpis = {
            "uptime": {"value": 99.5, "unit": "%", "trend": "stable"},
            "response_time": {"value": 150, "unit": "ms", "trend": "improving"},
            "compliance": {"value": 98.7, "unit": "%", "trend": "declining"}
        }
        
        cards = dashboard_service._generate_kpi_cards_data(sample_kpis)
        assert isinstance(cards, list)
        assert len(cards) == 3

    def test_calculate_health_score(self, dashboard_service):
        """Test overall health score calculation."""
        kpi_metrics = {
            "uptime": 99.5,
            "response_time": 150,
            "water_loss": 12.3,
            "compliance_rate": 98.7,
            "energy_efficiency": 85.2
        }
        
        health_score = dashboard_service._calculate_health_score(kpi_metrics)
        assert 0.0 <= health_score <= 100.0

    def test_identify_critical_issues(self, dashboard_service):
        """Test critical issues identification."""
        kpi_data = {
            "uptime": 95.0,  # Below threshold
            "response_time": 2000,  # Above threshold
            "compliance_rate": 85.0,  # Below threshold
            "water_loss": 25.0  # Above threshold
        }
        
        issues = dashboard_service._identify_critical_issues(kpi_data)
        assert isinstance(issues, list)
        assert len(issues) > 0

    def test_generate_trend_data(self, dashboard_service):
        """Test trend data generation."""
        historical_data = [
            {"timestamp": "2024-01-01", "value": 100},
            {"timestamp": "2024-01-02", "value": 105},
            {"timestamp": "2024-01-03", "value": 110},
            {"timestamp": "2024-01-04", "value": 108}
        ]
        
        trend = dashboard_service._generate_trend_data(historical_data)
        assert "direction" in trend
        assert "percentage_change" in trend
        assert "trend_strength" in trend

    def test_benchmark_comparison(self, dashboard_service):
        """Test benchmark comparison."""
        current_kpis = {
            "uptime": 99.5,
            "response_time": 150,
            "compliance_rate": 98.7
        }
        
        industry_benchmarks = {
            "uptime": 99.9,
            "response_time": 100,
            "compliance_rate": 99.5
        }
        
        comparison = dashboard_service._compare_with_benchmarks(current_kpis, industry_benchmarks)
        assert "uptime" in comparison
        assert "response_time" in comparison
        assert "compliance_rate" in comparison

    @pytest.mark.parametrize("kpi_category", ["system", "network", "quality", "maintenance"])
    def test_category_specific_calculations(self, dashboard_service, kpi_category):
        """Test category-specific KPI calculations."""
        sample_data = {
            "system": {"uptime": 99.5, "response_time": 150},
            "network": {"water_loss": 12.3, "pressure_efficiency": 85.2},
            "quality": {"compliance_rate": 98.7, "incidents": 2},
            "maintenance": {"mttr": 4.5, "preventive_ratio": 80.0}
        }
        
        category_score = dashboard_service._calculate_category_score(sample_data[kpi_category], kpi_category)
        assert 0.0 <= category_score <= 100.0

    def test_alert_threshold_evaluation(self, dashboard_service):
        """Test alert threshold evaluation."""
        kpi_values = {
            "uptime": 98.0,  # Below warning threshold
            "response_time": 500,  # Above warning threshold
            "water_loss": 20.0,  # Above critical threshold
            "compliance_rate": 95.0  # Normal
        }
        
        alerts = dashboard_service._evaluate_alert_thresholds(kpi_values)
        assert isinstance(alerts, list)
        
        # Check that alerts are generated for problematic KPIs
        alert_kpis = [alert["kpi_name"] for alert in alerts]
        assert "uptime" in alert_kpis or "response_time" in alert_kpis or "water_loss" in alert_kpis

    def test_kpi_data_validation(self, dashboard_service):
        """Test KPI data validation."""
        # Valid KPI data
        valid_data = {
            "kpi_name": "uptime",
            "value": 99.5,
            "unit": "%",
            "timestamp": "2024-01-01T10:00:00"
        }
        assert dashboard_service._validate_kpi_data(valid_data) is True

        # Invalid KPI data - negative value where not allowed
        invalid_data = {
            "kpi_name": "uptime",
            "value": -10.0,  # Invalid negative uptime
            "unit": "%"
        }
        assert dashboard_service._validate_kpi_data(invalid_data) is False 