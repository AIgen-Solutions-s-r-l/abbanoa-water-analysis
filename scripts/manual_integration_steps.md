# Manual Integration Steps for New Nodes

This guide provides the exact code changes needed to integrate the 6 new nodes into the dashboard.

## Quick Integration (Minimal Changes)

### 1. Update Sensor Repository Mappings

**File**: `src/infrastructure/repositories/sensor_data_repository.py`

Find the `uuid_to_node_mapping` dictionary (around line 25) and add these lines before the closing brace:

```python
            # New nodes from backup data
            "00000000-0000-0000-0000-000000215542": "215542",
            "00000000-0000-0000-0000-000000215600": "215600",
            "00000000-0000-0000-0000-000000273933": "273933",
            "00000000-0000-0000-0000-000000281492": "281492",
            "00000000-0000-0000-0000-000000288399": "288399",
            "00000000-0000-0000-0000-000000288400": "288400",
```

### 2. Update Sidebar Node Options

**File**: `src/presentation/streamlit/components/sidebar_filters.py`

Find the `multiselect` for node selection (around line 88) and replace the options list:

```python
        options=[
            "All Nodes", 
            "Sant'Anna", 
            "Seneca", 
            "Selargius Tank", 
            "External Supply",
            # New nodes
            "Node 215542",
            "Node 215600", 
            "Node 273933",
            "Node 281492",
            "Node 288399",
            "Node 288400"
        ],
```

### 3. Update Tab Components

For each of these files, add the new node mappings to the `node_mapping` dictionary:

**Files to update**:
- `src/presentation/streamlit/components/overview_tab.py`
- `src/presentation/streamlit/components/consumption_patterns_tab.py`
- `src/presentation/streamlit/components/network_efficiency_tab.py`
- `src/presentation/streamlit/components/anomaly_detection_tab.py`

Add these lines to each `node_mapping` dictionary:

```python
    # New nodes
    "Node 215542": "00000000-0000-0000-0000-000000215542",
    "Node 215600": "00000000-0000-0000-0000-000000215600",
    "Node 273933": "00000000-0000-0000-0000-000000273933",
    "Node 281492": "00000000-0000-0000-0000-000000281492",
    "Node 288399": "00000000-0000-0000-0000-000000288399",
    "Node 288400": "00000000-0000-0000-0000-000000288400",
```

### 4. Update Forecast Validation (Optional)

**File**: `src/presentation/api/endpoints/forecast_endpoint.py`

Add the new node IDs to `VALID_NODE_IDS`:

```python
VALID_NODE_IDS = [
    "node-santanna", "node-seneca", "node-serbatoio",
    # New nodes
    "215542", "215600", "273933", "281492", "288399", "288400"
]
```

## That's it! 🎉

With these 4 simple changes, the new nodes will be fully integrated into the dashboard.

## Testing

1. Start the dashboard:
   ```bash
   streamlit run src/presentation/streamlit/app.py
   ```

2. Check that:
   - New nodes appear in the sidebar dropdown
   - Selecting a new node shows data
   - All tabs work with the new nodes

## Enhanced Integration (Optional)

For a better user experience, you can:

### Group Nodes by Type in Sidebar

Replace the simple list with grouped options:

```python
options=[
    "All Nodes",
    "--- Original Nodes ---",
    "Sant'Anna", 
    "Seneca", 
    "Selargius Tank",
    "--- Distribution Nodes ---", 
    "Distribution 215542",
    "Distribution 215600",
    "Distribution 273933",
    "--- Monitoring Nodes ---",
    "Monitoring 281492",
    "Monitoring 288399", 
    "Monitoring 288400",
    "--- Other ---",
    "External Supply"
],
```

### Add Node Type Indicators

Update the display names to include the node type:

```python
node_mapping = {
    "Sant'Anna": "00000000-0000-0000-0000-000000000001",
    "Seneca": "00000000-0000-0000-0000-000000000002",
    "Selargius Tank": "00000000-0000-0000-0000-000000000003",
    # Distribution nodes
    "Distribution 215542": "00000000-0000-0000-0000-000000215542",
    "Distribution 215600": "00000000-0000-0000-0000-000000215600",
    "Distribution 273933": "00000000-0000-0000-0000-000000273933",
    # Monitoring nodes
    "Monitoring 281492": "00000000-0000-0000-0000-000000281492",
    "Monitoring 288399": "00000000-0000-0000-0000-000000288399",
    "Monitoring 288400": "00000000-0000-0000-0000-000000288400",
}
```

## Data Quality Enhancement

To show data quality indicators, modify the queries in tab components:

```python
# In any tab that fetches sensor data
readings_df = pd.DataFrame(readings_list)

# Add quality indicator column
if 'data_quality_score' in readings_df.columns:
    readings_df['quality_indicator'] = readings_df['data_quality_score'].apply(
        lambda x: '🟢' if x > 0.8 else '🟡' if x > 0.5 else '🔴'
    )
```

Then display the quality indicator in charts or tables.