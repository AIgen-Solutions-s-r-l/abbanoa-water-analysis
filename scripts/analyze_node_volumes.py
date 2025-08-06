#!/usr/bin/env python3
"""
Analyze node water volumes to identify tanks and create renaming recommendations.

This script:
1. Queries the database for node volume data
2. Analyzes volumes to identify tanks (high volume nodes)
3. Generates renaming recommendations based on volume patterns
"""

import asyncio
import asyncpg
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5434,
    'database': 'abbanoa_processing',
    'user': 'abbanoa_user',
    'password': 'abbanoa_secure_pass'
}

async def get_node_volume_data(days_back: int = 30) -> pd.DataFrame:
    """Get volume data for all nodes from the database."""
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        print(f"📊 Analyzing volume data from {start_time} to {end_time}")
        
        # Query for aggregated volume data by node
        query = """
            SELECT 
                n.node_id,
                n.node_name,
                n.node_type,
                COUNT(sr.timestamp) as reading_count,
                AVG(sr.total_flow) as avg_volume,
                MAX(sr.total_flow) as max_volume,
                MIN(sr.total_flow) as min_volume,
                STDDEV(sr.total_flow) as volume_stddev,
                MAX(sr.total_flow) - MIN(sr.total_flow) as volume_range
            FROM water_infrastructure.nodes n
            LEFT JOIN water_infrastructure.sensor_readings sr 
                ON n.node_id = sr.node_id
                AND sr.timestamp >= $1
                AND sr.timestamp <= $2
            WHERE n.is_active = true
            GROUP BY n.node_id, n.node_name, n.node_type
            ORDER BY avg_volume DESC NULLS LAST
        """
        
        rows = await conn.fetch(query, start_time, end_time)
        
        # Convert to DataFrame
        df = pd.DataFrame([dict(row) for row in rows])
        
        # Also get hourly volume changes to identify consumption patterns
        hourly_query = """
            SELECT 
                node_id,
                DATE_TRUNC('hour', timestamp) as hour,
                MAX(total_flow) - MIN(total_flow) as hourly_consumption
            FROM water_infrastructure.sensor_readings
            WHERE timestamp >= $1 AND timestamp <= $2
                AND total_flow IS NOT NULL
            GROUP BY node_id, hour
        """
        
        hourly_rows = await conn.fetch(hourly_query, start_time, end_time)
        hourly_df = pd.DataFrame([dict(row) for row in hourly_rows])
        
        if not hourly_df.empty:
            # Calculate average hourly consumption by node
            hourly_avg = hourly_df.groupby('node_id')['hourly_consumption'].agg(['mean', 'std']).reset_index()
            hourly_avg.columns = ['node_id', 'avg_hourly_consumption', 'std_hourly_consumption']
            
            # Merge with main dataframe
            df = df.merge(hourly_avg, on='node_id', how='left')
        
        return df
        
    finally:
        await conn.close()

def analyze_volumes(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Analyze volumes to categorize nodes."""
    
    # Remove nodes with no volume data
    df_with_data = df[df['avg_volume'].notna()].copy()
    
    if df_with_data.empty:
        print("⚠️  No volume data found!")
        return {}
    
    print(f"\n📈 Volume Statistics:")
    print(f"  - Nodes with data: {len(df_with_data)}")
    print(f"  - Volume range: {df_with_data['avg_volume'].min():.2f} - {df_with_data['avg_volume'].max():.2f} m³")
    
    # Calculate volume percentiles
    volume_percentiles = df_with_data['avg_volume'].quantile([0.25, 0.5, 0.75, 0.90, 0.95])
    
    print(f"\n📊 Volume Percentiles:")
    for p, v in volume_percentiles.items():
        print(f"  - {int(p*100)}th percentile: {v:.2f} m³")
    
    # Categorize nodes based on volume patterns
    categories = {
        'tanks': [],
        'distribution_nodes': [],
        'monitoring_points': [],
        'unknown': []
    }
    
    # Identify tanks: nodes with very high volumes (top 10% or specific threshold)
    tank_threshold = max(volume_percentiles[0.90], 100000)  # At least 100,000 m³
    
    for _, row in df_with_data.iterrows():
        node_id = row['node_id']
        avg_volume = row['avg_volume']
        
        # Tank identification criteria:
        # 1. Very high average volume
        # 2. Low hourly consumption relative to total volume (storage behavior)
        is_tank = False
        
        if avg_volume >= tank_threshold:
            # Check consumption pattern
            if pd.notna(row.get('avg_hourly_consumption')):
                consumption_ratio = row['avg_hourly_consumption'] / avg_volume
                # Tanks have low consumption relative to their volume
                if consumption_ratio < 0.01:  # Less than 1% per hour
                    is_tank = True
            else:
                # If no consumption data, use volume alone
                is_tank = True
        
        if is_tank:
            categories['tanks'].append(node_id)
        elif avg_volume >= volume_percentiles[0.5]:
            categories['distribution_nodes'].append(node_id)
        elif row['reading_count'] > 0:
            categories['monitoring_points'].append(node_id)
        else:
            categories['unknown'].append(node_id)
    
    # Print categorization results
    print(f"\n🏷️  Node Categorization:")
    for category, nodes in categories.items():
        print(f"  - {category}: {len(nodes)} nodes")
        if nodes and category == 'tanks':
            for node in nodes:
                node_data = df_with_data[df_with_data['node_id'] == node].iloc[0]
                print(f"    • {node}: {node_data['avg_volume']:.2f} m³ (current: {node_data['node_name']})")
    
    return categories, df_with_data

def generate_renaming_map(categories: Dict[str, List[str]], df: pd.DataFrame) -> Dict[str, str]:
    """Generate node renaming recommendations."""
    
    renaming_map = {}
    
    # Rename tanks
    tank_nodes = categories.get('tanks', [])
    for i, node_id in enumerate(sorted(tank_nodes)):
        node_data = df[df['node_id'] == node_id].iloc[0]
        # Use TANK01, TANK02, etc. for tanks
        new_name = f"TANK{i+1:02d}"
        renaming_map[node_id] = {
            'new_name': new_name,
            'old_name': node_data['node_name'],
            'avg_volume': float(node_data['avg_volume']),
            'category': 'tank'
        }
    
    # Rename distribution nodes
    dist_nodes = categories.get('distribution_nodes', [])
    for i, node_id in enumerate(sorted(dist_nodes)):
        node_data = df[df['node_id'] == node_id].iloc[0]
        # Use NODE01, NODE02, etc. for distribution nodes
        new_name = f"NODE{i+1:02d}"
        renaming_map[node_id] = {
            'new_name': new_name,
            'old_name': node_data['node_name'],
            'avg_volume': float(node_data['avg_volume']),
            'category': 'distribution'
        }
    
    # Rename monitoring points
    monitor_nodes = categories.get('monitoring_points', [])
    for i, node_id in enumerate(sorted(monitor_nodes)):
        node_data = df[df['node_id'] == node_id].iloc[0]
        # Use MONITOR01, MONITOR02, etc. for monitoring points
        new_name = f"MONITOR{i+1:02d}"
        renaming_map[node_id] = {
            'new_name': new_name,
            'old_name': node_data['node_name'],
            'avg_volume': float(node_data['avg_volume']) if pd.notna(node_data['avg_volume']) else 0,
            'category': 'monitoring'
        }
    
    return renaming_map

async def main():
    """Main analysis function."""
    print("🔍 Node Volume Analysis and Renaming Tool")
    print("=" * 50)
    
    # Get volume data
    df = await get_node_volume_data(days_back=30)
    
    if df.empty:
        print("❌ No node data found in database!")
        return
    
    # Analyze volumes
    categories, df_with_data = analyze_volumes(df)
    
    # Generate renaming recommendations
    renaming_map = generate_renaming_map(categories, df_with_data)
    
    # Save recommendations to file
    output_file = 'node_renaming_recommendations.json'
    with open(output_file, 'w') as f:
        json.dump(renaming_map, f, indent=2)
    
    print(f"\n💾 Renaming recommendations saved to: {output_file}")
    
    # Print summary
    print("\n📋 Renaming Summary:")
    for node_id, info in sorted(renaming_map.items(), key=lambda x: x[1]['new_name']):
        print(f"  {info['old_name']:30} → {info['new_name']:12} (Volume: {info['avg_volume']:,.0f} m³)")
    
    print("\n✅ Analysis complete!")
    print(f"   Found {len([v for v in renaming_map.values() if v['category'] == 'tank'])} tanks")
    print(f"   Found {len([v for v in renaming_map.values() if v['category'] == 'distribution'])} distribution nodes")
    print(f"   Found {len([v for v in renaming_map.values() if v['category'] == 'monitoring'])} monitoring points")

if __name__ == "__main__":
    asyncio.run(main())
