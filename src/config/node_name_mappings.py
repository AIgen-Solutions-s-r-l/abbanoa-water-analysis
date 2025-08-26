"""
Node name mappings for consistent naming across the system.

This module provides mappings between various node naming conventions:
- Italian/specific node names (used in data sources)
- Generic node names (used in Enhanced Overview)
- Node IDs (used in APIs and database)
"""

from typing import Dict, Optional

# Mapping: Specific names to generic names
SPECIFIC_TO_GENERIC_NODES: Dict[str, str] = {
    # Original nodes with Italian names
    "sant'anna": "Central Node A",
    "santanna": "Central Node A",
    "sant anna": "Central Node A",
    "selargius nodo via sant anna": "Central Node A",
    
    "seneca": "Central Node B",
    "selargius nodo via seneca": "Central Node B",
    
    "selargius tank": "Central Tank",
    "selargius serbatoio": "Central Tank",
    "serbatoio selargius": "Central Tank",
    
    "quartucciu tank": "Industrial Tank",
    "quartucciu serbatoio": "Industrial Tank",
    
    # Distribution nodes
    "distribution 215542": "Distribution Node 1",
    "selargius distribution 215542": "Distribution Node 1",
    
    "distribution 215600": "Distribution Node 2", 
    "selargius distribution 215600": "Distribution Node 2",
    
    "distribution 273933": "Distribution Node 3",
    "selargius distribution 273933": "Distribution Node 3",
    
    # Monitoring nodes
    "monitoring 281492": "Monitoring Point 1",
    "selargius monitoring 281492": "Monitoring Point 1",
    
    "monitoring 288399": "Monitoring Point 2",
    "selargius monitoring 288399": "Monitoring Point 2",
    
    "monitoring 288400": "Monitoring Point 3",
    "selargius monitoring 288400": "Monitoring Point 3",
    
    # Other nodes
    "external supply": "External Supply",
    "q_monserrato": "District Interconnection 4",
    "q.monserrato": "District Interconnection 4",
    "monserrato": "District Interconnection 4",
}

# UUID mappings for anomaly detection
UUID_TO_GENERIC_NODES: Dict[str, str] = {
    "00000000-0000-0000-0000-000000000001": "Central Node A",
    "00000000-0000-0000-0000-000000000002": "Central Node B",
    "00000000-0000-0000-0000-000000000003": "Central Tank",
    "00000000-0000-0000-0000-000000000004": "Industrial Tank",
}

# Node ID mappings
NODE_ID_TO_GENERIC: Dict[str, str] = {
    "NODE_001": "Central Node A",
    "NODE_002": "Central Node B", 
    "NODE_003": "Central Tank",
    "NODE_004": "Industrial Tank",
    "NODE_005": "Distribution Node 1",
    "NODE_006": "Distribution Node 2",
    "NODE_007": "Distribution Node 3",
    "NODE_008": "Monitoring Point 1",
    "NODE_009": "Monitoring Point 2",
    "NODE_010": "Monitoring Point 3",
    "DIST_001": "Central Distribution Hub",
    "node-santanna": "Central Node A",
    "node-seneca": "Central Node B",
    "node-serbatoio": "Central Tank",
}


def get_generic_node_name(node_reference: str) -> str:
    """
    Get generic node name from any node reference.
    
    Args:
        node_reference: Node reference (specific name, UUID, node ID)
        
    Returns:
        Generic node name or original reference if not found
    """
    # Normalize the reference
    normalized = node_reference.lower().strip()
    
    # Check specific name mapping
    if normalized in SPECIFIC_TO_GENERIC_NODES:
        return SPECIFIC_TO_GENERIC_NODES[normalized]
    
    # Check UUID mapping
    if node_reference in UUID_TO_GENERIC_NODES:
        return UUID_TO_GENERIC_NODES[node_reference]
    
    # Check node ID mapping
    if node_reference in NODE_ID_TO_GENERIC:
        return NODE_ID_TO_GENERIC[node_reference]
    
    # Return original if no mapping found
    return node_reference


def normalize_node_list(nodes: list) -> list:
    """
    Normalize a list of node references to generic names.
    
    Args:
        nodes: List of node references in any format
        
    Returns:
        List of normalized generic node names
    """
    return [get_generic_node_name(node) for node in nodes]


# Export commonly used generic node names
CENTRAL_DISTRICT_NODES = ["Central Node A", "Central Node B", "Central Tank"]
DISTRIBUTION_NODES = ["Distribution Node 1", "Distribution Node 2", "Distribution Node 3"]
MONITORING_NODES = ["Monitoring Point 1", "Monitoring Point 2", "Monitoring Point 3"]
ALL_GENERIC_NODE_NAMES = (
    CENTRAL_DISTRICT_NODES + 
    DISTRIBUTION_NODES + 
    MONITORING_NODES + 
    ["External Supply", "Industrial Tank"]
)
