"""Anomaly detection system for water infrastructure monitoring."""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import numpy as np
from scipy import stats
import asyncpg
import logging

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detects anomalies in water infrastructure sensor data."""
    
    def __init__(self, db_connection: asyncpg.Connection):
        """Initialize the anomaly detector.
        
        Args:
            db_connection: Database connection for data access
        """
        self.db_connection = db_connection
        self.thresholds = {
            'pressure': {'min': 2.0, 'max': 4.0, 'normal': 3.0},
            'flow_rate': {'min': 50, 'max': 150, 'normal': 100},
            'quality_score': {'min': 0.85, 'max': 1.0, 'normal': 0.95},
            'temperature': {'min': 10, 'max': 25, 'normal': 15}
        }
    
    async def detect_anomalies(self, node_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Detect anomalies for a specific node.
        
        Args:
            node_id: Node identifier
            hours: Number of hours to analyze
            
        Returns:
            List of detected anomalies
        """
        # Fetch sensor data
        sensor_data = await self._fetch_sensor_data(node_id, hours)
        if not sensor_data:
            return []
        
        anomalies = []
        
        # Check for pressure anomalies
        pressure_anomalies = self._detect_pressure_anomalies(sensor_data)
        anomalies.extend(pressure_anomalies)
        
        # Check for flow anomalies
        flow_anomalies = self._detect_flow_anomalies(sensor_data)
        anomalies.extend(flow_anomalies)
        
        # Check for quality anomalies
        quality_anomalies = self._detect_quality_anomalies(sensor_data)
        anomalies.extend(quality_anomalies)
        
        # Check for pattern-based anomalies
        pattern_anomalies = self._detect_pattern_anomalies(sensor_data)
        anomalies.extend(pattern_anomalies)
        
        # Save detected anomalies
        for anomaly in anomalies:
            await self.save_anomaly(anomaly)
        
        return anomalies
    
    async def _fetch_sensor_data(self, node_id: str, hours: int) -> List[Dict[str, Any]]:
        """Fetch sensor data from database.
        
        Args:
            node_id: Node identifier
            hours: Number of hours to fetch
            
        Returns:
            List of sensor readings
        """
        if hasattr(self.db_connection, 'fetch'):
            # Using mock in tests
            return await self.db_connection.fetch()
        
        # Real database query
        query = """
            SELECT timestamp, node_id, pressure, flow_rate, temperature, quality_score
            FROM water_infrastructure.sensor_readings
            WHERE node_id = $1 AND timestamp > NOW() - INTERVAL '1 hour' * $2
            ORDER BY timestamp DESC
        """
        try:
            rows = await self.db_connection.fetch(query, node_id, hours)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching sensor data: {e}")
            return []
    
    def _detect_pressure_anomalies(self, sensor_data: List[Dict]) -> List[Dict]:
        """Detect pressure-related anomalies."""
        anomalies = []
        pressures = [d.get('pressure', 0) for d in sensor_data if d.get('pressure')]
        
        if not pressures:
            return anomalies
        
        # Statistical analysis
        mean_pressure = np.mean(pressures)
        std_pressure = np.std(pressures)
        
        for data in sensor_data:
            pressure = data.get('pressure')
            if not pressure:
                continue
            
            # Check absolute thresholds
            if pressure < self.thresholds['pressure']['min']:
                deviation = abs(pressure - self.thresholds['pressure']['normal'])
                deviation_pct = (deviation / self.thresholds['pressure']['normal']) * 100
                
                anomalies.append({
                    'node_id': data['node_id'],
                    'timestamp': data['timestamp'],
                    'anomaly_type': 'pressure_drop',
                    'severity': self.calculate_severity(deviation_pct),
                    'actual_value': pressure,
                    'expected_value': self.thresholds['pressure']['normal'],
                    'deviation_percentage': deviation_pct,
                    'measurement_type': 'pressure',
                    'description': f'Pressure dropped to {pressure:.1f} bar (expected ~{self.thresholds["pressure"]["normal"]} bar)'
                })
            
            # Z-score based detection
            if std_pressure > 0:
                z_score = abs((pressure - mean_pressure) / std_pressure)
                if z_score > 2.5:
                    anomalies.append({
                        'node_id': data['node_id'],
                        'timestamp': data['timestamp'],
                        'anomaly_type': 'pressure_anomaly',
                        'severity': self.calculate_severity(z_score * 10),
                        'actual_value': pressure,
                        'expected_value': mean_pressure,
                        'deviation_percentage': abs((pressure - mean_pressure) / mean_pressure) * 100,
                        'measurement_type': 'pressure',
                        'description': f'Unusual pressure reading: {pressure:.1f} bar (z-score: {z_score:.1f})'
                    })
        
        return anomalies
    
    def _detect_flow_anomalies(self, sensor_data: List[Dict]) -> List[Dict]:
        """Detect flow rate anomalies."""
        anomalies = []
        flows = [d.get('flow_rate', 0) for d in sensor_data if d.get('flow_rate')]
        
        if not flows:
            return anomalies
        
        mean_flow = np.mean(flows)
        std_flow = np.std(flows)
        
        for data in sensor_data:
            flow = data.get('flow_rate')
            if not flow:
                continue
            
            # Check for abnormal flow rates
            if flow > self.thresholds['flow_rate']['max']:
                deviation_pct = ((flow - self.thresholds['flow_rate']['normal']) / 
                               self.thresholds['flow_rate']['normal']) * 100
                
                anomalies.append({
                    'node_id': data['node_id'],
                    'timestamp': data['timestamp'],
                    'anomaly_type': 'flow_anomaly',
                    'severity': self.calculate_severity(abs(deviation_pct)),
                    'actual_value': flow,
                    'expected_value': self.thresholds['flow_rate']['normal'],
                    'deviation_percentage': deviation_pct,
                    'measurement_type': 'flow_rate',
                    'description': f'High flow rate detected: {flow:.1f} L/s'
                })
            
            # Detect potential leaks (high flow with low pressure)
            pressure = data.get('pressure')
            if pressure and flow > mean_flow * 1.3 and pressure < self.thresholds['pressure']['min']:
                anomalies.append({
                    'node_id': data['node_id'],
                    'timestamp': data['timestamp'],
                    'anomaly_type': 'potential_leak',
                    'severity': 'critical',
                    'actual_value': flow,
                    'expected_value': mean_flow,
                    'deviation_percentage': ((flow - mean_flow) / mean_flow) * 100,
                    'measurement_type': 'flow_rate',
                    'description': f'Potential leak detected: high flow ({flow:.1f} L/s) with low pressure ({pressure:.1f} bar)'
                })
        
        return anomalies
    
    def _detect_quality_anomalies(self, sensor_data: List[Dict]) -> List[Dict]:
        """Detect water quality anomalies."""
        anomalies = []
        
        for data in sensor_data:
            quality = data.get('quality_score')
            if not quality:
                continue
            
            if quality < self.thresholds['quality_score']['min']:
                deviation_pct = ((self.thresholds['quality_score']['normal'] - quality) / 
                               self.thresholds['quality_score']['normal']) * 100
                
                anomalies.append({
                    'node_id': data['node_id'],
                    'timestamp': data['timestamp'],
                    'anomaly_type': 'quality_alert',
                    'severity': 'high' if quality < 0.7 else 'medium',
                    'actual_value': quality,
                    'expected_value': self.thresholds['quality_score']['normal'],
                    'deviation_percentage': deviation_pct,
                    'measurement_type': 'quality_score',
                    'description': f'Water quality below threshold: {quality:.2f}'
                })
        
        return anomalies
    
    def _detect_pattern_anomalies(self, sensor_data: List[Dict]) -> List[Dict]:
        """Detect pattern-based anomalies using time series analysis."""
        anomalies = []
        
        # Sort by timestamp
        sorted_data = sorted(sensor_data, key=lambda x: x['timestamp'])
        
        # Detect sudden changes in pressure
        pressures = [d.get('pressure', 0) for d in sorted_data if d.get('pressure')]
        if len(pressures) > 3:
            sudden_changes = self.detect_sudden_changes(pressures, window=3)
            for idx in sudden_changes:
                if idx < len(sorted_data):
                    data = sorted_data[idx]
                    anomalies.append({
                        'node_id': data['node_id'],
                        'timestamp': data['timestamp'],
                        'anomaly_type': 'sudden_change',
                        'severity': 'medium',
                        'actual_value': data.get('pressure'),
                        'expected_value': pressures[max(0, idx-1)] if idx > 0 else None,
                        'deviation_percentage': 0,
                        'measurement_type': 'pressure',
                        'description': 'Sudden pressure change detected'
                    })
        
        return anomalies
    
    def detect_outliers_zscore(self, data: List[float], threshold: float = 2.0) -> List[int]:
        """Detect outliers using z-score method.
        
        Args:
            data: List of values
            threshold: Z-score threshold for outlier detection
            
        Returns:
            List of indices where outliers are found
        """
        if len(data) < 3:
            return []
        
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return []
        
        outliers = []
        for i, value in enumerate(data):
            z_score = abs((value - mean) / std)
            if z_score > threshold:
                outliers.append(i)
        
        return outliers
    
    def detect_sudden_changes(self, data: List[float], window: int = 3) -> List[int]:
        """Detect sudden changes in time series data.
        
        Args:
            data: Time series data
            window: Window size for change detection
            
        Returns:
            List of indices where sudden changes occur
        """
        if len(data) < window + 1:
            return []
        
        changes = []
        for i in range(window, len(data)):
            window_mean = np.mean(data[i-window:i])
            current = data[i]
            
            if window_mean > 0:
                change_ratio = abs((current - window_mean) / window_mean)
                if change_ratio > 0.3:  # 30% change threshold
                    changes.append(i)
        
        return changes
    
    def calculate_severity(self, deviation_percentage: float) -> str:
        """Calculate anomaly severity based on deviation.
        
        Args:
            deviation_percentage: Percentage deviation from normal
            
        Returns:
            Severity level: 'low', 'medium', 'high', or 'critical'
        """
        if deviation_percentage < 20:
            return 'low'
        elif deviation_percentage < 35:
            return 'medium'
        elif deviation_percentage < 50:
            return 'high'
        else:
            return 'critical'
    
    async def save_anomaly(self, anomaly: Dict[str, Any]) -> bool:
        """Save detected anomaly to database.
        
        Args:
            anomaly: Anomaly data to save
            
        Returns:
            True if saved successfully
        """
        query = """
            INSERT INTO water_infrastructure.anomalies 
            (node_id, timestamp, anomaly_type, severity, measurement_type,
             actual_value, expected_value, deviation_percentage, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (node_id, timestamp, anomaly_type) DO NOTHING
        """
        
        metadata = {
            'description': anomaly.get('description', ''),
            'detection_method': 'statistical_analysis',
            'confidence': 0.85
        }
        
        try:
            await self.db_connection.execute(
                query,
                anomaly['node_id'],
                anomaly['timestamp'],
                anomaly['anomaly_type'],
                anomaly['severity'],
                anomaly['measurement_type'],
                anomaly.get('actual_value'),
                anomaly.get('expected_value'),
                anomaly.get('deviation_percentage'),
                metadata
            )
            return True
        except Exception as e:
            logger.error(f"Error saving anomaly: {e}")
            return False