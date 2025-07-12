"""Use case for analyzing water consumption patterns."""

from datetime import datetime
from typing import Dict, List
from uuid import UUID

import numpy as np

from src.application.dto.analysis_results_dto import ConsumptionPatternDTO
from src.application.interfaces.repositories import ISensorReadingRepository
from src.domain.entities.sensor_reading import SensorReading


class AnalyzeConsumptionPatternsUseCase:
    """Use case for analyzing water consumption patterns from sensor readings."""

    def __init__(self, sensor_reading_repository: ISensorReadingRepository) -> None:
        self.sensor_reading_repository = sensor_reading_repository

    async def execute(
        self,
        node_id: UUID,
        start_date: datetime,
        end_date: datetime,
        pattern_type: str = "daily",
    ) -> ConsumptionPatternDTO:
        """Analyze consumption patterns for a specific node and time period."""
        # Validate inputs
        if end_date <= start_date:
            raise ValueError("End date must be after start date")

        if pattern_type not in ["hourly", "daily", "weekly", "monthly"]:
            raise ValueError(f"Invalid pattern type: {pattern_type}")

        # Fetch sensor readings
        readings = await self.sensor_reading_repository.get_by_node_id(
            node_id=node_id, start_time=start_date, end_time=end_date
        )

        if not readings:
            raise ValueError(
                f"No readings found for node {node_id} in the specified period"
            )

        # Analyze patterns based on type
        if pattern_type == "hourly":
            pattern_data = self._analyze_hourly_patterns(readings)
        elif pattern_type == "daily":
            pattern_data = self._analyze_daily_patterns(readings)
        elif pattern_type == "weekly":
            pattern_data = self._analyze_weekly_patterns(readings)
        else:  # monthly
            pattern_data = self._analyze_monthly_patterns(readings)

        # Identify peak and off-peak periods
        peak_hours, off_peak_hours = self._identify_peak_periods(
            pattern_data["average_consumption"]
        )

        # Calculate variability
        variability = self._calculate_variability(pattern_data["all_values"])

        return ConsumptionPatternDTO(
            node_id=node_id,
            pattern_type=pattern_type,
            average_consumption=pattern_data["average_consumption"],
            peak_hours=peak_hours,
            off_peak_hours=off_peak_hours,
            variability_coefficient=variability,
        )

    def _analyze_hourly_patterns(self, readings: List[SensorReading]) -> Dict:
        """Analyze hourly consumption patterns."""
        hourly_data = {}

        for reading in readings:
            if reading.flow_rate:
                hour = reading.timestamp.strftime("%H:00")
                if hour not in hourly_data:
                    hourly_data[hour] = []
                # Handle both value objects and direct float values
                flow_val = (
                    reading.flow_rate.value
                    if hasattr(reading.flow_rate, "value")
                    else reading.flow_rate
                )
                hourly_data[hour].append(float(flow_val))

        average_consumption = {}
        all_values = []

        for hour in sorted(hourly_data.keys()):
            values = hourly_data[hour]
            average_consumption[hour] = round(np.mean(values), 2)
            all_values.extend(values)

        return {"average_consumption": average_consumption, "all_values": all_values}

    def _analyze_daily_patterns(self, readings: List[SensorReading]) -> Dict:
        """Analyze daily consumption patterns."""
        daily_data = {}

        for reading in readings:
            if reading.flow_rate:
                day = reading.timestamp.strftime("%A")
                if day not in daily_data:
                    daily_data[day] = []
                # Handle both value objects and direct float values
                flow_val = (
                    reading.flow_rate.value
                    if hasattr(reading.flow_rate, "value")
                    else reading.flow_rate
                )
                daily_data[day].append(float(flow_val))

        average_consumption = {}
        all_values = []

        days_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for day in days_order:
            if day in daily_data:
                values = daily_data[day]
                average_consumption[day] = round(np.mean(values), 2)
                all_values.extend(values)

        return {"average_consumption": average_consumption, "all_values": all_values}

    def _analyze_weekly_patterns(self, readings: List[SensorReading]) -> Dict:
        """Analyze weekly consumption patterns."""
        weekly_data = {}

        for reading in readings:
            if reading.flow_rate:
                week = reading.timestamp.strftime("Week %U")
                if week not in weekly_data:
                    weekly_data[week] = []
                # Handle both value objects and direct float values
                flow_val = (
                    reading.flow_rate.value
                    if hasattr(reading.flow_rate, "value")
                    else reading.flow_rate
                )
                weekly_data[week].append(float(flow_val))

        average_consumption = {}
        all_values = []

        for week in sorted(weekly_data.keys()):
            values = weekly_data[week]
            average_consumption[week] = round(np.mean(values), 2)
            all_values.extend(values)

        return {"average_consumption": average_consumption, "all_values": all_values}

    def _analyze_monthly_patterns(self, readings: List[SensorReading]) -> Dict:
        """Analyze monthly consumption patterns."""
        monthly_data = {}

        for reading in readings:
            if reading.flow_rate:
                month = reading.timestamp.strftime("%B")
                if month not in monthly_data:
                    monthly_data[month] = []
                # Handle both value objects and direct float values
                flow_val = (
                    reading.flow_rate.value
                    if hasattr(reading.flow_rate, "value")
                    else reading.flow_rate
                )
                monthly_data[month].append(float(flow_val))

        average_consumption = {}
        all_values = []

        months_order = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        for month in months_order:
            if month in monthly_data:
                values = monthly_data[month]
                average_consumption[month] = round(np.mean(values), 2)
                all_values.extend(values)

        return {"average_consumption": average_consumption, "all_values": all_values}

    def _identify_peak_periods(
        self, average_consumption: Dict[str, float]
    ) -> tuple[List[str], List[str]]:
        """Identify peak and off-peak consumption periods."""
        if not average_consumption:
            return [], []

        values = list(average_consumption.values())
        mean_consumption = np.mean(values)
        std_consumption = np.std(values)

        peak_threshold = mean_consumption + (0.5 * std_consumption)
        off_peak_threshold = mean_consumption - (0.5 * std_consumption)

        peak_hours = []
        off_peak_hours = []

        for period, consumption in average_consumption.items():
            if consumption >= peak_threshold:
                peak_hours.append(period)
            elif consumption <= off_peak_threshold:
                off_peak_hours.append(period)

        return peak_hours, off_peak_hours

    def _calculate_variability(self, values: List[float]) -> float:
        """Calculate coefficient of variation for consumption values."""
        if not values:
            return 0.0

        mean_value = np.mean(values)
        if mean_value == 0:
            return 0.0

        std_value = np.std(values)
        cv = (std_value / mean_value) * 100

        return round(cv, 2)
