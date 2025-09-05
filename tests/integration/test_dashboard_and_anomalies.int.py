import os
import httpx


API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")


def test_dashboard_summary_returns_200_and_valid_shape():
    # Arrange
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
    assert set(["active_nodes", "total_flow", "avg_pressure", "total_volume_m3", "anomaly_count"]) <= set(data["network"].keys())


def test_anomalies_returns_200_and_list():
    # Arrange
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


