"""Integration tests for weather endpoints following DEV-PROTO.yaml TDD."""

import pytest
import httpx

API_BASE = "http://localhost:8000/api/v1"


def test_weather_current_endpoint_returns_valid_response():
    """Should return current weather data with correct API prefix."""
    url = f"{API_BASE}/weather/current"
    response = httpx.get(url, timeout=10)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Check first weather entry structure
    weather_entry = data[0]
    required_fields = ['location', 'date', 'temperature', 'humidity', 'rainfall', 'windSpeed', 'conditions']
    for field in required_fields:
        assert field in weather_entry


def test_weather_locations_endpoint_returns_valid_response():
    """Should return weather locations with correct API prefix."""
    url = f"{API_BASE}/weather/locations"
    response = httpx.get(url, timeout=10)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_weather_statistics_endpoint_returns_valid_response():
    """Should return weather statistics with correct API prefix."""
    url = f"{API_BASE}/weather/statistics"
    response = httpx.get(url, timeout=10)
    
    assert response.status_code == 200
    data = response.json()
    assert 'overview' in data
    assert 'seasonalPatterns' in data


def test_weather_impact_analysis_endpoint_returns_valid_response():
    """Should return weather impact analysis with correct API prefix."""
    url = f"{API_BASE}/weather/impact-analysis"
    response = httpx.get(url, timeout=10)
    
    assert response.status_code == 200
    data = response.json()
    assert 'temperatureImpact' in data
    assert 'rainfallImpact' in data
    assert 'recommendations' in data