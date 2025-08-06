#!/usr/bin/env python3
"""
Analyze node water volumes from CSV data to identify tanks and create renaming recommendations.

This script analyzes the cleaned_data.csv file to identify which columns represent tanks
based on their volume patterns.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

def analyze_csv_data(csv_file: str = 'cleaned_data.csv'):
    """Analyze the CSV data to understand column structure and volumes."""
    
    print(f"📂 Reading CSV file: {csv_file}")
    
    # Read CSV with semicolon separator
    df = pd.read_csv(csv_file, sep=';')
    
    print(f"\n📊 Data shape: {df.shape}")
    print(f"\n📋 Columns found:")
    for i, col in enumerate(df.columns):
        print(f"  {i}: {col}")
    
    # Identify volume columns (M3 columns)
    volume_columns = [col for col in df.columns if 'M3' in col and not col.startswith('Unnamed')]
    
    print(f"\n💧 Volume columns identified: {len(volume_columns)}")
    
    # Analyze each volume column
    volume_stats = {}
    
    for col in volume_columns:
        try:
            # Convert to numeric, handling European decimal format
            values = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
            
            if values.notna().sum() > 0:
                stats = {
                    'column': col,
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'mean': float(values.mean()),
                    'std': float(values.std()),
                    'range': float(values.max() - values.min()),
                    'non_null_count': int(values.notna().sum()),
                    'total_consumption': float(values.max() - values.min()) if values.min() > 0 else 0
                }
                volume_stats[col] = stats
                
                print(f"\n  📈 {col}:")
                print(f"    - Range: {stats['min']:.0f} - {stats['max']:.0f} m³")
                print(f"    - Mean: {stats['mean']:.0f} m³")
                print(f"    - Total consumption: {stats['total_consumption']:.0f} m³")
        except Exception as e:
            print(f"  ⚠️  Error processing {col}: {e}")
    
    return volume_stats, df

def categorize_nodes(volume_stats: dict):
    """Categorize nodes based on volume patterns."""
    
    if not volume_stats:
        print("\n❌ No volume data to analyze!")
        return {}
    
    # Sort by maximum volume
    sorted_nodes = sorted(volume_stats.items(), key=lambda x: x[1]['max'], reverse=True)
    
    print("\n🏷️  Node Categorization based on volume:")
    
    categories = {
        'tanks': [],
        'distribution_nodes': [],
        'monitoring_points': []
    }
    
    # Calculate thresholds
    all_max_volumes = [stats['max'] for _, stats in sorted_nodes]
    if len(all_max_volumes) >= 3:
        tank_threshold = np.percentile(all_max_volumes, 80)  # Top 20% are likely tanks
    else:
        tank_threshold = max(all_max_volumes) * 0.8
    
    print(f"\n📏 Tank threshold (80th percentile): {tank_threshold:.0f} m³")
    
    # Categorize each node
    for col, stats in sorted_nodes:
        if stats['max'] >= tank_threshold and stats['max'] > 100000:  # At least 100,000 m³
            categories['tanks'].append((col, stats))
            print(f"  🏭 TANK: {col} (Max: {stats['max']:.0f} m³)")
        elif stats['total_consumption'] > 0:
            categories['distribution_nodes'].append((col, stats))
            print(f"  🔄 DISTRIBUTION: {col} (Max: {stats['max']:.0f} m³)")
        else:
            categories['monitoring_points'].append((col, stats))
            print(f"  📊 MONITORING: {col} (Max: {stats['max']:.0f} m³)")
    
    return categories

def generate_renaming_recommendations(categories: dict):
    """Generate renaming recommendations for the columns."""
    
    recommendations = {}
    
    # Map M3 columns to node names
    column_to_node_map = {
        'M3': 'NODE01',      # First M3 column
        'M3.1': 'NODE02',    # Second M3 column
        'M3.2': 'NODE03',    # Third M3 column
        'M3.3': 'NODE04'     # Fourth M3 column
    }
    
    # Override with tank names for identified tanks
    tank_num = 1
    for col, stats in categories.get('tanks', []):
        new_name = f'TANK{tank_num:02d}'
        recommendations[col] = {
            'current_column': col,
            'new_node_name': new_name,
            'category': 'tank',
            'max_volume': stats['max'],
            'total_consumption': stats['total_consumption']
        }
        tank_num += 1
    
    # Name remaining nodes
    node_num = 1
    for col, stats in categories.get('distribution_nodes', []):
        if col not in recommendations:
            new_name = f'NODE{node_num:02d}'
            recommendations[col] = {
                'current_column': col,
                'new_node_name': new_name,
                'category': 'distribution',
                'max_volume': stats['max'],
                'total_consumption': stats['total_consumption']
            }
            node_num += 1
    
    # Monitoring points
    monitor_num = 1
    for col, stats in categories.get('monitoring_points', []):
        if col not in recommendations:
            new_name = f'MONITOR{monitor_num:02d}'
            recommendations[col] = {
                'current_column': col,
                'new_node_name': new_name,
                'category': 'monitoring',
                'max_volume': stats['max'],
                'total_consumption': stats['total_consumption']
            }
            monitor_num += 1
    
    return recommendations

def main():
    """Main analysis function."""
    print("🔍 CSV Volume Analysis and Node Identification")
    print("=" * 50)
    
    # Analyze CSV data
    volume_stats, df = analyze_csv_data()
    
    if not volume_stats:
        print("\n❌ No volume data found in CSV!")
        return
    
    # Categorize nodes
    categories = categorize_nodes(volume_stats)
    
    # Generate renaming recommendations
    recommendations = generate_renaming_recommendations(categories)
    
    # Save recommendations
    output_file = 'csv_node_renaming_recommendations.json'
    with open(output_file, 'w') as f:
        json.dump(recommendations, f, indent=2)
    
    print(f"\n💾 Recommendations saved to: {output_file}")
    
    # Print summary
    print("\n📋 Renaming Summary:")
    print("-" * 50)
    for col, rec in sorted(recommendations.items()):
        print(f"  {col:8} → {rec['new_node_name']:12} ({rec['category']:12}) Max: {rec['max_volume']:,.0f} m³")
    
    # Create SQL script for database updates
    sql_file = 'rename_nodes.sql'
    with open(sql_file, 'w') as f:
        f.write("-- SQL script to rename nodes in the database\n")
        f.write("-- Generated from CSV volume analysis\n\n")
        
        for col, rec in recommendations.items():
            # Map column to potential node IDs (this is approximate and may need adjustment)
            # You'll need to verify the actual node_id mappings
            f.write(f"-- Rename {col} to {rec['new_node_name']} (Category: {rec['category']})\n")
            f.write(f"-- Max Volume: {rec['max_volume']:,.0f} m³\n")
            
            # Example SQL (adjust based on actual node_id mapping)
            if col == 'M3':
                node_id = '001'  # Adjust based on actual mapping
            elif col == 'M3.1':
                node_id = '002'
            elif col == 'M3.2':
                node_id = '003'
            elif col == 'M3.3':
                node_id = '004'
            else:
                node_id = 'XXX'  # Unknown mapping
            
            f.write(f"UPDATE water_infrastructure.nodes\n")
            f.write(f"SET node_name = '{rec['new_node_name']}',\n")
            f.write(f"    node_type = '{rec['category']}',\n")
            f.write(f"    updated_at = CURRENT_TIMESTAMP\n")
            f.write(f"WHERE node_id = '{node_id}';  -- TODO: Verify actual node_id\n\n")
    
    print(f"\n📄 SQL script generated: {sql_file}")
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()

