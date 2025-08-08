#!/usr/bin/env python3
"""
Analyze existing data patterns to create synthetic data from April to August 2025.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
try:
    import matplotlib.pyplot as plt
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("⚠️  Matplotlib not available, skipping plots")

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("⚠️  Scipy not available, using simple trend calculation")

def analyze_data_patterns():
    """Analyze the cleaned_data.csv to understand patterns."""
    
    print("📊 Analyzing existing data patterns...")
    
    # Read the data
    df = pd.read_csv('cleaned_data.csv', sep=';')
    
    # Convert date column
    df['timestamp'] = pd.to_datetime(df['DATA_RIFERIMENTO'])
    
    # Convert numeric columns (handling European decimal format)
    numeric_cols = ['GRD. C', 'L/S', 'M3', 'BAR', 'GRD. C.1', 'L/S.1', 
                    'M3.1', 'BAR.1', 'L/S.2', 'M3.2', 'L/S.3', 'M3.3']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
    
    # Extract time features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['day_of_month'] = df['timestamp'].dt.day
    df['month'] = df['timestamp'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6])
    
    print(f"\n📅 Data range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"📊 Total records: {len(df)}")
    
    # Analyze patterns for each metric
    patterns = {}
    
    # Map columns to nodes based on our renaming
    node_mapping = {
        'M3': 'NODE01',      # Distribution node
        'M3.1': 'MONITOR02', # Monitoring point
        'M3.2': 'MONITOR01', # Monitoring point  
        'M3.3': 'TANK01',    # Storage tank
        'L/S': 'NODE01_flow',
        'L/S.1': 'MONITOR02_flow',
        'L/S.2': 'MONITOR01_flow',
        'L/S.3': 'TANK01_flow',
        'BAR': 'NODE01_pressure',
        'BAR.1': 'MONITOR02_pressure',
        'GRD. C': 'NODE01_temp',
        'GRD. C.1': 'MONITOR02_temp'
    }
    
    for col, node_name in node_mapping.items():
        if col in df.columns and df[col].notna().sum() > 0:
            print(f"\n🔍 Analyzing {node_name} ({col})...")
            
            # Calculate daily patterns
            hourly_avg = df.groupby('hour')[col].mean()
            weekday_avg = df[~df['is_weekend']].groupby('hour')[col].mean()
            weekend_avg = df[df['is_weekend']].groupby('hour')[col].mean()
            
            # Calculate statistics
            patterns[node_name] = {
                'column': col,
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'hourly_pattern': hourly_avg.to_dict(),
                'weekday_pattern': weekday_avg.to_dict(),
                'weekend_pattern': weekend_avg.to_dict(),
                'daily_variation': float(hourly_avg.std()),
                'trend': calculate_trend(df, col),
                'seasonality': calculate_seasonality(df, col)
            }
            
            # For volume columns, calculate consumption rates
            if 'M3' in col:
                # Calculate hourly consumption
                df_sorted = df.sort_values('timestamp')
                df_sorted[f'{col}_diff'] = df_sorted[col].diff()
                df_sorted[f'{col}_hourly'] = df_sorted[f'{col}_diff'] / (df_sorted['timestamp'].diff().dt.total_seconds() / 3600)
                
                hourly_consumption = df_sorted[df_sorted[f'{col}_hourly'] > 0].groupby('hour')[f'{col}_hourly'].mean()
                patterns[node_name]['hourly_consumption'] = hourly_consumption.to_dict()
                patterns[node_name]['avg_hourly_consumption'] = float(hourly_consumption.mean()) if len(hourly_consumption) > 0 else 0
    
    # Save patterns
    with open('data_patterns.json', 'w') as f:
        json.dump(patterns, f, indent=2)
    
    print("\n💾 Patterns saved to data_patterns.json")
    
    # Create visualizations
    create_pattern_plots(df, patterns)
    
    return patterns, df

def calculate_trend(df, column):
    """Calculate linear trend over time."""
    if df[column].notna().sum() < 10:
        return 0.0
    
    # Use ordinal time for trend calculation
    x = df[df[column].notna()]['timestamp'].map(lambda x: x.toordinal())
    y = df[df[column].notna()][column]
    
    if len(x) > 1:
        if SCIPY_AVAILABLE:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            return float(slope)
        else:
            # Simple trend calculation without scipy
            x_mean = x.mean()
            y_mean = y.mean()
            numerator = ((x - x_mean) * (y - y_mean)).sum()
            denominator = ((x - x_mean) ** 2).sum()
            if denominator > 0:
                slope = numerator / denominator
                return float(slope)
    return 0.0

def calculate_seasonality(df, column):
    """Calculate monthly seasonality factors."""
    if df[column].notna().sum() < 10:
        return {}
    
    monthly_avg = df.groupby('month')[column].mean()
    overall_avg = df[column].mean()
    
    if overall_avg > 0:
        seasonality = (monthly_avg / overall_avg).to_dict()
    else:
        seasonality = monthly_avg.to_dict()
    
    return {int(k): float(v) for k, v in seasonality.items()}

def create_pattern_plots(df, patterns):
    """Create visualization plots of the patterns."""
    if not PLOTTING_AVAILABLE:
        print("\n⚠️  Skipping visualizations (matplotlib not available)")
        return
        
    print("\n📈 Creating pattern visualizations...")
    
    # Set up the plot style
    try:
        plt.style.use('seaborn-v0_8-darkgrid')
    except:
        plt.style.use('default')
    
    # Create hourly pattern plot for key metrics
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Hourly Patterns for Key Nodes', fontsize=16)
    
    plot_configs = [
        ('NODE01_flow', 'NODE01 Flow Rate (L/s)', axes[0, 0]),
        ('TANK01', 'TANK01 Volume (m³)', axes[0, 1]),
        ('NODE01_pressure', 'NODE01 Pressure (bar)', axes[1, 0]),
        ('MONITOR01_flow', 'MONITOR01 Flow Rate (L/s)', axes[1, 1])
    ]
    
    for node_name, title, ax in plot_configs:
        if node_name in patterns:
            pattern = patterns[node_name]
            hours = sorted(pattern['hourly_pattern'].keys())
            
            if pattern.get('weekday_pattern'):
                weekday_values = [pattern['weekday_pattern'].get(h, 0) for h in hours]
                weekend_values = [pattern['weekend_pattern'].get(h, 0) for h in hours]
                
                ax.plot(hours, weekday_values, 'b-', label='Weekday', linewidth=2)
                ax.plot(hours, weekend_values, 'r--', label='Weekend', linewidth=2)
                ax.legend()
            else:
                values = [pattern['hourly_pattern'].get(h, 0) for h in hours]
                ax.plot(hours, values, 'b-', linewidth=2)
            
            ax.set_xlabel('Hour of Day')
            ax.set_ylabel('Average Value')
            ax.set_title(title)
            ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('hourly_patterns.png', dpi=150, bbox_inches='tight')
    print("  ✅ Saved hourly_patterns.png")
    
    # Create consumption pattern for volumes
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    
    # Plot cumulative volume for TANK01
    df_sorted = df.sort_values('timestamp')
    ax2.plot(df_sorted['timestamp'], df_sorted['M3.3'], label='TANK01 Volume', linewidth=2)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Volume (m³)')
    ax2.set_title('TANK01 (Storage Tank) Volume Over Time')
    ax2.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('tank_volume_trend.png', dpi=150, bbox_inches='tight')
    print("  ✅ Saved tank_volume_trend.png")

if __name__ == "__main__":
    patterns, df = analyze_data_patterns()
    
    print("\n✅ Pattern analysis complete!")
    print(f"   Analyzed {len(patterns)} metrics")
    print(f"   Data points: {len(df)}")
    print("\n📊 Summary of key patterns:")
    
    for node, data in patterns.items():
        if 'flow' in node.lower() or node in ['NODE01', 'TANK01']:
            print(f"\n{node}:")
            print(f"  Mean: {data['mean']:.2f}")
            print(f"  Daily variation: {data['daily_variation']:.2f}")
            if 'avg_hourly_consumption' in data:
                print(f"  Avg hourly consumption: {data['avg_hourly_consumption']:.2f}")
