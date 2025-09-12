"""
Simple time series models for ML predictions.
Implements statistical methods without heavy ML dependencies.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy import signal, stats


class MovingAveragePredictor:
    """Weighted moving average predictor for time series."""

    def __init__(self, window_size: int = 7):
        """
        Initialize moving average predictor.

        Args:
            window_size: Number of periods for moving average
        """
        self.window_size = window_size
        self._generate_weights()

    def _generate_weights(self):
        """Generate exponentially decaying weights for recent data."""
        weights = np.exp(np.linspace(-1, 0, self.window_size))
        self.weights = weights / weights.sum()

    def predict(self, data: np.ndarray, steps: int = 1) -> np.ndarray:
        """
        Predict future values using weighted moving average.

        Args:
            data: Historical data
            steps: Number of steps ahead to predict

        Returns:
            Array of predictions
        """
        if len(data) < self.window_size:
            # Use simple average if not enough data
            return np.array([np.mean(data)] * steps)

        predictions = []
        current_data = data.copy()

        for _ in range(steps):
            # Use last window_size points with weights
            window = current_data[-self.window_size :]
            pred = np.sum(window * self.weights)
            predictions.append(pred)

            # Append prediction for next step
            current_data = np.append(current_data, pred)

        return np.array(predictions)

    def predict_with_confidence(
        self, data: np.ndarray, steps: int = 1, confidence: float = 0.95
    ) -> Dict[str, np.ndarray]:
        """
        Predict with confidence intervals.

        Args:
            data: Historical data
            steps: Number of steps ahead
            confidence: Confidence level (0-1)

        Returns:
            Dict with predictions and confidence bounds
        """
        predictions = self.predict(data, steps)

        # Calculate historical error
        if len(data) > self.window_size * 2:
            errors = []
            for i in range(self.window_size, len(data)):
                window = data[i - self.window_size : i]
                pred = np.sum(window * self.weights)
                errors.append(data[i] - pred)

            std_error = np.std(errors)
            z_score = stats.norm.ppf((1 + confidence) / 2)

            lower = predictions - z_score * std_error
            upper = predictions + z_score * std_error
        else:
            # Fallback to simple bounds
            std = np.std(data)
            lower = predictions - 2 * std
            upper = predictions + 2 * std

        return {
            "predictions": predictions,
            "lower_bound": lower,
            "upper_bound": upper,
            "confidence": confidence,
        }


class SeasonalDecomposer:
    """Extract seasonal patterns from time series data."""

    def __init__(self, period: int = 24):
        """
        Initialize seasonal decomposer.

        Args:
            period: Seasonal period (e.g., 24 for daily pattern in hourly data)
        """
        self.period = period

    def decompose(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Decompose time series into trend, seasonal, and residual.

        Args:
            data: Time series data

        Returns:
            Dict with trend, seasonal, and residual components
        """
        n = len(data)

        # Extract trend using moving average
        trend = self._extract_trend(data)

        # Remove trend
        detrended = data - trend

        # Extract seasonal pattern
        seasonal = self._extract_seasonal(detrended)

        # Calculate residual
        residual = data - trend - seasonal

        return {
            "trend": trend,
            "seasonal": seasonal,
            "residual": residual,
            "original": data,
        }

    def _extract_trend(self, data: np.ndarray) -> np.ndarray:
        """Extract trend using centered moving average."""
        n = len(data)
        trend = np.zeros(n)
        half_period = self.period // 2

        for i in range(n):
            start = max(0, i - half_period)
            end = min(n, i + half_period + 1)
            trend[i] = np.mean(data[start:end])

        return trend

    def _extract_seasonal(self, detrended: np.ndarray) -> np.ndarray:
        """Extract seasonal pattern by averaging over periods."""
        n = len(detrended)
        seasonal_pattern = np.zeros(self.period)
        counts = np.zeros(self.period)

        # Average values at each position in the period
        for i in range(n):
            pos = i % self.period
            seasonal_pattern[pos] += detrended[i]
            counts[pos] += 1

        # Avoid division by zero
        counts[counts == 0] = 1
        seasonal_pattern = seasonal_pattern / counts

        # Center the pattern
        seasonal_pattern -= np.mean(seasonal_pattern)

        # Repeat pattern to match data length
        seasonal = np.tile(seasonal_pattern, n // self.period + 1)[:n]

        return seasonal

    def get_seasonal_factors(self, data: np.ndarray) -> np.ndarray:
        """
        Get multiplicative seasonal factors.

        Args:
            data: Time series data

        Returns:
            Array of seasonal factors (one per period position)
        """
        components = self.decompose(data)
        seasonal = components["seasonal"]
        trend = components["trend"]

        # Avoid division by zero
        trend[trend == 0] = 1

        # Calculate multiplicative factors
        factors = np.zeros(self.period)
        for i in range(self.period):
            indices = np.arange(i, len(data), self.period)
            if len(indices) > 0:
                ratios = (trend[indices] + seasonal[indices]) / trend[indices]
                factors[i] = np.mean(ratios)

        # Normalize factors
        factors = factors / np.mean(factors)

        return factors


class SimpleAnomalyDetector:
    """Simple statistical anomaly detection."""

    def __init__(self, threshold_std: float = 2.0):
        """
        Initialize anomaly detector.

        Args:
            threshold_std: Number of standard deviations for anomaly threshold
        """
        self.threshold_std = threshold_std

    def detect(self, data: np.ndarray, detrend: bool = False) -> Dict[str, np.ndarray]:
        """
        Detect anomalies using statistical thresholds.

        Args:
            data: Time series data
            detrend: Whether to remove trend before detection

        Returns:
            Dict with anomaly indices and scores
        """
        if detrend:
            # Remove linear trend
            processed_data = signal.detrend(data, type="linear")
        else:
            processed_data = data.copy()

        # Calculate rolling statistics
        window = min(24, len(data) // 4)
        anomaly_scores = np.zeros(len(data))
        anomaly_indices = []

        for i in range(len(data)):
            # Get local window
            start = max(0, i - window // 2)
            end = min(len(data), i + window // 2)
            window_data = processed_data[start:end]

            if len(window_data) > 1:
                # Calculate z-score
                mean = np.mean(window_data)
                std = np.std(window_data)
                if std > 0:
                    z_score = abs(processed_data[i] - mean) / std
                    anomaly_scores[i] = z_score

                    if z_score > self.threshold_std:
                        anomaly_indices.append(i)

        return {
            "anomaly_indices": anomaly_indices,
            "anomaly_scores": anomaly_scores,
            "threshold": self.threshold_std,
        }

    def detect_change_points(self, data: np.ndarray) -> List[int]:
        """
        Detect points where statistical properties change.

        Args:
            data: Time series data

        Returns:
            List of change point indices
        """
        change_points = []
        window = min(24, len(data) // 10)

        for i in range(window, len(data) - window):
            # Compare statistics before and after
            before = data[i - window : i]
            after = data[i : i + window]

            # T-test for mean change
            t_stat, p_value = stats.ttest_ind(before, after)

            # F-test for variance change
            f_stat = np.var(after) / np.var(before) if np.var(before) > 0 else 1

            # Detect significant changes
            if p_value < 0.01 or f_stat > 2 or f_stat < 0.5:
                change_points.append(i)

        # Remove consecutive change points
        if change_points:
            filtered = [change_points[0]]
            for cp in change_points[1:]:
                if cp - filtered[-1] > window // 2:
                    filtered.append(cp)
            change_points = filtered

        return change_points
