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
