"""Integration tests for anomaly detection system."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
import asyncpg
import numpy as np


@pytest.fixture
def mock_db_connection(mocker):
    """Mock database connection."""
    mock_conn = AsyncMock()
    mock_connect = mocker.patch(
        'src.presentation.api.endpoints.anomaly_router.asyncpg.connect',
        return_value=mock_conn
    )
    return mock_conn


@pytest.fixture
def sample_sensor_data():
    """Generate sample sensor readings for testing."""
    base_time = datetime.now(timezone.utc)
    return [
        {
            'timestamp': base_time - timedelta(hours=i),
            'node_id': 'NODE-001',
            'pressure': 3.0 + np.random.normal(0, 0.1),  # Normal around 3.0 bar
            'flow_rate': 100.0 + np.random.normal(0, 5),  # Normal around 100 L/s
            'temperature': 15.0 + np.random.normal(0, 0.5),
            'quality_score': 0.95
        }
        for i in range(24)
    ]


@pytest.fixture
def anomalous_sensor_data():
    """Generate sensor data with anomalies."""
    base_time = datetime.now(timezone.utc)
    data = []
    for i in range(24):
        if i in [5, 6, 7]:  # Pressure drop anomaly
            pressure = 1.5  # Significant drop
            flow_rate = 150.0  # Increased flow (possible leak)
        elif i == 15:  # Quality anomaly
            pressure = 3.0
            flow_rate = 100.0
        else:
            pressure = 3.0 + np.random.normal(0, 0.1)
            flow_rate = 100.0 + np.random.normal(0, 5)
        
        data.append({
            'timestamp': base_time - timedelta(hours=i),
            'node_id': 'NODE-001',
            'pressure': pressure,
            'flow_rate': flow_rate,
            'temperature': 15.0 + np.random.normal(0, 0.5),
            'quality_score': 0.6 if i == 15 else 0.95
        })
    return data


class TestAnomalyDetection:
    """Test anomaly detection functionality."""
    
    async def test_detect_pressure_anomaly(self, mock_db_connection, anomalous_sensor_data):
        """Should detect pressure drop anomalies."""
        # Arrange
        mock_db_connection.fetch.return_value = anomalous_sensor_data
        mock_db_connection.close = AsyncMock()
        
        from src.application.anomaly_detector import AnomalyDetector
        detector = AnomalyDetector(mock_db_connection)
        
        # Act
        anomalies = await detector.detect_anomalies('NODE-001', hours=24)
        
        # Assert
        assert len(anomalies) > 0
        pressure_anomalies = [a for a in anomalies if a['anomaly_type'] == 'pressure_drop']
        assert len(pressure_anomalies) > 0
        assert pressure_anomalies[0]['severity'] in ['high', 'critical']
        assert pressure_anomalies[0]['actual_value'] < 2.0
    
    async def test_detect_flow_anomaly(self, mock_db_connection, anomalous_sensor_data):
        """Should detect abnormal flow rate patterns."""
        # Arrange
        mock_db_connection.fetch.return_value = anomalous_sensor_data
        mock_db_connection.close = AsyncMock()
        
        from src.application.anomaly_detector import AnomalyDetector
        detector = AnomalyDetector(mock_db_connection)
        
        # Act
        anomalies = await detector.detect_anomalies('NODE-001', hours=24)
        
        # Assert
        flow_anomalies = [a for a in anomalies if a['anomaly_type'] == 'flow_anomaly']
        assert len(flow_anomalies) > 0
        assert flow_anomalies[0]['actual_value'] > 130  # Significantly higher than normal
    
    async def test_detect_quality_anomaly(self, mock_db_connection, anomalous_sensor_data):
        """Should detect water quality issues."""
        # Arrange
        mock_db_connection.fetch.return_value = anomalous_sensor_data
        mock_db_connection.close = AsyncMock()
        
        from src.application.anomaly_detector import AnomalyDetector
        detector = AnomalyDetector(mock_db_connection)
        
        # Act
        anomalies = await detector.detect_anomalies('NODE-001', hours=24)
        
        # Assert
        quality_anomalies = [a for a in anomalies if a['anomaly_type'] == 'quality_alert']
        assert len(quality_anomalies) > 0
        assert quality_anomalies[0]['actual_value'] < 0.8  # Below threshold
    
    async def test_calculate_anomaly_severity(self, mock_db_connection):
        """Should correctly calculate anomaly severity based on deviation."""
        # Arrange
        from src.application.anomaly_detector import AnomalyDetector
        detector = AnomalyDetector(mock_db_connection)
        
        # Act & Assert
        assert detector.calculate_severity(10) == 'low'
        assert detector.calculate_severity(25) == 'medium'
        assert detector.calculate_severity(40) == 'high'
        assert detector.calculate_severity(60) == 'critical'
    
    async def test_no_anomalies_in_normal_data(self, mock_db_connection, sample_sensor_data):
        """Should not detect anomalies in normal sensor readings."""
        # Arrange
        mock_db_connection.fetch.return_value = sample_sensor_data
        mock_db_connection.close = AsyncMock()
        
        from src.application.anomaly_detector import AnomalyDetector
        detector = AnomalyDetector(mock_db_connection)
        
        # Act
        anomalies = await detector.detect_anomalies('NODE-001', hours=24)
        
        # Assert
        assert len(anomalies) == 0
    
    async def test_statistical_threshold_detection(self, mock_db_connection):
        """Should use statistical methods (z-score, IQR) for anomaly detection."""
        # Arrange
        data = [3.0] * 20 + [1.0]  # One outlier
        
        from src.application.anomaly_detector import AnomalyDetector
        detector = AnomalyDetector(mock_db_connection)
        
        # Act
        outliers = detector.detect_outliers_zscore(data, threshold=2.0)
        
        # Assert
        assert len(outliers) == 1
        assert outliers[0] == len(data) - 1  # Last element is outlier
    
    async def test_pattern_based_detection(self, mock_db_connection):
        """Should detect pattern-based anomalies (sudden changes, trends)."""
        # Arrange
        # Sudden spike pattern
        data = [3.0] * 10 + [6.0] + [3.0] * 10
        
        from src.application.anomaly_detector import AnomalyDetector
        detector = AnomalyDetector(mock_db_connection)
        
        # Act
        spikes = detector.detect_sudden_changes(data, window=3)
        
        # Assert
        assert len(spikes) > 0
        assert 10 in spikes  # Index of the spike
    
    async def test_persist_detected_anomalies(self, mock_db_connection):
        """Should save detected anomalies to database."""
        # Arrange
        anomaly = {
            'node_id': 'NODE-001',
            'timestamp': datetime.now(timezone.utc),
            'anomaly_type': 'pressure_drop',
            'severity': 'high',
            'actual_value': 1.5,
            'expected_value': 3.0,
            'deviation_percentage': 50.0
        }
        
        mock_db_connection.execute.return_value = None
        mock_db_connection.close = AsyncMock()
        
        from src.application.anomaly_detector import AnomalyDetector
        detector = AnomalyDetector(mock_db_connection)
        
        # Act
        result = await detector.save_anomaly(anomaly)
        
        # Assert
        assert result is True
        mock_db_connection.execute.assert_called_once()
        call_args = mock_db_connection.execute.call_args[0]
        assert 'INSERT INTO water_infrastructure.anomalies' in call_args[0]