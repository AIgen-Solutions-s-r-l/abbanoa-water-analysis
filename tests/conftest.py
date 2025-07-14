"""
Pytest configuration and shared fixtures for comprehensive API testing.

This module provides test configuration, fixtures, and utilities for testing
the complete 77-endpoint API suite across all service domains.
"""

import asyncio
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator, Dict, Any, List
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import the main FastAPI app (assuming it exists)
# from src.main import app
from src.infrastructure.data.hybrid_data_service import HybridDataService
from src.api.services.consumption_service import ConsumptionService
from src.api.services.water_quality_service import WaterQualityService
from src.api.services.forecasting_service import ForecastingService
from src.api.services.reports_service import ReportsService
from src.api.services.kpis.kpis_orchestrator import KPIOrchestrator
from src.api.services.filters_service import AdvancedFilteringService


# Test configuration
TEST_DATABASE_URL = "sqlite:///./test_database.db"
TEST_API_BASE_URL = "http://testserver"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def hybrid_service() -> HybridDataService:
    """Provide a test instance of HybridDataService."""
    return HybridDataService()


@pytest.fixture
async def consumption_service() -> ConsumptionService:
    """Provide a test instance of ConsumptionService."""
    return ConsumptionService()


@pytest.fixture
async def water_quality_service() -> WaterQualityService:
    """Provide a test instance of WaterQualityService."""
    return WaterQualityService()


@pytest.fixture
async def forecasting_service() -> ForecastingService:
    """Provide a test instance of ForecastingService."""
    return ForecastingService()


@pytest.fixture
async def reports_service() -> ReportsService:
    """Provide a test instance of ReportsService."""
    return ReportsService()


@pytest.fixture
async def kpi_orchestrator() -> KPIOrchestrator:
    """Provide a test instance of KPIOrchestrator."""
    return KPIOrchestrator()


@pytest.fixture
async def filtering_service() -> AdvancedFilteringService:
    """Provide a test instance of AdvancedFilteringService."""
    return AdvancedFilteringService()


# @pytest.fixture
# async def test_client() -> AsyncGenerator[AsyncClient, None]:
#     """Provide async test client for API integration tests."""
#     async with AsyncClient(app=app, base_url=TEST_API_BASE_URL) as client:
#         yield client


@pytest.fixture
def test_date_range() -> Dict[str, datetime]:
    """Provide standard test date range."""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=30)
    return {
        "start_time": start_time,
        "end_time": end_time
    }


@pytest.fixture
def test_nodes() -> List[str]:
    """Provide standard test node IDs."""
    return ["NODE_001", "NODE_002", "NODE_003", "NODE_004", "NODE_005"]


@pytest.fixture
def sample_consumption_data() -> List[Dict[str, Any]]:
    """Provide sample consumption data for testing."""
    base_time = datetime.now() - timedelta(days=7)
    data = []
    
    for i in range(100):
        data.append({
            "node_id": f"NODE_{i % 5:03d}",
            "timestamp": (base_time + timedelta(hours=i)).isoformat(),
            "consumption_value": 100 + (i * 10) % 500,
            "region": f"Region_{i % 3}",
            "zone": f"Zone_{i % 10}",
            "unit": "liters",
            "quality": "good" if i % 4 != 0 else "warning"
        })
    
    return data


@pytest.fixture
def sample_quality_data() -> List[Dict[str, Any]]:
    """Provide sample water quality data for testing."""
    base_time = datetime.now() - timedelta(days=7)
    data = []
    
    for i in range(100):
        data.append({
            "sensor_id": f"SENSOR_{i % 8:03d}",
            "timestamp": (base_time + timedelta(hours=i)).isoformat(),
            "ph_level": 7.0 + (i % 20 - 10) * 0.1,
            "temperature": 20.0 + (i % 15),
            "turbidity": 1.0 + (i % 10) * 0.5,
            "dissolved_oxygen": 8.0 + (i % 8) * 0.2,
            "conductivity": 500 + (i % 100),
            "compliance_status": "compliant" if i % 5 != 0 else "non_compliant",
            "region": f"Region_{i % 3}",
            "location": f"Location_{i % 20}"
        })
    
    return data


@pytest.fixture
def sample_forecast_data() -> List[Dict[str, Any]]:
    """Provide sample forecasting data for testing."""
    base_time = datetime.now()
    data = []
    
    for i in range(50):
        future_time = base_time + timedelta(days=i)
        data.append({
            "node_id": f"NODE_{i % 5:03d}",
            "timestamp": future_time.isoformat(),
            "predicted_consumption": 200 + (i * 15) % 400,
            "confidence_interval": [180 + (i * 15) % 400, 220 + (i * 15) % 400],
            "model_type": "arima" if i % 2 == 0 else "lstm",
            "accuracy_score": 0.85 + (i % 10) * 0.01,
            "forecast_horizon": "short_term" if i < 7 else "medium_term" if i < 30 else "long_term"
        })
    
    return data


@pytest.fixture
def test_performance_config() -> Dict[str, Any]:
    """Provide performance testing configuration."""
    return {
        "max_response_time_ms": 5000,
        "max_memory_usage_mb": 512,
        "concurrent_requests": 10,
        "stress_test_duration": 30,
        "acceptable_error_rate": 0.01
    }


@pytest.fixture
def test_pagination_config() -> Dict[str, Any]:
    """Provide pagination testing configuration."""
    return {
        "default_page_size": 50,
        "max_page_size": 1000,
        "test_page_sizes": [1, 10, 50, 100, 500]
    }


# Database fixtures for integration testing

@pytest_asyncio.fixture
async def test_database():
    """Set up and tear down test database."""
    # Setup test database
    # This would create a temporary database for testing
    yield
    # Cleanup test database
    pass


@pytest.fixture
def mock_external_api():
    """Mock external API dependencies."""
    class MockExternalAPI:
        async def get_weather_data(self):
            return {"temperature": 25.0, "humidity": 60.0}
        
        async def get_maintenance_schedule(self):
            return {"next_maintenance": "2024-01-15", "priority": "medium"}
    
    return MockExternalAPI()


# Test data generators

class TestDataGenerator:
    """Generate realistic test data for comprehensive testing."""
    
    @staticmethod
    def generate_consumption_timeseries(
        node_count: int = 5,
        days: int = 30,
        interval_hours: int = 1
    ) -> List[Dict[str, Any]]:
        """Generate realistic consumption time series data."""
        data = []
        base_time = datetime.now() - timedelta(days=days)
        
        for node_id in range(node_count):
            base_consumption = 100 + node_id * 50
            
            for hour in range(0, days * 24, interval_hours):
                timestamp = base_time + timedelta(hours=hour)
                
                # Add realistic patterns (daily cycle, noise, trends)
                daily_pattern = 50 * (1 + 0.5 * abs(timestamp.hour - 12) / 12)
                noise = (hour % 7 - 3) * 10
                trend = hour * 0.1
                
                consumption = base_consumption + daily_pattern + noise + trend
                
                data.append({
                    "node_id": f"NODE_{node_id:03d}",
                    "timestamp": timestamp.isoformat(),
                    "consumption_value": max(0, consumption),
                    "region": f"Region_{node_id % 3}",
                    "zone": f"Zone_{node_id % 2}",
                    "unit": "liters"
                })
        
        return data
    
    @staticmethod
    def generate_quality_readings(
        sensor_count: int = 8,
        days: int = 7,
        interval_hours: int = 4
    ) -> List[Dict[str, Any]]:
        """Generate realistic water quality readings."""
        data = []
        base_time = datetime.now() - timedelta(days=days)
        
        for sensor_id in range(sensor_count):
            for hour in range(0, days * 24, interval_hours):
                timestamp = base_time + timedelta(hours=hour)
                
                # Simulate realistic quality parameters
                ph_base = 7.2 + (sensor_id % 3 - 1) * 0.3
                ph_variation = (hour % 12 - 6) * 0.05
                ph_level = ph_base + ph_variation
                
                temp_base = 22 + sensor_id * 0.5
                temp_variation = 5 * abs((hour % 24 - 12) / 12)
                temperature = temp_base + temp_variation
                
                data.append({
                    "sensor_id": f"SENSOR_{sensor_id:03d}",
                    "timestamp": timestamp.isoformat(),
                    "ph_level": round(ph_level, 2),
                    "temperature": round(temperature, 1),
                    "turbidity": max(0.1, 1.0 + (hour % 10) * 0.2),
                    "dissolved_oxygen": 8.5 + (hour % 8 - 4) * 0.1,
                    "conductivity": 450 + sensor_id * 20 + (hour % 20),
                    "compliance_status": "compliant" if 6.5 <= ph_level <= 8.5 else "non_compliant"
                })
        
        return data


@pytest.fixture
def test_data_generator() -> TestDataGenerator:
    """Provide test data generator instance."""
    return TestDataGenerator()


# Performance testing utilities

class PerformanceTracker:
    """Track performance metrics during testing."""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation."""
        self.metrics[operation] = {"start": datetime.now()}
    
    def end_timer(self, operation: str):
        """End timing an operation."""
        if operation in self.metrics:
            end_time = datetime.now()
            duration = (end_time - self.metrics[operation]["start"]).total_seconds() * 1000
            self.metrics[operation]["duration_ms"] = duration
            self.metrics[operation]["end"] = end_time
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all performance metrics."""
        return self.metrics
    
    def assert_performance(self, operation: str, max_duration_ms: float):
        """Assert operation completed within time limit."""
        if operation in self.metrics and "duration_ms" in self.metrics[operation]:
            actual_duration = self.metrics[operation]["duration_ms"]
            assert actual_duration <= max_duration_ms, \
                f"Operation '{operation}' took {actual_duration}ms, expected <= {max_duration_ms}ms"


@pytest.fixture
def performance_tracker() -> PerformanceTracker:
    """Provide performance tracking utilities."""
    return PerformanceTracker()


# Test markers for organizing test execution

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line("markers", "integration: Integration tests for API endpoints")
    config.addinivalue_line("markers", "performance: Performance and load tests")
    config.addinivalue_line("markers", "e2e: End-to-end workflow tests")
    config.addinivalue_line("markers", "slow: Tests that take longer to execute")
    config.addinivalue_line("markers", "consumption: Tests related to consumption API")
    config.addinivalue_line("markers", "quality: Tests related to water quality API")
    config.addinivalue_line("markers", "forecasting: Tests related to forecasting API")
    config.addinivalue_line("markers", "reports: Tests related to reports API")
    config.addinivalue_line("markers", "kpis: Tests related to KPIs API")
    config.addinivalue_line("markers", "filtering: Tests related to filtering API")


# Test utilities for common assertions

class APITestUtils:
    """Utilities for common API testing patterns."""
    
    @staticmethod
    def assert_valid_response_structure(response_data: Dict[str, Any], required_fields: List[str]):
        """Assert response has required structure."""
        for field in required_fields:
            assert field in response_data, f"Missing required field: {field}"
    
    @staticmethod
    def assert_pagination_metadata(metadata: Dict[str, Any]):
        """Assert pagination metadata is valid."""
        required_fields = ["total_count", "page_count", "current_page", "has_next_page", "has_previous_page"]
        for field in required_fields:
            assert field in metadata, f"Missing pagination field: {field}"
        
        assert isinstance(metadata["total_count"], int), "total_count must be integer"
        assert metadata["total_count"] >= 0, "total_count must be non-negative"
        assert isinstance(metadata["current_page"], int), "current_page must be integer"
        assert metadata["current_page"] >= 1, "current_page must be >= 1"
    
    @staticmethod
    def assert_datetime_format(datetime_str: str):
        """Assert datetime string is in valid ISO format."""
        try:
            datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except ValueError:
            assert False, f"Invalid datetime format: {datetime_str}"
    
    @staticmethod
    def assert_performance_metrics(metrics: Dict[str, Any], max_response_time: float = 5000):
        """Assert performance metrics are within acceptable ranges."""
        if "execution_time_ms" in metrics:
            assert metrics["execution_time_ms"] <= max_response_time, \
                f"Response time {metrics['execution_time_ms']}ms exceeds limit {max_response_time}ms"


@pytest.fixture
def api_test_utils() -> APITestUtils:
    """Provide API testing utilities."""
    return APITestUtils()


# Error simulation utilities

class ErrorSimulator:
    """Simulate various error conditions for testing."""
    
    @staticmethod
    def simulate_database_error():
        """Simulate database connection error."""
        raise ConnectionError("Database connection failed")
    
    @staticmethod
    def simulate_timeout_error():
        """Simulate request timeout."""
        raise TimeoutError("Request timed out")
    
    @staticmethod
    def simulate_invalid_data():
        """Generate invalid test data."""
        return {
            "invalid_timestamp": "not-a-date",
            "negative_value": -100,
            "missing_required_field": None
        }


@pytest.fixture
def error_simulator() -> ErrorSimulator:
    """Provide error simulation utilities."""
    return ErrorSimulator() 