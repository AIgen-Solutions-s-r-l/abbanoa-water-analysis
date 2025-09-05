# Temporal Charts and Trend Analysis

This document describes the temporal charts and trend analysis functionality for consumption analytics.

## Overview

The temporal charts system provides comprehensive time-based visualization of water consumption patterns, including hourly patterns, trend analysis, and forecasting capabilities.

## Features

### 1. 24-Hour Consumption Pattern Chart

**Purpose**: Visualize daily consumption patterns across all 24 hours.

**Chart Type**: Bar Chart with peak hour highlighting

**Data Structure**:
```typescript
interface HourlyPattern {
  hour: number;                    // 0-23
  avg_consumption: number;         // Average consumption in liters
  peak_hour: boolean;             // Whether this is a peak hour
  hour_label: string;             // Formatted hour (e.g., "08:00")
  consumption_formatted: string;   // Formatted consumption (e.g., "75K L")
}
```

**Visual Features**:
- Blue bars for normal hours
- Red bars for peak hours
- Interactive tooltips with detailed information
- Responsive design for mobile and desktop

### 2. Consumption Timeline with Forecast

**Purpose**: Show consumption trends over time with forecasting.

**Chart Type**: Area Chart with dual data series

**Data Structure**:
```typescript
interface TimelineData {
  timestamp: string;              // ISO timestamp
  consumption_liters: number;     // Actual consumption
  forecast_consumption: number;   // Predicted consumption
}
```

**Visual Features**:
- Blue area for actual consumption
- Green area for forecast consumption
- Interactive tooltips showing both values
- Time-based X-axis with proper formatting

### 3. Trend Analysis Dashboard

**Purpose**: Provide comprehensive trend insights and statistics.

**Components**:
- Trend direction indicator (increasing/decreasing/stable)
- Growth rate percentage
- Peak and valley hour analysis
- Daily variance calculation
- Seasonal trend information

**Data Structure**:
```typescript
interface TrendAnalysis {
  growth_rate: number;            // Percentage growth
  trend_direction: 'increasing' | 'decreasing' | 'stable';
  peak_hour: number;             // Hour of peak consumption (0-23)
  valley_hour: number;           // Hour of lowest consumption (0-23)
  daily_variance: number;        // Variance percentage
  seasonal_trend: string;        // Seasonal pattern description
  avg_daily_consumption: number; // Average daily consumption
  peak_consumption: number;      // Peak hour consumption
  valley_consumption: number;    // Valley hour consumption
}
```

## API Endpoints

### 1. Hourly Pattern Endpoint

```
GET /api/v1/consumption/hourly-pattern
```

**Response**:
```json
{
  "hourly_pattern": [
    {
      "hour": 0,
      "avg_consumption": 62500,
      "peak_hour": false,
      "hour_label": "00:00",
      "consumption_formatted": "62.5K L"
    }
  ],
  "data_metadata": {
    "is_real_time": false,
    "data_source": "Historical Database"
  }
}
```

### 2. Trend Analysis Endpoint

```
GET /api/v1/consumption/trend-analysis
```

**Response**:
```json
{
  "trend_analysis": {
    "growth_rate": 2.5,
    "trend_direction": "increasing",
    "peak_hour": 8,
    "valley_hour": 4,
    "daily_variance": 35.2,
    "seasonal_trend": "stable",
    "avg_daily_consumption": 1500000,
    "peak_consumption": 75000,
    "valley_consumption": 45000
  },
  "data_metadata": {
    "is_real_time": false,
    "data_source": "Historical Database"
  }
}
```

## React Components

### TemporalCharts Component

**Location**: `src/components/consumption/TemporalCharts.tsx`

**Props**:
```typescript
interface TemporalChartsProps {
  timelineData: TimelineData[];
  hourlyPattern: HourlyPattern[];
  trendAnalysis: TrendAnalysis;
  className?: string;
}
```

**Features**:
- Responsive design with Tailwind CSS
- Dark mode support
- Interactive tooltips
- Custom color schemes
- Accessibility features

### Usage Example

```typescript
import { TemporalCharts } from '@/components/consumption/TemporalCharts';
import { useConsumptionData, useHourlyPattern, useTrendAnalysis } from '@/hooks/useConsumptionData';

function ConsumptionPage() {
  const { data: analyticsData } = useConsumptionData();
  const { data: hourlyData } = useHourlyPattern();
  const { data: trendData } = useTrendAnalysis();

  if (!analyticsData || !hourlyData || !trendData) {
    return <div>Loading...</div>;
  }

  return (
    <TemporalCharts
      timelineData={analyticsData.consumption_timeline}
      hourlyPattern={hourlyData.hourly_pattern}
      trendAnalysis={trendData.trend_analysis}
    />
  );
}
```

## Data Processing

### Backend Processing

The backend processes temporal data through several methods:

1. **Hourly Pattern Creation** (`_create_hourly_pattern_for_charts`)
   - Aggregates consumption data by hour
   - Identifies peak hours based on maximum consumption
   - Formats data for chart visualization

2. **Trend Analysis** (`_create_trend_analysis`)
   - Calculates growth rates and trend directions
   - Identifies peak and valley hours
   - Computes daily variance and seasonal patterns

3. **Timeline Creation** (`_create_consumption_timeline`)
   - Creates 24-hour timeline with actual and forecast data
   - Handles missing data points gracefully
   - Ensures chronological order

### Frontend Processing

The frontend processes data for visualization:

1. **Chart Data Formatting**
   - Converts timestamps to readable time formats
   - Formats consumption numbers (K, M, L)
   - Prepares data for Recharts components

2. **Interactive Features**
   - Custom tooltips with detailed information
   - Color coding for peak vs normal hours
   - Responsive chart sizing

## Chart Libraries

### Recharts

The temporal charts use Recharts for visualization:

- **BarChart**: For 24-hour consumption pattern
- **AreaChart**: For timeline with forecast
- **ResponsiveContainer**: For responsive design
- **Custom Tooltips**: For enhanced user experience

### Features Used

- **CartesianGrid**: For better readability
- **XAxis/YAxis**: With custom formatters
- **Tooltip**: Custom tooltips with detailed information
- **Legend**: For data series identification
- **Cell**: For individual bar coloring

## Styling

### Color Scheme

- **Primary Blue**: `#3b82f6` - Normal consumption
- **Peak Red**: `#ef4444` - Peak hours
- **Forecast Green**: `#10b981` - Forecast data
- **Trend Colors**: Green (increasing), Red (decreasing), Gray (stable)

### Responsive Design

- Mobile-first approach
- Breakpoints for tablet and desktop
- Flexible chart containers
- Touch-friendly interactions

## Performance Considerations

### Data Optimization

- Efficient data aggregation on backend
- Minimal data transfer between API and frontend
- Caching of processed data
- Lazy loading of chart components

### Rendering Optimization

- Virtual scrolling for large datasets
- Debounced chart updates
- Efficient re-rendering with React hooks
- Optimized chart configurations

## Testing

### Test Coverage

The temporal charts include comprehensive tests:

1. **Data Structure Tests**
   - Verify correct data types
   - Validate required fields
   - Check data ranges

2. **Chart Functionality Tests**
   - Test chart rendering
   - Verify interactive features
   - Validate responsive behavior

3. **Integration Tests**
   - API endpoint testing
   - Component integration
   - Data flow validation

### Test Files

- `tests/presentation/frontend/test_temporal_charts.py`
- Component unit tests
- Integration tests

## Future Enhancements

### Planned Features

1. **Advanced Forecasting**
   - Machine learning-based predictions
   - Seasonal pattern recognition
   - Anomaly detection

2. **Interactive Features**
   - Date range selection
   - Drill-down capabilities
   - Export functionality

3. **Real-time Updates**
   - WebSocket integration
   - Live data streaming
   - Real-time alerts

4. **Advanced Analytics**
   - Statistical analysis
   - Correlation studies
   - Predictive modeling

### Technical Improvements

1. **Performance**
   - WebGL rendering for large datasets
   - Server-side rendering optimization
   - Caching strategies

2. **Accessibility**
   - Screen reader support
   - Keyboard navigation
   - High contrast modes

3. **Mobile Experience**
   - Touch gestures
   - Mobile-optimized charts
   - Offline capabilities
