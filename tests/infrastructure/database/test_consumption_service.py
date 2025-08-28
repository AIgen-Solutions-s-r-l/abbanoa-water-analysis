"""
Tests for ConsumptionService using real database data.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database.consumption_service import ConsumptionService, ConsumptionServiceError
from src.infrastructure.database.models import Node, SensorReading


class TestConsumptionService:
    """Test suite for ConsumptionService with real data."""
    
    @pytest.fixture
    def database_url(self):
        """Get test database URL."""
        return "postgresql://abbanoa_user:abbanoa_secure_pass@localhost:5432/abbanoa_processing"
    
    @pytest.fixture
    def consumption_service(self, database_url):
        """Create ConsumptionService instance."""
        return ConsumptionService(database_url)
    
    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        return Mock()
    
    def test_get_consumption_analytics_returns_real_data_metadata(self, consumption_service):
        """Test that get_consumption_analytics returns real data metadata."""
        # Arrange & Act
        result = consumption_service.get_consumption_analytics()
        
        # Assert
        assert 'data_metadata' in result
        metadata = result['data_metadata']
        
        # Verify real data indicators
        assert metadata['is_real_time'] is False
        assert metadata['data_source'] == 'Historical Database'
        assert metadata['total_readings'] > 0
        assert metadata['active_nodes'] > 0
        
        # Verify date range is realistic (should be from Nov 2024 to June 2025)
        earliest = datetime.fromisoformat(metadata['earliest_timestamp'].replace('Z', '+00:00'))
        latest = datetime.fromisoformat(metadata['latest_timestamp'].replace('Z', '+00:00'))
        
        assert earliest.year == 2024
        assert latest.year == 2025
        assert earliest < latest
    
    def test_get_consumption_analytics_returns_real_node_data(self, consumption_service):
        """Test that get_consumption_analytics returns real node data."""
        # Arrange & Act
        result = consumption_service.get_consumption_analytics()
        
        # Assert
        assert 'district_consumption' in result
        district_data = result['district_consumption']
        
        # Should have data for real nodes
        assert len(district_data) > 0
        
        # Verify node names match real infrastructure
        node_names = [node['district_name'] for node in district_data]
        expected_nodes = [
            'Via Dante Principale',
            'Via Roma Secondario', 
            'Piazza Italia Distribuzione',
            'Nodo Via Sant Anna',
            'Nodo Via Seneca',
            'Serbatoio Selargius',
            'Serbatoio Cuccuru Linu'
        ]
        
        # At least some nodes should match
        matching_nodes = [name for name in node_names if any(expected in name for expected in expected_nodes)]
        assert len(matching_nodes) > 0
    
    def test_get_consumption_analytics_returns_real_consumption_timeline(self, consumption_service):
        """Test that get_consumption_analytics returns real consumption timeline."""
        # Arrange & Act
        result = consumption_service.get_consumption_analytics()
        
        # Assert
        assert 'consumption_timeline' in result
        timeline = result['consumption_timeline']
        
        # Should have 24 hours of data
        assert len(timeline) == 24
        
        # Each hour should have realistic consumption values
        for hour_data in timeline:
            assert 'timestamp' in hour_data
            assert 'consumption_liters' in hour_data
            assert 'forecast_consumption' in hour_data
            
            # Consumption should be realistic (not zero or negative)
            assert hour_data['consumption_liters'] >= 0
            assert hour_data['forecast_consumption'] >= 0
    
    def test_get_consumption_analytics_returns_real_summary_metrics(self, consumption_service):
        """Test that get_consumption_analytics returns real summary metrics."""
        # Arrange & Act
        result = consumption_service.get_consumption_analytics()
        
        # Assert
        assert 'summary' in result
        summary = result['summary']
        
        # Should have realistic consumption values
        assert summary['total_daily_consumption'] > 0
        assert summary['total_monthly_consumption'] > 0
        assert summary['total_users'] > 0
        assert summary['avg_consumption_per_user'] > 0
        
        # System efficiency should be realistic
        assert 0.5 <= summary['system_efficiency'] <= 1.0
        assert 0 <= summary['water_loss_percentage'] <= 50
    
    def test_get_consumption_analytics_handles_database_errors_gracefully(self, consumption_service):
        """Test that get_consumption_analytics handles database errors gracefully."""
        # Arrange - Mock session to raise exception
        with patch.object(consumption_service, 'get_session') as mock_get_session:
            mock_session = Mock()
            mock_session.query.side_effect = Exception("Database connection failed")
            mock_get_session.return_value = mock_session
            
            # Act & Assert
            with pytest.raises(ConsumptionServiceError) as exc_info:
                consumption_service.get_consumption_analytics()
            
            assert "Database error" in str(exc_info.value)
    
    def test_get_consumption_analytics_returns_real_user_segments(self, consumption_service):
        """Test that get_consumption_analytics returns realistic user segments."""
        # Arrange & Act
        result = consumption_service.get_consumption_analytics()
        
        # Assert
        assert 'user_segments' in result
        segments = result['user_segments']
        
        # Should have residential, commercial, and industrial segments
        segment_types = [seg['segment'] for seg in segments]
        assert 'Residential' in segment_types
        assert 'Commercial' in segment_types
        assert 'Industrial' in segment_types
        
        # Each segment should have realistic data
        for segment in segments:
            assert segment['user_count'] > 0
            assert 0 <= segment['percentage'] <= 100
            assert segment['avg_daily_consumption'] > 0
            assert segment['trend'] in ['stable', 'increasing', 'decreasing']
    
    def test_get_consumption_analytics_returns_real_peak_demand_data(self, consumption_service):
        """Test that get_consumption_analytics returns realistic peak demand data."""
        # Arrange & Act
        result = consumption_service.get_consumption_analytics()
        
        # Assert
        assert 'peak_demand' in result
        peak_data = result['peak_demand']
        
        # Should have peak time in HH:MM format
        assert ':' in peak_data['daily_peak_time']
        assert peak_data['daily_peak_consumption'] > 0
        
        # Should have realistic peak information
        assert peak_data['weekly_peak_day'] in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        assert peak_data['seasonal_peak_month'] in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
