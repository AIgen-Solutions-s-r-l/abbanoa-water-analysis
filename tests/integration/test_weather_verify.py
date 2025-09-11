"""Verify weather transparency implementation."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import requests
import subprocess
import time
import signal

def test_weather_transparency():
    """Test that weather API includes transparency fields."""
    
    # Start the weather server
    server_process = subprocess.Popen(
        ["python3", "src/servers/weather_server_prod.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONPATH": "/root/abbanoa-water-analysis"}
    )
    
    # Give server time to start
    time.sleep(2)
    
    try:
        # Test current weather endpoint
        response = requests.get("http://localhost:8002/weather/current")
        assert response.status_code == 200
        
        data = response.json()
        print(f"✓ Got {len(data)} weather locations")
        
        # Check data_source field
        for location_data in data:
            assert "data_source" in location_data, f"Missing data_source in {location_data.get('location')}"
            assert location_data["data_source"] in ["real", "estimated"]
            print(f"  ✓ {location_data['location']}: data_source = {location_data['data_source']}")
            
            assert "last_real_update" in location_data, f"Missing last_real_update in {location_data.get('location')}"
            print(f"  ✓ {location_data['location']}: last_real_update = {location_data['last_real_update']}")
        
        # Test statistics endpoint
        response = requests.get("http://localhost:8002/weather/statistics")
        assert response.status_code == 200
        
        stats_data = response.json()
        assert "dataQuality" in stats_data
        assert "realDataPercentage" in stats_data["dataQuality"]
        assert "estimatedDataPercentage" in stats_data["dataQuality"]
        print(f"✓ Statistics includes data quality: {stats_data['dataQuality']['realDataPercentage']}% real data")
        
        # Test impact analysis
        response = requests.get("http://localhost:8002/weather/impact-analysis")
        assert response.status_code == 200
        
        impact_data = response.json()
        assert "dataReliability" in impact_data
        assert "reliabilityNote" in impact_data
        print(f"✓ Impact analysis shows reliability: {impact_data['dataReliability']}")
        
        # Test status endpoint
        response = requests.get("http://localhost:8002/weather/status")
        assert response.status_code == 200
        
        status_data = response.json()
        assert "real_data_available" in status_data
        assert "data_source" in status_data
        if not status_data["real_data_available"]:
            assert "fallback_reason" in status_data
        print(f"✓ Status shows data source: {status_data['data_source']}")
        
        print("\n✅ All weather transparency tests PASSED!")
        
    finally:
        # Stop the server
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    test_weather_transparency()