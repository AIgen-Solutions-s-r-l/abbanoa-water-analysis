"""
Mock configuration for tests to avoid Google Cloud dependencies.
This file can be used instead of conftest.py for testing without external dependencies.
"""

import sys
from unittest.mock import MagicMock

# Mock google.cloud module before any imports
sys.modules['google'] = MagicMock()
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.bigquery'] = MagicMock()

# Now we can safely import the rest
import asyncio
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator, Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch

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
async def mock_hybrid_service():
    """Provide a mocked HybridDataService for testing."""
    service = MagicMock()
    service.get_sensor_readings = AsyncMock(return_value=None)
    service.get_quality_data = AsyncMock(return_value=None)
    return service


@pytest.fixture
async def mock_consumption_service():
    """Provide a mocked ConsumptionService for testing."""
    service = MagicMock()
    service.calculate_consumption = AsyncMock(return_value={})
    return service


@pytest.fixture
def quality_config_mock():
    """Mock quality configuration for testing."""
    from unittest.mock import MagicMock
    config = MagicMock()
    
    # Mock temperature thresholds
    config.temperature.optimal = 15.0
    config.temperature.min_normal = 10.0
    config.temperature.max_normal = 20.0
    config.temperature.alert_threshold = 25.0
    config.temperature.high_alert_threshold = 30.0
    
    # Mock pressure thresholds
    config.pressure.optimal = 4.0
    config.pressure.minimum = 2.0
    config.pressure.critical = 1.0
    config.pressure.maximum = 6.0
    
    # Mock flow thresholds
    config.flow.minimum = 0.1
    config.flow.stagnation = 0.5
    config.flow.normal_min = 50.0
    config.flow.normal_max = 150.0
    config.flow.normal_value = 100.0
    
    # Mock quality score thresholds
    config.quality_score.excellent = 0.9
    config.quality_score.good = 0.7
    config.quality_score.acceptable = 0.6
    config.quality_score.minimum = 0.85
    config.quality_score.normal = 0.95
    config.quality_score.maximum = 1.0
    
    # Mock compliance thresholds
    config.compliance.quality_warning = 90.0
    config.compliance.quality_target = 98.0
    config.compliance.temperature_warning = 95.0
    config.compliance.temperature_target = 99.0
    config.compliance.pressure_warning = 90.0
    config.compliance.contamination_warning = 5
    config.compliance.contamination_target = 0
    
    # Mock quality grades
    config.quality_grades.grade_a = 90.0
    config.quality_grades.grade_b = 80.0
    config.quality_grades.grade_c = 70.0
    config.quality_grades.grade_d = 60.0
    
    # Mock get_grade method
    def get_grade(percentage):
        if percentage >= 90: return MagicMock(value='A')
        elif percentage >= 80: return MagicMock(value='B')
        elif percentage >= 70: return MagicMock(value='C')
        elif percentage >= 60: return MagicMock(value='D')
        else: return MagicMock(value='F')
    
    config.quality_grades.get_grade = get_grade
    
    return config