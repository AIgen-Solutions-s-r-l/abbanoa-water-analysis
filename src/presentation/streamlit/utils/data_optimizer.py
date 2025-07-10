"""
Data optimization utility for handling large time ranges efficiently.

This module provides strategies for data sampling, aggregation, and progressive loading
to improve dashboard performance for large datasets.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID
import pandas as pd
import numpy as np
from dataclasses import dataclass

from src.domain.entities.sensor_reading import SensorReading
from src.application.interfaces.repositories import ISensorReadingRepository

logger = logging.getLogger(__name__)


@dataclass
class OptimizationStrategy:
    """Configuration for data optimization strategies."""
    
    # Time range thresholds (in days)
    REAL_TIME_THRESHOLD = 1      # < 1 day: use all data
    HOURLY_THRESHOLD = 7         # < 7 days: hourly aggregation
    DAILY_THRESHOLD = 30         # < 30 days: daily aggregation
    WEEKLY_THRESHOLD = 365       # < 365 days: weekly aggregation
    
    # Sampling rates
    SAMPLE_RATE_LARGE = 0.1      # 10% for very large datasets
    SAMPLE_RATE_MEDIUM = 0.5     # 50% for medium datasets
    
    # Record count thresholds
    LARGE_DATASET_THRESHOLD = 100000
    MEDIUM_DATASET_THRESHOLD = 10000


class DataOptimizer:
    """Data optimization utility for efficient data loading."""
    
    def __init__(self, sensor_repo: ISensorReadingRepository):
        """Initialize the data optimizer."""
        self.sensor_repo = sensor_repo
        self.strategy = OptimizationStrategy()
    
    def get_optimization_strategy(self, start_time: datetime, end_time: datetime, 
                                 estimated_records: Optional[int] = None) -> Dict[str, Any]:
        """Determine the best optimization strategy for the given time range."""
        time_delta = end_time - start_time
        days = time_delta.days
        
        strategy = {
            'use_sampling': False,
            'use_aggregation': False,
            'aggregation_interval': None,
            'sample_rate': 1.0,
            'progressive_loading': False,
            'max_records_per_batch': 10000,
            'explanation': ''
        }
        
        if days <= self.strategy.REAL_TIME_THRESHOLD:
            # Real-time data: use all data
            strategy['explanation'] = 'Real-time range: using all data'
            
        elif days <= self.strategy.HOURLY_THRESHOLD:
            # Short range: hourly aggregation
            strategy['use_aggregation'] = True
            strategy['aggregation_interval'] = 'hour'
            strategy['explanation'] = 'Short range: hourly aggregation'
            
        elif days <= self.strategy.DAILY_THRESHOLD:
            # Medium range: daily aggregation
            strategy['use_aggregation'] = True
            strategy['aggregation_interval'] = 'day'
            strategy['explanation'] = 'Medium range: daily aggregation'
            
        elif days <= self.strategy.WEEKLY_THRESHOLD:
            # Long range: weekly aggregation + sampling
            strategy['use_aggregation'] = True
            strategy['use_sampling'] = True
            strategy['aggregation_interval'] = 'week'
            strategy['sample_rate'] = self.strategy.SAMPLE_RATE_MEDIUM
            strategy['progressive_loading'] = True
            strategy['explanation'] = 'Long range: weekly aggregation + 50% sampling'
            
        else:
            # Very long range: monthly aggregation + heavy sampling
            strategy['use_aggregation'] = True
            strategy['use_sampling'] = True
            strategy['aggregation_interval'] = 'month'
            strategy['sample_rate'] = self.strategy.SAMPLE_RATE_LARGE
            strategy['progressive_loading'] = True
            strategy['explanation'] = 'Very long range: monthly aggregation + 10% sampling'
        
        # Adjust based on estimated record count
        if estimated_records:
            if estimated_records > self.strategy.LARGE_DATASET_THRESHOLD:
                strategy['use_sampling'] = True
                strategy['sample_rate'] = min(strategy['sample_rate'], self.strategy.SAMPLE_RATE_LARGE)
                strategy['progressive_loading'] = True
                strategy['explanation'] += f' (large dataset: {estimated_records:,} records)'
            elif estimated_records > self.strategy.MEDIUM_DATASET_THRESHOLD:
                strategy['use_sampling'] = True
                strategy['sample_rate'] = min(strategy['sample_rate'], self.strategy.SAMPLE_RATE_MEDIUM)
                strategy['explanation'] += f' (medium dataset: {estimated_records:,} records)'
        
        return strategy
    
    async def get_optimized_data(self, node_id: UUID, start_time: datetime, 
                               end_time: datetime, strategy: Optional[Dict[str, Any]] = None) -> Tuple[List[SensorReading], Dict[str, Any]]:
        """Get optimized data based on the optimization strategy."""
        
        if strategy is None:
            strategy = self.get_optimization_strategy(start_time, end_time)
        
        logger.info(f"Using optimization strategy: {strategy['explanation']}")
        
        # Get raw data
        raw_data = await self.sensor_repo.get_by_node_id(
            node_id=node_id,
            start_time=start_time,
            end_time=end_time
        )
        
        if not raw_data:
            return [], {'strategy': strategy, 'original_count': 0, 'optimized_count': 0}
        
        original_count = len(raw_data)
        optimized_data = raw_data
        
        # Apply sampling if needed
        if strategy['use_sampling'] and strategy['sample_rate'] < 1.0:
            sample_size = int(len(raw_data) * strategy['sample_rate'])
            if sample_size > 0:
                # Use systematic sampling to preserve time distribution
                step = len(raw_data) // sample_size
                if step > 1:
                    optimized_data = raw_data[::step]
                    logger.info(f"Applied sampling: {len(optimized_data)} records (from {original_count})")
        
        # Apply aggregation if needed
        if strategy['use_aggregation']:
            optimized_data = self._aggregate_data(optimized_data, strategy['aggregation_interval'])
            logger.info(f"Applied {strategy['aggregation_interval']} aggregation: {len(optimized_data)} records")
        
        optimization_info = {
            'strategy': strategy,
            'original_count': original_count,
            'optimized_count': len(optimized_data),
            'reduction_ratio': 1 - (len(optimized_data) / original_count) if original_count > 0 else 0
        }
        
        return optimized_data, optimization_info
    
    def _aggregate_data(self, data: List[SensorReading], interval: str) -> List[SensorReading]:
        """Aggregate sensor readings by time interval."""
        if not data:
            return []
        
        # Convert to DataFrame for easier aggregation
        df_data = []
        for reading in data:
            df_data.append({
                'timestamp': reading.timestamp,
                'node_id': reading.node_id,
                'flow_rate': reading.flow_rate.value if reading.flow_rate else None,
                'pressure': reading.pressure.value if reading.pressure else None,
                'temperature': reading.temperature.value if reading.temperature else None,
                'quality_score': reading.quality_score,
                'is_anomaly': reading.is_anomaly
            })
        
        df = pd.DataFrame(df_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Define aggregation rules
        agg_rules = {
            'flow_rate': 'mean',
            'pressure': 'mean', 
            'temperature': 'mean',
            'quality_score': 'mean',
            'is_anomaly': 'max'  # If any reading in the interval is anomalous
        }
        
        # Determine resampling frequency
        freq_map = {
            'hour': 'H',
            'day': 'D',
            'week': 'W',
            'month': 'M'
        }
        
        freq = freq_map.get(interval, 'H')
        
        # Resample and aggregate
        aggregated = df.resample(freq).agg(agg_rules).dropna()
        
        # Convert back to SensorReading objects
        aggregated_readings = []
        for timestamp, row in aggregated.iterrows():
            from src.domain.value_objects.measurement import Measurement
            
            reading = SensorReading(
                id=UUID('00000000-0000-0000-0000-000000000000'),  # Dummy ID for aggregated data
                node_id=data[0].node_id,  # Use the first reading's node_id
                timestamp=timestamp.to_pydatetime(),
                flow_rate=Measurement(value=row['flow_rate'], unit='L/min') if pd.notna(row['flow_rate']) else None,
                pressure=Measurement(value=row['pressure'], unit='bar') if pd.notna(row['pressure']) else None,
                temperature=Measurement(value=row['temperature'], unit='°C') if pd.notna(row['temperature']) else None,
                quality_score=row['quality_score'] if pd.notna(row['quality_score']) else None,
                is_anomaly=bool(row['is_anomaly']) if pd.notna(row['is_anomaly']) else False
            )
            aggregated_readings.append(reading)
        
        return aggregated_readings
    
    async def get_data_size_estimate(self, node_id: UUID, start_time: datetime, 
                                   end_time: datetime) -> int:
        """Estimate the number of records for a given time range."""
        # Simple estimation based on time range
        # In a real implementation, you might query metadata tables
        time_delta = end_time - start_time
        hours = time_delta.total_seconds() / 3600
        
        # Rough estimate: 1 reading per 5 minutes = 12 readings per hour
        estimated_records = int(hours * 12)
        
        return estimated_records
    
    def get_performance_recommendations(self, time_range_days: int, 
                                      estimated_records: int) -> List[str]:
        """Get performance recommendations for the given parameters."""
        recommendations = []
        
        if time_range_days > 365:
            recommendations.append(
                "⚠️ Very long time range (>1 year). Consider using summary views or reports instead."
            )
        elif time_range_days > 30:
            recommendations.append(
                "📊 Long time range detected. Data will be aggregated to improve performance."
            )
        
        if estimated_records > self.strategy.LARGE_DATASET_THRESHOLD:
            recommendations.append(
                f"📈 Large dataset ({estimated_records:,} estimated records). Sampling will be applied."
            )
        
        if time_range_days > 7:
            recommendations.append(
                "🔄 Consider using cached summaries for frequently accessed long-term data."
            )
        
        return recommendations


# Utility functions for Streamlit integration
def get_optimized_data_for_streamlit(sensor_repo: ISensorReadingRepository, 
                                   node_id: UUID, start_time: datetime, 
                                   end_time: datetime) -> Tuple[List[SensorReading], Dict[str, Any]]:
    """Synchronous wrapper for Streamlit integration."""
    optimizer = DataOptimizer(sensor_repo)
    
    # Run async function in event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            optimizer.get_optimized_data(node_id, start_time, end_time)
        )
        return result
    finally:
        loop.close()


def show_optimization_info(optimization_info: Dict[str, Any]) -> None:
    """Display optimization information in Streamlit."""
    import streamlit as st
    
    strategy = optimization_info['strategy']
    original_count = optimization_info['original_count']
    optimized_count = optimization_info['optimized_count']
    reduction_ratio = optimization_info['reduction_ratio']
    
    if reduction_ratio > 0:
        st.info(
            f"🚀 **Data Optimization Applied**: {strategy['explanation']}\n\n"
            f"📊 **Records**: {original_count:,} → {optimized_count:,} "
            f"({reduction_ratio:.1%} reduction)\n\n"
            f"⚡ **Performance**: Loading time significantly reduced"
        )
    else:
        st.info(f"📊 **Strategy**: {strategy['explanation']}") 