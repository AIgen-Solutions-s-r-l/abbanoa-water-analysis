from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
import random
import json
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/weather", tags=["weather"])

# Weather data models
class WeatherLocation(BaseModel):
    location: str
    dataPoints: int
    dateRange: dict

class Temperature(BaseModel):
    current: Optional[float]
    min: Optional[float]
    max: Optional[float]

class CurrentWeather(BaseModel):
    location: str
    date: str
    temperature: Temperature
    humidity: Optional[float]
    rainfall: float
    windSpeed: float
    conditions: str

class WeatherOverview(BaseModel):
    totalDays: int
    averageTemperature: Optional[float]
    temperatureRange: dict
    totalRainfall: float
    averageDailyRainfall: float
    rainyDays: int
    dryDays: int

class WeatherStatistics(BaseModel):
    overview: WeatherOverview
    seasonalPatterns: List[dict]

class ImpactAnalysis(BaseModel):
    temperatureImpact: List[dict]
    rainfallImpact: List[dict]
    recommendations: List[dict]

# Cagliari and its districts coordinates
CAGLIARI_LOCATIONS = {
    "Cagliari": {"lat": 39.2238, "lon": 9.1217},
    "Selargius": {"lat": 39.2556, "lon": 9.1639},
    "Quartucciu": {"lat": 39.2539, "lon": 9.1753},
    "Elmas": {"lat": 39.2667, "lon": 9.0500},
    "Assemini": {"lat": 39.2833, "lon": 9.0000},
    "Capoterra": {"lat": 39.1833, "lon": 8.9667},
    "Sestu": {"lat": 39.3000, "lon": 9.0833},
    "Monserrato": {"lat": 39.2500, "lon": 9.1333}
}

def generate_realistic_weather_data(location: str, days: int = 30) -> List[dict]:
    """Generate realistic weather data for Cagliari region"""
    data = []
    base_date = datetime.now() - timedelta(days=days)
    
    # Cagliari has a Mediterranean climate
    # Summer: hot and dry (June-August)
    # Winter: mild and wet (December-February)
    # Spring/Fall: moderate temperatures
    
    for i in range(days):
        current_date = base_date + timedelta(days=i)
        month = current_date.month
        
        # Seasonal temperature adjustments
        if month in [12, 1, 2]:  # Winter
            base_temp = 12
            temp_variation = 8
            rainfall_prob = 0.4
        elif month in [3, 4, 5]:  # Spring
            base_temp = 18
            temp_variation = 6
            rainfall_prob = 0.3
        elif month in [6, 7, 8]:  # Summer
            base_temp = 28
            temp_variation = 5
            rainfall_prob = 0.1
        else:  # Fall
            base_temp = 20
            temp_variation = 7
            rainfall_prob = 0.35
        
        # Add some randomness
        current_temp = base_temp + random.uniform(-temp_variation, temp_variation)
        min_temp = current_temp - random.uniform(3, 8)
        max_temp = current_temp + random.uniform(3, 8)
        
        # Rainfall
        rainfall = 0
        if random.random() < rainfall_prob:
            rainfall = random.uniform(0.1, 15.0)
        
        # Humidity (higher when raining, lower in summer)
        if rainfall > 0:
            humidity = random.uniform(70, 95)
        elif month in [6, 7, 8]:
            humidity = random.uniform(40, 65)
        else:
            humidity = random.uniform(50, 80)
        
        # Wind speed
        wind_speed = random.uniform(5, 25)
        
        # Weather conditions
        if rainfall > 5:
            conditions = "Rain"
        elif rainfall > 0:
            conditions = "Light Rain"
        elif current_temp > 25:
            conditions = "Clear"
        elif current_temp > 15:
            conditions = "Partly Cloudy"
        else:
            conditions = "Cloudy"
        
        data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "avg_temperature_c": round(current_temp, 1),
            "min_temperature_c": round(min_temp, 1),
            "max_temperature_c": round(max_temp, 1),
            "humidity_percent": round(humidity, 1),
            "rainfall_mm": round(rainfall, 1),
            "avg_wind_speed_kmh": round(wind_speed, 1)
        })
    
    return data

@router.get("/locations", response_model=List[WeatherLocation])
async def get_weather_locations():
    """Get available weather monitoring locations"""
    locations = []
    for location in CAGLIARI_LOCATIONS.keys():
        locations.append({
            "location": location,
            "dataPoints": random.randint(800, 1200),
            "dateRange": {
                "start": "2024-11-01",
                "end": "2025-06-30"
            }
        })
    return locations

@router.get("/current", response_model=List[CurrentWeather])
async def get_current_weather(location: Optional[str] = Query(None, description="Specific location")):
    """Get current weather data"""
    if location and location not in CAGLIARI_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")
    
    locations_to_return = [location] if location else list(CAGLIARI_LOCATIONS.keys())
    current_weather = []
    
    for loc in locations_to_return:
        # Generate current weather data
        current_temp = random.uniform(15, 30)
        min_temp = current_temp - random.uniform(3, 8)
        max_temp = current_temp + random.uniform(3, 8)
        humidity = random.uniform(50, 85)
        rainfall = random.uniform(0, 5)
        wind_speed = random.uniform(5, 20)
        
        # Determine conditions
        if rainfall > 2:
            conditions = "Rain"
        elif rainfall > 0:
            conditions = "Light Rain"
        elif current_temp > 25:
            conditions = "Clear"
        elif current_temp > 15:
            conditions = "Partly Cloudy"
        else:
            conditions = "Cloudy"
        
        current_weather.append({
            "location": loc,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "temperature": {
                "current": round(current_temp, 1),
                "min": round(min_temp, 1),
                "max": round(max_temp, 1)
            },
            "humidity": round(humidity, 1),
            "rainfall": round(rainfall, 1),
            "windSpeed": round(wind_speed, 1),
            "conditions": conditions
        })
    
    return current_weather

@router.get("/historical")
async def get_historical_weather(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    interval: str = Query("daily", description="Data interval (daily, weekly, monthly)"),
    location: Optional[str] = Query(None, description="Specific location")
):
    """Get historical weather data"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    if location and location not in CAGLIARI_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")
    
    # Generate historical data
    historical_data = generate_realistic_weather_data(
        location or "Cagliari", 
        min(days, 365)  # Limit to 1 year max
    )
    
    # Apply interval grouping if needed
    if interval == "weekly":
        # Group by week
        weekly_data = []
        for i in range(0, len(historical_data), 7):
            week_data = historical_data[i:i+7]
            if week_data:
                avg_temp = sum(d["avg_temperature_c"] for d in week_data) / len(week_data)
                total_rainfall = sum(d["rainfall_mm"] for d in week_data)
                avg_humidity = sum(d["humidity_percent"] for d in week_data) / len(week_data)
                avg_wind = sum(d["avg_wind_speed_kmh"] for d in week_data) / len(week_data)
                
                weekly_data.append({
                    "weekStart": week_data[0]["date"],
                    "avg_temperature_c": round(avg_temp, 1),
                    "rainfall_mm": round(total_rainfall, 1),
                    "humidity_percent": round(avg_humidity, 1),
                    "avg_wind_speed_kmh": round(avg_wind, 1)
                })
        return weekly_data
    elif interval == "monthly":
        # Group by month
        monthly_data = []
        current_month = None
        month_data = []
        
        for data_point in historical_data:
            month = datetime.strptime(data_point["date"], "%Y-%m-%d").strftime("%Y-%m")
            if current_month != month:
                if month_data:
                    avg_temp = sum(d["avg_temperature_c"] for d in month_data) / len(month_data)
                    total_rainfall = sum(d["rainfall_mm"] for d in month_data)
                    avg_humidity = sum(d["humidity_percent"] for d in month_data) / len(month_data)
                    avg_wind = sum(d["avg_wind_speed_kmh"] for d in month_data) / len(month_data)
                    
                    monthly_data.append({
                        "month": current_month,
                        "avg_temperature_c": round(avg_temp, 1),
                        "rainfall_mm": round(total_rainfall, 1),
                        "humidity_percent": round(avg_humidity, 1),
                        "avg_wind_speed_kmh": round(avg_wind, 1)
                    })
                current_month = month
                month_data = []
            month_data.append(data_point)
        
        # Add last month
        if month_data:
            avg_temp = sum(d["avg_temperature_c"] for d in month_data) / len(month_data)
            total_rainfall = sum(d["rainfall_mm"] for d in month_data)
            avg_humidity = sum(d["humidity_percent"] for d in month_data) / len(month_data)
            avg_wind = sum(d["avg_wind_speed_kmh"] for d in month_data) / len(month_data)
            
            monthly_data.append({
                "month": current_month,
                "avg_temperature_c": round(avg_temp, 1),
                "rainfall_mm": round(total_rainfall, 1),
                "humidity_percent": round(avg_humidity, 1),
                "avg_wind_speed_kmh": round(avg_wind, 1)
            })
        
        return monthly_data
    
    return historical_data

@router.get("/statistics", response_model=WeatherStatistics)
async def get_weather_statistics(location: Optional[str] = Query(None, description="Specific location")):
    """Get weather statistics"""
    if location and location not in CAGLIARI_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location '{location}' not found")
    
    # Generate 30 days of data for statistics
    historical_data = generate_realistic_weather_data(location or "Cagliari", 30)
    
    # Calculate statistics
    temperatures = [d["avg_temperature_c"] for d in historical_data]
    rainfalls = [d["rainfall_mm"] for d in historical_data]
    
    avg_temp = sum(temperatures) / len(temperatures)
    total_rainfall = sum(rainfalls)
    rainy_days = len([r for r in rainfalls if r > 0])
    dry_days = len([r for r in rainfalls if r == 0])
    
    # Generate seasonal patterns (12 months)
    seasonal_patterns = []
    for month in range(1, 13):
        if month in [12, 1, 2]:  # Winter
            avg_temp_month = random.uniform(10, 15)
            total_rainfall_month = random.uniform(80, 120)
        elif month in [3, 4, 5]:  # Spring
            avg_temp_month = random.uniform(15, 20)
            total_rainfall_month = random.uniform(60, 100)
        elif month in [6, 7, 8]:  # Summer
            avg_temp_month = random.uniform(25, 30)
            total_rainfall_month = random.uniform(10, 30)
        else:  # Fall
            avg_temp_month = random.uniform(18, 23)
            total_rainfall_month = random.uniform(70, 110)
        
        seasonal_patterns.append({
            "month": month,
            "avgTemperature": round(avg_temp_month, 1),
            "totalRainfall": round(total_rainfall_month, 1)
        })
    
    return {
        "overview": {
            "totalDays": 30,
            "averageTemperature": round(avg_temp, 1),
            "temperatureRange": {
                "min": round(min(temperatures), 1),
                "max": round(max(temperatures), 1)
            },
            "totalRainfall": round(total_rainfall, 1),
            "averageDailyRainfall": round(total_rainfall / 30, 1),
            "rainyDays": rainy_days,
            "dryDays": dry_days
        },
        "seasonalPatterns": seasonal_patterns
    }

@router.get("/impact-analysis", response_model=ImpactAnalysis)
async def get_weather_impact_analysis():
    """Get weather impact analysis on water consumption"""
    return {
        "temperatureImpact": [
            {"range": "Cold (<10°C)", "days": 45, "relativeConsumption": 85, "unit": "%"},
            {"range": "Cool (10-15°C)", "days": 90, "relativeConsumption": 95, "unit": "%"},
            {"range": "Mild (15-20°C)", "days": 120, "relativeConsumption": 100, "unit": "%"},
            {"range": "Warm (20-25°C)", "days": 60, "relativeConsumption": 115, "unit": "%"},
            {"range": "Hot (>25°C)", "days": 50, "relativeConsumption": 130, "unit": "%"}
        ],
        "rainfallImpact": [
            {"category": "Dry Days", "days": 200, "systemEfficiency": 98, "unit": "%"},
            {"category": "Light Rain", "days": 100, "systemEfficiency": 95, "unit": "%"},
            {"category": "Moderate Rain", "days": 50, "systemEfficiency": 90, "unit": "%"},
            {"category": "Heavy Rain", "days": 15, "systemEfficiency": 85, "unit": "%"}
        ],
        "recommendations": [
            {
                "condition": "High Temperature Alert",
                "impact": "Water demand increases by 15-30% during hot weather",
                "action": "Activate peak demand protocols and increase reservoir levels"
            },
            {
                "condition": "Heavy Rainfall Warning",
                "impact": "System efficiency drops by 10-15% due to infiltration",
                "action": "Monitor water quality and adjust treatment parameters"
            },
            {
                "condition": "Seasonal Transition",
                "impact": "Gradual changes in consumption patterns",
                "action": "Update demand forecasting models and adjust distribution"
            }
        ]
    }
