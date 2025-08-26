
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from src.application.services.weather_service import WeatherService
from src.presentation.api.dependencies import get_weather_service
from src.schemas.weather import Weather, HistoricalWeather, WeatherStatistics, WeatherLocation, WeatherImpactAnalysis

router = APIRouter()

@router.get("/weather/current", response_model=List[Weather])
async def get_current_weather(
    location: Optional[str] = Query(None, description="Filter by location name"),
    weather_service: WeatherService = Depends(get_weather_service)
):
    try:
        return await weather_service.get_current_weather(location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather/historical", response_model=List[HistoricalWeather])
async def get_historical_weather(
    location: Optional[str] = Query(None, description="Location name (optional, returns all locations if not specified)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    interval: str = Query("daily", description="Data interval: daily, weekly, monthly"),
    weather_service: WeatherService = Depends(get_weather_service)
):
    try:
        return await weather_service.get_historical_weather(location, start_date, end_date, interval)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather/statistics", response_model=WeatherStatistics)
async def get_weather_statistics(
    location: Optional[str] = Query(None, description="Filter by location name"),
    weather_service: WeatherService = Depends(get_weather_service)
):
    try:
        return await weather_service.get_weather_statistics(location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather/locations", response_model=List[WeatherLocation])
async def get_weather_locations(weather_service: WeatherService = Depends(get_weather_service)):
    try:
        return await weather_service.get_weather_locations()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather/impact-analysis", response_model=WeatherImpactAnalysis)
async def get_weather_impact_analysis(weather_service: WeatherService = Depends(get_weather_service)):
    try:
        return await weather_service.get_weather_impact_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
