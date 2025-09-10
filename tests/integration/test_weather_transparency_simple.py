"""Simple test runner for weather transparency without pytest."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from src.servers.weather_server_prod import app

def test_current_weather_data_source():
    """Test that current weather includes data_source field."""
    client = TestClient(app)
    response = client.get("/weather/current")
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response sample: {data[0] if data else 'No data'}")
    
    # Check for data_source field
    for location_data in data:
        if "data_source" not in location_data:
            print(f"❌ FAIL: Missing 'data_source' field in {location_data.get('location', 'unknown')}")
            return False
        else:
            print(f"✓ Found data_source: {location_data['data_source']}")
    
    return True

def test_last_real_update_field():
    """Test for last_real_update timestamp."""
    client = TestClient(app)
    response = client.get("/weather/current")
    
    data = response.json()
    
    for location_data in data:
        if "last_real_update" not in location_data:
            print(f"❌ FAIL: Missing 'last_real_update' field in {location_data.get('location', 'unknown')}")
            return False
    
    return True

if __name__ == "__main__":
    print("Running weather transparency tests...")
    print("-" * 50)
    
    tests = [
        ("Data source field test", test_current_weather_data_source),
        ("Last real update test", test_last_real_update_field)
    ]
    
    failed = []
    for name, test_func in tests:
        print(f"\nRunning: {name}")
        try:
            if not test_func():
                failed.append(name)
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed.append(name)
    
    print("\n" + "=" * 50)
    if failed:
        print(f"❌ {len(failed)} tests FAILED (Expected in RED phase):")
        for test in failed:
            print(f"  - {test}")
    else:
        print("✅ All tests passed (Unexpected in RED phase!)")