"""
Centralized node configuration for the water infrastructure system.

This file contains all node definitions and mappings to avoid duplication
across different components.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class NodeConfig:
    """Configuration for a monitoring node."""

    node_id: str
    uuid: str
    bigquery_id: str
    display_name: str
    full_name: str
    node_type: str
    district: str
    latitude: float
    longitude: float
    is_active: bool = True
    installation_date: datetime = datetime(2024, 1, 1)


# Original nodes
ORIGINAL_NODES = {
    "sant_anna": NodeConfig(
        node_id="001",
        uuid="00000000-0000-0000-0000-000000000001",
        bigquery_id="node-santanna",
        display_name="Sant'Anna",
        full_name="SELARGIUS NODO VIA SANT ANNA",
        node_type="distribution",
        district="Selargius",
        latitude=39.2547,
        longitude=9.1642,
    ),
    "seneca": NodeConfig(
        node_id="002",
        uuid="00000000-0000-0000-0000-000000000002",
        bigquery_id="node-seneca",
        display_name="Seneca",
        full_name="SELARGIUS NODO VIA SENECA",
        node_type="distribution",
        district="Selargius",
        latitude=39.2456,
        longitude=9.1523,
    ),
    "selargius_tank": NodeConfig(
        node_id="003",
        uuid="00000000-0000-0000-0000-000000000003",
        bigquery_id="node-serbatoio",
        display_name="Selargius Tank",
        full_name="SELARGIUS SERBATOIO",
        node_type="storage",
        district="Selargius",
        latitude=39.2501,
        longitude=9.1589,
    ),
}

# New nodes from backup data
NEW_NODES = {
    "node_215542": NodeConfig(
        node_id="215542",
        uuid="00000000-0000-0000-0000-000000215542",
        bigquery_id="node-215542",
        display_name="Distribution 215542",
        full_name="Selargius Distribution 215542",
        node_type="distribution",
        district="Selargius",
        latitude=39.2238,
        longitude=9.1422,
    ),
    "node_215600": NodeConfig(
        node_id="215600",
        uuid="00000000-0000-0000-0000-000000215600",
        bigquery_id="node-215600",
        display_name="Distribution 215600",
        full_name="Selargius Distribution 215600",
        node_type="distribution",
        district="Selargius",
        latitude=39.2238,
        longitude=9.1422,
    ),
    "node_273933": NodeConfig(
        node_id="273933",
        uuid="00000000-0000-0000-0000-000000273933",
        bigquery_id="node-273933",
        display_name="Distribution 273933",
        full_name="Selargius Distribution 273933",
        node_type="distribution",
        district="Selargius",
        latitude=39.2238,
        longitude=9.1422,
    ),
    "node_281492": NodeConfig(
        node_id="281492",
        uuid="00000000-0000-0000-0000-000000281492",
        bigquery_id="node-281492",
        display_name="Monitoring 281492",
        full_name="Selargius Monitoring 281492",
        node_type="monitoring",
        district="Selargius",
        latitude=39.2238,
        longitude=9.1422,
    ),
    "node_288399": NodeConfig(
        node_id="288399",
        uuid="00000000-0000-0000-0000-000000288399",
        bigquery_id="node-288399",
        display_name="Monitoring 288399",
        full_name="Selargius Monitoring 288399",
        node_type="monitoring",
        district="Selargius",
        latitude=39.2238,
        longitude=9.1422,
    ),
    "node_288400": NodeConfig(
        node_id="288400",
        uuid="00000000-0000-0000-0000-000000288400",
        bigquery_id="node-288400",
        display_name="Monitoring 288400",
        full_name="Selargius Monitoring 288400",
        node_type="monitoring",
        district="Selargius",
        latitude=39.2238,
        longitude=9.1422,
    ),
}

# Combined node configuration
ALL_NODES = {**ORIGINAL_NODES, **NEW_NODES}

# Mapping helpers
UUID_TO_NODE = {node.uuid: node for node in ALL_NODES.values()}
BIGQUERY_ID_TO_NODE = {node.bigquery_id: node for node in ALL_NODES.values()}
DISPLAY_NAME_TO_UUID = {node.display_name: node.uuid for node in ALL_NODES.values()}

# Node groupings
DISTRIBUTION_NODES = [
    node for node in ALL_NODES.values() if node.node_type == "distribution"
]
MONITORING_NODES = [
    node for node in ALL_NODES.values() if node.node_type == "monitoring"
]
STORAGE_NODES = [node for node in ALL_NODES.values() if node.node_type == "storage"]

# Districts
DISTRICTS = list(set(node.district for node in ALL_NODES.values()))

# Valid IDs for API validation
VALID_NODE_IDS = [node.bigquery_id for node in ALL_NODES.values()]
VALID_DISTRICT_IDS = [f"DIST_{i:03d}" for i in range(1, len(DISTRICTS) + 1)]
