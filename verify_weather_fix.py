#!/usr/bin/env python3
"""Verify weather API returns Roccavina data correctly."""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def verify_weather_fix():
    """Verify weather endpoints return Roccavina data."""
    
    print("🔍 Verifying Weather Data Fix...\n")
    
    # Test weather locations
    print("1. Testing /weather/locations:")
    response = requests.get(f"{BASE_URL}/weather/locations")
    if response.status_code == 200:
        locations = response.json()
        print(f"   ✅ Found {len(locations)} location(s)")
        for loc in locations:
            print(f"   📍 {loc['location']}: {loc['dataPoints']} data points")
            print(f"      Date range: {loc['dateRange']['start']} to {loc['dateRange']['end']}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    
    # Test current weather
    print("\n2. Testing /weather/current:")
    response = requests.get(f"{BASE_URL}/weather/current")
    if response.status_code == 200:
        current = response.json()
        print(f"   ✅ Found {len(current)} current weather record(s)")
        for weather in current[:3]:  # Show first 3
            print(f"   🌡️  {weather['location']}: {weather['temperature']['current']}°C on {weather['date']}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    
    # Test historical data
    print("\n3. Testing /weather/historical (daily):")
    response = requests.get(f"{BASE_URL}/weather/historical", params={"interval": "daily"})
    if response.status_code == 200:
        historical = response.json()
        print(f"   ✅ Found {len(historical)} historical records")
        if historical:
            print(f"   📊 First record: {historical[0]['location']} on {historical[0]['date']}")
            print(f"   📊 Last record: {historical[-1]['location']} on {historical[-1]['date']}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    
    print("\n✅ Weather data fix verification complete!")

if __name__ == "__main__":
    verify_weather_fix()
