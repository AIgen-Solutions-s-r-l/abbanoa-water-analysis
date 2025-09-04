"""
Unit tests for weather API endpoint location transformations.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))


class TestWeatherEndpointTransformations(unittest.TestCase):
    """Test weather API endpoints with location transformations."""
    
    @patch('src.presentation.api.app_postgres.pool')
    async def test_get_current_weather_transforms_locations(self, mock_pool):
        """Test that current weather endpoint transforms location names."""
        # Arrange
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # Mock database results with various locations
        mock_conn.fetch.return_value = [
            {
                'location': 'Cagliari',
                'date': MagicMock(isoformat=lambda: '2024-01-01'),
                'avg_temperature_c': 25.5,
                'min_temperature_c': 20.0,
                'max_temperature_c': 30.0,
                'humidity_percent': 65,
                'rainfall_mm': 0.0,
                'avg_wind_speed_kmh': 15.0,
                'weather_phenomena': 'Sunny'
            },
            {
                'location': 'Maccarese',
                'date': MagicMock(isoformat=lambda: '2024-01-01'),
                'avg_temperature_c': 24.0,
                'min_temperature_c': 19.0,
                'max_temperature_c': 29.0,
                'humidity_percent': 70,
                'rainfall_mm': 0.5,
                'avg_wind_speed_kmh': 12.0,
                'weather_phenomena': 'Partly Cloudy'
            },
            {
                'location': 'Selargius',
                'date': MagicMock(isoformat=lambda: '2024-01-01'),
                'avg_temperature_c': 26.0,
                'min_temperature_c': 21.0,
                'max_temperature_c': 31.0,
                'humidity_percent': 60,
                'rainfall_mm': 0.0,
                'avg_wind_speed_kmh': 18.0,
                'weather_phenomena': 'Clear'
            }
        ]
        
        # Import the function to test
        from src.presentation.api.app_postgres import get_current_weather_with_transformation
        
        # Act
        result = await get_current_weather_with_transformation(location=None)
        
        # Assert
        # Should only contain Abbanoa (transformed from Cagliari)
        # Maccarese and Selargius should be filtered out
        assert len(result) == 1
        assert result[0]['location'] == 'Abbanoa'
        assert result[0]['temperature']['current'] == 25.5
    
    @patch('src.presentation.api.app_postgres.pool')
    async def test_get_weather_locations_filters_hidden(self, mock_pool):
        """Test that weather locations endpoint filters hidden locations."""
        # Arrange
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # Mock database results
        mock_conn.fetch.return_value = [
            {
                'location': 'Cagliari',
                'data_points': 1000,
                'first_date': MagicMock(isoformat=lambda: '2023-01-01'),
                'last_date': MagicMock(isoformat=lambda: '2024-01-01')
            },
            {
                'location': 'Maccarese',
                'data_points': 800,
                'first_date': MagicMock(isoformat=lambda: '2023-01-01'),
                'last_date': MagicMock(isoformat=lambda: '2024-01-01')
            },
            {
                'location': 'Selargius',
                'data_points': 900,
                'first_date': MagicMock(isoformat=lambda: '2023-01-01'),
                'last_date': MagicMock(isoformat=lambda: '2024-01-01')
            }
        ]
        
        # Import the function to test
        from src.presentation.api.app_postgres import get_weather_locations_with_transformation
        
        # Act
        result = await get_weather_locations_with_transformation()
        
        # Assert
        # Should only contain Abbanoa
        assert len(result) == 1
        assert result[0]['location'] == 'Abbanoa'
        assert result[0]['dataPoints'] == 1000
    
    @patch('src.presentation.api.app_postgres.pool')
    async def test_query_location_transformed_to_actual(self, mock_pool):
        """Test that queries for Abbanoa are transformed to Cagliari."""
        # Arrange
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        # Import the function to test
        from src.presentation.api.app_postgres import get_current_weather_with_transformation
        
        # Act
        await get_current_weather_with_transformation(location='Abbanoa')
        
        # Assert
        # Check that the query was called with 'Cagliari' not 'Abbanoa'
        mock_conn.fetch.assert_called_once()
        args = mock_conn.fetch.call_args[0]
        assert 'Cagliari' in args[1]  # Second argument should be the transformed location


if __name__ == '__main__':
    unittest.main()
