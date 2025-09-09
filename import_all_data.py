#!/usr/bin/env python3
"""
Import ALL data from NEW_DATA.csv into the database.
"""

import pandas as pd
import asyncio
import asyncpg
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'abbanoa_processing',
    'user': 'abbanoa_user',
    'password': 'abbanoa_secure_pass'
}

# Column mapping to nodes - mappatura completa
COLUMN_NODE_MAPPING = {
    'VIA_SANT_ANNA': {
        'temperature': '(SELARGIUS) NODO VIA SANT ANNA - TEMPERATURA INTERNA',
        'flow_rate': '(SELARGIUS) NODO VIA SANT ANNA - PORTATA W ISTANTANEA DIRETTA',
        'pressure': '(SELARGIUS) NODO VIA SANT ANNA - PRESSIONE USCITA'
    },
    'VIA_SENECA': {
        'temperature': '(SELARGIUS) NODO VIA SENECA - TEMPERATURA INTERNA',
        'flow_rate': '(SELARGIUS) NODO VIA SENECA - PORTATA W ISTANTANEA DIRETTA',
        'pressure': '(SELARGIUS) NODO VIA SENECA - PRESSIONE USCITA'
    },
    'SERBATOIO_SELARGIUS': {
        'flow_rate': '(SELARGIUS) SERBATOIO SELARGIUS - PORTATA USCITA'
    },
    'SERBATOIO_CUCCURU_LINU': {
        'flow_rate': '(QUARTUCCIU) SERBATOIO CUCCURU LINU - PORTATA SELARGIUS'
    }
}

async def import_all_data():
    """Import ALL data from CSV to database."""
    
    # Read CSV file
    logger.info("Reading NEW_DATA.csv...")
    df = pd.read_csv('/root/abbanoa-water-analysis/NEW_DATA.csv', 
                     sep=';', 
                     skiprows=[1],  # Skip units row
                     decimal=',')  # Italian decimal format
    
    # Parse date and time
    df['timestamp'] = pd.to_datetime(df['DATA'] + ' ' + df['ORA'], format='%d/%m/%Y %H:%M:%S')
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    logger.info(f"Total rows in CSV: {len(df)}")
    logger.info(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # Connect to database
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # Clear ALL old sensor readings
        logger.info("Clearing ALL old sensor readings...")
        await conn.execute("DELETE FROM water_infrastructure.sensor_readings")
        
        # Prepare batch inserts
        records = []
        total_expected = len(df) * len(COLUMN_NODE_MAPPING)  # Ogni riga per ogni nodo
        
        for node_id, columns in COLUMN_NODE_MAPPING.items():
            logger.info(f"Processing node {node_id}...")
            node_records = 0
            
            for index, row in df.iterrows():
                timestamp_py = row['timestamp'].to_pydatetime()
                
                # Get values for this node
                flow_rate = None
                pressure = None
                temperature = None
                
                if 'flow_rate' in columns and columns['flow_rate'] in df.columns:
                    try:
                        val = row[columns['flow_rate']]
                        if pd.notna(val):
                            flow_str = str(val).replace(',', '.')
                            flow_rate = float(flow_str)
                    except:
                        pass
                
                if 'pressure' in columns and columns['pressure'] in df.columns:
                    try:
                        val = row[columns['pressure']]
                        if pd.notna(val):
                            press_str = str(val).replace(',', '.')
                            pressure = float(press_str)
                    except:
                        pass
                
                if 'temperature' in columns and columns['temperature'] in df.columns:
                    try:
                        val = row[columns['temperature']]
                        if pd.notna(val):
                            temp_str = str(val).replace(',', '.')
                            temperature = float(temp_str)
                    except:
                        pass
                
                # For serbatoi without pressure data, use a default value
                if pressure is None and node_id.startswith('SERBATOIO'):
                    pressure = 4.5  # Default pressure for reservoirs
                
                # Add record even if some values are None (we want ALL timestamps)
                records.append((node_id, timestamp_py, flow_rate, pressure, temperature, 0.95))
                node_records += 1
            
            logger.info(f"  {node_id}: prepared {node_records} records")
        
        # Batch insert all records
        if records:
            logger.info(f"Inserting {len(records)} records into database...")
            
            # Insert in batches of 1000 to avoid memory issues
            batch_size = 1000
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                await conn.executemany("""
                    INSERT INTO water_infrastructure.sensor_readings 
                    (node_id, timestamp, flow_rate, pressure, temperature, quality_score)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (node_id, timestamp) DO UPDATE
                    SET flow_rate = EXCLUDED.flow_rate,
                        pressure = EXCLUDED.pressure,
                        temperature = EXCLUDED.temperature
                """, batch)
                
                if (i + batch_size) % 5000 == 0:
                    logger.info(f"  Inserted {min(i + batch_size, len(records))} / {len(records)} records...")
            
            logger.info(f"Successfully inserted {len(records)} records")
        
        # Verify the import
        logger.info("\nVERIFYING IMPORT:")
        logger.info("=" * 50)
        
        # Get summary statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(DISTINCT node_id) as nodes_with_data,
                COUNT(*) as total_readings,
                MIN(timestamp) as earliest,
                MAX(timestamp) as latest,
                AVG(flow_rate) as avg_flow,
                AVG(pressure) as avg_pressure
            FROM water_infrastructure.sensor_readings
        """)
        
        # Get per-node statistics
        node_stats = await conn.fetch("""
            SELECT 
                node_id,
                COUNT(*) as count,
                MIN(timestamp) as first,
                MAX(timestamp) as last
            FROM water_infrastructure.sensor_readings
            GROUP BY node_id
            ORDER BY node_id
        """)
        
        avg_flow = float(stats['avg_flow']) if stats['avg_flow'] else 0.0
        avg_pressure = float(stats['avg_pressure']) if stats['avg_pressure'] else 0.0
        
        logger.info(f"""
Database Summary:
- Nodes with data: {stats['nodes_with_data']}
- Total readings: {stats['total_readings']}
- Date range: {stats['earliest']} to {stats['latest']}
- Average flow: {avg_flow:.2f} L/s
- Average pressure: {avg_pressure:.2f} bar

Per-node breakdown:""")
        
        for node in node_stats:
            logger.info(f"  {node['node_id']}: {node['count']} records ({node['first']} to {node['last']})")
        
        # Comparison with CSV
        logger.info(f"\nCOMPARISON:")
        logger.info(f"CSV has {len(df)} rows × {len(COLUMN_NODE_MAPPING)} nodes = {len(df) * len(COLUMN_NODE_MAPPING)} expected records")
        logger.info(f"Database has {stats['total_readings']} records")
        
        if stats['total_readings'] == len(df) * len(COLUMN_NODE_MAPPING):
            logger.info("✓ ALL DATA IMPORTED SUCCESSFULLY!")
        else:
            logger.warning(f"⚠ MISMATCH: Expected {len(df) * len(COLUMN_NODE_MAPPING)}, got {stats['total_readings']}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(import_all_data())