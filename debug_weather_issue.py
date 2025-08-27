#!/usr/bin/env python3
"""Debug weather data issue."""

import asyncio
import asyncpg
import os
from datetime import datetime
import requests

POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5434)),
    "database": os.getenv("POSTGRES_DB", "abbanoa_processing"),
    "user": os.getenv("POSTGRES_USER", "abbanoa_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "abbanoa_secure_pass"),
}

async def debug_weather_data():
    """Debug weather data issues."""
    conn = await asyncpg.connect(**POSTGRES_CONFIG)
    
    try:
        print("🔍 Debugging Weather Data...\n")
        
        # Check Selargius data
        print("1. Checking Selargius data in database:")
        result = await conn.fetchrow("""
            SELECT 
                MIN(date) as min_date, 
                MAX(date) as max_date,
                COUNT(*) as total_records,
                COUNT(DISTINCT date) as unique_dates
            FROM water_infrastructure.weather_data
            WHERE location = 'Selargius'
        """)
        print(f"   Date range: {result['min_date']} to {result['max_date']}")
        print(f"   Total records: {result['total_records']}")
        print(f"   Unique dates: {result['unique_dates']}")
        
        # Check recent data
        print("\n2. Recent Selargius records:")
        recent = await conn.fetch("""
            SELECT date, avg_temperature_c, weather_phenomena
            FROM water_infrastructure.weather_data
            WHERE location = 'Selargius'
            ORDER BY date DESC
            LIMIT 5
        """)
        for row in recent:
            print(f"   {row['date']}: {row['avg_temperature_c']}°C - {row['weather_phenomena']}")
        
        # Check data within last 7 days
        print("\n3. Data within last 7 days:")
        last_week = await conn.fetch("""
            SELECT date, location, avg_temperature_c
            FROM water_infrastructure.weather_data
            WHERE location = 'Selargius' 
            AND date >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY date DESC
        """)
        print(f"   Found {len(last_week)} records in last 7 days")
        
        # Check data within date range used by test
        print("\n4. Data for test date range (2024-01-01 to 2024-01-08):")
        test_range = await conn.fetch("""
            SELECT date, location, avg_temperature_c
            FROM water_infrastructure.weather_data
            WHERE location = 'Selargius' 
            AND date BETWEEN '2024-01-01' AND '2024-01-08'
            ORDER BY date
        """)
        print(f"   Found {len(test_range)} records for test range")
        if test_range:
            for row in test_range[:3]:
                print(f"   {row['date']}: {row['avg_temperature_c']}°C")
        
    finally:
        await conn.close()
    
    # Test API calls
    print("\n5. Testing API calls:")
    
    # Test historical with proper date range
    print("\n   Testing /weather/historical with Selargius date range:")
    response = requests.get("http://localhost:8000/api/v1/weather/historical", params={
        'start_date': '2023-06-01',
        'end_date': '2023-06-10',
        'interval': 'daily'
    })
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Records returned: {len(data)}")
    if data:
        print(f"   First record: {data[0]}")

if __name__ == "__main__":
    asyncio.run(debug_weather_data())
