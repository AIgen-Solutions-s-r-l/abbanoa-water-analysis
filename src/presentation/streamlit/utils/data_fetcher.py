"""
Data fetcher utility for retrieving forecast and historical data.

This module handles all data retrieval operations, including integration
with the ForecastConsumption use case and BigQuery for historical data.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import requests
import streamlit as st
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class DataFetcher:
    """Utility class for fetching forecast and historical data."""

    def __init__(self, api_base_url: str = None):
        """Initialize the data fetcher.
        
        Args:
            api_base_url: Base URL for the API (defaults to env var or localhost)
        """
        # Use environment variable, parameter, or default
        self.api_base_url = api_base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    @st.cache_data
    def get_forecast(
        _self, district_id: str, metric: str, horizon: int = 7
    ) -> pd.DataFrame:
        """Fetch forecast data for a specific district and metric.

        Args:
            district_id: District identifier
            metric: Metric to forecast (flow_rate, pressure, consumption)
            horizon: Forecast horizon in days

        Returns:
            DataFrame with forecast data
        """
        try:
            # Call the forecast API endpoint
            url = f"{_self.api_base_url}/api/v1/forecasts/{district_id}/{metric}"
            params = {
                "horizon": horizon,
                "include_historical": False,  # We'll fetch historical separately
                "historical_days": 0
            }
            
            logger.info(f"Fetching forecast from API: {url}")
            response = _self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Convert forecast data to DataFrame
                if data.get("forecast_data"):
                    df = pd.DataFrame(data["forecast_data"])
                    
                    # Rename columns to match expected format
                    df = df.rename(columns={
                        "value": "predicted",
                        "timestamp": "timestamp"
                    })
                    
                    # Ensure timestamp is datetime
                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                    
                    # Add district and metric columns
                    df["district_id"] = district_id
                    df["metric"] = metric
                    
                    logger.info(f"Successfully fetched {len(df)} forecast records")
                    return df
                else:
                    logger.warning("No forecast data in response")
                    
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                
        except RequestException as e:
            logger.error(f"Network error fetching forecast: {str(e)}")
            # Provide helpful error message for common issues
            if "Connection refused" in str(e) or "Failed to establish a new connection" in str(e):
                logger.error("API server is not running. Please start it with: ./run_api.sh")
        except Exception as e:
            logger.error(f"Error processing forecast data: {str(e)}")
        
        # Return empty dataframe on error
        return pd.DataFrame(
            {
                "timestamp": [],
                "predicted": [],
                "lower_bound": [],
                "upper_bound": [],
                "metric": [],
                "district_id": [],
            }
        )

    @st.cache_data
    def get_historical_data(
        _self, district_id: str, metric: str, days_back: int = 30
    ) -> pd.DataFrame:
        """Fetch historical data for a specific district and metric.

        Args:
            district_id: District identifier
            metric: Metric type
            days_back: Number of days of historical data

        Returns:
            DataFrame with historical data
        """
        try:
            # Call the forecast API with historical data included
            url = f"{_self.api_base_url}/api/v1/forecasts/{district_id}/{metric}"
            params = {
                "horizon": 1,  # Minimal forecast
                "include_historical": True,
                "historical_days": days_back
            }
            
            logger.info(f"Fetching historical data from API: {url}")
            response = _self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract historical data
                if data.get("historical_data"):
                    df = pd.DataFrame(data["historical_data"])
                    
                    # Ensure timestamp is datetime
                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                    
                    # Add district and metric columns if not present
                    if "district_id" not in df.columns:
                        df["district_id"] = district_id
                    if "metric" not in df.columns:
                        df["metric"] = metric
                    
                    logger.info(f"Successfully fetched {len(df)} historical records")
                    return df
                else:
                    logger.warning("No historical data in response")
                    
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                
        except RequestException as e:
            logger.error(f"Network error fetching historical data: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing historical data: {str(e)}")
        
        # Return empty dataframe on error
        return pd.DataFrame(
            {"timestamp": [], "value": [], "metric": [], "district_id": []}
        )

    def get_district_summary(_self, district_id: str) -> Dict[str, Any]:
        """Fetch summary statistics for a district.

        Args:
            district_id: District identifier

        Returns:
            Dictionary with summary statistics
        """
        # Return zeros - no synthetic data
        return {
            "avg_daily_consumption": 0,
            "peak_flow_rate": 0,
            "min_pressure": 0,
            "avg_pressure": 0,
            "total_nodes": 0,
            "active_alerts": 0,
            "last_update": None,
            "data_completeness": 0,
        }

    def get_system_metrics(_self) -> Dict[str, Any]:
        """Fetch system performance metrics.

        Returns:
            Dictionary with system metrics
        """
        return {
            "api_latency_ms": 0,
            "cache_hit_rate": 0,
            "model_accuracy_mape": 0,
            "last_model_update": None,
        }

    @st.cache_data(ttl=30)  # 30-second cache for efficiency summary
    def get_efficiency_summary(
        _self, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get network efficiency summary with 30-second cache.
        
        Args:
            start_time: Start time for efficiency calculation
            end_time: End time for efficiency calculation
            
        Returns:
            Dictionary with efficiency metrics including:
            - efficiency_percentage: Overall network efficiency
            - loss_percentage: Water loss percentage
            - avg_pressure: Average network pressure
            - reservoir_level: Reservoir level percentage
            - total_input_volume: Total water input
            - total_output_volume: Total water output
            - active_nodes: Number of active monitoring nodes
        """
        try:
            # Use API client with appropriate endpoint
            endpoint = "/api/v1/network/efficiency"
            params = {}
            
            if start_time:
                params["start_time"] = start_time.isoformat()
            if end_time:
                params["end_time"] = end_time.isoformat()
                
            response = _self.session.get(
                f"{_self.api_base_url}{endpoint}",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                efficiency_data = response.json()
                
                # Calculate derived metrics
                efficiency_percentage = efficiency_data.get('efficiency_percentage', 95.0)
                loss_percentage = 100.0 - efficiency_percentage
                avg_pressure = efficiency_data.get('avg_pressure', 2.5)  # Default pressure in mH2O
                reservoir_level = efficiency_data.get('reservoir_level', 75.0)  # Default percentage
                
                return {
                    "efficiency_percentage": efficiency_percentage,
                    "loss_percentage": loss_percentage,
                    "loss_m3_per_hour": efficiency_data.get('total_loss_volume', 0) / 24,  # Convert to hourly
                    "avg_pressure_mh2o": avg_pressure,
                    "reservoir_level_percentage": reservoir_level,
                    "total_input_volume": efficiency_data.get('total_input_volume', 0),
                    "total_output_volume": efficiency_data.get('total_output_volume', 0),
                    "active_nodes": efficiency_data.get('active_nodes', 0),
                    "total_nodes": efficiency_data.get('total_nodes', 8),
                    "last_updated": datetime.now().isoformat()
                }
            else:
                logger.warning(f"API request failed with status {response.status_code}")
                return _self._get_mock_efficiency_summary()
                
        except RequestException as e:
            logger.error(f"Error fetching efficiency summary: {e}")
            return _self._get_mock_efficiency_summary()
    
    @st.cache_data(ttl=60)  # 1-minute cache for trend data
    def get_efficiency_trends(
        _self,
        hours_back: int = 24,
        district_filter: Optional[str] = None,
        node_filter: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get efficiency trend data for charting.
        
        Args:
            hours_back: Number of hours of historical data to fetch
            district_filter: Optional district filter
            node_filter: Optional node filter
            
        Returns:
            DataFrame with columns: timestamp, efficiency_percentage, loss_percentage, 
            pressure_mh2o, reservoir_level_percentage
        """
        try:
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            
            endpoint = "/api/v1/network/efficiency/trends"
            params = {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "interval": "1hour"
            }
            
            if district_filter:
                params["district"] = district_filter
            if node_filter:
                params["node"] = node_filter
                
            response = _self.session.get(
                f"{_self.api_base_url}{endpoint}",
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                trend_data = response.json()
                
                if trend_data:
                    df = pd.DataFrame(trend_data)
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    # Add target efficiency line (95% target)
                    df['target_efficiency'] = 95.0
                    return df
                else:
                    return _self._get_mock_efficiency_trends(hours_back)
            else:
                logger.warning(f"Trends API request failed with status {response.status_code}")
                return _self._get_mock_efficiency_trends(hours_back)
                
        except RequestException as e:
            logger.error(f"Error fetching efficiency trends: {e}")
            return _self._get_mock_efficiency_trends(hours_back)
    
    def _get_mock_efficiency_summary(self) -> Dict[str, Any]:
        """Generate mock efficiency summary data for development/fallback."""
        return {
            "efficiency_percentage": 94.2,
            "loss_percentage": 5.8,
            "loss_m3_per_hour": 12.5,
            "avg_pressure_mh2o": 2.8,
            "reservoir_level_percentage": 78.3,
            "total_input_volume": 5200.0,
            "total_output_volume": 4896.4,
            "active_nodes": 6,
            "total_nodes": 8,
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_mock_efficiency_trends(self, hours_back: int) -> pd.DataFrame:
        """Generate mock efficiency trend data for development/fallback."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        # Generate hourly timestamps
        timestamps = pd.date_range(start=start_time, end=end_time, freq='1H')
        
        # Generate realistic efficiency trends with some variation
        np.random.seed(42)  # For reproducible data
        base_efficiency = 94.0
        efficiency_trend = base_efficiency + np.random.normal(0, 1.5, len(timestamps))
        efficiency_trend = np.clip(efficiency_trend, 88.0, 98.0)  # Realistic bounds
        
        # Create complementary data
        loss_trend = 100.0 - efficiency_trend
        pressure_trend = 2.8 + np.random.normal(0, 0.3, len(timestamps))
        pressure_trend = np.clip(pressure_trend, 2.0, 4.0)  # Realistic pressure range
        
        reservoir_trend = 78.0 + np.random.normal(0, 5.0, len(timestamps))
        reservoir_trend = np.clip(reservoir_trend, 60.0, 95.0)  # Realistic reservoir levels
        
        return pd.DataFrame({
            'timestamp': timestamps,
            'efficiency_percentage': efficiency_trend,
            'loss_percentage': loss_trend,
            'pressure_mh2o': pressure_trend,
            'reservoir_level_percentage': reservoir_trend,
            'target_efficiency': [95.0] * len(timestamps)  # 95% target line
        })
