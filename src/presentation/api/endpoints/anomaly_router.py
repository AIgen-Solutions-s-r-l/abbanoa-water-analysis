"""Anomaly detection API endpoints."""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
import asyncpg
import os
import logging

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from src.application.anomaly_detector import AnomalyDetector

router = APIRouter(prefix="/api/v1", tags=["anomalies"])
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', '5432')),
    'database': os.getenv('POSTGRES_DB', 'abbanoa_processing'),
    'user': os.getenv('POSTGRES_USER', 'abbanoa_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'abbanoa_secure_pass')
}


async def get_db_connection():
    """Get database connection."""
    return await asyncpg.connect(**DB_CONFIG)


@router.get("/anomalies")
async def get_anomalies(
    hours: int = Query(24, description="Hours to look back"),
    node_id: Optional[str] = Query(None, description="Filter by node ID"),
    severity: Optional[str] = Query(None, description="Filter by severity")
) -> List[Dict[str, Any]]:
    """Get recent anomalies."""
    try:
        conn = await get_db_connection()
        
        # Build the query with filters
        query = """
            SELECT 
                a.anomaly_id as id,
                a.node_id,
                n.node_name,
                a.timestamp,
                a.anomaly_type,
                a.severity,
                a.measurement_type,
                a.actual_value,
                a.expected_value,
                a.deviation_percentage,
                COALESCE(a.metadata->>'description', a.anomaly_type || ' anomaly detected') as description,
                a.resolved_at,
                COALESCE(a.metadata->>'confidence', '0.85') as confidence
            FROM water_infrastructure.anomalies a
            JOIN water_infrastructure.nodes n ON a.node_id = n.node_id
            WHERE a.timestamp > NOW() - INTERVAL '1 hour' * $1
        """
        
        params = [hours]
        param_count = 1
        
        if node_id is not None:
            param_count += 1
            query += f" AND a.node_id = ${param_count}"
            params.append(str(node_id))
            
        if severity is not None:
            param_count += 1
            query += f" AND a.severity = ${param_count}"
            params.append(str(severity))
            
        query += " ORDER BY a.timestamp DESC"
        
        anomalies_data = await conn.fetch(query, *params)
        
        # Transform anomalies data
        anomalies = []
        for row in anomalies_data:
            anomalies.append({
                "id": row['id'],
                "node_id": row['node_id'],
                "node_name": row['node_name'],
                "timestamp": row['timestamp'].isoformat(),
                "anomaly_type": row['anomaly_type'],
                "severity": row['severity'],
                "measurement_type": row['measurement_type'],
                "actual_value": float(row['actual_value']) if row['actual_value'] else None,
                "expected_value": float(row['expected_value']) if row['expected_value'] else None,
                "deviation_percentage": float(row['deviation_percentage']) if row['deviation_percentage'] else 0.0,
                "description": row['description'],
                "resolved_at": row['resolved_at'].isoformat() if row['resolved_at'] else None,
                "confidence": float(row['confidence'])
            })
        
        await conn.close()
        
        # Return only real data from database
        return anomalies
        
    except Exception as e:
        logger.error(f"Error fetching anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/anomalies/detect")
async def detect_anomalies(
    background_tasks: BackgroundTasks,
    node_id: Optional[str] = Query(None, description="Node ID to analyze"),
    hours: int = Query(24, description="Hours of data to analyze")
) -> Dict[str, Any]:
    """Trigger anomaly detection for specified nodes."""
    try:
        conn = await get_db_connection()
        detector = AnomalyDetector(conn)
        
        # If no node specified, analyze all nodes
        if node_id:
            nodes = [node_id]
        else:
            # Get all active nodes
            node_query = "SELECT node_id FROM water_infrastructure.nodes WHERE status = 'active'"
            node_rows = await conn.fetch(node_query)
            nodes = [row['node_id'] for row in node_rows]
        
        # Run detection for each node
        total_anomalies = 0
        results = []
        
        for node in nodes:
            anomalies = await detector.detect_anomalies(node, hours)
            total_anomalies += len(anomalies)
            if anomalies:
                results.append({
                    "node_id": node,
                    "anomalies_found": len(anomalies),
                    "severities": list(set(a['severity'] for a in anomalies))
                })
        
        await conn.close()
        
        return {
            "status": "completed",
            "nodes_analyzed": len(nodes),
            "total_anomalies_detected": total_anomalies,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error during anomaly detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomalies/statistics")
async def get_anomaly_statistics(
    days: int = Query(7, description="Number of days for statistics")
) -> Dict[str, Any]:
    """Get anomaly statistics and trends."""
    try:
        conn = await get_db_connection()
        
        # Get anomaly counts by type and severity
        stats_query = """
            SELECT 
                anomaly_type,
                severity,
                COUNT(*) as count,
                DATE(timestamp) as date
            FROM water_infrastructure.anomalies
            WHERE timestamp > NOW() - INTERVAL '1 day' * $1
            GROUP BY anomaly_type, severity, DATE(timestamp)
            ORDER BY date DESC, count DESC
        """
        
        stats_data = await conn.fetch(stats_query, days)
        
        # Get top affected nodes
        nodes_query = """
            SELECT 
                a.node_id,
                n.node_name,
                COUNT(*) as anomaly_count,
                array_agg(DISTINCT a.anomaly_type) as types
            FROM water_infrastructure.anomalies a
            JOIN water_infrastructure.nodes n ON a.node_id = n.node_id
            WHERE a.timestamp > NOW() - INTERVAL '1 day' * $1
            GROUP BY a.node_id, n.node_name
            ORDER BY anomaly_count DESC
            LIMIT 10
        """
        
        nodes_data = await conn.fetch(nodes_query, days)
        
        await conn.close()
        
        # Process statistics
        by_type = {}
        by_severity = {}
        timeline = {}
        
        for row in stats_data:
            # By type
            if row['anomaly_type'] not in by_type:
                by_type[row['anomaly_type']] = 0
            by_type[row['anomaly_type']] += row['count']
            
            # By severity
            if row['severity'] not in by_severity:
                by_severity[row['severity']] = 0
            by_severity[row['severity']] += row['count']
            
            # Timeline
            date_str = row['date'].isoformat()
            if date_str not in timeline:
                timeline[date_str] = 0
            timeline[date_str] += row['count']
        
        # Process top nodes
        top_nodes = []
        for row in nodes_data:
            top_nodes.append({
                "node_id": row['node_id'],
                "node_name": row['node_name'],
                "anomaly_count": row['anomaly_count'],
                "anomaly_types": list(row['types'])
            })
        
        return {
            "period_days": days,
            "total_anomalies": sum(by_type.values()),
            "by_type": by_type,
            "by_severity": by_severity,
            "timeline": timeline,
            "top_affected_nodes": top_nodes,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching anomaly statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 