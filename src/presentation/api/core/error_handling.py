"""
Centralized error handling for API endpoints.
Provides decorators and utilities for consistent error responses.
"""

from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException
import asyncpg
import logging

logger = logging.getLogger(__name__)


def handle_database_errors(func: Callable) -> Callable:
    """
    Decorator to handle database-related errors consistently.
    
    Converts database exceptions to appropriate HTTP responses.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncpg.PostgresConnectionError as e:
            logger.error(f"Database connection error: {e}")
            raise HTTPException(
                status_code=503,
                detail="Database connection unavailable. Please try again later."
            )
        except asyncpg.PostgresError as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Database operation failed."
            )
        except asyncpg.DataError as e:
            logger.error(f"Data validation error: {e}")
            raise HTTPException(
                status_code=400,
                detail="Invalid data provided."
            )
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
    
    return wrapper


def handle_api_errors(
    default_status: int = 500,
    default_message: str = "An error occurred"
) -> Callable:
    """
    Decorator factory for handling API errors with custom defaults.
    
    Args:
        default_status: Default HTTP status code for unhandled errors
        default_message: Default error message
        
    Usage:
        @handle_api_errors(default_status=503)
        async def my_endpoint():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTPExceptions as-is
                raise
            except ValueError as e:
                logger.error(f"Value error in {func.__name__}: {e}")
                raise HTTPException(status_code=400, detail=str(e))
            except KeyError as e:
                logger.error(f"Key error in {func.__name__}: {e}")
                raise HTTPException(status_code=400, detail=f"Missing required field: {e}")
            except Exception as e:
                logger.error(f"Unhandled error in {func.__name__}: {e}")
                raise HTTPException(
                    status_code=default_status,
                    detail=default_message if not str(e) else str(e)
                )
        
        return wrapper
    
    return decorator


class ErrorResponse:
    """Standard error response format."""
    
    @staticmethod
    def bad_request(detail: str = "Bad request") -> HTTPException:
        """400 Bad Request."""
        return HTTPException(status_code=400, detail=detail)
    
    @staticmethod
    def unauthorized(detail: str = "Unauthorized") -> HTTPException:
        """401 Unauthorized."""
        return HTTPException(status_code=401, detail=detail)
    
    @staticmethod
    def forbidden(detail: str = "Forbidden") -> HTTPException:
        """403 Forbidden."""
        return HTTPException(status_code=403, detail=detail)
    
    @staticmethod
    def not_found(resource: str = "Resource") -> HTTPException:
        """404 Not Found."""
        return HTTPException(status_code=404, detail=f"{resource} not found")
    
    @staticmethod
    def conflict(detail: str = "Conflict") -> HTTPException:
        """409 Conflict."""
        return HTTPException(status_code=409, detail=detail)
    
    @staticmethod
    def unprocessable_entity(detail: str = "Unprocessable entity") -> HTTPException:
        """422 Unprocessable Entity."""
        return HTTPException(status_code=422, detail=detail)
    
    @staticmethod
    def internal_server_error(detail: str = "Internal server error") -> HTTPException:
        """500 Internal Server Error."""
        return HTTPException(status_code=500, detail=detail)
    
    @staticmethod
    def service_unavailable(detail: str = "Service temporarily unavailable") -> HTTPException:
        """503 Service Unavailable."""
        return HTTPException(status_code=503, detail=detail)


# Export commonly used items
__all__ = [
    'handle_database_errors',
    'handle_api_errors',
    'ErrorResponse'
]