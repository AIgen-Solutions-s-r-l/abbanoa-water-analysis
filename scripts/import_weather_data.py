#!/usr/bin/env python3
"""Import weather data from CSV files into PostgreSQL database."""

import asyncio
import asyncpg
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5434,
    'database': 'abbanoa_processing',
    'user': 'abbanoa_user',
    'password': 'abbanoa_secure_pass'
}

# SQL for creating weather data table
CREATE_WEATHER_TABLE = """
CREATE TABLE IF NOT EXISTS water_infrastructure.weather_data (
    id SERIAL PRIMARY KEY,
    location VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    avg_temperature_c NUMERIC(5,2),
    min_temperature_c NUMERIC(5,2),
    max_temperature_c NUMERIC(5,2),
    dew_point_c NUMERIC(5,2),
    humidity_percent INTEGER,
    visibility_km NUMERIC(5,2),
    avg_wind_speed_kmh NUMERIC(5,2),
    max_wind_speed_kmh NUMERIC(5,2),
    wind_gust_kmh NUMERIC(5,2),
    sea_level_pressure_mb NUMERIC(6,2),
    avg_pressure_mb NUMERIC(6,2),
    rainfall_mm NUMERIC(6,2),
    weather_phenomena TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(location, date)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_weather_location_date ON water_infrastructure.weather_data(location, date);
CREATE INDEX IF NOT EXISTS idx_weather_date ON water_infrastructure.weather_data(date);
CREATE INDEX IF NOT EXISTS idx_weather_location ON water_infrastructure.weather_data(location);
CREATE INDEX IF NOT EXISTS idx_weather_temperature ON water_infrastructure.weather_data(avg_temperature_c);
CREATE INDEX IF NOT EXISTS idx_weather_rainfall ON water_infrastructure.weather_data(rainfall_mm);
"""

def parse_italian_number(value_str):
    """Parse Italian number format (comma as decimal separator)."""
    if pd.isna(value_str) or value_str == '' or value_str == '0':
        return None
    try:
        # Replace comma with dot for decimal separator
        return float(str(value_str).replace(',', '.'))
    except:
        return None

def parse_italian_date(date_str):
    """Parse Italian date format (D/M/YYYY)."""
    try:
        return datetime.strptime(date_str, '%d/%m/%Y').date()
    except:
        return None

async def create_weather_table(conn):
    """Create the weather data table if it doesn't exist."""
    logger.info("Creating weather data table...")
    await conn.execute(CREATE_WEATHER_TABLE)
    logger.info("Weather data table created successfully")

async def import_csv_file(conn, filepath):
    """Import a single CSV file into the database."""
    logger.info(f"Processing file: {filepath}")
    
    try:
        # Read CSV with semicolon separator
        df = pd.read_csv(filepath, sep=';', encoding='utf-8')
        
        # Get location from filename (e.g., "Selargius" from "Selargius-2024-Gennaio.csv")
        location = Path(filepath).stem.split('-')[0]
        
        inserted_count = 0
        skipped_count = 0
        
        for _, row in df.iterrows():
            try:
                # Parse date
                date = parse_italian_date(row['DATA'])
                if not date:
                    continue
                
                # Parse numeric values
                avg_temp = parse_italian_number(row['TMEDIA °C'])
                min_temp = parse_italian_number(row['TMIN °C'])
                max_temp = parse_italian_number(row['TMAX °C'])
                dew_point = parse_italian_number(row['PUNTORUGIADA °C'])
                humidity = int(row['UMIDITA %']) if pd.notna(row['UMIDITA %']) and row['UMIDITA %'] != '0' else None
                visibility = parse_italian_number(row['VISIBILITA km'])
                avg_wind = parse_italian_number(row['VENTOMEDIA km/h'])
                max_wind = parse_italian_number(row['VENTOMAX km/h'])
                gust = parse_italian_number(row['RAFFICA km/h'])
                sea_pressure = parse_italian_number(row['PRESSIONESLM mb'])
                avg_pressure = parse_italian_number(row['PRESSIONEMEDIA mb'])
                rainfall = parse_italian_number(row['PIOGGIA mm'])
                phenomena = row['FENOMENI'] if pd.notna(row['FENOMENI']) and row['FENOMENI'] != '' else None
                
                # Insert into database
                try:
                    await conn.execute("""
                        INSERT INTO water_infrastructure.weather_data 
                        (location, date, avg_temperature_c, min_temperature_c, max_temperature_c,
                         dew_point_c, humidity_percent, visibility_km, avg_wind_speed_kmh,
                         max_wind_speed_kmh, wind_gust_kmh, sea_level_pressure_mb,
                         avg_pressure_mb, rainfall_mm, weather_phenomena)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                        ON CONFLICT (location, date) DO NOTHING
                    """, location, date, avg_temp, min_temp, max_temp,
                        dew_point, humidity, visibility, avg_wind,
                        max_wind, gust, sea_pressure,
                        avg_pressure, rainfall, phenomena)
                    inserted_count += 1
                except Exception as e:
                    logger.warning(f"Error inserting row for {location} on {date}: {e}")
                    skipped_count += 1
                    
            except Exception as e:
                logger.warning(f"Error processing row: {e}")
                skipped_count += 1
                continue
        
        logger.info(f"Completed {filepath}: {inserted_count} inserted, {skipped_count} skipped")
        return inserted_count, skipped_count
        
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return 0, 0

async def import_all_weather_data():
    """Import all weather CSV files from TEMP directory."""
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # Create table if it doesn't exist
        await create_weather_table(conn)
        
        # Get all CSV files in TEMP directory
        temp_dir = Path('TEMP')
        csv_files = list(temp_dir.glob('*.csv'))
        
        logger.info(f"Found {len(csv_files)} CSV files to process")
        
        total_inserted = 0
        total_skipped = 0
        
        # Process each file
        for csv_file in sorted(csv_files):
            inserted, skipped = await import_csv_file(conn, csv_file)
            total_inserted += inserted
            total_skipped += skipped
        
        # Get summary statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(DISTINCT location) as locations,
                COUNT(*) as total_records,
                MIN(date) as earliest_date,
                MAX(date) as latest_date,
                AVG(avg_temperature_c) as avg_temp,
                SUM(rainfall_mm) as total_rainfall
            FROM water_infrastructure.weather_data
        """)
        
        logger.info(f"\n=== Import Summary ===")
        logger.info(f"Total records imported: {total_inserted}")
        logger.info(f"Total records skipped: {total_skipped}")
        logger.info(f"\n=== Database Statistics ===")
        logger.info(f"Locations: {stats['locations']}")
        logger.info(f"Total records: {stats['total_records']}")
        logger.info(f"Date range: {stats['earliest_date']} to {stats['latest_date']}")
        logger.info(f"Average temperature: {stats['avg_temp']:.1f}°C")
        logger.info(f"Total rainfall: {stats['total_rainfall']:.1f}mm")
        
    finally:
        await conn.close()

async def verify_import():
    """Verify the imported data with some sample queries."""
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # Sample data from each location
        logger.info("\n=== Sample Data ===")
        locations = await conn.fetch("""
            SELECT DISTINCT location 
            FROM water_infrastructure.weather_data 
            ORDER BY location
        """)
        
        for loc in locations:
            sample = await conn.fetchrow("""
                SELECT date, avg_temperature_c, rainfall_mm, weather_phenomena
                FROM water_infrastructure.weather_data
                WHERE location = $1
                ORDER BY date DESC
                LIMIT 1
            """, loc['location'])
            
            logger.info(f"{loc['location']}: Latest data on {sample['date']} - "
                       f"Temp: {sample['avg_temperature_c']}°C, "
                       f"Rain: {sample['rainfall_mm']}mm, "
                       f"Weather: {sample['weather_phenomena'] or 'Clear'}")
        
        # Monthly averages
        logger.info("\n=== Monthly Temperature Averages (2024) ===")
        monthly_avg = await conn.fetch("""
            SELECT 
                EXTRACT(MONTH FROM date) as month,
                location,
                AVG(avg_temperature_c) as avg_temp,
                SUM(rainfall_mm) as total_rain
            FROM water_infrastructure.weather_data
            WHERE EXTRACT(YEAR FROM date) = 2024
            GROUP BY EXTRACT(MONTH FROM date), location
            ORDER BY location, month
            LIMIT 10
        """)
        
        for row in monthly_avg:
            logger.info(f"{row['location']} - Month {int(row['month'])}: "
                       f"Avg Temp: {row['avg_temp']:.1f}°C, "
                       f"Total Rain: {row['total_rain']:.1f}mm")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    logger.info("Starting weather data import...")
    asyncio.run(import_all_weather_data())
    
    logger.info("\nVerifying imported data...")
    asyncio.run(verify_import())
    
    logger.info("\nWeather data import completed successfully!") 