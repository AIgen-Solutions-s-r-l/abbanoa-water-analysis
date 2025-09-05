"""
Integration tests for weather API endpoints.
"""

import unittest
import requests
import json
from datetime import datetime, timedelta


class TestWeatherAPIIntegration(unittest.TestCase):
    """Integration tests for weather API endpoints."""
    
    BASE_URL = "http://localhost:8000/api/v1"
    
    def test_weather_locations_returns_abbanoa(self):
        """Test that /weather/locations returns only Abbanoa."""
        # Arrange
        url = f"{self.BASE_URL}/weather/locations"
        
        # Act
        response = requests.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        locations = response.json()
        self.assertIsInstance(locations, list)
        self.assertEqual(len(locations), 1)
        self.assertEqual(locations[0]['location'], 'Abbanoa')
        self.assertGreater(locations[0]['dataPoints'], 0)
        self.assertIn('dateRange', locations[0])
        self.assertIn('start', locations[0]['dateRange'])
        self.assertIn('end', locations[0]['dateRange'])
    
    def test_weather_current_returns_abbanoa_data(self):
        """Test that /weather/current returns Abbanoa weather data."""
        # Arrange
        url = f"{self.BASE_URL}/weather/current"
        
        # Act
        response = requests.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        current_weather = response.json()
        self.assertIsInstance(current_weather, list)
        self.assertGreater(len(current_weather), 0)
        
        # Check first weather record
        weather = current_weather[0]
        self.assertEqual(weather['location'], 'Abbanoa')
        self.assertIn('date', weather)
        self.assertIn('temperature', weather)
        self.assertIn('current', weather['temperature'])
        self.assertIn('humidity', weather)
        self.assertIn('rainfall', weather)
        self.assertIn('windSpeed', weather)
        self.assertIn('conditions', weather)
    
    def test_weather_historical_daily_returns_data(self):
        """Test that /weather/historical returns daily data for Abbanoa."""
        # Arrange
        # Use dates that exist in the database
        start_date = datetime(2023, 6, 1).date()
        end_date = datetime(2023, 6, 7).date()
        url = f"{self.BASE_URL}/weather/historical"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'interval': 'daily'
        }
        
        # Act
        response = requests.get(url, params=params)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        historical_data = response.json()
        self.assertIsInstance(historical_data, list)
        self.assertGreater(len(historical_data), 0)
        
        # Check data structure
        for record in historical_data:
            self.assertEqual(record['location'], 'Abbanoa')
            self.assertIn('date', record)
            self.assertIn('temperature', record)
            self.assertIn('temperatureMin', record)
            self.assertIn('temperatureMax', record)
            self.assertIn('humidity', record)
            self.assertIn('rainfall', record)
            self.assertIn('windSpeed', record)
    
    def test_weather_historical_with_location_filter(self):
        """Test that /weather/historical with location=Abbanoa returns data."""
        # Arrange
        # Use dates that exist in the database
        start_date = datetime(2023, 6, 1).date()
        end_date = datetime(2023, 6, 30).date()
        url = f"{self.BASE_URL}/weather/historical"
        params = {
            'location': 'Abbanoa',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'interval': 'daily'
        }
        
        # Act
        response = requests.get(url, params=params)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        historical_data = response.json()
        self.assertIsInstance(historical_data, list)
        self.assertGreater(len(historical_data), 0)
        
        # Verify all records are for Abbanoa
        for record in historical_data:
            self.assertEqual(record['location'], 'Abbanoa')
    
    def test_weather_statistics_returns_data(self):
        """Test that /weather/statistics returns data for Abbanoa."""
        # Arrange
        url = f"{self.BASE_URL}/weather/statistics"
        params = {'location': 'Abbanoa'}
        
        # Act
        response = requests.get(url, params=params)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        stats = response.json()
        self.assertIsInstance(stats, dict)
        
        # Check statistics structure based on actual response
        self.assertIn('overview', stats)
        overview = stats['overview']
        self.assertIn('totalDays', overview)
        self.assertIn('averageTemperature', overview)
        self.assertIn('temperatureRange', overview)
        self.assertIn('min', overview['temperatureRange'])
        self.assertIn('max', overview['temperatureRange'])
        self.assertIn('totalRainfall', overview)
        self.assertIn('averageDailyRainfall', overview)
        self.assertIn('rainyDays', overview)
    
    def test_no_data_for_hidden_locations(self):
        """Test that hidden locations (Maccarese, Cagliari) return no data."""
        # Arrange
        url = f"{self.BASE_URL}/weather/current"
        hidden_locations = ['Maccarese', 'Cagliari']
        
        # Act & Assert
        for location in hidden_locations:
            params = {'location': location}
            response = requests.get(url, params=params)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            # Should return empty list for hidden locations
            self.assertEqual(len(data), 0)


if __name__ == '__main__':
    unittest.main()
