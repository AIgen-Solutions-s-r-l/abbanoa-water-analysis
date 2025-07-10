"""
Centralized node mappings for the Streamlit dashboard.

This module provides mappings between display names and node IDs
for both original and new sensor nodes.
"""

from uuid import UUID
from typing import Dict, List

# Original nodes mapping
ORIGINAL_NODES = {
    "Sant'Anna": UUID("00000000-0000-0000-0000-000000000001"),
    "Seneca": UUID("00000000-0000-0000-0000-000000000002"),
    "Selargius Tank": UUID("00000000-0000-0000-0000-000000000003"),
}

# New backup data nodes mapping
NEW_NODES = {
    "Distribution 215542": "215542",
    "Distribution 215600": "215600",
    "Distribution 273933": "273933",
    "Monitoring 281492": "281492",
    "Monitoring 288399": "288399",
    "Monitoring 288400": "288400",
}

# Combined mapping for all nodes
ALL_NODE_MAPPINGS = {
    **{k: str(v) for k, v in ORIGINAL_NODES.items()},
    **NEW_NODES
}

# Node type categorization
NODE_CATEGORIES = {
    "Original Nodes": ["Sant'Anna", "Seneca", "Selargius Tank", "External Supply"],
    "Distribution Nodes": ["Distribution 215542", "Distribution 215600", "Distribution 273933"],
    "Monitoring Nodes": ["Monitoring 281492", "Monitoring 288399", "Monitoring 288400"],
}

def get_node_id(display_name: str) -> str:
    """Get node ID from display name."""
    if display_name in ALL_NODE_MAPPINGS:
        return ALL_NODE_MAPPINGS[display_name]
    elif display_name == "External Supply":
        # Special case for external supply
        return "external-supply"
    return None

def get_node_ids_from_selection(selected_nodes: List[str]) -> List[str]:
    """Convert display names to node IDs."""
    if "All Nodes" in selected_nodes:
        return list(ALL_NODE_MAPPINGS.values())
    
    node_ids = []
    for node in selected_nodes:
        if node.startswith("---"):  # Skip category headers
            continue
        node_id = get_node_id(node)
        if node_id:
            node_ids.append(node_id)
    
    return node_ids

def get_node_display_name(node_id: str) -> str:
    """Get display name from node ID."""
    # Reverse lookup
    for display_name, mapped_id in ALL_NODE_MAPPINGS.items():
        if mapped_id == node_id:
            return display_name
    
    # Check if it's a new node ID
    for display_name, mapped_id in NEW_NODES.items():
        if mapped_id == node_id:
            return display_name
            
    return f"Node {node_id}"