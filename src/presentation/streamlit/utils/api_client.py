"""
API Client for connecting to the Processing Services API.

This client handles all communication with the REST API,
eliminating the need for direct database queries or calculations
in the dashboard.
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import streamlit as st
import pandas as pd


class APIClient:
    """Client for interacting with the Processing Services API."""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for the API (defaults to environment variable or localhost)
        """
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        
        # Configure retries
        retry = Retry(
            total=3,
            read=3,
            connect=3,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 504)
        )
        
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default timeout
        session.timeout = 30
        
        return session
        
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Any:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to API server. Please ensure the processing services are running.")
            return None
        except requests.exceptions.Timeout:
            st.error("API request timed out. The server might be overloaded.")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            st.error(f"API error: {e}")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            return None
            
    @st.cache_data(ttl=60)  # Cache for 1 minute
    def get_nodes(self) -> List[Dict[str, Any]]:
        """Get list of all active nodes."""
        result = self._make_request("GET", "/api/v1/nodes")
        return result or []
        
    @st.cache_data(ttl=30)  # Cache for 30 seconds
    def get_node_metrics(self, node_id: str, time_window: str = "1hour") -> Optional[Dict[str, Any]]:
        """Get latest metrics for a specific node."""
        result = self._make_request(
            "GET", 
            f"/api/v1/nodes/{node_id}/metrics",
            params={"time_window": time_window}
        )
        return result
        
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_node_history(
        self, 
        node_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        time_window: str = "1hour"
    ) -> pd.DataFrame:
        """Get historical metrics for a node."""
        params = {"time_window": time_window}
        
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()
            
        result = self._make_request(
            "GET",
            f"/api/v1/nodes/{node_id}/history",
            params=params
        )
        
        if result:
            df = pd.DataFrame(result)
            if not df.empty:
                df['window_start'] = pd.to_datetime(df['window_start'])
                df['window_end'] = pd.to_datetime(df['window_end'])
            return df
        return pd.DataFrame()
        
    @st.cache_data(ttl=60)
    def get_network_metrics(self, time_range: str = "24h") -> Optional[Dict[str, Any]]:
        """Get network-wide metrics."""
        result = self._make_request(
            "GET",
            "/api/v1/network/metrics",
            params={"time_range": time_range}
        )
        return result
        
    @st.cache_data(ttl=300)
    def get_network_efficiency(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """Get network efficiency metrics."""
        params = {}
        
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()
            
        result = self._make_request(
            "GET",
            "/api/v1/network/efficiency",
            params=params
        )
        return result
        
    @st.cache_data(ttl=60)
    def get_predictions(
        self,
        node_id: str,
        model_type: str = "flow_prediction",
        horizon_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get ML predictions for a node."""
        result = self._make_request(
            "GET",
            f"/api/v1/predictions/{node_id}",
            params={
                "model_type": model_type,
                "horizon_hours": horizon_hours
            }
        )
        return result or []
        
    @st.cache_data(ttl=300)
    def get_anomalies(
        self,
        hours: int = 24,
        node_id: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent anomalies."""
        params = {"hours": hours}
        
        if node_id:
            params["node_id"] = node_id
        if severity:
            params["severity"] = severity
            
        result = self._make_request(
            "GET",
            "/api/v1/anomalies",
            params=params
        )
        return result or []
        
    @st.cache_data(ttl=60)
    def get_data_quality(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get data quality metrics for a node."""
        result = self._make_request(
            "GET",
            f"/api/v1/quality/{node_id}"
        )
        return result
        
    @st.cache_data(ttl=30)
    def get_system_status(self) -> Optional[Dict[str, Any]]:
        """Get overall system status."""
        result = self._make_request("GET", "/api/v1/status")
        return result
        
    @st.cache_data(ttl=10)  # Short cache for dashboard
    def get_dashboard_summary(self) -> Optional[Dict[str, Any]]:
        """Get summary data for dashboard display."""
        result = self._make_request("GET", "/api/v1/dashboard/summary")
        return result
        
    def health_check(self) -> bool:
        """Check if API is healthy."""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
            
            
# Singleton instance
_api_client: Optional[APIClient] = None


def get_api_client() -> APIClient:
    """Get or create API client singleton."""
    global _api_client
    if _api_client is None:
        _api_client = APIClient()
    return _api_client