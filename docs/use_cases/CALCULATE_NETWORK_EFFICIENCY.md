# Calculate Network Efficiency Use Case

This document provides a detailed overview of the `CalculateNetworkEfficiencyUseCase`, which is responsible for calculating water network efficiency metrics.

## Use Case Description

The `CalculateNetworkEfficiencyUseCase` calculates the efficiency of a water network for a given time period. It can also be used to detect potential leakage zones within the network.

## API Endpoint

The use case is exposed through the following API endpoint:

`POST /api/v1/efficiency/calculate`

### Request Body

```json
{
  "network_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "start_date": "2023-01-01T00:00:00Z",
  "end_date": "2023-01-31T23:59:59Z",
  "include_node_details": true
}
```

*   `network_id` (string, required): The UUID of the water network to analyze.
*   `start_date` (string, required): The start date of the analysis period in ISO 8601 format.
*   `end_date` (string, required): The end date of the analysis period in ISO 8601 format.
*   `include_node_details` (boolean, optional): Whether to include detailed information about each node's contribution to the network efficiency.

### Response Body

```json
{
  "network_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "period_start": "2023-01-01T00:00:00Z",
  "period_end": "2023-01-31T23:59:59Z",
  "efficiency_percentage": 95.5,
  "total_input_volume": 10000,
  "total_output_volume": 9550,
  "loss_volume": 450,
  "loss_percentage": 4.5,
  "node_contributions": {
    "a1b2c3d4-e5f6-7890-1234-567890abcdef": {
      "node_name": "Node A",
      "total_volume": 5000,
      "average_flow_rate": 10.5,
      "reading_count": 720
    }
  }
}
```

## Implementation Details

The use case is implemented in the `src/application/use_cases/calculate_network_efficiency.py` file. It uses the `WaterNetworkRepository`, `MonitoringNodeRepository`, and `SensorReadingRepository` to fetch the necessary data. The actual efficiency calculation is performed by the `NetworkEfficiencyService`.

## Detecting Leakage Zones

The use case also provides a method for detecting potential leakage zones within the network. This functionality is exposed through the `detect_leakage_zones` method, which is not yet available through the API.
