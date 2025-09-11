"""
Comprehensive integration tests for dashboard and anomalies APIs.
Tests all DTO fields and edge cases to match production contracts.
"""

import os
import httpx
import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone
from tests.fixtures.comprehensive_mocks import ComprehensiveMockFixtures


API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")


class TestDashboardAPIComprehensive:
    """Comprehensive tests for dashboard API endpoints."""
    
    @patch('src.presentation.api.endpoints.dashboard_router.get_db_connection')
    def test_dashboard_summary_complete_dto_structure(self, mock_get_db_connection):
        """Test that dashboard response matches complete production DTO structure."""
        # Arrange
        fixtures = ComprehensiveMockFixtures()
        mock_conn = fixtures.get_mock_db_connection('standard')
        mock_get_db_connection.return_value = mock_conn
        
        url = f"{API_BASE}/dashboard/summary"
        
        # Act
        resp = httpx.get(url, timeout=10)
        
        # Assert
        assert resp.status_code == 200
        data = resp.json()
        
        # Validate top-level structure
        assert "success" in data
        assert data["success"] is True
        assert "data" in data
        
        dashboard_data = data["data"]
        
        # Validate overview section
        assert "overview" in dashboard_data
        overview = dashboard_data["overview"]
        assert "totalConsumption" in overview
        assert "activeConnections" in overview
        assert "anomalies" in overview
        assert "efficiency" in overview
        assert "lastUpdate" in overview
        assert isinstance(overview["totalConsumption"], (int, float))
        assert isinstance(overview["activeConnections"], int)
        assert isinstance(overview["anomalies"], int)
        assert isinstance(overview["efficiency"], (int, float))
        
        # Validate metrics section
        assert "metrics" in dashboard_data
        metrics = dashboard_data["metrics"]
        
        # Flow rate metrics
        assert "flowRate" in metrics
        flow_rate = metrics["flowRate"]
        assert "current" in flow_rate
        assert "average" in flow_rate
        assert "peak" in flow_rate
        assert all(isinstance(flow_rate[k], (int, float)) for k in ["current", "average", "peak"])
        
        # Pressure metrics
        assert "pressure" in metrics
        pressure = metrics["pressure"]
        assert "current" in pressure
        assert "average" in pressure
        assert "minimum" in pressure
        assert all(isinstance(pressure[k], (int, float)) for k in ["current", "average", "minimum"])
        
        # Quality metrics
        assert "quality" in metrics
        quality = metrics["quality"]
        assert "score" in quality
        assert "status" in quality
        assert isinstance(quality["score"], (int, float))
        assert isinstance(quality["status"], str)
        
        # Validate nodes array
        assert "nodes" in dashboard_data
        assert isinstance(dashboard_data["nodes"], list)
        if dashboard_data["nodes"]:
            node = dashboard_data["nodes"][0]
            assert "node_id" in node
            assert "node_name" in node
            assert "flow_rate" in node
            assert "pressure" in node
            assert "temperature" in node
            assert "anomaly_count" in node
            assert "quality_score" in node
            assert "last_reading" in node
        
        # Validate network section
        assert "network" in dashboard_data
        network = dashboard_data["network"]
        required_network_fields = [
            "active_nodes", "total_flow_lps", "average_pressure_bar",
            "total_volume_m3", "anomaly_count", "efficiency_percentage",
            "alert_count", "energy_consumption_kwh", "water_quality_index",
            "active_connections"
        ]
        for field in required_network_fields:
            assert field in network, f"Missing network field: {field}"
        
        # Validate additional top-level fields
        assert "recent_anomalies" in dashboard_data
        assert "total_consumption" in dashboard_data
        assert "system_health" in dashboard_data
        assert "last_updated" in dashboard_data
        assert "data_timestamp" in dashboard_data
        assert "data_note" in dashboard_data
    
    @patch('src.presentation.api.endpoints.dashboard_router.get_db_connection')
    def test_dashboard_with_no_data(self, mock_get_db_connection):
        """Test dashboard response when no data is available."""
        # Arrange
        fixtures = ComprehensiveMockFixtures()
        mock_conn = fixtures.get_mock_db_connection('no_data')
        mock_get_db_connection.return_value = mock_conn
        
        # Also mock the fetch results for nodes
        mock_conn.fetch.return_value = []
        mock_conn.fetchrow.return_value = {'latest_timestamp': None}
        
        url = f"{API_BASE}/dashboard/summary"
        
        # Act
        resp = httpx.get(url, timeout=10)
        
        # Assert
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        
        dashboard_data = data["data"]
        assert dashboard_data["nodes"] == []
        assert dashboard_data["network"]["active_nodes"] == 0
        assert dashboard_data["network"]["total_flow_lps"] == 0.0
        assert dashboard_data["data_timestamp"] is None
    
    @patch('src.presentation.api.endpoints.dashboard_router.get_db_connection')
    def test_dashboard_with_partial_data(self, mock_get_db_connection):
        """Test dashboard response with partial data (some nulls)."""
        # Arrange
        fixtures = ComprehensiveMockFixtures()
        mock_conn = fixtures.get_mock_db_connection('partial')
        mock_get_db_connection.return_value = mock_conn
        
        url = f"{API_BASE}/dashboard/summary"
        
        # Act
        resp = httpx.get(url, timeout=10)
        
        # Assert
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        
        # Should handle partial data gracefully
        dashboard_data = data["data"]
        assert "overview" in dashboard_data
        assert "metrics" in dashboard_data
        assert "network" in dashboard_data
    
    @patch('src.presentation.api.endpoints.dashboard_router.get_db_connection')
    def test_dashboard_with_database_error(self, mock_get_db_connection):
        """Test dashboard response when database error occurs."""
        # Arrange
        mock_conn = AsyncMock()
        mock_conn.fetchrow.side_effect = Exception("Database connection failed")
        mock_get_db_connection.return_value = mock_conn
        
        url = f"{API_BASE}/dashboard/summary"
        
        # Act
        resp = httpx.get(url, timeout=10)
        
        # Assert
        assert resp.status_code == 500
        assert "detail" in resp.json()


class TestAnomaliesAPIComprehensive:
    """Comprehensive tests for anomalies API endpoints."""
    
    @patch('src.presentation.api.endpoints.anomaly_router.get_db_connection')
    def test_anomalies_complete_dto_structure(self, mock_get_db_connection):
        """Test that anomalies response matches complete production DTO structure."""
        # Arrange
        fixtures = ComprehensiveMockFixtures()
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        
        # Create comprehensive anomaly data
        anomaly_data = []
        base_time = datetime.now(timezone.utc)
        for i in range(3):
            anomaly_data.append({
                'id': f'TEST_ANOM_{i+1}',
                'node_id': f'TEST_NODE_{i+1}',
                'node_name': f'Test Node {i+1}',
                'timestamp': base_time - timedelta(hours=i),
                'anomaly_type': 'pressure_drop' if i % 2 == 0 else 'flow_spike',
                'severity': ['low', 'medium', 'high'][i],
                'measurement_type': 'pressure' if i % 2 == 0 else 'flow_rate',
                'actual_value': 2.1 + i * 0.3,
                'expected_value': 3.5,
                'deviation_percentage': 15.5 + i * 2.1,
                'description': f'Test anomaly {i+1}',
                'resolved_at': None,
                'confidence': 0.85 + i * 0.05
            })
        
        mock_conn.fetch.return_value = anomaly_data
        mock_conn.close = AsyncMock()
        
        url = f"{API_BASE}/anomalies?hours=24"
        
        # Act
        resp = httpx.get(url, timeout=10)
        
        # Assert
        assert resp.status_code == 200
        anomalies = resp.json()
        assert isinstance(anomalies, list)
        assert len(anomalies) == 3
        
        # Validate complete structure of first anomaly
        anomaly = anomalies[0]
        required_fields = [
            "id", "node_id", "node_name", "timestamp", "anomaly_type",
            "severity", "measurement_type", "actual_value", "expected_value",
            "deviation_percentage", "description", "resolved_at", "confidence"
        ]
        
        for field in required_fields:
            assert field in anomaly, f"Missing field: {field}"
        
        # Validate field types
        assert isinstance(anomaly["id"], str)
        assert isinstance(anomaly["node_id"], str)
        assert isinstance(anomaly["node_name"], str)
        assert isinstance(anomaly["timestamp"], str)
        assert isinstance(anomaly["anomaly_type"], str)
        assert isinstance(anomaly["severity"], str)
        assert isinstance(anomaly["measurement_type"], str)
        assert anomaly["actual_value"] is None or isinstance(anomaly["actual_value"], (int, float))
        assert anomaly["expected_value"] is None or isinstance(anomaly["expected_value"], (int, float))
        assert isinstance(anomaly["deviation_percentage"], (int, float))
        assert isinstance(anomaly["description"], str)
        assert anomaly["resolved_at"] is None or isinstance(anomaly["resolved_at"], str)
        assert isinstance(anomaly["confidence"], (int, float))
    
    @patch('src.presentation.api.endpoints.anomaly_router.get_db_connection')
    def test_anomalies_with_filters(self, mock_get_db_connection):
        """Test anomalies endpoint with various filters."""
        # Arrange
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.fetch.return_value = []
        mock_conn.close = AsyncMock()
        
        # Test with node_id filter
        url = f"{API_BASE}/anomalies?hours=24&node_id=TEST_NODE_1"
        resp = httpx.get(url, timeout=10)
        assert resp.status_code == 200
        
        # Test with severity filter
        url = f"{API_BASE}/anomalies?hours=24&severity=high"
        resp = httpx.get(url, timeout=10)
        assert resp.status_code == 200
        
        # Test with both filters
        url = f"{API_BASE}/anomalies?hours=24&node_id=TEST_NODE_1&severity=medium"
        resp = httpx.get(url, timeout=10)
        assert resp.status_code == 200
    
    @patch('src.presentation.api.endpoints.anomaly_router.get_db_connection')
    def test_anomalies_empty_result(self, mock_get_db_connection):
        """Test anomalies endpoint when no anomalies are found."""
        # Arrange
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.fetch.return_value = []
        mock_conn.close = AsyncMock()
        
        url = f"{API_BASE}/anomalies?hours=1"
        
        # Act
        resp = httpx.get(url, timeout=10)
        
        # Assert
        assert resp.status_code == 200
        anomalies = resp.json()
        assert isinstance(anomalies, list)
        assert len(anomalies) == 0
    
    @patch('src.presentation.api.endpoints.anomaly_router.get_db_connection')
    def test_anomaly_statistics_complete_structure(self, mock_get_db_connection):
        """Test anomaly statistics endpoint with complete DTO structure."""
        # Arrange
        fixtures = ComprehensiveMockFixtures()
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        
        # Mock statistics query results
        base_time = datetime.now(timezone.utc)
        stats_data = []
        for i in range(7):
            stats_data.append({
                'anomaly_type': 'pressure_drop' if i % 2 == 0 else 'flow_spike',
                'severity': ['low', 'medium', 'high'][i % 3],
                'count': 5 + i,
                'date': (base_time - timedelta(days=i)).date()
            })
        
        nodes_data = []
        for i in range(5):
            nodes_data.append({
                'node_id': f'TEST_NODE_{i+1}',
                'node_name': f'Test Node {i+1}',
                'anomaly_count': 10 - i,
                'types': ['pressure_drop', 'flow_spike'] if i % 2 == 0 else ['temperature_anomaly']
            })
        
        mock_conn.fetch.side_effect = [stats_data, nodes_data]
        mock_conn.close = AsyncMock()
        
        url = f"{API_BASE}/anomalies/statistics?days=7"
        
        # Act
        resp = httpx.get(url, timeout=10)
        
        # Assert
        assert resp.status_code == 200
        stats = resp.json()
        
        # Validate complete structure
        required_fields = [
            "period_days", "total_anomalies", "by_type", "by_severity",
            "timeline", "top_affected_nodes", "generated_at"
        ]
        
        for field in required_fields:
            assert field in stats, f"Missing field: {field}"
        
        # Validate field types
        assert isinstance(stats["period_days"], int)
        assert isinstance(stats["total_anomalies"], int)
        assert isinstance(stats["by_type"], dict)
        assert isinstance(stats["by_severity"], dict)
        assert isinstance(stats["timeline"], dict)
        assert isinstance(stats["top_affected_nodes"], list)
        assert isinstance(stats["generated_at"], str)
        
        # Validate top_affected_nodes structure
        if stats["top_affected_nodes"]:
            node = stats["top_affected_nodes"][0]
            assert "node_id" in node
            assert "node_name" in node
            assert "anomaly_count" in node
            assert "anomaly_types" in node
            assert isinstance(node["anomaly_types"], list)
    
    @patch('src.presentation.api.endpoints.anomaly_router.get_db_connection')
    def test_acknowledge_anomaly_success(self, mock_get_db_connection):
        """Test successful anomaly acknowledgment."""
        # Arrange
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        
        resolved_time = datetime.now(timezone.utc)
        mock_conn.fetchrow.return_value = {
            'anomaly_id': 1,
            'node_id': 'TEST_NODE_1',
            'resolved_at': resolved_time
        }
        mock_conn.close = AsyncMock()
        
        url = f"{API_BASE}/anomalies/1/acknowledge"
        
        # Act
        resp = httpx.patch(url, timeout=10)
        
        # Assert
        assert resp.status_code == 200
        result = resp.json()
        assert result["status"] == "success"
        assert result["anomaly_id"] == 1
        assert result["node_id"] == "TEST_NODE_1"
        assert "resolved_at" in result
        assert result["message"] == "Anomaly acknowledged successfully"
    
    @patch('src.presentation.api.endpoints.anomaly_router.get_db_connection')
    def test_acknowledge_anomaly_not_found(self, mock_get_db_connection):
        """Test anomaly acknowledgment when anomaly not found."""
        # Arrange
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.fetchrow.return_value = None
        mock_conn.close = AsyncMock()
        
        url = f"{API_BASE}/anomalies/999/acknowledge"
        
        # Act
        resp = httpx.patch(url, timeout=10)
        
        # Assert
        assert resp.status_code == 404
        assert "detail" in resp.json()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @patch('src.presentation.api.endpoints.dashboard_router.get_db_connection')
    def test_dashboard_with_extreme_values(self, mock_get_db_connection):
        """Test dashboard with extreme/maximum values."""
        # Arrange
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        
        # Setup extreme values
        mock_conn.fetchrow.side_effect = [
            {'latest_timestamp': datetime.now(timezone.utc)},
            {
                'total_liters': 999999999.99,
                'avg_flow_rate': 9999.99,
                'avg_pressure': 10.0,
                'active_connections': 10000
            },
            {
                'pressure_anomalies': 999,
                'flow_anomalies': 999,
                'temp_anomalies': 999
            }
        ]
        
        mock_conn.fetch.return_value = []
        mock_conn.close = AsyncMock()
        
        url = f"{API_BASE}/dashboard/summary"
        
        # Act
        resp = httpx.get(url, timeout=10)
        
        # Assert
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        
        # Values should be handled without overflow
        dashboard_data = data["data"]
        assert dashboard_data["overview"]["totalConsumption"] == 999999999.99
        assert dashboard_data["overview"]["activeConnections"] == 10000
    
    @patch('src.presentation.api.endpoints.anomaly_router.get_db_connection')
    def test_anomalies_with_null_optional_fields(self, mock_get_db_connection):
        """Test anomalies with null values in optional fields."""
        # Arrange
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        
        # Create anomaly with null optional fields
        anomaly_data = [{
            'id': 'TEST_ANOM_1',
            'node_id': 'TEST_NODE_1',
            'node_name': 'Test Node 1',
            'timestamp': datetime.now(timezone.utc),
            'anomaly_type': 'unknown',
            'severity': 'low',
            'measurement_type': 'unknown',
            'actual_value': None,  # Null value
            'expected_value': None,  # Null value
            'deviation_percentage': 0.0,
            'description': 'Unknown anomaly',
            'resolved_at': None,  # Null value
            'confidence': 0.5
        }]
        
        mock_conn.fetch.return_value = anomaly_data
        mock_conn.close = AsyncMock()
        
        url = f"{API_BASE}/anomalies?hours=24"
        
        # Act
        resp = httpx.get(url, timeout=10)
        
        # Assert
        assert resp.status_code == 200
        anomalies = resp.json()
        assert len(anomalies) == 1
        
        anomaly = anomalies[0]
        assert anomaly["actual_value"] is None
        assert anomaly["expected_value"] is None
        assert anomaly["resolved_at"] is None
        assert anomaly["deviation_percentage"] == 0.0


# Add this to imports at the top of the file
from datetime import timedelta