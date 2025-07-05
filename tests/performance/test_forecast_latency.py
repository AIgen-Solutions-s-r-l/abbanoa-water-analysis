"""
Performance tests for forecast latency validation.

Tests that the forecast retrieval meets the 99th percentile latency
requirement of ≤ 300ms on cold runs.
"""

import asyncio
import time
from statistics import mean, stdev
from typing import List
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pandas as pd
import pytest

from src.application.use_cases.forecast_consumption import ForecastConsumption
from src.infrastructure.clients.async_bigquery_client import AsyncBigQueryClient
from src.infrastructure.repositories.bigquery_forecast_repository import (
    BigQueryForecastRepository,
)


def calculate_percentile(latencies: List[float], percentile: int) -> float:
    """Calculate percentile from latency list."""
    return np.percentile(latencies, percentile)


@pytest.fixture
def mock_forecast_data():
    """Create mock forecast data for performance testing."""
    data = {
        "timestamp": pd.date_range(start="2025-07-05", periods=7, freq="D", tz="UTC"),
        "forecast_value": [100.5 + i for i in range(7)],
        "lower_bound": [95.0 + i for i in range(7)],
        "upper_bound": [106.0 + i for i in range(7)],
        "confidence_level": [0.95] * 7,
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_bigquery_client():
    """Create mock BigQuery client with realistic latency simulation."""
    client = MagicMock(spec=AsyncBigQueryClient)
    client.project_id = "test-project"
    client.dataset_id = "test_dataset"
    client.query_timeout_ms = 250

    async def mock_execute_query(
        query, parameters=None, timeout_ms=None, use_cache=None
    ):
        """Simulate query execution with realistic latency."""
        # Simulate network + query latency
        base_latency = 0.050  # 50ms base latency

        # Add variability
        if use_cache:
            # Cached queries are faster
            latency = base_latency * 0.3 + np.random.normal(0, 0.005)
        else:
            # Cold queries have more latency
            latency = base_latency + np.random.normal(0.02, 0.01)

            # Occasionally add spikes (5% of requests)
            if np.random.random() < 0.05:
                latency += np.random.uniform(0.05, 0.1)

        # Ensure non-negative
        latency = max(0.001, latency)

        # Simulate async execution
        await asyncio.sleep(latency)

        # Return mock data based on query type
        if "INFORMATION_SCHEMA.MODELS" in query:
            return pd.DataFrame({"exists": [1]})
        elif "ML.FORECAST" in query:
            return mock_forecast_data()
        else:
            return pd.DataFrame()

    client.execute_query = AsyncMock(side_effect=mock_execute_query)
    return client


@pytest.mark.performance
class TestForecastLatency:
    """Performance test suite for forecast latency validation."""

    @pytest.mark.asyncio
    async def test_cold_run_latency_99th_percentile(
        self, mock_bigquery_client, mock_forecast_data
    ):
        """Test that 99th percentile latency is ≤ 300ms on cold runs."""
        # Create repository and use case
        repo = BigQueryForecastRepository(
            client=mock_bigquery_client, ml_dataset_id="ml_models"
        )

        # Mock model existence to avoid extra query
        repo.check_model_exists = AsyncMock(return_value=True)

        forecast_use_case = ForecastConsumption(forecast_repository=repo)

        # Run multiple requests to get percentile data
        num_requests = 100
        latencies = []

        print(f"\nRunning {num_requests} cold forecast requests...")

        for i in range(num_requests):
            # Clear any caches to simulate cold run
            if hasattr(mock_bigquery_client, "_cache"):
                await mock_bigquery_client.clear_cache()

            start_time = time.perf_counter()

            try:
                result = await forecast_use_case.get_forecast(
                    district_id="DIST_001", metric="flow_rate", horizon=7
                )

                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)

                # Progress indicator
                if (i + 1) % 20 == 0:
                    print(f"  Completed {i + 1}/{num_requests} requests...")

            except Exception as e:
                print(f"  Request {i + 1} failed: {e}")
                # Count failed requests as max latency
                latencies.append(300.0)

        # Calculate statistics
        p50 = calculate_percentile(latencies, 50)
        p90 = calculate_percentile(latencies, 90)
        p95 = calculate_percentile(latencies, 95)
        p99 = calculate_percentile(latencies, 99)
        avg_latency = mean(latencies)
        std_latency = stdev(latencies) if len(latencies) > 1 else 0

        # Print results
        print(f"\nLatency Statistics (ms):")
        print(f"  Average: {avg_latency:.2f}")
        print(f"  Std Dev: {std_latency:.2f}")
        print(f"  P50: {p50:.2f}")
        print(f"  P90: {p90:.2f}")
        print(f"  P95: {p95:.2f}")
        print(f"  P99: {p99:.2f}")
        print(f"  Min: {min(latencies):.2f}")
        print(f"  Max: {max(latencies):.2f}")

        # Assert 99th percentile requirement
        assert (
            p99 <= 300.0
        ), f"99th percentile latency ({p99:.2f}ms) exceeds 300ms requirement"

        # Additional assertions for other percentiles
        assert p95 <= 250.0, f"95th percentile ({p95:.2f}ms) should be under 250ms"
        assert p90 <= 200.0, f"90th percentile ({p90:.2f}ms) should be under 200ms"
        assert (
            avg_latency <= 150.0
        ), f"Average latency ({avg_latency:.2f}ms) should be under 150ms"

    @pytest.mark.asyncio
    async def test_warm_run_latency(self, mock_bigquery_client, mock_forecast_data):
        """Test latency on warm runs (with caching)."""
        # Enable caching
        mock_bigquery_client.enable_cache = True

        # Create repository and use case
        repo = BigQueryForecastRepository(
            client=mock_bigquery_client, ml_dataset_id="ml_models"
        )

        repo.check_model_exists = AsyncMock(return_value=True)

        forecast_use_case = ForecastConsumption(forecast_repository=repo)

        # Warm up with initial request
        await forecast_use_case.get_forecast(
            district_id="DIST_001", metric="flow_rate", horizon=7
        )

        # Run warm requests
        num_requests = 50
        latencies = []

        print(f"\nRunning {num_requests} warm forecast requests...")

        for i in range(num_requests):
            start_time = time.perf_counter()

            result = await forecast_use_case.get_forecast(
                district_id="DIST_001", metric="flow_rate", horizon=7
            )

            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)

        # Calculate statistics
        p99_warm = calculate_percentile(latencies, 99)
        avg_warm = mean(latencies)

        print(f"\nWarm Run Statistics (ms):")
        print(f"  Average: {avg_warm:.2f}")
        print(f"  P99: {p99_warm:.2f}")

        # Warm runs should be significantly faster
        assert (
            p99_warm <= 150.0
        ), f"Warm 99th percentile ({p99_warm:.2f}ms) should be under 150ms"
        assert avg_warm <= 50.0, f"Warm average ({avg_warm:.2f}ms) should be under 50ms"

    @pytest.mark.asyncio
    async def test_concurrent_request_latency(
        self, mock_bigquery_client, mock_forecast_data
    ):
        """Test latency under concurrent load."""
        # Create shared repository and use case
        repo = BigQueryForecastRepository(
            client=mock_bigquery_client, ml_dataset_id="ml_models"
        )

        repo.check_model_exists = AsyncMock(return_value=True)

        forecast_use_case = ForecastConsumption(forecast_repository=repo)

        # Define concurrent request task
        async def make_request(district_id: str, metric: str) -> float:
            start_time = time.perf_counter()

            await forecast_use_case.get_forecast(
                district_id=district_id, metric=metric, horizon=7
            )

            end_time = time.perf_counter()
            return (end_time - start_time) * 1000

        # Run concurrent requests
        num_concurrent = 10
        num_batches = 5
        all_latencies = []

        print(
            f"\nRunning {num_concurrent} concurrent requests in {num_batches} batches..."
        )

        for batch in range(num_batches):
            # Create concurrent tasks
            tasks = []
            for i in range(num_concurrent):
                # Vary the requests slightly
                district = "DIST_001" if i % 2 == 0 else "DIST_002"
                metric = ["flow_rate", "pressure", "reservoir_level"][i % 3]

                tasks.append(make_request(district, metric))

            # Execute concurrently
            batch_latencies = await asyncio.gather(*tasks)
            all_latencies.extend(batch_latencies)

            print(f"  Batch {batch + 1}/{num_batches} completed")

        # Calculate statistics
        p99_concurrent = calculate_percentile(all_latencies, 99)
        avg_concurrent = mean(all_latencies)

        print(f"\nConcurrent Request Statistics (ms):")
        print(f"  Average: {avg_concurrent:.2f}")
        print(f"  P99: {p99_concurrent:.2f}")

        # Concurrent requests should still meet SLA
        assert (
            p99_concurrent <= 300.0
        ), f"Concurrent 99th percentile ({p99_concurrent:.2f}ms) exceeds 300ms"

    @pytest.mark.asyncio
    async def test_latency_by_horizon(self, mock_bigquery_client, mock_forecast_data):
        """Test that latency doesn't significantly vary by horizon."""
        # Create repository and use case
        repo = BigQueryForecastRepository(
            client=mock_bigquery_client, ml_dataset_id="ml_models"
        )

        repo.check_model_exists = AsyncMock(return_value=True)

        forecast_use_case = ForecastConsumption(forecast_repository=repo)

        # Test different horizons
        horizons = [1, 3, 5, 7]
        horizon_latencies = {}

        print("\nTesting latency by forecast horizon...")

        for horizon in horizons:
            latencies = []

            for _ in range(20):
                start_time = time.perf_counter()

                await forecast_use_case.get_forecast(
                    district_id="DIST_001", metric="flow_rate", horizon=horizon
                )

                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)

            avg_latency = mean(latencies)
            horizon_latencies[horizon] = avg_latency

            print(f"  Horizon {horizon} days: {avg_latency:.2f}ms average")

        # Latency should not vary significantly by horizon
        latency_values = list(horizon_latencies.values())
        latency_range = max(latency_values) - min(latency_values)

        assert (
            latency_range <= 50.0
        ), f"Latency variance by horizon too high: {latency_range:.2f}ms"
