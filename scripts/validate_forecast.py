#!/usr/bin/env python3
"""Validation script for forecast functionality."""

import asyncio
import json
import time
from datetime import datetime

import pandas as pd
import requests


class ForecastValidator:
    """Validates the forecast functionality end-to-end."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """Initialize validator."""
        self.api_base_url = api_base_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {}
        }
    
    def test_api_health(self) -> bool:
        """Test if API is healthy."""
        print("🔍 Testing API health...")
        try:
            response = requests.get(f"{self.api_base_url}/")
            if response.status_code == 200:
                print("✅ API is healthy")
                return True
            else:
                print(f"❌ API returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            return False
    
    def test_forecast_endpoint(self, district_id: str, metric: str, horizon: int = 7) -> dict:
        """Test forecast endpoint."""
        print(f"\n🔍 Testing forecast for {district_id}/{metric}...")
        
        test_result = {
            "test": f"forecast_{district_id}_{metric}",
            "status": "failed",
            "details": {}
        }
        
        try:
            start_time = time.time()
            
            # Call forecast endpoint
            url = f"{self.api_base_url}/api/v1/forecasts/{district_id}/{metric}"
            params = {
                "horizon": horizon,
                "include_historical": True,
                "historical_days": 30
            }
            
            response = requests.get(url, params=params, timeout=30)
            duration_ms = (time.time() - start_time) * 1000
            
            test_result["details"]["duration_ms"] = duration_ms
            test_result["details"]["status_code"] = response.status_code
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["district_id", "metric", "horizon", "forecast_data", "metadata"]
                missing_fields = [f for f in required_fields if f not in data]
                
                if missing_fields:
                    test_result["details"]["error"] = f"Missing fields: {missing_fields}"
                    print(f"❌ Response missing fields: {missing_fields}")
                else:
                    # Validate forecast data
                    forecast_count = len(data.get("forecast_data", []))
                    historical_count = len(data.get("historical_data", [])) if data.get("historical_data") else 0
                    
                    test_result["details"]["forecast_points"] = forecast_count
                    test_result["details"]["historical_points"] = historical_count
                    
                    if forecast_count == horizon:
                        test_result["status"] = "passed"
                        print(f"✅ Forecast successful: {forecast_count} points, {duration_ms:.0f}ms")
                        
                        # Check data quality
                        if forecast_count > 0:
                            first_point = data["forecast_data"][0]
                            test_result["details"]["sample_value"] = first_point.get("value")
                            test_result["details"]["has_confidence_intervals"] = all(
                                k in first_point for k in ["lower_bound", "upper_bound"]
                            )
                    else:
                        test_result["details"]["error"] = f"Expected {horizon} points, got {forecast_count}"
                        print(f"❌ Wrong number of forecast points: {forecast_count}")
            else:
                error_data = response.json() if response.headers.get("content-type") == "application/json" else {}
                test_result["details"]["error"] = error_data.get("detail", response.text)
                print(f"❌ API error: {response.status_code} - {test_result['details']['error']}")
                
        except requests.Timeout:
            test_result["details"]["error"] = "Request timeout"
            print("❌ Request timed out")
        except Exception as e:
            test_result["details"]["error"] = str(e)
            print(f"❌ Error: {e}")
        
        self.results["tests"].append(test_result)
        return test_result
    
    def test_invalid_inputs(self):
        """Test error handling with invalid inputs."""
        print("\n🔍 Testing error handling...")
        
        # Test invalid district
        test_result = {
            "test": "invalid_district",
            "status": "failed",
            "details": {}
        }
        
        try:
            response = requests.get(
                f"{self.api_base_url}/api/v1/forecasts/INVALID/flow_rate",
                timeout=10
            )
            
            if response.status_code == 400:
                test_result["status"] = "passed"
                print("✅ Invalid district correctly rejected")
            else:
                test_result["details"]["error"] = f"Expected 400, got {response.status_code}"
                print(f"❌ Wrong status code: {response.status_code}")
                
        except Exception as e:
            test_result["details"]["error"] = str(e)
            print(f"❌ Error: {e}")
        
        self.results["tests"].append(test_result)
    
    def test_model_status(self):
        """Test model status endpoint."""
        print("\n🔍 Testing model status...")
        
        test_result = {
            "test": "model_status",
            "status": "failed",
            "details": {}
        }
        
        try:
            response = requests.get(
                f"{self.api_base_url}/api/v1/forecasts/models/status",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                model_count = data.get("total_models", 0)
                active_count = data.get("active_models", 0)
                
                test_result["details"]["total_models"] = model_count
                test_result["details"]["active_models"] = active_count
                
                if model_count > 0:
                    test_result["status"] = "passed"
                    print(f"✅ Model status: {active_count}/{model_count} active")
                else:
                    print("❌ No models found")
            else:
                test_result["details"]["error"] = f"Status code: {response.status_code}"
                print(f"❌ Failed to get model status: {response.status_code}")
                
        except Exception as e:
            test_result["details"]["error"] = str(e)
            print(f"❌ Error: {e}")
        
        self.results["tests"].append(test_result)
    
    def test_performance(self):
        """Test forecast performance."""
        print("\n🔍 Testing performance...")
        
        districts = ["DIST_001", "DIST_002"]
        metrics = ["flow_rate", "pressure"]
        
        latencies = []
        
        for district in districts:
            for metric in metrics:
                try:
                    start_time = time.time()
                    response = requests.get(
                        f"{self.api_base_url}/api/v1/forecasts/{district}/{metric}",
                        params={"horizon": 7, "include_historical": False},
                        timeout=10
                    )
                    latency_ms = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        latencies.append(latency_ms)
                        
                except:
                    pass
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            
            test_result = {
                "test": "performance",
                "status": "passed" if avg_latency < 1000 else "warning",
                "details": {
                    "avg_latency_ms": avg_latency,
                    "max_latency_ms": max_latency,
                    "requests_tested": len(latencies)
                }
            }
            
            print(f"✅ Performance: avg={avg_latency:.0f}ms, max={max_latency:.0f}ms")
        else:
            test_result = {
                "test": "performance",
                "status": "failed",
                "details": {"error": "No successful requests"}
            }
            print("❌ No successful performance measurements")
        
        self.results["tests"].append(test_result)
    
    def run_all_tests(self):
        """Run all validation tests."""
        print("🚀 Starting Forecast Validation")
        print("=" * 50)
        
        # Check API health first
        if not self.test_api_health():
            print("\n⚠️  API is not accessible. Please start the API server first.")
            return
        
        # Test valid forecasts
        test_cases = [
            ("DIST_001", "flow_rate"),
            ("DIST_001", "pressure"),
            ("DIST_002", "flow_rate"),
            ("DIST_002", "pressure"),
        ]
        
        for district, metric in test_cases:
            self.test_forecast_endpoint(district, metric)
        
        # Test error handling
        self.test_invalid_inputs()
        
        # Test model status
        self.test_model_status()
        
        # Test performance
        self.test_performance()
        
        # Generate summary
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for t in self.results["tests"] if t["status"] == "passed")
        failed_tests = sum(1 for t in self.results["tests"] if t["status"] == "failed")
        
        self.results["summary"] = {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Validation Summary")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {self.results['summary']['success_rate']:.1f}%")
        
        # Save results
        with open("forecast_validation_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print("\n💾 Results saved to forecast_validation_results.json")
        
        return self.results["summary"]["success_rate"] >= 80


if __name__ == "__main__":
    import sys
    
    # Get API URL from command line or use default
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    validator = ForecastValidator(api_url)
    success = validator.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)