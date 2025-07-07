"""Forecast Calculation Service - Backend-side calculations for forecast functionality."""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.infrastructure.clients.async_bigquery_client import AsyncBigQueryClient
from src.infrastructure.logging.forecast_logger import get_forecast_logger

logger = logging.getLogger(__name__)
forecast_logger = get_forecast_logger(__name__)


class ForecastCalculationService:
    """Service responsible for all forecast calculations on the backend."""
    
    def __init__(self, bigquery_client: AsyncBigQueryClient):
        """Initialize the forecast calculation service.
        
        Args:
            bigquery_client: Async BigQuery client for database operations
        """
        self.client = bigquery_client
        self.project_id = bigquery_client.project_id
        self.dataset_id = bigquery_client.dataset_id
        self.ml_dataset_id = getattr(bigquery_client, 'ml_dataset_id', 'ml_models')
        
    async def calculate_forecast(
        self,
        district_id: str,
        metric: str,
        horizon: int = 7,
        include_history_days: int = 30,
        confidence_level: float = 0.8
    ) -> Dict[str, pd.DataFrame]:
        """Execute all forecast calculations backend-side.
        
        Args:
            district_id: District identifier (e.g., "DIST_001")
            metric: Metric type (e.g., "flow_rate", "pressure")
            horizon: Forecast horizon in days
            include_history_days: Days of historical data to include
            confidence_level: Confidence level for intervals (0.8 = 80%)
            
        Returns:
            Dictionary containing:
                - historical: DataFrame with historical data
                - forecast: DataFrame with predictions and confidence intervals
                - metrics: Dictionary with calculated metrics
        """
        start_time = time.time()
        request_id = f"{district_id}_{metric}_{horizon}_{int(start_time)}"
        
        forecast_logger.log_forecast_request(
            request_id=request_id,
            district_id=district_id,
            metric=metric,
            horizon=horizon,
            confidence_level=confidence_level,
            include_history_days=include_history_days
        )
        
        try:
            # Get historical data
            hist_start = time.time()
            historical = await self._fetch_historical_data(
                district_id, metric, include_history_days
            )
            hist_duration = (time.time() - hist_start) * 1000
            
            forecast_logger.log_calculation_step(
                step_name="fetch_historical_data",
                input_size=include_history_days,
                output_size=len(historical),
                duration_ms=hist_duration,
                request_id=request_id
            )
            
            # Generate forecast using ARIMA model
            forecast_start = time.time()
            forecast = await self._generate_forecast(
                district_id, metric, horizon, confidence_level
            )
            forecast_duration = (time.time() - forecast_start) * 1000
            
            forecast_logger.log_ml_model_call(
                model_name=f"arima_{district_id.lower()}_{metric}",
                status="success",
                duration_ms=forecast_duration,
                records_generated=len(forecast),
                request_id=request_id
            )
            
            # Calculate additional metrics backend-side
            metrics = self._calculate_metrics(historical, forecast)
            logger.debug(f"Calculated metrics: {metrics}")
            
            # Enhance forecast with additional calculations
            forecast = self._enhance_forecast_data(forecast, historical)
            
            # Aggregate and validate results
            results = self._aggregate_results(historical, forecast, metrics)
            
            # Log performance metrics
            total_duration = (time.time() - start_time) * 1000
            forecast_logger.log_performance_metric(
                metric_name="forecast_total_duration",
                value=total_duration,
                unit="ms",
                request_id=request_id,
                district_id=district_id,
                metric=metric
            )
            
            logger.info(f"Successfully calculated forecast for {district_id}/{metric}")
            return results
            
        except Exception as e:
            forecast_logger.log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                error_context={
                    "district_id": district_id,
                    "metric": metric,
                    "horizon": horizon,
                    "request_id": request_id
                }
            )
            
            # Return fallback forecast using simple methods
            forecast_logger.log_fallback_used(
                reason=f"Primary forecast failed: {str(e)}",
                fallback_method="simple_moving_average",
                request_id=request_id
            )
            
            return await self._fallback_forecast(district_id, metric, horizon, include_history_days)
    
    async def _fetch_historical_data(
        self, district_id: str, metric: str, days: int
    ) -> pd.DataFrame:
        """Fetch historical data from BigQuery.
        
        Args:
            district_id: District identifier
            metric: Metric type
            days: Number of days to fetch
            
        Returns:
            DataFrame with historical data
        """
        query = f"""
        SELECT
            date_utc as timestamp,
            avg_value as value,
            district_id,
            metric_type as metric
        FROM `{self.project_id}.{self.dataset_id}.vw_daily_timeseries`
        WHERE district_id = @district_id
            AND metric_type = @metric
            AND date_utc >= DATE_SUB(CURRENT_DATE(), INTERVAL @days DAY)
            AND date_utc <= CURRENT_DATE()
        ORDER BY date_utc
        """
        
        from google.cloud.bigquery import ScalarQueryParameter
        
        parameters = [
            ScalarQueryParameter("district_id", "STRING", district_id),
            ScalarQueryParameter("metric", "STRING", metric),
            ScalarQueryParameter("days", "INT64", days),
        ]
        
        query_start = time.time()
        df = await self.client.execute_query(query, parameters=parameters)
        query_duration = (time.time() - query_start) * 1000
        
        forecast_logger.log_bigquery_query(
            query_type="fetch_historical_data",
            duration_ms=query_duration,
            rows_returned=len(df),
            district_id=district_id,
            metric=metric,
            days_requested=days
        )
        
        # Ensure timestamp is datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Calculate moving averages backend-side
        df = self._calculate_moving_averages(df)
        
        return df
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def _generate_forecast(
        self,
        district_id: str,
        metric: str,
        horizon: int,
        confidence_level: float
    ) -> pd.DataFrame:
        """Generate forecast using ARIMA_PLUS model.
        
        Args:
            district_id: District identifier
            metric: Metric type
            horizon: Forecast horizon in days
            confidence_level: Confidence level for intervals
            
        Returns:
            DataFrame with forecast results
        """
        # Construct model name based on district and metric
        district_lower = district_id.lower()
        model_name = f"arima_{district_lower}_{metric}"
        
        # Z-score for confidence level (0.8 = 80% => z = 1.28)
        z_score = self._get_z_score(confidence_level)
        
        query = f"""
        WITH forecast_input AS (
            SELECT
                CONCAT(@district_id, '_', @metric) as district_metric_id,
                date_utc,
                avg_value
            FROM `{self.project_id}.{self.dataset_id}.vw_daily_timeseries`
            WHERE district_id = @district_id
                AND metric_type = @metric
                AND date_utc >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
                AND date_utc <= CURRENT_DATE()
        )
        SELECT
            forecast_timestamp as timestamp,
            district_metric_id,
            forecast_value,
            standard_error,
            confidence_level,
            forecast_value - ({z_score} * standard_error) as lower_bound,
            forecast_value + ({z_score} * standard_error) as upper_bound,
            @district_id as district_id,
            @metric as metric
        FROM ML.FORECAST(
            MODEL `{self.project_id}.{self.ml_dataset_id}.{model_name}`,
            (SELECT * FROM forecast_input),
            STRUCT(@horizon AS horizon, @confidence_level AS confidence_level)
        )
        WHERE forecast_timestamp > CURRENT_DATE()
        ORDER BY forecast_timestamp
        """
        
        from google.cloud.bigquery import ScalarQueryParameter
        
        parameters = [
            ScalarQueryParameter("district_id", "STRING", district_id),
            ScalarQueryParameter("metric", "STRING", metric),
            ScalarQueryParameter("horizon", "INT64", horizon),
            ScalarQueryParameter("confidence_level", "FLOAT64", confidence_level),
        ]
        
        try:
            df = await self.client.execute_query(query, parameters=parameters)
            
            # Ensure timestamp is datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Rename columns for consistency
            df = df.rename(columns={'forecast_value': 'value'})
            
            return df
            
        except Exception as e:
            logger.error(f"ML.FORECAST failed for model {model_name}: {str(e)}")
            raise
    
    def _calculate_moving_averages(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate 7-day and 30-day moving averages.
        
        Args:
            data: DataFrame with 'value' column
            
        Returns:
            DataFrame with added moving average columns
        """
        data = data.sort_values('timestamp')
        data['ma_7'] = data['value'].rolling(window=7, min_periods=1).mean()
        data['ma_30'] = data['value'].rolling(window=30, min_periods=1).mean()
        return data
    
    def _calculate_metrics(
        self, historical: pd.DataFrame, forecast: pd.DataFrame
    ) -> Dict[str, float]:
        """Calculate trend and statistical metrics.
        
        Args:
            historical: Historical data
            forecast: Forecast data
            
        Returns:
            Dictionary of calculated metrics
        """
        # Calculate trend metrics from historical data
        trend_direction = self._get_trend_direction(historical)
        trend_strength = self._calculate_trend_strength(historical)
        seasonality_score = self._detect_seasonality(historical)
        
        # Calculate forecast metrics
        forecast_mean = forecast['value'].mean() if len(forecast) > 0 else 0
        forecast_std = forecast['value'].std() if len(forecast) > 0 else 0
        
        # Calculate historical metrics for comparison
        hist_mean = historical['value'].mean() if len(historical) > 0 else 0
        hist_std = historical['value'].std() if len(historical) > 0 else 0
        
        # Percent change from historical to forecast
        percent_change = ((forecast_mean - hist_mean) / hist_mean * 100) if hist_mean != 0 else 0
        
        return {
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'seasonality_score': seasonality_score,
            'forecast_mean': forecast_mean,
            'forecast_std': forecast_std,
            'historical_mean': hist_mean,
            'historical_std': hist_std,
            'percent_change': percent_change,
            'confidence_level': 0.8  # 80% confidence intervals
        }
    
    def _get_trend_direction(self, data: pd.DataFrame) -> str:
        """Determine trend direction using linear regression.
        
        Args:
            data: DataFrame with time series data
            
        Returns:
            'increasing', 'decreasing', or 'stable'
        """
        if len(data) < 2:
            return 'stable'
            
        # Simple linear regression on the values
        x = np.arange(len(data))
        y = data['value'].values
        
        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]
        
        # Determine trend based on slope relative to mean
        mean_value = y.mean()
        relative_slope = abs(slope) / mean_value if mean_value != 0 else 0
        
        if relative_slope < 0.01:  # Less than 1% change
            return 'stable'
        elif slope > 0:
            return 'increasing'
        else:
            return 'decreasing'
    
    def _calculate_trend_strength(self, data: pd.DataFrame) -> float:
        """Calculate trend strength using R-squared of linear fit.
        
        Args:
            data: DataFrame with time series data
            
        Returns:
            R-squared value (0-1)
        """
        if len(data) < 2:
            return 0.0
            
        x = np.arange(len(data))
        y = data['value'].values
        
        # Fit linear regression
        coeffs = np.polyfit(x, y, 1)
        p = np.poly1d(coeffs)
        
        # Calculate R-squared
        yhat = p(x)
        ybar = np.mean(y)
        ssreg = np.sum((yhat - ybar)**2)
        sstot = np.sum((y - ybar)**2)
        
        r_squared = ssreg / sstot if sstot != 0 else 0
        
        return float(r_squared)
    
    def _detect_seasonality(self, data: pd.DataFrame) -> float:
        """Detect seasonality using autocorrelation.
        
        Args:
            data: DataFrame with time series data
            
        Returns:
            Seasonality score (0-1)
        """
        if len(data) < 14:  # Need at least 2 weeks of data
            return 0.0
            
        values = data['value'].values
        
        # Check weekly seasonality (7-day autocorrelation)
        if len(values) >= 7:
            acf_7 = np.corrcoef(values[:-7], values[7:])[0, 1]
        else:
            acf_7 = 0
            
        # Return absolute autocorrelation as seasonality score
        return float(abs(acf_7))
    
    def _enhance_forecast_data(
        self, forecast: pd.DataFrame, historical: pd.DataFrame
    ) -> pd.DataFrame:
        """Enhance forecast data with additional calculations.
        
        Args:
            forecast: Forecast DataFrame
            historical: Historical DataFrame
            
        Returns:
            Enhanced forecast DataFrame
        """
        # Ensure confidence intervals exist
        if 'lower_bound' not in forecast.columns and 'standard_error' in forecast.columns:
            # Calculate 80% confidence intervals (z = 1.28)
            forecast['lower_bound'] = forecast['value'] - (1.28 * forecast['standard_error'])
            forecast['upper_bound'] = forecast['value'] + (1.28 * forecast['standard_error'])
        
        # Add trend from historical data
        if len(historical) > 0:
            last_value = historical.iloc[-1]['value']
            forecast['change_from_last'] = forecast['value'] - last_value
            forecast['percent_change'] = (forecast['change_from_last'] / last_value * 100) if last_value != 0 else 0
        
        return forecast
    
    def _aggregate_results(
        self,
        historical: pd.DataFrame,
        forecast: pd.DataFrame,
        metrics: Dict[str, float]
    ) -> Dict[str, any]:
        """Aggregate all results into final output format.
        
        Args:
            historical: Historical data
            forecast: Forecast data
            metrics: Calculated metrics
            
        Returns:
            Dictionary with all results
        """
        return {
            'historical': historical,
            'forecast': forecast,
            'metrics': metrics,
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'historical_days': len(historical),
                'forecast_days': len(forecast),
                'confidence_level': metrics.get('confidence_level', 0.8)
            }
        }
    
    def _get_z_score(self, confidence_level: float) -> float:
        """Get z-score for given confidence level.
        
        Args:
            confidence_level: Confidence level (e.g., 0.8 for 80%)
            
        Returns:
            Z-score value
        """
        z_scores = {
            0.80: 1.28,
            0.90: 1.645,
            0.95: 1.96,
            0.99: 2.576
        }
        return z_scores.get(confidence_level, 1.28)
    
    async def _fallback_forecast(
        self,
        district_id: str,
        metric: str,
        horizon: int,
        include_history_days: int
    ) -> Dict[str, any]:
        """Generate fallback forecast using simple moving average.
        
        Args:
            district_id: District identifier
            metric: Metric type
            horizon: Forecast horizon in days
            include_history_days: Days of historical data
            
        Returns:
            Fallback forecast results
        """
        logger.warning(f"Using fallback forecast for {district_id}/{metric}")
        
        try:
            # Get historical data
            historical = await self._fetch_historical_data(
                district_id, metric, include_history_days
            )
            
            if len(historical) == 0:
                # No data available
                return {
                    'historical': pd.DataFrame(),
                    'forecast': pd.DataFrame(),
                    'metrics': {},
                    'metadata': {
                        'error': 'No historical data available',
                        'fallback': True
                    }
                }
            
            # Simple moving average forecast
            last_values = historical.tail(7)['value'].values
            mean_value = last_values.mean()
            std_value = last_values.std() if len(last_values) > 1 else mean_value * 0.1
            
            # Generate forecast dates
            last_date = historical['timestamp'].max()
            forecast_dates = pd.date_range(
                start=last_date + timedelta(days=1),
                periods=horizon,
                freq='D'
            )
            
            # Create forecast dataframe
            forecast = pd.DataFrame({
                'timestamp': forecast_dates,
                'value': mean_value,
                'lower_bound': mean_value - (1.28 * std_value),
                'upper_bound': mean_value + (1.28 * std_value),
                'district_id': district_id,
                'metric': metric,
                'standard_error': std_value
            })
            
            # Calculate simple metrics
            metrics = {
                'trend_direction': 'stable',
                'trend_strength': 0.0,
                'seasonality_score': 0.0,
                'forecast_mean': mean_value,
                'forecast_std': std_value,
                'historical_mean': historical['value'].mean(),
                'historical_std': historical['value'].std(),
                'percent_change': 0.0,
                'confidence_level': 0.8,
                'fallback_method': 'moving_average'
            }
            
            return {
                'historical': historical,
                'forecast': forecast,
                'metrics': metrics,
                'metadata': {
                    'generated_at': datetime.utcnow().isoformat(),
                    'historical_days': len(historical),
                    'forecast_days': len(forecast),
                    'confidence_level': 0.8,
                    'fallback': True
                }
            }
            
        except Exception as e:
            logger.error(f"Fallback forecast failed: {str(e)}", exc_info=True)
            return {
                'historical': pd.DataFrame(),
                'forecast': pd.DataFrame(),
                'metrics': {},
                'metadata': {
                    'error': str(e),
                    'fallback': True
                }
            }