# API Reference Guide

## Overview

The Abbanoa Water Infrastructure Analytics Platform provides a comprehensive RESTful API built with FastAPI. The API offers access to sensor data, ML predictions, network metrics, and system monitoring capabilities.

## Base Information

- **Base URL**: `http://localhost:8000` (development), `https://api.curator.aigensolutions.it` (production)
- **API Version**: v1
- **Content Type**: `application/json`
- **Authentication**: JWT Bearer tokens
- **Rate Limiting**: 1000 requests per hour per API key

## Interactive Documentation

When the API service is running, interactive documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Authentication

### JWT Authentication

```bash
# Obtain token
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_username&password=your_password"

# Use token in requests
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/api/v1/nodes"
```

### API Key Authentication

```bash
# Using API key in header
curl -H "X-API-Key: YOUR_API_KEY" \
  "http://localhost:8000/api/v1/nodes"
```

## Core Endpoints

### Health and Status

#### GET /health
Returns the health status of the API service.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-12T20:30:00Z",
  "version": "1.2.3.14",
  "environment": "production"
}
```

#### GET /status
Returns detailed system status including all services.

**Response**:
```json
{
  "api": "healthy",
  "database": "healthy",
  "redis": "healthy",
  "bigquery": "healthy",
  "processing_service": "running",
  "last_update": "2025-07-12T20:29:30Z"
}
```

### Node Management

#### GET /api/v1/nodes
Retrieve all monitoring nodes.

**Query Parameters**:
- `active_only` (boolean, optional): Filter for active nodes only
- `region` (string, optional): Filter by geographic region

**Response**:
```json
{
  "nodes": [
    {
      "id": "215542",
      "name": "Selargius Node 1",
      "location": {
        "latitude": 39.2544,
        "longitude": 9.1428,
        "address": "Via Roma, Selargius"
      },
      "status": "active",
      "sensor_types": ["flow_rate", "pressure", "temperature"],
      "last_reading": "2025-07-12T20:00:00Z",
      "installation_date": "2024-11-01T00:00:00Z"
    }
  ],
  "total_count": 6,
  "active_count": 6
}
```

#### GET /api/v1/nodes/{node_id}
Retrieve specific node details.

**Path Parameters**:
- `node_id` (string, required): Node identifier

**Response**:
```json
{
  "id": "215542",
  "name": "Selargius Node 1",
  "location": {
    "latitude": 39.2544,
    "longitude": 9.1428,
    "address": "Via Roma, Selargius"
  },
  "status": "active",
  "sensor_types": ["flow_rate", "pressure", "temperature"],
  "last_reading": "2025-07-12T20:00:00Z",
  "installation_date": "2024-11-01T00:00:00Z",
  "metadata": {
    "manufacturer": "Hidroconta",
    "model": "HM-4000",
    "firmware_version": "2.1.0"
  }
}
```

### Sensor Data

#### GET /api/v1/nodes/{node_id}/readings
Retrieve sensor readings for a specific node.

**Path Parameters**:
- `node_id` (string, required): Node identifier

**Query Parameters**:
- `start_time` (ISO datetime, optional): Start of time range
- `end_time` (ISO datetime, optional): End of time range
- `limit` (integer, optional): Maximum number of records (default: 100, max: 1000)
- `metric_type` (string, optional): Filter by metric type (flow_rate, pressure, temperature)

**Response**:
```json
{
  "node_id": "215542",
  "readings": [
    {
      "timestamp": "2025-07-12T20:00:00Z",
      "flow_rate": 12.5,
      "pressure": 2.3,
      "temperature": 18.2,
      "total_flow": 145.7,
      "quality_score": 0.95
    }
  ],
  "total_count": 48,
  "time_range": {
    "start": "2025-07-12T00:00:00Z",
    "end": "2025-07-12T20:00:00Z"
  }
}
```

#### POST /api/v1/nodes/{node_id}/readings
Submit new sensor readings (for data ingestion).

**Path Parameters**:
- `node_id` (string, required): Node identifier

**Request Body**:
```json
{
  "readings": [
    {
      "timestamp": "2025-07-12T20:30:00Z",
      "flow_rate": 13.2,
      "pressure": 2.4,
      "temperature": 18.5,
      "total_flow": 146.2
    }
  ]
}
```

**Response**:
```json
{
  "message": "Readings successfully ingested",
  "ingested_count": 1,
  "errors": []
}
```

### Network Metrics

#### GET /api/v1/network/metrics
Retrieve network-wide performance metrics.

**Query Parameters**:
- `start_time` (ISO datetime, optional): Start of time range
- `end_time` (ISO datetime, optional): End of time range
- `aggregation` (string, optional): Aggregation level (hourly, daily, weekly)

**Response**:
```json
{
  "metrics": {
    "total_flow": 1250.7,
    "average_pressure": 2.2,
    "network_efficiency": 0.87,
    "active_nodes": 6,
    "data_quality": 0.94
  },
  "time_range": {
    "start": "2025-07-12T00:00:00Z",
    "end": "2025-07-12T20:30:00Z"
  },
  "node_breakdown": [
    {
      "node_id": "215542",
      "flow_rate": 12.5,
      "pressure": 2.3,
      "efficiency": 0.89
    }
  ]
}
```

#### GET /api/v1/network/efficiency
Calculate network efficiency metrics.

**Query Parameters**:
- `time_period` (string, optional): Analysis period (24h, 7d, 30d)
- `include_breakdown` (boolean, optional): Include node-level breakdown

**Response**:
```json
{
  "overall_efficiency": 0.87,
  "efficiency_trend": "improving",
  "benchmark_comparison": 0.05,
  "time_period": "24h",
  "breakdown": [
    {
      "node_id": "215542",
      "efficiency": 0.89,
      "flow_consistency": 0.92,
      "pressure_stability": 0.85
    }
  ],
  "recommendations": [
    "Optimize pressure settings on node 273933",
    "Schedule maintenance for node 288400"
  ]
}
```

### Predictions and Forecasting

#### GET /api/v1/predictions/{node_id}
Retrieve ML predictions for a specific node.

**Path Parameters**:
- `node_id` (string, required): Node identifier

**Query Parameters**:
- `horizon` (integer, optional): Prediction horizon in days (1-7, default: 7)
- `metric_type` (string, optional): Metric to predict (flow_rate, pressure)
- `include_confidence` (boolean, optional): Include confidence intervals

**Response**:
```json
{
  "node_id": "215542",
  "metric_type": "flow_rate",
  "horizon_days": 7,
  "model_used": "prophet_v2.1",
  "model_accuracy": 0.92,
  "predictions": [
    {
      "timestamp": "2025-07-13T00:00:00Z",
      "predicted_value": 12.8,
      "confidence_lower": 11.5,
      "confidence_upper": 14.1,
      "confidence_level": 0.95
    }
  ],
  "generated_at": "2025-07-12T20:30:00Z"
}
```

#### POST /api/v1/predictions/batch
Generate batch predictions for multiple nodes.

**Request Body**:
```json
{
  "node_ids": ["215542", "215600", "273933"],
  "horizon_days": 7,
  "metric_types": ["flow_rate", "pressure"],
  "include_confidence": true
}
```

**Response**:
```json
{
  "predictions": {
    "215542": {
      "flow_rate": [...],
      "pressure": [...]
    }
  },
  "model_info": {
    "version": "prophet_v2.1",
    "accuracy": 0.92,
    "training_date": "2025-07-12T00:00:00Z"
  }
}
```

### Anomaly Detection

#### GET /api/v1/anomalies
Retrieve detected anomalies.

**Query Parameters**:
- `start_time` (ISO datetime, optional): Start of time range
- `end_time` (ISO datetime, optional): End of time range
- `severity` (string, optional): Filter by severity (low, medium, high, critical)
- `node_id` (string, optional): Filter by specific node
- `status` (string, optional): Filter by status (active, acknowledged, resolved)

**Response**:
```json
{
  "anomalies": [
    {
      "id": "anom_20250712_001",
      "node_id": "273933",
      "metric_type": "pressure",
      "severity": "high",
      "status": "active",
      "detected_at": "2025-07-12T19:45:00Z",
      "description": "Pressure drop detected - 15% below normal range",
      "anomaly_score": 0.85,
      "expected_value": 2.3,
      "actual_value": 1.95,
      "recommendations": [
        "Check for potential leaks in distribution line",
        "Verify pump operation status"
      ]
    }
  ],
  "total_count": 3,
  "active_count": 1
}
```

#### POST /api/v1/anomalies/{anomaly_id}/acknowledge
Acknowledge an anomaly.

**Path Parameters**:
- `anomaly_id` (string, required): Anomaly identifier

**Request Body**:
```json
{
  "acknowledged_by": "operator_id",
  "notes": "Investigating potential leak in sector 3"
}
```

### Data Quality

#### GET /api/v1/data-quality
Retrieve data quality metrics.

**Query Parameters**:
- `start_time` (ISO datetime, optional): Start of time range
- `end_time` (ISO datetime, optional): End of time range
- `node_id` (string, optional): Filter by specific node

**Response**:
```json
{
  "overall_quality": 0.94,
  "quality_trend": "stable",
  "metrics": {
    "completeness": 0.96,
    "accuracy": 0.93,
    "consistency": 0.92,
    "timeliness": 0.95
  },
  "node_breakdown": [
    {
      "node_id": "215542",
      "quality_score": 0.95,
      "issues": []
    },
    {
      "node_id": "288400",
      "quality_score": 0.88,
      "issues": ["intermittent_readings", "calibration_drift"]
    }
  ]
}
```

## Response Codes

### Success Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content returned

### Client Error Codes
- `400 Bad Request`: Invalid request format or parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `429 Too Many Requests`: Rate limit exceeded

### Server Error Codes
- `500 Internal Server Error`: Unexpected server error
- `502 Bad Gateway`: Upstream service unavailable
- `503 Service Unavailable`: Service temporarily unavailable
- `504 Gateway Timeout`: Upstream service timeout

## Error Response Format

All error responses follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid node_id format",
    "details": {
      "field": "node_id",
      "expected_format": "6-digit string",
      "provided_value": "invalid"
    },
    "request_id": "req_12345"
  }
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Default Limit**: 1000 requests per hour per API key
- **Burst Limit**: 100 requests per minute
- **Headers**: Rate limit information in response headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1625097600
```

## Pagination

For endpoints returning large datasets, pagination is supported:

**Query Parameters**:
- `limit` (integer): Number of records per page (default: 100, max: 1000)
- `offset` (integer): Number of records to skip
- `cursor` (string): Cursor-based pagination token

**Response Format**:
```json
{
  "data": [...],
  "pagination": {
    "limit": 100,
    "offset": 0,
    "total": 1500,
    "has_more": true,
    "next_cursor": "eyJpZCI6MTAwfQ=="
  }
}
```

## Webhooks

The API supports webhooks for real-time notifications:

### Webhook Events
- `anomaly.detected`: New anomaly detected
- `data.quality_alert`: Data quality issue detected
- `node.offline`: Node goes offline
- `node.online`: Node comes back online

### Webhook Payload
```json
{
  "event_type": "anomaly.detected",
  "event_id": "evt_12345",
  "timestamp": "2025-07-12T20:30:00Z",
  "data": {
    "anomaly_id": "anom_20250712_001",
    "node_id": "273933",
    "severity": "high"
  }
}
```

### Webhook Configuration
```bash
curl -X POST "http://localhost:8000/api/v1/webhooks" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/abbanoa",
    "events": ["anomaly.detected", "node.offline"],
    "secret": "your_webhook_secret"
  }'
```

## SDK and Client Libraries

### Python Client
```python
from abbanoa_client import AbbanoaClient

client = AbbanoaClient(
    base_url="http://localhost:8000",
    api_key="your_api_key"
)

# Get node data
nodes = client.nodes.list()
readings = client.nodes.get_readings("215542", limit=100)

# Get predictions
predictions = client.predictions.get("215542", horizon=7)
```

### JavaScript Client
```javascript
import { AbbanoaClient } from '@abbanoa/js-client';

const client = new AbbanoaClient({
  baseUrl: 'http://localhost:8000',
  apiKey: 'your_api_key'
});

// Get node data
const nodes = await client.nodes.list();
const readings = await client.nodes.getReadings('215542', { limit: 100 });
```

## Changelog

### Version 1.2.3.14
- Added data quality endpoints
- Improved anomaly detection response format
- Added batch prediction capabilities
- Enhanced error response structure

---

*For technical support, contact: tech-support@abbanoa.it*
*For API issues, create an issue at: [GitHub Issues](https://github.com/abbanoa/water-infrastructure/issues)*