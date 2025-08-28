"""
Weather Location Mapping Configuration
Maps actual weather data sources to display names.
"""

from typing import Dict, Optional

# Mapping of actual location names (in database) to display names
LOCATION_DISPLAY_MAPPING: Dict[str, str] = {
    "Selargius": "Roccavina",
    # Other locations are filtered out
}

# Reverse mapping for API queries
DISPLAY_TO_ACTUAL_MAPPING: Dict[str, str] = {
    "Roccavina": "Selargius",
}

# Locations that should be filtered out from results
HIDDEN_LOCATIONS = {"Maccarese", "Cagliari"}


def get_display_name(actual_location: str) -> Optional[str]:
    """
    Get the display name for a location.
    Returns None if the location should be hidden.
    """
    if actual_location in HIDDEN_LOCATIONS:
        return None
    return LOCATION_DISPLAY_MAPPING.get(actual_location, actual_location)


def get_actual_location(display_name: str) -> str:
    """
    Get the actual location name from a display name.
    """
    return DISPLAY_TO_ACTUAL_MAPPING.get(display_name, display_name)


def transform_weather_data(weather_data: Dict) -> Optional[Dict]:
    """
    Transform weather data with location mapping.
    Returns None if the location should be hidden.
    """
    if not weather_data:
        return None
    
    actual_location = weather_data.get("location", "")
    display_name = get_display_name(actual_location)
    
    if display_name is None:
        return None
    
    # Create a copy and update the location name
    transformed_data = weather_data.copy()
    transformed_data["location"] = display_name
    return transformed_data
