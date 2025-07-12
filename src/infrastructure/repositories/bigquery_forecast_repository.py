"""
BigQuery implementation of the forecast repository.

This module provides the concrete implementation of the ForecastRepositoryInterface
using BigQuery ML for forecast data retrieval.
"""

import logging
from typing import Optional

import pandas as pd
from google.cloud.bigquery import ScalarQueryParameter

from src.application.interfaces.forecast_repository import ForecastRepositoryInterface
from src.infrastructure.clients.async_bigquery_client import AsyncBigQueryClient
from src.shared.exceptions.forecast_exceptions import (
    ForecastNotFoundException,
    ForecastServiceException,
)


class BigQueryForecastRepository(ForecastRepositoryInterface):
    """
    BigQuery implementation of forecast repository.

    Retrieves forecast data from BigQuery ML models using the async client
    for optimal performance.
    """

    def __init__(
        self,
        client: AsyncBigQueryClient,
        ml_dataset_id: str = "ml_models",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize BigQuery forecast repository.

        Args:
            client: Async BigQuery client instance
            ml_dataset_id: Dataset containing ML models
            logger: Logger instance
        """
        self.client = client
        self.ml_dataset_id = ml_dataset_id
        self.logger = logger or logging.getLogger(__name__)

    async def get_model_forecast(
        self, model_name: str, district_metric_id: str, horizon: int
    ) -> pd.DataFrame:
        """
        Retrieve forecast data from a BigQuery ML model.

        Args:
            model_name: Name of the ML model
            district_metric_id: Combined district and metric ID
            horizon: Forecast horizon in days

        Returns:
            DataFrame with forecast data

        Raises:
            ForecastNotFoundException: Model or forecast not found
            ForecastServiceException: Service-level error
            ForecastTimeoutException: Request timeout
        """
        self.logger.info(
            f"Retrieving forecast from model '{model_name}' "
            f"for '{district_metric_id}' with horizon {horizon}"
        )

        # Check if model exists first
        if not await self.check_model_exists(model_name):
            raise ForecastNotFoundException(
                district_id=district_metric_id.split("_")[0],
                metric="_".join(district_metric_id.split("_")[1:]),
                horizon=horizon,
                details={"model_name": model_name},
            )

        # Build forecast query with proper input data
        query = f"""
        WITH forecast_input AS (
            SELECT
                '{district_metric_id}' as district_metric_id,
                DATE(timestamp) as date_utc,
                AVG(CASE
                    WHEN RIGHT(@district_metric_id, 9) = 'flow_rate' THEN flow_rate
                    WHEN RIGHT(@district_metric_id, 8) = 'pressure' THEN pressure
                    WHEN RIGHT(@district_metric_id, 11) = 'temperature' THEN temperature
                    ELSE flow_rate
                END) as avg_value
            FROM `{self.client.project_id}.{self.client.dataset_id}.v_sensor_readings_normalized`
            WHERE node_id = LEFT(@district_metric_id, STRPOS(@district_metric_id, '_') - 1)
                AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
                AND timestamp <= CURRENT_TIMESTAMP()
            GROUP BY DATE(timestamp)
        )
        SELECT
            forecast_timestamp AS timestamp,
            district_metric_id,
            forecast_value,
            standard_error,
            confidence_level,
            forecast_value - (1.28 * standard_error) as lower_bound,
            forecast_value + (1.28 * standard_error) as upper_bound
        FROM ML.FORECAST(
            MODEL `{self.client.project_id}.{self.ml_dataset_id}.{model_name}`,
            (SELECT * FROM forecast_input),
            STRUCT(@horizon AS horizon, 0.8 AS confidence_level)
        )
        WHERE forecast_timestamp > CURRENT_DATE()
            AND forecast_timestamp <= DATE_ADD(CURRENT_DATE(), INTERVAL @horizon DAY)
        ORDER BY forecast_timestamp
        """

        # Query parameters
        parameters = [
            ScalarQueryParameter("horizon", "INT64", horizon),
            ScalarQueryParameter("district_metric_id", "STRING", district_metric_id),
        ]

        try:
            # Execute forecast query
            df = await self.client.execute_query(
                query=query,
                parameters=parameters,
                timeout_ms=200,  # Tight timeout for 300ms SLA
            )

            if df.empty:
                raise ForecastNotFoundException(
                    district_id=district_metric_id.split("_")[0],
                    metric="_".join(district_metric_id.split("_")[1:]),
                    horizon=horizon,
                    details={
                        "model_name": model_name,
                        "reason": "No forecast data returned",
                    },
                )

            # Ensure timestamp is timezone-aware UTC
            if "timestamp" in df.columns and df["timestamp"].dt.tz is None:
                df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")

            # Add default confidence level if missing
            if "confidence_level" not in df.columns:
                df["confidence_level"] = 0.95

            return df

        except ForecastNotFoundException:
            raise
        except Exception as e:
            self.logger.error(
                f"Error retrieving forecast from model '{model_name}': {str(e)}"
            )
            raise ForecastServiceException(
                f"Failed to retrieve forecast from model '{model_name}'",
                service="bigquery_ml",
                original_error=e,
            )

    async def check_model_exists(self, model_name: str) -> bool:
        """
        Check if a BigQuery ML model exists.

        Args:
            model_name: Name of the ML model

        Returns:
            True if model exists, False otherwise
        """
        query = f"""
        SELECT 1
        FROM `{self.client.project_id}.{self.ml_dataset_id}.INFORMATION_SCHEMA.MODELS`
        WHERE model_name = @model_name
        LIMIT 1
        """

        parameters = [ScalarQueryParameter("model_name", "STRING", model_name)]

        try:
            df = await self.client.execute_query(
                query=query,
                parameters=parameters,
                timeout_ms=100,  # Fast check
                use_cache=True,  # Cache model existence checks
            )
            return not df.empty

        except Exception as e:
            self.logger.error(f"Error checking model existence: {str(e)}")
            # On error, assume model doesn't exist rather than failing
            return False

    async def get_model_metadata(self, model_name: str) -> dict:
        """
        Retrieve metadata about a BigQuery ML model.

        Args:
            model_name: Name of the ML model

        Returns:
            Dictionary containing model metadata
        """
        query = f"""
        SELECT
            model_name,
            model_type,
            creation_time AS created_at,
            last_modified_time AS last_updated,
            training_options
        FROM `{self.client.project_id}.{self.ml_dataset_id}.INFORMATION_SCHEMA.MODELS`
        WHERE model_name = @model_name
        """

        parameters = [ScalarQueryParameter("model_name", "STRING", model_name)]

        try:
            df = await self.client.execute_query(
                query=query, parameters=parameters, timeout_ms=100, use_cache=True
            )

            if df.empty:
                raise ForecastNotFoundException(
                    district_id="unknown",
                    metric="unknown",
                    horizon=0,
                    details={"model_name": model_name},
                )

            # Convert first row to dict
            metadata = df.iloc[0].to_dict()

            # Get latest performance metrics if available
            perf_query = f"""
            SELECT
                mean_absolute_percentage_error AS mape,
                mean_absolute_error AS mae,
                root_mean_squared_error AS rmse
            FROM
                ML.EVALUATE(MODEL `{self.client.project_id}.{self.ml_dataset_id}.{model_name}`)
            """

            try:
                perf_df = await self.client.execute_query(
                    query=perf_query, timeout_ms=150, use_cache=True
                )

                if not perf_df.empty:
                    metadata["performance_metrics"] = perf_df.iloc[0].to_dict()

            except Exception:
                # Performance metrics are optional
                pass

            return metadata

        except ForecastNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving model metadata: {str(e)}")
            raise ForecastServiceException(
                f"Failed to retrieve metadata for model '{model_name}'",
                service="bigquery_ml",
                original_error=e,
            )
