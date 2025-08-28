# Consumption Analytics Integration

This document describes the integration of real consumption analytics data into the Next.js frontend.

## Overview

The consumption analytics integration provides real-time access to water consumption data from the backend API, replacing mock data with actual database information.

## Architecture

### Backend API Endpoints

The following API endpoints are available for consumption analytics:

- `GET /api/v1/consumption/analytics` - Comprehensive consumption data
- `GET /api/v1/consumption/summary` - Summary metrics only
- `GET /api/v1/consumption/districts` - District-specific data
- `GET /api/v1/consumption/timeline` - 24-hour consumption timeline
- `GET /api/v1/consumption/segments` - User segmentation data
- `GET /api/v1/consumption/peak-demand` - Peak demand analysis
- `GET /api/v1/consumption/conservation` - Conservation opportunities

### Frontend Components

#### Services

- `src/services/consumption.service.ts` - Main service for API communication
- Provides TypeScript interfaces for all data structures
- Handles error handling and data formatting
- Supports environment-based configuration

#### Hooks

- `src/hooks/useConsumptionData.ts` - React hooks for data fetching
- Provides loading states and error handling
- Supports auto-refresh functionality
- Individual hooks for different data types

#### Components

- `src/components/consumption/ConsumptionDashboard.tsx` - Main dashboard component
- Displays real consumption data with proper formatting
- Shows data freshness indicators
- Responsive design with Tailwind CSS

## Data Structure

### ConsumptionAnalytics Interface

```typescript
interface ConsumptionAnalytics {
  data_metadata: {
    total_readings: number;
    active_nodes: number;
    is_real_time: boolean;
    data_source: string;
    latest_timestamp: string;
    earliest_timestamp: string;
    flow_readings: number;
    synthetic_percentage: number;
    data_age_hours: number;
  };
  summary: {
    total_daily_consumption: number;
    total_monthly_consumption: number;
    total_users: number;
    avg_consumption_per_user: number;
    system_efficiency: number;
    water_loss_percentage: number;
  };
  district_consumption: Array<{
    district_id: string;
    district_name: string;
    node_type: string;
    total_users: number;
    daily_consumption_liters: number;
    monthly_consumption_liters: number;
    avg_per_user_daily: number;
    peak_hour: number;
    efficiency_score: number;
  }>;
  consumption_timeline: Array<{
    timestamp: string;
    consumption_liters: number;
    forecast_consumption: number;
  }>;
  user_segments: Array<{
    segment: string;
    user_count: number;
    percentage: number;
    avg_daily_consumption: number;
    trend: string;
  }>;
  peak_demand: {
    daily_peak_time: string;
    daily_peak_consumption: number;
    weekly_peak_day: string;
    monthly_peak_date: string;
    seasonal_peak_month: string;
  };
  conservation_opportunities: Array<{
    opportunity: string;
    potential_savings_liters_daily: number;
    potential_savings_percentage: number;
    implementation_cost: string;
    roi_months: number;
  }>;
}
```

## Usage

### Basic Usage

```typescript
import { useConsumptionData } from '@/hooks/useConsumptionData';
import { ConsumptionDashboard } from '@/components/consumption/ConsumptionDashboard';

function MyPage() {
  const { data, loading, error, refresh } = useConsumptionData();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return <ConsumptionDashboard />;
}
```

### Service Usage

```typescript
import { consumptionService } from '@/services/consumption.service';

// Fetch all consumption data
const analytics = await consumptionService.getConsumptionAnalytics();

// Format numbers for display
const formatted = consumptionService.formatConsumptionNumber(1500000); // "1.5M L"

// Get data freshness
const freshness = consumptionService.getDataFreshness(analytics.data_metadata);
```

## Configuration

### Environment Variables

Create a `.env.local` file in the frontend directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Development Settings
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_DEBUG_MODE=true

# Feature Flags
NEXT_PUBLIC_ENABLE_REAL_TIME_UPDATES=true
NEXT_PUBLIC_ENABLE_CONSUMPTION_ANALYTICS=true
```

### API URL Configuration

The service automatically uses the `NEXT_PUBLIC_API_URL` environment variable or defaults to `http://localhost:8000/api/v1` for local development.

## Features

### Real Data Integration

- ✅ Connects to real PostgreSQL database
- ✅ Uses actual sensor readings from 41,704+ data points
- ✅ Displays real district information (Via Dante, Via Roma, etc.)
- ✅ Shows actual consumption patterns and trends

### Data Freshness

- ✅ Real-time data indicators
- ✅ Data age tracking (hours/days)
- ✅ Source information (Historical Database)
- ✅ Quality metrics (100% real data)

### Error Handling

- ✅ Graceful API error handling
- ✅ Loading states for better UX
- ✅ Retry functionality
- ✅ Fallback displays for missing data

### Responsive Design

- ✅ Mobile-friendly layout
- ✅ Tailwind CSS styling
- ✅ Dark mode support
- ✅ Accessible components

## Testing

### Unit Tests

Run the integration tests:

```bash
# From the project root
python -m pytest tests/presentation/frontend/test_consumption_dashboard_integration.py -v
```

### Frontend Tests

```bash
# From the frontend directory
npm test
```

## Development

### Adding New Endpoints

1. Add the endpoint to the backend API
2. Add the method to `ConsumptionService`
3. Create a new hook in `useConsumptionData.ts`
4. Update the TypeScript interfaces
5. Add tests for the new functionality

### Styling

The components use Tailwind CSS classes and follow the existing design system. Icons are from Lucide React.

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check if the backend server is running
   - Verify the `NEXT_PUBLIC_API_URL` environment variable
   - Check network connectivity

2. **Data Not Loading**
   - Verify the database has data
   - Check browser console for errors
   - Ensure the API endpoints are accessible

3. **TypeScript Errors**
   - Run `npm run type-check` to identify issues
   - Update interfaces if API response structure changes

### Debug Mode

Enable debug mode by setting `NEXT_PUBLIC_DEBUG_MODE=true` to see detailed console logs.

## Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Advanced filtering and search
- [ ] Export functionality
- [ ] Custom date range selection
- [ ] Comparative analytics
- [ ] Alert system for anomalies
