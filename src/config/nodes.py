"""
Centralized node configuration for the water infrastructure system.

This file contains all node definitions and mappings to avoid duplication
across different components.
"""

from typing import Dict, List
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
        longitude=9.1642
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
        longitude=9.1523
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
        longitude=9.1589
    )
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
        longitude=9.1422
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
        longitude=9.1422
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
        longitude=9.1422
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
        longitude=9.1422
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
        longitude=9.1422
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
        longitude=9.1422
    ),
}

# Volume-based renamed nodes
RENAMED_NODES = {
    "tank01": NodeConfig(
        node_id="CENTRO_SUD",
        uuid="00000000-0000-0000-0000-000000000004",
        bigquery_id="node-tank01",
        display_name="TANK01",
        full_name="Storage Tank 01 (11M m³)",
        node_type="storage",
        district="Selargius",
        latitude=39.2501,
        longitude=9.1589
    ),
    "node01": NodeConfig(
        node_id="CENTRO_EST",
        uuid="00000000-0000-0000-0000-000000000005",
        bigquery_id="node-node01",
        display_name="NODE01",
        full_name="Distribution Node 01 (1.9M m³)",
        node_type="distribution",
        district="Selargius",
        latitude=39.2547,
        longitude=9.1642
    ),
    "monitor01": NodeConfig(
        node_id="CENTRO_OVEST",
        uuid="00000000-0000-0000-0000-000000000006",
        bigquery_id="node-monitor01",
        display_name="MONITOR01",
        full_name="Monitoring Point 01 (5.2M m³)",
        node_type="monitoring",
        district="Selargius",
        latitude=39.2456,
        longitude=9.1523
    ),
    "monitor02": NodeConfig(
        node_id="CENTRO_NORD",
        uuid="00000000-0000-0000-0000-000000000007",
        bigquery_id="node-monitor02",
        display_name="MONITOR02",
        full_name="Monitoring Point 02 (165K m³)",
        node_type="monitoring",
        district="Selargius",
        latitude=39.2238,
        longitude=9.1422
    )
}

# Interconnection nodes
INTERCONNECTION_NODES = {
    "intercon01": NodeConfig(
        node_id="FIORI",
        uuid="00000000-0000-0000-0000-000000000008",
        bigquery_id="node-intercon01",
        display_name="INTERCON01",
        full_name="Interconnection Point 01 (Fiori)",
        node_type="interconnection",
        district="Selargius",
        latitude=39.2400,
        longitude=9.1500
    ),
    "intercon02": NodeConfig(
        node_id="Q_GALLUS",
        uuid="00000000-0000-0000-0000-000000000009",
        bigquery_id="node-intercon02",
        display_name="INTERCON02",
        full_name="Interconnection Point 02 (Q.Gallus)",
        node_type="interconnection",
        district="Selargius",
        latitude=39.2410,
        longitude=9.1510
    ),
    "intercon03": NodeConfig(
        node_id="Q_MATTEOTTI",
        uuid="00000000-0000-0000-0000-000000000010",
        bigquery_id="node-intercon03",
        display_name="INTERCON03",
        full_name="Interconnection Point 03 (Q.Matteotti)",
        node_type="interconnection",
        district="Selargius",
        latitude=39.2420,
        longitude=9.1520
    ),
    "intercon04": NodeConfig(
        node_id="Q_MONSERRATO",
        uuid="00000000-0000-0000-0000-000000000011",
        bigquery_id="node-intercon04",
        display_name="INTERCON04",
        full_name="Interconnection Point 04 (Q.Monserrato)",
        node_type="interconnection",
        district="Selargius",
        latitude=39.2430,
        longitude=9.1530
    ),
    "intercon05": NodeConfig(
        node_id="Q_NENNI_SUD",
        uuid="00000000-0000-0000-0000-000000000012",
        bigquery_id="node-intercon05",
        display_name="INTERCON05",
        full_name="Interconnection Point 05 (Q.Nenni Sud)",
        node_type="interconnection",
        district="Selargius",
        latitude=39.2440,
        longitude=9.1540
    ),
    "intercon06": NodeConfig(
        node_id="Q_SANTANNA",
        uuid="00000000-0000-0000-0000-000000000013",
        bigquery_id="node-intercon06",
        display_name="INTERCON06",
        full_name="Interconnection Point 06 (Q.Sant'Anna)",
        node_type="interconnection",
        district="Selargius",
        latitude=39.2450,
        longitude=9.1550
    ),
    "intercon07": NodeConfig(
        node_id="Q_SARDEGNA",
        uuid="00000000-0000-0000-0000-000000000014",
        bigquery_id="node-intercon07",
        display_name="INTERCON07",
        full_name="Interconnection Point 07 (Q.Sardegna)",
        node_type="interconnection",
        district="Selargius",
        latitude=39.2460,
        longitude=9.1560
    ),
    "intercon08": NodeConfig(
        node_id="Q_TRIESTE",
        uuid="00000000-0000-0000-0000-000000000015",
        bigquery_id="node-intercon08",
        display_name="INTERCON08",
        full_name="Interconnection Point 08 (Q.Trieste)",
        node_type="interconnection",
        district="Selargius",
        latitude=39.2470,
        longitude=9.1570
    )
}

# Zone meter nodes
ZONE_METER_NODES = {
    "zone01": NodeConfig(
        node_id="LIBERTA",
        uuid="00000000-0000-0000-0000-000000000016",
        bigquery_id="node-zone01",
        display_name="ZONE01",
        full_name="Zone Meter 01 (Libertà)",
        node_type="zone_meter",
        district="Selargius",
        latitude=39.2480,
        longitude=9.1580
    ),
    "zone02": NodeConfig(
        node_id="STADIO",
        uuid="00000000-0000-0000-0000-000000000017",
        bigquery_id="node-zone02",
        display_name="ZONE02",
        full_name="Zone Meter 02 (Stadio)",
        node_type="zone_meter",
        district="Selargius",
        latitude=39.2490,
        longitude=9.1590
    )
}

# Combined node configuration
ALL_NODES = {**ORIGINAL_NODES, **NEW_NODES, **RENAMED_NODES, **INTERCONNECTION_NODES, **ZONE_METER_NODES}

# Mapping helpers
UUID_TO_NODE = {node.uuid: node for node in ALL_NODES.values()}
BIGQUERY_ID_TO_NODE = {node.bigquery_id: node for node in ALL_NODES.values()}
DISPLAY_NAME_TO_UUID = {node.display_name: node.uuid for node in ALL_NODES.values()}

# Node groupings
DISTRIBUTION_NODES = [node for node in ALL_NODES.values() if node.node_type == "distribution"]
MONITORING_NODES = [node for node in ALL_NODES.values() if node.node_type == "monitoring"]
STORAGE_NODES = [node for node in ALL_NODES.values() if node.node_type == "storage"]
INTERCONNECTION_POINTS = [node for node in ALL_NODES.values() if node.node_type == "interconnection"]
ZONE_METERS = [node for node in ALL_NODES.values() if node.node_type == "zone_meter"]

# Districts
DISTRICTS = list(set(node.district for node in ALL_NODES.values()))

# Valid IDs for API validation
VALID_NODE_IDS = [node.bigquery_id for node in ALL_NODES.values()]
VALID_DISTRICT_IDS = [f"DIST_{i:03d}" for i in range(1, len(DISTRICTS) + 1)]
