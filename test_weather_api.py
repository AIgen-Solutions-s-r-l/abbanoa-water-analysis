#!/usr/bin/env python3
"""Test script to verify weather API location transformations."""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_weather_endpoints():
    """Test all weather endpoints for location transformations."""
    
    print("🌤️  Testing Weather API Location Transformations...\n")
    
    # Test 1: Get weather locations
    print("1. Testing /weather/locations endpoint:")
    try:
        response = requests.get(f"{BASE_URL}/weather/locations")
        if response.status_code == 200:
            locations = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📍 Locations found: {len(locations)}")
            for loc in locations:
                print(f"      - {loc['location']} ({loc['dataPoints']} data points)")
            
            # Verify only Roccavina is shown
            location_names = [loc['location'] for loc in locations]
            assert "Roccavina" in location_names, "Roccavina not found in locations"
            assert "Cagliari" not in location_names, "Cagliari should not be visible"
            assert "Maccarese" not in location_names, "Maccarese should not be visible"
            assert "Selargius" not in location_names, "Selargius should not be visible"
            print("   ✅ Location filtering working correctly!")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n2. Testing /weather/current endpoint:")
    try:
        # Test without location filter
        response = requests.get(f"{BASE_URL}/weather/current")
        if response.status_code == 200:
            current_weather = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Current weather data points: {len(current_weather)}")
            for weather in current_weather:
                print(f"      - {weather['location']}: {weather['temperature']['current']}°C")
            
            # Verify transformations
            locations = [w['location'] for w in current_weather]
            assert all(loc == "Roccavina" for loc in locations), "All locations should be Roccavina"
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            
        # Test with location filter
        print("\n   Testing with location filter 'Roccavina':")
        response = requests.get(f"{BASE_URL}/weather/current", params={"location": "Roccavina"})
        if response.status_code == 200:
            filtered_weather = response.json()
            print(f"   ✅ Filtered results: {len(filtered_weather)} location(s)")
            if filtered_weather:
                print(f"   📍 Location: {filtered_weather[0]['location']}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n3. Testing /weather/historical endpoint:")
    try:
        response = requests.get(f"{BASE_URL}/weather/historical", params={"interval": "daily"})
        if response.status_code == 200:
            historical = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📈 Historical data points: {len(historical)}")
            
            # Check unique locations
            unique_locations = set(h['location'] for h in historical)
            print(f"   📍 Unique locations: {', '.join(unique_locations)}")
            assert unique_locations == {"Roccavina"}, "Only Roccavina should be present"
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n4. Testing /weather/statistics endpoint:")
    try:
        response = requests.get(f"{BASE_URL}/weather/statistics", params={"location": "Roccavina"})
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Statistics retrieved successfully")
            if 'temperature' in stats:
                print(f"      - Average temp: {stats['temperature']['average']}°C")
                print(f"      - Total rainfall: {stats['rainfall']['total']}mm")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ All weather API transformation tests completed!")

if __name__ == "__main__":
    test_weather_endpoints()
