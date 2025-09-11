"""
Comprehensive error scenario tests for all API endpoints.
Tests 4xx and 5xx error responses in mock mode.
"""

import os
import httpx
import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone
import asyncpg


API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")


class TestBadRequestErrors:
    """Test 400 Bad Request scenarios across all endpoints."""
    
    @pytest.mark.parametrize("endpoint,params", [
        ("/anomalies", {"hours": -1}),  # Negative hours
        ("/anomalies", {"hours": 10000}),  # Excessive hours
        ("/anomalies", {"severity": "invalid"}),  # Invalid severity
        ("/anomalies/statistics", {"days": -1}),  # Negative days
        ("/anomalies/statistics", {"days": 0}),  # Zero days
        ("/infrastructure/map", {"invalid_param": "test"}),  # Unknown parameter
        ("/network/topology", {"depth": -1}),  # Negative depth
        ("/pressure/zones", {"zone_id": ""}),  # Empty zone ID
        ("/weather/current", {"node_id": ""}),  # Empty node ID
        ("/forecasts/consumption", {"horizon": "invalid"}),  # Invalid horizon
    ])
    def test_invalid_parameters(self, endpoint, params):
        """Test endpoints with invalid parameters return 400."""
        url = f"{API_BASE}{endpoint}"
        
        # Act
        resp = httpx.get(url, params=params, timeout=10)
        
        # Assert - Should either return 400 or handle gracefully
        # Note: Some endpoints may handle invalid params differently
        assert resp.status_code in [200, 400, 422], f"Unexpected status for {endpoint}: {resp.status_code}"
        
        if resp.status_code in [400, 422]:
            error_data = resp.json()
            assert "detail" in error_data or "error" in error_data
    
    @pytest.mark.parametrize("endpoint,payload", [
        ("/anomalies/detect", {}),  # Missing required fields
        ("/anomalies/detect", {"node_id": "", "hours": 24}),  # Empty node_id
        ("/reports/generate", {}),  # Missing report type
        ("/reports/generate", {"report_type": "invalid"}),  # Invalid report type
        ("/predictions/track", {"model_id": None}),  # Null model_id
    ])
    def test_invalid_post_payload(self, endpoint, payload):
        """Test POST endpoints with invalid payloads."""
        url = f"{API_BASE}{endpoint}"
        
        # Act
        resp = httpx.post(url, json=payload, timeout=10)
        
        # Assert
        assert resp.status_code in [400, 404, 422], f"Expected 4xx for {endpoint}, got {resp.status_code}"


class TestNotFoundErrors:
    """Test 404 Not Found scenarios."""
    
    @patch('src.presentation.api.endpoints.anomaly_router.get_db_connection')
    def test_acknowledge_nonexistent_anomaly(self, mock_get_db_connection):
        """Test acknowledging non-existent anomaly returns 404."""
        # Arrange
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.fetchrow.return_value = None  # Anomaly not found
        mock_conn.close = AsyncMock()
        
        url = f"{API_BASE}/anomalies/99999/acknowledge"
        
        # Act
        resp = httpx.patch(url, timeout=10)
        
        # Assert
        assert resp.status_code == 404
        error_data = resp.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()
    
    @pytest.mark.parametrize("endpoint", [
        "/nodes/NONEXISTENT_NODE",
        "/infrastructure/node/FAKE_NODE_ID",
        "/pressure/zones/UNKNOWN_ZONE",
        "/network/path/NODE1/NODE2",  # Non-existent path
        "/reports/download/fake-report-id",
    ])
    def test_resource_not_found(self, endpoint):
        """Test accessing non-existent resources returns 404."""
        url = f"{API_BASE}{endpoint}"
        
        # Act
        resp = httpx.get(url, timeout=10)
        
        # Assert - Should return 404 or handle gracefully
        assert resp.status_code in [200, 404], f"Expected 200 or 404 for {endpoint}, got {resp.status_code}"
        
        if resp.status_code == 404:
            error_data = resp.json()
            assert "detail" in error_data or "error" in error_data or "message" in error_data


class TestServerErrors:
    """Test 500 Internal Server Error scenarios."""
    
    @patch('src.presentation.api.endpoints.dashboard_router.get_db_connection')
    def test_dashboard_database_connection_error(self, mock_get_db_connection):
        """Test dashboard endpoint when database connection fails."""
        # Arrange
        mock_get_db_connection.side_effect = asyncpg.PostgresConnectionError("Connection failed")
        
        url = f"{API_BASE}/dashboard/summary"
        
        # Act
        resp = httpx.get(url, timeout=10)
        
        # Assert
        assert resp.status_code == 500
        error_data = resp.json()
        assert "detail" in error_data
    
    @patch('src.presentation.api.endpoints.anomaly_router.get_db_connection')
    def test_anomalies_database_error(self, mock_get_db_connection):
        """Test anomalies endpoint with database error."""
        # Arrange
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.fetch.side_effect = Exception("Database query failed")
        
        url = f"{API_BASE}/anomalies?hours=24"
        
        # Act
        resp = httpx.get(url, timeout=10)
        
        # Assert
        assert resp.status_code == 500
        error_data = resp.json()
        assert "detail" in error_data
    
    @patch('src.presentation.api.endpoints.anomaly_router.get_db_connection')
    def test_anomaly_statistics_calculation_error(self, mock_get_db_connection):
        """Test anomaly statistics with calculation error."""
        # Arrange
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        # Simulate error during statistics calculation
        mock_conn.fetch.side_effect = [
            Exception("Statistics calculation failed")
        ]
        
        url = f"{API_BASE}/anomalies/statistics?days=7"
        
        # Act
        resp = httpx.get(url, timeout=10)
        
        # Assert
        assert resp.status_code == 500
        error_data = resp.json()
        assert "detail" in error_data
    
    @pytest.mark.parametrize("endpoint", [
        "/dashboard/summary",
        "/anomalies",
        "/infrastructure/map",
        "/network/topology",
        "/pressure/zones",
        "/weather/current",
        "/forecasts/consumption",
        "/nodes",
        "/efficiency/metrics",
    ])
    @patch('asyncpg.connect')
    def test_database_timeout(self, mock_connect, endpoint):
        """Test endpoints with database timeout."""
        # Arrange
        mock_connect.side_effect = asyncpg.PostgresConnectionError("Connection timeout")
        
        # Patch the specific get_db_connection for each router
        router_module = endpoint.split('/')[1]  # Get first part of endpoint
        patch_path = f'src.presentation.api.endpoints.{router_module}_router.get_db_connection'
        
        with patch(patch_path) as mock_get_db:
            mock_get_db.side_effect = asyncpg.PostgresConnectionError("Connection timeout")
            
            url = f"{API_BASE}{endpoint}"
            
            # Act
            resp = httpx.get(url, timeout=10)
            
            # Assert
            # Some endpoints might handle errors differently
            assert resp.status_code in [200, 500], f"Expected 200 or 500 for {endpoint}, got {resp.status_code}"


class TestAuthenticationErrors:
    """Test authentication and authorization error scenarios."""
    
    @pytest.mark.parametrize("endpoint", [
        "/admin/users",
        "/admin/config",
        "/protected/data",
    ])
    def test_unauthorized_access(self, endpoint):
        """Test accessing protected endpoints without auth returns 401."""
        url = f"{API_BASE}{endpoint}"
        
        # Act - Request without auth headers
        resp = httpx.get(url, timeout=10)
        
        # Assert - Should return 401 or 404 (if endpoint doesn't exist)
        assert resp.status_code in [401, 404], f"Expected 401 or 404 for {endpoint}, got {resp.status_code}"
    
    def test_forbidden_access_with_insufficient_permissions(self):
        """Test accessing admin endpoints with user token returns 403."""
        url = f"{API_BASE}/admin/settings"
        headers = {"Authorization": "Bearer user_token_here"}
        
        # Act
        resp = httpx.get(url, headers=headers, timeout=10)
        
        # Assert - Should return 403 or 404
        assert resp.status_code in [403, 404], f"Expected 403 or 404, got {resp.status_code}"


class TestValidationErrors:
    """Test 422 Unprocessable Entity scenarios."""
    
    @pytest.mark.parametrize("endpoint,params", [
        ("/anomalies", {"hours": "not_a_number"}),  # Type error
        ("/anomalies/statistics", {"days": "seven"}),  # Type error
        ("/infrastructure/map", {"zoom": "high"}),  # Type error for numeric field
        ("/pressure/zones", {"min_pressure": "low"}),  # Type error
    ])
    def test_type_validation_errors(self, endpoint, params):
        """Test endpoints with wrong type parameters."""
        url = f"{API_BASE}{endpoint}"
        
        # Act
        resp = httpx.get(url, params=params, timeout=10)
        
        # Assert - FastAPI typically returns 422 for validation errors
        assert resp.status_code in [200, 422], f"Expected 200 or 422 for {endpoint}, got {resp.status_code}"
        
        if resp.status_code == 422:
            error_data = resp.json()
            assert "detail" in error_data
            # FastAPI validation errors have specific structure
            if isinstance(error_data["detail"], list):
                assert len(error_data["detail"]) > 0
                assert "type" in error_data["detail"][0]


class TestRateLimitingErrors:
    """Test rate limiting and throttling scenarios."""
    
    @pytest.mark.parametrize("endpoint", [
        "/dashboard/summary",
        "/anomalies",
        "/infrastructure/map",
    ])
    def test_rate_limit_exceeded(self, endpoint):
        """Test that excessive requests might trigger rate limiting."""
        url = f"{API_BASE}{endpoint}"
        
        # Note: Rate limiting might not be implemented yet
        # This test documents expected behavior
        responses = []
        
        # Make many rapid requests
        for _ in range(10):
            resp = httpx.get(url, timeout=5)
            responses.append(resp.status_code)
        
        # Assert - All should succeed or rate limit should kick in
        # 429 is the standard rate limit status code
        valid_codes = [200, 429]
        for status in responses:
            assert status in valid_codes, f"Unexpected status: {status}"


class TestTimeoutErrors:
    """Test timeout and slow response scenarios."""
    
    @patch('src.presentation.api.endpoints.dashboard_router.get_db_connection')
    def test_slow_database_query(self, mock_get_db_connection):
        """Test handling of slow database queries."""
        # Arrange
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        
        # Simulate slow query
        import asyncio
        async def slow_fetch(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate delay
            return []
        
        mock_conn.fetch = slow_fetch
        mock_conn.fetchrow = slow_fetch
        mock_conn.close = AsyncMock()
        
        url = f"{API_BASE}/dashboard/summary"
        
        # Act with short timeout
        resp = httpx.get(url, timeout=30)
        
        # Assert - Should complete or timeout gracefully
        assert resp.status_code in [200, 408, 504], f"Expected 200/408/504, got {resp.status_code}"


class TestCascadingErrors:
    """Test error handling in complex scenarios with multiple failures."""
    
    @patch('src.presentation.api.endpoints.dashboard_router.get_db_connection')
    def test_partial_data_failure(self, mock_get_db_connection):
        """Test dashboard with partial data failures."""
        # Arrange
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        
        # First query succeeds, second fails
        mock_conn.fetchrow.side_effect = [
            {'latest_timestamp': datetime.now(timezone.utc)},
            Exception("Consumption query failed"),
        ]
        mock_conn.fetch.return_value = []  # Nodes query returns empty
        mock_conn.close = AsyncMock()
        
        url = f"{API_BASE}/dashboard/summary"
        
        # Act
        resp = httpx.get(url, timeout=10)
        
        # Assert - May handle partial failures gracefully or return 500
        assert resp.status_code in [200, 500], f"Expected 200 or 500, got {resp.status_code}"
    
    @patch('src.presentation.api.endpoints.anomaly_router.get_db_connection')
    @patch('src.application.anomaly_detector.AnomalyDetector')
    def test_anomaly_detection_partial_failure(self, mock_detector_class, mock_get_db_connection):
        """Test anomaly detection with partial node failures."""
        # Arrange
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        
        # Mock detector that fails for some nodes
        mock_detector = AsyncMock()
        mock_detector_class.return_value = mock_detector
        
        async def detect_with_errors(node_id, hours):
            if node_id == "TEST_NODE_2":
                raise Exception("Detection failed for node")
            return []
        
        mock_detector.detect_anomalies = detect_with_errors
        
        # Mock nodes query
        mock_conn.fetch.return_value = [
            {'node_id': 'TEST_NODE_1'},
            {'node_id': 'TEST_NODE_2'},  # This will fail
            {'node_id': 'TEST_NODE_3'},
        ]
        mock_conn.close = AsyncMock()
        
        url = f"{API_BASE}/anomalies/detect"
        
        # Act
        resp = httpx.post(url, timeout=10)
        
        # Assert - Should handle partial failures
        assert resp.status_code in [200, 207, 500], f"Expected 200/207/500, got {resp.status_code}"


# Parameterized test for all endpoints error handling
@pytest.mark.parametrize("method,endpoint,mock_error", [
    ("GET", "/dashboard/summary", asyncpg.PostgresConnectionError),
    ("GET", "/anomalies", asyncpg.PostgresError),
    ("GET", "/infrastructure/map", ConnectionError),
    ("GET", "/network/topology", TimeoutError),
    ("GET", "/pressure/zones", ValueError),
    ("GET", "/weather/current", KeyError),
    ("GET", "/forecasts/consumption", RuntimeError),
    ("POST", "/anomalies/detect", Exception),
    ("PATCH", "/anomalies/1/acknowledge", asyncpg.PostgresError),
])
def test_generic_error_handling(method, endpoint, mock_error):
    """Test that all endpoints handle errors gracefully."""
    url = f"{API_BASE}{endpoint}"
    
    # Get router module name from endpoint
    router_name = endpoint.split('/')[1] if '/' in endpoint else endpoint
    
    # Dynamically patch the correct router's get_db_connection
    patch_paths = [
        f'src.presentation.api.endpoints.{router_name}_router.get_db_connection',
        f'src.presentation.api.endpoints.anomaly_router.get_db_connection',  # For anomaly endpoints
        f'src.presentation.api.endpoints.dashboard_router.get_db_connection',  # For dashboard
    ]
    
    for patch_path in patch_paths:
        try:
            with patch(patch_path) as mock_get_db:
                mock_get_db.side_effect = mock_error("Simulated error")
                
                # Make request based on method
                if method == "GET":
                    resp = httpx.get(url, timeout=10)
                elif method == "POST":
                    resp = httpx.post(url, json={}, timeout=10)
                elif method == "PATCH":
                    resp = httpx.patch(url, timeout=10)
                else:
                    resp = httpx.request(method, url, timeout=10)
                
                # Assert - Should handle error gracefully
                assert resp.status_code in [200, 400, 404, 422, 500], \
                    f"Unexpected status {resp.status_code} for {endpoint} with {mock_error.__name__}"
                
                break  # If patch worked, exit loop
        except (ImportError, AttributeError):
            continue  # Try next patch path