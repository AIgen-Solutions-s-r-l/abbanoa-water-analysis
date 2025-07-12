#!/usr/bin/env python3
"""Debug script to test API connection from Python (simulates Streamlit)."""

import requests
import os

# Test the same way Streamlit would
api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")

print(f"Testing API connection to: {api_base_url}")

try:
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    response = requests.get(f"{api_base_url}/health", timeout=10)
    print(f"✅ Health Status: {response.status_code}")
    print(f"✅ Response: {response.json()}")

    # Test forecast endpoint
    print("\n2. Testing forecast endpoint...")
    url = f"{api_base_url}/api/v1/forecasts/DIST_001/flow_rate"
    params = {"horizon": 7, "include_historical": False, "historical_days": 7}

    print(f"URL: {url}")
    print(f"Params: {params}")

    response = requests.get(url, params=params, timeout=10)
    print(f"✅ Forecast Status: {response.status_code}")

    data = response.json()
    print(f"✅ Response keys: {list(data.keys())}")
    print(f"✅ Metadata: {data.get('metadata', {})}")

    if data.get("forecast_data"):
        print(f"✅ Forecast data points: {len(data['forecast_data'])}")
    else:
        print("⚠️  No forecast data returned")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("Make sure Docker container is running: docker ps")
