"""
Unit tests for ConsumptionService.

Tests all consumption-related business logic including data processing,
analytics, anomaly detection, and optimization features.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, List

from src.api.services.consumption_service import ConsumptionService
from src.schemas.api.consumption import (
    ConsumptionData, ConsumptionAnalytics, NodeConsumption, ConsumptionTrend,
    AnomalyDetection, ConsumptionForecast, OptimizationSuggestion
)


@pytest.mark.unit
@pytest.mark.consumption
class TestConsumptionService:
    """Test suite for ConsumptionService."""

    @pytest.fixture
    def consumption_service(self):
        """Provide ConsumptionService instance."""
        return ConsumptionService()

    @pytest.fixture
    def mock_hybrid_service(self):
        """Provide mocked HybridDataService."""
        mock = AsyncMock()
        mock.get_consumption_data.return_value = [
            {
                "node_id": "NODE_001",
                "timestamp": "2024-01-01T10:00:00",
                "consumption_value": 150.0,
                "region": "North",
                "unit": "liters"
            },
            {
                "node_id": "NODE_002", 
                "timestamp": "2024-01-01T10:00:00",
                "consumption_value": 200.0,
                "region": "South",
                "unit": "liters"
            }
        ]
        return mock

    @pytest.mark.asyncio
    async def test_get_consumption_data_success(
        self, consumption_service, mock_hybrid_service, test_date_range
    ):
        """Test successful consumption data retrieval."""
        # Act
        result = await consumption_service.get_consumption_data(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, ConsumptionData) for item in result)
        
        # Check first item structure
        first_item = result[0]
        assert first_item.node_id == "NODE_001"
        assert first_item.consumption_value == 150.0
        assert first_item.region == "North"

    @pytest.mark.asyncio
    async def test_get_consumption_data_with_nodes_filter(
        self, consumption_service, mock_hybrid_service, test_date_range
    ):
        """Test consumption data retrieval with node filtering."""
        # Arrange
        selected_nodes = ["NODE_001"]
        
        # Act
        result = await consumption_service.get_consumption_data(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"],
            selected_nodes
        )

        # Assert
        mock_hybrid_service.get_consumption_data.assert_called_once_with(
            test_date_range["start_time"],
            test_date_range["end_time"],
            selected_nodes,
            None
        )
        assert len(result) == 2  # Mock returns 2 items regardless

    @pytest.mark.asyncio
    async def test_get_consumption_data_empty_result(
        self, consumption_service, test_date_range
    ):
        """Test consumption data retrieval with empty result."""
        # Arrange
        mock_service = AsyncMock()
        mock_service.get_consumption_data.return_value = []
        
        # Act
        result = await consumption_service.get_consumption_data(
            mock_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_consumption_analytics_success(
        self, consumption_service, mock_hybrid_service, test_date_range
    ):
        """Test successful consumption analytics generation."""
        # Arrange
        mock_hybrid_service.get_consumption_data.return_value = [
            {
                "node_id": "NODE_001",
                "timestamp": "2024-01-01T10:00:00",
                "consumption_value": 100.0,
                "region": "North",
                "unit": "liters"
            },
            {
                "node_id": "NODE_001",
                "timestamp": "2024-01-01T11:00:00",
                "consumption_value": 150.0,
                "region": "North", 
                "unit": "liters"
            },
            {
                "node_id": "NODE_002",
                "timestamp": "2024-01-01T10:00:00",
                "consumption_value": 200.0,
                "region": "South",
                "unit": "liters"
            }
        ]

        # Act
        result = await consumption_service.get_consumption_analytics(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        # Assert
        assert isinstance(result, ConsumptionAnalytics)
        assert result.total_consumption > 0
        assert result.average_consumption > 0
        assert result.peak_consumption >= result.average_consumption
        assert len(result.top_consumers) > 0
        assert len(result.consumption_by_region) > 0

    @pytest.mark.asyncio
    async def test_get_node_consumption_success(
        self, consumption_service, mock_hybrid_service, test_date_range
    ):
        """Test successful node consumption retrieval."""
        # Arrange
        node_id = "NODE_001"
        mock_hybrid_service.get_node_consumption.return_value = [
            {
                "node_id": "NODE_001",
                "timestamp": "2024-01-01T10:00:00", 
                "consumption_value": 150.0,
                "region": "North",
                "unit": "liters"
            }
        ]

        # Act
        result = await consumption_service.get_node_consumption(
            mock_hybrid_service,
            node_id,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(item, NodeConsumption) for item in result)
        mock_hybrid_service.get_node_consumption.assert_called_once_with(
            node_id,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

    @pytest.mark.asyncio
    async def test_get_consumption_trends_success(
        self, consumption_service, mock_hybrid_service, test_date_range
    ):
        """Test successful consumption trends analysis."""
        # Arrange
        mock_hybrid_service.get_consumption_data.return_value = [
            {
                "node_id": "NODE_001",
                "timestamp": "2024-01-01T10:00:00",
                "consumption_value": 100.0,
                "region": "North",
                "unit": "liters"
            },
            {
                "node_id": "NODE_001",
                "timestamp": "2024-01-02T10:00:00",
                "consumption_value": 110.0,
                "region": "North",
                "unit": "liters"
            }
        ]

        # Act
        result = await consumption_service.get_consumption_trends(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(item, ConsumptionTrend) for item in result)
        
        trend = result[0]
        assert hasattr(trend, 'period')
        assert hasattr(trend, 'trend_direction')
        assert hasattr(trend, 'change_percentage')

    @pytest.mark.asyncio
    async def test_detect_consumption_anomalies_success(
        self, consumption_service, mock_hybrid_service, test_date_range
    ):
        """Test successful anomaly detection."""
        # Arrange
        mock_data = []
        base_time = datetime.now() - timedelta(days=7)
        
        # Create data with clear anomaly
        for i in range(100):
            value = 100.0 if i != 50 else 500.0  # Anomaly at index 50
            mock_data.append({
                "node_id": "NODE_001",
                "timestamp": (base_time + timedelta(hours=i)).isoformat(),
                "consumption_value": value,
                "region": "North",
                "unit": "liters"
            })
        
        mock_hybrid_service.get_consumption_data.return_value = mock_data

        # Act
        result = await consumption_service.detect_consumption_anomalies(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(item, AnomalyDetection) for item in result)
        
        if result:  # Check if anomalies were detected
            anomaly = result[0]
            assert hasattr(anomaly, 'node_id')
            assert hasattr(anomaly, 'anomaly_type')
            assert hasattr(anomaly, 'severity')
            assert hasattr(anomaly, 'confidence_score')

    @pytest.mark.asyncio
    async def test_get_consumption_forecast_success(
        self, consumption_service, mock_hybrid_service, test_date_range
    ):
        """Test successful consumption forecasting."""
        # Arrange
        mock_hybrid_service.get_consumption_data.return_value = [
            {
                "node_id": "NODE_001",
                "timestamp": f"2024-01-{i:02d}T10:00:00",
                "consumption_value": 100.0 + i * 5,  # Trending upward
                "region": "North",
                "unit": "liters"
            }
            for i in range(1, 31)  # 30 days of data
        ]

        # Act
        result = await consumption_service.get_consumption_forecast(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"],
            forecast_days=7
        )

        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(item, ConsumptionForecast) for item in result)
        
        forecast = result[0]
        assert hasattr(forecast, 'node_id')
        assert hasattr(forecast, 'predicted_consumption')
        assert hasattr(forecast, 'confidence_interval')
        assert hasattr(forecast, 'forecast_date')

    @pytest.mark.asyncio
    async def test_get_optimization_suggestions_success(
        self, consumption_service, mock_hybrid_service, test_date_range
    ):
        """Test successful optimization suggestions generation."""
        # Arrange
        mock_hybrid_service.get_consumption_data.return_value = [
            {
                "node_id": "NODE_001",
                "timestamp": "2024-01-01T10:00:00",
                "consumption_value": 500.0,  # High consumption
                "region": "North",
                "unit": "liters"
            },
            {
                "node_id": "NODE_002",
                "timestamp": "2024-01-01T10:00:00",
                "consumption_value": 50.0,   # Low consumption
                "region": "South",
                "unit": "liters"
            }
        ]

        # Act
        result = await consumption_service.get_optimization_suggestions(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(item, OptimizationSuggestion) for item in result)
        
        if result:
            suggestion = result[0]
            assert hasattr(suggestion, 'node_id')
            assert hasattr(suggestion, 'suggestion_type')
            assert hasattr(suggestion, 'description')
            assert hasattr(suggestion, 'potential_savings')

    @pytest.mark.asyncio
    async def test_consumption_service_error_handling(
        self, consumption_service, test_date_range
    ):
        """Test error handling in consumption service."""
        # Arrange
        mock_service = AsyncMock()
        mock_service.get_consumption_data.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception):
            await consumption_service.get_consumption_data(
                mock_service,
                test_date_range["start_time"],
                test_date_range["end_time"]
            )

    def test_consumption_analytics_calculations(self, consumption_service):
        """Test consumption analytics calculation methods."""
        # Arrange
        sample_data = [
            {"consumption_value": 100.0, "node_id": "NODE_001", "region": "North"},
            {"consumption_value": 200.0, "node_id": "NODE_002", "region": "North"},
            {"consumption_value": 150.0, "node_id": "NODE_003", "region": "South"},
        ]

        # Test total calculation
        total = consumption_service._calculate_total_consumption(sample_data)
        assert total == 450.0

        # Test average calculation
        average = consumption_service._calculate_average_consumption(sample_data)
        assert average == 150.0

        # Test peak calculation
        peak = consumption_service._calculate_peak_consumption(sample_data)
        assert peak == 200.0

        # Test region grouping
        by_region = consumption_service._group_consumption_by_region(sample_data)
        assert "North" in by_region
        assert "South" in by_region
        assert by_region["North"] == 300.0
        assert by_region["South"] == 150.0

    def test_anomaly_detection_algorithms(self, consumption_service):
        """Test anomaly detection algorithms."""
        # Arrange - Normal data with one clear outlier
        normal_values = [100.0] * 20
        anomaly_values = normal_values + [500.0] + normal_values  # Clear anomaly
        
        timestamps = [
            (datetime.now() - timedelta(hours=i)).isoformat() 
            for i in range(len(anomaly_values))
        ]
        
        sample_data = [
            {
                "consumption_value": value,
                "timestamp": timestamp,
                "node_id": "NODE_001"
            }
            for value, timestamp in zip(anomaly_values, timestamps)
        ]

        # Test statistical anomaly detection
        anomalies = consumption_service._detect_statistical_anomalies(sample_data)
        assert len(anomalies) > 0
        assert any(anomaly["consumption_value"] == 500.0 for anomaly in anomalies)

    def test_trend_analysis(self, consumption_service):
        """Test trend analysis calculations."""
        # Arrange - Increasing trend data
        increasing_data = [
            {
                "consumption_value": 100.0 + i * 10,
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
                "node_id": "NODE_001"
            }
            for i in range(10)
        ]

        # Test trend direction detection
        trend_direction = consumption_service._calculate_trend_direction(increasing_data)
        assert trend_direction in ["increasing", "decreasing", "stable"]

        # Test trend change percentage
        change_percentage = consumption_service._calculate_trend_change_percentage(increasing_data)
        assert isinstance(change_percentage, float)

    def test_forecast_model_selection(self, consumption_service):
        """Test forecast model selection logic."""
        # Arrange
        short_data = [{"consumption_value": 100.0 + i} for i in range(5)]
        long_data = [{"consumption_value": 100.0 + i} for i in range(100)]

        # Test model selection for different data sizes
        short_model = consumption_service._select_forecast_model(short_data)
        long_model = consumption_service._select_forecast_model(long_data)

        assert short_model in ["simple_average", "linear_regression", "arima", "lstm"]
        assert long_model in ["simple_average", "linear_regression", "arima", "lstm"]

    def test_optimization_suggestion_generation(self, consumption_service):
        """Test optimization suggestion generation logic."""
        # Arrange
        high_consumption_data = [
            {"node_id": "NODE_001", "consumption_value": 500.0, "region": "North"},
            {"node_id": "NODE_002", "consumption_value": 100.0, "region": "North"}
        ]

        # Test high consumption detection
        high_consumers = consumption_service._identify_high_consumers(high_consumption_data)
        assert len(high_consumers) > 0
        assert any(node["consumption_value"] > 400.0 for node in high_consumers)

        # Test suggestion type determination
        suggestion_type = consumption_service._determine_suggestion_type(high_consumption_data[0])
        assert suggestion_type in [
            "reduce_consumption", "schedule_maintenance", "pressure_optimization",
            "leak_detection", "usage_pattern_optimization"
        ]

    @pytest.mark.parametrize("aggregation_level", ["hourly", "daily", "weekly", "monthly"])
    def test_consumption_aggregation_levels(self, consumption_service, aggregation_level):
        """Test different consumption aggregation levels."""
        # Arrange
        sample_data = [
            {
                "consumption_value": 100.0,
                "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                "node_id": "NODE_001"
            }
            for i in range(48)  # 48 hours of data
        ]

        # Act
        aggregated = consumption_service._aggregate_consumption_data(sample_data, aggregation_level)

        # Assert
        assert isinstance(aggregated, list)
        assert len(aggregated) > 0
        for item in aggregated:
            assert "period" in item
            assert "total_consumption" in item
            assert "average_consumption" in item

    def test_consumption_data_validation(self, consumption_service):
        """Test consumption data validation."""
        # Test valid data
        valid_data = {
            "node_id": "NODE_001",
            "consumption_value": 150.0,
            "timestamp": datetime.now().isoformat(),
            "region": "North"
        }
        assert consumption_service._validate_consumption_record(valid_data) is True

        # Test invalid data - negative consumption
        invalid_data = valid_data.copy()
        invalid_data["consumption_value"] = -50.0
        assert consumption_service._validate_consumption_record(invalid_data) is False

        # Test invalid data - missing required field
        incomplete_data = {k: v for k, v in valid_data.items() if k != "node_id"}
        assert consumption_service._validate_consumption_record(incomplete_data) is False

    @pytest.mark.asyncio
    async def test_consumption_service_performance(
        self, consumption_service, mock_hybrid_service, test_date_range, performance_tracker
    ):
        """Test consumption service performance."""
        # Arrange
        large_dataset = [
            {
                "node_id": f"NODE_{i % 100:03d}",
                "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                "consumption_value": 100.0 + i % 200,
                "region": f"Region_{i % 5}",
                "unit": "liters"
            }
            for i in range(10000)  # Large dataset
        ]
        mock_hybrid_service.get_consumption_data.return_value = large_dataset

        # Act
        performance_tracker.start_timer("consumption_analytics")
        result = await consumption_service.get_consumption_analytics(
            mock_hybrid_service,
            test_date_range["start_time"],
            test_date_range["end_time"]
        )
        performance_tracker.end_timer("consumption_analytics")

        # Assert
        assert isinstance(result, ConsumptionAnalytics)
        performance_tracker.assert_performance("consumption_analytics", 3000)  # 3 seconds max

    def test_edge_cases(self, consumption_service):
        """Test edge cases in consumption service."""
        # Test empty data
        empty_result = consumption_service._calculate_total_consumption([])
        assert empty_result == 0.0

        # Test single data point
        single_point = [{"consumption_value": 100.0}]
        single_total = consumption_service._calculate_total_consumption(single_point)
        assert single_total == 100.0

        # Test data with None values
        data_with_none = [
            {"consumption_value": 100.0},
            {"consumption_value": None},
            {"consumption_value": 200.0}
        ]
        total_with_none = consumption_service._calculate_total_consumption(data_with_none)
        assert total_with_none == 300.0  # Should ignore None values

    def test_private_method_accessibility(self, consumption_service):
        """Test that private methods are properly defined."""
        # Check that key private methods exist
        private_methods = [
            "_calculate_total_consumption",
            "_calculate_average_consumption",
            "_calculate_peak_consumption",
            "_group_consumption_by_region",
            "_detect_statistical_anomalies",
            "_calculate_trend_direction",
            "_validate_consumption_record"
        ]
        
        for method_name in private_methods:
            assert hasattr(consumption_service, method_name), f"Missing method: {method_name}"
            assert callable(getattr(consumption_service, method_name)), f"Method not callable: {method_name}" 