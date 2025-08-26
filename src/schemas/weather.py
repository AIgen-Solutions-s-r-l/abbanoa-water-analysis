
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Temperature(BaseModel):
    current: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None

class Weather(BaseModel):
    location: str
    date: str
    temperature: Temperature
    humidity: Optional[int] = None
    rainfall: float
    windSpeed: float
    conditions: str

class HistoricalWeather(BaseModel):
    location: Optional[str] = None
    date: Optional[str] = None
    weekStart: Optional[str] = None
    month: Optional[str] = None
    temperature: Optional[float] = None
    temperatureMin: Optional[float] = None
    temperatureMax: Optional[float] = None
    humidity: Optional[float] = None
    rainfall: float
    windSpeed: float
    conditions: Optional[str] = None

class TemperatureRange(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None

class Overview(BaseModel):
    totalDays: int
    averageTemperature: Optional[float] = None
    temperatureRange: TemperatureRange
    totalRainfall: float
    averageDailyRainfall: float
    rainyDays: int
    dryDays: int

class SeasonalPattern(BaseModel):
    month: int
    avgTemperature: Optional[float] = None
    totalRainfall: float

class WeatherStatistics(BaseModel):
    overview: Overview
    seasonalPatterns: List[SeasonalPattern]

class WeatherLocation(BaseModel):
    location: str
    dataPoints: int
    dateRange: Dict[str, str]

class TemperatureImpact(BaseModel):
    range: str
    days: int
    relativeConsumption: int
    unit: str

class RainfallImpact(BaseModel):
    category: str
    days: int
    systemEfficiency: int
    unit: str

class Recommendation(BaseModel):
    condition: str
    impact: str
    action: str

class WeatherImpactAnalysis(BaseModel):
    temperatureImpact: List[TemperatureImpact]
    rainfallImpact: List[RainfallImpact]
    recommendations: List[Recommendation]
