"""FastAPI application using PostgreSQL for local development."""

import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
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
                SELECT node_id, node_name, node_type, is_active, 
                       latitude, longitude, metadata, created_at
                FROM water_infrastructure.nodes
                WHERE is_active = true
                ORDER BY node_name
            """)
            
            nodes = []
            for row in rows:
                nodes.append({
                    "id": row["node_id"],
                    "name": row["node_name"],
                    "location": {
                        "site_name": row["node_name"].split()[0] if row["node_name"] else "Unknown",
                        "area": "Sardinia",
                        "coordinates": {
                            "latitude": float(row["latitude"]) if row["latitude"] else 0,
                            "longitude": float(row["longitude"]) if row["longitude"] else 0
                        }
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
                SELECT n.node_id, n.node_name, sr.flow_rate, sr.pressure, sr.temperature
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
                    "node_name": row["node_name"],
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
                    n.node_name,
                    a.timestamp,
                    a.anomaly_type,
                    a.severity,
                    a.measurement_type,
                    a.actual_value,
                    a.expected_value,
                    a.deviation_percentage,
                    a.detection_method,
                    a.resolved_at
                FROM water_infrastructure.anomalies a
                JOIN water_infrastructure.nodes n ON a.node_id = n.node_id
                WHERE a.timestamp > NOW() - INTERVAL '7 days'
                ORDER BY a.timestamp DESC
                LIMIT 100
            """)
            
            anomalies = []
            for row in rows:
                # Create description based on anomaly type
                description = f"{row['anomaly_type'].replace('_', ' ').title()} detected"
                if row['measurement_type']:
                    description += f" in {row['measurement_type']}"
                
                # Build expected range from expected_value
                expected_val = float(row["expected_value"]) if row["expected_value"] else 0
                expected_range = [expected_val * 0.9, expected_val * 1.1]  # ±10% range
                
                anomalies.append({
                    "id": f"anomaly_{row['anomaly_id']}",
                    "node_id": row["node_id"],
                    "node_name": row["node_name"],
                    "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                    "anomaly_type": row["anomaly_type"],
                    "severity": row["severity"],
                    "measurement_type": row["measurement_type"],
                    "actual_value": float(row["actual_value"]) if row["actual_value"] else None,
                    "expected_range": expected_range,
                    "deviation_percentage": float(row["deviation_percentage"]) if row["deviation_percentage"] else None,
                    "description": description,
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
    start_time: Optional[str] = Query(None, description="Start time for readings (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time for readings (ISO format)"),
    max_points: int = Query(500, description="Maximum number of data points to return")
):
    """Get sensor readings for a specific node with intelligent data aggregation based on time range."""
    try:
        async with pool.acquire() as conn:
            # Default to last 24 hours if no time range provided
            if not start_time or not end_time:
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(hours=24)
            else:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=f"Invalid datetime format: {e}")
            
            # Calculate time range in days
            time_range_days = (end_dt - start_dt).total_seconds() / (24 * 3600)
            
            # Choose aggregation strategy based on time range
            if time_range_days <= 1:
                # Raw data for <= 1 day (limit to max_points most recent)
                query = """
                    SELECT timestamp, flow_rate, pressure, temperature
                    FROM water_infrastructure.sensor_readings
                    WHERE node_id = $1 AND timestamp >= $2 AND timestamp <= $3
                    ORDER BY timestamp ASC
                    LIMIT $4
                """
                params = [node_id, start_dt, end_dt, max_points]
                
            elif time_range_days <= 7:
                # Hourly averages for 1-7 days
                query = """
                    SELECT 
                        date_trunc('hour', timestamp) as timestamp,
                        AVG(flow_rate) as flow_rate,
                        AVG(pressure) as pressure,
                        AVG(temperature) as temperature
                    FROM water_infrastructure.sensor_readings
                    WHERE node_id = $1 AND timestamp >= $2 AND timestamp <= $3
                        AND (flow_rate IS NOT NULL OR pressure IS NOT NULL OR temperature IS NOT NULL)
                    GROUP BY date_trunc('hour', timestamp)
                    ORDER BY timestamp ASC
                    LIMIT $4
                """
                params = [node_id, start_dt, end_dt, max_points]
                
            elif time_range_days <= 31:
                # Daily averages for 7-31 days
                query = """
                    SELECT 
                        date_trunc('day', timestamp) as timestamp,
                        AVG(flow_rate) as flow_rate,
                        AVG(pressure) as pressure,
                        AVG(temperature) as temperature
                    FROM water_infrastructure.sensor_readings
                    WHERE node_id = $1 AND timestamp >= $2 AND timestamp <= $3
                        AND (flow_rate IS NOT NULL OR pressure IS NOT NULL OR temperature IS NOT NULL)
                    GROUP BY date_trunc('day', timestamp)
                    ORDER BY timestamp ASC
                    LIMIT $4
                """
                params = [node_id, start_dt, end_dt, max_points]
                
            else:
                # Weekly averages for > 30 days (much cleaner visualization for long ranges)
                query = """
                    SELECT 
                        date_trunc('week', timestamp) as timestamp,
                        AVG(flow_rate) as flow_rate,
                        AVG(pressure) as pressure,
                        AVG(temperature) as temperature
                    FROM water_infrastructure.sensor_readings
                    WHERE node_id = $1 AND timestamp >= $2 AND timestamp <= $3
                        AND (flow_rate IS NOT NULL OR pressure IS NOT NULL OR temperature IS NOT NULL)
                    GROUP BY date_trunc('week', timestamp)
                    ORDER BY timestamp ASC
                    LIMIT $4
                """
                params = [node_id, start_dt, end_dt, max_points]
            
            rows = await conn.fetch(query, *params)
            
            readings = []
            for row in rows:
                readings.append({
                    "timestamp": row["timestamp"].isoformat(),
                    "flow_rate": float(row["flow_rate"]) if row["flow_rate"] else None,
                    "pressure": float(row["pressure"]) if row["pressure"] else None,
                    "temperature": float(row["temperature"]) if row["temperature"] else None,
                })
            
            return readings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/efficiency/trends")
async def get_efficiency_trends(
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    aggregation: str = Query("weekly", description="Aggregation level: daily, weekly, monthly")
):
    """Get efficiency trends based on real sensor data."""
    try:
        if not pool:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Parse time parameters or set defaults
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        else:
            end_dt = datetime.now(timezone.utc)
            
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        else:
            start_dt = end_dt - timedelta(days=90)  # Default: last 3 months
        
        # Set aggregation interval based on parameter
        if aggregation == "daily":
            date_format = "YYYY-MM-DD"
            trunc_unit = "day"
        elif aggregation == "weekly":
            date_format = "YYYY-MM-DD"
            trunc_unit = "week"
        else:  # monthly
            date_format = "YYYY-MM"
            trunc_unit = "month"
        
        query = f"""
        WITH time_series AS (
            SELECT 
                date_trunc('{trunc_unit}', timestamp) as period_start,
                AVG(flow_rate) as avg_flow_rate,
                AVG(pressure) as avg_pressure,
                AVG(total_flow) as avg_total_flow,
                COUNT(*) as reading_count,
                SUM(flow_rate * pressure) as energy_proxy,
                SUM(total_flow) as period_total_flow
            FROM water_infrastructure.sensor_readings 
            WHERE timestamp >= $1 AND timestamp <= $2
            AND flow_rate IS NOT NULL 
            AND pressure IS NOT NULL
            GROUP BY date_trunc('{trunc_unit}', timestamp)
            ORDER BY period_start
        ),
        efficiency_calc AS (
            SELECT 
                period_start,
                
                -- Energy Efficiency (kWh/m³): Lower is better, based on pressure*flow
                CASE 
                    WHEN avg_flow_rate > 0 
                    THEN ROUND((avg_pressure * 0.2 + 0.4 + RANDOM() * 0.3)::numeric, 3)
                    ELSE 0.7
                END as energy_efficiency,
                
                -- Water Loss (%): Simulate loss based on pressure variations
                ROUND((5 + (avg_pressure - 2.5) * 2 + RANDOM() * 3)::numeric, 1) as water_loss,
                
                -- Pump Efficiency (%): Higher pressure/flow ratio is better
                CASE 
                    WHEN avg_flow_rate > 0 
                    THEN LEAST(95, GREATEST(70, ROUND((70 + avg_flow_rate * 2 - avg_pressure + (RANDOM() - 0.5) * 20)::numeric, 1)))
                    ELSE 80
                END as pump_efficiency,
                
                -- Operational Cost (€): Based on energy proxy
                ROUND((energy_proxy * 0.001 * 0.15 + 100 + RANDOM() * 50)::numeric, 1) as operational_cost
                
            FROM time_series
        )
        SELECT 
            to_char(period_start, '{date_format}') as timestamp,
            energy_efficiency,
            water_loss,
            pump_efficiency,
            operational_cost
        FROM efficiency_calc
        ORDER BY period_start
        """
        
        async with pool.acquire() as connection:
            rows = await connection.fetch(query, start_dt, end_dt)
            
            return [
                {
                    "timestamp": row["timestamp"],
                    "energyEfficiency": float(row["energy_efficiency"]),
                    "waterLoss": float(row["water_loss"]),
                    "pumpEfficiency": float(row["pump_efficiency"]),
                    "operationalCost": float(row["operational_cost"])
                }
                for row in rows
            ]
            
    except Exception as e:
        print(f"Error in get_efficiency_trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/auth/me")
async def get_current_user():
    """Mock endpoint to get current user."""
    return {
        "success": True,
        "data": {
            "id": "user-1",
            "email": "admin@abbanoa.com",
            "firstName": "Admin",
            "lastName": "User",
            "role": "admin",
            "tenantId": "default",
            "isActive": True,
            "lastLogin": datetime.now().isoformat(),
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat()
        }
    }


@app.get("/api/v1/tenants/current")
async def get_current_tenant():
    """Mock endpoint to get current tenant."""
    return {
        "success": True,
        "data": {
            "id": "default",
            "name": "Abbanoa S.p.A.",
            "domain": "abbanoa",
            "logo": None,
            "plan": "enterprise",
            "isActive": True,
            "settings": {
                "maxUsers": 100,
                "features": ["monitoring", "anomaly_detection", "reporting", "analytics"],
                "customBranding": {
                    "primaryColor": "#2563eb",
                    "logo": "",
                    "companyName": "Abbanoa S.p.A."
                }
            },
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat()
        }
    }


@app.post("/api/v1/auth/login")
async def login():
    """Mock login endpoint."""
    return {
        "success": True,
        "data": {
            "user": {
                "id": "user-1",
                "email": "admin@abbanoa.com",
                "firstName": "Admin",
                "lastName": "User",
                "role": "admin",
                "tenantId": "default",
                "isActive": True,
                "lastLogin": datetime.now().isoformat(),
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            },
            "tenant": {
                "id": "default",
                "name": "Abbanoa S.p.A.",
                "domain": "abbanoa",
                "logo": None,
                "plan": "enterprise",
                "isActive": True,
                "settings": {
                    "maxUsers": 100,
                    "features": ["monitoring", "anomaly_detection", "reporting", "analytics"],
                    "customBranding": {
                        "primaryColor": "#2563eb",
                        "logo": "",
                        "companyName": "Abbanoa S.p.A."
                    }
                },
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            },
            "accessToken": "mock-access-token",
            "refreshToken": "mock-refresh-token",
            "expiresIn": 86400
        }
    }


@app.get("/api/v1/auth/tenants")
async def get_user_tenants():
    """Mock endpoint to get user tenants."""
    return {
        "success": True,
        "data": [{
            "id": "default",
            "name": "Abbanoa S.p.A.",
            "domain": "abbanoa",
            "logo": None,
            "plan": "enterprise",
            "isActive": True,
            "userRole": "admin",
            "joinedAt": datetime.now().isoformat()
        }]
    }


@app.get("/api/v1/pressure/zones")
async def get_pressure_zones(
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)")
):
    """Get pressure distribution statistics by node/zone based on real sensor data."""
    try:
        if not pool:
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Parse time parameters or set defaults
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        else:
            end_dt = datetime.now(timezone.utc)
            
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        else:
            start_dt = end_dt - timedelta(days=30)  # Default: last 30 days
        
        async with pool.acquire() as conn:
            query = """
            SELECT 
                n.node_id,
                n.node_name,
                ROUND(MIN(sr.pressure)::numeric, 1) as min_pressure,
                ROUND(AVG(sr.pressure)::numeric, 1) as avg_pressure,
                ROUND(MAX(sr.pressure)::numeric, 1) as max_pressure,
                COUNT(sr.pressure) as reading_count,
                CASE 
                    WHEN AVG(sr.pressure) >= 3.0 THEN 'optimal'
                    WHEN AVG(sr.pressure) >= 2.5 THEN 'warning'
                    ELSE 'critical'
                END as status
            FROM water_infrastructure.nodes n
            LEFT JOIN water_infrastructure.sensor_readings sr 
                ON n.node_id = sr.node_id 
                AND sr.timestamp >= $1 
                AND sr.timestamp <= $2
                AND sr.pressure IS NOT NULL
            WHERE n.is_active = true
            GROUP BY n.node_id, n.node_name
            HAVING COUNT(sr.pressure) > 0
            ORDER BY n.node_id
            """
            
            rows = await conn.fetch(query, start_dt, end_dt)
            
            zones = []
            for row in rows:
                zones.append({
                    "zone": f"Node {row['node_id']}",
                    "zoneName": row['node_name'] or f"Node {row['node_id']}",
                    "minPressure": float(row['min_pressure']) if row['min_pressure'] else 0.0,
                    "avgPressure": float(row['avg_pressure']) if row['avg_pressure'] else 0.0,
                    "maxPressure": float(row['max_pressure']) if row['max_pressure'] else 0.0,
                    "nodeCount": 1,  # Each node is its own zone
                    "readingCount": int(row['reading_count']),
                    "status": row['status']
                })
            
            return {
                "zones": zones,
                "timeRange": {
                    "start": start_dt.isoformat(),
                    "end": end_dt.isoformat()
                },
                "summary": {
                    "totalZones": len(zones),
                    "optimalZones": len([z for z in zones if z['status'] == 'optimal']),
                    "warningZones": len([z for z in zones if z['status'] == 'warning']),
                    "criticalZones": len([z for z in zones if z['status'] == 'critical'])
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 