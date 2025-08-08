#!/usr/bin/env python3
"""
Weather API Integration for Abbanoa Water Infrastructure
Fetches weather data to make synthetic data generation more realistic
"""

import aiohttp
import asyncio
from datetime import datetime, timezone
from typing import Dict, Optional, List
import json
import os
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    """Weather data structure"""
    timestamp: datetime
    temperature: float  # Celsius
    humidity: float  # Percentage
    pressure: float  # hPa
    wind_speed: float  # m/s
    rain_volume: float  # mm in last hour
    cloud_coverage: float  # Percentage
    condition: str  # Clear, Rain, Clouds, etc.
    feels_like: float  # Celsius
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'wind_speed': self.wind_speed,
            'rain_volume': self.rain_volume,
            'cloud_coverage': self.cloud_coverage,
            'condition': self.condition,
            'feels_like': self.feels_like
        }

class WeatherAPI:
    """Base class for weather API integrations"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.cache_file = '/home/alessio/Customers/Abbanoa/data/weather_cache.json'
        self._cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cached weather data"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save weather data to cache"""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self._cache, f, indent=2)
    
    async def get_current_weather(self, lat: float, lon: float) -> Optional[WeatherData]:
        """Get current weather data"""
        raise NotImplementedError
    
    async def get_forecast(self, lat: float, lon: float, hours: int = 24) -> List[WeatherData]:
        """Get weather forecast"""
        raise NotImplementedError

class OpenWeatherMapAPI(WeatherAPI):
    """OpenWeatherMap API integration"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    async def get_current_weather(self, lat: float, lon: float) -> Optional[WeatherData]:
        """Get current weather from OpenWeatherMap"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/weather"
                params = {
                    'lat': lat,
                    'lon': lon,
                    'appid': self.api_key,
                    'units': 'metric'
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        weather = WeatherData(
                            timestamp=datetime.now(timezone.utc),
                            temperature=data['main']['temp'],
                            humidity=data['main']['humidity'],
                            pressure=data['main']['pressure'],
                            wind_speed=data['wind']['speed'],
                            rain_volume=data.get('rain', {}).get('1h', 0.0),
                            cloud_coverage=data['clouds']['all'],
                            condition=data['weather'][0]['main'],
                            feels_like=data['main']['feels_like']
                        )
                        
                        # Cache the result
                        cache_key = f"current_{lat}_{lon}_{weather.timestamp.strftime('%Y%m%d%H')}"
                        self._cache[cache_key] = weather.to_dict()
                        self._save_cache()
                        
                        return weather
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return None
    
    async def get_forecast(self, lat: float, lon: float, hours: int = 24) -> List[WeatherData]:
        """Get weather forecast from OpenWeatherMap"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/forecast"
                params = {
                    'lat': lat,
                    'lon': lon,
                    'appid': self.api_key,
                    'units': 'metric',
                    'cnt': hours // 3  # API returns 3-hour intervals
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        forecasts = []
                        
                        for item in data['list']:
                            weather = WeatherData(
                                timestamp=datetime.fromtimestamp(item['dt'], timezone.utc),
                                temperature=item['main']['temp'],
                                humidity=item['main']['humidity'],
                                pressure=item['main']['pressure'],
                                wind_speed=item['wind']['speed'],
                                rain_volume=item.get('rain', {}).get('3h', 0.0) / 3,  # Convert to hourly
                                cloud_coverage=item['clouds']['all'],
                                condition=item['weather'][0]['main'],
                                feels_like=item['main']['feels_like']
                            )
                            forecasts.append(weather)
                        
                        return forecasts
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            return []

class MockWeatherAPI(WeatherAPI):
    """Mock weather API for testing without real API key"""
    
    async def get_current_weather(self, lat: float, lon: float) -> Optional[WeatherData]:
        """Generate mock weather data"""
        import random
        
        # Simulate Mediterranean climate patterns
        hour = datetime.now(timezone.utc).hour
        base_temp = 22 + 5 * (1 if 10 <= hour <= 16 else -1)
        
        return WeatherData(
            timestamp=datetime.now(timezone.utc),
            temperature=base_temp + random.uniform(-2, 2),
            humidity=60 + random.uniform(-20, 20),
            pressure=1013 + random.uniform(-10, 10),
            wind_speed=random.uniform(1, 10),
            rain_volume=0.0 if random.random() > 0.1 else random.uniform(0.1, 5),
            cloud_coverage=random.uniform(0, 100),
            condition=random.choice(['Clear', 'Clouds', 'Rain'] if random.random() > 0.1 else ['Clear']),
            feels_like=base_temp + random.uniform(-3, 3)
        )
    
    async def get_forecast(self, lat: float, lon: float, hours: int = 24) -> List[WeatherData]:
        """Generate mock forecast data"""
        forecasts = []
        current = await self.get_current_weather(lat, lon)
        
        for h in range(hours):
            # Create variations from current weather
            weather = WeatherData(
                timestamp=current.timestamp.replace(hour=(current.timestamp.hour + h) % 24),
                temperature=current.temperature + h * 0.1,
                humidity=current.humidity,
                pressure=current.pressure,
                wind_speed=current.wind_speed,
                rain_volume=current.rain_volume,
                cloud_coverage=current.cloud_coverage,
                condition=current.condition,
                feels_like=current.feels_like + h * 0.1
            )
            forecasts.append(weather)
        
        return forecasts

def get_weather_api(api_key: Optional[str] = None, provider: str = 'openweathermap') -> WeatherAPI:
    """Factory function to get weather API instance"""
    if not api_key:
        logger.warning("No weather API key provided, using mock data")
        return MockWeatherAPI("")
    
    if provider == 'openweathermap':
        return OpenWeatherMapAPI(api_key)
    else:
        raise ValueError(f"Unknown weather provider: {provider}")

def calculate_weather_impact(weather: WeatherData) -> Dict[str, float]:
    """Calculate impact factors based on weather conditions"""
    impacts = {
        'flow_rate_multiplier': 1.0,
        'pressure_multiplier': 1.0,
        'temperature_offset': 0.0
    }
    
    # Temperature impact on water consumption
    if weather.temperature > 30:
        impacts['flow_rate_multiplier'] *= 1.3  # 30% more consumption
    elif weather.temperature > 25:
        impacts['flow_rate_multiplier'] *= 1.15
    elif weather.temperature < 10:
        impacts['flow_rate_multiplier'] *= 0.9  # Less consumption
    
    # Rain impact
    if weather.rain_volume > 0:
        impacts['flow_rate_multiplier'] *= 0.8  # Less irrigation/washing
        impacts['pressure_multiplier'] *= 1.05  # Slightly higher pressure
    
    # Humidity impact
    if weather.humidity < 40:
        impacts['flow_rate_multiplier'] *= 1.1  # Dry conditions
    
    # Wind impact on pressure
    if weather.wind_speed > 10:
        impacts['pressure_multiplier'] *= 0.98
    
    # Temperature offset for water temperature sensors
    impacts['temperature_offset'] = (weather.temperature - 20) * 0.3
    
    return impacts

# Demo usage
async def demo():
    """Demo weather integration"""
    # Cagliari coordinates
    lat, lon = 39.2238, 9.1217
    
    # Use mock API for demo
    weather_api = get_weather_api()
    
    print("🌤️  Weather Integration Demo")
    print("=" * 50)
    
    # Get current weather
    current = await weather_api.get_current_weather(lat, lon)
    if current:
        print(f"\nCurrent Weather in Cagliari:")
        print(f"  Temperature: {current.temperature:.1f}°C (feels like {current.feels_like:.1f}°C)")
        print(f"  Condition: {current.condition}")
        print(f"  Humidity: {current.humidity:.0f}%")
        print(f"  Rain: {current.rain_volume:.1f} mm/h")
        
        # Calculate impacts
        impacts = calculate_weather_impact(current)
        print(f"\nImpact on Water System:")
        print(f"  Flow Rate: {impacts['flow_rate_multiplier']:.0%} of normal")
        print(f"  Pressure: {impacts['pressure_multiplier']:.0%} of normal")
        print(f"  Water Temp Offset: {impacts['temperature_offset']:+.1f}°C")

if __name__ == "__main__":
    asyncio.run(demo())
