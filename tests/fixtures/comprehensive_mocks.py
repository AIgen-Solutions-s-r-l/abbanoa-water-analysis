"""
Comprehensive mock fixtures for dashboard and anomalies APIs.
These fixtures match the complete production DTOs structure.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock


class ComprehensiveMockFixtures:
    """Provides comprehensive mock data matching production DTOs."""
    
    @staticmethod
    def get_dashboard_mock_data(
        include_nulls: bool = False,
        empty_arrays: bool = False,
        edge_case: str = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive dashboard mock data.
        
        Args:
            include_nulls: Include null values for optional fields
            empty_arrays: Return empty arrays for collections
            edge_case: Specific edge case to test ('no_data', 'partial_data', 'max_values')
        """
        base_time = datetime.now(timezone.utc)
        
        if edge_case == 'no_data':
            return {
                "success": True,
                "data": {
                    "overview": {
                        "totalConsumption": 0.0,
                        "activeConnections": 0,
                        "anomalies": 0,
                        "efficiency": 0.0,
                        "lastUpdate": base_time.isoformat()
                    },
                    "metrics": {
                        "flowRate": {
                            "current": 0.0,
                            "average": 0.0,
                            "peak": 0.0
                        },
                        "pressure": {
                            "current": 0.0,
                            "average": 0.0,
                            "minimum": 0.0
                        },
                        "quality": {
                            "score": 0.0,
                            "status": "Unknown"
                        }
                    },
                    "nodes": [],
                    "network": {
                        "active_nodes": 0,
                        "total_flow_lps": 0.0,
                        "average_pressure_bar": 0.0,
                        "total_volume_m3": 0.0,
                        "anomaly_count": 0,
                        "efficiency_percentage": 0.0,
                        "alert_count": 0,
                        "energy_consumption_kwh": 0.0,
                        "water_quality_index": 0.0,
                        "active_connections": 0
                    },
                    "recent_anomalies": 0,
                    "total_consumption": 0.0,
                    "system_health": 0.0,
                    "last_updated": base_time.isoformat(),
                    "data_timestamp": None,
                    "data_note": "No data available"
                }
            }
        
        # Standard mock data with all fields
        nodes_data = []
        if not empty_arrays:
            for i in range(5):
                nodes_data.append({
                    "node_id": f"TEST_NODE_{i+1}",
                    "node_name": f"Test Node {i+1}",
                    "flow_rate": 10.5 + i * 2.3 if not include_nulls else (None if i % 2 == 0 else 10.5),
                    "pressure": 3.2 + i * 0.1 if not include_nulls else (None if i % 3 == 0 else 3.2),
                    "temperature": 18.5 + i * 0.5,
                    "anomaly_count": i % 2,
                    "quality_score": 0.95 - i * 0.02,
                    "last_reading": (base_time - timedelta(minutes=i*5)).isoformat() if not include_nulls else None
                })
        
        if edge_case == 'max_values':
            # Test with maximum/extreme values
            total_consumption = 999999999.99
            active_connections = 10000
            anomalies = 999
            efficiency = 100.0
            flow_rate = 9999.99
            pressure = 10.0
        elif edge_case == 'partial_data':
            # Some fields with data, some without
            total_consumption = 50000.0
            active_connections = 5
            anomalies = 0
            efficiency = None if include_nulls else 75.0
            flow_rate = 15.3
            pressure = None if include_nulls else 3.0
        else:
            # Normal values
            total_consumption = 125000.5
            active_connections = 42
            anomalies = 3
            efficiency = 87.5
            flow_rate = 45.7
            pressure = 3.5
        
        return {
            "success": True,
            "data": {
                "overview": {
                    "totalConsumption": total_consumption,
                    "activeConnections": active_connections,
                    "anomalies": anomalies,
                    "efficiency": efficiency,
                    "lastUpdate": base_time.isoformat()
                },
                "metrics": {
                    "flowRate": {
                        "current": flow_rate,
                        "average": flow_rate * 0.95,
                        "peak": flow_rate * 1.2
                    },
                    "pressure": {
                        "current": pressure,
                        "average": pressure,
                        "minimum": pressure * 0.9 if pressure else 0.0
                    },
                    "quality": {
                        "score": 95.0,
                        "status": "Good"
                    }
                },
                "nodes": nodes_data,
                "network": {
                    "active_nodes": len(nodes_data),
                    "total_flow_lps": flow_rate,
                    "average_pressure_bar": pressure,
                    "total_volume_m3": total_consumption / 1000,
                    "anomaly_count": anomalies,
                    "efficiency_percentage": efficiency,
                    "alert_count": anomalies,
                    "energy_consumption_kwh": flow_rate * 0.5 if flow_rate else 0.0,
                    "water_quality_index": 95.0,
                    "active_connections": active_connections
                },
                "recent_anomalies": anomalies,
                "total_consumption": total_consumption,
                "system_health": efficiency,
                "last_updated": base_time.isoformat(),
                "data_timestamp": (base_time - timedelta(minutes=5)).isoformat() if not include_nulls else None,
                "data_note": "Showing latest available historical data from September 2025"
            }
        }
    
    @staticmethod
    def get_anomalies_mock_data(
        count: int = 5,
        include_nulls: bool = False,
        empty_array: bool = False,
        edge_case: str = None
    ) -> List[Dict[str, Any]]:
        """
        Generate comprehensive anomalies mock data.
        
        Args:
            count: Number of anomalies to generate
            include_nulls: Include null values for optional fields
            empty_array: Return empty array
            edge_case: Specific edge case ('resolved', 'critical', 'mixed_severity')
        """
        if empty_array:
            return []
        
        base_time = datetime.now(timezone.utc)
        anomalies = []
        
        severities = ['low', 'medium', 'high', 'critical']
        anomaly_types = ['pressure_drop', 'flow_spike', 'temperature_anomaly', 'quality_issue', 'sensor_failure']
        measurement_types = ['pressure', 'flow_rate', 'temperature', 'ph', 'turbidity']
        
        for i in range(count):
            if edge_case == 'critical':
                severity = 'critical'
                anomaly_type = 'sensor_failure'
            elif edge_case == 'resolved':
                severity = 'low'
                resolved_at = (base_time - timedelta(hours=i+1)).isoformat()
            elif edge_case == 'mixed_severity':
                severity = severities[i % len(severities)]
                resolved_at = (base_time - timedelta(hours=i+1)).isoformat() if i % 2 == 0 else None
            else:
                severity = severities[i % len(severities)]
                resolved_at = None
            
            anomaly = {
                "id": f"TEST_ANOM_{i+1}",
                "node_id": f"TEST_NODE_{(i % 5) + 1}",
                "node_name": f"Test Node {(i % 5) + 1}",
                "timestamp": (base_time - timedelta(hours=i*2)).isoformat(),
                "anomaly_type": anomaly_types[i % len(anomaly_types)],
                "severity": severity,
                "measurement_type": measurement_types[i % len(measurement_types)],
                "actual_value": 2.1 + i * 0.3 if not include_nulls else None,
                "expected_value": 3.5 if not include_nulls else None,
                "deviation_percentage": 15.5 + i * 2.1 if not include_nulls else 0.0,
                "description": f"Test {anomaly_types[i % len(anomaly_types)]} anomaly detected",
                "resolved_at": resolved_at if edge_case == 'resolved' else (None if not include_nulls else None),
                "confidence": 0.85 + (i % 10) * 0.01
            }
            
            anomalies.append(anomaly)
        
        return anomalies
    
    @staticmethod
    def get_anomaly_statistics_mock(
        days: int = 7,
        edge_case: str = None
    ) -> Dict[str, Any]:
        """
        Generate mock data for anomaly statistics endpoint.
        
        Args:
            days: Number of days for statistics
            edge_case: Specific edge case ('no_anomalies', 'single_type', 'high_volume')
        """
        base_time = datetime.now(timezone.utc)
        
        if edge_case == 'no_anomalies':
            return {
                "period_days": days,
                "total_anomalies": 0,
                "by_type": {},
                "by_severity": {},
                "timeline": {},
                "top_affected_nodes": [],
                "generated_at": base_time.isoformat()
            }
        
        if edge_case == 'single_type':
            by_type = {"pressure_drop": 10}
            by_severity = {"medium": 10}
        elif edge_case == 'high_volume':
            by_type = {
                "pressure_drop": 500,
                "flow_spike": 450,
                "temperature_anomaly": 300,
                "quality_issue": 200,
                "sensor_failure": 50
            }
            by_severity = {
                "low": 300,
                "medium": 600,
                "high": 400,
                "critical": 200
            }
        else:
            by_type = {
                "pressure_drop": 15,
                "flow_spike": 12,
                "temperature_anomaly": 8,
                "quality_issue": 5
            }
            by_severity = {
                "low": 10,
                "medium": 20,
                "high": 8,
                "critical": 2
            }
        
        # Generate timeline
        timeline = {}
        for day in range(days):
            date = (base_time - timedelta(days=day)).date()
            if edge_case == 'high_volume':
                timeline[date.isoformat()] = 200 + day * 10
            else:
                timeline[date.isoformat()] = 5 + (day % 3)
        
        # Generate top affected nodes
        top_nodes = []
        if edge_case != 'no_anomalies':
            node_count = 10 if edge_case == 'high_volume' else 3
            for i in range(node_count):
                top_nodes.append({
                    "node_id": f"TEST_NODE_{i+1}",
                    "node_name": f"Test Node {i+1}",
                    "anomaly_count": 10 - i if edge_case != 'high_volume' else 100 - i*5,
                    "anomaly_types": ["pressure_drop", "flow_spike"] if i % 2 == 0 else ["temperature_anomaly"]
                })
        
        return {
            "period_days": days,
            "total_anomalies": sum(by_type.values()),
            "by_type": by_type,
            "by_severity": by_severity,
            "timeline": timeline,
            "top_affected_nodes": top_nodes,
            "generated_at": base_time.isoformat()
        }
    
    @staticmethod
    def get_mock_db_connection(
        scenario: str = 'standard'
    ) -> AsyncMock:
        """
        Create a mock database connection for different test scenarios.
        
        Args:
            scenario: Test scenario ('standard', 'no_data', 'error', 'partial')
        """
        mock_conn = AsyncMock()
        
        if scenario == 'error':
            mock_conn.fetchrow.side_effect = Exception("Database connection error")
            mock_conn.fetch.side_effect = Exception("Database connection error")
        elif scenario == 'no_data':
            mock_conn.fetchrow.return_value = None
            mock_conn.fetch.return_value = []
        elif scenario == 'partial':
            # Return partial data (some queries succeed, some return empty)
            mock_conn.fetchrow.side_effect = [
                {'latest_timestamp': datetime.now(timezone.utc)},
                None,  # No consumption data
                {'pressure_anomalies': 1, 'flow_anomalies': 0, 'temp_anomalies': 0}
            ]
            mock_conn.fetch.return_value = []
        else:
            # Standard scenario with full data
            fixtures = ComprehensiveMockFixtures()
            dashboard_data = fixtures.get_dashboard_mock_data()
            
            mock_conn.fetchrow.side_effect = [
                {'latest_timestamp': datetime.now(timezone.utc)},
                {
                    'total_liters': 125000.5,
                    'avg_flow_rate': 45.7,
                    'avg_pressure': 3.5,
                    'active_connections': 42
                },
                {
                    'pressure_anomalies': 1,
                    'flow_anomalies': 1,
                    'temp_anomalies': 1
                }
            ]
            
            # Mock nodes data
            nodes_data = []
            for i in range(5):
                nodes_data.append({
                    'node_id': f'TEST_NODE_{i+1}',
                    'node_name': f'Test Node {i+1}',
                    'node_type': 'distribution' if i % 2 == 0 else 'reservoir',
                    'flow_rate': 10.5 + i * 2.3,
                    'pressure': 3.2 + i * 0.1,
                    'temperature': 18.5 + i * 0.5,
                    'last_reading': datetime.now(timezone.utc),
                    'quality_score': 0.95 - i * 0.02
                })
            
            mock_conn.fetch.return_value = nodes_data
        
        mock_conn.close = AsyncMock()
        return mock_conn