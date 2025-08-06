"""
Updated node configuration based on volume analysis.
Generated: 2025-08-06T17:55:01.572212
"""

from typing import Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class NodeConfig:
    """Configuration for a monitoring node."""
    node_id: str
    display_name: str
    node_type: str
    category: str
    max_volume_m3: float
    
# Node configurations based on volume analysis
VOLUME_BASED_NODES = {
    "TANK01": NodeConfig(
        node_id="tank01",
        display_name="TANK01",
        node_type="tank",
        category="Tank",
        max_volume_m3=11077575
    ),
    "NODE01": NodeConfig(
        node_id="node01",
        display_name="NODE01",
        node_type="distribution",
        category="Distribution",
        max_volume_m3=1925967
    ),
    "MONITOR01": NodeConfig(
        node_id="monitor01",
        display_name="MONITOR01",
        node_type="monitoring",
        category="Monitoring",
        max_volume_m3=5219552
    ),
    "MONITOR02": NodeConfig(
        node_id="monitor02",
        display_name="MONITOR02",
        node_type="monitoring",
        category="Monitoring",
        max_volume_m3=165619
    ),
}
