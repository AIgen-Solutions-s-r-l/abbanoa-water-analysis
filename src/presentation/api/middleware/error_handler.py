"""Error handling middleware for the API."""

import logging
import traceback
from typing import Callable

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.shared.exceptions.forecast_exceptions import (
    ForecastNotFoundException,
    ForecastServiceException,
    ForecastTimeoutException,
    InvalidForecastRequestException,
)

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors and exceptions in a consistent way."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and handle any exceptions."""
        try:
            response = await call_next(request)
            return response

        except ForecastNotFoundException as e:
            logger.warning(f"Forecast not found: {str(e)}")
            return JSONResponse(
                status_code=404,
                content={
                    "error": "forecast_not_found",
                    "message": str(e),
                    "details": {
                        "district_id": e.district_id,
                        "metric": e.metric,
                        "horizon": e.horizon,
                    },
                },
            )

        except InvalidForecastRequestException as e:
            logger.warning(f"Invalid forecast request: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_request",
                    "message": str(e),
                    "details": {
                        "field": getattr(e, "field", "unknown"),
                        "value": getattr(e, "value", None),
                    },
                },
            )

        except ForecastTimeoutException as e:
            logger.error(f"Forecast timeout: {str(e)}")
            return JSONResponse(
                status_code=504,
                content={
                    "error": "forecast_timeout",
                    "message": "Forecast request timed out. Please try again.",
                    "details": {"timeout_ms": getattr(e, "timeout_ms", 5000)},
                },
            )

        except ForecastServiceException as e:
            logger.error(f"Forecast service error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=503,
                content={
                    "error": "service_error",
                    "message": "Forecast service is temporarily unavailable.",
                    "details": {
                        "service": getattr(e, "service", "forecast"),
                        "retry_after": 60,  # seconds
                    },
                },
            )

        except HTTPException:
            # Let FastAPI handle HTTP exceptions normally
            raise

        except Exception as e:
            # Log the full traceback for unexpected errors
            logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")

            # Return a generic error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_error",
                    "message": "An unexpected error occurred. Please try again later.",
                    "request_id": str(request.state.request_id)
                    if hasattr(request.state, "request_id")
                    else None,
                },
            )


def register_error_handlers(app):
    """Register custom error handlers with the FastAPI app."""

    @app.exception_handler(ForecastNotFoundException)
    async def forecast_not_found_handler(
        request: Request, exc: ForecastNotFoundException
    ):
        return JSONResponse(
            status_code=404,
            content={
                "error": "forecast_not_found",
                "message": str(exc),
                "details": {
                    "district_id": exc.district_id,
                    "metric": exc.metric,
                    "horizon": exc.horizon,
                },
            },
        )

    @app.exception_handler(InvalidForecastRequestException)
    async def invalid_request_handler(
        request: Request, exc: InvalidForecastRequestException
    ):
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_request",
                "message": str(exc),
                "details": {
                    "field": getattr(exc, "field", "unknown"),
                    "value": getattr(exc, "value", None),
                },
            },
        )

    @app.exception_handler(ForecastTimeoutException)
    async def timeout_handler(request: Request, exc: ForecastTimeoutException):
        return JSONResponse(
            status_code=504,
            content={
                "error": "timeout",
                "message": "Request timed out",
                "details": {"timeout_ms": getattr(exc, "timeout_ms", 5000)},
            },
        )

    @app.exception_handler(ForecastServiceException)
    async def service_error_handler(request: Request, exc: ForecastServiceException):
        return JSONResponse(
            status_code=503,
            content={
                "error": "service_unavailable",
                "message": "Service temporarily unavailable",
                "details": {
                    "service": getattr(exc, "service", "unknown"),
                    "retry_after": 60,
                },
            },
        )
