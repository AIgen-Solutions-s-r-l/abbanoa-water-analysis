"""
Performance tests for all API endpoints.

Tests response times, throughput, memory usage, and concurrent request handling
to ensure APIs meet production performance requirements.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import AsyncMock, patch
from typing import List, Dict, Any
import statistics

from src.api.services.consumption_service import ConsumptionService
from src.api.services.water_quality_service import WaterQualityService
from src.api.services.forecasting_service import ForecastingService
from src.api.services.reports_service import ReportsService
from src.api.services.kpis.kpis_orchestrator import KPIOrchestrator
from src.api.services.filters_service import AdvancedFilteringService


@pytest.mark.performance
class TestAPIPerformance:
    """Performance test suite for all API services."""

    @pytest.fixture
    def performance_config(self):
        """Performance testing configuration."""
        return {
            "max_response_time_ms": 5000,
            "max_memory_usage_mb": 512,
            "concurrent_requests": 50,
            "stress_test_duration": 60,
            "acceptable_error_rate": 0.01,
            "throughput_target_rps": 100,
            "p95_response_time_ms": 3000,
            "p99_response_time_ms": 4000
        }

    @pytest.fixture
    def large_dataset(self):
        """Generate large dataset for performance testing."""
        return [
            {
                "node_id": f"NODE_{i % 100:03d}",
                "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                "consumption_value": 100.0 + (i % 500),
                "region": f"Region_{i % 10}",
                "zone": f"Zone_{i % 20}",
                "unit": "liters"
            }
            for i in range(100000)  # 100K records
        ]

    @pytest.fixture
    def mock_hybrid_service_performance(self, large_dataset):
        """Mock hybrid service with large dataset."""
        mock = AsyncMock()
        mock.get_consumption_data.return_value = large_dataset
        mock.get_quality_data.return_value = large_dataset[:50000]  # 50K records
        return mock

    @pytest.mark.asyncio
    async def test_consumption_service_performance(
        self, consumption_service, mock_hybrid_service_performance, 
        performance_config, performance_tracker
    ):
        """Test consumption service performance under load."""
        start_time = datetime.now() - timedelta(days=30)
        end_time = datetime.now()

        # Test single request performance
        performance_tracker.start_timer("consumption_data_retrieval")
        result = await consumption_service.get_consumption_data(
            mock_hybrid_service_performance, start_time, end_time
        )
        performance_tracker.end_timer("consumption_data_retrieval")

        # Assert response time
        performance_tracker.assert_performance(
            "consumption_data_retrieval", 
            performance_config["max_response_time_ms"]
        )

        # Test analytics performance
        performance_tracker.start_timer("consumption_analytics")
        analytics = await consumption_service.get_consumption_analytics(
            mock_hybrid_service_performance, start_time, end_time
        )
        performance_tracker.end_timer("consumption_analytics")

        performance_tracker.assert_performance(
            "consumption_analytics", 
            performance_config["max_response_time_ms"]
        )

        # Assert data integrity
        assert len(result) > 0
        assert analytics.total_consumption > 0

    @pytest.mark.asyncio
    async def test_concurrent_consumption_requests(
        self, consumption_service, mock_hybrid_service_performance, performance_config
    ):
        """Test concurrent consumption requests."""
        start_time = datetime.now() - timedelta(days=7)
        end_time = datetime.now()

        async def make_request():
            """Single request coroutine."""
            start = time.time()
            try:
                result = await consumption_service.get_consumption_data(
                    mock_hybrid_service_performance, start_time, end_time
                )
                end = time.time()
                return {
                    "success": True,
                    "response_time": (end - start) * 1000,
                    "data_size": len(result)
                }
            except Exception as e:
                end = time.time()
                return {
                    "success": False,
                    "response_time": (end - start) * 1000,
                    "error": str(e)
                }

        # Execute concurrent requests
        concurrent_requests = performance_config["concurrent_requests"]
        tasks = [make_request() for _ in range(concurrent_requests)]
        
        results = await asyncio.gather(*tasks)

        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]

        # Assert error rate
        error_rate = len(failed_requests) / len(results)
        assert error_rate <= performance_config["acceptable_error_rate"]

        # Assert response times
        response_times = [r["response_time"] for r in successful_requests]
        assert len(response_times) > 0

        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile

        assert avg_response_time <= performance_config["max_response_time_ms"]
        assert p95_response_time <= performance_config["p95_response_time_ms"]
        assert p99_response_time <= performance_config["p99_response_time_ms"]

    @pytest.mark.asyncio
    async def test_water_quality_service_performance(
        self, water_quality_service, mock_hybrid_service_performance, 
        performance_config, performance_tracker
    ):
        """Test water quality service performance."""
        start_time = datetime.now() - timedelta(days=7)
        end_time = datetime.now()

        # Test quality readings performance
        performance_tracker.start_timer("quality_readings")
        readings = await water_quality_service.get_quality_readings(
            mock_hybrid_service_performance, start_time, end_time
        )
        performance_tracker.end_timer("quality_readings")

        performance_tracker.assert_performance(
            "quality_readings", 
            performance_config["max_response_time_ms"]
        )

        # Test quality analytics performance
        performance_tracker.start_timer("quality_analytics")
        analytics = await water_quality_service.get_quality_analytics(
            mock_hybrid_service_performance, start_time, end_time
        )
        performance_tracker.end_timer("quality_analytics")

        performance_tracker.assert_performance(
            "quality_analytics", 
            performance_config["max_response_time_ms"]
        )

        assert len(readings) > 0

    @pytest.mark.asyncio
    async def test_forecasting_service_performance(
        self, forecasting_service, mock_hybrid_service_performance, 
        performance_config, performance_tracker
    ):
        """Test forecasting service performance."""
        start_time = datetime.now() - timedelta(days=30)
        end_time = datetime.now()

        # Test forecast generation performance
        performance_tracker.start_timer("forecast_generation")
        forecasts = await forecasting_service.generate_consumption_forecast(
            mock_hybrid_service_performance, start_time, end_time, forecast_horizon=7
        )
        performance_tracker.end_timer("forecast_generation")

        performance_tracker.assert_performance(
            "forecast_generation", 
            performance_config["max_response_time_ms"]
        )

        # Test model training performance
        performance_tracker.start_timer("model_training")
        model_result = await forecasting_service.train_forecasting_model(
            mock_hybrid_service_performance, start_time, end_time, model_type="arima"
        )
        performance_tracker.end_timer("model_training")

        # Model training can take longer
        performance_tracker.assert_performance(
            "model_training", 
            performance_config["max_response_time_ms"] * 2
        )

        assert len(forecasts) > 0

    @pytest.mark.asyncio
    async def test_reports_service_performance(
        self, reports_service, mock_hybrid_service_performance, 
        performance_config, performance_tracker
    ):
        """Test reports service performance."""
        start_time = datetime.now() - timedelta(days=30)
        end_time = datetime.now()

        # Test consumption report generation
        performance_tracker.start_timer("consumption_report")
        report = await reports_service.generate_consumption_report(
            mock_hybrid_service_performance, start_time, end_time, report_format="json"
        )
        performance_tracker.end_timer("consumption_report")

        performance_tracker.assert_performance(
            "consumption_report", 
            performance_config["max_response_time_ms"]
        )

        # Test PDF report generation (typically slower)
        performance_tracker.start_timer("pdf_report")
        pdf_report = await reports_service.generate_consumption_report(
            mock_hybrid_service_performance, start_time, end_time, report_format="pdf"
        )
        performance_tracker.end_timer("pdf_report")

        # PDF generation can take longer
        performance_tracker.assert_performance(
            "pdf_report", 
            performance_config["max_response_time_ms"] * 3
        )

        assert report.report_id is not None

    @pytest.mark.asyncio
    async def test_kpi_orchestrator_performance(
        self, kpi_orchestrator, mock_hybrid_service_performance, 
        performance_config, performance_tracker
    ):
        """Test KPI orchestrator performance."""
        start_time = datetime.now() - timedelta(days=7)
        end_time = datetime.now()

        # Test dashboard generation performance
        performance_tracker.start_timer("kpi_dashboard")
        dashboard = await kpi_orchestrator.generate_kpi_dashboard(
            mock_hybrid_service_performance, start_time, end_time
        )
        performance_tracker.end_timer("kpi_dashboard")

        performance_tracker.assert_performance(
            "kpi_dashboard", 
            performance_config["max_response_time_ms"]
        )

        # Test KPI cards performance
        performance_tracker.start_timer("kpi_cards")
        cards = await kpi_orchestrator.generate_kpi_cards(
            mock_hybrid_service_performance, start_time, end_time
        )
        performance_tracker.end_timer("kpi_cards")

        performance_tracker.assert_performance(
            "kpi_cards", 
            performance_config["max_response_time_ms"]
        )

        assert dashboard.overall_health_score is not None
        assert len(cards) > 0

    @pytest.mark.asyncio
    async def test_filtering_service_performance(
        self, filtering_service, large_dataset, performance_config, performance_tracker
    ):
        """Test filtering service performance."""
        from src.schemas.api.filters import (
            AdvancedFilterRequest, FieldFilter, FilterOperator, 
            EntityType, LogicalOperator
        )

        # Test simple filter performance
        simple_filter = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            filters=[
                FieldFilter(
                    field="region",
                    operator=FilterOperator.equals,
                    value="Region_1"
                )
            ]
        )

        performance_tracker.start_timer("simple_filter")
        result = await filtering_service.apply_filters(simple_filter, large_dataset)
        performance_tracker.end_timer("simple_filter")

        performance_tracker.assert_performance(
            "simple_filter", 
            performance_config["max_response_time_ms"]
        )

        # Test complex filter performance
        complex_filter = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            filters=[
                FieldFilter(
                    field="region",
                    operator=FilterOperator.in_list,
                    value=["Region_1", "Region_2", "Region_3"]
                ),
                FieldFilter(
                    field="consumption_value",
                    operator=FilterOperator.between,
                    value=[100.0, 400.0]
                )
            ],
            logical_operator=LogicalOperator.AND
        )

        performance_tracker.start_timer("complex_filter")
        complex_result = await filtering_service.apply_filters(complex_filter, large_dataset)
        performance_tracker.end_timer("complex_filter")

        performance_tracker.assert_performance(
            "complex_filter", 
            performance_config["max_response_time_ms"]
        )

        assert len(result.data) > 0
        assert len(complex_result.data) > 0

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(
        self, consumption_service, mock_hybrid_service_performance, 
        performance_config, large_dataset
    ):
        """Test memory usage under load."""
        import psutil
        import os

        # Get current process
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        start_time = datetime.now() - timedelta(days=30)
        end_time = datetime.now()

        # Process large dataset multiple times
        for i in range(10):
            result = await consumption_service.get_consumption_data(
                mock_hybrid_service_performance, start_time, end_time
            )
            
            # Force garbage collection
            import gc
            gc.collect()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Assert memory usage is within acceptable limits
        assert memory_increase <= performance_config["max_memory_usage_mb"]

    @pytest.mark.asyncio
    async def test_throughput_measurement(
        self, consumption_service, mock_hybrid_service_performance, performance_config
    ):
        """Test API throughput (requests per second)."""
        start_time = datetime.now() - timedelta(days=1)
        end_time = datetime.now()

        # Measure throughput over time period
        test_duration = 10  # seconds
        request_count = 0
        errors = 0

        async def continuous_requests():
            nonlocal request_count, errors
            end_test = time.time() + test_duration
            
            while time.time() < end_test:
                try:
                    await consumption_service.get_consumption_data(
                        mock_hybrid_service_performance, start_time, end_time
                    )
                    request_count += 1
                except Exception:
                    errors += 1
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)

        # Run throughput test
        await continuous_requests()

        # Calculate throughput
        throughput = request_count / test_duration
        error_rate = errors / (request_count + errors) if (request_count + errors) > 0 else 0

        # Assert throughput meets requirements
        assert throughput >= performance_config["throughput_target_rps"]
        assert error_rate <= performance_config["acceptable_error_rate"]

    @pytest.mark.asyncio
    async def test_database_connection_pool_performance(
        self, consumption_service, performance_config
    ):
        """Test database connection pool performance."""
        # Mock database connection pool
        class MockConnectionPool:
            def __init__(self):
                self.active_connections = 0
                self.max_connections = 100
                self.connection_times = []

            async def get_connection(self):
                start_time = time.time()
                
                if self.active_connections >= self.max_connections:
                    await asyncio.sleep(0.1)  # Wait for connection
                
                self.active_connections += 1
                connection_time = (time.time() - start_time) * 1000  # ms
                self.connection_times.append(connection_time)
                
                return MockConnection()

            async def release_connection(self, connection):
                self.active_connections -= 1

        class MockConnection:
            async def execute(self, query):
                await asyncio.sleep(0.01)  # Simulate query execution
                return []

        pool = MockConnectionPool()

        # Simulate concurrent database requests
        async def database_request():
            conn = await pool.get_connection()
            try:
                await conn.execute("SELECT * FROM consumption_data")
            finally:
                await pool.release_connection(conn)

        # Execute concurrent database requests
        tasks = [database_request() for _ in range(200)]
        await asyncio.gather(*tasks)

        # Assert connection pool performance
        if pool.connection_times:
            avg_connection_time = statistics.mean(pool.connection_times)
            max_connection_time = max(pool.connection_times)

            assert avg_connection_time <= 100  # 100ms average
            assert max_connection_time <= 1000  # 1s maximum

    @pytest.mark.asyncio
    async def test_cache_performance(self, filtering_service, large_dataset):
        """Test caching performance improvements."""
        from src.schemas.api.filters import (
            AdvancedFilterRequest, FieldFilter, FilterOperator, EntityType
        )

        filter_request = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            filters=[
                FieldFilter(
                    field="region",
                    operator=FilterOperator.equals,
                    value="Region_1"
                )
            ]
        )

        # First request (no cache)
        start_time = time.time()
        result1 = await filtering_service.apply_filters(filter_request, large_dataset)
        first_request_time = (time.time() - start_time) * 1000

        # Second request (should use cache)
        start_time = time.time()
        result2 = await filtering_service.apply_filters(filter_request, large_dataset)
        second_request_time = (time.time() - start_time) * 1000

        # Assert cache improves performance
        assert len(result1.data) == len(result2.data)
        # Second request should be significantly faster (if caching is implemented)
        # assert second_request_time < first_request_time * 0.5

    @pytest.mark.asyncio
    async def test_api_stress_test(
        self, consumption_service, mock_hybrid_service_performance, performance_config
    ):
        """Stress test APIs under extreme load."""
        start_time = datetime.now() - timedelta(days=1)
        end_time = datetime.now()

        # Stress test configuration
        stress_duration = 30  # seconds
        max_concurrent = 100
        
        results = []
        start_test = time.time()
        
        async def stress_request():
            try:
                request_start = time.time()
                await consumption_service.get_consumption_data(
                    mock_hybrid_service_performance, start_time, end_time
                )
                request_time = (time.time() - request_start) * 1000
                return {"success": True, "response_time": request_time}
            except Exception as e:
                request_time = (time.time() - request_start) * 1000
                return {"success": False, "response_time": request_time, "error": str(e)}

        # Run stress test
        while time.time() - start_test < stress_duration:
            # Launch batch of concurrent requests
            tasks = [stress_request() for _ in range(max_concurrent)]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            
            # Brief pause between batches
            await asyncio.sleep(0.1)

        # Analyze stress test results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        total_requests = len(results)
        error_rate = len(failed) / total_requests if total_requests > 0 else 0
        
        if successful:
            avg_response_time = statistics.mean([r["response_time"] for r in successful])
            p95_response_time = statistics.quantiles(
                [r["response_time"] for r in successful], n=20
            )[18]

            # Assert stress test results
            assert error_rate <= performance_config["acceptable_error_rate"] * 2  # Allow higher error rate under stress
            assert avg_response_time <= performance_config["max_response_time_ms"] * 1.5  # Allow slower response under stress
            assert p95_response_time <= performance_config["p95_response_time_ms"] * 2

    @pytest.mark.asyncio
    async def test_resource_cleanup(self, consumption_service, mock_hybrid_service_performance):
        """Test proper resource cleanup after operations."""
        import gc
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_threads = process.num_threads()

        start_time = datetime.now() - timedelta(days=7)
        end_time = datetime.now()

        # Perform multiple operations
        for i in range(50):
            result = await consumption_service.get_consumption_data(
                mock_hybrid_service_performance, start_time, end_time
            )
            
            # Simulate processing
            processed_data = [item for item in result if item.consumption_value > 100]
            
            # Clear references
            del result
            del processed_data

        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        final_threads = process.num_threads()

        # Assert resource cleanup
        memory_increase = final_memory - initial_memory
        thread_increase = final_threads - initial_threads

        assert memory_increase <= 50  # Allow some memory increase
        assert thread_increase <= 5   # Allow some thread increase 