"""
FastAPI server for Abbanoa Water Analysis API
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from src.presentation.api.consumption_routes import router as consumption_router

# Create FastAPI app
app = FastAPI(
    title="Abbanoa Water Analysis API",
    description="API for water consumption analytics and infrastructure management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(consumption_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "Abbanoa Water Analysis API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "abbanoa-water-analysis-api"
    }

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting Abbanoa Water Analysis API on {host}:{port}")
    
    uvicorn.run(
        "sqlalchemy_server:app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
