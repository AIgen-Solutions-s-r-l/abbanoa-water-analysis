"""
Weather API Configuration for Abbanoa Water Infrastructure

To use real weather data:
1. Sign up for a free OpenWeatherMap account at https://openweathermap.org/api
2. Get your API key from the account dashboard
3. Set the OPENWEATHERMAP_API_KEY environment variable:
   export OPENWEATHERMAP_API_KEY="your_api_key_here"
   
Or directly set it in this file (not recommended for production)
"""

import os
from typing import Optional

# Weather API Provider (currently only 'openweathermap' is supported)
WEATHER_PROVIDER = 'openweathermap'

# API Key - preferably set as environment variable
WEATHER_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY', None)

# Location coordinates for Cagliari, Sardinia
LOCATION_LAT = 39.2238
LOCATION_LON = 9.1217
LOCATION_NAME = "Cagliari"

# Weather impact configurations
WEATHER_IMPACTS = {
    # Temperature thresholds and impacts on water consumption
    'temperature': {
        'hot_threshold': 30,  # °C
        'warm_threshold': 25,  # °C
        'cold_threshold': 10,  # °C
        'hot_flow_multiplier': 1.3,  # 30% increase in hot weather
        'warm_flow_multiplier': 1.15,  # 15% increase in warm weather
        'cold_flow_multiplier': 0.9,  # 10% decrease in cold weather
    },
    
    # Rain impacts
    'rain': {
        'flow_reduction': 0.8,  # 20% reduction during rain (less irrigation)
        'pressure_increase': 1.05,  # 5% pressure increase
        'quality_impact_per_mm': 0.02,  # Quality reduction per mm of rain
    },
    
    # Humidity impacts
    'humidity': {
        'dry_threshold': 40,  # %
        'dry_flow_multiplier': 1.1,  # 10% increase in dry conditions
    },
    
    # Wind impacts
    'wind': {
        'strong_threshold': 10,  # m/s
        'pressure_reduction': 0.98,  # 2% pressure reduction in strong wind
    }
}

# Cache settings
WEATHER_CACHE_DIR = '/home/alessio/Customers/Abbanoa/data'
WEATHER_CACHE_HOURS = 1  # Cache weather data for 1 hour

# Fallback weather data if API is unavailable
FALLBACK_WEATHER = {
    'temperature': 22.0,
    'humidity': 65.0,
    'pressure': 1013.0,
    'wind_speed': 3.0,
    'rain_volume': 0.0,
    'cloud_coverage': 30.0,
    'condition': 'Clear'
}

def get_api_key() -> Optional[str]:
    """Get weather API key from environment or config"""
    return WEATHER_API_KEY

def is_weather_enabled() -> bool:
    """Check if weather integration is enabled"""
    return WEATHER_API_KEY is not None
