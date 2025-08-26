import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import EnhancedOverviewPage from '../page';

// Mock the components
jest.mock('@/components/water/WaterKPIRibbon', () => ({
  __esModule: true,
  default: () => <div data-testid="water-kpi-ribbon">Water KPI Ribbon</div>,
}));

jest.mock('@/components/water/FlowAnalyticsChart', () => ({
  __esModule: true,
  default: () => <div data-testid="flow-analytics-chart">Flow Analytics Chart</div>,
}));

jest.mock('@/components/water/NetworkPerformanceAnalytics', () => ({
  __esModule: true,
  default: () => <div data-testid="network-performance">Network Performance</div>,
}));

jest.mock('@/components/water/SystemHealthGauges', () => ({
  __esModule: true,
  default: () => <div data-testid="system-health">System Health</div>,
}));

jest.mock('@/components/common/DateRangeSelector', () => ({
  __esModule: true,
  default: ({ onDateRangeChange }: any) => (
    <div data-testid="date-range-selector">Date Range Selector</div>
  ),
}));

describe('EnhancedOverviewPage', () => {
  let originalFetch: typeof global.fetch;
  let consoleErrorSpy: jest.SpyInstance;
  let consoleWarnSpy: jest.SpyInstance;

  beforeEach(() => {
    originalFetch = global.fetch;
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(() => {
    global.fetch = originalFetch;
    consoleErrorSpy.mockRestore();
    consoleWarnSpy.mockRestore();
    jest.clearAllMocks();
  });

  it('should handle successful dashboard data fetch', async () => {
    const mockDashboardData = {
      kpis: {
        total_flow: 450.5,
        average_pressure: 3.2,
        water_quality_index: 95.0,
        energy_consumption: {
          pump_efficiency_percent: 75,
          current_power_kw: 125.5,
          daily_cost_eur: 150.25,
          cost_per_cubic_meter: 0.125,
        },
      },
      nodes: [
        { id: 'NODE1', name: 'Node 1', flow_rate: 10, pressure: 3 },
        { id: 'NODE2', name: 'Node 2', flow_rate: 15, pressure: 3.5 },
      ],
    };

    const mockAnomalies = [
      {
        id: '1',
        severity: 'high',
        anomaly_type: 'High Flow',
        description: 'Unusual flow detected',
        node_id: 'NODE1',
        timestamp: new Date().toISOString(),
        resolved_at: null,
      },
    ];

    global.fetch = jest.fn((url: string) => {
      console.log('Mock fetch called with URL:', url);
      if (typeof url === 'string' && url.includes('/api/proxy/v1/dashboard/summary')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          headers: {
            get: (key: string) => key === 'content-type' ? 'application/json' : null,
          },
          json: () => Promise.resolve(mockDashboardData),
        } as unknown as Response);
      }
      if (typeof url === 'string' && url.includes('/api/proxy/v1/anomalies')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          headers: {
            get: (key: string) => key === 'content-type' ? 'application/json' : null,
          },
          json: () => Promise.resolve(mockAnomalies),
        } as unknown as Response);
      }
      return Promise.reject(new Error('Unknown URL'));
    });

    render(<EnhancedOverviewPage />);

    // Should show loading state initially
    expect(screen.getByText('Loading real-time data...')).toBeInTheDocument();

    // Wait for data to load
    await waitFor(() => {
      expect(screen.queryByText('Loading real-time data...')).not.toBeInTheDocument();
    });

    // Check that the page renders with data
    expect(screen.getByText('🚀 Enhanced System Overview')).toBeInTheDocument();
    expect(screen.getByText('450.5')).toBeInTheDocument(); // Flow rate
    expect(screen.getByText('3.2')).toBeInTheDocument(); // Pressure
  });

  it('should handle dashboard data fetch error with non-OK response', async () => {
    const mockDashboardData = {
      kpis: {
        total_flow: 450.5,
        average_pressure: 3.2,
        water_quality_index: 95.0,
      },
      nodes: [],
    };

    // Simulate a response with data but non-OK status (like 500)
    global.fetch = jest.fn((url: string) => {
      if (typeof url === 'string' && url.includes('/api/proxy/v1/dashboard/summary')) {
        return Promise.resolve({
          ok: false,
          status: 500,
          headers: {
            get: (key: string) => key === 'content-type' ? 'application/json' : null,
          },
          json: () => Promise.resolve(mockDashboardData),
        } as unknown as Response);
      }
      if (typeof url === 'string' && url.includes('/api/proxy/v1/anomalies')) {
        return Promise.resolve({
          ok: true,
          headers: {
            get: (key: string) => key === 'content-type' ? 'application/json' : null,
          },
          json: () => Promise.resolve([]),
        } as unknown as Response);
      }
      return Promise.reject(new Error('Unknown URL'));
    });

    render(<EnhancedOverviewPage />);

    await waitFor(() => {
      expect(screen.queryByText('Loading real-time data...')).not.toBeInTheDocument();
    });

    // Should still render with the data from the error response
    expect(screen.getByText('🚀 Enhanced System Overview')).toBeInTheDocument();
    
    // Since we now handle error responses gracefully, no error is logged but a warning is
    expect(consoleErrorSpy).not.toHaveBeenCalled();
    expect(consoleWarnSpy).toHaveBeenCalledWith(
      'Dashboard API returned status 500, but attempting to use data if available'
    );
  });

  it('should handle complete fetch failure', async () => {
    global.fetch = jest.fn(() => Promise.reject(new Error('Network error')));

    render(<EnhancedOverviewPage />);

    await waitFor(() => {
      expect(screen.queryByText('Loading real-time data...')).not.toBeInTheDocument();
    });

    // Should still render with fallback data
    expect(screen.getByText('🚀 Enhanced System Overview')).toBeInTheDocument();
    
    // Check that error was logged
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'Error fetching dashboard data:',
      expect.any(Error)
    );
  });

  it('should handle null dashboard data gracefully', async () => {
    global.fetch = jest.fn((url: string) => {
      if (typeof url === 'string' && url.includes('/api/proxy/v1/dashboard/summary')) {
        return Promise.resolve({
          ok: true,
          headers: {
            get: (key: string) => key === 'content-type' ? 'application/json' : null,
          },
          json: () => Promise.resolve(null),
        } as unknown as Response);
      }
      if (typeof url === 'string' && url.includes('/api/proxy/v1/anomalies')) {
        return Promise.resolve({
          ok: true,
          headers: {
            get: (key: string) => key === 'content-type' ? 'application/json' : null,
          },
          json: () => Promise.resolve([]),
        } as unknown as Response);
      }
      return Promise.reject(new Error('Unknown URL'));
    });

    render(<EnhancedOverviewPage />);

    await waitFor(() => {
      expect(screen.queryByText('Loading real-time data...')).not.toBeInTheDocument();
    });

    // Should render with default values
    expect(screen.getByText('🚀 Enhanced System Overview')).toBeInTheDocument();
    // Check for specific text showing 0 active nodes
    expect(screen.getByText('Active Nodes')).toBeInTheDocument();
  });
});
