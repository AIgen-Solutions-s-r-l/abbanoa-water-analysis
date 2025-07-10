"""
Simple anomaly detector for the new sensor nodes.

This module provides direct anomaly detection on sensor_readings_ml data
without going through the UUID-based monitoring node system.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from google.cloud import bigquery
import streamlit as st
from src.presentation.streamlit.utils.node_mappings import ALL_NODE_MAPPINGS, NEW_NODES


class SimpleAnomalyDetector:
    """Simple anomaly detector that works directly with BigQuery data."""
    
    def __init__(self, client: Optional[bigquery.Client] = None):
        self.client = client or bigquery.Client(project="abbanoa-464816", location="EU")
        self.project_id = "abbanoa-464816"
        self.dataset_id = "water_infrastructure"
    
    def detect_anomalies(self, time_window_hours: int = 24) -> List[Dict]:
        """Detect anomalies in sensor data."""
        anomalies = []
        
        # Use historical data range
        end_time = datetime(2025, 3, 31, 23, 59, 59)
        start_time = end_time - timedelta(hours=time_window_hours)
        
        # Get numeric node IDs
        numeric_nodes = [nid for nid in NEW_NODES.values() if nid.isdigit()]
        
        for node_id in numeric_nodes:
            try:
                # Query for anomaly detection
                query = f"""
                WITH node_stats AS (
                    SELECT 
                        node_id,
                        timestamp,
                        flow_rate,
                        pressure,
                        temperature,
                        AVG(flow_rate) OVER (
                            PARTITION BY node_id 
                            ORDER BY timestamp 
                            ROWS BETWEEN 48 PRECEDING AND CURRENT ROW
                        ) as avg_flow,
                        STDDEV(flow_rate) OVER (
                            PARTITION BY node_id 
                            ORDER BY timestamp 
                            ROWS BETWEEN 48 PRECEDING AND CURRENT ROW
                        ) as stddev_flow,
                        AVG(pressure) OVER (
                            PARTITION BY node_id 
                            ORDER BY timestamp 
                            ROWS BETWEEN 48 PRECEDING AND CURRENT ROW
                        ) as avg_pressure,
                        STDDEV(pressure) OVER (
                            PARTITION BY node_id 
                            ORDER BY timestamp 
                            ROWS BETWEEN 48 PRECEDING AND CURRENT ROW
                        ) as stddev_pressure
                    FROM `{self.project_id}.{self.dataset_id}.sensor_readings_ml`
                    WHERE node_id = '{node_id}'
                        AND timestamp >= '{start_time.isoformat()}'
                        AND timestamp <= '{end_time.isoformat()}'
                        AND data_quality_score > 0.5
                )
                SELECT *
                FROM node_stats
                WHERE 
                    -- Flow anomalies
                    (flow_rate > avg_flow + 3 * stddev_flow AND flow_rate > 10)
                    OR (flow_rate < avg_flow - 3 * stddev_flow AND avg_flow > 5)
                    -- Pressure anomalies
                    OR (pressure > avg_pressure + 3 * stddev_pressure AND pressure > 0)
                    OR (pressure < avg_pressure - 3 * stddev_pressure AND avg_pressure > 2)
                    -- Zero flow when normally active
                    OR (flow_rate = 0 AND avg_flow > 5)
                ORDER BY timestamp DESC
                LIMIT 50
                """
                
                result = self.client.query(query).result()
                
                for row in result:
                    # Determine anomaly type and severity
                    anomaly_type = "unknown"
                    severity = "medium"
                    description = ""
                    
                    if row.flow_rate > row.avg_flow + 3 * row.stddev_flow:
                        anomaly_type = "high_flow"
                        severity = "high"
                        description = f"Flow spike: {row.flow_rate:.1f} L/s (normal: {row.avg_flow:.1f} L/s)"
                    elif row.flow_rate < row.avg_flow - 3 * row.stddev_flow:
                        anomaly_type = "low_flow"
                        severity = "medium"
                        description = f"Low flow: {row.flow_rate:.1f} L/s (normal: {row.avg_flow:.1f} L/s)"
                    elif row.flow_rate == 0 and row.avg_flow > 5:
                        anomaly_type = "no_flow"
                        severity = "high"
                        description = f"No flow detected (normal: {row.avg_flow:.1f} L/s)"
                    elif row.pressure > row.avg_pressure + 3 * row.stddev_pressure:
                        anomaly_type = "high_pressure"
                        severity = "high"
                        description = f"High pressure: {row.pressure:.1f} bar (normal: {row.avg_pressure:.1f} bar)"
                    elif row.pressure < row.avg_pressure - 3 * row.stddev_pressure:
                        anomaly_type = "low_pressure"
                        severity = "critical"
                        description = f"Low pressure: {row.pressure:.1f} bar (normal: {row.avg_pressure:.1f} bar)"
                    
                    # Get display name
                    display_name = f"Node {node_id}"
                    for name, nid in ALL_NODE_MAPPINGS.items():
                        if nid == node_id:
                            display_name = name
                            break
                    
                    anomalies.append({
                        "timestamp": row.timestamp,
                        "node_id": node_id,
                        "node_name": display_name,
                        "anomaly_type": anomaly_type,
                        "severity": severity,
                        "description": description,
                        "flow_rate": row.flow_rate,
                        "pressure": row.pressure,
                        "temperature": row.temperature,
                    })
                    
            except Exception as e:
                # Skip nodes with errors
                continue
        
        # Sort by timestamp descending
        anomalies.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return anomalies
    
    def get_anomaly_summary(self, time_window_hours: int = 24) -> Dict:
        """Get summary statistics for anomalies."""
        anomalies = self.detect_anomalies(time_window_hours)
        
        # Count by type
        type_counts = {}
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        node_counts = {}
        
        for anomaly in anomalies:
            # Type counts
            atype = anomaly["anomaly_type"]
            type_counts[atype] = type_counts.get(atype, 0) + 1
            
            # Severity counts
            severity = anomaly["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Node counts
            node = anomaly["node_name"]
            node_counts[node] = node_counts.get(node, 0) + 1
        
        return {
            "total_anomalies": len(anomalies),
            "type_counts": type_counts,
            "severity_counts": severity_counts,
            "node_counts": node_counts,
            "recent_anomalies": anomalies[:10]  # Top 10 most recent
        }