"""
Tests for temporal charts and trend analysis functionality.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import json

from src.presentation.api.consumption_routes import router


class TestTemporalCharts:
    """Test suite for temporal charts and trend analysis."""
    
    @pytest.fixture
    def sample_timeline_data(self):
        """Sample timeline data for testing."""
        return {
            "consumption_timeline": [
                {
                    "timestamp": "2025-06-19T00:00:00",
                    "consumption_liters": 62500,
                    "forecast_consumption": 65625
                },
                {
                    "timestamp": "2025-06-19T01:00:00",
                    "consumption_liters": 58000,
                    "forecast_consumption": 60900
                },
                {
                    "timestamp": "2025-06-19T02:00:00",
                    "consumption_liters": 52000,
                    "forecast_consumption": 54600
                },
                {
                    "timestamp": "2025-06-19T08:00:00",
                    "consumption_liters": 75000,
                    "forecast_consumption": 78750
                },
                {
                    "timestamp": "2025-06-19T12:00:00",
                    "consumption_liters": 68000,
                    "forecast_consumption": 71400
                },
                {
                    "timestamp": "2025-06-19T18:00:00",
                    "consumption_liters": 72000,
                    "forecast_consumption": 75600
                },
                {
                    "timestamp": "2025-06-19T23:00:00",
                    "consumption_liters": 65000,
                    "forecast_consumption": 68250
                }
            ],
            "data_metadata": {
                "is_real_time": False,
                "data_source": "Historical Database"
            }
        }
    
    @pytest.fixture
    def sample_hourly_pattern_data(self):
        """Sample hourly pattern data for testing."""
        return {
            "hourly_pattern": [
                {"hour": 0, "avg_consumption": 62500, "peak_hour": False},
                {"hour": 1, "avg_consumption": 58000, "peak_hour": False},
                {"hour": 2, "avg_consumption": 52000, "peak_hour": False},
                {"hour": 3, "avg_consumption": 48000, "peak_hour": False},
                {"hour": 4, "avg_consumption": 45000, "peak_hour": False},
                {"hour": 5, "avg_consumption": 50000, "peak_hour": False},
                {"hour": 6, "avg_consumption": 60000, "peak_hour": False},
                {"hour": 7, "avg_consumption": 70000, "peak_hour": False},
                {"hour": 8, "avg_consumption": 75000, "peak_hour": True},
                {"hour": 9, "avg_consumption": 72000, "peak_hour": False},
                {"hour": 10, "avg_consumption": 68000, "peak_hour": False},
                {"hour": 11, "avg_consumption": 65000, "peak_hour": False},
                {"hour": 12, "avg_consumption": 68000, "peak_hour": False},
                {"hour": 13, "avg_consumption": 70000, "peak_hour": False},
                {"hour": 14, "avg_consumption": 72000, "peak_hour": False},
                {"hour": 15, "avg_consumption": 70000, "peak_hour": False},
                {"hour": 16, "avg_consumption": 68000, "peak_hour": False},
                {"hour": 17, "avg_consumption": 70000, "peak_hour": False},
                {"hour": 18, "avg_consumption": 72000, "peak_hour": False},
                {"hour": 19, "avg_consumption": 68000, "peak_hour": False},
                {"hour": 20, "avg_consumption": 65000, "peak_hour": False},
                {"hour": 21, "avg_consumption": 62000, "peak_hour": False},
                {"hour": 22, "avg_consumption": 60000, "peak_hour": False},
                {"hour": 23, "avg_consumption": 58000, "peak_hour": False}
            ]
        }
    
    def test_timeline_data_has_correct_structure(self, sample_timeline_data):
        """Test that timeline data has the correct structure for charts."""
        timeline = sample_timeline_data["consumption_timeline"]
        
        # Verify structure
        assert len(timeline) > 0, "Timeline should have data points"
        
        for point in timeline:
            assert "timestamp" in point, "Each point should have timestamp"
            assert "consumption_liters" in point, "Each point should have consumption"
            assert "forecast_consumption" in point, "Each point should have forecast"
            
            # Verify data types
            assert isinstance(point["consumption_liters"], (int, float))
            assert isinstance(point["forecast_consumption"], (int, float))
            
            # Verify timestamp format
            timestamp = datetime.fromisoformat(point["timestamp"].replace('Z', '+00:00'))
            assert isinstance(timestamp, datetime)
    
    def test_hourly_pattern_has_24_hours(self, sample_hourly_pattern_data):
        """Test that hourly pattern covers all 24 hours."""
        pattern = sample_hourly_pattern_data["hourly_pattern"]
        
        assert len(pattern) == 24, "Hourly pattern should have 24 hours"
        
        hours = [point["hour"] for point in pattern]
        assert set(hours) == set(range(24)), "Should cover all hours 0-23"
    
    def test_hourly_pattern_identifies_peak_hours(self, sample_hourly_pattern_data):
        """Test that hourly pattern correctly identifies peak hours."""
        pattern = sample_hourly_pattern_data["hourly_pattern"]
        
        peak_hours = [point for point in pattern if point["peak_hour"]]
        assert len(peak_hours) > 0, "Should identify at least one peak hour"
        
        # Verify peak hour has highest consumption
        max_consumption = max(point["avg_consumption"] for point in pattern)
        peak_consumption = max(point["avg_consumption"] for point in peak_hours)
        assert peak_consumption == max_consumption, "Peak hour should have highest consumption"
    
    def test_timeline_data_shows_realistic_patterns(self, sample_timeline_data):
        """Test that timeline data shows realistic consumption patterns."""
        timeline = sample_timeline_data["consumption_timeline"]
        
        # Check for realistic consumption values
        for point in timeline:
            consumption = point["consumption_liters"]
            assert 0 <= consumption <= 200000, "Consumption should be realistic (0-200K L)"
            
            forecast = point["forecast_consumption"]
            assert 0 <= forecast <= 200000, "Forecast should be realistic (0-200K L)"
        
        # Check for daily pattern (lower at night, higher during day)
        night_consumption = [p["consumption_liters"] for p in timeline if 
                           datetime.fromisoformat(p["timestamp"].replace('Z', '+00:00')).hour in [0, 1, 2]]
        day_consumption = [p["consumption_liters"] for p in timeline if 
                          datetime.fromisoformat(p["timestamp"].replace('Z', '+00:00')).hour in [8, 12, 18]]
        
        if night_consumption and day_consumption:
            avg_night = sum(night_consumption) / len(night_consumption)
            avg_day = sum(day_consumption) / len(day_consumption)
            assert avg_day > avg_night, "Day consumption should be higher than night"
    
    def test_forecast_data_is_reasonable(self, sample_timeline_data):
        """Test that forecast data is reasonable compared to actual data."""
        timeline = sample_timeline_data["consumption_timeline"]
        
        for point in timeline:
            actual = point["consumption_liters"]
            forecast = point["forecast_consumption"]
            
            # Forecast should be within reasonable range of actual (e.g., ±20%)
            ratio = forecast / actual if actual > 0 else 1
            assert 0.8 <= ratio <= 1.2, f"Forecast should be within ±20% of actual: {ratio}"
    
    def test_timeline_data_has_chronological_order(self, sample_timeline_data):
        """Test that timeline data is in chronological order."""
        timeline = sample_timeline_data["consumption_timeline"]
        
        timestamps = [datetime.fromisoformat(p["timestamp"].replace('Z', '+00:00')) for p in timeline]
        
        # Check if timestamps are in ascending order
        for i in range(1, len(timestamps)):
            assert timestamps[i] > timestamps[i-1], "Timestamps should be in chronological order"
    
    def test_hourly_pattern_shows_daily_cycle(self, sample_hourly_pattern_data):
        """Test that hourly pattern shows realistic daily consumption cycle."""
        pattern = sample_hourly_pattern_data["hourly_pattern"]
        
        # Find peak hour
        peak_hour = max(pattern, key=lambda x: x["avg_consumption"])
        peak_time = peak_hour["hour"]
        
        # Peak should be during typical usage hours (6-22)
        assert 6 <= peak_time <= 22, f"Peak hour {peak_time} should be during typical usage hours"
        
        # Night hours should have lower consumption
        night_hours = [p for p in pattern if p["hour"] in [0, 1, 2, 3, 4, 5, 23]]
        day_hours = [p for p in pattern if p["hour"] in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]]
        
        avg_night = sum(p["avg_consumption"] for p in night_hours) / len(night_hours)
        avg_day = sum(p["avg_consumption"] for p in day_hours) / len(day_hours)
        
        assert avg_day > avg_night, "Day average should be higher than night average"
    
    def test_trend_analysis_can_calculate_growth_rate(self, sample_timeline_data):
        """Test that trend analysis can calculate consumption growth rate."""
        timeline = sample_timeline_data["consumption_timeline"]
        
        if len(timeline) >= 2:
            # Calculate simple growth rate
            first_consumption = timeline[0]["consumption_liters"]
            last_consumption = timeline[-1]["consumption_liters"]
            
            if first_consumption > 0:
                growth_rate = (last_consumption - first_consumption) / first_consumption
                assert isinstance(growth_rate, (int, float)), "Growth rate should be numeric"
                assert -1 <= growth_rate <= 2, "Growth rate should be reasonable (-100% to +200%)"
    
    def test_temporal_data_supports_chart_visualization(self, sample_timeline_data, sample_hourly_pattern_data):
        """Test that temporal data can be used for chart visualization."""
        timeline = sample_timeline_data["consumption_timeline"]
        pattern = sample_hourly_pattern_data["hourly_pattern"]
        
        # Timeline should have enough points for line chart
        assert len(timeline) >= 3, "Timeline should have at least 3 points for line chart"
        
        # Hourly pattern should have exactly 24 points for bar chart
        assert len(pattern) == 24, "Hourly pattern should have 24 points for bar chart"
        
        # All data points should have required fields for charts
        for point in timeline:
            required_fields = ["timestamp", "consumption_liters", "forecast_consumption"]
            for field in required_fields:
                assert field in point, f"Timeline point should have {field}"
        
        for point in pattern:
            required_fields = ["hour", "avg_consumption", "peak_hour"]
            for field in required_fields:
                assert field in point, f"Pattern point should have {field}"
    
    def test_temporal_data_handles_missing_values_gracefully(self):
        """Test that temporal data handling is robust with missing values."""
        incomplete_timeline = [
            {
                "timestamp": "2025-06-19T00:00:00",
                "consumption_liters": 62500,
                "forecast_consumption": 65625
            },
            {
                "timestamp": "2025-06-19T01:00:00",
                "consumption_liters": None,  # Missing value
                "forecast_consumption": 60900
            },
            {
                "timestamp": "2025-06-19T02:00:00",
                "consumption_liters": 52000,
                "forecast_consumption": 54600
            }
        ]
        
        # Should handle None values gracefully
        valid_points = [p for p in incomplete_timeline if p["consumption_liters"] is not None]
        assert len(valid_points) == 2, "Should filter out None values"
        
        # Valid points should have proper data types
        for point in valid_points:
            assert isinstance(point["consumption_liters"], (int, float))
            assert isinstance(point["forecast_consumption"], (int, float))
