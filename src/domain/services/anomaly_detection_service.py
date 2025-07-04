"""Domain service for anomaly detection in sensor readings."""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import numpy as np

from src.domain.entities.sensor_reading import SensorReading
from src.domain.events.sensor_events import AnomalyDetectedEvent, ThresholdExceededEvent
from src.domain.value_objects.measurements import FlowRate, Pressure, Temperature


class AnomalyDetectionService:
    """Service for detecting anomalies in water infrastructure sensor data."""

    def __init__(
        self,
        z_score_threshold: float = 3.0,
        min_data_points: int = 10,
        rolling_window_hours: int = 24,
    ) -> None:
        self.z_score_threshold = z_score_threshold
        self.min_data_points = min_data_points
        self.rolling_window_hours = rolling_window_hours

    def detect_anomalies(
        self, readings: List[SensorReading], reference_time: Optional[datetime] = None
    ) -> List[AnomalyDetectedEvent]:
        """Detect anomalies in a list of sensor readings."""
        if len(readings) < self.min_data_points:
            return []

        reference_time = reference_time or datetime.utcnow()
        anomalies = []

        # Group readings by measurement type
        flow_rates = [(r.timestamp, r.flow_rate.value) for r in readings if r.flow_rate]
        pressures = [(r.timestamp, r.pressure.value) for r in readings if r.pressure]
        temperatures = [
            (r.timestamp, r.temperature.value) for r in readings if r.temperature
        ]

        # Detect anomalies for each measurement type
        if flow_rates:
            flow_anomalies = self._detect_statistical_anomalies(
                flow_rates, "flow_rate", readings[0].node_id
            )
            anomalies.extend(flow_anomalies)

        if pressures:
            pressure_anomalies = self._detect_statistical_anomalies(
                pressures, "pressure", readings[0].node_id
            )
            anomalies.extend(pressure_anomalies)

        if temperatures:
            temp_anomalies = self._detect_statistical_anomalies(
                temperatures, "temperature", readings[0].node_id
            )
            anomalies.extend(temp_anomalies)

        return anomalies

    def _detect_statistical_anomalies(
        self,
        time_series: List[Tuple[datetime, float]],
        measurement_type: str,
        node_id: any,
    ) -> List[AnomalyDetectedEvent]:
        """Detect statistical anomalies using z-score method."""
        if len(time_series) < self.min_data_points:
            return []

        values = np.array([v for _, v in time_series])
        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return []

        anomalies = []
        for timestamp, value in time_series:
            z_score = abs((value - mean) / std)

            if z_score > self.z_score_threshold:
                severity = self._calculate_severity(z_score)
                anomaly = AnomalyDetectedEvent(
                    aggregate_id=node_id,
                    node_id=node_id,
                    sensor_type=measurement_type,
                    anomaly_type="statistical_outlier",
                    severity=severity,
                    measurement_value=value,
                    threshold=mean + (self.z_score_threshold * std),
                    description=f"Value {value} deviates {z_score:.2f} standard deviations from mean {mean:.2f}",
                )
                anomalies.append(anomaly)

        return anomalies

    def _calculate_severity(self, z_score: float) -> str:
        """Calculate anomaly severity based on z-score."""
        if z_score >= 5:
            return "critical"
        elif z_score >= 4:
            return "high"
        elif z_score >= 3:
            return "medium"
        else:
            return "low"

    def check_thresholds(
        self,
        reading: SensorReading,
        flow_rate_limits: Optional[Tuple[float, float]] = None,
        pressure_limits: Optional[Tuple[float, float]] = None,
        temperature_limits: Optional[Tuple[float, float]] = None,
    ) -> List[ThresholdExceededEvent]:
        """Check if sensor readings exceed configured thresholds."""
        events = []

        if reading.flow_rate and flow_rate_limits:
            min_flow, max_flow = flow_rate_limits
            if reading.flow_rate.value < min_flow:
                event = ThresholdExceededEvent(
                    aggregate_id=reading.node_id,
                    node_id=reading.node_id,
                    measurement_type="flow_rate",
                    current_value=reading.flow_rate.value,
                    threshold_value=min_flow,
                    threshold_type="lower",
                )
                events.append(event)
            elif reading.flow_rate.value > max_flow:
                event = ThresholdExceededEvent(
                    aggregate_id=reading.node_id,
                    node_id=reading.node_id,
                    measurement_type="flow_rate",
                    current_value=reading.flow_rate.value,
                    threshold_value=max_flow,
                    threshold_type="upper",
                )
                events.append(event)

        if reading.pressure and pressure_limits:
            min_pressure, max_pressure = pressure_limits
            if reading.pressure.value < min_pressure:
                event = ThresholdExceededEvent(
                    aggregate_id=reading.node_id,
                    node_id=reading.node_id,
                    measurement_type="pressure",
                    current_value=reading.pressure.value,
                    threshold_value=min_pressure,
                    threshold_type="lower",
                )
                events.append(event)
            elif reading.pressure.value > max_pressure:
                event = ThresholdExceededEvent(
                    aggregate_id=reading.node_id,
                    node_id=reading.node_id,
                    measurement_type="pressure",
                    current_value=reading.pressure.value,
                    threshold_value=max_pressure,
                    threshold_type="upper",
                )
                events.append(event)

        if reading.temperature and temperature_limits:
            min_temp, max_temp = temperature_limits
            if reading.temperature.value < min_temp:
                event = ThresholdExceededEvent(
                    aggregate_id=reading.node_id,
                    node_id=reading.node_id,
                    measurement_type="temperature",
                    current_value=reading.temperature.value,
                    threshold_value=min_temp,
                    threshold_type="lower",
                )
                events.append(event)
            elif reading.temperature.value > max_temp:
                event = ThresholdExceededEvent(
                    aggregate_id=reading.node_id,
                    node_id=reading.node_id,
                    measurement_type="temperature",
                    current_value=reading.temperature.value,
                    threshold_value=max_temp,
                    threshold_type="upper",
                )
                events.append(event)

        return events
