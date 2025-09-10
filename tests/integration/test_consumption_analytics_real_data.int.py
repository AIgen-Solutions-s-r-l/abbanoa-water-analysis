"""Integration tests for consumption analytics with real database data."""

import os
import httpx
import pytest
from datetime import datetime

API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")


def test_consumption_analytics_uses_real_database_data():
    """Test that consumption analytics endpoint returns real database data, not mocks."""
    url = f"{API_BASE}/consumption/analytics"
    resp = httpx.get(url, timeout=10)
    
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    
    data = resp.json()
    
    # Verify structure
    assert "summary" in data
    assert "district_consumption" in data
    assert "consumption_timeline" in data
    assert "data_metadata" in data
    
    summary = data["summary"]
    
    # These values should NOT be the hardcoded mock values
    assert summary["total_daily_consumption"] != 2500000.0, "Should not return mock value 2500000.0"
    assert summary["total_users"] != 47500, "Should not return mock value 47500"
    assert summary["system_efficiency"] != 0.892, "Should not return mock value 0.892"
    
    # Verify data_metadata indicates real data
    metadata = data["data_metadata"]
    assert metadata["data_source"] == "postgresql_sensor_readings", "Should indicate PostgreSQL source"
    assert metadata["synthetic_percentage"] == 0, "Should be 0% synthetic for real data"
    
    # Verify consumption is calculated from actual flow rates
    assert summary["total_daily_consumption"] > 0, "Should have positive consumption from flow data"
    
    # District consumption should be based on real nodes
    districts = data["district_consumption"]
    assert len(districts) > 0, "Should have district data from real nodes"
    
    # Check that district names match actual database zones
    district_names = [d["district_name"] for d in districts]
    expected_zones = ["Cagliari Centro", "Cagliari Nord", "Quartucciu", "Selargius"]
    
    # At least one real zone should be present
    assert any(zone in " ".join(district_names) for zone in expected_zones), \
        f"Should contain real zone names, got: {district_names}"


def test_consumption_timeline_uses_real_timestamps():
    """Test that consumption timeline uses real sensor reading timestamps."""
    url = f"{API_BASE}/consumption/analytics"
    resp = httpx.get(url, timeout=10)
    
    assert resp.status_code == 200
    data = resp.json()
    
    timeline = data["consumption_timeline"]
    assert len(timeline) > 0, "Should have timeline data"
    
    # Verify timestamps are from actual readings, not generated
    for point in timeline:
        timestamp = datetime.fromisoformat(point["timestamp"].replace("Z", "+00:00"))
        # Real data points should have actual historical timestamps
        assert "consumption_liters" in point
        assert point["consumption_liters"] > 0
        
        # Forecast should be None or based on real patterns
        if "forecast_consumption" in point:
            assert point["forecast_consumption"] != 108000.0, "Should not use mock forecast value"


def test_user_segments_calculated_from_flow_patterns():
    """Test that user segments are calculated from real flow patterns."""
    url = f"{API_BASE}/consumption/analytics"
    resp = httpx.get(url, timeout=10)
    
    assert resp.status_code == 200
    data = resp.json()
    
    segments = data["user_segments"]
    assert len(segments) > 0, "Should have user segments"
    
    # Verify segments are not mock values
    for segment in segments:
        assert segment["user_count"] != 42000, "Should not use mock user count"
        assert segment["percentage"] != 88.4, "Should not use mock percentage"
        assert segment["avg_daily_consumption"] != 48.2, "Should not use mock consumption"


def test_peak_demand_from_real_data():
    """Test that peak demand is calculated from real sensor data."""
    url = f"{API_BASE}/consumption/analytics"
    resp = httpx.get(url, timeout=10)
    
    assert resp.status_code == 200
    data = resp.json()
    
    peak = data["peak_demand"]
    
    # Should not return mock values
    assert peak["daily_peak_consumption"] != 165000.0, "Should not use mock peak value"
    assert peak["daily_peak_time"] != "19:30", "Should calculate actual peak time"
    
    # Peak consumption should be realistic based on flow data
    assert peak["daily_peak_consumption"] > 0


def test_conservation_opportunities_based_on_real_analysis():
    """Test that conservation opportunities are based on real data analysis."""
    url = f"{API_BASE}/consumption/analytics"
    resp = httpx.get(url, timeout=10)
    
    assert resp.status_code == 200
    data = resp.json()
    
    opportunities = data["conservation_opportunities"]
    
    # Should provide real opportunities based on actual data patterns
    if len(opportunities) > 0:
        opp = opportunities[0]
        assert opp["potential_savings_liters_daily"] != 125000.0, "Should not use mock savings value"
        assert opp["potential_savings_percentage"] != 5.0, "Should calculate real percentage"