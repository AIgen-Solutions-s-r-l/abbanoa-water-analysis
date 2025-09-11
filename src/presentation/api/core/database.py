"""
Centralized database configuration and connection management.
This module eliminates duplication across API endpoints.
"""

import os
import asyncpg
from typing import Dict, Any, Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Centralized database configuration."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get database configuration from environment variables."""
        return {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', '5432')),
            'database': os.getenv('POSTGRES_DB', 'abbanoa_processing'),
            'user': os.getenv('POSTGRES_USER', 'abbanoa_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'abbanoa_secure_pass')
        }
    
    @staticmethod
    def get_connection_string() -> str:
        """Get PostgreSQL connection string."""
        config = DatabaseConfig.get_config()
        return (
            f"postgresql://{config['user']}:{config['password']}@"
            f"{config['host']}:{config['port']}/{config['database']}"
        )


async def get_db_connection() -> asyncpg.Connection:
    """
    Get a database connection using centralized configuration.
    
    Returns:
        asyncpg.Connection: Database connection
        
    Raises:
        asyncpg.PostgresError: If connection fails
    """
    config = DatabaseConfig.get_config()
    try:
        return await asyncpg.connect(**config)
    except asyncpg.PostgresError as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


async def get_db_pool(
    min_size: int = 10,
    max_size: int = 20,
    timeout: float = 60.0
) -> asyncpg.Pool:
    """
    Create a connection pool for better performance.
    
    Args:
        min_size: Minimum number of connections
        max_size: Maximum number of connections
        timeout: Connection timeout in seconds
        
    Returns:
        asyncpg.Pool: Connection pool
    """
    config = DatabaseConfig.get_config()
    return await asyncpg.create_pool(
        **config,
        min_size=min_size,
        max_size=max_size,
        timeout=timeout
    )


def with_db_connection(func):
    """
    Decorator that provides a database connection to the wrapped function.
    The connection is automatically closed after the function completes.
    
    Usage:
        @with_db_connection
        async def my_endpoint(conn: asyncpg.Connection, ...):
            result = await conn.fetch("SELECT ...")
            return result
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = await get_db_connection()
            # Inject connection as first argument
            result = await func(conn, *args, **kwargs)
            return result
        finally:
            if conn:
                await conn.close()
    
    return wrapper


class DatabaseConnectionManager:
    """
    Context manager for database connections.
    
    Usage:
        async with DatabaseConnectionManager() as conn:
            result = await conn.fetch("SELECT ...")
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize connection manager.
        
        Args:
            config: Optional custom configuration (uses default if None)
        """
        self.config = config or DatabaseConfig.get_config()
        self.conn = None
    
    async def __aenter__(self) -> asyncpg.Connection:
        """Acquire database connection."""
        self.conn = await asyncpg.connect(**self.config)
        return self.conn
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release database connection."""
        if self.conn:
            await self.conn.close()


# Export commonly used items
__all__ = [
    'DatabaseConfig',
    'get_db_connection',
    'get_db_pool',
    'with_db_connection',
    'DatabaseConnectionManager'
]