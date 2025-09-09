import os
import httpx
import pytest
from unittest.mock import patch, AsyncMock


API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")


@patch('src.presentation.api.endpoints.dashboard_router.get_db_connection')
def test_dashboard_summary_returns_200_and_valid_shape(mock_get_db_connection):
    # Arrange
    mock_conn = AsyncMock()
    mock_get_db_connection.return_value = mock_conn
    
    # Mock latest timestamp query
    mock_conn.fetchrow.return_value = {'latest_timestamp': None}
    
    # Mock nodes data query
    mock_conn.fetch.return_value = [
        {
            'node_id': 'TEST_NODE_1',
            'node_name': 'Test Node 1', 
            'node_type': 'distribution',
            'flow_rate': 10.5,
            'pressure': 3.2,
            'temperature': 18.5,
            'last_reading': None,
            'quality_score': 0.95
        }
    ]
    
    url = f"{API_BASE}/dashboard/summary"

    # Act
    resp = httpx.get(url, timeout=10)

    # Assert
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "nodes" in data
    assert "network" in data
    assert "last_updated" in data
    assert isinstance(data["nodes"], list)
    assert set(["active_nodes", "total_flow_lps", "average_pressure_bar", "total_volume_m3", "anomaly_count"]) <= set(data["network"].keys())


@patch('src.presentation.api.endpoints.anomaly_router.get_db_connection')
def test_anomalies_returns_200_and_list(mock_get_db_connection):
    # Arrange
    mock_conn = AsyncMock()
    mock_get_db_connection.return_value = mock_conn
    
    # Mock anomalies query response
    mock_conn.fetch.return_value = [
        {
            'anomaly_id': 'TEST_ANOM_1',
            'node_id': 'TEST_NODE_1',
            'timestamp': '2025-09-09T10:00:00Z',
            'anomaly_type': 'pressure_drop',
            'severity': 'medium',
            'description': 'Test pressure anomaly',
            'resolved_at': None
        }
    ]
    
    url = f"{API_BASE}/anomalies?hours=24"

    # Act
    resp = httpx.get(url, timeout=10)

    # Assert
    assert resp.status_code == 200, resp.text
    anomalies = resp.json()
    assert isinstance(anomalies, list)
    # If there are anomalies, validate a few fields
    if anomalies:
        a0 = anomalies[0]
        for key in ["id", "node_id", "timestamp", "anomaly_type", "severity"]:
            assert key in a0


