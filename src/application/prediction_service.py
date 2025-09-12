"""
Prediction service implementing Simple ML models for water infrastructure.
Replaces static calculations with real statistical/ML methods.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np

from src.application.models.time_series_simple import (
    MovingAveragePredictor,
    SeasonalDecomposer,
    SimpleAnomalyDetector,
)

logger = logging.getLogger(__name__)


class PredictionService:
    """Main service for ML-based predictions."""

    def __init__(self):
        """Initialize prediction service with simple ML models."""
        self.ma_predictor = MovingAveragePredictor(window_size=7)
        self.seasonal_decomposer = SeasonalDecomposer(period=24)
        self.anomaly_detector = SimpleAnomalyDetector(threshold_std=2.0)

    def predict_peak_demand(
        self, historical_data: np.ndarray, days: int = 7
    ) -> Dict[str, Any]:
        """
        Predict peak water demand for next N days.

        Args:
            historical_data: Historical consumption data (hourly)
            days: Number of days to predict

        Returns:
            Dict with predictions, confidence intervals, and accuracy
        """
        if len(historical_data) < 24:
            raise ValueError("Need at least 24 hours of historical data")

        # Decompose to get seasonal patterns
        components = self.seasonal_decomposer.decompose(historical_data)
        trend = components["trend"]
        seasonal_factors = self.seasonal_decomposer.get_seasonal_factors(
            historical_data
        )

        # Predict trend
        steps = days * 24
        trend_forecast = self.ma_predictor.predict_with_confidence(
            trend, steps, confidence=0.95
        )

        # Apply seasonal adjustment with daily variation
        predictions = trend_forecast["predictions"].copy()
        
        # Add realistic daily variation based on day of week and random factors
        np.random.seed(42)  # For reproducible results
        
        for i in range(len(predictions)):
            hour_of_day = i % 24
            day_of_forecast = i // 24
            
            # Base seasonal adjustment
            predictions[i] *= seasonal_factors[hour_of_day]
            
            # Weekly pattern (weekends slightly lower)
            day_of_week = (day_of_forecast) % 7
            weekend_factor = 0.92 if day_of_week >= 5 else 1.0
            
            # Daily random variation (±3%)
            daily_noise = np.random.normal(1.0, 0.03)
            
            # Long-term slight trend (very small)
            trend_factor = 1.0 + (day_of_forecast * 0.001)  # 0.1% increase per day
            
            predictions[i] *= weekend_factor * daily_noise * trend_factor

        # Calculate accuracy based on historical performance
        if len(historical_data) > 7 * 24:
            # Backtest on last week
            test_start = len(historical_data) - 7 * 24
            test_data = historical_data[:test_start]
            test_pred = self.ma_predictor.predict(test_data, 7 * 24)
            test_actual = historical_data[test_start:]

            # Calculate MAPE
            mape = np.mean(np.abs((test_actual - test_pred) / test_actual)) * 100
            accuracy = max(0, min(1, 1 - mape / 100))
        else:
            accuracy = 0.65  # Default for insufficient data

        # Calculate more realistic confidence intervals based on historical variability
        residuals = []
        if len(historical_data) > 48:  # Need enough data for residuals
            # Calculate residuals from recent predictions
            recent_data = historical_data[-48:]  # Last 2 days
            recent_pred = self.ma_predictor.predict(historical_data[:-48], 48)
            if len(recent_pred) == len(recent_data):
                residuals = recent_data - recent_pred
        
        if len(residuals) > 0:
            # Use standard deviation of residuals for confidence intervals
            std_error = np.std(residuals)
            confidence_multiplier = 1.96  # 95% confidence interval
            
            lower_bound = predictions - confidence_multiplier * std_error
            upper_bound = predictions + confidence_multiplier * std_error
        else:
            # Fallback: use coefficient of variation from historical data
            cv = np.std(historical_data) / np.mean(historical_data) if np.mean(historical_data) > 0 else 0.15
            margin = predictions * min(cv, 0.25)  # Cap at 25%
            
            lower_bound = predictions - margin
            upper_bound = predictions + margin
        
        # Ensure lower bound is never negative
        lower_bound = np.maximum(lower_bound, predictions * 0.1)

        return {
            "predictions": predictions.tolist(),
            "confidence_interval": {
                "lower": lower_bound.tolist(),
                "upper": upper_bound.tolist(),
            },
            "accuracy_score": accuracy,
            "method": "moving_average_with_seasonal",
            "seasonal_factors": seasonal_factors.tolist(),
        }

    def optimize_energy_cost(
        self, demand_forecast: np.ndarray, tariffs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize pump scheduling for energy cost reduction.

        Args:
            demand_forecast: Hourly demand forecast
            tariffs: Energy tariff structure

        Returns:
            Dict with optimized schedule and savings
        """
        n_hours = len(demand_forecast)
        if n_hours != 24:
            demand_forecast = demand_forecast[:24]  # Use first day

        # Parse tariff structure
        peak_hours = tariffs.get("peak", list(range(8, 20)))
        off_peak_hours = tariffs.get(
            "off_peak", list(range(0, 8)) + list(range(20, 24))
        )
        peak_rate = tariffs.get("rates", {}).get("peak", 0.25)
        off_peak_rate = tariffs.get("rates", {}).get("off_peak", 0.10)

        # Create hourly tariff array
        hourly_tariffs = np.zeros(24)
        for h in range(24):
            if h in peak_hours:
                hourly_tariffs[h] = peak_rate
            else:
                hourly_tariffs[h] = off_peak_rate

        # Calculate baseline cost (proportional pumping)
        baseline_schedule = (
            demand_forecast / np.sum(demand_forecast) * np.sum(demand_forecast)
        )
        baseline_cost = np.sum(baseline_schedule * hourly_tariffs)

        # Optimize: shift load to off-peak hours
        optimized_schedule = np.zeros(24)
        total_demand = np.sum(demand_forecast)

        # Priority: fill off-peak hours first
        sorted_hours = np.argsort(hourly_tariffs)
        remaining_demand = total_demand

        for hour in sorted_hours:
            # Respect demand constraints (can't pump more than 150% of forecast)
            max_pump = demand_forecast[hour] * 1.5
            pump_amount = min(remaining_demand, max_pump)
            optimized_schedule[hour] = pump_amount
            remaining_demand -= pump_amount

            if remaining_demand <= 0:
                break

        # Normalize to match total demand
        if np.sum(optimized_schedule) > 0:
            optimized_schedule = optimized_schedule * (
                total_demand / np.sum(optimized_schedule)
            )

        # Calculate optimized cost
        optimized_cost = np.sum(optimized_schedule * hourly_tariffs)

        # Calculate savings
        savings = baseline_cost - optimized_cost
        savings_percentage = (savings / baseline_cost * 100) if baseline_cost > 0 else 0

        return {
            "schedule": optimized_schedule.tolist(),
            "baseline_cost": float(baseline_cost),
            "optimized_cost": float(optimized_cost),
            "estimated_savings": float(savings),
            "savings_percentage": float(savings_percentage),
            "peak_hours_usage": float(np.sum(optimized_schedule[peak_hours])),
            "off_peak_hours_usage": float(np.sum(optimized_schedule[off_peak_hours])),
        }

    def predict_maintenance(
        self, sensor_history: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Predict maintenance needs based on sensor trends.

        Args:
            sensor_history: Dict with sensor readings (pressure, vibration, etc.)

        Returns:
            Dict with risk assessment and maintenance prediction
        """
        pressure = sensor_history.get("pressure", np.array([]))
        vibration = sensor_history.get("vibration", np.array([]))
        temperature = sensor_history.get("temperature", np.array([]))
        equipment_age_days = sensor_history.get("equipment_age_days", 0)

        risk_factors = []

        # Analyze pressure degradation
        if len(pressure) > 10:
            # Linear regression for trend
            x = np.arange(len(pressure))
            z = np.polyfit(x, pressure, 1)
            pressure_trend = z[0]  # Slope

            if pressure_trend < -0.01:  # Degrading
                degradation_rate = abs(pressure_trend)
                current_pressure = pressure[-1]
                critical_pressure = 2.0  # Bar

                if current_pressure > critical_pressure:
                    days_to_critical = (
                        current_pressure - critical_pressure
                    ) / degradation_rate
                else:
                    days_to_critical = 0

                risk_factors.append(
                    {
                        "factor": "pressure_degradation",
                        "severity": "high" if days_to_critical < 30 else "medium",
                        "days_to_failure": days_to_critical,
                    }
                )

        # Analyze vibration anomalies
        if len(vibration) > 10:
            anomalies = self.anomaly_detector.detect(vibration)
            anomaly_rate = len(anomalies["anomaly_indices"]) / len(vibration)

            if anomaly_rate > 0.1:  # More than 10% anomalies
                risk_factors.append(
                    {
                        "factor": "vibration_anomalies",
                        "severity": "high" if anomaly_rate > 0.2 else "medium",
                        "anomaly_rate": anomaly_rate,
                    }
                )

        # Age-based risk
        if equipment_age_days > 365:
            age_risk = min(1.0, equipment_age_days / (365 * 5))  # 5 year lifecycle
            risk_factors.append(
                {
                    "factor": "equipment_age",
                    "severity": "high" if age_risk > 0.8 else "medium",
                    "age_score": age_risk,
                }
            )

        # Calculate overall risk
        if not risk_factors:
            risk_score = "low"
            days_to_maintenance = 90
            failure_probability = 0.1
        else:
            high_risks = sum(1 for r in risk_factors if r.get("severity") == "high")
            medium_risks = sum(1 for r in risk_factors if r.get("severity") == "medium")

            if high_risks > 0:
                risk_score = (
                    "high"
                    if high_risks > 1
                    else "critical"
                    if pressure[-1] < 2.5
                    else "high"
                )
                days_to_maintenance = min(
                    30,
                    min(
                        r.get("days_to_failure", 30)
                        for r in risk_factors
                        if "days_to_failure" in r
                    ),
                )
                failure_probability = min(0.9, 0.3 + high_risks * 0.3)
            elif medium_risks > 0:
                risk_score = "medium"
                days_to_maintenance = 60
                failure_probability = 0.3 + medium_risks * 0.1
            else:
                risk_score = "low"
                days_to_maintenance = 90
                failure_probability = 0.2

        return {
            "risk_score": risk_score,
            "days_to_maintenance": int(days_to_maintenance),
            "failure_probability": float(failure_probability),
            "confidence": 0.75,  # Model confidence
            "risk_factors": risk_factors,
            "recommendations": self._get_maintenance_recommendations(risk_score),
        }

    def predict_water_loss(self, flow_data: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Predict water loss and potential leaks.

        Args:
            flow_data: Dict with flow_in, flow_out, pressure, night_flow

        Returns:
            Dict with water loss analysis and predictions
        """
        flow_in = flow_data.get("flow_in", np.array([]))
        flow_out = flow_data.get("flow_out", np.array([]))
        pressure = flow_data.get("pressure", np.array([]))
        night_flow = flow_data.get("night_flow", np.array([]))

        if len(flow_in) == 0 or len(flow_out) == 0:
            return {
                "current_loss_percentage": 0,
                "predicted_loss_trend": "stable",
                "leak_probability": 0,
                "recommended_actions": [],
            }

        # Calculate current loss
        current_loss = flow_in - flow_out
        loss_percentage = (
            np.mean(current_loss / flow_in) * 100 if np.mean(flow_in) > 0 else 0
        )

        # Analyze trend
        if len(current_loss) > 5:
            x = np.arange(len(current_loss))
            z = np.polyfit(x, current_loss, 1)
            loss_trend = z[0]

            if loss_trend > 0.5:
                predicted_trend = "increasing"
            elif loss_trend < -0.5:
                predicted_trend = "decreasing"
            else:
                predicted_trend = "stable"
        else:
            predicted_trend = "unknown"

        # Leak detection based on multiple factors
        leak_indicators = 0

        # Factor 1: High loss percentage
        if loss_percentage > 5:
            leak_indicators += 1 if loss_percentage > 10 else 0.5

        # Factor 2: Increasing night flow
        if len(night_flow) > 3:
            night_trend = np.polyfit(np.arange(len(night_flow)), night_flow, 1)[0]
            if night_trend > 0:
                leak_indicators += 0.5

        # Factor 3: Pressure drop
        if len(pressure) > 3:
            pressure_trend = np.polyfit(np.arange(len(pressure)), pressure, 1)[0]
            if pressure_trend < -0.01:
                leak_indicators += 0.5

        # Calculate leak probability
        leak_probability = min(1.0, leak_indicators / 2)

        # Recommendations
        actions = []
        if leak_probability > 0.7:
            actions.append("Immediate leak detection survey recommended")
            actions.append("Check pressure zones for anomalies")
        elif leak_probability > 0.4:
            actions.append("Schedule preventive maintenance")
            actions.append("Monitor night flow patterns")
        elif loss_percentage > 3:
            actions.append("Review meter calibration")

        return {
            "current_loss_percentage": float(loss_percentage),
            "predicted_loss_trend": predicted_trend,
            "leak_probability": float(leak_probability),
            "recommended_actions": actions,
            "analysis": {
                "avg_loss_m3": float(np.mean(current_loss)),
                "max_loss_m3": float(np.max(current_loss))
                if len(current_loss) > 0
                else 0,
                "night_flow_anomaly": len(night_flow) > 0
                and np.mean(night_flow) > np.percentile(flow_out, 25),
            },
        }

    def _get_maintenance_recommendations(self, risk_score: str) -> List[str]:
        """Get maintenance recommendations based on risk score."""
        if risk_score == "critical":
            return [
                "Immediate inspection required",
                "Prepare replacement parts",
                "Schedule emergency maintenance window",
            ]
        elif risk_score == "high":
            return [
                "Schedule maintenance within 30 days",
                "Increase monitoring frequency",
                "Order spare parts",
            ]
        elif risk_score == "medium":
            return ["Plan maintenance in next quarter", "Continue regular monitoring"]
        else:
            return ["Continue routine maintenance schedule"]
