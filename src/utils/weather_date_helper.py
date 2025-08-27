"""
Weather date helper utilities.
Handles date adjustments for weather data queries.
"""

from datetime import datetime, date, timedelta
from typing import Tuple, Optional
import asyncpg


async def get_available_date_range(conn: asyncpg.Connection) -> Tuple[date, date]:
    """
    Get the available date range from the weather data.
    
    Returns:
        Tuple of (min_date, max_date) available in the database
    """
    result = await conn.fetchrow("""
        SELECT MIN(date) as min_date, MAX(date) as max_date
        FROM water_infrastructure.weather_data
        WHERE location = 'Selargius'
    """)
    
    return result['min_date'], result['max_date']


async def adjust_date_range_to_available(
    conn: asyncpg.Connection,
    requested_start: date,
    requested_end: date
) -> Tuple[date, date]:
    """
    Adjust requested date range to fit within available data.
    
    If requested dates are beyond available data, adjust them to the 
    nearest available period while maintaining the same duration.
    
    Args:
        conn: Database connection
        requested_start: Requested start date
        requested_end: Requested end date
        
    Returns:
        Tuple of (adjusted_start, adjusted_end)
    """
    min_date, max_date = await get_available_date_range(conn)
    
    # If no data available, return requested dates
    if not min_date or not max_date:
        return requested_start, requested_end
    
    # Calculate requested duration
    requested_duration = (requested_end - requested_start).days
    
    # If requested end date is after max available date
    if requested_end > max_date:
        # Shift the range to end at max_date
        adjusted_end = max_date
        adjusted_start = max_date - timedelta(days=requested_duration)
        
        # Ensure start date is not before min_date
        if adjusted_start < min_date:
            adjusted_start = min_date
            
        return adjusted_start, adjusted_end
    
    # If requested start date is before min available date
    if requested_start < min_date:
        adjusted_start = min_date
        adjusted_end = min_date + timedelta(days=requested_duration)
        
        # Ensure end date is not after max_date
        if adjusted_end > max_date:
            adjusted_end = max_date
            
        return adjusted_start, adjusted_end
    
    # If dates are within range, return as is
    return requested_start, requested_end


def get_default_date_range_for_interval(
    interval: str,
    base_date: Optional[date] = None
) -> Tuple[date, date]:
    """
    Get default date range based on interval type.
    
    Args:
        interval: 'week', 'month', 'year'
        base_date: Base date to calculate from (defaults to Dec 31, 2024)
        
    Returns:
        Tuple of (start_date, end_date)
    """
    # Default to Dec 31, 2024 (last date in our data)
    if base_date is None:
        base_date = date(2024, 12, 31)
    
    if interval == 'week':
        end_date = base_date
        start_date = end_date - timedelta(days=7)
    elif interval == 'month':
        # Last complete month
        if base_date.day == 31:
            end_date = base_date
            start_date = date(base_date.year, base_date.month, 1)
        else:
            # Go to previous month
            if base_date.month == 1:
                end_date = date(base_date.year - 1, 12, 31)
                start_date = date(base_date.year - 1, 12, 1)
            else:
                import calendar
                prev_month = base_date.month - 1
                last_day = calendar.monthrange(base_date.year, prev_month)[1]
                end_date = date(base_date.year, prev_month, last_day)
                start_date = date(base_date.year, prev_month, 1)
    elif interval == 'year':
        # Last complete year
        end_date = date(2024, 12, 31)
        start_date = date(2024, 1, 1)
    else:
        # Default to last 30 days
        end_date = base_date
        start_date = end_date - timedelta(days=30)
    
    return start_date, end_date
