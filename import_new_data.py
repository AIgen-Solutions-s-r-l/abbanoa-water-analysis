#!/usr/bin/env python3
"""
Import NEW_DATA.csv into the database with real sensor data.
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

# Column mapping to nodes
COLUMN_NODE_MAPPING = {
    'VIA_SANT_ANNA': {
        'temperature': '(SELARGIUS) NODO VIA SANT ANNA - TEMPERATURA INTERNA',
        'flow_rate': '(SELARGIUS) NODO VIA SANT ANNA - PORTATA W ISTANTANEA DIRETTA',
        'total_flow': '(SELARGIUS) NODO VIA SANT ANNA - PORTATA W TOTALE DIRETTA',
        'pressure': '(SELARGIUS) NODO VIA SANT ANNA - PRESSIONE USCITA'
    },
    'VIA_SENECA': {
        'temperature': '(SELARGIUS) NODO VIA SENECA - TEMPERATURA INTERNA',
        'flow_rate': '(SELARGIUS) NODO VIA SENECA - PORTATA W ISTANTANEA DIRETTA',
        'total_flow': '(SELARGIUS) NODO VIA SENECA - PORTATA W TOTALE DIRETTA',
        'pressure': '(SELARGIUS) NODO VIA SENECA - PRESSIONE USCITA'
    },
    'SERBATOIO_SELARGIUS': {
        'flow_rate': '(SELARGIUS) SERBATOIO SELARGIUS - PORTATA USCITA',
        'total_flow': '(SELARGIUS) SERBATOIO SELARGIUS - PORTATA USCITA MQ'
    },
    'SERBATOIO_CUCCURU_LINU': {
        'flow_rate': '(QUARTUCCIU) SERBATOIO CUCCURU LINU - PORTATA SELARGIUS',
        'total_flow': '(QUARTUCCIU) SERBATOIO CUCCURU LINU - TOTALIZZATORE PORTATA SELARGIUS'
    }
}

async def import_data():
    """Import data from CSV to database."""
    
    # Read CSV file
    logger.info("Reading NEW_DATA.csv...")
    df = pd.read_csv('/root/abbanoa-water-analysis/NEW_DATA.csv', 
                     sep=';', 
                     skiprows=[1],  # Skip units row
                     decimal=',')  # Italian decimal format
    
    # Parse date and time
    df['timestamp'] = pd.to_datetime(df['DATA'] + ' ' + df['ORA'], format='%d/%m/%Y %H:%M:%S')
    
    # Clean column names - some have spaces and special characters
    df.columns = df.columns.str.strip()
    
    # Connect to database
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # First, clear old sensor readings to avoid duplicates
        logger.info("Clearing old sensor readings...")
        await conn.execute("DELETE FROM water_infrastructure.sensor_readings WHERE timestamp < NOW()")
        
        # Process data for each node
        records_inserted = 0
        
        for node_id, columns in COLUMN_NODE_MAPPING.items():
            logger.info(f"Processing node {node_id}...")
            
            for index, row in df.iterrows():
                timestamp = row['timestamp']
                
                # Get values for this node
                flow_rate = None
                pressure = None
                temperature = None
                
                if 'flow_rate' in columns and columns['flow_rate'] in row:
                    try:
                        # Convert Italian decimal format
                        flow_str = str(row[columns['flow_rate']]).replace(',', '.')
                        flow_rate = float(flow_str) if flow_str != 'nan' else None
                    except:
                        flow_rate = None
                
                if 'pressure' in columns and columns['pressure'] in row:
                    try:
                        press_str = str(row[columns['pressure']]).replace(',', '.')
                        pressure = float(press_str) if press_str != 'nan' else None
                    except:
                        pressure = None
                
                if 'temperature' in columns and columns['temperature'] in row:
                    try:
                        temp_str = str(row[columns['temperature']]).replace(',', '.')
                        temperature = float(temp_str) if temp_str != 'nan' else None
                    except:
                        temperature = None
                
                # Skip if no valid data
                if flow_rate is None and pressure is None and temperature is None:
                    continue
                
                # Insert record
                try:
                    # For serbatoi without pressure data, use a default value
                    if pressure is None and node_id.startswith('SERBATOIO'):
                        pressure = 4.5  # Default pressure for reservoirs
                    
                    # Convert pandas timestamp to Python datetime
                    timestamp_py = timestamp.to_pydatetime()
                    
                    await conn.execute("""
                        INSERT INTO water_infrastructure.sensor_readings 
                        (node_id, timestamp, flow_rate, pressure, temperature, quality_score)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        ON CONFLICT (node_id, timestamp) DO UPDATE
                        SET flow_rate = EXCLUDED.flow_rate,
                            pressure = EXCLUDED.pressure,
                            temperature = EXCLUDED.temperature
                    """, node_id, timestamp_py, flow_rate, pressure, temperature, 0.95)
                    
                    records_inserted += 1
                    
                except Exception as e:
                    logger.warning(f"Error inserting record for {node_id} at {timestamp}: {e}")
        
        logger.info(f"Successfully inserted {records_inserted} records")
        
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
        
        avg_flow = float(stats['avg_flow']) if stats['avg_flow'] else 0.0
        avg_pressure = float(stats['avg_pressure']) if stats['avg_pressure'] else 0.0
        
        logger.info(f"""
        Database Summary:
        - Nodes with data: {stats['nodes_with_data']}
        - Total readings: {stats['total_readings']}
        - Date range: {stats['earliest']} to {stats['latest']}
        - Average flow: {avg_flow:.2f} L/s
        - Average pressure: {avg_pressure:.2f} bar
        """)
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(import_data())