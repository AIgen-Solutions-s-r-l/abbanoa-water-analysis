"""Domain service for anomaly detection in sensor readings."""

from datetime import datetime
from typing import List, Optional, Tuple

import numpy as np

from src.domain.entities.sensor_reading import SensorReading
from src.domain.events.sensor_events import AnomalyDetectedEvent, ThresholdExceededEvent


class AnomalyDetectionService:
    """Service for detecting anomalies in water infrastructure sensor data."""

    def __init__(
        self,
        z_score_threshold: float = 2.5,
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

        # Group readings by measurement type, safely extracting values
        flow_rates = []
        for r in readings:
            if r.flow_rate is not None:
                try:
                    value = (
                        r.flow_rate.value
                        if hasattr(r.flow_rate, "value")
                        else float(r.flow_rate)
                    )
                    flow_rates.append((r.timestamp, value))
                except (ValueError, TypeError):
                    continue

        pressures = []
        for r in readings:
            if r.pressure is not None:
                try:
                    value = (
                        r.pressure.value
                        if hasattr(r.pressure, "value")
                        else float(r.pressure)
                    )
                    pressures.append((r.timestamp, value))
                except (ValueError, TypeError):
                    continue

        temperatures = []
        for r in readings:
            if r.temperature is not None:
                try:
                    value = (
                        r.temperature.value
                        if hasattr(r.temperature, "value")
                        else float(r.temperature)
                    )
                    temperatures.append((r.timestamp, value))
                except (ValueError, TypeError):
                    continue

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

        # Apply final deduplication across all measurement types
        # Keep only the most severe anomaly per timestamp (rounded to minute)
        deduplicated_anomalies = self._deduplicate_by_timestamp(anomalies)

        return deduplicated_anomalies

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
        seen_anomalies = set()  # To deduplicate similar anomalies

        for timestamp, value in time_series:
            z_score = abs((value - mean) / std)

            if z_score > self.z_score_threshold:
                # Create a key to identify duplicate anomalies (same value, same minute)
                minute_key = (
                    timestamp.replace(second=0, microsecond=0),  # Round to minute
                    round(value, 1),  # Round value to 1 decimal
                    measurement_type,
                )

                # Skip if we've already seen this anomaly
                if minute_key in seen_anomalies:
                    continue

                seen_anomalies.add(minute_key)

                severity = self._calculate_severity(z_score)
                anomaly = AnomalyDetectedEvent(
                    node_id=node_id,
                    sensor_type=measurement_type,
                    anomaly_type="statistical_outlier",
                    severity=severity,
                    measurement_value=value,
                    threshold=mean + (self.z_score_threshold * std),
                    description=f"Value {value} deviates {z_score:.2f} standard deviations from mean {mean:.2f}",
                    timestamp=timestamp,
                )
                anomalies.append(anomaly)

        # Also detect rapid changes (rate-of-change anomalies)
        rate_anomalies = self._detect_rate_of_change_anomalies(
            time_series, measurement_type, node_id
        )
        anomalies.extend(rate_anomalies)

        # Sort by severity and deviation magnitude (most severe first)
        anomalies.sort(
            key=lambda a: (
                {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(a.severity, 4),
                -abs(a.measurement_value - mean),  # Most extreme values first
            )
        )

        # Return all anomalies (no artificial limit for better monitoring)
        return anomalies

    def _detect_rate_of_change_anomalies(
        self,
        time_series: List[Tuple[datetime, float]],
        measurement_type: str,
        node_id: any,
    ) -> List[AnomalyDetectedEvent]:
        """Detect anomalies based on rapid rate of change."""
        if len(time_series) < 3:
            return []

        # Sort by timestamp to ensure proper order
        time_series.sort(key=lambda x: x[0])

        # Calculate rate of change between consecutive points
        rate_changes = []
        for i in range(1, len(time_series)):
            prev_time, prev_value = time_series[i - 1]
            curr_time, curr_value = time_series[i]

            # Calculate rate per hour
            time_diff = (curr_time - prev_time).total_seconds() / 3600
            if time_diff > 0:
                rate = abs(curr_value - prev_value) / time_diff
                rate_changes.append((curr_time, curr_value, rate))

        if not rate_changes:
            return []

        # Detect anomalous rate changes
        rates = [r for _, _, r in rate_changes]
        rate_mean = np.mean(rates)
        rate_std = np.std(rates)

        if rate_std == 0:
            return []

        anomalies = []
        for timestamp, value, rate in rate_changes:
            z_score = abs((rate - rate_mean) / rate_std)

            # Use a lower threshold for rate anomalies (2.0 instead of 2.5)
            if z_score > 2.0:
                severity = "high" if z_score > 3.0 else "medium"
                anomaly = AnomalyDetectedEvent(
                    node_id=node_id,
                    sensor_type=measurement_type,
                    anomaly_type="rapid_change",
                    severity=severity,
                    measurement_value=value,
                    threshold=rate_mean + (2.0 * rate_std),
                    description=f"Rapid change detected: {rate:.2f} units/hour (z-score: {z_score:.2f})",
                    timestamp=timestamp,
                )
                anomalies.append(anomaly)

        return anomalies

    def _calculate_severity(self, z_score: float) -> str:
        """Calculate anomaly severity based on z-score."""
        if z_score >= 4:
            return "critical"
        elif z_score >= 3:
            return "high"
        elif z_score >= 2.5:
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
            try:
                flow_val = (
                    reading.flow_rate.value
                    if hasattr(reading.flow_rate, "value")
                    else float(reading.flow_rate)
                )
                if flow_val < min_flow:
                    event = ThresholdExceededEvent(
                        node_id=reading.node_id,
                        measurement_type="flow_rate",
                        current_value=flow_val,
                        threshold_value=min_flow,
                        threshold_type="lower",
                    )
                    events.append(event)
                elif flow_val > max_flow:
                    event = ThresholdExceededEvent(
                        node_id=reading.node_id,
                        measurement_type="flow_rate",
                        current_value=flow_val,
                        threshold_value=max_flow,
                        threshold_type="upper",
                    )
                    events.append(event)
            except (ValueError, TypeError):
                pass

        if reading.pressure and pressure_limits:
            min_pressure, max_pressure = pressure_limits
            try:
                pressure_val = (
                    reading.pressure.value
                    if hasattr(reading.pressure, "value")
                    else float(reading.pressure)
                )
                if pressure_val < min_pressure:
                    event = ThresholdExceededEvent(
                        node_id=reading.node_id,
                        measurement_type="pressure",
                        current_value=pressure_val,
                        threshold_value=min_pressure,
                        threshold_type="lower",
                    )
                    events.append(event)
                elif pressure_val > max_pressure:
                    event = ThresholdExceededEvent(
                        node_id=reading.node_id,
                        measurement_type="pressure",
                        current_value=pressure_val,
                        threshold_value=max_pressure,
                        threshold_type="upper",
                    )
                    events.append(event)
            except (ValueError, TypeError):
                pass

        if reading.temperature and temperature_limits:
            min_temp, max_temp = temperature_limits
            try:
                temp_val = (
                    reading.temperature.value
                    if hasattr(reading.temperature, "value")
                    else float(reading.temperature)
                )
                if temp_val < min_temp:
                    event = ThresholdExceededEvent(
                        node_id=reading.node_id,
                        measurement_type="temperature",
                        current_value=temp_val,
                        threshold_value=min_temp,
                        threshold_type="lower",
                    )
                    events.append(event)
                elif temp_val > max_temp:
                    event = ThresholdExceededEvent(
                        node_id=reading.node_id,
                        measurement_type="temperature",
                        current_value=temp_val,
                        threshold_value=max_temp,
                        threshold_type="upper",
                    )
                    events.append(event)
            except (ValueError, TypeError):
                pass

        return events

    def _deduplicate_by_timestamp(
        self, anomalies: List[AnomalyDetectedEvent]
    ) -> List[AnomalyDetectedEvent]:
        """Deduplicate anomalies by timestamp, keeping the most severe one per minute."""
        if not anomalies:
            return []

        # Group anomalies by timestamp (rounded to minute)
        timestamp_groups = {}
        for anomaly in anomalies:
            timestamp_key = anomaly.occurred_at.replace(second=0, microsecond=0)
            if timestamp_key not in timestamp_groups:
                timestamp_groups[timestamp_key] = []
            timestamp_groups[timestamp_key].append(anomaly)

        # For each timestamp, keep only the most severe anomaly
        deduplicated_anomalies = []
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        for timestamp, group_anomalies in timestamp_groups.items():
            # Sort by severity (most severe first), then by deviation magnitude
            group_anomalies.sort(
                key=lambda a: (
                    severity_order.get(a.severity, 4),
                    (
                        -abs(a.measurement_value - a.threshold)
                        if a.measurement_value is not None and a.threshold is not None
                        else 0
                    ),
                )
            )

            # Take the most severe anomaly
            best_anomaly = group_anomalies[0]

            # Enhance description to mention if multiple measurement types were affected
            if len(group_anomalies) > 1:
                measurement_types = [a.sensor_type for a in group_anomalies]
                best_anomaly.description = f"{best_anomaly.description} (Multiple measurements affected: {', '.join(measurement_types)})"

            deduplicated_anomalies.append(best_anomaly)

        # Sort final result by timestamp (newest first)
        deduplicated_anomalies.sort(key=lambda a: a.occurred_at, reverse=True)

        return deduplicated_anomalies
