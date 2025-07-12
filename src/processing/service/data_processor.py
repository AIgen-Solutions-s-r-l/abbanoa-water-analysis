"""
Data processor that handles metric computation with multi-threading.

This module processes raw sensor data and computes aggregated metrics
using parallel processing for optimal performance.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from google.cloud import bigquery

logger = logging.getLogger(__name__)


class DataProcessor:
    """Handles data processing and metric computation."""

    def __init__(self, max_workers: int = 4):
        """
        Initialize data processor.

        Args:
            max_workers: Maximum number of parallel workers
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.postgres_manager = None
        self.bigquery_client = None

    async def initialize(self, postgres_manager, bigquery_client):
        """Initialize with database connections."""
        self.postgres_manager = postgres_manager
        self.bigquery_client = bigquery_client
        logger.info(f"Data processor initialized with {self.max_workers} workers")

    async def process_new_data(
        self,
        start_timestamp: datetime,
        end_timestamp: datetime,
        job_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process new data from BigQuery and compute metrics.

        Args:
            start_timestamp: Start of data range
            end_timestamp: End of data range
            job_id: Processing job ID for tracking

        Returns:
            Processing results summary
        """
        logger.info(f"Processing data from {start_timestamp} to {end_timestamp}")

        try:
            # 1. Get list of nodes with new data
            nodes = await self._get_nodes_with_data(start_timestamp, end_timestamp)

            if not nodes:
                return {"success": True, "total_records": 0, "processed_nodes": []}

            # 2. Process nodes in parallel
            total_records = 0
            processed_nodes = []
            failed_nodes = []

            # Create tasks for parallel processing
            loop = asyncio.get_event_loop()
            tasks = []

            for node_batch in self._batch_nodes(nodes, batch_size=10):
                task = loop.run_in_executor(
                    self.executor,
                    self._process_node_batch,
                    node_batch,
                    start_timestamp,
                    end_timestamp,
                )
                tasks.append(task)

            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Batch processing failed: {result}")
                else:
                    total_records += result["records_processed"]
                    processed_nodes.extend(result["nodes_processed"])
                    failed_nodes.extend(result["nodes_failed"])

            # 3. Compute network-wide metrics
            await self._compute_network_efficiency(start_timestamp, end_timestamp)

            # 4. Update data quality metrics
            await self._update_data_quality_metrics(
                processed_nodes, start_timestamp, end_timestamp
            )

            return {
                "success": True,
                "total_records": total_records,
                "processed_nodes": processed_nodes,
                "failed_nodes": failed_nodes,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
            }

        except Exception as e:
            logger.error(f"Data processing failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _process_node_batch(
        self, nodes: List[str], start_timestamp: datetime, end_timestamp: datetime
    ) -> Dict[str, Any]:
        """Process a batch of nodes (runs in thread pool)."""
        records_processed = 0
        nodes_processed = []
        nodes_failed = []

        for node_id in nodes:
            try:
                # Fetch data from BigQuery
                df = self._fetch_node_data(node_id, start_timestamp, end_timestamp)

                if df.empty:
                    continue

                # Compute metrics for different time windows
                for window in ["5min", "1hour", "1day"]:
                    metrics = self._compute_metrics(df, node_id, window)
                    asyncio.run(self._store_metrics(metrics))

                records_processed += len(df)
                nodes_processed.append(node_id)

            except Exception as e:
                logger.error(f"Failed to process node {node_id}: {e}")
                nodes_failed.append(node_id)

        return {
            "records_processed": records_processed,
            "nodes_processed": nodes_processed,
            "nodes_failed": nodes_failed,
        }

    def _fetch_node_data(
        self, node_id: str, start_timestamp: datetime, end_timestamp: datetime
    ) -> pd.DataFrame:
        """Fetch data for a specific node from BigQuery."""
        query = f"""
        SELECT 
            timestamp,
            node_id,
            temperature,
            flow_rate,
            pressure,
            volume as total_flow,
            data_quality_score as quality_score
        FROM `{self.bigquery_client.project_id}.{self.bigquery_client.dataset_id}.sensor_readings_ml`
        WHERE node_id = @node_id
        AND timestamp BETWEEN @start_timestamp AND @end_timestamp
        ORDER BY timestamp
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("node_id", "STRING", node_id),
                bigquery.ScalarQueryParameter(
                    "start_timestamp", "TIMESTAMP", start_timestamp
                ),
                bigquery.ScalarQueryParameter(
                    "end_timestamp", "TIMESTAMP", end_timestamp
                ),
            ]
        )

        return self.bigquery_client.client.query(
            query, job_config=job_config
        ).to_dataframe()

    def _compute_metrics(
        self, df: pd.DataFrame, node_id: str, window: str
    ) -> List[Dict[str, Any]]:
        """Compute aggregated metrics for a time window."""
        # Set timestamp as index
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)

        # Determine resampling frequency
        freq_map = {"5min": "5T", "1hour": "1H", "1day": "1D"}
        freq = freq_map[window]

        # Resample and compute aggregations
        metrics = []

        for period_start, period_data in df.resample(freq):
            if period_data.empty:
                continue

            period_end = period_start + pd.Timedelta(freq)

            # Compute metrics
            metric = {
                "node_id": node_id,
                "time_window": window,
                "window_start": period_start.to_pydatetime(),
                "window_end": period_end.to_pydatetime(),
                # Flow metrics
                "avg_flow_rate": period_data["flow_rate"].mean(),
                "min_flow_rate": period_data["flow_rate"].min(),
                "max_flow_rate": period_data["flow_rate"].max(),
                "total_volume": period_data["total_flow"].sum(),
                "flow_variance": period_data["flow_rate"].var(),
                # Pressure metrics
                "avg_pressure": period_data["pressure"].mean(),
                "min_pressure": period_data["pressure"].min(),
                "max_pressure": period_data["pressure"].max(),
                "pressure_variance": period_data["pressure"].var(),
                # Temperature metrics
                "avg_temperature": period_data["temperature"].mean(),
                "min_temperature": period_data["temperature"].min(),
                "max_temperature": period_data["temperature"].max(),
                # Quality metrics
                "data_completeness": len(period_data)
                / self._expected_data_points(window)
                * 100,
                "anomaly_count": self._detect_anomalies(period_data),
                "quality_score": (
                    period_data["quality_score"].mean()
                    if "quality_score" in period_data
                    else 1.0
                ),
                "computed_at": datetime.now(),
            }

            metrics.append(metric)

        return metrics

    def _expected_data_points(self, window: str) -> int:
        """Get expected number of data points for a time window."""
        # Assuming data every 30 minutes
        expected = {
            "5min": 1,  # At least 1 point per 5 minutes
            "1hour": 2,  # 2 points per hour (30-minute intervals)
            "1day": 48,  # 48 points per day
        }
        return expected.get(window, 1)

    def _detect_anomalies(self, df: pd.DataFrame) -> int:
        """Simple anomaly detection based on statistical thresholds."""
        anomaly_count = 0

        # Flow rate anomalies (outside 3 standard deviations)
        if "flow_rate" in df.columns:
            mean_flow = df["flow_rate"].mean()
            std_flow = df["flow_rate"].std()
            anomalies = df[
                (df["flow_rate"] < mean_flow - 3 * std_flow)
                | (df["flow_rate"] > mean_flow + 3 * std_flow)
            ]
            anomaly_count += len(anomalies)

        # Pressure anomalies
        if "pressure" in df.columns:
            # Pressure should be between 2 and 8 bar typically
            pressure_anomalies = df[(df["pressure"] < 2) | (df["pressure"] > 8)]
            anomaly_count += len(pressure_anomalies)

        return anomaly_count

    async def _store_metrics(self, metrics: List[Dict[str, Any]]):
        """Store computed metrics in PostgreSQL."""
        if not metrics:
            return

        async with self.postgres_manager.acquire() as conn:
            # Use COPY for efficient bulk insert
            await conn.copy_records_to_table(
                "computed_metrics",
                records=[
                    (
                        m["node_id"],
                        m["time_window"],
                        m["window_start"],
                        m["window_end"],
                        m["avg_flow_rate"],
                        m["min_flow_rate"],
                        m["max_flow_rate"],
                        m["total_volume"],
                        m["flow_variance"],
                        m["avg_pressure"],
                        m["min_pressure"],
                        m["max_pressure"],
                        m["pressure_variance"],
                        m["avg_temperature"],
                        m["min_temperature"],
                        m["max_temperature"],
                        m["data_completeness"],
                        m["anomaly_count"],
                        m["quality_score"],
                        m["computed_at"],
                    )
                    for m in metrics
                ],
                schema_name="water_infrastructure",
            )

    async def _get_nodes_with_data(
        self, start_timestamp: datetime, end_timestamp: datetime
    ) -> List[str]:
        """Get list of nodes that have data in the time range."""
        query = f"""
        SELECT DISTINCT node_id
        FROM `{self.bigquery_client.project_id}.{self.bigquery_client.dataset_id}.sensor_readings_ml`
        WHERE timestamp BETWEEN @start_timestamp AND @end_timestamp
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter(
                    "start_timestamp", "TIMESTAMP", start_timestamp
                ),
                bigquery.ScalarQueryParameter(
                    "end_timestamp", "TIMESTAMP", end_timestamp
                ),
            ]
        )

        result = self.bigquery_client.client.query(
            query, job_config=job_config
        ).result()
        return [row.node_id for row in result]

    def _batch_nodes(self, nodes: List[str], batch_size: int) -> List[List[str]]:
        """Split nodes into batches for parallel processing."""
        for i in range(0, len(nodes), batch_size):
            yield nodes[i : i + batch_size]

    async def _compute_network_efficiency(
        self, start_timestamp: datetime, end_timestamp: datetime
    ):
        """Compute network-wide efficiency metrics."""
        async with self.postgres_manager.acquire() as conn:
            # Get aggregated metrics for the period
            result = await conn.fetchrow(
                """
                SELECT 
                    COUNT(DISTINCT node_id) as active_nodes,
                    SUM(total_volume) as total_volume,
                    AVG(avg_pressure) as avg_pressure,
                    SUM(anomaly_count) as total_anomalies
                FROM water_infrastructure.computed_metrics
                WHERE window_start >= $1 AND window_end <= $2
                AND time_window = '1hour'
            """,
                start_timestamp,
                end_timestamp,
            )

            if result:
                # Store network efficiency
                await conn.execute(
                    """
                    INSERT INTO water_infrastructure.network_efficiency
                    (computation_timestamp, time_window, window_start, window_end,
                     total_input_volume, total_output_volume, efficiency_percentage,
                     active_nodes, total_anomalies)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                    datetime.now(),
                    "1day",
                    start_timestamp,
                    end_timestamp,
                    result["total_volume"],
                    result["total_volume"] * 0.95,  # Assume 5% loss
                    95.0,
                    result["active_nodes"],
                    result["total_anomalies"],
                )

    async def _update_data_quality_metrics(
        self, nodes: List[str], start_timestamp: datetime, end_timestamp: datetime
    ):
        """Update data quality metrics for processed nodes."""
        for node_id in nodes:
            async with self.postgres_manager.acquire() as conn:
                # Get computed metrics for quality assessment
                metrics = await conn.fetch(
                    """
                    SELECT data_completeness, anomaly_count, quality_score
                    FROM water_infrastructure.computed_metrics
                    WHERE node_id = $1 
                    AND window_start >= $2 
                    AND window_end <= $3
                    AND time_window = '1hour'
                """,
                    node_id,
                    start_timestamp,
                    end_timestamp,
                )

                if metrics:
                    avg_completeness = np.mean(
                        [m["data_completeness"] for m in metrics]
                    )
                    total_anomalies = sum(m["anomaly_count"] for m in metrics)
                    avg_quality = np.mean([m["quality_score"] for m in metrics])

                    # Store quality metrics
                    await conn.execute(
                        """
                        INSERT INTO water_infrastructure.data_quality_metrics
                        (node_id, check_timestamp, time_window, 
                         completeness_score, validity_score, consistency_score, 
                         overall_quality_score, outliers_detected)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                        node_id,
                        datetime.now(),
                        "1day",
                        avg_completeness / 100,
                        0.95,
                        0.90,  # Placeholder validity/consistency
                        avg_quality,
                        total_anomalies,
                    )

    async def check_data_quality(self):
        """Periodic data quality check across all nodes."""
        logger.info("Running data quality check...")

        # This would implement comprehensive data quality checks
        # For now, it's a placeholder for the scheduled job
        pass
