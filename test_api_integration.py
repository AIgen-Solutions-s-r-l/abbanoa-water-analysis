#!/usr/bin/env python3
"""
Test script to verify API integration with dashboard.
"""

import requests
import json
from datetime import datetime


def test_api_endpoints():
    """Test all API endpoints."""
    base_url = "http://localhost:8000"

    print("🔍 Testing API Endpoints...")
    print("=" * 50)

    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

    # Test nodes endpoint
    print("\n2. Testing nodes endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/nodes")
        if response.status_code == 200:
            nodes = response.json()
            print(f"✅ Found {len(nodes)} nodes")
            if nodes:
                print(f"   First node: {nodes[0]['node_name']}")
        else:
            print(f"❌ Nodes endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test network metrics
    print("\n3. Testing network metrics...")
    try:
        response = requests.get(f"{base_url}/api/v1/network/metrics?time_range=24h")
        if response.status_code == 200:
            metrics = response.json()
            print("✅ Network metrics retrieved")
            print(f"   Active nodes: {metrics.get('active_nodes', 0)}")
            print(f"   Total flow: {metrics.get('total_flow', 0):.1f} L/s")
            print(f"   Avg pressure: {metrics.get('avg_pressure', 0):.2f} bar")
        else:
            print(f"❌ Network metrics failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test dashboard summary
    print("\n4. Testing dashboard summary...")
    try:
        response = requests.get(f"{base_url}/api/v1/dashboard/summary")
        if response.status_code == 200:
            summary = response.json()
            print("✅ Dashboard summary retrieved")
            print(f"   Nodes with data: {len(summary.get('nodes', []))}")
            print(f"   Recent anomalies: {summary.get('recent_anomalies', 0)}")
        else:
            print(f"❌ Dashboard summary failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test system status
    print("\n5. Testing system status...")
    try:
        response = requests.get(f"{base_url}/api/v1/status")
        if response.status_code == 200:
            status = response.json()
            print("✅ System status retrieved")
            print(f"   Status: {status.get('status', 'unknown')}")
            print(f"   Active models: {len(status.get('active_models', {}))}")
        else:
            print(f"❌ System status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 50)
    print("✅ API integration test completed!")

    return True


def test_dashboard_with_api():
    """Test dashboard with API."""
    print("\n📊 Dashboard API Integration")
    print("=" * 50)

    print("\nTo test the dashboard with API:")
    print("1. Ensure processing services are running:")
    print("   ./scripts/start_processing_services.sh")
    print("\n2. Start the dashboard:")
    print("   poetry run streamlit run src/presentation/streamlit/app.py")
    print("\n3. The dashboard will automatically detect and use the API")
    print("4. Look for '🚀 Using Processing Services API' in the footer")
    print("\n5. Benefits you should notice:")
    print("   - Faster page loads")
    print("   - No loading spinners for calculations")
    print("   - Real-time data from processed results")
    print("   - ML predictions available")


if __name__ == "__main__":
    if test_api_endpoints():
        test_dashboard_with_api()
    else:
        print("\n⚠️  Please start the processing services first:")
        print("   ./scripts/start_processing_services.sh")
