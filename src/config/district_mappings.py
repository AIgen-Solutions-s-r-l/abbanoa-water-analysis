"""
District name mappings for consistent naming across the system.

This module provides mappings between various district naming conventions:
- Italian place names (used in data sources)
- Generic district names (used in Enhanced Overview)
- District IDs (used in APIs and database)
"""

from typing import Dict, Optional

# Primary mapping: District ID to generic name
DISTRICT_NAMES: Dict[str, str] = {
    "DIST_001": "Central Business District",
    "DIST_002": "Residential North",
    "DIST_003": "Industrial South",
    "DIST_004": "Suburban East",
    "DIST_005": "Coastal West"
}

# Mapping: Italian place names to district IDs
PLACE_TO_DISTRICT: Dict[str, str] = {
    # Selargius area
    "selargius": "DIST_001",
    "selargius_distribution": "DIST_001",
    "selargius distribution": "DIST_001",
    
    # Cagliari area
    "cagliari": "DIST_002",
    "cagliari_centro": "DIST_002",
    "cagliari centro": "DIST_002",
    
    # Quartu area
    "quartu": "DIST_003",
    "quartu_santelena": "DIST_003",
    "quartu sant'elena": "DIST_003",
    "quartucciu": "DIST_003",
    
    # Monserrato area
    "monserrato": "DIST_004",
    "monserrato_residential": "DIST_004",
    "monserrato residential": "DIST_004",
    
    # Coastal area
    "coastal": "DIST_005",
    "marina": "DIST_005",
    "porto": "DIST_005"
}

# Reverse mapping: District ID to Italian place name (for legacy compatibility)
DISTRICT_TO_PLACE: Dict[str, str] = {
    "DIST_001": "Selargius",
    "DIST_002": "Cagliari",
    "DIST_003": "Quartu",
    "DIST_004": "Monserrato",
    "DIST_005": "Coastal"
}


def get_district_id(place_name: str) -> Optional[str]:
    """
    Get district ID from Italian place name.
    
    Args:
        place_name: Italian place name (case-insensitive)
        
    Returns:
        District ID or None if not found
    """
    normalized_name = place_name.lower().strip()
    return PLACE_TO_DISTRICT.get(normalized_name)


def get_generic_district_name(identifier: str) -> str:
    """
    Get generic district name from either district ID or Italian place name.
    
    Args:
        identifier: District ID (DIST_XXX) or Italian place name
        
    Returns:
        Generic district name or original identifier if not found
    """
    # First check if it's already a district ID
    if identifier in DISTRICT_NAMES:
        return DISTRICT_NAMES[identifier]
    
    # Try to get district ID from place name
    district_id = get_district_id(identifier)
    if district_id:
        return DISTRICT_NAMES.get(district_id, identifier)
    
    # Return original if no mapping found
    return identifier


def get_italian_place_name(district_id: str) -> Optional[str]:
    """
    Get Italian place name from district ID (for legacy compatibility).
    
    Args:
        district_id: District ID (DIST_XXX)
        
    Returns:
        Italian place name or None if not found
    """
    return DISTRICT_TO_PLACE.get(district_id)


def normalize_district_reference(reference: str) -> str:
    """
    Normalize any district reference to the standard generic name.
    
    This function handles:
    - District IDs (DIST_XXX)
    - Italian place names
    - Already normalized generic names
    
    Args:
        reference: Any form of district reference
        
    Returns:
        Normalized generic district name
    """
    # Check if it's already a generic name
    if reference in DISTRICT_NAMES.values():
        return reference
    
    # Otherwise, try to convert
    return get_generic_district_name(reference)


# Export all district IDs for easy access
ALL_DISTRICT_IDS = list(DISTRICT_NAMES.keys())

# Export all generic names for UI dropdowns
ALL_GENERIC_NAMES = list(DISTRICT_NAMES.values())
