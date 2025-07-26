"""FastAPI application using PostgreSQL for local development."""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncpg
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5434)),
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
    pool = await asyncpg.create_pool(**POSTGRES_CONFIG)
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
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        status = "healthy"
    except Exception as e:
        status = "unhealthy"
    
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-local"
    }


@app.get("/api/v1/nodes")
async def list_nodes():
    """List all monitoring nodes."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT node_id, name, node_type, is_active, location, metadata, created_at
                FROM water_infrastructure.nodes
                WHERE is_active = true
                ORDER BY name
            """)
            
            nodes = []
            for row in rows:
                nodes.append({
                    "id": row["node_id"],
                    "name": row["name"],
                    "location": {
                        "site_name": row["name"].split()[0],  # Extract area from name
                        "area": "Sardinia",
                        "coordinates": row["location"] if row["location"] else {}
                    },
                    "node_type": row["node_type"],
                    "status": "active" if row["is_active"] else "inactive",
                    "description": f"Monitoring station - {row['node_id']}"
                })
            
            return nodes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/dashboard/summary")
async def get_dashboard_summary():
    """Get dashboard summary data."""
    try:
        async with pool.acquire() as conn:
            # Get active nodes count
            node_count = await conn.fetchval("""
                SELECT COUNT(*) FROM water_infrastructure.nodes WHERE is_active = true
            """)
            
            # Get latest readings
            latest_readings = await conn.fetch("""
                SELECT n.node_id, n.name, sr.flow_rate, sr.pressure, sr.temperature
                FROM water_infrastructure.nodes n
                LEFT JOIN LATERAL (
                    SELECT flow_rate, pressure, temperature
                    FROM water_infrastructure.sensor_readings
                    WHERE node_id = n.node_id
                    ORDER BY timestamp DESC
                    LIMIT 1
                ) sr ON true
                WHERE n.is_active = true
            """)
            
            # Get anomaly count
            anomaly_count = await conn.fetchval("""
                SELECT COUNT(*) 
                FROM water_infrastructure.anomalies 
                WHERE timestamp > NOW() - INTERVAL '24 hours'
                AND resolved_at IS NULL
            """)
            
            # Build response
            nodes = []
            total_flow = 0.0
            total_pressure = 0.0
            pressure_count = 0
            
            for row in latest_readings:
                node_data = {
                    "node_id": row["node_id"],
                    "node_name": row["name"],
                    "flow_rate": float(row["flow_rate"]) if row["flow_rate"] else 0.0,
                    "pressure": float(row["pressure"]) if row["pressure"] else 0.0,
                    "anomaly_count": 0,
                    "quality_score": 0.95
                }
                nodes.append(node_data)
                
                if row["flow_rate"]:
                    total_flow += float(row["flow_rate"])
                if row["pressure"]:
                    total_pressure += float(row["pressure"])
                    pressure_count += 1
            
            avg_pressure = total_pressure / pressure_count if pressure_count > 0 else 0
            
            return {
                "nodes": nodes,
                "network": {
                    "active_nodes": node_count,
                    "total_flow": round(total_flow, 2),
                    "avg_pressure": round(avg_pressure, 2),
                    "total_volume_m3": round(total_flow * 3.6, 2),  # Convert L/s to m³/h
                    "anomaly_count": anomaly_count or 0
                },
                "recent_anomalies": anomaly_count or 0,
                "last_updated": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/anomalies")
async def get_anomalies():
    """Get recent anomalies."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    a.anomaly_id,
                    a.node_id,
                    n.name as node_name,
                    a.timestamp,
                    a.anomaly_type,
                    a.severity,
                    a.measurement_type,
                    a.actual_value,
                    a.expected_range,
                    a.deviation_percentage,
                    a.description,
                    a.resolved_at
                FROM water_infrastructure.anomalies a
                JOIN water_infrastructure.nodes n ON a.node_id = n.node_id
                WHERE a.timestamp > NOW() - INTERVAL '7 days'
                ORDER BY a.timestamp DESC
                LIMIT 100
            """)
            
            anomalies = []
            for row in rows:
                anomalies.append({
                    "id": f"anomaly_{row['anomaly_id']}",
                    "node_id": row["node_id"],
                    "node_name": row["node_name"],
                    "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                    "anomaly_type": row["anomaly_type"],
                    "severity": row["severity"],
                    "measurement_type": row["measurement_type"],
                    "actual_value": float(row["actual_value"]) if row["actual_value"] else None,
                    "expected_range": row["expected_range"],
                    "deviation_percentage": float(row["deviation_percentage"]) if row["deviation_percentage"] else None,
                    "description": row["description"],
                    "resolved_at": row["resolved_at"].isoformat() if row["resolved_at"] else None
                })
            
            # If no real anomalies, return a mock one
            if not anomalies:
                anomalies = [{
                    "id": "anomaly_mock_001",
                    "node_id": "node-001",
                    "node_name": "Selargius Monitoring Station",
                    "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                    "anomaly_type": "pressure_drop",
                    "severity": "warning",
                    "measurement_type": "pressure",
                    "actual_value": 1.8,
                    "expected_range": [2.0, 3.0],
                    "deviation_percentage": 10.0,
                    "description": "Pressure below expected range",
                    "resolved_at": None
                }]
            
            return anomalies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/nodes/{node_id}/readings")
async def get_node_readings(
    node_id: str,
    limit: int = Query(100, description="Maximum number of readings to return")
):
    """Get sensor readings for a specific node."""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT timestamp, flow_rate, pressure, temperature, volume
                FROM water_infrastructure.sensor_readings
                WHERE node_id = $1
                ORDER BY timestamp DESC
                LIMIT $2
            """, node_id, limit)
            
            readings = []
            for row in rows:
                readings.append({
                    "timestamp": row["timestamp"].isoformat(),
                    "flow_rate": float(row["flow_rate"]) if row["flow_rate"] else None,
                    "pressure": float(row["pressure"]) if row["pressure"] else None,
                    "temperature": float(row["temperature"]) if row["temperature"] else None,
                    "volume": float(row["volume"]) if row["volume"] else None
                })
            
            return readings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 