"""Integration tests for pressure zones endpoint."""

import os
import httpx
import pytest


API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")


def test_pressure_zones_returns_proper_structure():
    """Test that pressure zones endpoint returns proper structure."""
    # Make request with USE_MOCK_API=true 
    url = f"{API_BASE}/pressure/zones"
    resp = httpx.get(url, timeout=10)
    
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    data = resp.json()
    assert "zones" in data, "Response must contain 'zones' key"
    assert isinstance(data["zones"], list), "zones must be a list"
    assert len(data["zones"]) > 0, "zones list must not be empty"
    
    # Validate zone structure
    zone = data["zones"][0]
    required_fields = [
        "zone",
        "zoneName", 
        "minPressure",
        "avgPressure",
        "maxPressure",
        "nodeCount",
        "nodesWithData",
        "efficiency",
        "status"
    ]
    for field in required_fields:
        assert field in zone, f"Zone missing required field: {field}"
    
    # Validate field types
    assert isinstance(zone["zone"], str)
    assert isinstance(zone["zoneName"], str)
    assert isinstance(zone["minPressure"], (int, float))
    assert isinstance(zone["avgPressure"], (int, float))
    assert isinstance(zone["maxPressure"], (int, float))
    assert isinstance(zone["nodeCount"], int)
    assert isinstance(zone["nodesWithData"], int)
    assert isinstance(zone["efficiency"], (int, float))
    assert isinstance(zone["status"], str)
    
    # Validate logical constraints
    assert zone["minPressure"] <= zone["avgPressure"] <= zone["maxPressure"]
    assert zone["nodeCount"] >= 0
    assert zone["nodesWithData"] >= 0
    assert zone["nodesWithData"] <= zone["nodeCount"]
    assert 0 <= zone["efficiency"] <= 100
    assert zone["status"] in ["optimal", "normal", "warning", "critical", "unknown"]


def test_pressure_zones_with_mock_data():
    """Test that pressure zones endpoint returns expected mock data."""
    url = f"{API_BASE}/pressure/zones"
    resp = httpx.get(url, timeout=10)
    
    assert resp.status_code == 200
    data = resp.json()
    
    # Verify we get the expected number of zones from mock
    assert len(data["zones"]) == 5
    
    # Check specific mock zone values
    zone_centro = next((z for z in data["zones"] if z["zone"] == "Z01"), None)
    assert zone_centro is not None
    assert zone_centro["zoneName"] == "Zona Centro"
    assert zone_centro["avgPressure"] == 4.5
    assert zone_centro["efficiency"] == 96.5
    assert zone_centro["status"] == "optimal"


def test_pressure_zones_efficiency():
    """Test pressure zones efficiency calculations."""
    url = f"{API_BASE}/pressure/zones"
    resp = httpx.get(url, timeout=10)
    
    assert resp.status_code == 200
    data = resp.json()
    
    for zone in data["zones"]:
        efficiency = zone["efficiency"]
        status = zone["status"]
        avg_pressure = zone["avgPressure"]
        
        # High efficiency zones should have good status
        if efficiency >= 95 and 4.0 <= avg_pressure <= 5.0:
            assert status == "optimal", f"Zone {zone['zone']} should be optimal with efficiency {efficiency}"
        
        # Low pressure should trigger warning
        if avg_pressure < 3.0:
            assert status in ["warning", "critical"], f"Zone {zone['zone']} should have warning/critical status with pressure {avg_pressure}"


