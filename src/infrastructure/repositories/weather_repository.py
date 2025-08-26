
import asyncpg
from typing import List, Optional
from src.schemas.weather import (
    Weather, HistoricalWeather, WeatherStatistics, WeatherLocation, 
    WeatherImpactAnalysis, Temperature, TemperatureRange, Overview, 
    SeasonalPattern, TemperatureImpact, RainfallImpact, Recommendation
)
from datetime import datetime, timedelta

class WeatherRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_current_weather(self, location: Optional[str]) -> List[Weather]:
        async with self.pool.acquire() as conn:
            if location:
                rows = await conn.fetch("""
                    SELECT DISTINCT ON (location)
                        location, date, avg_temperature_c, min_temperature_c, max_temperature_c,
                        humidity_percent, rainfall_mm, avg_wind_speed_kmh, weather_phenomena
                    FROM water_infrastructure.weather_data
                    WHERE location = $1
                    ORDER BY location, date DESC
                """, location)
            else:
                rows = await conn.fetch("""
                    SELECT DISTINCT ON (location)
                        location, date, avg_temperature_c, min_temperature_c, max_temperature_c,
                        humidity_percent, rainfall_mm, avg_wind_speed_kmh, weather_phenomena
                    FROM water_infrastructure.weather_data
                    ORDER BY location, date DESC
                """)
            
            return [Weather(
                location=row['location'],
                date=row['date'].isoformat(),
                temperature=Temperature(
                    current=float(row['avg_temperature_c']) if row['avg_temperature_c'] else None,
                    min=float(row['min_temperature_c']) if row['min_temperature_c'] else None,
                    max=float(row['max_temperature_c']) if row['max_temperature_c'] else None
                ),
                humidity=row['humidity_percent'],
                rainfall=float(row['rainfall_mm']) if row['rainfall_mm'] else 0,
                windSpeed=float(row['avg_wind_speed_kmh']) if row['avg_wind_speed_kmh'] else 0,
                conditions=row['weather_phenomena'] or "Clear"
            ) for row in rows]

    async def get_historical_weather(self, location: Optional[str], start_date: Optional[str], end_date: Optional[str], interval: str) -> List[HistoricalWeather]:
        async with self.pool.acquire() as conn:
            if not end_date:
                end_date = datetime.now().date()
            else:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).date()
            else:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            
            if interval == "daily":
                if location:
                    rows = await conn.fetch("""
                        SELECT location, date, avg_temperature_c, min_temperature_c, max_temperature_c,
                               humidity_percent, rainfall_mm, avg_wind_speed_kmh, weather_phenomena
                        FROM water_infrastructure.weather_data
                        WHERE location = $1 AND date BETWEEN $2 AND $3
                        ORDER BY date
                    """, location, start_date, end_date)
                else:
                    rows = await conn.fetch("""
                        SELECT location, date, avg_temperature_c, min_temperature_c, max_temperature_c,
                               humidity_percent, rainfall_mm, avg_wind_speed_kmh, weather_phenomena
                        FROM water_infrastructure.weather_data
                        WHERE date BETWEEN $1 AND $2
                        ORDER BY location, date
                    """, start_date, end_date)
                
                return [HistoricalWeather(
                    location=row['location'],
                    date=row['date'].isoformat(),
                    temperature=float(row['avg_temperature_c']) if row['avg_temperature_c'] else None,
                    temperatureMin=float(row['min_temperature_c']) if row['min_temperature_c'] else None,
                    temperatureMax=float(row['max_temperature_c']) if row['max_temperature_c'] else None,
                    humidity=row['humidity_percent'],
                    rainfall=float(row['rainfall_mm']) if row['rainfall_mm'] else 0,
                    windSpeed=float(row['avg_wind_speed_kmh']) if row['avg_wind_speed_kmh'] else 0,
                    conditions=row['weather_phenomena'] or "Clear"
                ) for row in rows]
                
            elif interval == "weekly":
                rows = await conn.fetch("""
                    SELECT 
                        DATE_TRUNC('week', date) as week_start,
                        AVG(avg_temperature_c) as avg_temp,
                        MIN(min_temperature_c) as min_temp,
                        MAX(max_temperature_c) as max_temp,
                        AVG(humidity_percent) as avg_humidity,
                        SUM(rainfall_mm) as total_rainfall,
                        AVG(avg_wind_speed_kmh) as avg_wind
                    FROM water_infrastructure.weather_data
                    WHERE location = $1 AND date BETWEEN $2 AND $3
                    GROUP BY week_start
                    ORDER BY week_start
                """, location, start_date, end_date)
                
                return [HistoricalWeather(
                    weekStart=row['week_start'].isoformat(),
                    temperature=float(row['avg_temp']) if row['avg_temp'] else None,
                    temperatureMin=float(row['min_temp']) if row['min_temp'] else None,
                    temperatureMax=float(row['max_temp']) if row['max_temp'] else None,
                    humidity=float(row['avg_humidity']) if row['avg_humidity'] else None,
                    rainfall=float(row['total_rainfall']) if row['total_rainfall'] else 0,
                    windSpeed=float(row['avg_wind']) if row['avg_wind'] else 0
                ) for row in rows]
                
            else:  # monthly
                rows = await conn.fetch("""
                    SELECT 
                        DATE_TRUNC('month', date) as month_start,
                        AVG(avg_temperature_c) as avg_temp,
                        MIN(min_temperature_c) as min_temp,
                        MAX(max_temperature_c) as max_temp,
                        AVG(humidity_percent) as avg_humidity,
                        SUM(rainfall_mm) as total_rainfall,
                        AVG(avg_wind_speed_kmh) as avg_wind
                    FROM water_infrastructure.weather_data
                    WHERE location = $1 AND date BETWEEN $2 AND $3
                    GROUP BY month_start
                    ORDER BY month_start
                """, location, start_date, end_date)
                
                return [HistoricalWeather(
                    month=row['month_start'].isoformat(),
                    temperature=float(row['avg_temp']) if row['avg_temp'] else None,
                    temperatureMin=float(row['min_temp']) if row['min_temp'] else None,
                    temperatureMax=float(row['max_temp']) if row['max_temp'] else None,
                    humidity=float(row['avg_humidity']) if row['avg_humidity'] else None,
                    rainfall=float(row['total_rainfall']) if row['total_rainfall'] else 0,
                    windSpeed=float(row['avg_wind']) if row['avg_wind'] else 0
                ) for row in rows]

    async def get_weather_statistics(self, location: Optional[str]) -> WeatherStatistics:
        async with self.pool.acquire() as conn:
            if location:
                weather_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_days,
                        AVG(avg_temperature_c) as avg_temp,
                        MIN(min_temperature_c) as min_temp,
                        MAX(max_temperature_c) as max_temp,
                        SUM(rainfall_mm) as total_rainfall,
                        AVG(rainfall_mm) as avg_daily_rainfall,
                        COUNT(CASE WHEN rainfall_mm > 0 THEN 1 END) as rainy_days
                    FROM water_infrastructure.weather_data
                    WHERE location = $1
                """, location)
            else:
                weather_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_days,
                        AVG(avg_temperature_c) as avg_temp,
                        MIN(min_temperature_c) as min_temp,
                        MAX(max_temperature_c) as max_temp,
                        SUM(rainfall_mm) as total_rainfall,
                        AVG(rainfall_mm) as avg_daily_rainfall,
                        COUNT(CASE WHEN rainfall_mm > 0 THEN 1 END) as rainy_days
                    FROM water_infrastructure.weather_data
                """)
            
            seasonal_data = await conn.fetch("""
                SELECT 
                    EXTRACT(MONTH FROM date) as month,
                    AVG(avg_temperature_c) as avg_temp,
                    SUM(rainfall_mm) as total_rainfall
                FROM water_infrastructure.weather_data
                WHERE ($1::text IS NULL OR location = $1)
                GROUP BY month
                ORDER BY month
            """, location)
            
            overview = Overview(
                totalDays=weather_stats['total_days'],
                averageTemperature=float(weather_stats['avg_temp']) if weather_stats['avg_temp'] else None,
                temperatureRange=TemperatureRange(
                    min=float(weather_stats['min_temp']) if weather_stats['min_temp'] else None,
                    max=float(weather_stats['max_temp']) if weather_stats['max_temp'] else None
                ),
                totalRainfall=float(weather_stats['total_rainfall']) if weather_stats['total_rainfall'] else 0,
                averageDailyRainfall=float(weather_stats['avg_daily_rainfall']) if weather_stats['avg_daily_rainfall'] else 0,
                rainyDays=weather_stats['rainy_days'],
                dryDays=weather_stats['total_days'] - weather_stats['rainy_days']
            )

            seasonal_patterns = [SeasonalPattern(
                month=int(row['month']),
                avgTemperature=float(row['avg_temp']) if row['avg_temp'] else None,
                totalRainfall=float(row['total_rainfall']) if row['total_rainfall'] else 0
            ) for row in seasonal_data]

            return WeatherStatistics(overview=overview, seasonalPatterns=seasonal_patterns)

    async def get_weather_locations(self) -> List[WeatherLocation]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT DISTINCT location,
                       COUNT(*) as data_points,
                       MIN(date) as first_date,
                       MAX(date) as last_date
                FROM water_infrastructure.weather_data
                GROUP BY location
                ORDER BY location
            """)
            
            return [WeatherLocation(
                location=row['location'],
                dataPoints=row['data_points'],
                dateRange={
                    "start": row['first_date'].isoformat(),
                    "end": row['last_date'].isoformat()
                }
            ) for row in rows]

    async def get_weather_impact_analysis(self) -> WeatherImpactAnalysis:
        async with self.pool.acquire() as conn:
            temp_impact = await conn.fetch("""
                WITH temp_ranges AS (
                    SELECT 
                        CASE 
                            WHEN avg_temperature_c < 10 THEN 'Cold (<10°C)'
                            WHEN avg_temperature_c < 20 THEN 'Mild (10-20°C)'
                            WHEN avg_temperature_c < 30 THEN 'Warm (20-30°C)'
                            ELSE 'Hot (>30°C)'
                        END as temp_range,
                        date
                    FROM water_infrastructure.weather_data
                )
                SELECT 
                    temp_range,
                    COUNT(*) as days,
                    CASE 
                        WHEN temp_range = 'Cold (<10°C)' THEN 95
                        WHEN temp_range = 'Mild (10-20°C)' THEN 100
                        WHEN temp_range = 'Warm (20-30°C)' THEN 115
                        ELSE 130
                    END as relative_consumption
                FROM temp_ranges
                GROUP BY temp_range
                ORDER BY 
                    CASE temp_range
                        WHEN 'Cold (<10°C)' THEN 1
                        WHEN 'Mild (10-20°C)' THEN 2
                        WHEN 'Warm (20-30°C)' THEN 3
                        ELSE 4
                    END
            """)
            
            rainfall_impact = await conn.fetch("""
                WITH rainfall_categories AS (
                    SELECT 
                        CASE 
                            WHEN rainfall_mm = 0 THEN 'No Rain'
                            WHEN rainfall_mm < 5 THEN 'Light Rain (0-5mm)'
                            WHEN rainfall_mm < 20 THEN 'Moderate Rain (5-20mm)'
                            ELSE 'Heavy Rain (>20mm)'
                        END as rainfall_category,
                        date
                    FROM water_infrastructure.weather_data
                )
                SELECT 
                    rainfall_category,
                    COUNT(*) as days,
                    CASE 
                        WHEN rainfall_category = 'No Rain' THEN 98
                        WHEN rainfall_category = 'Light Rain (0-5mm)' THEN 95
                        WHEN rainfall_category = 'Moderate Rain (5-20mm)' THEN 90
                        ELSE 85
                    END as system_efficiency
                FROM rainfall_categories
                GROUP BY rainfall_category
                ORDER BY 
                    CASE rainfall_category
                        WHEN 'No Rain' THEN 1
                        WHEN 'Light Rain (0-5mm)' THEN 2
                        WHEN 'Moderate Rain (5-20mm)' THEN 3
                        ELSE 4
                    END
            """)
            
            recommendations = [
                Recommendation(condition="High Temperature", impact="Increased water demand by 30-40%", action="Increase pump capacity and monitor pressure levels"),
                Recommendation(condition="Heavy Rainfall", impact="Potential infiltration and system efficiency reduction", action="Increase monitoring frequency and check for anomalies"),
                Recommendation(condition="Prolonged Dry Period", impact="Higher continuous demand", action="Implement water conservation measures")
            ]

            return WeatherImpactAnalysis(
                temperatureImpact=[TemperatureImpact(range=row['temp_range'], days=row['days'], relativeConsumption=row['relative_consumption'], unit="%") for row in temp_impact],
                rainfallImpact=[RainfallImpact(category=row['rainfall_category'], days=row['days'], systemEfficiency=row['system_efficiency'], unit="%") for row in rainfall_impact],
                recommendations=recommendations
            )
