# Network Efficiency API Documentation

## Overview

The Network Efficiency API provides comprehensive analytics and metrics for water infrastructure network performance. This API enables real-time monitoring, performance analysis, and operational insights for water distribution networks.

## Base URL

```
https://api.abbanoa.com/v1/efficiency
```

## Authentication

All API requests require proper authentication headers (details to be configured based on deployment setup).

## Endpoints

### GET /v1/efficiency/summary

Get comprehensive network efficiency summary including overall metrics, system-wide statistics, and individual node performance data.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `time_range` | string | No | `"24h"` | Time range for analysis. Valid values: `"1h"`, `"6h"`, `"24h"`, `"3d"`, `"7d"`, `"30d"` |
| `node_ids` | array[string] | No | `null` | Optional list of specific node IDs to analyze |

#### Example Request

```bash
curl -X GET "https://api.abbanoa.com/v1/efficiency/summary?time_range=24h&node_ids=215542,288400" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json"
```

#### Response Schema

```json
{
  "summary": {
    "time_range": "24h",
    "period_start": "2024-01-15T00:00:00Z",
    "period_end": "2024-01-16T00:00:00Z",
    "total_nodes": 8,
    "active_nodes": 7,
    "analyzed_hours": 24
  },
  "efficiency_metrics": {
    "network_efficiency_percentage": 87.5,
    "total_throughput_m3h": 1250.75,
    "average_pressure_bar": 4.2,
    "quality_score": 0.95,
    "operational_efficiency": 83.3,
    "flow_consistency_score": 0.92
  },
  "system_metrics": {
    "total_system_volume_m3": 30018.0,
    "avg_system_flow_rate": 15.8,
    "avg_system_pressure": 4.2,
    "avg_system_quality": 0.95,
    "active_nodes": 10,
    "total_readings": 240
  },
  "node_performance": [
    {
      "node_id": "215542",
      "node_name": "Main Sensor 215542",
      "node_type": "meter",
      "reading_count": 24,
      "avg_flow_rate": 7.76,
      "avg_pressure": 6.77,
      "avg_temperature": 18.5,
      "total_volume_m3": 669.6,
      "avg_quality_score": 0.98,
      "uptime_percentage": 100.0,
      "first_reading": "2024-01-15T00:00:00Z",
      "last_reading": "2024-01-15T23:00:00Z"
    }
  ],
  "metadata": {
    "generated_at": "2024-01-16T10:30:00Z",
    "data_source": "sensor_readings_hourly",
    "version": "1.0"
  }
}
```

#### Response Fields

##### Summary Object

| Field | Type | Description |
|-------|------|-------------|
| `time_range` | string | Time range analyzed |
| `period_start` | string | Start of analysis period (ISO 8601) |
| `period_end` | string | End of analysis period (ISO 8601) |
| `total_nodes` | integer | Total number of nodes analyzed |
| `active_nodes` | integer | Number of active nodes |
| `analyzed_hours` | integer | Number of hours analyzed |

##### Efficiency Metrics Object

| Field | Type | Description |
|-------|------|-------------|
| `network_efficiency_percentage` | float | Overall network efficiency percentage |
| `total_throughput_m3h` | float | Total system throughput in m³/hour |
| `average_pressure_bar` | float | Average system pressure in bar |
| `quality_score` | float | Average data quality score (0-1) |
| `operational_efficiency` | float | Operational efficiency percentage |
| `flow_consistency_score` | float | Flow consistency score (0-1) |

##### System Metrics Object

| Field | Type | Description |
|-------|------|-------------|
| `total_system_volume_m3` | float | Total system volume in m³ |
| `avg_system_flow_rate` | float | Average system flow rate in L/s |
| `avg_system_pressure` | float | Average system pressure in bar |
| `avg_system_quality` | float | Average system data quality score |
| `active_nodes` | integer | Number of active nodes |
| `total_readings` | integer | Total number of readings |

##### Node Performance Object

| Field | Type | Description |
|-------|------|-------------|
| `node_id` | string | Unique node identifier |
| `node_name` | string | Human-readable node name |
| `node_type` | string | Type of node (e.g., 'meter', 'sensor') |
| `reading_count` | integer | Number of readings in the time period |
| `avg_flow_rate` | float | Average flow rate in L/s |
| `avg_pressure` | float | Average pressure in bar |
| `avg_temperature` | float | Average temperature in °C |
| `total_volume_m3` | float | Total volume processed in m³ |
| `avg_quality_score` | float | Average quality score (0-1) |
| `uptime_percentage` | float | Node uptime percentage |
| `first_reading` | string | Timestamp of first reading (ISO 8601) |
| `last_reading` | string | Timestamp of last reading (ISO 8601) |

### GET /v1/efficiency/health

Health check endpoint for the efficiency service.

#### Example Request

```bash
curl -X GET "https://api.abbanoa.com/v1/efficiency/health" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

#### Response Schema

```json
{
  "status": "healthy",
  "service": "efficiency",
  "version": "1.0",
  "timestamp": "2024-01-16T10:30:00Z"
}
```

## Error Responses

The API uses standard HTTP status codes and returns detailed error information in JSON format.

### Error Response Schema

```json
{
  "error": "error_type",
  "message": "Human-readable error message",
  "details": {
    "additional": "error context"
  }
}
```

### Common Error Codes

#### 400 Bad Request

**Invalid Time Range**
```json
{
  "error": "invalid_time_range",
  "message": "Invalid time range: 48h. Must be one of: ['1h', '6h', '24h', '3d', '7d', '30d']",
  "details": {
    "provided_value": "48h",
    "valid_values": ["1h", "6h", "24h", "3d", "7d", "30d"]
  }
}
```

**Invalid Node IDs**
```json
{
  "error": "invalid_node_ids",
  "message": "node_ids must be a non-empty list of strings",
  "details": {
    "provided_value": [],
    "expected_type": "List[str]"
  }
}
```

#### 500 Internal Server Error

```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred while processing the efficiency summary",
  "details": {
    "time_range": "24h",
    "node_ids": null
  }
}
```

#### 503 Service Unavailable

```json
{
  "error": "service_unavailable",
  "message": "Efficiency service is currently unavailable",
  "details": {
    "error": "Database connection failed"
  }
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Standard requests**: 100 requests per minute per API key
- **Burst requests**: 300 requests per 5 minutes per API key

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1642348800
```

## Data Freshness

The efficiency data is updated every 5 minutes from the live ETL pipeline:

- **Data source**: PostgreSQL `sensor_readings_hourly` materialized view
- **Update frequency**: Every 5 minutes
- **Data retention**: 
  - Recent data (< 90 days): PostgreSQL (warm storage)
  - Historical data (> 90 days): BigQuery (cold storage)

## SDK Examples

### Python

```python
import requests
from typing import Optional, List

class EfficiencyAPI:
    def __init__(self, api_key: str, base_url: str = "https://api.abbanoa.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_efficiency_summary(self, time_range: str = "24h", node_ids: Optional[List[str]] = None):
        """Get network efficiency summary."""
        url = f"{self.base_url}/v1/efficiency/summary"
        params = {"time_range": time_range}
        
        if node_ids:
            params["node_ids"] = node_ids
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

# Usage
api = EfficiencyAPI("your_api_key")
summary = api.get_efficiency_summary(time_range="24h", node_ids=["215542", "288400"])
print(f"Network efficiency: {summary['efficiency_metrics']['network_efficiency_percentage']}%")
```

### JavaScript

```javascript
class EfficiencyAPI {
    constructor(apiKey, baseUrl = 'https://api.abbanoa.com') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }
    
    async getEfficiencySummary(timeRange = '24h', nodeIds = null) {
        const url = new URL(`${this.baseUrl}/v1/efficiency/summary`);
        url.searchParams.append('time_range', timeRange);
        
        if (nodeIds) {
            nodeIds.forEach(nodeId => url.searchParams.append('node_ids', nodeId));
        }
        
        const response = await fetch(url, {
            method: 'GET',
            headers: this.headers
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
}

// Usage
const api = new EfficiencyAPI('your_api_key');
const summary = await api.getEfficiencySummary('24h', ['215542', '288400']);
console.log(`Network efficiency: ${summary.efficiency_metrics.network_efficiency_percentage}%`);
```

## Testing

### Interactive API Documentation

Visit the interactive API documentation at:
```
https://api.abbanoa.com/docs
```

### Testing Endpoints

The API includes comprehensive test coverage with:

- **Unit tests**: Core service logic validation
- **Integration tests**: Full API endpoint testing
- **Performance tests**: Load and stress testing
- **Security tests**: Authentication and authorization

### CI/CD Pipeline

The efficiency API is automatically tested on every commit with:

- Code quality checks (Black, Flake8, MyPy)
- Security scanning (Bandit, Safety)
- Comprehensive test suite execution
- Docker image building and validation

## Monitoring

The efficiency service includes comprehensive monitoring:

- **Health checks**: `/v1/efficiency/health` endpoint
- **Metrics collection**: Response times, error rates, throughput
- **Logging**: Structured logging with request tracing
- **Alerting**: Automatic alerts for service degradation

## Support

For API support, please contact:

- **Technical Support**: api-support@abbanoa.com
- **Documentation**: https://docs.abbanoa.com/api/efficiency
- **Status Page**: https://status.abbanoa.com

## Changelog

### Version 1.0 (January 2024)

- Initial release of Network Efficiency API
- Comprehensive efficiency metrics and analytics
- Node performance monitoring
- Real-time data integration
- Complete test coverage and CI/CD pipeline 