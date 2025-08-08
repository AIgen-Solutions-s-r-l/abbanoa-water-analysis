#!/usr/bin/env python3
"""
Weather-Aware Hourly Synthetic Data Generator for Abbanoa Water Infrastructure
Integrates real-time weather data to create more realistic sensor readings
"""

import asyncio
import asyncpg
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import json
from typing import Dict, List, Tuple, Optional
import logging
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from weather_integration import get_weather_api, calculate_weather_impact, WeatherData

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/alessio/Customers/Abbanoa/logs/hourly_data_generator_weather.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5434,
    'database': 'abbanoa_processing',
    'user': 'abbanoa_user',
    'password': 'abbanoa_secure_pass'
}

# Data patterns file
PATTERNS_FILE = '/home/alessio/Customers/Abbanoa/scripts/data_patterns.json'

# Weather API configuration (set your API key here or in environment)
WEATHER_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY', None)
CAGLIARI_LAT = 39.2238
CAGLIARI_LON = 9.1217

def load_data_patterns() -> Dict:
    """Load pre-analyzed data patterns"""
    if os.path.exists(PATTERNS_FILE):
        try:
            with open(PATTERNS_FILE, 'r') as f:
                raw_patterns = json.load(f)
            
            # Convert node-specific patterns to general patterns
            if 'TANK01' in raw_patterns and 'hourly_pattern' in raw_patterns['TANK01']:
                hourly = raw_patterns['TANK01']['hourly_pattern']
                daily = raw_patterns['TANK01'].get('daily_pattern', {str(d): 1.0 for d in range(7)})
                
                # Normalize patterns
                avg_hourly = sum(float(v) for v in hourly.values()) / len(hourly)
                normalized_hourly = {k: float(v) / avg_hourly for k, v in hourly.items()}
                
                return {
                    'hourly_patterns': normalized_hourly,
                    'daily_patterns': daily,
                    'monthly_patterns': {str(m): 1.0 for m in range(1, 13)},
                    'base_values': {
                        'temperature': 22.0,
                        'flow_rate': 150.0,
                        'pressure': 3.5,
                        'total_flow': 3600.0
                    },
                    'variations': {
                        'temperature': 2.0,
                        'flow_rate': 30.0,
                        'pressure': 0.5,
                        'total_flow': 500.0
                    }
                }
            else:
                return get_default_patterns()
        except Exception as e:
            logger.warning(f"Error loading patterns: {e}")
            return get_default_patterns()
    else:
        return get_default_patterns()

def get_default_patterns() -> Dict:
    """Default patterns if patterns file is not available"""
    return {
        'hourly_patterns': {str(h): 1.0 for h in range(24)},
        'daily_patterns': {str(d): 1.0 for d in range(7)},
        'monthly_patterns': {str(m): 1.0 for m in range(1, 13)},
        'base_values': {
            'temperature': 22.0,
            'flow_rate': 150.0,
            'pressure': 3.5,
            'total_flow': 3600.0
        },
        'variations': {
            'temperature': 2.0,
            'flow_rate': 30.0,
            'pressure': 0.5,
            'total_flow': 500.0
        }
    }

def get_node_specific_multipliers(node_type: str) -> Dict[str, float]:
    """Get multipliers based on node type"""
    multipliers = {
        'storage': {'flow_rate': 3.0, 'pressure': 1.2, 'total_flow': 5.0},
        'distribution': {'flow_rate': 1.5, 'pressure': 1.0, 'total_flow': 2.0},
        'monitoring': {'flow_rate': 1.0, 'pressure': 0.9, 'total_flow': 1.0},
        'interconnection': {'flow_rate': 2.0, 'pressure': 1.1, 'total_flow': 3.0},
        'zone_meter': {'flow_rate': 0.8, 'pressure': 0.85, 'total_flow': 0.8}
    }
    return multipliers.get(node_type, {'flow_rate': 1.0, 'pressure': 1.0, 'total_flow': 1.0})

def generate_sensor_reading(
    timestamp: datetime,
    node_id: str,
    node_type: str,
    patterns: Dict,
    weather_data: Optional[WeatherData] = None,
    last_values: Dict[str, float] = None
) -> Dict:
    """Generate a single sensor reading based on patterns and weather"""
    
    # Extract time components
    hour = timestamp.hour
    day_of_week = timestamp.weekday()
    month = timestamp.month
    
    # Get patterns
    hourly_mult = patterns['hourly_patterns'].get(str(hour), 1.0)
    daily_mult = patterns['daily_patterns'].get(str(day_of_week), 1.0)
    monthly_mult = patterns['monthly_patterns'].get(str(month), 1.0)
    
    # Get base values and variations
    base_values = patterns['base_values']
    variations = patterns['variations']
    
    # Get node-specific multipliers
    node_mult = get_node_specific_multipliers(node_type)
    
    # Calculate weather impact if available
    weather_impacts = {'flow_rate_multiplier': 1.0, 'pressure_multiplier': 1.0, 'temperature_offset': 0.0}
    if weather_data:
        weather_impacts = calculate_weather_impact(weather_data)
        logger.debug(f"Weather impacts: {weather_impacts}")
    
    # Generate values with patterns and random variation
    reading = {}
    
    # Temperature (affected by weather)
    base_temp = base_values.get('temperature', 20.0)
    temp_variation = variations.get('temperature', 1.0)
    
    # Water temperature is influenced by ambient temperature but with lag
    water_temp = base_temp + weather_impacts['temperature_offset']
    if last_values and 'temperature' in last_values:
        # Smooth transition from last value
        water_temp = 0.8 * last_values['temperature'] + 0.2 * water_temp
    
    reading['temperature'] = round(water_temp + np.random.normal(0, temp_variation * 0.1), 2)
    
    # Flow rate (heavily affected by weather and time patterns)
    base_flow = base_values.get('flow_rate', 150.0)
    flow_variation = variations.get('flow_rate', 30.0)
    
    # Apply all multipliers
    flow_rate = base_flow * hourly_mult * daily_mult * monthly_mult
    flow_rate *= node_mult.get('flow_rate', 1.0)
    flow_rate *= weather_impacts['flow_rate_multiplier']
    
    # Add random variation
    flow_rate *= (1.0 + np.random.normal(0, 0.05))
    
    if last_values and 'flow_rate' in last_values:
        flow_rate = 0.7 * flow_rate + 0.3 * last_values['flow_rate']
    
    reading['flow_rate'] = round(max(0.1, flow_rate), 2)
    
    # Pressure (affected by weather and flow rate)
    base_pressure = base_values.get('pressure', 3.5)
    pressure_variation = variations.get('pressure', 0.5)
    
    # Pressure inversely related to flow rate
    flow_factor = 1.0 - (reading['flow_rate'] - base_flow) / (base_flow * 3)
    pressure = base_pressure * flow_factor * weather_impacts['pressure_multiplier']
    pressure *= node_mult.get('pressure', 1.0)
    
    if last_values and 'pressure' in last_values:
        pressure = 0.8 * pressure + 0.2 * last_values['pressure']
    
    reading['pressure'] = round(max(0.1, pressure + np.random.normal(0, pressure_variation * 0.1)), 2)
    
    # Total flow (accumulation over 30 minutes)
    reading['total_flow'] = round(reading['flow_rate'] * 30.0 * 60.0 / 1000.0, 2)  # Convert to m³
    
    # Quality score (slightly affected by weather - rain can affect turbidity)
    base_quality = 0.92
    if weather_data and weather_data.rain_volume > 0:
        base_quality -= min(0.1, weather_data.rain_volume * 0.02)  # Rain reduces quality
    
    reading['quality_score'] = round(np.clip(np.random.normal(base_quality, 0.03), 0.7, 0.99), 2)
    
    return reading

async def get_latest_readings(conn: asyncpg.Connection) -> Dict[str, Dict]:
    """Get the latest sensor readings for each node"""
    query = """
    WITH latest_readings AS (
        SELECT DISTINCT ON (node_id)
            node_id,
            temperature,
            flow_rate,
            pressure,
            total_flow,
            timestamp
        FROM water_infrastructure.sensor_readings
        ORDER BY node_id, timestamp DESC
    )
    SELECT * FROM latest_readings;
    """
    
    rows = await conn.fetch(query)
    
    latest = {}
    for row in rows:
        latest[row['node_id']] = {
            'temperature': float(row['temperature']) if row['temperature'] else 22.0,
            'flow_rate': float(row['flow_rate']) if row['flow_rate'] else 150.0,
            'pressure': float(row['pressure']) if row['pressure'] else 3.5,
            'total_flow': float(row['total_flow']) if row['total_flow'] else 3600.0,
            'timestamp': row['timestamp']
        }
    
    return latest

async def check_existing_data(
    conn: asyncpg.Connection,
    node_id: str,
    start_time: datetime,
    end_time: datetime
) -> bool:
    """Check if data already exists for the given time range"""
    query = """
    SELECT COUNT(*) as count
    FROM water_infrastructure.sensor_readings
    WHERE node_id = $1
    AND timestamp >= $2
    AND timestamp < $3;
    """
    
    result = await conn.fetchval(query, node_id, start_time, end_time)
    return result > 0

async def insert_sensor_readings(
    conn: asyncpg.Connection,
    readings: List[Tuple]
) -> int:
    """Insert sensor readings into the database"""
    if not readings:
        return 0
    
    query = """
    INSERT INTO water_infrastructure.sensor_readings
    (timestamp, node_id, temperature, flow_rate, pressure, total_flow, quality_score, is_interpolated)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8);
    """
    
    try:
        await conn.executemany(query, readings)
        return len(readings)
    except Exception as e:
        logger.error(f"Error inserting readings: {e}")
        return 0

async def generate_hourly_data():
    """Main function to generate and insert hourly data with weather awareness"""
    logger.info("Starting weather-aware hourly data generation...")
    
    # Load patterns
    patterns = load_data_patterns()
    
    # Initialize weather API
    weather_api = get_weather_api(WEATHER_API_KEY)
    
    # Get current weather
    weather_data = await weather_api.get_current_weather(CAGLIARI_LAT, CAGLIARI_LON)
    if weather_data:
        logger.info(f"Current weather: {weather_data.temperature}°C, {weather_data.condition}, "
                   f"Humidity: {weather_data.humidity}%, Rain: {weather_data.rain_volume}mm/h")
    else:
        logger.warning("Could not fetch weather data, using patterns only")
    
    # Connect to database
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # Get current time (rounded to nearest 30 minutes)
        now = datetime.now(timezone.utc)
        current_minute = now.minute
        
        if current_minute < 30:
            base_time = now.replace(minute=0, second=0, microsecond=0)
            time_slot_1 = base_time - timedelta(hours=1)
            time_slot_2 = base_time - timedelta(minutes=30)
        else:
            base_time = now.replace(minute=30, second=0, microsecond=0)
            time_slot_1 = base_time - timedelta(minutes=30)
            time_slot_2 = base_time
        
        logger.info(f"Generating data for time slots: {time_slot_1} and {time_slot_2}")
        
        # Get latest readings for continuity
        latest_readings = await get_latest_readings(conn)
        
        # Get list of active nodes from database
        active_nodes = await conn.fetch("""
            SELECT node_id, node_type, node_name
            FROM water_infrastructure.nodes
            WHERE is_active = true
            ORDER BY node_id;
        """)
        
        logger.info(f"Found {len(active_nodes)} active nodes in database")
        
        # Generate readings for all active nodes
        readings_to_insert = []
        nodes_processed = 0
        
        for node_row in active_nodes:
            node_id = node_row['node_id']
            node_type = node_row['node_type']
            
            # Get last values for this node
            last_values = latest_readings.get(node_id, None)
            
            # Generate readings for both time slots
            for timestamp in [time_slot_1, time_slot_2]:
                # Check if data already exists
                if await check_existing_data(conn, node_id, timestamp, timestamp + timedelta(minutes=1)):
                    logger.debug(f"Data already exists for {node_id} at {timestamp}, skipping...")
                    continue
                
                # Generate reading with weather data
                reading = generate_sensor_reading(
                    timestamp=timestamp,
                    node_id=node_id,
                    node_type=node_type,
                    patterns=patterns,
                    weather_data=weather_data,
                    last_values=last_values
                )
                
                # Prepare for insertion
                readings_to_insert.append((
                    timestamp,
                    node_id,
                    reading['temperature'],
                    reading['flow_rate'],
                    reading['pressure'],
                    reading['total_flow'],
                    reading['quality_score'],
                    True  # is_interpolated = True for synthetic data
                ))
                
                # Update last values for next reading
                last_values = reading
            
            nodes_processed += 1
        
        # Insert all readings
        if readings_to_insert:
            inserted_count = await insert_sensor_readings(conn, readings_to_insert)
            logger.info(f"Successfully inserted {inserted_count} readings for {nodes_processed} nodes")
            
            # Log weather impact summary
            if weather_data:
                impacts = calculate_weather_impact(weather_data)
                logger.info(f"Weather impacts applied - Flow: {impacts['flow_rate_multiplier']:.0%}, "
                           f"Pressure: {impacts['pressure_multiplier']:.0%}")
        else:
            logger.info("No new data to insert (all time slots already have data)")
        
        logger.info(f"Weather-aware hourly data generation completed. Processed {nodes_processed} nodes.")
        
    except Exception as e:
        logger.error(f"Error in hourly data generation: {e}")
        raise
    finally:
        await conn.close()

async def main():
    """Main entry point"""
    try:
        await generate_hourly_data()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs('/home/alessio/Customers/Abbanoa/logs', exist_ok=True)
    
    # Run the weather-aware hourly data generation
    asyncio.run(main())
