"""Integration tests for ML predictions API endpoints."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.presentation.api.app_postgres import app


class TestPredictionsAPI:
    """Test suite for predictions API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_db_pool(self):
        """Mock database pool."""
        with patch("src.presentation.api.app_postgres.db_pool") as mock:
            mock_conn = MagicMock()
            mock_conn.fetchone = MagicMock(return_value={"data": [100] * 168})
            mock_conn.fetch = MagicMock(
                return_value=[
                    {"hour": i, "consumption": 100 + i * 5} for i in range(168)
                ]
            )
            mock.acquire.return_value.__aenter__.return_value = mock_conn
            yield mock

    def test_predict_peak_demand(self, client, mock_db_pool):
        """Test peak demand prediction endpoint."""
        # Act
        response = client.get("/api/v1/predictions/peak-demand?zone_id=1&days=7")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert "confidence_interval" in data
        assert "accuracy_score" in data
        assert len(data["predictions"]) == 7 * 24
        assert 0 <= data["accuracy_score"] <= 1

    def test_optimize_energy_schedule(self, client, mock_db_pool):
        """Test energy optimization endpoint."""
        # Act
        response = client.post(
            "/api/v1/predictions/optimize-energy",
            json={
                "zone_id": 1,
                "tariffs": {
                    "peak": [8, 9, 10, 11, 17, 18, 19, 20],
                    "off_peak": list(range(0, 8)) + list(range(21, 24)),
                    "rates": {"peak": 0.25, "off_peak": 0.10},
                },
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "schedule" in data
        assert "estimated_savings" in data
        assert "savings_percentage" in data
        assert data["estimated_savings"] >= 0
        assert len(data["schedule"]) == 24

    def test_predict_maintenance(self, client, mock_db_pool):
        """Test maintenance prediction endpoint."""
        # Arrange
        mock_db_pool.acquire.return_value.__aenter__.return_value.fetch.return_value = [
            {"timestamp": "2024-01-01T00:00:00", "pressure": 3.0 - i * 0.01}
            for i in range(100)
        ]

        # Act
        response = client.get("/api/v1/predictions/maintenance?equipment_id=PUMP001")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data
        assert "days_to_maintenance" in data
        assert "failure_probability" in data
        assert "recommendations" in data
        assert data["risk_score"] in ["low", "medium", "high", "critical"]

    def test_predict_water_loss(self, client, mock_db_pool):
        """Test water loss prediction endpoint."""
        # Arrange
        mock_db_pool.acquire.return_value.__aenter__.return_value.fetch.return_value = [
            {"flow_in": 100, "flow_out": 95, "pressure": 3.2, "night_flow": 20}
            for _ in range(24)
        ]

        # Act
        response = client.get("/api/v1/predictions/water-loss?zone_id=1")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "current_loss_percentage" in data
        assert "predicted_loss_trend" in data
        assert "leak_probability" in data
        assert "recommended_actions" in data
        assert 0 <= data["leak_probability"] <= 1

    def test_predictions_with_missing_data(self, client, mock_db_pool):
        """Test predictions handle missing data gracefully."""
        # Arrange
        mock_db_pool.acquire.return_value.__aenter__.return_value.fetch.return_value = []

        # Act
        response = client.get("/api/v1/predictions/peak-demand?zone_id=999&days=7")

        # Assert
        assert response.status_code == 404
        assert "error" in response.json()