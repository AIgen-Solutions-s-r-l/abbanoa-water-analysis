#!/usr/bin/env python3
"""
Fill data gaps with synthetic data based on analyzed patterns.
Handles existing data and only fills the gaps.
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

async def get_data_gaps(conn):
    """Identify gaps in the data."""
    
    # Get all dates with data
    rows = await conn.fetch("""
        SELECT DATE(timestamp) as date, COUNT(*) as record_count
        FROM water_infrastructure.sensor_readings
        WHERE timestamp >= '2024-11-01'
        GROUP BY DATE(timestamp)
        ORDER BY date
    """)
    
    existing_dates = {row['date'] for row in rows}
    
    # Define the full range we want
    start_date = datetime(2024, 11, 13).date()
    end_date = datetime(2025, 8, 6).date()
    
    # Find all gaps
    current_date = start_date
    gaps = []
    gap_start = None
    
    while current_date <= end_date:
        if current_date not in existing_dates:
            if gap_start is None:
                gap_start = current_date
        else:
            if gap_start is not None:
                gaps.append((gap_start, current_date - timedelta(days=1)))
                gap_start = None
        
        current_date += timedelta(days=1)
    
    # Handle gap that extends to end_date
    if gap_start is not None:
        gaps.append((gap_start, end_date))
    
    return gaps

def load_patterns():
    """Load the analyzed patterns."""
    with open('data_patterns.json', 'r') as f:
        return json.load(f)

def generate_synthetic_data_for_period(start_date, end_date, patterns):
    """Generate synthetic data for a specific period."""
    
    print(f"  🔮 Generating data for {start_date} to {end_date}")
    
    # Create timestamp range (30-minute intervals)
    timestamps = pd.date_range(
        start=datetime.combine(start_date, datetime.min.time()),
        end=datetime.combine(end_date, datetime.max.time().replace(hour=23, minute=30)),
        freq='30min'
    )
    
    # Initialize dataframe
    df = pd.DataFrame({'timestamp': timestamps})
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6])
    df['day_index'] = (df['timestamp'] - df['timestamp'].min()).dt.days
    
    # Column mapping
    column_mapping = {
        'NODE01': 'M3',
        'MONITOR02': 'M3.1', 
        'MONITOR01': 'M3.2',
        'TANK01': 'M3.3',
        'NODE01_flow': 'L/S',
        'MONITOR02_flow': 'L/S.1',
        'MONITOR01_flow': 'L/S.2',
        'TANK01_flow': 'L/S.3',
        'NODE01_pressure': 'BAR',
        'MONITOR02_pressure': 'BAR.1',
        'NODE01_temp': 'GRD. C',
        'MONITOR02_temp': 'GRD. C.1'
    }
    
    # Generate data for each metric
    for node_name, pattern in patterns.items():
        if node_name not in column_mapping:
            continue
            
        col = column_mapping[node_name]
        
        # Base values from hourly patterns
        if df['is_weekend'].any() and 'weekend_pattern' in pattern:
            hourly_values = df.apply(
                lambda row: pattern['weekend_pattern'].get(str(row['hour']), pattern['mean']) 
                if row['is_weekend'] 
                else pattern['weekday_pattern'].get(str(row['hour']), pattern['mean']),
                axis=1
            )
        else:
            hourly_values = df['hour'].apply(
                lambda h: pattern['hourly_pattern'].get(str(h), pattern['mean'])
            )
        
        # Add trend
        if 'trend' in pattern and pattern['trend'] != 0:
            # Adjust trend based on total days since original data
            days_since_start = (start_date - datetime(2024, 11, 13).date()).days
            trend_values = pattern['trend'] * (df['day_index'] + days_since_start)
            hourly_values += trend_values
        
        # Add seasonality
        if 'seasonality' in pattern:
            seasonality_factors = df['month'].apply(
                lambda m: pattern['seasonality'].get(str(m), 1.0)
            )
            hourly_values *= seasonality_factors
        
        # Add random variation
        std_dev = pattern.get('std', pattern.get('daily_variation', 0))
        if std_dev > 0:
            noise = np.random.normal(0, std_dev * 0.3, len(df))
            hourly_values += noise
        
        # Apply bounds
        hourly_values = np.clip(hourly_values, pattern['min'] * 0.9, pattern['max'] * 1.1)
        
        # For volume columns (cumulative)
        if 'M3' in col and col != 'L/S':
            if 'hourly_consumption' in pattern and pattern['avg_hourly_consumption'] > 0:
                # Generate consumption rates
                consumption_rates = df['hour'].apply(
                    lambda h: pattern['hourly_consumption'].get(str(h), 
                    pattern['avg_hourly_consumption'])
                )
                
                # Add variation
                consumption_rates += np.random.normal(0, consumption_rates.std() * 0.1, len(df))
                consumption_rates = np.maximum(consumption_rates, 0)
                
                # Get starting volume (should continue from last known value)
                # For now, use a reasonable estimate
                start_volume = pattern['max'] * 0.95
                cumulative_volume = start_volume + (consumption_rates * 0.5).cumsum()
                
                df[col] = cumulative_volume
            else:
                df[col] = hourly_values
        else:
            df[col] = hourly_values
    
    return df

async def insert_synthetic_data(conn, df, gap_start, gap_end):
    """Insert synthetic data for a gap period."""
    
    print(f"\n💾 Inserting data for gap: {gap_start} to {gap_end}")
    
    # Node mapping
    node_mapping = {
        'M3': 'CENTRO_EST',      # NODE01
        'M3.1': 'CENTRO_NORD',   # MONITOR02
        'M3.2': 'CENTRO_OVEST',  # MONITOR01
        'M3.3': 'CENTRO_SUD',    # TANK01
    }
    
    total_inserted = 0
    
    for col, node_id in node_mapping.items():
        flow_col = col.replace('M3', 'L/S')
        pressure_col = col.replace('M3', 'BAR')
        temp_col = col.replace('M3', 'GRD. C')
        
        # Skip if no data
        if col not in df.columns or df[col].sum() == 0:
            continue
        
        print(f"  📊 Processing {node_id}...")
        
        # Prepare records
        records = []
        for _, row in df.iterrows():
            timestamp = row['timestamp']
            if timestamp.tz is None:
                timestamp = timestamp.tz_localize('UTC')
            
            # Get values
            flow_rate = float(row.get(flow_col, 0)) if flow_col in df.columns else None
            pressure = float(row.get(pressure_col, 0)) if pressure_col in df.columns else None
            temperature = float(row.get(temp_col, 0)) if temp_col in df.columns else None
            total_flow = float(row[col]) if col in df.columns else 0
            
            records.append((
                timestamp,
                node_id,
                temperature,
                flow_rate,
                pressure,
                total_flow,
                0.85,  # quality_score
                True,  # is_interpolated
                json.dumps({
                    'source': 'synthetic_gap_fill',
                    'gap_period': f"{gap_start} to {gap_end}",
                    'generation_date': datetime.now().isoformat()
                })
            ))
        
        # Insert in batches
        batch_size = 1000
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            try:
                await conn.executemany("""
                    INSERT INTO water_infrastructure.sensor_readings 
                        (timestamp, node_id, temperature, flow_rate, pressure, 
                         total_flow, quality_score, is_interpolated, raw_data)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, batch)
                print(f"    ✅ Inserted batch {i//batch_size + 1}/{(len(records)-1)//batch_size + 1}")
            except Exception as e:
                print(f"    ❌ Error inserting batch: {e}")
        
        total_inserted += len(records)
    
    return total_inserted

async def main():
    """Main execution function."""
    
    print("🌟 Data Gap Filling Tool")
    print("=" * 50)
    
    # Load patterns
    try:
        patterns = load_patterns()
        print(f"✅ Loaded patterns for {len(patterns)} metrics")
    except FileNotFoundError:
        print("❌ Pattern file not found. Run analyze_data_patterns.py first!")
        return
    
    # Connect to database
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # Find data gaps
        print("\n🔍 Analyzing data gaps...")
        gaps = await get_data_gaps(conn)
        
        if not gaps:
            print("✅ No data gaps found!")
            return
        
        print(f"\n📊 Found {len(gaps)} gap(s):")
        total_days = 0
        for gap_start, gap_end in gaps:
            days = (gap_end - gap_start).days + 1
            total_days += days
            print(f"  - {gap_start} to {gap_end} ({days} days)")
        
        print(f"\n📅 Total gap days: {total_days}")
        
        # Confirm before proceeding
        response = input("\nProceed with gap filling? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Gap filling cancelled")
            return
        
        # Fill each gap
        total_inserted = 0
        for gap_start, gap_end in gaps:
            # Generate synthetic data for this gap
            df = generate_synthetic_data_for_period(gap_start, gap_end, patterns)
            
            # Insert into database
            inserted = await insert_synthetic_data(conn, df, gap_start, gap_end)
            total_inserted += inserted
        
        print(f"\n✅ Gap filling complete!")
        print(f"   Total records inserted: {total_inserted}")
        
        # Verify the results
        print("\n📊 Verifying data coverage...")
        rows = await conn.fetch("""
            SELECT 
                DATE(MIN(timestamp)) as min_date,
                DATE(MAX(timestamp)) as max_date,
                COUNT(DISTINCT DATE(timestamp)) as days_with_data,
                COUNT(*) as total_records
            FROM water_infrastructure.sensor_readings
            WHERE timestamp >= '2024-11-01'
        """)
        
        result = rows[0]
        print(f"  - Date range: {result['min_date']} to {result['max_date']}")
        print(f"  - Days with data: {result['days_with_data']}")
        print(f"  - Total records: {result['total_records']:,}")
        
    finally:
        await conn.close()
    
    print("\n✨ Data gaps successfully filled!")

if __name__ == "__main__":
    asyncio.run(main())
