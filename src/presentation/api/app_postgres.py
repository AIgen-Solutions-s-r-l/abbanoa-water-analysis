"""FastAPI application using PostgreSQL for local development - Refactored Version."""

import os
from datetime import datetime, timezone
import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Abbanoa Water Infrastructure API (PostgreSQL)",
    description="Local API using PostgreSQL for water infrastructure monitoring",
    version="1.0.0-local",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL connection details from environment
POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "172.17.0.1"),  # Docker host IP
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "database": os.getenv("POSTGRES_DB", "abbanoa_processing"),
    "user": os.getenv("POSTGRES_USER", "abbanoa_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "abbanoa_secure_pass"),
}

# Connection pool
pool: asyncpg.Pool = None


@app.on_event("startup")
async def startup_event():
    """Initialize database connection pool on startup."""
    global pool
    
    try:
        pool = await asyncpg.create_pool(**POSTGRES_CONFIG)
        app.state.pool = pool  # Store pool in app state for dependency injection
    except Exception as e:
        logger.warning(f"Failed to connect to database: {e}")
        if os.getenv("ENV", "development") != "development":
            raise
        else:
            logger.info("Running in development mode - continuing without database")
            pool = None
            app.state.pool = None
    
    # Include user routes
    try:
        from .user_routes import router as user_router
        app.include_router(user_router)
        logger.info("User routes loaded successfully")
    except ImportError as e:
        logger.warning(f"User routes module not found: {e}")
    
    # Include weather routes
    try:
        from .endpoints.weather_router import router as weather_router
        app.include_router(weather_router)
        logger.info("Weather routes loaded successfully")
    except ImportError as e:
        logger.warning(f"Weather routes module not found: {e}")
    
    # Include consumption routes
    try:
        from .modules.consumption_routes import router as consumption_router
        app.include_router(consumption_router)
        logger.info("Consumption routes loaded successfully")
    except ImportError as e:
        logger.warning(f"Consumption routes module not found: {e}")
    
    # Include anomaly routes
    try:
        from .endpoints.anomaly_router import router as anomaly_router
        app.include_router(anomaly_router)
        logger.info("Anomaly routes loaded successfully")
    except ImportError as e:
        logger.warning(f"Anomaly routes module not found: {e}")
    
    # Include dashboard routes
    try:
        from .endpoints.dashboard_router import router as dashboard_router
        app.include_router(dashboard_router)
        logger.info("Dashboard routes loaded successfully")
    except ImportError as e:
        logger.warning(f"Dashboard routes module not found: {e}")
    
    # Include pressure routes
    try:
        from .endpoints.pressure_router import router as pressure_router
        app.include_router(pressure_router)
        logger.info("Pressure routes loaded successfully")
    except ImportError as e:
        logger.warning(f"Pressure routes module not found: {e}")
    
    # Include infrastructure routes
    try:
        from .endpoints.infrastructure_router import router as infrastructure_router
        app.include_router(infrastructure_router)
        logger.info("Infrastructure routes loaded successfully")
    except ImportError as e:
        logger.warning(f"Infrastructure routes module not found: {e}")
    
    print(f"Connected to PostgreSQL at {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection pool on shutdown."""
    global pool
    if pool:
        await pool.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-local",
        "database": "PostgreSQL"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        if pool:
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint."""
    return {
        "api": "Abbanoa Water Infrastructure API",
        "version": "1.0.0-local",
        "environment": "development",
        "database": "PostgreSQL",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }
