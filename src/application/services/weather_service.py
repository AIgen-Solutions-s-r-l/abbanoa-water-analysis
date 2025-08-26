
from typing import List, Optional
from src.infrastructure.repositories.weather_repository import WeatherRepository
from src.schemas.weather import Weather, HistoricalWeather, WeatherStatistics, WeatherLocation, WeatherImpactAnalysis

class WeatherService:
    def __init__(self, weather_repository: WeatherRepository):
        self.weather_repository = weather_repository

    async def get_current_weather(self, location: Optional[str]) -> List[Weather]:
        return await self.weather_repository.get_current_weather(location)

    async def get_historical_weather(self, location: Optional[str], start_date: Optional[str], end_date: Optional[str], interval: str) -> List[HistoricalWeather]:
        return await self.weather_repository.get_historical_weather(location, start_date, end_date, interval)

    async def get_weather_statistics(self, location: Optional[str]) -> WeatherStatistics:
        return await self.weather_repository.get_weather_statistics(location)

    async def get_weather_locations(self) -> List[WeatherLocation]:
        return await self.weather_repository.get_weather_locations()

    async def get_weather_impact_analysis(self) -> WeatherImpactAnalysis:
        return await self.weather_repository.get_weather_impact_analysis()
