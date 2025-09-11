"""Database transaction management mixin"""

import asyncpg
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseTransactionMixin:
    """Mixin for safe database transactions with rollback"""
    
    @asynccontextmanager
    async def transaction(self):
        """Async context manager for database transactions with automatic rollback
        
        Usage:
            async with self.transaction() as conn:
                await conn.execute("INSERT ...")
                await conn.execute("UPDATE ...")
                # Automatic commit if no exception
                # Automatic rollback if exception occurs
        """
        conn = await self.pool.acquire()
        transaction = conn.transaction()
        
        try:
            await transaction.start()
            logger.debug("Transaction started")
            yield conn
            await transaction.commit()
            logger.debug("Transaction committed")
        except Exception as e:
            logger.error(f"Transaction failed, rolling back: {e}")
            await transaction.rollback()
            raise
        finally:
            await self.pool.release(conn)
    
    async def execute_with_retry(
        self,
        query: str,
        *args,
        max_retries: int = 3,
        retry_delay: float = 0.1
    ):
        """Execute query with retry logic
        
        Args:
            query: SQL query
            *args: Query parameters
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            Query result
        """
        import asyncio
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                async with self.pool.acquire() as conn:
                    return await conn.fetch(query, *args)
            except (asyncpg.ConnectionError, asyncpg.InterfaceError) as e:
                last_exception = e
                if attempt < max_retries:
                    logger.warning(f"Query failed (attempt {attempt + 1}), retrying: {e}")
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"Query failed after {max_retries + 1} attempts: {e}")
            except Exception as e:
                # Don't retry for other types of exceptions
                logger.error(f"Non-retryable error: {e}")
                raise
        
        raise last_exception
    
    async def batch_execute(self, operations: list):
        """Execute multiple operations in a single transaction
        
        Args:
            operations: List of (query, args) tuples
            
        Returns:
            List of results
        """
        results = []
        
        async with self.transaction() as conn:
            for query, args in operations:
                result = await conn.fetch(query, *args)
                results.append(result)
        
        return results