# Infrastructure Map Node Names Fix

## Issue Description

When clicking on nodes in the Infrastructure Map, the node detail modal was showing old node names (like "Seneca Node", "Serbatoio Node", "Sant'Anna Node") instead of the new systematic names (like "Q.MATTEOTTI", "CENTRO EST", etc.).

## Root Cause

The issue was in the API endpoints that provide data to the Infrastructure Map:

1. **Dashboard Router** (`src/presentation/api/endpoints/dashboard_router.py`) was using hardcoded mock data with old node names
2. **Anomaly Router** (`src/presentation/api/endpoints/anomaly_router.py`) was also using hardcoded mock data

The Infrastructure Map fetches data from these endpoints, so it was receiving the old names instead of the actual database data.

## Solution

### 1. Updated Dashboard Router

**File**: `src/presentation/api/endpoints/dashboard_router.py`

**Changes**:
- Replaced hardcoded mock data with real database queries
- Added database connection configuration
- Now fetches actual node data from `water_infrastructure.nodes` table
- Returns real node names like "Q.MATTEOTTI", "CENTRO EST", etc.

**Before**:
```python
return {
    "nodes": [
        {
            "node_id": "node-seneca",
            "node_name": "Seneca Node",  # Old name
            "flow_rate": 200.0,
            # ...
        }
    ]
}
```

**After**:
```python
# Real database query
nodes_query = """
    SELECT DISTINCT ON (n.node_id)
        n.node_id,
        n.node_name,  # Real names from database
        n.node_type,
        COALESCE(sr.flow_rate, 0.0) as flow_rate,
        COALESCE(sr.pressure, 0.0) as pressure,
        # ...
    FROM water_infrastructure.nodes n
    LEFT JOIN water_infrastructure.sensor_readings sr 
        ON sr.node_id = n.node_id
    WHERE n.is_active = true
"""
```

### 2. Updated Anomaly Router

**File**: `src/presentation/api/endpoints/anomaly_router.py`

**Changes**:
- Replaced hardcoded mock data with real database queries
- Fixed SQL query to use correct column names (`anomaly_id` instead of `id`)
- Now fetches actual anomaly data with correct node names
- Proper parameter handling for optional filters

**Before**:
```python
mock_anomalies = [
    {
        "node_id": "node-serbatoio",
        "node_name": "Serbatoio Node",  # Old name
        # ...
    }
]
```

**After**:
```python
# Real database query
query = """
    SELECT 
        a.anomaly_id as id,
        a.node_id,
        n.node_name,  # Real names from database
        # ...
    FROM water_infrastructure.anomalies a
    JOIN water_infrastructure.nodes n ON a.node_id = n.node_id
"""
```

## Verification

The fix was verified by:

1. **Database Check**: Confirmed that the database contains the correct node names:
   ```
   Q.MATTEOTTI, CENTRO EST, CENTRO NORD, CENTRO OVEST, CENTRO SUD,
   FIORI, LIBERTÀ, Q.GALLUS, Q.MONSERRATO, Q.NENNI SUD, Q.SANT'ANNA,
   Q.SARDEGNA, Q.TRIESTE, STADIO
   ```

2. **API Test**: Created and ran a test script that verified:
   - Dashboard summary endpoint returns correct node names
   - Anomaly endpoint works correctly
   - No old names ("Seneca Node", "Serbatoio Node", "Sant'Anna Node") are present

3. **Test Results**:
   ```
   ✅ Dashboard Summary Test PASSED
   📊 Found 14 nodes
   ✅ No old node names found - all names are correct!
   
   ✅ Anomalies Endpoint Test PASSED
   📊 Found 0 anomalies
   
   ✅ ALL TESTS PASSED
   🎉 Infrastructure Map will now show correct node names!
   ```

## Impact

**Before Fix**: When clicking on nodes in the Infrastructure Map, users saw old names like "Seneca Node"

**After Fix**: When clicking on nodes in the Infrastructure Map, users now see the correct new names like "Q.MATTEOTTI"

## Files Modified

1. `src/presentation/api/endpoints/dashboard_router.py` - Updated to use real database data
2. `src/presentation/api/endpoints/anomaly_router.py` - Updated to use real database data

## Testing

To test the fix:

1. Start the API server
2. Navigate to the Infrastructure Map
3. Click on any node
4. Verify that the node detail modal shows the correct node name (e.g., "Q.MATTEOTTI" instead of "Seneca Node")

## Notes

- The fix maintains backward compatibility
- No changes were needed to the frontend Infrastructure Map component
- The fix uses the existing database schema
- All node names now come from the authoritative source (database)
