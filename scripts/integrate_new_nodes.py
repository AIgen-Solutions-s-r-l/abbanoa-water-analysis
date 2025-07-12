#!/usr/bin/env python3
"""
Integrate new sensor nodes from backup data into the dashboard.

This script updates all necessary configuration files and repositories
to include the 6 new nodes from the backup data processing.
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# New nodes to add (from backup data)
NEW_NODES = {
    "215542": {
        "name": "Selargius Distribution 215542",
        "display_name": "Distribution 215542",
        "type": "distribution",
        "district": "Selargius",
        "uuid": "00000000-0000-0000-0000-000000215542",
        "bigquery_id": "node-215542",
        "location": {"lat": 39.2238, "lon": 9.1422},
    },
    "215600": {
        "name": "Selargius Distribution 215600",
        "display_name": "Distribution 215600",
        "type": "distribution",
        "district": "Selargius",
        "uuid": "00000000-0000-0000-0000-000000215600",
        "bigquery_id": "node-215600",
        "location": {"lat": 39.2238, "lon": 9.1422},
    },
    "273933": {
        "name": "Selargius Distribution 273933",
        "display_name": "Distribution 273933",
        "type": "distribution",
        "district": "Selargius",
        "uuid": "00000000-0000-0000-0000-000000273933",
        "bigquery_id": "node-273933",
        "location": {"lat": 39.2238, "lon": 9.1422},
    },
    "281492": {
        "name": "Selargius Monitoring 281492",
        "display_name": "Monitoring 281492",
        "type": "monitoring",
        "district": "Selargius",
        "uuid": "00000000-0000-0000-0000-000000281492",
        "bigquery_id": "node-281492",
        "location": {"lat": 39.2238, "lon": 9.1422},
    },
    "288399": {
        "name": "Selargius Monitoring 288399",
        "display_name": "Monitoring 288399",
        "type": "monitoring",
        "district": "Selargius",
        "uuid": "00000000-0000-0000-0000-000000288399",
        "bigquery_id": "node-288399",
        "location": {"lat": 39.2238, "lon": 9.1422},
    },
    "288400": {
        "name": "Selargius Monitoring 288400",
        "display_name": "Monitoring 288400",
        "type": "monitoring",
        "district": "Selargius",
        "uuid": "00000000-0000-0000-0000-000000288400",
        "bigquery_id": "node-288400",
        "location": {"lat": 39.2238, "lon": 9.1422},
    },
}


class DashboardIntegrator:
    """Integrates new nodes into the dashboard configuration."""

    def __init__(self):
        self.updates_made = []
        self.backup_files = []

    def backup_file(self, file_path: Path):
        """Create a backup of the file before modifying."""
        backup_path = file_path.with_suffix(file_path.suffix + ".backup")
        content = file_path.read_text()
        backup_path.write_text(content)
        self.backup_files.append((file_path, backup_path))

    def update_static_repository(self):
        """Update the static monitoring node repository."""
        print("\n1. Updating Static Repository...")

        file_path = (
            project_root
            / "src/infrastructure/repositories/static_monitoring_node_repository.py"
        )
        self.backup_file(file_path)

        content = file_path.read_text()

        # Find the _nodes list
        nodes_start = content.find("self._nodes = [")
        nodes_end = content.find("]", nodes_start) + 1

        if nodes_start == -1:
            print("❌ Could not find _nodes list in static repository")
            return

        # Generate new node entries
        new_node_entries = []
        for node_id, info in NEW_NODES.items():
            node_entry = """            MonitoringNode(
                id=UUID("{info['uuid']}"),
                name="{info['name']}",
                location=NodeLocation(
                    latitude={info['location']['lat']},
                    longitude={info['location']['lon']},
                    address="{info['district']}, Sardinia"
                ),
                node_type=NodeType.{info['type'].upper()},
                installation_date=datetime(2024, 1, 1),
                is_active=True,
                metadata={{"district": "{info['district']}", "original_id": "{node_id}"}}
            ),"""
            new_node_entries.append(node_entry)

        # Insert new nodes before the closing bracket
        existing_nodes = content[nodes_start:nodes_end]
        new_nodes_str = (
            existing_nodes.rstrip("]")
            + "\n"
            + "\n".join(new_node_entries)
            + "\n        ]"
        )

        # Replace in content
        new_content = content[:nodes_start] + new_nodes_str + content[nodes_end:]

        file_path.write_text(new_content)
        self.updates_made.append(
            f"✅ Updated static repository with {len(NEW_NODES)} new nodes"
        )

    def update_sensor_repository(self):
        """Update the sensor data repository with new mappings."""
        print("\n2. Updating Sensor Repository...")

        file_path = (
            project_root / "src/infrastructure/repositories/sensor_data_repository.py"
        )
        self.backup_file(file_path)

        content = file_path.read_text()

        # Find the node mapping
        mapping_start = content.find("uuid_to_node_mapping = {")
        mapping_end = content.find("}", mapping_start) + 1

        if mapping_start == -1:
            print("❌ Could not find uuid_to_node_mapping")
            return

        # Add new mappings
        new_mappings = []
        for node_id, info in NEW_NODES.items():
            new_mappings.append(
                f'            "{info["uuid"]}": "{info["bigquery_id"]}",'
            )

        # Insert before closing brace
        existing_mapping = content[mapping_start:mapping_end]
        updated_mapping = (
            existing_mapping.rstrip("}").rstrip()
            + ",\n"
            + "\n".join(new_mappings)
            + "\n        }"
        )

        new_content = content[:mapping_start] + updated_mapping + content[mapping_end:]

        file_path.write_text(new_content)
        self.updates_made.append("✅ Updated sensor repository mappings")

    def update_sidebar_filters(self):
        """Update sidebar filters to include new nodes."""
        print("\n3. Updating Sidebar Filters...")

        file_path = (
            project_root / "src/presentation/streamlit/components/sidebar_filters.py"
        )
        self.backup_file(file_path)

        content = file_path.read_text()

        # Find node options list
        options_pattern = r'options=\["All Nodes", "Sant\'Anna", "Seneca", "Selargius Tank", "External Supply"\]'

        # Create new options list with grouped nodes
        new_options = [
            '"All Nodes"',
            '"--- Original Nodes ---"',
            '"Sant\'Anna"',
            '"Seneca"',
            '"Selargius Tank"',
            '"External Supply"',
            '"--- Distribution Nodes ---"',
        ]

        # Add distribution nodes
        for node_id, info in NEW_NODES.items():
            if info["type"] == "distribution":
                new_options.append(f'"{info["display_name"]}"')

        new_options.append('"--- Monitoring Nodes ---"')

        # Add monitoring nodes
        for node_id, info in NEW_NODES.items():
            if info["type"] == "monitoring":
                new_options.append(f'"{info["display_name"]}"')

        new_options_str = f'options=[{", ".join(new_options)}]'

        # Replace in content
        new_content = re.sub(options_pattern, new_options_str, content)

        file_path.write_text(new_content)
        self.updates_made.append("✅ Updated sidebar with grouped node options")

    def update_tab_components(self):
        """Update all tab components with new node mappings."""
        print("\n4. Updating Tab Components...")

        tab_files = [
            "overview_tab.py",
            "consumption_patterns_tab.py",
            "network_efficiency_tab.py",
            "anomaly_detection_tab.py",
        ]

        for tab_file in tab_files:
            file_path = (
                project_root / f"src/presentation/streamlit/components/{tab_file}"
            )
            if not file_path.exists():
                continue

            self.backup_file(file_path)
            content = file_path.read_text()

            # Find node mapping dictionary
            mapping_pattern = r"node_mapping = \{[^}]+\}"
            mapping_match = re.search(mapping_pattern, content, re.DOTALL)

            if not mapping_match:
                print(f"⚠️  No node mapping found in {tab_file}")
                continue

            # Build new mapping
            new_mapping_lines = ["node_mapping = {"]
            new_mapping_lines.append(
                '    "Sant\'Anna": "00000000-0000-0000-0000-000000000001",'
            )
            new_mapping_lines.append(
                '    "Seneca": "00000000-0000-0000-0000-000000000002",'
            )
            new_mapping_lines.append(
                '    "Selargius Tank": "00000000-0000-0000-0000-000000000003",'
            )

            # Add new nodes
            for node_id, info in NEW_NODES.items():
                new_mapping_lines.append(
                    f'    "{info["display_name"]}": "{info["uuid"]}",'
                )

            new_mapping_lines.append("}")
            new_mapping = "\n".join(new_mapping_lines)

            # Replace in content
            new_content = (
                content[: mapping_match.start()]
                + new_mapping
                + content[mapping_match.end() :]
            )

            file_path.write_text(new_content)

        self.updates_made.append(f"✅ Updated {len(tab_files)} tab components")

    def update_forecast_config(self):
        """Update forecast configuration to include new nodes."""
        print("\n5. Updating Forecast Configuration...")

        # Update forecast endpoint validation
        file_path = project_root / "src/presentation/api/endpoints/forecast_endpoint.py"
        if file_path.exists():
            self.backup_file(file_path)
            content = file_path.read_text()

            # Find VALID_NODE_IDS
            valid_nodes_pattern = r"VALID_NODE_IDS = \[[^\]]+\]"
            valid_nodes_match = re.search(valid_nodes_pattern, content)

            if valid_nodes_match:
                # Add new node IDs
                new_node_ids = [
                    f'"{info["bigquery_id"]}"' for info in NEW_NODES.values()
                ]
                existing_ids = '"node-santanna", "node-seneca", "node-serbatoio"'
                all_ids = f'{existing_ids}, {", ".join(new_node_ids)}'
                new_valid_nodes = f"VALID_NODE_IDS = [{all_ids}]"

                new_content = (
                    content[: valid_nodes_match.start()]
                    + new_valid_nodes
                    + content[valid_nodes_match.end() :]
                )
                file_path.write_text(new_content)

                self.updates_made.append("✅ Updated forecast endpoint validation")

    def create_node_config_file(self):
        """Create a centralized node configuration file."""
        print("\n6. Creating Centralized Node Configuration...")

        config_path = project_root / "src/config/nodes.py"
        config_path.parent.mkdir(exist_ok=True)

        config_content = '''"""
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
'''

        # Add new nodes to config
        for node_id, info in NEW_NODES.items():
            config_content += """    "node_{node_id}": NodeConfig(
        node_id="{node_id}",
        uuid="{info['uuid']}",
        bigquery_id="{info['bigquery_id']}",
        display_name="{info['display_name']}",
        full_name="{info['name']}",
        node_type="{info['type']}",
        district="{info['district']}",
        latitude={info['location']['lat']},
        longitude={info['location']['lon']}
    ),
"""

        config_content += """}

# Combined node configuration
ALL_NODES = {**ORIGINAL_NODES, **NEW_NODES}

# Mapping helpers
UUID_TO_NODE = {node.uuid: node for node in ALL_NODES.values()}
BIGQUERY_ID_TO_NODE = {node.bigquery_id: node for node in ALL_NODES.values()}
DISPLAY_NAME_TO_UUID = {node.display_name: node.uuid for node in ALL_NODES.values()}

# Node groupings
DISTRIBUTION_NODES = [node for node in ALL_NODES.values() if node.node_type == "distribution"]
MONITORING_NODES = [node for node in ALL_NODES.values() if node.node_type == "monitoring"]
STORAGE_NODES = [node for node in ALL_NODES.values() if node.node_type == "storage"]

# Districts
DISTRICTS = list(set(node.district for node in ALL_NODES.values()))

# Valid IDs for API validation
VALID_NODE_IDS = [node.bigquery_id for node in ALL_NODES.values()]
VALID_DISTRICT_IDS = [f"DIST_{i:03d}" for i in range(1, len(DISTRICTS) + 1)]
"""

        config_path.write_text(config_content)
        self.updates_made.append("✅ Created centralized node configuration")

    def create_migration_guide(self):
        """Create a migration guide for developers."""
        print("\n7. Creating Migration Guide...")

        guide_path = project_root / "docs/NODE_INTEGRATION_GUIDE.md"

        guide_content = """# Node Integration Guide

## Overview

This guide documents the integration of 6 new sensor nodes from the backup data processing pipeline into the dashboard.

## New Nodes Added

### Distribution Nodes
- **Node 215542**: Selargius Distribution Node
- **Node 215600**: Selargius Distribution Node
- **Node 273933**: Selargius Distribution Node

### Monitoring Nodes
- **Node 281492**: Selargius Monitoring Node
- **Node 288399**: Selargius Monitoring Node
- **Node 288400**: Selargius Monitoring Node

## Integration Changes

### 1. Static Repository
- Added 6 new MonitoringNode entries with proper UUIDs and metadata
- Location: `/src/infrastructure/repositories/static_monitoring_node_repository.py`

### 2. Sensor Repository
- Updated UUID to BigQuery ID mappings
- Location: `/src/infrastructure/repositories/sensor_data_repository.py`

### 3. Sidebar Filters
- Added grouped node selection with categories:
  - Original Nodes
  - Distribution Nodes
  - Monitoring Nodes
- Location: `/src/presentation/streamlit/components/sidebar_filters.py`

### 4. Tab Components
- Updated node mappings in all dashboard tabs
- Files updated:
  - `overview_tab.py`
  - `consumption_patterns_tab.py`
  - `network_efficiency_tab.py`
  - `anomaly_detection_tab.py`

### 5. Forecast Configuration
- Added new node IDs to VALID_NODE_IDS
- Location: `/src/presentation/api/endpoints/forecast_endpoint.py`

### 6. Centralized Configuration
- Created new configuration file: `/src/config/nodes.py`
- Provides single source of truth for all node definitions

## Usage

### Accessing New Nodes in Code

```python
from src.config.nodes import ALL_NODES, DISPLAY_NAME_TO_UUID

# Get node by display name
node_uuid = DISPLAY_NAME_TO_UUID["Distribution 215542"]

# Get all distribution nodes
distribution_nodes = [n for n in ALL_NODES.values() if n.node_type == "distribution"]
```

### Querying New Node Data

The new nodes are automatically available through the existing repositories:

```python
# In any use case or repository
sensor_data = await sensor_repository.get_latest_readings(
    node_ids=["00000000-0000-0000-0000-000000215542"]
)
```

## Data Quality

The new nodes include additional metadata:
- `data_quality_score`: 0-1 score indicating data reliability
- `is_interpolated`: Boolean flag for interpolated values
- `source_file`: Original CSV filename

## Testing

Run the dashboard to verify:
1. New nodes appear in sidebar filters
2. Data displays correctly for each node
3. All visualizations work with new nodes
4. Forecast functionality includes new nodes

## Rollback

If needed, restore from backup files:
```bash
# All modified files have .backup copies
ls src/**/*.backup
```

## Next Steps

1. **Optimize Queries**: With 9 total nodes, consider query optimization
2. **Add Quality Indicators**: Display data quality scores in UI
3. **Enhanced Filtering**: Add node type filtering
4. **District Grouping**: Group nodes by district in visualizations

---

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

        guide_path.write_text(guide_content)
        self.updates_made.append("✅ Created integration guide")

    def run_integration(self):
        """Run the complete integration process."""
        print("=== Dashboard Integration Process ===\n")

        try:
            # Run all updates
            self.update_static_repository()
            self.update_sensor_repository()
            self.update_sidebar_filters()
            self.update_tab_components()
            self.update_forecast_config()
            self.create_node_config_file()
            self.create_migration_guide()

            # Summary
            print("\n=== Integration Summary ===")
            for update in self.updates_made:
                print(update)

            print(
                f"\n✅ Integration complete! {len(self.updates_made)} components updated."
            )
            print(f"\nBackup files created: {len(self.backup_files)}")

            # Save backup list
            backup_list_path = project_root / "integration_backups.txt"
            with open(backup_list_path, "w") as f:
                f.write(f"Integration performed: {datetime.now()}\n\n")
                for original, backup in self.backup_files:
                    f.write(f"{original} -> {backup}\n")

            print(f"\nBackup list saved to: {backup_list_path}")

        except Exception as e:
            print(f"\n❌ Error during integration: {e}")
            print("\nRolling back changes...")
            self.rollback()

    def rollback(self):
        """Rollback all changes by restoring backups."""
        for original, backup in self.backup_files:
            if backup.exists():
                original.write_text(backup.read_text())
                backup.unlink()
                print(f"✅ Restored {original}")


def main():
    """Main integration function."""
    integrator = DashboardIntegrator()
    integrator.run_integration()


if __name__ == "__main__":
    main()
