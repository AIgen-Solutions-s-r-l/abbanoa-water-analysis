#!/usr/bin/env python3
"""Test the infrastructure API endpoint."""

import requests
import json
import sys

def test_infrastructure_endpoint():
    """Test the infrastructure map data endpoint."""
    base_url = "http://localhost:8000"
    
    # Test infrastructure endpoint
    print("Testing infrastructure map-data endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/infrastructure/map-data")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Infrastructure endpoint is working!")
            print(f"Network Health: {data.get('network_health', 'N/A')}%")
            print(f"Total Flow: {data.get('total_flow', 'N/A')} L/s")
            print(f"Avg Pressure: {data.get('avg_pressure', 'N/A')} bar")
            print(f"Active Alerts: {data.get('active_alerts', 'N/A')}")
            print(f"Number of nodes: {len(data.get('nodes', []))}")
            print(f"Number of zones: {len(data.get('zones', []))}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False
    
    # Test network summary endpoint
    print("\nTesting network summary endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/infrastructure/network-summary")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Network summary endpoint is working!")
            network = data.get('network', {})
            print(f"Total Nodes: {network.get('total_nodes', 'N/A')}")
            print(f"Active Nodes: {network.get('active_nodes', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_infrastructure_endpoint()
    sys.exit(0 if success else 1)