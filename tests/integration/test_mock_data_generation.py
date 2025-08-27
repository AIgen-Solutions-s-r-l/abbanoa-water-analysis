"""
Integration tests for mock data generation system.

Tests the complete mock data generation pipeline including:
- Hourly data generator
- Bulk data generator
- Database connectivity
- Node configuration compatibility
- Scheduling verification
"""

import pytest
import asyncio
import asyncpg
from datetime import datetime, timezone, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.hourly_data_generator import generate_hourly_data, DB_CONFIG


class TestMockDataGeneration:
    """Test suite for mock data generation system."""
    
    @pytest.fixture
    async def db_connection(self):
        """Database connection fixture."""
        conn = await asyncpg.connect(**DB_CONFIG)
        yield conn
        await conn.close()
    
    @pytest.mark.asyncio
    async def test_database_connectivity(self, db_connection):
        """Test database connectivity and basic operations."""
        # Test basic query
        result = await db_connection.fetchval("SELECT COUNT(*) FROM water_infrastructure.nodes WHERE is_active = true")
        assert result > 0, "No active nodes found in database"
        
        # Test node types
        node_types = await db_connection.fetch("""
            SELECT DISTINCT node_type, COUNT(*) as count
            FROM water_infrastructure.nodes
            WHERE is_active = true
            GROUP BY node_type
        """)
        
        expected_types = {'distribution_center', 'interconnection', 'zone_meter'}
        actual_types = {row['node_type'] for row in node_types}
        
        assert actual_types.issubset(expected_types), f"Unexpected node types: {actual_types - expected_types}"
    
    @pytest.mark.asyncio
    async def test_node_configuration_consistency(self, db_connection):
        """Test that node configuration is consistent across the system."""
        # Get nodes from database
        db_nodes = await db_connection.fetch("""
            SELECT node_id, node_name, node_type
            FROM water_infrastructure.nodes
            WHERE is_active = true
            ORDER BY node_name
        """)
        
        # Verify we have the expected number of nodes
        assert len(db_nodes) == 14, f"Expected 14 nodes, found {len(db_nodes)}"
        
        # Verify node naming convention
        for node in db_nodes:
            node_name = node['node_name']
            node_type = node['node_type']
            
            if node_type == 'distribution_center':
                assert node_name.startswith('DIST'), f"Distribution node should start with 'DIST': {node_name}"
            elif node_type == 'interconnection':
                assert node_name.startswith('INTERCON'), f"Interconnection node should start with 'INTERCON': {node_name}"
            elif node_type == 'zone_meter':
                assert node_name.startswith('ZONE'), f"Zone meter should start with 'ZONE': {node_name}"
    
    @pytest.mark.asyncio
    async def test_hourly_data_generation(self, db_connection):
        """Test hourly data generation functionality."""
        # Get initial record count
        initial_count = await db_connection.fetchval("""
            SELECT COUNT(*) 
            FROM water_infrastructure.sensor_readings 
            WHERE timestamp > NOW() - INTERVAL '1 hour'
        """)
        
        # Run hourly data generation
        await generate_hourly_data()
        
        # Get final record count
        final_count = await db_connection.fetchval("""
            SELECT COUNT(*) 
            FROM water_infrastructure.sensor_readings 
            WHERE timestamp > NOW() - INTERVAL '1 hour'
        """)
        
        # Verify data was generated (may be same if data already existed)
        assert final_count >= initial_count, "Data generation should not decrease record count"
        
        # Verify data quality
        recent_data = await db_connection.fetch("""
            SELECT node_id, temperature, flow_rate, pressure, total_flow, is_interpolated
            FROM water_infrastructure.sensor_readings
            WHERE timestamp > NOW() - INTERVAL '1 hour'
            AND is_interpolated = true
            LIMIT 10
        """)
        
        for record in recent_data:
            assert record['temperature'] is not None, "Temperature should not be null"
            assert record['flow_rate'] is not None, "Flow rate should not be null"
            assert record['pressure'] is not None, "Pressure should not be null"
            assert record['total_flow'] is not None, "Total flow should not be null"
            assert record['is_interpolated'] is True, "Synthetic data should be marked as interpolated"
    
    @pytest.mark.asyncio
    async def test_data_continuity(self, db_connection):
        """Test that generated data maintains continuity."""
        # Get latest readings for each node
        latest_readings = await db_connection.fetch("""
            SELECT DISTINCT ON (node_id)
                node_id, temperature, flow_rate, pressure, total_flow, timestamp
            FROM water_infrastructure.sensor_readings
            WHERE is_interpolated = true
            ORDER BY node_id, timestamp DESC
        """)
        
        # Verify all active nodes have recent data
        active_nodes = await db_connection.fetch("""
            SELECT node_id FROM water_infrastructure.nodes WHERE is_active = true
        """)
        
        active_node_ids = {node['node_id'] for node in active_nodes}
        nodes_with_data = {reading['node_id'] for reading in latest_readings}
        
        assert active_node_ids.issubset(nodes_with_data), f"Missing data for nodes: {active_node_ids - nodes_with_data}"
        
        # Verify data is recent (within last 2 hours)
        two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)
        for reading in latest_readings:
            assert reading['timestamp'] > two_hours_ago, f"Data too old for node {reading['node_id']}"
    
    @pytest.mark.asyncio
    async def test_scheduling_verification(self, db_connection):
        """Test that scheduling system is working correctly."""
        # Check if systemd timer is active
        import subprocess
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'abbanoa-hourly-data.timer'],
                capture_output=True,
                text=True
            )
            assert result.stdout.strip() == 'active', f"Timer not active: {result.stdout}"
        except FileNotFoundError:
            pytest.skip("systemctl not available (not running on systemd system)")
        
        # Check recent execution logs
        try:
            result = subprocess.run([
                'journalctl', '-u', 'abbanoa-hourly-data.service',
                '--since', '1 hour ago',
                '--no-pager'
            ], capture_output=True, text=True)
            
            assert 'Successfully inserted' in result.stdout, "No successful execution found in recent logs"
        except FileNotFoundError:
            pytest.skip("journalctl not available")
    
    @pytest.mark.asyncio
    async def test_data_patterns(self, db_connection):
        """Test that generated data follows realistic patterns."""
        # Get hourly data for the last 24 hours
        hourly_data = await db_connection.fetch("""
            SELECT 
                EXTRACT(HOUR FROM timestamp) as hour,
                AVG(temperature) as avg_temp,
                AVG(flow_rate) as avg_flow,
                AVG(pressure) as avg_pressure
            FROM water_infrastructure.sensor_readings
            WHERE timestamp > NOW() - INTERVAL '24 hours'
            AND is_interpolated = true
            GROUP BY EXTRACT(HOUR FROM timestamp)
            ORDER BY hour
        """)
        
        # Verify we have data for multiple hours
        assert len(hourly_data) > 0, "No hourly data found"
        
        # Verify temperature is within realistic range (10-30°C)
        for record in hourly_data:
            assert 10 <= record['avg_temp'] <= 30, f"Temperature out of range: {record['avg_temp']}"
            assert record['avg_flow'] > 0, f"Flow rate should be positive: {record['avg_flow']}"
            assert 1 <= record['avg_pressure'] <= 10, f"Pressure out of range: {record['avg_pressure']}"
    
    @pytest.mark.asyncio
    async def test_api_integration(self, db_connection):
        """Test that the dashboard API works with generated data."""
        # Simulate dashboard API query
        dashboard_data = await db_connection.fetch("""
            SELECT DISTINCT ON (n.node_id)
                n.node_id,
                n.node_name,
                n.node_type,
                COALESCE(sr.flow_rate, 0.0) as flow_rate,
                COALESCE(sr.pressure, 0.0) as pressure,
                COALESCE(sr.quality_score, 0.95) as quality_score
            FROM water_infrastructure.nodes n
            LEFT JOIN water_infrastructure.sensor_readings sr 
                ON sr.node_id = n.node_id
                AND sr.timestamp > NOW() - INTERVAL '24 hours'
            WHERE n.is_active = true
            ORDER BY n.node_id, sr.timestamp DESC NULLS LAST
        """)
        
        # Verify API returns data for all active nodes
        assert len(dashboard_data) == 14, f"Expected 14 nodes, got {len(dashboard_data)}"
        
        # Verify data quality
        for record in dashboard_data:
            assert record['node_id'] is not None, "Node ID should not be null"
            assert record['node_name'] is not None, "Node name should not be null"
            assert record['node_type'] is not None, "Node type should not be null"
            assert record['quality_score'] >= 0.9, f"Quality score too low: {record['quality_score']}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
