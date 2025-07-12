"""Enhanced logging configuration for forecast pipeline."""

import logging
import sys
from typing import Any, Dict

import structlog
from structlog.processors import (
    CallsiteParameter,
    CallsiteParameterAdder,
    JSONRenderer,
    TimeStamper,
    dict_tracebacks,
)


class ForecastLogger:
    """Enhanced logger for forecast pipeline with structured logging."""

    def __init__(self, name: str):
        """Initialize forecast logger with structured logging."""
        self.name = name
        self._configure_structlog()
        self.logger = structlog.get_logger(name)

    def _configure_structlog(self):
        """Configure structured logging with proper processors."""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                CallsiteParameterAdder(
                    parameters=[
                        CallsiteParameter.FILENAME,
                        CallsiteParameter.FUNC_NAME,
                        CallsiteParameter.LINENO,
                    ]
                ),
                dict_tracebacks,
                JSONRenderer()
                if sys.stdout.isatty()
                else structlog.dev.ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    def log_forecast_request(
        self, request_id: str, district_id: str, metric: str, horizon: int, **kwargs
    ):
        """Log forecast request with context."""
        self.logger.info(
            "forecast_request_started",
            request_id=request_id,
            district_id=district_id,
            metric=metric,
            horizon=horizon,
            **kwargs,
        )

    def log_bigquery_query(
        self, query_type: str, duration_ms: float, rows_returned: int, **kwargs
    ):
        """Log BigQuery query execution."""
        self.logger.info(
            "bigquery_query_executed",
            query_type=query_type,
            duration_ms=duration_ms,
            rows_returned=rows_returned,
            **kwargs,
        )

    def log_ml_model_call(
        self, model_name: str, status: str, duration_ms: float, **kwargs
    ):
        """Log ML model invocation."""
        level = "info" if status == "success" else "error"
        getattr(self.logger, level)(
            "ml_model_called",
            model_name=model_name,
            status=status,
            duration_ms=duration_ms,
            **kwargs,
        )

    def log_calculation_step(
        self,
        step_name: str,
        input_size: int,
        output_size: int,
        duration_ms: float,
        **kwargs,
    ):
        """Log calculation step execution."""
        self.logger.debug(
            "calculation_step_completed",
            step_name=step_name,
            input_size=input_size,
            output_size=output_size,
            duration_ms=duration_ms,
            **kwargs,
        )

    def log_error(
        self,
        error_type: str,
        error_message: str,
        error_context: Dict[str, Any],
        **kwargs,
    ):
        """Log error with full context."""
        self.logger.error(
            "forecast_error",
            error_type=error_type,
            error_message=error_message,
            error_context=error_context,
            **kwargs,
            exc_info=True,
        )

    def log_fallback_used(self, reason: str, fallback_method: str, **kwargs):
        """Log when fallback mechanism is used."""
        self.logger.warning(
            "fallback_mechanism_used",
            reason=reason,
            fallback_method=fallback_method,
            **kwargs,
        )

    def log_performance_metric(
        self, metric_name: str, value: float, unit: str, **kwargs
    ):
        """Log performance metrics."""
        self.logger.info(
            "performance_metric",
            metric_name=metric_name,
            value=value,
            unit=unit,
            **kwargs,
        )

    def log_data_quality_issue(
        self, issue_type: str, affected_records: int, severity: str, **kwargs
    ):
        """Log data quality issues."""
        self.logger.warning(
            "data_quality_issue",
            issue_type=issue_type,
            affected_records=affected_records,
            severity=severity,
            **kwargs,
        )


def get_forecast_logger(name: str) -> ForecastLogger:
    """Get or create a forecast logger instance."""
    return ForecastLogger(name)


# Configure root logger for the application
def configure_application_logging(log_level: str = "INFO"):
    """Configure application-wide logging settings."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            # Add file handler if needed
            # logging.FileHandler("forecast_pipeline.log")
        ],
    )

    # Set specific log levels for libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    # Enable debug logging for our modules
    logging.getLogger("src.infrastructure").setLevel(logging.DEBUG)
    logging.getLogger("src.application").setLevel(logging.DEBUG)
    logging.getLogger("src.presentation").setLevel(logging.DEBUG)
