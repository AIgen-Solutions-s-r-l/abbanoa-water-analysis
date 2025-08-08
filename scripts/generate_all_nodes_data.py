#!/usr/bin/env python3
"""
Generate synthetic data for ALL nodes in the system, including those without historical patterns.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import asyncio
import asyncpg

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5434,
    'database': 'abbanoa_processing',
    'user': 'abbanoa_user',
    'password': 'abbanoa_secure_pass'
}

# Default patterns for nodes without historical data
DEFAULT_PATTERNS = {
    'interconnection': {
        'flow_rate': {
            'mean': 45.0,
            'std': 8.0,
            'min': 20.0,
            'max': 80.0,
            'hourly_variation': {
                '0': 30, '1': 28, '2': 27, '3': 26, '4': 28, '5': 32,
                '6': 40, '7': 55, '8': 65, '9': 60, '10': 58, '11': 56,
                '12': 54, '13': 52, '14': 50, '15': 48, '16': 50, '17': 55,
                '18': 60, '19': 58, '20': 52, '21': 45, '22': 38, '23': 33
            }
        },
        'pressure': {
            'mean': 3.5,
            'std': 0.3,
            'min': 2.5,
            'max': 4.5
        },
        'temperature': {
            'mean': 15.0,
            'std': 2.0,
            'min': 10.0,
            'max': 22.0
        }
    },
    'zone_meter': {
        'flow_rate': {
            'mean': 25.0,
            'std': 5.0,
            'min': 10.0,
            'max': 50.0,
            'hourly_variation': {
                '0': 15, '1': 12, '2': 10, '3': 10, '4': 12, '5': 18,
                '6': 25, '7': 35, '8': 40, '9': 38, '10': 36, '11': 34,
                '12': 32, '13': 30, '14': 28, '15': 27, '16': 30, '17': 35,
                '18': 38, '19': 35, '20': 30, '21': 25, '22': 20, '23': 17
            }
        },
        'pressure': {
            'mean': 2.8,
            'std': 0.2,
            'min': 2.0,
            'max': 3.5
        },
        'temperature': {
            'mean': 16.0,
            'std': 1.5,
            'min': 12.0,
            'max': 20.0
        },
        'total_flow': {
            'daily_consumption': 2000,  # m³/day
            'start_value': 100000
        }
    }
}

async def get_all_nodes(conn):
    """Get all active nodes from the database."""
    rows = await conn.fetch("""
        SELECT node_id, node_name, node_type
        FROM water_infrastructure.nodes
        WHERE is_active = true
        ORDER BY node_type, node_name
    """)
    return [dict(row) for row in rows]

async def check_existing_data(conn, node_id, start_date, end_date):
    """Check if node already has complete data for the date range."""
    # Expected records: 48 per day (30-minute intervals)
    expected_days = (end_date.date() - start_date.date()).days + 1
    expected_records = expected_days * 48
    
    count = await conn.fetchval("""
        SELECT COUNT(*)
        FROM water_infrastructure.sensor_readings
        WHERE node_id = $1
        AND timestamp >= $2
        AND timestamp <= $3
    """, node_id, start_date, end_date)
    
    # Consider data complete if we have at least 90% of expected records
    return count >= (expected_records * 0.9)

def generate_synthetic_data_for_node(node, start_date, end_date, existing_patterns=None):
    """Generate synthetic data for a specific node."""
    
    print(f"  🔮 Generating data for {node['node_name']} ({node['node_type']})")
    
    # Create timestamp range (30-minute intervals)
    timestamps = pd.date_range(
        start=start_date,
        end=end_date,
        freq='30min'
    )
    
    df = pd.DataFrame({'timestamp': timestamps})
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6])
    df['day_index'] = (df['timestamp'] - df['timestamp'].min()).dt.days
    
    # Determine patterns to use
    if node['node_id'] in ['CENTRO_EST', 'CENTRO_NORD', 'CENTRO_OVEST', 'CENTRO_SUD']:
        # These nodes have historical patterns from the CSV analysis
        return None  # Skip - already handled
    
    # Use default patterns based on node type
    if node['node_type'] in DEFAULT_PATTERNS:
        patterns = DEFAULT_PATTERNS[node['node_type']]
    else:
        # Generic pattern for unknown types
        patterns = DEFAULT_PATTERNS['interconnection']
    
    # Generate flow rate
    if 'flow_rate' in patterns:
        flow_pattern = patterns['flow_rate']
        hourly_values = df['hour'].apply(
            lambda h: flow_pattern['hourly_variation'].get(str(h), flow_pattern['mean'])
        )
        
        # Add weekend variation (lower on weekends)
        weekend_factor = df['is_weekend'].apply(lambda x: 0.7 if x else 1.0)
        hourly_values *= weekend_factor
        
        # Add noise
        noise = np.random.normal(0, flow_pattern['std'], len(df))
        flow_rate = hourly_values + noise
        flow_rate = np.clip(flow_rate, flow_pattern['min'], flow_pattern['max'])
        df['flow_rate'] = flow_rate
    else:
        df['flow_rate'] = 0
    
    # Generate pressure
    if 'pressure' in patterns:
        press_pattern = patterns['pressure']
        # Pressure correlates with flow rate
        base_pressure = press_pattern['mean']
        if 'flow_rate' in df:
            # Higher flow = slightly lower pressure
            pressure_adj = (df['flow_rate'] - df['flow_rate'].mean()) * -0.01
        else:
            pressure_adj = 0
        
        pressure = base_pressure + pressure_adj + np.random.normal(0, press_pattern['std'], len(df))
        pressure = np.clip(pressure, press_pattern['min'], press_pattern['max'])
        df['pressure'] = pressure
    else:
        df['pressure'] = None
    
    # Generate temperature
    if 'temperature' in patterns:
        temp_pattern = patterns['temperature']
        # Temperature has daily and seasonal variation
        daily_temp = np.sin((df['hour'] - 6) * np.pi / 12) * 2  # Peak at noon
        seasonal_temp = np.sin((df['month'] - 1) * np.pi / 6) * 3  # Peak in summer
        
        temperature = temp_pattern['mean'] + daily_temp + seasonal_temp
        temperature += np.random.normal(0, temp_pattern['std'], len(df))
        temperature = np.clip(temperature, temp_pattern['min'], temp_pattern['max'])
        df['temperature'] = temperature
    else:
        df['temperature'] = None
    
    # Generate total flow (cumulative) for zone meters
    if 'total_flow' in patterns and node['node_type'] == 'zone_meter':
        flow_pattern = patterns['total_flow']
        # Calculate hourly consumption based on flow rate
        if 'flow_rate' in df:
            hourly_consumption = df['flow_rate'] * 1.8  # L/s to m³/30min
        else:
            hourly_consumption = flow_pattern['daily_consumption'] / 48  # Default daily consumption
        
        # Add some variation
        hourly_consumption *= np.random.uniform(0.9, 1.1, len(df))
        
        # Calculate cumulative
        start_value = flow_pattern['start_value']
        df['total_flow'] = start_value + hourly_consumption.cumsum()
    else:
        # For interconnection points, total flow is not cumulative
        if 'flow_rate' in df:
            # Just use a scaled version of flow rate
            df['total_flow'] = df['flow_rate'] * 100
        else:
            df['total_flow'] = 0
    
    return df

async def insert_node_data(conn, node, df):
    """Insert synthetic data for a node."""
    
    records = []
    for _, row in df.iterrows():
        timestamp = row['timestamp']
        if timestamp.tz is None:
            timestamp = timestamp.tz_localize('UTC')
        
        records.append((
            timestamp,
            node['node_id'],
            float(row['temperature']) if pd.notna(row.get('temperature')) else None,
            float(row['flow_rate']) if pd.notna(row.get('flow_rate')) else None,
            float(row['pressure']) if pd.notna(row.get('pressure')) else None,
            float(row['total_flow']) if pd.notna(row.get('total_flow')) else 0,
            0.85,  # quality_score
            True,  # is_interpolated
            json.dumps({
                'source': 'synthetic_all_nodes',
                'node_type': node['node_type'],
                'generation_date': datetime.now().isoformat()
            })
        ))
    
    # Insert in batches
    batch_size = 1000
    total_inserted = 0
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        try:
            await conn.executemany("""
                INSERT INTO water_infrastructure.sensor_readings 
                    (timestamp, node_id, temperature, flow_rate, pressure, 
                     total_flow, quality_score, is_interpolated, raw_data)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, batch)
            total_inserted += len(batch)
        except Exception as e:
            print(f"    ❌ Error inserting batch: {e}")
    
    return total_inserted

async def main():
    """Main execution function."""
    
    print("🌟 Synthetic Data Generation for ALL Nodes")
    print("=" * 60)
    
    # Define date range
    start_date = datetime(2024, 11, 13, 0, 0, 0)
    end_date = datetime(2025, 8, 6, 23, 30, 0)
    
    print(f"\n📅 Date range: {start_date} to {end_date}")
    print(f"   Duration: {(end_date - start_date).days} days")
    
    # Connect to database
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # Get all nodes
        nodes = await get_all_nodes(conn)
        print(f"\n📊 Found {len(nodes)} active nodes")
        
        # Group by type
        nodes_by_type = {}
        for node in nodes:
            node_type = node['node_type']
            if node_type not in nodes_by_type:
                nodes_by_type[node_type] = []
            nodes_by_type[node_type].append(node)
        
        print("\nNodes by type:")
        for node_type, type_nodes in sorted(nodes_by_type.items()):
            print(f"  - {node_type}: {len(type_nodes)} nodes")
        
        # Check which nodes need data
        nodes_needing_data = []
        print("\n🔍 Checking existing data...")
        
        expected_days = (end_date.date() - start_date.date()).days + 1
        expected_records = expected_days * 48
        print(f"   Expected records per node: {expected_records:,} ({expected_days} days × 48 records/day)")
        
        for node in nodes:
            count = await conn.fetchval("""
                SELECT COUNT(*)
                FROM water_infrastructure.sensor_readings
                WHERE node_id = $1
                AND timestamp >= $2
                AND timestamp <= $3
            """, node['node_id'], start_date, end_date)
            
            coverage = (count / expected_records * 100) if expected_records > 0 else 0
            
            if coverage >= 90:
                print(f"  ✓ {node['node_name']:12} - {count:6,} records ({coverage:5.1f}% coverage)")
            else:
                print(f"  ✗ {node['node_name']:12} - {count:6,} records ({coverage:5.1f}% coverage) - Needs data")
                nodes_needing_data.append(node)
        
        if not nodes_needing_data:
            print("\n✅ All nodes already have data!")
            return
        
        print(f"\n📊 {len(nodes_needing_data)} nodes need synthetic data")
        
        # Confirm before proceeding
        response = input("\nProceed with synthetic data generation? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Generation cancelled")
            return
        
        # Generate and insert data for each node
        total_inserted = 0
        print("\n🔄 Generating synthetic data...")
        
        for node in nodes_needing_data:
            # Generate data
            df = generate_synthetic_data_for_node(node, start_date, end_date)
            
            if df is not None:
                print(f"\n  💾 Inserting data for {node['node_name']}...")
                inserted = await insert_node_data(conn, node, df)
                print(f"    ✅ Inserted {inserted} records")
                total_inserted += inserted
        
        print(f"\n✅ Total records inserted: {total_inserted}")
        
        # Verify final state
        print("\n📊 Final node data coverage:")
        
        for node in nodes:
            count = await conn.fetchval("""
                SELECT COUNT(*)
                FROM water_infrastructure.sensor_readings
                WHERE node_id = $1
                AND timestamp >= $2
            """, node['node_id'], start_date)
            
            print(f"  {node['node_name']:12} - {count:,} records")
        
    finally:
        await conn.close()
    
    print("\n✨ Synthetic data generation complete for ALL nodes!")

if __name__ == "__main__":
    asyncio.run(main())
