# Detect Network Anomalies Use Case

This document provides a detailed overview of the `DetectNetworkAnomaliesUseCase`, which is responsible for detecting anomalies in the water network.

## Use Case Description

The `DetectNetworkAnomaliesUseCase` detects anomalies in sensor readings for all or a specified set of monitoring nodes. It can also send notifications for critical anomalies.

## API Endpoint

The use case is exposed through the following API endpoint:

`POST /api/v1/anomalies/detect`

### Request Body

```json
{
  "node_ids": [
    "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  ],
  "time_window_hours": 24,
  "notify_on_critical": true
}
```

*   `node_ids` (array of strings, optional): A list of UUIDs of the monitoring nodes to analyze. If not provided, all active nodes will be analyzed.
*   `time_window_hours` (integer, optional): The number of hours to look back for anomalies. Defaults to 24.
*   `notify_on_critical` (boolean, optional): Whether to send notifications for critical anomalies. Defaults to true.

### Response Body

```json
[
  {
    "node_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "timestamp": "2023-01-15T10:30:00Z",
    "anomaly_type": "flow_spike",
    "severity": "critical",
    "measurement_type": "flow_rate",
    "actual_value": 250.5,
    "expected_range": [50, 120],
    "deviation_percentage": 108.75,
    "description": "Flow rate is significantly higher than expected."
  }
]
```

## Implementation Details

The use case is implemented in the `src/application/use_cases/detect_network_anomalies.py` file. It uses the `SensorReadingRepository` and `MonitoringNodeRepository` to fetch the necessary data. The actual anomaly detection is performed by the `AnomalyDetectionService`.

## Notifications

If `notify_on_critical` is set to `true` in the request, the use case will send a notification for any anomalies with a severity of `critical` or `high`. The notification is sent using the `INotificationService`.
