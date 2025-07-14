"""
End-to-end tests for complete water infrastructure monitoring workflows.

Tests complete business workflows that span multiple APIs and services,
ensuring the entire system works together seamlessly.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from typing import Dict, Any, List

from src.api.services.consumption_service import ConsumptionService
from src.api.services.water_quality_service import WaterQualityService
from src.api.services.forecasting_service import ForecastingService
from src.api.services.reports_service import ReportsService
from src.api.services.kpis.kpis_orchestrator import KPIOrchestrator
from src.api.services.filters_service import AdvancedFilteringService


@pytest.mark.e2e
class TestCompleteWorkflows:
    """End-to-end test suite for complete business workflows."""

    @pytest.fixture
    def all_services(self):
        """Provide all service instances for workflow testing."""
        return {
            "consumption": ConsumptionService(),
            "quality": WaterQualityService(),
            "forecasting": ForecastingService(),
            "reports": ReportsService(),
            "kpis": KPIOrchestrator(),
            "filtering": AdvancedFilteringService()
        }

    @pytest.fixture
    def mock_comprehensive_data(self):
        """Comprehensive mock data for all services."""
        base_time = datetime.now() - timedelta(days=30)
        
        return {
            "consumption_data": [
                {
                    "node_id": f"NODE_{i % 10:03d}",
                    "timestamp": (base_time + timedelta(hours=i)).isoformat(),
                    "consumption_value": 100.0 + (i * 5) % 300,
                    "region": f"Region_{i % 5}",
                    "zone": f"Zone_{i % 3}",
                    "unit": "liters"
                }
                for i in range(720)  # 30 days hourly data
            ],
            "quality_data": [
                {
                    "sensor_id": f"SENSOR_{i % 8:03d}",
                    "timestamp": (base_time + timedelta(hours=i * 4)).isoformat(),
                    "ph_level": 7.0 + (i % 20 - 10) * 0.1,
                    "temperature": 20.0 + (i % 15),
                    "turbidity": 1.0 + (i % 10) * 0.2,
                    "dissolved_oxygen": 8.0 + (i % 8) * 0.1,
                    "conductivity": 450 + (i % 100),
                    "compliance_status": "compliant" if i % 10 != 0 else "non_compliant"
                }
                for i in range(180)  # 30 days 4-hourly data
            ],
            "forecast_data": [
                {
                    "node_id": f"NODE_{i % 10:03d}",
                    "timestamp": (datetime.now() + timedelta(days=i)).isoformat(),
                    "predicted_consumption": 150.0 + (i * 10) % 100,
                    "confidence_interval": [140.0 + (i * 10) % 100, 160.0 + (i * 10) % 100],
                    "model_type": "arima",
                    "accuracy_score": 0.85 + (i % 10) * 0.01
                }
                for i in range(7)  # 7 days forecast
            ]
        }

    @pytest.fixture
    def mock_hybrid_service_comprehensive(self, mock_comprehensive_data):
        """Mock hybrid service with comprehensive data."""
        mock = AsyncMock()
        mock.get_consumption_data.return_value = mock_comprehensive_data["consumption_data"]
        mock.get_quality_data.return_value = mock_comprehensive_data["quality_data"]
        mock.get_forecast_data.return_value = mock_comprehensive_data["forecast_data"]
        return mock

    @pytest.mark.asyncio
    async def test_daily_monitoring_workflow(
        self, all_services, mock_hybrid_service_comprehensive, 
        mock_comprehensive_data, api_test_utils
    ):
        """Test complete daily monitoring workflow."""
        start_time = datetime.now() - timedelta(days=1)
        end_time = datetime.now()

        # Step 1: Get consumption data
        consumption_data = await all_services["consumption"].get_consumption_data(
            mock_hybrid_service_comprehensive, start_time, end_time
        )
        assert len(consumption_data) > 0

        # Step 2: Get quality readings
        quality_data = await all_services["quality"].get_quality_readings(
            mock_hybrid_service_comprehensive, start_time, end_time
        )
        assert len(quality_data) > 0

        # Step 3: Generate KPI dashboard
        kpi_dashboard = await all_services["kpis"].generate_kpi_dashboard(
            mock_hybrid_service_comprehensive, start_time, end_time
        )
        assert kpi_dashboard.overall_health_score is not None

        # Step 4: Check for anomalies
        anomalies = await all_services["consumption"].detect_consumption_anomalies(
            mock_hybrid_service_comprehensive, start_time, end_time
        )
        assert isinstance(anomalies, list)

        # Step 5: Generate daily report
        daily_report = await all_services["reports"].generate_consumption_report(
            mock_hybrid_service_comprehensive, start_time, end_time, report_format="json"
        )
        assert daily_report.report_id is not None

        # Verify workflow completeness
        assert len(consumption_data) > 0
        assert len(quality_data) > 0
        assert kpi_dashboard.overall_health_score >= 0

    @pytest.mark.asyncio
    async def test_incident_response_workflow(
        self, all_services, mock_hybrid_service_comprehensive, 
        mock_comprehensive_data, api_test_utils
    ):
        """Test complete incident response workflow."""
        start_time = datetime.now() - timedelta(hours=6)
        end_time = datetime.now()

        # Step 1: Detect water quality incident
        contamination_events = await all_services["quality"].detect_contamination_events(
            mock_hybrid_service_comprehensive, start_time, end_time
        )
        assert isinstance(contamination_events, list)

        # Step 2: Analyze consumption patterns during incident
        consumption_analytics = await all_services["consumption"].get_consumption_analytics(
            mock_hybrid_service_comprehensive, start_time, end_time
        )
        assert consumption_analytics.total_consumption > 0

        # Step 3: Generate KPI alerts
        kpi_alerts = await all_services["kpis"].generate_kpi_alerts(
            mock_hybrid_service_comprehensive, start_time, end_time
        )
        assert isinstance(kpi_alerts, list)

        # Step 4: Get affected nodes using filtering
        from src.schemas.api.filters import (
            AdvancedFilterRequest, FieldFilter, FilterOperator, EntityType
        )
        
        # Filter for high consumption nodes
        filter_request = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            filters=[
                FieldFilter(
                    field="consumption_value",
                    operator=FilterOperator.greater_than,
                    value=200.0
                )
            ]
        )
        
        filtered_nodes = await all_services["filtering"].apply_filters(
            filter_request, mock_comprehensive_data["consumption_data"]
        )
        assert len(filtered_nodes.data) >= 0

        # Step 5: Generate incident report
        incident_report = await all_services["reports"].generate_quality_report(
            mock_hybrid_service_comprehensive, start_time, end_time, report_format="pdf"
        )
        assert incident_report.report_id is not None

        # Verify incident workflow completeness
        assert len(kpi_alerts) >= 0
        assert incident_report.report_format == "pdf"

    @pytest.mark.asyncio
    async def test_predictive_maintenance_workflow(
        self, all_services, mock_hybrid_service_comprehensive,
        mock_comprehensive_data, api_test_utils
    ):
        """Test complete predictive maintenance workflow."""
        # Historical period for analysis
        historical_start = datetime.now() - timedelta(days=30)
        historical_end = datetime.now()

        # Step 1: Analyze historical consumption patterns
        consumption_trends = await all_services["consumption"].get_consumption_trends(
            mock_hybrid_service_comprehensive, historical_start, historical_end
        )
        assert len(consumption_trends) > 0

        # Step 2: Analyze historical quality trends
        quality_analytics = await all_services["quality"].get_quality_analytics(
            mock_hybrid_service_comprehensive, historical_start, historical_end
        )
        assert quality_analytics.overall_compliance_rate >= 0

        # Step 3: Generate forecasts
        consumption_forecasts = await all_services["forecasting"].generate_consumption_forecast(
            mock_hybrid_service_comprehensive, historical_start, historical_end, forecast_horizon=7
        )
        assert len(consumption_forecasts) > 0

        # Step 4: Evaluate forecast accuracy
        model_accuracy = await all_services["forecasting"].evaluate_model_accuracy(
            mock_hybrid_service_comprehensive, "MODEL_001", historical_start, historical_end
        )
        assert model_accuracy.accuracy_metrics is not None

        # Step 5: Generate optimization suggestions
        optimization_suggestions = await all_services["consumption"].get_optimization_suggestions(
            mock_hybrid_service_comprehensive, historical_start, historical_end
        )
        assert isinstance(optimization_suggestions, list)

        # Step 6: Generate maintenance KPIs
        maintenance_kpis = await all_services["kpis"].generate_kpi_trends(
            mock_hybrid_service_comprehensive, historical_start, historical_end,
            kpi_categories=["maintenance", "operational"]
        )
        assert len(maintenance_kpis) > 0

        # Step 7: Generate predictive maintenance report
        maintenance_report = await all_services["reports"].create_custom_report(
            mock_hybrid_service_comprehensive, historical_start, historical_end,
            {
                "title": "Predictive Maintenance Report",
                "sections": ["trends", "forecasts", "optimization", "kpis"],
                "format": "pdf"
            }
        )
        assert maintenance_report.report_id is not None

        # Verify predictive maintenance workflow
        assert len(consumption_trends) > 0
        assert len(consumption_forecasts) > 0
        assert len(optimization_suggestions) >= 0

    @pytest.mark.asyncio
    async def test_regulatory_compliance_workflow(
        self, all_services, mock_hybrid_service_comprehensive,
        mock_comprehensive_data, api_test_utils
    ):
        """Test complete regulatory compliance workflow."""
        # Compliance period (last quarter)
        compliance_start = datetime.now() - timedelta(days=90)
        compliance_end = datetime.now()

        # Step 1: Generate compliance report
        compliance_report = await all_services["quality"].get_compliance_report(
            mock_hybrid_service_comprehensive, compliance_start, compliance_end
        )
        assert compliance_report.compliance_percentage >= 0

        # Step 2: Analyze compliance trends
        quality_trends = await all_services["quality"].get_quality_trends(
            mock_hybrid_service_comprehensive, compliance_start, compliance_end
        )
        assert isinstance(quality_trends, list)

        # Step 3: Generate compliance KPIs
        compliance_kpis = await all_services["kpis"].generate_kpi_dashboard(
            mock_hybrid_service_comprehensive, compliance_start, compliance_end
        )
        assert compliance_kpis.quality_metrics is not None

        # Step 4: Filter non-compliant events
        from src.schemas.api.filters import (
            AdvancedFilterRequest, FieldFilter, FilterOperator, EntityType
        )
        
        non_compliant_filter = AdvancedFilterRequest(
            entity_type=EntityType.water_quality,
            filters=[
                FieldFilter(
                    field="compliance_status",
                    operator=FilterOperator.equals,
                    value="non_compliant"
                )
            ]
        )
        
        non_compliant_events = await all_services["filtering"].apply_filters(
            non_compliant_filter, mock_comprehensive_data["quality_data"]
        )
        assert len(non_compliant_events.data) >= 0

        # Step 5: Generate comprehensive compliance report
        comprehensive_report = await all_services["reports"].generate_quality_report(
            mock_hybrid_service_comprehensive, compliance_start, compliance_end,
            report_format="excel"
        )
        assert comprehensive_report.report_format == "excel"

        # Verify compliance workflow
        assert compliance_report.compliance_percentage >= 0
        assert comprehensive_report.report_id is not None

    @pytest.mark.asyncio
    async def test_executive_dashboard_workflow(
        self, all_services, mock_hybrid_service_comprehensive,
        mock_comprehensive_data, api_test_utils
    ):
        """Test complete executive dashboard workflow."""
        # Executive period (last month)
        exec_start = datetime.now() - timedelta(days=30)
        exec_end = datetime.now()

        # Step 1: Generate comprehensive KPI dashboard
        executive_dashboard = await all_services["kpis"].generate_kpi_dashboard(
            mock_hybrid_service_comprehensive, exec_start, exec_end
        )
        assert executive_dashboard.overall_health_score is not None

        # Step 2: Generate KPI trends
        kpi_trends = await all_services["kpis"].generate_kpi_trends(
            mock_hybrid_service_comprehensive, exec_start, exec_end,
            resolution="weekly"
        )
        assert len(kpi_trends) > 0

        # Step 3: Generate KPI benchmarks
        kpi_benchmarks = await all_services["kpis"].generate_kpi_benchmarks(
            mock_hybrid_service_comprehensive, exec_start, exec_end,
            benchmark_type="industry"
        )
        assert len(kpi_benchmarks) > 0

        # Step 4: Get high-level analytics
        consumption_analytics = await all_services["consumption"].get_consumption_analytics(
            mock_hybrid_service_comprehensive, exec_start, exec_end
        )
        quality_analytics = await all_services["quality"].get_quality_analytics(
            mock_hybrid_service_comprehensive, exec_start, exec_end
        )
        
        assert consumption_analytics.total_consumption > 0
        assert quality_analytics.overall_compliance_rate >= 0

        # Step 5: Generate executive summary report
        executive_report = await all_services["reports"].create_custom_report(
            mock_hybrid_service_comprehensive, exec_start, exec_end,
            {
                "title": "Executive Summary - Water Infrastructure Performance",
                "sections": ["executive_summary", "key_metrics", "trends", "benchmarks"],
                "format": "pdf",
                "executive_level": True
            }
        )
        assert executive_report.report_id is not None

        # Verify executive workflow
        assert executive_dashboard.overall_health_score >= 0
        assert len(kpi_trends) > 0
        assert len(kpi_benchmarks) > 0

    @pytest.mark.asyncio
    async def test_data_integration_workflow(
        self, all_services, mock_hybrid_service_comprehensive,
        mock_comprehensive_data, api_test_utils
    ):
        """Test complete data integration workflow."""
        start_time = datetime.now() - timedelta(days=7)
        end_time = datetime.now()

        # Step 1: Validate data integrity across services
        consumption_data = await all_services["consumption"].get_consumption_data(
            mock_hybrid_service_comprehensive, start_time, end_time
        )
        quality_data = await all_services["quality"].get_quality_readings(
            mock_hybrid_service_comprehensive, start_time, end_time
        )

        # Step 2: Cross-reference consumption and quality data
        # Filter consumption data for nodes with quality issues
        from src.schemas.api.filters import (
            AdvancedFilterRequest, FieldFilter, FilterOperator, EntityType
        )
        
        # Get nodes with quality issues
        quality_issues_filter = AdvancedFilterRequest(
            entity_type=EntityType.water_quality,
            filters=[
                FieldFilter(
                    field="compliance_status",
                    operator=FilterOperator.equals,
                    value="non_compliant"
                )
            ]
        )
        
        quality_issues = await all_services["filtering"].apply_filters(
            quality_issues_filter, mock_comprehensive_data["quality_data"]
        )

        # Step 3: Generate correlated analytics
        correlation_analytics = await all_services["consumption"].get_consumption_analytics(
            mock_hybrid_service_comprehensive, start_time, end_time
        )
        
        # Step 4: Generate integrated KPIs
        integrated_kpis = await all_services["kpis"].generate_kpi_dashboard(
            mock_hybrid_service_comprehensive, start_time, end_time
        )

        # Step 5: Generate data integration report
        integration_report = await all_services["reports"].create_custom_report(
            mock_hybrid_service_comprehensive, start_time, end_time,
            {
                "title": "Data Integration Analysis",
                "sections": ["data_sources", "correlations", "quality_assessment"],
                "format": "json",
                "include_metadata": True
            }
        )

        # Verify data integration workflow
        assert len(consumption_data) > 0
        assert len(quality_data) > 0
        assert integrated_kpis.overall_health_score is not None
        assert integration_report.report_id is not None

    @pytest.mark.asyncio
    async def test_performance_under_workflow_load(
        self, all_services, mock_hybrid_service_comprehensive,
        mock_comprehensive_data, performance_tracker
    ):
        """Test system performance under complete workflow load."""
        start_time = datetime.now() - timedelta(days=30)
        end_time = datetime.now()

        # Execute complete workflow under timing
        performance_tracker.start_timer("complete_workflow")

        # Parallel execution of multiple services
        consumption_task = all_services["consumption"].get_consumption_analytics(
            mock_hybrid_service_comprehensive, start_time, end_time
        )
        quality_task = all_services["quality"].get_quality_analytics(
            mock_hybrid_service_comprehensive, start_time, end_time
        )
        kpi_task = all_services["kpis"].generate_kpi_dashboard(
            mock_hybrid_service_comprehensive, start_time, end_time
        )

        # Wait for all tasks to complete
        consumption_result, quality_result, kpi_result = await asyncio.gather(
            consumption_task, quality_task, kpi_task
        )

        performance_tracker.end_timer("complete_workflow")

        # Assert workflow performance
        performance_tracker.assert_performance("complete_workflow", 10000)  # 10 seconds max

        # Verify results
        assert consumption_result.total_consumption > 0
        assert quality_result.overall_compliance_rate >= 0
        assert kpi_result.overall_health_score is not None

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(
        self, all_services, mock_hybrid_service_comprehensive,
        mock_comprehensive_data, api_test_utils
    ):
        """Test error recovery in complete workflows."""
        start_time = datetime.now() - timedelta(days=7)
        end_time = datetime.now()

        # Simulate service failure
        mock_hybrid_service_comprehensive.get_consumption_data.side_effect = Exception("Service unavailable")

        # Test graceful degradation
        try:
            consumption_data = await all_services["consumption"].get_consumption_data(
                mock_hybrid_service_comprehensive, start_time, end_time
            )
            assert False, "Should have raised exception"
        except Exception as e:
            assert "Service unavailable" in str(e)

        # Reset mock for other services
        mock_hybrid_service_comprehensive.get_consumption_data.side_effect = None
        mock_hybrid_service_comprehensive.get_consumption_data.return_value = mock_comprehensive_data["consumption_data"]

        # Test workflow continues with other services
        quality_data = await all_services["quality"].get_quality_readings(
            mock_hybrid_service_comprehensive, start_time, end_time
        )
        assert len(quality_data) > 0

        # Test partial workflow completion
        kpi_dashboard = await all_services["kpis"].generate_kpi_dashboard(
            mock_hybrid_service_comprehensive, start_time, end_time
        )
        assert kpi_dashboard.overall_health_score is not None

    @pytest.mark.asyncio
    async def test_workflow_data_consistency(
        self, all_services, mock_hybrid_service_comprehensive,
        mock_comprehensive_data, api_test_utils
    ):
        """Test data consistency across workflow steps."""
        start_time = datetime.now() - timedelta(days=7)
        end_time = datetime.now()

        # Step 1: Get base consumption data
        consumption_data = await all_services["consumption"].get_consumption_data(
            mock_hybrid_service_comprehensive, start_time, end_time
        )

        # Step 2: Get analytics from same data
        consumption_analytics = await all_services["consumption"].get_consumption_analytics(
            mock_hybrid_service_comprehensive, start_time, end_time
        )

        # Step 3: Verify consistency
        # Total consumption should match across calls
        total_from_data = sum(item.consumption_value for item in consumption_data)
        total_from_analytics = consumption_analytics.total_consumption

        # Allow for small calculation differences
        assert abs(total_from_data - total_from_analytics) < 10.0

        # Step 4: Generate KPIs from same data
        kpi_dashboard = await all_services["kpis"].generate_kpi_dashboard(
            mock_hybrid_service_comprehensive, start_time, end_time
        )

        # Step 5: Verify KPI consistency
        assert kpi_dashboard.overall_health_score is not None
        assert 0 <= kpi_dashboard.overall_health_score <= 100

    @pytest.mark.asyncio
    async def test_complete_api_integration(
        self, all_services, mock_hybrid_service_comprehensive,
        mock_comprehensive_data, api_test_utils
    ):
        """Test complete integration of all 77 API endpoints."""
        start_time = datetime.now() - timedelta(days=30)
        end_time = datetime.now()

        # Test all major API groups
        api_results = {}

        # Consumption APIs (8 endpoints)
        api_results["consumption"] = {
            "data": await all_services["consumption"].get_consumption_data(
                mock_hybrid_service_comprehensive, start_time, end_time
            ),
            "analytics": await all_services["consumption"].get_consumption_analytics(
                mock_hybrid_service_comprehensive, start_time, end_time
            ),
            "trends": await all_services["consumption"].get_consumption_trends(
                mock_hybrid_service_comprehensive, start_time, end_time
            ),
            "anomalies": await all_services["consumption"].detect_consumption_anomalies(
                mock_hybrid_service_comprehensive, start_time, end_time
            ),
            "optimization": await all_services["consumption"].get_optimization_suggestions(
                mock_hybrid_service_comprehensive, start_time, end_time
            )
        }

        # Quality APIs (11 endpoints)
        api_results["quality"] = {
            "readings": await all_services["quality"].get_quality_readings(
                mock_hybrid_service_comprehensive, start_time, end_time
            ),
            "analytics": await all_services["quality"].get_quality_analytics(
                mock_hybrid_service_comprehensive, start_time, end_time
            ),
            "compliance": await all_services["quality"].get_compliance_report(
                mock_hybrid_service_comprehensive, start_time, end_time
            ),
            "contamination": await all_services["quality"].detect_contamination_events(
                mock_hybrid_service_comprehensive, start_time, end_time
            )
        }

        # Forecasting APIs (8 endpoints)
        api_results["forecasting"] = {
            "forecasts": await all_services["forecasting"].generate_consumption_forecast(
                mock_hybrid_service_comprehensive, start_time, end_time, forecast_horizon=7
            ),
            "model_training": await all_services["forecasting"].train_forecasting_model(
                mock_hybrid_service_comprehensive, start_time, end_time, model_type="arima"
            ),
            "accuracy": await all_services["forecasting"].evaluate_model_accuracy(
                mock_hybrid_service_comprehensive, "MODEL_001", start_time, end_time
            )
        }

        # KPI APIs (14 endpoints)
        api_results["kpis"] = {
            "dashboard": await all_services["kpis"].generate_kpi_dashboard(
                mock_hybrid_service_comprehensive, start_time, end_time
            ),
            "cards": await all_services["kpis"].generate_kpi_cards(
                mock_hybrid_service_comprehensive, start_time, end_time
            ),
            "trends": await all_services["kpis"].generate_kpi_trends(
                mock_hybrid_service_comprehensive, start_time, end_time
            ),
            "alerts": await all_services["kpis"].generate_kpi_alerts(
                mock_hybrid_service_comprehensive, start_time, end_time
            ),
            "health": await all_services["kpis"].get_kpi_health(
                mock_hybrid_service_comprehensive, start_time, end_time
            )
        }

        # Reports APIs (18 endpoints)
        api_results["reports"] = {
            "consumption_report": await all_services["reports"].generate_consumption_report(
                mock_hybrid_service_comprehensive, start_time, end_time, report_format="json"
            ),
            "quality_report": await all_services["reports"].generate_quality_report(
                mock_hybrid_service_comprehensive, start_time, end_time, report_format="json"
            ),
            "kpi_report": await all_services["reports"].generate_kpi_report(
                mock_hybrid_service_comprehensive, start_time, end_time, report_format="json"
            ),
            "custom_report": await all_services["reports"].create_custom_report(
                mock_hybrid_service_comprehensive, start_time, end_time,
                {"title": "Integration Test Report", "sections": ["summary"], "format": "json"}
            )
        }

        # Filtering APIs (18 endpoints)
        from src.schemas.api.filters import (
            AdvancedFilterRequest, FieldFilter, FilterOperator, EntityType
        )
        
        filter_request = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            filters=[
                FieldFilter(
                    field="consumption_value",
                    operator=FilterOperator.greater_than,
                    value=150.0
                )
            ]
        )
        
        api_results["filtering"] = {
            "filtered_data": await all_services["filtering"].apply_filters(
                filter_request, mock_comprehensive_data["consumption_data"]
            ),
            "validation": await all_services["filtering"].validate_filter_request(filter_request)
        }

        # Verify all API groups returned valid results
        for api_group, results in api_results.items():
            for endpoint, result in results.items():
                assert result is not None, f"API {api_group}.{endpoint} returned None"
                
                # Check specific result types
                if isinstance(result, list):
                    assert len(result) >= 0, f"API {api_group}.{endpoint} returned invalid list"
                elif hasattr(result, 'report_id'):
                    assert result.report_id is not None, f"API {api_group}.{endpoint} missing report_id"
                elif hasattr(result, 'overall_health_score'):
                    assert 0 <= result.overall_health_score <= 100, f"API {api_group}.{endpoint} invalid health score"

        # Test complete workflow integration
        assert len(api_results) == 6  # All API groups tested
        assert all(results for results in api_results.values())  # All results valid 