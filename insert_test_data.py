#!/usr/bin/env python3
"""
Simple script to insert test data into the database for Consumption Analytics
"""

import psycopg2
from datetime import datetime, timedelta
import random

# Database configuration
DB_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'database': 'abbanoa_processing',
    'user': 'abbanoa_user',
    'password': 'abbanoa_secure_pass'
}

def create_tables():
    """Create the necessary tables if they don't exist."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Create nodes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            node_id VARCHAR(50) PRIMARY KEY,
            node_name VARCHAR(100) NOT NULL,
            node_type VARCHAR(50) NOT NULL,
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create sensor_readings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id SERIAL PRIMARY KEY,
            node_id VARCHAR(50) REFERENCES nodes(node_id),
            timestamp TIMESTAMP NOT NULL,
            flow_rate_liters_per_second DECIMAL(10, 2),
            pressure_bar DECIMAL(5, 2),
            temperature_celsius DECIMAL(5, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Tables created successfully")

def insert_test_nodes():
    """Insert test nodes."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    nodes = [
        ('VIA_DANTE_1', 'Via Dante Principale', 'main'),
        ('VIA_ROMA_2', 'Via Roma Secondario', 'secondary'),
        ('ZONA_INDUSTRIALE_1', 'Zona Industriale Nord', 'industrial'),
        ('RESIDENZIALE_1', 'Zona Residenziale Centro', 'residential'),
        ('COMMERCIALE_1', 'Zona Commerciale Sud', 'commercial'),
        ('VIA_GARIBALDI_3', 'Via Garibaldi Terziario', 'secondary'),
        ('ZONA_OSPEDALE_1', 'Ospedale Civico', 'main')
    ]
    
    for node_id, node_name, node_type in nodes:
        cursor.execute("""
            INSERT INTO nodes (node_id, node_name, node_type)
            VALUES (%s, %s, %s)
            ON CONFLICT (node_id) DO NOTHING
        """, (node_id, node_name, node_type))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Inserted {len(nodes)} test nodes")

def insert_test_readings():
    """Insert test sensor readings."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Get all node IDs
    cursor.execute("SELECT node_id FROM nodes")
    node_ids = [row[0] for row in cursor.fetchall()]
    
    if not node_ids:
        print("❌ No nodes found. Please insert nodes first.")
        return
    
    # Generate readings for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    current_date = start_date
    
    readings_count = 0
    
    while current_date <= end_date:
        for node_id in node_ids:
            # Generate 24 hourly readings per day
            for hour in range(24):
                timestamp = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                
                # Base values based on node type
                if 'main' in node_id:
                    base_flow = 4.5
                    base_pressure = 3.2
                elif 'secondary' in node_id:
                    base_flow = 2.8
                    base_pressure = 2.5
                elif 'industrial' in node_id:
                    base_flow = 8.7
                    base_pressure = 4.5
                else:
                    base_flow = 1.8
                    base_pressure = 2.0
                
                # Add some variation
                flow_rate = base_flow + random.uniform(-0.5, 0.5)
                pressure = base_pressure + random.uniform(-0.3, 0.3)
                temperature = 15 + random.uniform(-5, 10)
                
                cursor.execute("""
                    INSERT INTO sensor_readings 
                    (node_id, timestamp, flow_rate_liters_per_second, pressure_bar, temperature_celsius)
                    VALUES (%s, %s, %s, %s, %s)
                """, (node_id, timestamp, flow_rate, pressure, temperature))
                
                readings_count += 1
        
        current_date += timedelta(days=1)
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Inserted {readings_count} test readings")

def verify_data():
    """Verify that data was inserted correctly."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Count nodes
    cursor.execute("SELECT COUNT(*) FROM nodes")
    node_count = cursor.fetchone()[0]
    
    # Count readings
    cursor.execute("SELECT COUNT(*) FROM sensor_readings")
    reading_count = cursor.fetchone()[0]
    
    # Get date range
    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM sensor_readings")
    date_range = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    print(f"📊 Data Summary:")
    print(f"   Nodes: {node_count}")
    print(f"   Readings: {reading_count}")
    if date_range[0] and date_range[1]:
        print(f"   Date Range: {date_range[0]} to {date_range[1]}")

def main():
    """Main function to insert test data."""
    print("🚀 Starting test data insertion...")
    
    try:
        create_tables()
        insert_test_nodes()
        insert_test_readings()
        verify_data()
        print("✅ Test data insertion completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
