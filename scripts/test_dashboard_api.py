#!/usr/bin/env python3
"""Test script to verify dashboard API integration."""

import requests
import sys

API_BASE_URL = "http://localhost:8000"


def test_api_endpoints():
    """Test all API endpoints used by the dashboard."""

    endpoints = [
        ("/health", "Health Check"),
        ("/api/v1/nodes", "Nodes List"),
        ("/api/v1/dashboard/summary", "Dashboard Summary"),
        ("/api/v1/status", "System Status"),
    ]

    print("Testing API endpoints...")
    print("-" * 50)

    all_passed = True

    for endpoint, name in endpoints:
        try:
            url = f"{API_BASE_URL}{endpoint}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                print(f"✅ {name}: OK")
                if endpoint == "/api/v1/nodes":
                    data = response.json()
                    print(f"   Found {len(data)} nodes")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                all_passed = False

        except Exception as e:
            print(f"❌ {name}: {str(e)}")
            all_passed = False

    print("-" * 50)

    if all_passed:
        print("✅ All API endpoints are working!")
        print("\nThe dashboard should be accessible at:")
        print("  - Local: http://localhost:8502")
        print("  - Public: https://curator.aigensolutions.it")
        return 0
    else:
        print("❌ Some API endpoints failed!")
        print("\nPlease check:")
        print("  1. Processing services are running:")
        print("     docker compose -f docker-compose.processing.yml ps")
        print("  2. API logs:")
        print("     docker logs abbanoa-api")
        return 1


if __name__ == "__main__":
    sys.exit(test_api_endpoints())
