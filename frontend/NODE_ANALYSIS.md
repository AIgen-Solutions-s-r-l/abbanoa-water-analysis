# Node Analysis and Infrastructure Management

This document describes the node-specific and infrastructure type analysis functionality for water consumption analytics.

## Overview

The node analysis system provides comprehensive insights into individual network nodes and infrastructure types, enabling detailed monitoring, performance analysis, and maintenance planning for the water distribution network.

## Features

### 1. Node-Specific Analysis

**Purpose**: Provide detailed analysis for each network node with performance metrics and operational status.

**Key Metrics**:
- **Efficiency Score**: Performance rating based on water loss and operational metrics
- **Water Loss Percentage**: Percentage of water lost in the node
- **Pressure & Flow Rate**: Average operational parameters
- **User Count**: Number of users served by the node
- **Consumption Patterns**: Daily and monthly consumption data
- **Maintenance Schedule**: Last and next maintenance dates
- **Alert System**: Number of active alerts and operational status

**Data Structure**:
```typescript
interface NodeData {
  node_id: string;                    // Unique node identifier
  node_name: string;                  // Human-readable node name
  node_type: string;                  // main, secondary, industrial, etc.
  infrastructure_type: string;        // primary_distribution, secondary_distribution, etc.
  total_users: number;                // Number of users served
  daily_consumption_liters: number;   // Daily consumption in liters
  monthly_consumption_liters: number; // Monthly consumption in liters
  avg_per_user_daily: number;         // Average consumption per user
  peak_hour: number;                  // Hour of peak consumption
  efficiency_score: number;           // Performance efficiency (0-1)
  water_loss_percentage: number;      // Water loss percentage
  pressure_avg: number;               // Average pressure (bar)
  flow_rate_avg: number;              // Average flow rate (L/s)
  last_maintenance: string;           // Last maintenance date
  next_maintenance: string;           // Next maintenance date
  status: string;                     // operational, maintenance, offline
  alerts: number;                     // Number of active alerts
  performance_rating: string;         // excellent, good, fair, poor
}
```

### 2. Infrastructure Summary Dashboard

**Purpose**: Provide high-level overview of the entire network infrastructure.

**Summary Metrics**:
- **Total Nodes**: Complete count of network nodes
- **Node Type Distribution**: Breakdown by main, secondary, industrial
- **Operational Status**: Number of operational vs. non-operational nodes
- **User Coverage**: Total users served across the network
- **Average Efficiency**: Network-wide efficiency score
- **Maintenance Requirements**: Nodes requiring immediate attention

**Data Structure**:
```typescript
interface InfrastructureSummary {
  total_nodes: number;                // Total number of nodes
  main_nodes: number;                 // Primary distribution nodes
  secondary_nodes: number;            // Secondary distribution nodes
  industrial_nodes: number;           // Industrial supply nodes
  total_users_served: number;         // Total users across network
  total_daily_consumption: number;    // Total daily consumption
  avg_efficiency: number;             // Average efficiency score
  avg_water_loss: number;             // Average water loss percentage
  operational_nodes: number;          // Number of operational nodes
  maintenance_required: number;       // Nodes requiring maintenance
}
```

### 3. Infrastructure Types Analysis

**Purpose**: Analyze performance and characteristics by infrastructure type.

**Infrastructure Categories**:
- **Primary Distribution**: Main water distribution network
- **Secondary Distribution**: Secondary distribution network
- **Industrial Supply**: Industrial water supply network
- **Residential Distribution**: Residential water distribution
- **Commercial Distribution**: Commercial water distribution

**Analysis Metrics**:
- **Node Count**: Number of nodes per infrastructure type
- **User Coverage**: Total users served by each type
- **Consumption Patterns**: Daily consumption by type
- **Performance Metrics**: Efficiency, water loss, pressure, flow rate
- **Criticality Levels**: low, medium, high, critical
- **Maintenance Frequency**: Recommended maintenance intervals

**Data Structure**:
```typescript
interface InfrastructureType {
  type: string;                       // Infrastructure type identifier
  description: string;                // Human-readable description
  node_count: number;                 // Number of nodes
  total_users: number;                // Total users served
  daily_consumption: number;          // Daily consumption
  avg_efficiency: number;             // Average efficiency
  avg_water_loss: number;             // Average water loss
  avg_pressure: number;               // Average pressure
  avg_flow_rate: number;              // Average flow rate
  performance_rating: string;         // Performance rating
  maintenance_frequency_days: number; // Maintenance frequency
  criticality_level: string;          // Criticality level
}
```

## API Endpoints

### 1. Node Analysis Endpoint

```
GET /api/v1/consumption/node-analysis
```

**Response**:
```json
{
  "node_analysis": [
    {
      "node_id": "VIA_DANTE_1",
      "node_name": "Via Dante Principale",
      "node_type": "main",
      "infrastructure_type": "primary_distribution",
      "total_users": 25000,
      "daily_consumption_liters": 375000,
      "efficiency_score": 0.92,
      "water_loss_percentage": 8.0,
      "status": "operational",
      "alerts": 0,
      "performance_rating": "excellent"
    }
  ],
  "infrastructure_summary": {
    "total_nodes": 3,
    "operational_nodes": 3,
    "total_users_served": 45000,
    "avg_efficiency": 0.92
  },
  "data_metadata": {
    "is_real_time": false,
    "data_source": "Historical Database"
  }
}
```

### 2. Infrastructure Types Endpoint

```
GET /api/v1/consumption/infrastructure-types
```

**Response**:
```json
{
  "infrastructure_types": [
    {
      "type": "primary_distribution",
      "description": "Primary water distribution network",
      "node_count": 1,
      "total_users": 25000,
      "daily_consumption": 375000,
      "avg_efficiency": 0.92,
      "criticality_level": "high"
    }
  ],
  "data_metadata": {
    "is_real_time": false,
    "data_source": "Historical Database"
  }
}
```

## React Components

### NodeAnalysis Component

**Location**: `src/components/consumption/NodeAnalysis.tsx`

**Props**:
```typescript
interface NodeAnalysisProps {
  nodeAnalysis: NodeData[];
  infrastructureSummary: InfrastructureSummary;
  infrastructureTypes: InfrastructureType[];
  className?: string;
}
```

**Features**:
- **Interactive Table**: Sortable and filterable node data
- **Performance Indicators**: Visual performance ratings and alerts
- **Infrastructure Overview**: Summary cards with key metrics
- **Chart Visualizations**: Pie charts and bar charts for data analysis
- **Responsive Design**: Mobile-friendly interface
- **Dark Mode Support**: Consistent with application theme

### Usage Example

```typescript
import { NodeAnalysis } from '@/components/consumption/NodeAnalysis';
import { useNodeAnalysis, useInfrastructureTypes } from '@/hooks/useConsumptionData';

function InfrastructurePage() {
  const { data: nodeData } = useNodeAnalysis();
  const { data: infraData } = useInfrastructureTypes();

  if (!nodeData || !infraData) {
    return <div>Loading...</div>;
  }

  return (
    <NodeAnalysis
      nodeAnalysis={nodeData.node_analysis}
      infrastructureSummary={nodeData.infrastructure_summary}
      infrastructureTypes={infraData.infrastructure_types}
    />
  );
}
```

## Data Processing

### Backend Processing

The backend processes node data through several methods:

1. **Detailed Node Analysis** (`_create_detailed_node_analysis`)
   - Calculates performance metrics for each node
   - Determines infrastructure type based on node type
   - Computes efficiency scores and water loss percentages
   - Generates maintenance schedules and alert counts

2. **Infrastructure Summary** (`_create_infrastructure_summary`)
   - Aggregates data across all nodes
   - Calculates network-wide metrics
   - Identifies operational status and maintenance requirements

3. **Infrastructure Types Analysis** (`_create_infrastructure_types_analysis`)
   - Groups nodes by infrastructure type
   - Calculates type-specific performance metrics
   - Determines criticality levels and maintenance frequencies

### Performance Calculations

#### Efficiency Score
```python
def _calculate_efficiency_score(self, node_type: str) -> float:
    base_scores = {
        "main": 0.92,
        "secondary": 0.88,
        "industrial": 0.95,
        "residential": 0.90,
        "commercial": 0.87
    }
    return base_scores.get(node_type, 0.85)
```

#### Water Loss Percentage
```python
def _calculate_water_loss(self, node_type: str) -> float:
    loss_rates = {
        "main": 8.0,
        "secondary": 12.0,
        "industrial": 5.0,
        "residential": 10.0,
        "commercial": 15.0
    }
    return loss_rates.get(node_type, 10.0)
```

#### Performance Rating
```python
def _calculate_performance_rating(self, efficiency: float, water_loss: float) -> str:
    if efficiency >= 0.95 and water_loss <= 5:
        return "excellent"
    elif efficiency >= 0.90 and water_loss <= 10:
        return "good"
    elif efficiency >= 0.85 and water_loss <= 15:
        return "fair"
    else:
        return "poor"
```

## Infrastructure Types

### Primary Distribution
- **Purpose**: Main water distribution network
- **Characteristics**: High pressure, large flow rates
- **Criticality**: High
- **Maintenance**: Every 90 days
- **Typical Efficiency**: 92%

### Secondary Distribution
- **Purpose**: Secondary distribution network
- **Characteristics**: Medium pressure, moderate flow rates
- **Criticality**: Medium
- **Maintenance**: Every 90 days
- **Typical Efficiency**: 88%

### Industrial Supply
- **Purpose**: Industrial water supply network
- **Characteristics**: High pressure, very large flow rates
- **Criticality**: High
- **Maintenance**: Every 90 days
- **Typical Efficiency**: 95%

### Residential Distribution
- **Purpose**: Residential water distribution
- **Characteristics**: Low pressure, small flow rates
- **Criticality**: Medium
- **Maintenance**: Every 120 days
- **Typical Efficiency**: 90%

### Commercial Distribution
- **Purpose**: Commercial water distribution
- **Characteristics**: Medium pressure, moderate flow rates
- **Criticality**: Medium
- **Maintenance**: Every 90 days
- **Typical Efficiency**: 87%

## Alert System

### Alert Categories
- **Operational Alerts**: Performance below thresholds
- **Maintenance Alerts**: Scheduled maintenance due
- **Critical Alerts**: System failures or safety issues
- **Efficiency Alerts**: Water loss above acceptable levels

### Alert Calculation
```python
def _calculate_alerts(self, node_type: str, efficiency: float) -> int:
    base_alerts = {
        "main": 0,
        "secondary": 1,
        "industrial": 0,
        "residential": 2,
        "commercial": 1
    }
    
    # Add alerts based on efficiency
    if efficiency < 0.85:
        return base_alerts.get(node_type, 0) + 2
    elif efficiency < 0.90:
        return base_alerts.get(node_type, 0) + 1
    else:
        return base_alerts.get(node_type, 0)
```

## Maintenance Planning

### Maintenance Scheduling
- **Frequency**: Based on infrastructure type and criticality
- **Intervals**: 30-365 days depending on node type
- **Priority**: High criticality nodes have more frequent maintenance
- **Tracking**: Last and next maintenance dates for each node

### Maintenance Requirements
- **Immediate**: Nodes with critical alerts
- **Scheduled**: Nodes approaching maintenance dates
- **Preventive**: Nodes with declining performance metrics
- **Emergency**: Nodes with system failures

## Performance Monitoring

### Key Performance Indicators (KPIs)
1. **Efficiency Score**: Overall performance rating
2. **Water Loss Percentage**: Operational efficiency
3. **Pressure Consistency**: Network stability
4. **Flow Rate Stability**: Supply reliability
5. **User Satisfaction**: Service quality metrics

### Performance Thresholds
- **Excellent**: Efficiency ≥ 95%, Water Loss ≤ 5%
- **Good**: Efficiency ≥ 90%, Water Loss ≤ 10%
- **Fair**: Efficiency ≥ 85%, Water Loss ≤ 15%
- **Poor**: Efficiency < 85%, Water Loss > 15%

## Data Visualization

### Charts and Graphs
1. **Node Type Distribution**: Pie chart showing node distribution
2. **Infrastructure Performance**: Bar chart comparing efficiency by type
3. **Performance Trends**: Line charts for historical analysis
4. **Alert Distribution**: Heat maps for alert patterns

### Interactive Features
- **Filtering**: By node type, performance rating, status
- **Sorting**: By efficiency, consumption, alerts, users
- **Drill-down**: Detailed node information on click
- **Export**: Data export for reporting

## Integration Points

### Real-time Monitoring
- **Sensor Integration**: Real-time pressure and flow data
- **Alert System**: Immediate notification of issues
- **Status Updates**: Live operational status
- **Performance Tracking**: Continuous efficiency monitoring

### Reporting Integration
- **Maintenance Reports**: Scheduled maintenance summaries
- **Performance Reports**: Efficiency and loss analysis
- **Operational Reports**: Daily operational status
- **Compliance Reports**: Regulatory compliance data

## Future Enhancements

### Planned Features
1. **Predictive Maintenance**: AI-powered maintenance prediction
2. **Advanced Analytics**: Machine learning for performance optimization
3. **Geographic Visualization**: Map-based node representation
4. **Mobile Monitoring**: Mobile app for field operations

### Technical Improvements
1. **Real-time Updates**: WebSocket integration for live data
2. **Advanced Filtering**: Complex query capabilities
3. **Data Export**: Multiple format support (PDF, Excel, CSV)
4. **API Enhancements**: GraphQL for flexible data queries

## Testing

### Test Coverage
- **Data Validation**: Node data structure and integrity
- **Performance Metrics**: Accuracy of calculations
- **Alert System**: Proper alert generation and classification
- **UI Components**: Component rendering and interactions
- **API Endpoints**: Endpoint functionality and error handling

### Test Files
- `tests/presentation/frontend/test_node_analysis.py`
- Component unit tests
- Integration tests
- API endpoint tests
