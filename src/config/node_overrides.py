"""
Node configuration overrides for new backup data nodes.

This file provides a simple way to extend the existing node configuration
without modifying all the existing files.
"""

# New node configurations that can be imported and used
NEW_BACKUP_NODES = {
    "215542": {
        "node_id": "215542",
        "name": "Distribution 215542",
        "type": "distribution",
        "district": "Selargius",
        "bigquery_table": "sensor_readings_ml",
    },
    "215600": {
        "node_id": "215600",
        "name": "Distribution 215600",
        "type": "distribution",
        "district": "Selargius",
        "bigquery_table": "sensor_readings_ml",
    },
    "273933": {
        "node_id": "273933",
        "name": "Distribution 273933",
        "type": "distribution",
        "district": "Selargius",
        "bigquery_table": "sensor_readings_ml",
    },
    "281492": {
        "node_id": "281492",
        "name": "Monitoring 281492",
        "type": "monitoring",
        "district": "Selargius",
        "bigquery_table": "sensor_readings_ml",
    },
    "288399": {
        "node_id": "288399",
        "name": "Monitoring 288399",
        "type": "monitoring",
        "district": "Selargius",
        "bigquery_table": "sensor_readings_ml",
    },
    "288400": {
        "node_id": "288400",
        "name": "Monitoring 288400",
        "type": "monitoring",
        "district": "Selargius",
        "bigquery_table": "sensor_readings_ml",
    },
}


def get_all_node_names():
    """Get all node names including new ones."""
    original_nodes = ["Sant'Anna", "Seneca", "Selargius Tank", "External Supply"]
    new_nodes = [node["name"] for node in NEW_BACKUP_NODES.values()]
    return original_nodes + new_nodes


def get_node_config(node_name):
    """Get configuration for a specific node."""
    # Check new nodes first
    for node_id, config in NEW_BACKUP_NODES.items():
        if config["name"] == node_name:
            return config
    return None
