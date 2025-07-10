# Node Integration Guide

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

Generated: 2025-07-10 07:58:18
