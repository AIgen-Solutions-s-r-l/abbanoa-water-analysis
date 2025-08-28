from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(title="Weather Test API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3001", "http://localhost:3000", "https://curator.abbanoa.aigensolutions.it"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/")
async def root():
    return {"message": "Weather API is running!"}

@app.get("/weather/locations")
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

@app.get("/weather/current")
async def get_current_weather():
    """Get current weather data"""
    current_weather = []
    
    for loc in CAGLIARI_LOCATIONS.keys():
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

@app.get("/weather/statistics")
async def get_weather_statistics():
    """Get weather statistics"""
    return {
        "overview": {
            "totalDays": 30,
            "averageTemperature": 23.5,
            "temperatureRange": {
                "min": 15.2,
                "max": 32.1
            },
            "totalRainfall": 45.2,
            "averageDailyRainfall": 1.5,
            "rainyDays": 8,
            "dryDays": 22
        },
        "seasonalPatterns": [
            {"month": 1, "avgTemperature": 12.5, "totalRainfall": 85.3},
            {"month": 2, "avgTemperature": 13.2, "totalRainfall": 78.1},
            {"month": 3, "avgTemperature": 15.8, "totalRainfall": 65.4}
        ]
    }

@app.get("/weather/historical")
async def get_historical_weather(
    start_date: str,
    end_date: str,
    interval: str = "daily",
    location: Optional[str] = None
):
    """Get historical weather data"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}
    
    if location and location not in CAGLIARI_LOCATIONS:
        return {"error": f"Location '{location}' not found"}
    
    # Generate historical data
    historical_data = []
    current_date = start
    
    for i in range(min(days, 365)):  # Limit to 1 year max
        # Generate realistic weather data
        base_temp = 20 + 10 * (i / 365)  # Seasonal variation
        temp_variation = random.uniform(-5, 5)
        avg_temp = base_temp + temp_variation
        
        min_temp = avg_temp - random.uniform(3, 8)
        max_temp = avg_temp + random.uniform(3, 8)
        humidity = random.uniform(50, 85)
        rainfall = random.uniform(0, 10) if random.random() < 0.3 else 0  # 30% chance of rain
        wind_speed = random.uniform(5, 20)
        
        historical_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "avg_temperature_c": round(avg_temp, 1),
            "min_temperature_c": round(min_temp, 1),
            "max_temperature_c": round(max_temp, 1),
            "humidity_percent": round(humidity, 1),
            "rainfall_mm": round(rainfall, 1),
            "avg_wind_speed_kmh": round(wind_speed, 1)
        })
        
        current_date += timedelta(days=1)
    
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

@app.get("/weather/impact-analysis")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
