"""
Unit tests for weather location mapping configuration.
"""

import unittest
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.config.weather_location_mapping import (
    get_display_name,
    get_actual_location,
    transform_weather_data,
    HIDDEN_LOCATIONS
)


class TestWeatherLocationMapping(unittest.TestCase):
    """Test weather location name transformations."""
    
    def test_get_display_name_for_cagliari(self):
        """Test that Cagliari is displayed as Roccavina."""
        # Arrange
        actual_location = "Cagliari"
        
        # Act
        display_name = get_display_name(actual_location)
        
        # Assert
        assert display_name == "Roccavina"
    
    def test_get_display_name_for_hidden_locations(self):
        """Test that hidden locations return None."""
        # Arrange
        hidden_locations = ["Maccarese", "Selargius"]
        
        # Act & Assert
        for location in hidden_locations:
            assert get_display_name(location) is None
    
    def test_get_display_name_for_unknown_location(self):
        """Test that unknown locations return their original name."""
        # Arrange
        unknown_location = "UnknownCity"
        
        # Act
        display_name = get_display_name(unknown_location)
        
        # Assert
        assert display_name == "UnknownCity"
    
    def test_get_actual_location_from_display_name(self):
        """Test reverse mapping from display name to actual location."""
        # Arrange
        display_name = "Roccavina"
        
        # Act
        actual_location = get_actual_location(display_name)
        
        # Assert
        assert actual_location == "Cagliari"
    
    def test_get_actual_location_for_unknown_display_name(self):
        """Test that unknown display names return original value."""
        # Arrange
        unknown_display = "UnknownDisplay"
        
        # Act
        actual_location = get_actual_location(unknown_display)
        
        # Assert
        assert actual_location == "UnknownDisplay"
    
    def test_transform_weather_data_for_cagliari(self):
        """Test transforming weather data for Cagliari."""
        # Arrange
        weather_data = {
            "location": "Cagliari",
            "temperature": 25.5,
            "humidity": 65,
            "conditions": "Sunny"
        }
        
        # Act
        transformed = transform_weather_data(weather_data)
        
        # Assert
        assert transformed is not None
        assert transformed["location"] == "Roccavina"
        assert transformed["temperature"] == 25.5
        assert transformed["humidity"] == 65
        assert transformed["conditions"] == "Sunny"
    
    def test_transform_weather_data_for_hidden_location(self):
        """Test that weather data for hidden locations returns None."""
        # Arrange
        weather_data_maccarese = {
            "location": "Maccarese",
            "temperature": 24.0,
            "humidity": 70
        }
        weather_data_selargius = {
            "location": "Selargius",
            "temperature": 26.0,
            "humidity": 60
        }
        
        # Act & Assert
        assert transform_weather_data(weather_data_maccarese) is None
        assert transform_weather_data(weather_data_selargius) is None
    
    def test_transform_weather_data_with_none_input(self):
        """Test that None input returns None."""
        # Arrange & Act
        result = transform_weather_data(None)
        
        # Assert
        assert result is None
    
    def test_transform_weather_data_preserves_original(self):
        """Test that transformation doesn't modify the original data."""
        # Arrange
        original_data = {
            "location": "Cagliari",
            "temperature": 25.5,
            "humidity": 65
        }
        
        # Act
        transformed = transform_weather_data(original_data)
        
        # Assert
        assert original_data["location"] == "Cagliari"  # Original unchanged
        assert transformed["location"] == "Roccavina"  # Transformed changed
    
    def test_hidden_locations_set(self):
        """Test that HIDDEN_LOCATIONS contains expected locations."""
        # Assert
        assert "Maccarese" in HIDDEN_LOCATIONS
        assert "Selargius" in HIDDEN_LOCATIONS
        assert "Cagliari" not in HIDDEN_LOCATIONS


if __name__ == '__main__':
    unittest.main()
