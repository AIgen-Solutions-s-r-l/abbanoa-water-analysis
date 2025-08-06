# Node Renaming Based on Water Volume Analysis

## Summary

We've successfully analyzed the water volume data from `cleaned_data.csv` to identify which nodes are tanks versus regular distribution or monitoring nodes. Based on the volume analysis, we've created scripts and recommendations for renaming the nodes in your database.

## Volume Analysis Results

The CSV file contains 4 volume columns (M3, M3.1, M3.2, M3.3) representing different nodes. Based on their maximum volumes:

| CSV Column | Max Volume (m³) | Category      | New Name   | Reasoning |
|------------|-----------------|---------------|------------|-----------|
| M3.3       | 11,077,575      | Tank          | TANK01     | Extremely high volume (11M m³) indicates storage tank |
| M3.2       | 5,219,552       | Monitoring    | MONITOR01  | High volume but no consumption pattern |
| M3         | 1,925,967       | Distribution  | NODE01     | Moderate volume with active consumption |
| M3.1       | 165,619         | Monitoring    | MONITOR02  | Lower volume monitoring point |

## Key Findings

1. **TANK01 (M3.3)**: With over 11 million m³ capacity, this is clearly a storage tank
2. **NODE01 (M3)**: Shows active consumption (1.9M m³ total), indicating a distribution node
3. **MONITOR01 & MONITOR02**: No consumption patterns, likely monitoring points

## Files Created

1. **`analyze_csv_volumes.py`** - Script that analyzes the CSV data and identifies tanks based on volume
2. **`csv_node_renaming_recommendations.json`** - JSON file with renaming recommendations
3. **`rename_nodes_simple.sql`** - SQL script for manual database updates
4. **`rename_nodes_database.py`** - Python script for automated database updates
5. **`node_config_volume_based.py`** - Updated node configuration based on analysis

## How to Apply the Renaming

### Option 1: Manual SQL Update
```bash
# Review and run the SQL script
psql -h localhost -p 5434 -U abbanoa_user -d abbanoa_processing < scripts/rename_nodes_simple.sql
```

### Option 2: Automated Python Script
```bash
# Run the automated renaming script
python3 scripts/rename_nodes_database.py
```

## Important Notes

1. **Verify Node ID Mapping**: The scripts assume a mapping between CSV columns and database node IDs. You may need to adjust the node_id values in the SQL script based on your actual database.

2. **Backup First**: Always backup your database before running renaming operations.

3. **Volume Thresholds**: The tank identification is based on:
   - Volume > 100,000 m³ AND
   - Volume in top 20% of all nodes
   - Low consumption ratio (< 1% per hour)

## Next Steps

1. Review the node ID mappings in your database
2. Run either the SQL script or Python script to apply the renaming
3. Update any dashboard or reporting configurations that reference the old node names
4. Consider adding these volume-based categorizations to your monitoring dashboards

## Volume Statistics

- **Total nodes analyzed**: 4
- **Identified tanks**: 1 (TANK01 with 11M m³)
- **Distribution nodes**: 1 (NODE01 with 1.9M m³)
- **Monitoring points**: 2 (MONITOR01 with 5.2M m³, MONITOR02 with 165K m³)

