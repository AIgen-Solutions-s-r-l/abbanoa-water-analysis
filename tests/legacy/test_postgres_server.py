#!/usr/bin/env python3
"""
Simple test server for PostgreSQL connection and SQLAlchemy.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import our service
from src.infrastructure.database.consumption_service import ConsumptionService, ConsumptionServiceError

app = FastAPI(title="PostgreSQL Test API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "PostgreSQL Test API is running!"}

@app.get("/api/v1/consumption/analytics")
async def get_consumption_analytics():
    """Test endpoint for consumption analytics."""
    try:
        # Use SQLAlchemy service
        database_url = "postgresql://abbanoa_user:abbanoa_secure_pass@localhost:5432/abbanoa_processing"
        consumption_service = ConsumptionService(database_url)
        
        return consumption_service.get_consumption_analytics()
        
    except ConsumptionServiceError as e:
        return {"error": f"Service error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(
        "test_postgres_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
