"""Integration tests for pressure zones endpoint."""

import os
import httpx


API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")


def test_pressure_zones_returns_200_and_valid_structure():
    """Test that pressure zones endpoint returns proper structure."""
    url = f"{API_BASE}/pressure/zones"
    resp = httpx.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    data = resp.json()
    assert "zones" in data, "Response must contain 'zones' key"
    assert isinstance(data["zones"], list), "zones must be a list"
    
    # If zones exist, validate structure
    if data["zones"]:
        zone = data["zones"][0]
        required_fields = [
            "zone",
            "zoneName", 
            "minPressure",
            "avgPressure",
            "maxPressure",
            "nodeCount",
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
        assert isinstance(zone["status"], str)


def test_pressure_zones_mock_mode():
    """Test that mock mode returns expected data structure."""
    # This test will pass when USE_MOCK_API=true
    if os.getenv("USE_MOCK_API", "").lower() == "true":
        url = f"{API_BASE}/pressure/zones"
        resp = httpx.get(url, timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        
        # Mock should return at least one zone for testing
        assert len(data["zones"]) >= 1, "Mock mode should return at least one zone"
        
        # Verify mock data has realistic values
        zone = data["zones"][0]
        assert zone["minPressure"] <= zone["avgPressure"] <= zone["maxPressure"]
        assert zone["nodeCount"] > 0
        assert zone["status"] in ["normal", "warning", "critical"]