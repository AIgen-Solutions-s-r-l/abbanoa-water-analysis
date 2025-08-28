"""
Simple tests for consumption API routes.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime

from src.presentation.api.consumption_routes import router


def test_consumption_routes_import():
    """Test that consumption routes can be imported."""
    assert router is not None
    assert hasattr(router, 'routes')


def test_consumption_analytics_endpoint_exists():
    """Test that the consumption analytics endpoint is defined."""
    # Check if the route exists
    routes = [route for route in router.routes if route.path == "/consumption/analytics"]
    assert len(routes) > 0, "Analytics endpoint should exist"
    
    route = routes[0]
    assert route.methods == {"GET"}, "Analytics endpoint should be GET"


def test_consumption_summary_endpoint_exists():
    """Test that the consumption summary endpoint is defined."""
    # Check if the route exists
    routes = [route for route in router.routes if route.path == "/consumption/summary"]
    assert len(routes) > 0, "Summary endpoint should exist"
    
    route = routes[0]
    assert route.methods == {"GET"}, "Summary endpoint should be GET"


def test_consumption_districts_endpoint_exists():
    """Test that the consumption districts endpoint is defined."""
    # Check if the route exists
    routes = [route for route in router.routes if route.path == "/consumption/districts"]
    assert len(routes) > 0, "Districts endpoint should exist"
    
    route = routes[0]
    assert route.methods == {"GET"}, "Districts endpoint should be GET"


def test_consumption_timeline_endpoint_exists():
    """Test that the consumption timeline endpoint is defined."""
    # Check if the route exists
    routes = [route for route in router.routes if route.path == "/consumption/timeline"]
    assert len(routes) > 0, "Timeline endpoint should exist"
    
    route = routes[0]
    assert route.methods == {"GET"}, "Timeline endpoint should be GET"


def test_consumption_segments_endpoint_exists():
    """Test that the consumption segments endpoint is defined."""
    # Check if the route exists
    routes = [route for route in router.routes if route.path == "/consumption/segments"]
    assert len(routes) > 0, "Segments endpoint should exist"
    
    route = routes[0]
    assert route.methods == {"GET"}, "Segments endpoint should be GET"


def test_consumption_peak_demand_endpoint_exists():
    """Test that the consumption peak demand endpoint is defined."""
    # Check if the route exists
    routes = [route for route in router.routes if route.path == "/consumption/peak-demand"]
    assert len(routes) > 0, "Peak demand endpoint should exist"
    
    route = routes[0]
    assert route.methods == {"GET"}, "Peak demand endpoint should be GET"


def test_consumption_conservation_endpoint_exists():
    """Test that the consumption conservation endpoint is defined."""
    # Check if the route exists
    routes = [route for route in router.routes if route.path == "/consumption/conservation"]
    assert len(routes) > 0, "Conservation endpoint should exist"
    
    route = routes[0]
    assert route.methods == {"GET"}, "Conservation endpoint should be GET"


def test_get_consumption_service_function():
    """Test that get_consumption_service function exists and works."""
    from src.presentation.api.consumption_routes import get_consumption_service
    
    # Test that the function exists
    assert callable(get_consumption_service)
    
    # Test that it returns a ConsumptionService instance
    service = get_consumption_service()
    assert service is not None
    assert hasattr(service, 'get_consumption_analytics')
