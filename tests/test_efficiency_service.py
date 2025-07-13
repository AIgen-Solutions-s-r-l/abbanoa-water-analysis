"""
Unit and integration tests for the Network Efficiency Service.

This module contains comprehensive test cases for the EfficiencyService class
and the associated API endpoints, covering various scenarios and edge cases.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncpg
from fastapi.testclient import TestClient
from fastapi import HTTPException

from src.core.efficiency_service import EfficiencyService
from src.routes.efficiency import router, get_efficiency_service
from src.schemas.api.efficiency import EfficiencyResponse


class TestEfficiencyService:
    """Unit tests for the EfficiencyService class."""

    @pytest.fixture
    def mock_postgres_manager(self):
        """Create a mock PostgreSQL manager."""
        manager = Mock()
        manager.acquire = AsyncMock()
        return manager

    @pytest.fixture
    def mock_connection(self):
        """Create a mock database connection."""
        conn = Mock()
        conn.fetch = AsyncMock()
        conn.fetchrow = AsyncMock()
        return conn

    @pytest.fixture
    def efficiency_service(self, mock_postgres_manager):
        """Create an efficiency service instance with mocked dependencies."""
        service = EfficiencyService()
        service.postgres_manager = mock_postgres_manager
        return service

    @pytest.fixture
    def sample_node_data(self):
        """Sample node data for testing."""
        return [
            {
                'node_id': '215542',
                'reading_count': 24,
                'avg_flow_rate': 7.76,
                'avg_pressure': 6.77,
                'avg_temperature': 18.5,
                'total_volume': 669.6,
                'avg_quality_score': 0.98,
                'first_reading': datetime(2024, 1, 15, 0, 0),
                'last_reading': datetime(2024, 1, 15, 23, 0)
            },
            {
                'node_id': '288400',
                'reading_count': 24,
                'avg_flow_rate': 41.14,
                'avg_pressure': 0.16,
                'avg_temperature': 19.2,
                'total_volume': 3556.8,
                'avg_quality_score': 0.95,
                'first_reading': datetime(2024, 1, 15, 0, 0),
                'last_reading': datetime(2024, 1, 15, 23, 0)
            }
        ]

    @pytest.fixture
    def sample_metadata(self):
        """Sample node metadata for testing."""
        return {
            '215542': {
                'node_name': 'Main Sensor 215542',
                'node_type': 'meter',
                'location_name': 'District A',
                'is_active': True
            },
            '288400': {
                'node_name': 'Flow Meter 288400',
                'node_type': 'meter',
                'location_name': 'District B',
                'is_active': True
            }
        }

    @pytest.fixture
    def sample_system_metrics(self):
        """Sample system metrics for testing."""
        return {
            'total_system_volume': 4226.4,
            'avg_system_flow_rate': 24.45,
            'avg_system_pressure': 3.465,
            'avg_system_quality': 0.965,
            'active_nodes': 2,
            'total_readings': 48
        }

    # Test 1: Basic service initialization
    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test that the service initializes correctly."""
        service = EfficiencyService()
        assert service.postgres_manager is None
        
        # Mock the get_postgres_manager function
        with patch('src.core.efficiency_service.get_postgres_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager
            
            await service.initialize()
            
            assert service.postgres_manager == mock_manager
            mock_get_manager.assert_called_once()

    # Test 2: Time range parsing
    def test_parse_time_range_valid(self, efficiency_service):
        """Test parsing valid time ranges."""
        assert efficiency_service._parse_time_range("1h") == 1
        assert efficiency_service._parse_time_range("6h") == 6
        assert efficiency_service._parse_time_range("24h") == 24
        assert efficiency_service._parse_time_range("3d") == 72
        assert efficiency_service._parse_time_range("7d") == 168
        assert efficiency_service._parse_time_range("30d") == 720

    # Test 3: Invalid time range parsing
    def test_parse_time_range_invalid(self, efficiency_service):
        """Test parsing invalid time ranges."""
        with pytest.raises(ValueError, match="Invalid time range"):
            efficiency_service._parse_time_range("48h")
        
        with pytest.raises(ValueError, match="Invalid time range"):
            efficiency_service._parse_time_range("invalid")

    # Test 4: Calculate efficiency metrics with valid data
    def test_calculate_efficiency_metrics_valid_data(self, efficiency_service, sample_node_data):
        """Test calculating efficiency metrics with valid node data."""
        # Convert sample data to mock records
        mock_records = []
        for node in sample_node_data:
            mock_record = Mock()
            for key, value in node.items():
                setattr(mock_record, key, value)
            mock_records.append(mock_record)
        
        metrics = efficiency_service._calculate_efficiency_metrics(mock_records, 24)
        
        # Verify metrics structure
        assert 'network_efficiency_percentage' in metrics
        assert 'total_throughput_m3h' in metrics
        assert 'average_pressure_bar' in metrics
        assert 'quality_score' in metrics
        assert 'operational_efficiency' in metrics
        assert 'flow_consistency_score' in metrics
        
        # Verify calculated values
        assert metrics['total_throughput_m3h'] == round((669.6 + 3556.8) / 24, 2)
        assert metrics['average_pressure_bar'] == round((6.77 + 0.16) / 2, 2)
        assert metrics['quality_score'] == round((0.98 + 0.95) / 2, 3)
        assert metrics['operational_efficiency'] == 100.0  # Both nodes have flow rates > 0

    # Test 5: Calculate efficiency metrics with empty data
    def test_calculate_efficiency_metrics_empty_data(self, efficiency_service):
        """Test calculating efficiency metrics with empty node data."""
        metrics = efficiency_service._calculate_efficiency_metrics([], 24)
        
        # Verify all metrics are zero
        assert metrics['network_efficiency_percentage'] == 0
        assert metrics['total_throughput_m3h'] == 0
        assert metrics['average_pressure_bar'] == 0
        assert metrics['quality_score'] == 0
        assert metrics['operational_efficiency'] == 0

    # Test 6: Calculate uptime percentage
    def test_calculate_uptime_percentage(self, efficiency_service):
        """Test calculating uptime percentage for nodes."""
        # Mock node record
        mock_node = Mock()
        mock_node.configure_mock(**{'reading_count': 20})
        
        # Test with 24 expected readings
        uptime = efficiency_service._calculate_uptime_percentage(mock_node, 24)
        assert uptime == round((20 / 24) * 100, 2)
        
        # Test with perfect uptime
        mock_node.configure_mock(**{'reading_count': 24})
        uptime = efficiency_service._calculate_uptime_percentage(mock_node, 24)
        assert uptime == 100.0
        
        # Test with zero readings
        mock_node.configure_mock(**{'reading_count': 0})
        uptime = efficiency_service._calculate_uptime_percentage(mock_node, 24)
        assert uptime == 0.0

    # Test 7: Get efficiency summary with valid parameters
    @pytest.mark.asyncio
    async def test_get_efficiency_summary_valid_params(self, efficiency_service, mock_connection, sample_node_data, sample_metadata, sample_system_metrics):
        """Test getting efficiency summary with valid parameters."""
        # Setup mocks
        efficiency_service.postgres_manager.acquire.return_value.__aenter__.return_value = mock_connection
        
        # Mock database responses
        mock_connection.fetch.return_value = sample_node_data
        mock_connection.fetchrow.return_value = sample_system_metrics
        
        # Mock the helper methods
        efficiency_service._get_node_metadata = AsyncMock(return_value=sample_metadata)
        efficiency_service._calculate_system_metrics = AsyncMock(return_value=sample_system_metrics)
        
        # Call the method
        result = await efficiency_service.get_efficiency_summary(time_range="24h", node_ids=None)
        
        # Verify response structure
        assert 'summary' in result
        assert 'efficiency_metrics' in result
        assert 'system_metrics' in result
        assert 'node_performance' in result
        assert 'metadata' in result
        
        # Verify summary data
        assert result['summary']['time_range'] == "24h"
        assert result['summary']['total_nodes'] == 2
        assert result['summary']['active_nodes'] == 2
        assert result['summary']['analyzed_hours'] == 24
        
        # Verify node performance data
        assert len(result['node_performance']) == 2
        assert result['node_performance'][0]['node_id'] == '215542'
        assert result['node_performance'][0]['node_name'] == 'Main Sensor 215542'

    # Test 8: Get efficiency summary with node filtering
    @pytest.mark.asyncio
    async def test_get_efficiency_summary_with_node_filter(self, efficiency_service, mock_connection, sample_node_data, sample_metadata, sample_system_metrics):
        """Test getting efficiency summary with node ID filtering."""
        # Setup mocks
        efficiency_service.postgres_manager.acquire.return_value.__aenter__.return_value = mock_connection
        
        # Filter to only one node
        filtered_data = [sample_node_data[0]]
        mock_connection.fetch.return_value = filtered_data
        mock_connection.fetchrow.return_value = sample_system_metrics
        
        # Mock the helper methods
        efficiency_service._get_node_metadata = AsyncMock(return_value=sample_metadata)
        efficiency_service._calculate_system_metrics = AsyncMock(return_value=sample_system_metrics)
        
        # Call the method with node filtering
        result = await efficiency_service.get_efficiency_summary(time_range="24h", node_ids=["215542"])
        
        # Verify filtering worked
        assert result['summary']['total_nodes'] == 1
        assert len(result['node_performance']) == 1
        assert result['node_performance'][0]['node_id'] == '215542'

    # Test 9: Get efficiency summary with different time ranges
    @pytest.mark.asyncio
    async def test_get_efficiency_summary_different_time_ranges(self, efficiency_service, mock_connection, sample_node_data, sample_metadata, sample_system_metrics):
        """Test getting efficiency summary with different time ranges."""
        # Setup mocks
        efficiency_service.postgres_manager.acquire.return_value.__aenter__.return_value = mock_connection
        mock_connection.fetch.return_value = sample_node_data
        mock_connection.fetchrow.return_value = sample_system_metrics
        
        # Mock the helper methods
        efficiency_service._get_node_metadata = AsyncMock(return_value=sample_metadata)
        efficiency_service._calculate_system_metrics = AsyncMock(return_value=sample_system_metrics)
        
        # Test different time ranges
        time_ranges = ["1h", "6h", "24h", "3d", "7d", "30d"]
        expected_hours = [1, 6, 24, 72, 168, 720]
        
        for time_range, expected_hour in zip(time_ranges, expected_hours):
            result = await efficiency_service.get_efficiency_summary(time_range=time_range, node_ids=None)
            assert result['summary']['time_range'] == time_range
            assert result['summary']['analyzed_hours'] == expected_hour

    # Test 10: Get efficiency summary with database error
    @pytest.mark.asyncio
    async def test_get_efficiency_summary_database_error(self, efficiency_service, mock_connection):
        """Test handling database errors in get_efficiency_summary."""
        # Setup mocks to raise an exception
        efficiency_service.postgres_manager.acquire.return_value.__aenter__.return_value = mock_connection
        mock_connection.fetch.side_effect = Exception("Database connection failed")
        
        # Verify that the exception is re-raised
        with pytest.raises(Exception, match="Database connection failed"):
            await efficiency_service.get_efficiency_summary(time_range="24h", node_ids=None)

    # Test 11: Get node metadata with filtering
    @pytest.mark.asyncio
    async def test_get_node_metadata_with_filter(self, efficiency_service, mock_connection):
        """Test getting node metadata with node ID filtering."""
        # Setup mock response
        mock_connection.fetch.return_value = [
            {
                'node_id': '215542',
                'node_name': 'Main Sensor 215542',
                'node_type': 'meter',
                'location_name': 'District A',
                'is_active': True
            }
        ]
        
        result = await efficiency_service._get_node_metadata(mock_connection, ["215542"])
        
        assert '215542' in result
        assert result['215542']['node_name'] == 'Main Sensor 215542'
        assert result['215542']['node_type'] == 'meter'
        assert result['215542']['location_name'] == 'District A'
        assert result['215542']['is_active'] is True

    # Test 12: Calculate system metrics
    @pytest.mark.asyncio
    async def test_calculate_system_metrics(self, efficiency_service, mock_connection):
        """Test calculating system-wide metrics."""
        # Setup mock response
        mock_connection.fetchrow.return_value = {
            'total_system_volume': 4226.4,
            'avg_system_flow_rate': 24.45,
            'avg_system_pressure': 3.465,
            'avg_system_quality': 0.965,
            'active_nodes': 2,
            'total_readings': 48
        }
        
        start_time = datetime(2024, 1, 15, 0, 0)
        end_time = datetime(2024, 1, 16, 0, 0)
        
        result = await efficiency_service._calculate_system_metrics(mock_connection, start_time, end_time, None)
        
        assert result['total_system_volume_m3'] == 4226.4
        assert result['avg_system_flow_rate'] == 24.45
        assert result['avg_system_pressure'] == 3.465
        assert result['avg_system_quality'] == 0.965
        assert result['active_nodes'] == 2
        assert result['total_readings'] == 48


class TestEfficiencyAPI:
    """Integration tests for the Efficiency API endpoints."""

    @pytest.fixture
    def mock_efficiency_service(self):
        """Create a mock efficiency service."""
        service = Mock()
        service.get_efficiency_summary = AsyncMock()
        service.initialize = AsyncMock()
        return service

    @pytest.fixture
    def sample_api_response(self):
        """Sample API response for testing."""
        return {
            "summary": {
                "time_range": "24h",
                "period_start": "2024-01-15T00:00:00",
                "period_end": "2024-01-16T00:00:00",
                "total_nodes": 2,
                "active_nodes": 2,
                "analyzed_hours": 24
            },
            "efficiency_metrics": {
                "network_efficiency_percentage": 87.5,
                "total_throughput_m3h": 176.1,
                "average_pressure_bar": 3.465,
                "quality_score": 0.965,
                "operational_efficiency": 100.0,
                "flow_consistency_score": 0.85
            },
            "system_metrics": {
                "total_system_volume_m3": 4226.4,
                "avg_system_flow_rate": 24.45,
                "avg_system_pressure": 3.465,
                "avg_system_quality": 0.965,
                "active_nodes": 2,
                "total_readings": 48
            },
            "node_performance": [
                {
                    "node_id": "215542",
                    "node_name": "Main Sensor 215542",
                    "node_type": "meter",
                    "reading_count": 24,
                    "avg_flow_rate": 7.76,
                    "avg_pressure": 6.77,
                    "avg_temperature": 18.5,
                    "total_volume_m3": 669.6,
                    "avg_quality_score": 0.98,
                    "uptime_percentage": 100.0,
                    "first_reading": "2024-01-15T00:00:00",
                    "last_reading": "2024-01-15T23:00:00"
                }
            ],
            "metadata": {
                "generated_at": "2024-01-16T10:30:00",
                "data_source": "sensor_readings_hourly",
                "version": "1.0"
            }
        }

    # Test 13: API endpoint with valid parameters
    @pytest.mark.asyncio
    async def test_api_endpoint_valid_params(self, mock_efficiency_service, sample_api_response):
        """Test the API endpoint with valid parameters."""
        # Setup mock
        mock_efficiency_service.get_efficiency_summary.return_value = sample_api_response
        
        # Import and test the endpoint function
        from src.routes.efficiency import get_efficiency_summary
        
        result = await get_efficiency_summary(
            time_range="24h",
            node_ids=None,
            service=mock_efficiency_service
        )
        
        # Verify the service was called correctly
        mock_efficiency_service.get_efficiency_summary.assert_called_once_with(
            time_range="24h",
            node_ids=None
        )
        
        # Verify the response structure
        assert result.summary.time_range == "24h"
        assert result.summary.total_nodes == 2
        assert result.efficiency_metrics.network_efficiency_percentage == 87.5
        assert len(result.node_performance) == 1

    # Test 14: API endpoint with invalid time range
    @pytest.mark.asyncio
    async def test_api_endpoint_invalid_time_range(self, mock_efficiency_service):
        """Test the API endpoint with invalid time range."""
        from src.routes.efficiency import get_efficiency_summary
        
        # Test with invalid time range
        with pytest.raises(HTTPException) as exc_info:
            await get_efficiency_summary(
                time_range="48h",
                node_ids=None,
                service=mock_efficiency_service
            )
        
        assert exc_info.value.status_code == 400
        assert "invalid_time_range" in str(exc_info.value.detail)

    # Test 15: API endpoint with invalid node IDs
    @pytest.mark.asyncio
    async def test_api_endpoint_invalid_node_ids(self, mock_efficiency_service):
        """Test the API endpoint with invalid node IDs."""
        from src.routes.efficiency import get_efficiency_summary
        
        # Test with empty node IDs list
        with pytest.raises(HTTPException) as exc_info:
            await get_efficiency_summary(
                time_range="24h",
                node_ids=[],
                service=mock_efficiency_service
            )
        
        assert exc_info.value.status_code == 400
        assert "invalid_node_ids" in str(exc_info.value.detail)

    # Test 16: API endpoint with service error
    @pytest.mark.asyncio
    async def test_api_endpoint_service_error(self, mock_efficiency_service):
        """Test the API endpoint with service error."""
        from src.routes.efficiency import get_efficiency_summary
        
        # Setup service to raise an exception
        mock_efficiency_service.get_efficiency_summary.side_effect = Exception("Service error")
        
        # Test that exception is handled
        with pytest.raises(HTTPException) as exc_info:
            await get_efficiency_summary(
                time_range="24h",
                node_ids=None,
                service=mock_efficiency_service
            )
        
        assert exc_info.value.status_code == 500
        assert "internal_error" in str(exc_info.value.detail)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 