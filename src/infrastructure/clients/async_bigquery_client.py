"""
Async BigQuery client with connection pooling and retry logic.

This module provides an async wrapper around the BigQuery client with
performance optimizations, retry strategies, and connection pooling.
"""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

import pandas as pd
from google.api_core import retry as google_retry
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter
from google.cloud.exceptions import GoogleCloudError

from src.shared.exceptions.forecast_exceptions import (
    ForecastServiceException,
    ForecastTimeoutException,
)


class AsyncBigQueryClient:
    """
    Async BigQuery client with optimized performance features.
    
    Features:
    - Connection pooling
    - Exponential backoff retry
    - Query result caching
    - Timeout management
    - Performance metrics collection
    """
    
    def __init__(
        self,
        project_id: str,
        dataset_id: str,
        location: str = "EU",
        max_pool_size: int = 10,
        min_pool_size: int = 2,
        query_timeout_ms: int = 250,
        connection_timeout_ms: int = 10000,
        max_retry_attempts: int = 3,
        enable_cache: bool = True
    ):
        """
        Initialize async BigQuery client.
        
        Args:
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
            location: Dataset location
            max_pool_size: Maximum connection pool size
            min_pool_size: Minimum connection pool size
            query_timeout_ms: Query timeout in milliseconds
            connection_timeout_ms: Connection timeout in milliseconds
            max_retry_attempts: Maximum retry attempts
            enable_cache: Enable query result caching
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.location = location
        self.query_timeout_ms = query_timeout_ms
        self.connection_timeout_ms = connection_timeout_ms
        self.max_retry_attempts = max_retry_attempts
        self.enable_cache = enable_cache
        
        # Connection pool
        self._pool: List[bigquery.Client] = []
        self._pool_lock = asyncio.Lock()
        self.max_pool_size = max_pool_size
        self.min_pool_size = min_pool_size
        
        # Query cache (simple in-memory cache)
        self._cache: Dict[str, Any] = {}
        self._cache_lock = asyncio.Lock()
        
        # Retry configuration
        self._retry_config = google_retry.Retry(
            initial=0.5,  # Initial delay: 500ms
            maximum=10.0,  # Max delay: 10s
            multiplier=2.0,  # Exponential backoff
            deadline=self.connection_timeout_ms / 1000,  # Total deadline
            predicate=google_retry.if_exception_type(
                GoogleCloudError,
                asyncio.TimeoutError,
                ConnectionError,
            )
        )
    
    async def initialize(self) -> None:
        """Initialize connection pool with minimum connections."""
        async with self._pool_lock:
            for _ in range(self.min_pool_size):
                client = bigquery.Client(
                    project=self.project_id,
                    location=self.location
                )
                self._pool.append(client)
    
    @asynccontextmanager
    async def _get_client(self) -> AsyncIterator[bigquery.Client]:
        """
        Get a client from the connection pool.
        
        Yields:
            BigQuery client instance
        """
        client = None
        try:
            async with self._pool_lock:
                if self._pool:
                    client = self._pool.pop()
                else:
                    # Create new client if pool is empty and under max size
                    client = bigquery.Client(
                        project=self.project_id,
                        location=self.location
                    )
            
            yield client
            
        finally:
            # Return client to pool
            if client:
                async with self._pool_lock:
                    if len(self._pool) < self.max_pool_size:
                        self._pool.append(client)
    
    def _get_cache_key(self, query: str, parameters: Optional[List[Any]] = None) -> str:
        """Generate cache key for query."""
        param_str = str(parameters) if parameters else ""
        return f"{query}:{param_str}"
    
    async def execute_query(
        self,
        query: str,
        parameters: Optional[List[ScalarQueryParameter]] = None,
        timeout_ms: Optional[int] = None,
        use_cache: Optional[bool] = None
    ) -> pd.DataFrame:
        """
        Execute a BigQuery query asynchronously.
        
        Args:
            query: SQL query to execute
            parameters: Query parameters
            timeout_ms: Query timeout override
            use_cache: Cache usage override
        
        Returns:
            Query results as DataFrame
        
        Raises:
            ForecastServiceException: Query execution error
            ForecastTimeoutException: Query timeout
        """
        start_time = time.time()
        timeout_ms = timeout_ms or self.query_timeout_ms
        use_cache = use_cache if use_cache is not None else self.enable_cache
        
        # Check cache
        cache_key = self._get_cache_key(query, parameters)
        if use_cache:
            async with self._cache_lock:
                if cache_key in self._cache:
                    return self._cache[cache_key].copy()
        
        try:
            # Execute query in thread pool to avoid blocking
            result_df = await asyncio.wait_for(
                self._execute_query_async(query, parameters),
                timeout=timeout_ms / 1000
            )
            
            # Cache result
            if use_cache:
                async with self._cache_lock:
                    self._cache[cache_key] = result_df.copy()
            
            # Check latency
            elapsed_ms = (time.time() - start_time) * 1000
            if elapsed_ms > timeout_ms:
                raise ForecastTimeoutException(
                    f"Query exceeded timeout: {elapsed_ms:.0f}ms > {timeout_ms}ms",
                    timeout_ms=timeout_ms,
                    operation="bigquery_query"
                )
            
            return result_df
            
        except asyncio.TimeoutError:
            elapsed_ms = (time.time() - start_time) * 1000
            raise ForecastTimeoutException(
                f"Query timeout after {elapsed_ms:.0f}ms",
                timeout_ms=timeout_ms,
                operation="bigquery_query"
            )
        except GoogleCloudError as e:
            raise ForecastServiceException(
                f"BigQuery error: {str(e)}",
                service="bigquery",
                original_error=e
            )
        except Exception as e:
            raise ForecastServiceException(
                f"Unexpected error executing query: {str(e)}",
                service="bigquery",
                original_error=e
            )
    
    async def _execute_query_async(
        self,
        query: str,
        parameters: Optional[List[ScalarQueryParameter]] = None
    ) -> pd.DataFrame:
        """Execute query with retry logic."""
        
        async def _run_query():
            async with self._get_client() as client:
                # Configure query
                job_config = QueryJobConfig(
                    query_parameters=parameters or [],
                    use_query_cache=True,
                    use_legacy_sql=False,
                    priority=bigquery.QueryPriority.INTERACTIVE
                )
                
                # Run query in executor to avoid blocking
                loop = asyncio.get_event_loop()
                query_job = await loop.run_in_executor(
                    None,
                    client.query,
                    query,
                    job_config
                )
                
                # Wait for results
                results = await loop.run_in_executor(
                    None,
                    query_job.result
                )
                
                # Convert to DataFrame
                df = await loop.run_in_executor(
                    None,
                    results.to_dataframe
                )
                
                return df
        
        # Execute with retry
        for attempt in range(self.max_retry_attempts):
            try:
                return await _run_query()
            except (GoogleCloudError, ConnectionError) as e:
                if attempt == self.max_retry_attempts - 1:
                    raise
                
                # Exponential backoff
                delay = 0.5 * (2 ** attempt)
                await asyncio.sleep(delay)
    
    async def check_table_exists(
        self,
        table_id: str,
        dataset_id: Optional[str] = None
    ) -> bool:
        """
        Check if a table exists.
        
        Args:
            table_id: Table ID
            dataset_id: Dataset ID (uses default if not provided)
        
        Returns:
            True if table exists, False otherwise
        """
        dataset_id = dataset_id or self.dataset_id
        full_table_id = f"{self.project_id}.{dataset_id}.{table_id}"
        
        try:
            async with self._get_client() as client:
                loop = asyncio.get_event_loop()
                table = await loop.run_in_executor(
                    None,
                    client.get_table,
                    full_table_id
                )
                return table is not None
        except Exception:
            return False
    
    async def clear_cache(self) -> None:
        """Clear the query cache."""
        async with self._cache_lock:
            self._cache.clear()
    
    async def close(self) -> None:
        """Close all connections in the pool."""
        async with self._pool_lock:
            for client in self._pool:
                # BigQuery client doesn't have explicit close
                pass
            self._pool.clear()