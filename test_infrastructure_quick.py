"""Quick test to verify infrastructure implementation."""

import sys
import asyncio
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone

# Add project to path
sys.path.insert(0, '/root/abbanoa-water-analysis')

from src.presentation.api.endpoints import infrastructure_router

async def test_no_mock_function():
    """Verify mock function is removed."""
    assert not hasattr(infrastructure_router, 'get_mock_infrastructure_data'), "Mock function should be removed"
    assert not hasattr(infrastructure_router, 'FIXED_NODE_COORDINATES'), "Fixed coordinates should be removed"
    print("✓ Mock data function and constants removed")

async def test_pipes_function_exists():
    """Verify pipes function exists."""
    assert hasattr(infrastructure_router, 'get_pipes_data'), "get_pipes_data function should exist"
    
    # Test with mock connection
    mock_conn = MagicMock()
    mock_conn.fetch = AsyncMock(return_value=[])
    
    result = await infrastructure_router.get_pipes_data(mock_conn, [])
    assert isinstance(result, list), "Should return a list"
    print("✓ Pipes function exists and works")

async def test_error_handling():
    """Verify proper error handling."""
    from fastapi import HTTPException
    
    # Mock get_db_connection to return None
    original_get_db = infrastructure_router.get_db_connection
    infrastructure_router.get_db_connection = AsyncMock(return_value=None)
    
    try:
        await infrastructure_router.get_infrastructure_map_data()
        assert False, "Should have raised HTTPException"
    except HTTPException as e:
        assert e.status_code == 503, f"Expected 503, got {e.status_code}"
        assert "Database connection unavailable" in str(e.detail)
        print("✓ Returns 503 when database unavailable")
    finally:
        infrastructure_router.get_db_connection = original_get_db

async def main():
    """Run all tests."""
    print("Running infrastructure tests...")
    await test_no_mock_function()
    await test_pipes_function_exists()
    await test_error_handling()
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(main())