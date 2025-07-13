"""
Core service layer for network efficiency analytics.

This service provides high-level business logic for network efficiency calculations,
connecting to the data layer and returning JSON-formatted results for the API.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncpg
from decimal import Decimal

from src.infrastructure.database.postgres_manager import get_postgres_manager

logger = logging.getLogger(__name__)


class EfficiencyService:
    """Service layer for network efficiency analytics."""
    
    def __init__(self):
        """Initialize the efficiency service."""
        self.postgres_manager = None
        
    async def initialize(self) -> None:
        """Initialize database connections."""
        self.postgres_manager = await get_postgres_manager()
        logger.info("Efficiency service initialized")
        
    async def get_efficiency_summary(
        self,
        time_range: str = "24h",
        node_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get network efficiency summary for specified time range and nodes.
        
        Args:
            time_range: Time range for analysis ("1h", "6h", "24h", "3d", "7d", "30d")
            node_ids: Optional list of specific node IDs to analyze
            
        Returns:
            Dictionary containing efficiency metrics and summary data
        """
        try:
            # Parse time range
            hours = self._parse_time_range(time_range)
            start_time = datetime.utcnow() - timedelta(hours=hours)
            end_time = datetime.utcnow()
            
            # Get aggregated data from sensor_readings_hourly
            async with self.postgres_manager.acquire() as conn:
                # Build query with optional node filtering
                node_filter = ""
                params = [start_time, end_time]
                
                if node_ids:
                    node_filter = f"AND node_id = ANY($3::text[])"
                    params.append(node_ids)
                
                query = f"""
                    SELECT 
                        node_id,
                        COUNT(*) as reading_count,
                        AVG(avg_flow_rate) as avg_flow_rate,
                        AVG(avg_pressure) as avg_pressure,
                        AVG(avg_temperature) as avg_temperature,
                        SUM(total_volume_m3) as total_volume,
                        AVG(avg_quality_score) as avg_quality_score,
                        MIN(bucket) as first_reading,
                        MAX(bucket) as last_reading
                    FROM water_infrastructure.sensor_readings_hourly
                    WHERE bucket >= $1 AND bucket <= $2
                    {node_filter}
                    GROUP BY node_id
                    ORDER BY avg_flow_rate DESC
                """
                
                node_data = await conn.fetch(query, *params)
                
                # Get node metadata
                node_metadata = await self._get_node_metadata(conn, node_ids)
                
                # Calculate system-wide metrics
                system_metrics = await self._calculate_system_metrics(conn, start_time, end_time, node_ids)
                
                # Calculate efficiency metrics
                efficiency_metrics = self._calculate_efficiency_metrics(node_data, hours)
                
                # Build response
                response = {
                    "summary": {
                        "time_range": time_range,
                        "period_start": start_time.isoformat(),
                        "period_end": end_time.isoformat(),
                        "total_nodes": len(node_data),
                        "active_nodes": len([n for n in node_data if n['avg_flow_rate'] and n['avg_flow_rate'] > 0]),
                        "analyzed_hours": hours
                    },
                    "efficiency_metrics": efficiency_metrics,
                    "system_metrics": system_metrics,
                    "node_performance": [
                        {
                            "node_id": str(node['node_id']),
                            "node_name": node_metadata.get(node['node_id'], {}).get('node_name', f"Node {node['node_id']}"),
                            "node_type": node_metadata.get(node['node_id'], {}).get('node_type', 'unknown'),
                            "reading_count": int(node['reading_count']),
                            "avg_flow_rate": float(node['avg_flow_rate'] or 0),
                            "avg_pressure": float(node['avg_pressure'] or 0),
                            "avg_temperature": float(node['avg_temperature'] or 0),
                            "total_volume_m3": float(node['total_volume'] or 0),
                            "avg_quality_score": float(node['avg_quality_score'] or 0),
                            "uptime_percentage": self._calculate_uptime_percentage(node, hours),
                            "first_reading": node['first_reading'].isoformat() if node['first_reading'] else None,
                            "last_reading": node['last_reading'].isoformat() if node['last_reading'] else None
                        }
                        for node in node_data
                    ],
                    "metadata": {
                        "generated_at": datetime.utcnow().isoformat(),
                        "data_source": "sensor_readings_hourly",
                        "version": "1.0"
                    }
                }
                
                return response
                
        except Exception as e:
            logger.error(f"Error getting efficiency summary: {e}")
            raise
            
    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to hours."""
        time_map = {
            "1h": 1,
            "6h": 6,
            "24h": 24,
            "3d": 72,
            "7d": 168,
            "30d": 720
        }
        
        if time_range not in time_map:
            raise ValueError(f"Invalid time range: {time_range}. Must be one of: {list(time_map.keys())}")
            
        return time_map[time_range]
        
    async def _get_node_metadata(self, conn: asyncpg.Connection, node_ids: Optional[List[str]]) -> Dict[str, Dict]:
        """Get node metadata from nodes table."""
        node_filter = ""
        params = []
        
        if node_ids:
            node_filter = "WHERE node_id = ANY($1::text[])"
            params.append(node_ids)
            
        query = f"""
            SELECT node_id, node_name, node_type, location_name, is_active
            FROM water_infrastructure.nodes
            {node_filter}
        """
        
        rows = await conn.fetch(query, *params)
        return {
            row['node_id']: {
                'node_name': row['node_name'],
                'node_type': row['node_type'],
                'location_name': row['location_name'],
                'is_active': row['is_active']
            }
            for row in rows
        }
        
    async def _calculate_system_metrics(
        self,
        conn: asyncpg.Connection,
        start_time: datetime,
        end_time: datetime,
        node_ids: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Calculate system-wide efficiency metrics."""
        node_filter = ""
        params = [start_time, end_time]
        
        if node_ids:
            node_filter = "AND node_id = ANY($3::text[])"
            params.append(node_ids)
            
        query = f"""
            SELECT 
                SUM(total_volume_m3) as total_system_volume,
                AVG(avg_flow_rate) as avg_system_flow_rate,
                AVG(avg_pressure) as avg_system_pressure,
                AVG(avg_quality_score) as avg_system_quality,
                COUNT(DISTINCT node_id) as active_nodes,
                SUM(reading_count) as total_readings
            FROM water_infrastructure.sensor_readings_hourly
            WHERE bucket >= $1 AND bucket <= $2
            {node_filter}
        """
        
        result = await conn.fetchrow(query, *params)
        
        return {
            "total_system_volume_m3": float(result['total_system_volume'] or 0),
            "avg_system_flow_rate": float(result['avg_system_flow_rate'] or 0),
            "avg_system_pressure": float(result['avg_system_pressure'] or 0),
            "avg_system_quality": float(result['avg_system_quality'] or 0),
            "active_nodes": int(result['active_nodes'] or 0),
            "total_readings": int(result['total_readings'] or 0)
        }
        
    def _calculate_efficiency_metrics(self, node_data: List[asyncpg.Record], hours: int) -> Dict[str, Any]:
        """Calculate efficiency metrics from node data."""
        if not node_data:
            return {
                "network_efficiency_percentage": 0,
                "total_throughput_m3h": 0,
                "average_pressure_bar": 0,
                "quality_score": 0,
                "operational_efficiency": 0
            }
            
        # Calculate total system throughput
        total_volume = sum(float(node['total_volume'] or 0) for node in node_data)
        total_throughput = total_volume / hours if hours > 0 else 0
        
        # Calculate average pressure
        pressures = [float(node['avg_pressure'] or 0) for node in node_data if node['avg_pressure']]
        avg_pressure = sum(pressures) / len(pressures) if pressures else 0
        
        # Calculate quality score
        quality_scores = [float(node['avg_quality_score'] or 0) for node in node_data if node['avg_quality_score']]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Calculate operational efficiency (percentage of nodes with good flow rates)
        active_nodes = len([n for n in node_data if n['avg_flow_rate'] and n['avg_flow_rate'] > 0])
        operational_efficiency = (active_nodes / len(node_data)) * 100 if node_data else 0
        
        # Network efficiency based on flow consistency and pressure optimization
        flow_rates = [float(node['avg_flow_rate'] or 0) for node in node_data if node['avg_flow_rate']]
        flow_consistency = 1 - (max(flow_rates) - min(flow_rates)) / (max(flow_rates) + min(flow_rates)) if len(flow_rates) > 1 and max(flow_rates) > 0 else 0
        
        network_efficiency = (
            (flow_consistency * 0.4) +
            (avg_quality * 0.3) +
            (min(avg_pressure / 10, 1) * 0.3)  # Normalize pressure to 0-1 scale
        ) * 100
        
        return {
            "network_efficiency_percentage": round(network_efficiency, 2),
            "total_throughput_m3h": round(total_throughput, 2),
            "average_pressure_bar": round(avg_pressure, 2),
            "quality_score": round(avg_quality, 3),
            "operational_efficiency": round(operational_efficiency, 2),
            "flow_consistency_score": round(flow_consistency, 3)
        }
        
    def _calculate_uptime_percentage(self, node: asyncpg.Record, hours: int) -> float:
        """Calculate uptime percentage for a node."""
        expected_readings = hours  # Expecting 1 reading per hour
        actual_readings = int(node['reading_count'])
        
        uptime = min((actual_readings / expected_readings) * 100, 100) if expected_readings > 0 else 0
        return round(uptime, 2) 