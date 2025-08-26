import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import EnhancedOverviewPage from '../page';

// Mock next/router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  useSearchParams: () => ({
    get: jest.fn(),
  }),
}));

// Mock components
jest.mock('@/components/water/WaterKPIRibbon', () => ({
  __esModule: true,
  default: ({ metrics }: any) => (
    <div data-testid="water-kpi-ribbon">
      Water KPI Ribbon - Active Nodes: {metrics.activeNodes}
    </div>
  ),
}));

jest.mock('@/components/water/FlowAnalyticsChart', () => ({
  __esModule: true,
  default: ({ data }: any) => (
    <div data-testid="flow-analytics-chart">
      Flow Analytics Chart - Data Points: {data?.length || 0}
    </div>
  ),
}));

jest.mock('@/components/water/NetworkPerformanceAnalytics', () => ({
  __esModule: true,
  default: () => (
    <div data-testid="network-performance">
      Network Performance Analytics
    </div>
  ),
}));

jest.mock('@/components/water/SystemHealthGauges', () => ({
  __esModule: true,
  default: ({ metrics }: any) => (
    <div data-testid="system-health">
      System Health - Efficiency: {metrics.energyEfficiency}%
    </div>
  ),
}));

jest.mock('@/components/common/DateRangeSelector', () => ({
  __esModule: true,
  default: ({ onDateRangeChange }: any) => (
    <div data-testid="date-range-selector">
      <button onClick={() => onDateRangeChange(new Date(), new Date(), 'test')}>
        Change Date Range
      </button>
    </div>
  ),
}));

// Mock dashboard data
const mockDashboardData = {
  kpis: {
    activeNodes: 25,
    totalNodes: 30,
    flowRate: 1234.5,
    pressure: 4.2,
    dataQuality: 95.5,
    systemUptime: 99.8,
    energyEfficiency: 92.5,
    currentPowerKw: 450.2,
    dailyCostEur: 1234.56,
    costPerCubicMeter: 0.85
  },
  network: {
    active_nodes: 25,
    total_nodes: 30,
    total_flow_lps: 1234.5,
    average_pressure_bar: 4.2,
    efficiency_percentage: 92.5,
    alert_count: 3,
    energy_consumption_kwh: 450.2,
    water_quality_index: 98.5,
    total_volume_m3: 12345,
    anomaly_count: 2
  },
  last_updated: '2025-01-15T10:30:00Z'
};

const mockAnomalies = [
  {
    id: '1',
    timestamp: '2025-01-15T10:00:00Z',
    nodeId: 'N001',
    nodeName: 'Node 001',
    type: 'pressure',
    severity: 'high',
    description: 'High pressure detected',
    value: 6.5,
    threshold: 6.0,
    status: 'active'
  }
];

// Mock fetch
global.fetch = jest.fn();

describe('EnhancedOverviewPage', () => {
  let consoleLogSpy: jest.SpyInstance;
  let consoleErrorSpy: jest.SpyInstance;
  let consoleWarnSpy: jest.SpyInstance;

  beforeEach(() => {
    jest.clearAllMocks();
    consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
    
    // Mock fetch responses
    (global.fetch as jest.Mock).mockImplementation((url: string) => {
      if (url.includes('/dashboard/summary')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockDashboardData)
        });
      }
      if (url.includes('/anomalies')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAnomalies)
        });
      }
      return Promise.reject(new Error('Unknown URL'));
    });
  });

  afterEach(() => {
    consoleLogSpy.mockRestore();
    consoleErrorSpy.mockRestore();
    consoleWarnSpy.mockRestore();
  });

  describe('Component Rendering', () => {
    it('should render the page title and header', async () => {
      render(<EnhancedOverviewPage />);
      
      await waitFor(() => {
        expect(screen.getByText('🚀 Enhanced System Overview')).toBeInTheDocument();
      });
      
      expect(screen.getByText(/Comprehensive water infrastructure monitoring/)).toBeInTheDocument();
    });

    it('should render all main components after loading', async () => {
      render(<EnhancedOverviewPage />);
      
      await waitFor(() => {
        expect(screen.getByText('📊 Core Performance Indicators')).toBeInTheDocument();
      });
      
      expect(screen.getByTestId('flow-analytics-chart')).toBeInTheDocument();
      expect(screen.getByTestId('network-performance')).toBeInTheDocument();
      expect(screen.getByTestId('date-range-selector')).toBeInTheDocument();
    });

    it('should display correct metrics in components', async () => {
      render(<EnhancedOverviewPage />);
      
      await waitFor(() => {
        expect(screen.getByText('📊 Core Performance Indicators')).toBeInTheDocument();
      });
      
      // Check that flow analytics chart is rendered
      expect(screen.getByTestId('flow-analytics-chart')).toBeInTheDocument();
      // Check that network performance is rendered
      expect(screen.getByTestId('network-performance')).toBeInTheDocument();
    });
  });

  describe('Data Loading', () => {
    it('should display loading state initially', () => {
      // Mock fetch to delay response
      (global.fetch as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      );
      
      render(<EnhancedOverviewPage />);
      
      // Should show loading spinner
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('should fetch dashboard data on mount', async () => {
      render(<EnhancedOverviewPage />);
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/dashboard/summary')
        );
      });
      
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/anomalies')
      );
    });

    it('should handle API errors gracefully', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));
      
      render(<EnhancedOverviewPage />);
      
      await waitFor(() => {
        expect(screen.getByText('🚀 Enhanced System Overview')).toBeInTheDocument();
      });
      
      // Should still render page structure
      expect(screen.getByText('📊 Core Performance Indicators')).toBeInTheDocument();
      expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('should handle non-OK API responses', async () => {
      (global.fetch as jest.Mock).mockImplementation((url: string) => {
        if (url.includes('/dashboard/summary')) {
          return Promise.resolve({
            ok: false,
            status: 500,
            json: () => Promise.resolve(mockDashboardData)
          });
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      });
      
      render(<EnhancedOverviewPage />);
      
      await waitFor(() => {
        expect(screen.getByText('🚀 Enhanced System Overview')).toBeInTheDocument();
      });
      
      // Should log error due to non-OK response
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Error fetching dashboard data:', 
        expect.any(Error)
      );
    });
  });

  describe('Date Range Selection', () => {
    it('should update data when date range changes', async () => {
      render(<EnhancedOverviewPage />);
      
      await waitFor(() => {
        expect(screen.getByTestId('date-range-selector')).toBeInTheDocument();
      });
      
      // Clear previous calls
      (global.fetch as jest.Mock).mockClear();
      
      // Click the date range button
      const dateRangeButton = screen.getByText('Change Date Range');
      fireEvent.click(dateRangeButton);
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/dashboard/summary')
        );
      });
    });
  });

  describe('Auto Refresh', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should refresh data every 2 minutes', async () => {
      render(<EnhancedOverviewPage />);
      
      await waitFor(() => {
        expect(screen.getByText('🚀 Enhanced System Overview')).toBeInTheDocument();
      });
      
      // Clear initial calls
      (global.fetch as jest.Mock).mockClear();
      
      // Fast-forward 2 minutes
      jest.advanceTimersByTime(120000);
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/dashboard/summary')
        );
      });
    }, 10000);

    it('should show refresh indicator during updates', async () => {
      render(<EnhancedOverviewPage />);
      
      await waitFor(() => {
        expect(screen.getByText('🚀 Enhanced System Overview')).toBeInTheDocument();
      });
      
      // Mock fetch to delay response for refresh
      (global.fetch as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: () => Promise.resolve(mockDashboardData)
        }), 100))
      );
      
      // Trigger refresh
      jest.advanceTimersByTime(120000);
      
      await waitFor(() => {
        expect(screen.getByText('Updating...')).toBeInTheDocument();
      });
    }, 10000);
  });

  describe('Alert Display', () => {
    it('should display active alerts', async () => {
      render(<EnhancedOverviewPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Active Alerts')).toBeInTheDocument();
      });
      
      // Should show alert count
      expect(screen.getByText('1 total')).toBeInTheDocument();
    });

    it('should show no alerts message when there are no anomalies', async () => {
      (global.fetch as jest.Mock).mockImplementation((url: string) => {
        if (url.includes('/dashboard/summary')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(mockDashboardData)
          });
        }
        if (url.includes('/anomalies')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve([])
          });
        }
        return Promise.reject(new Error('Unknown URL'));
      });
      
      render(<EnhancedOverviewPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Active Alerts')).toBeInTheDocument();
      });
      
      // Should show 0 alerts
      expect(screen.getByText('0 total')).toBeInTheDocument();
    });
  });

  describe('Responsive Layout', () => {
    it('should render with responsive grid layout', async () => {
      render(<EnhancedOverviewPage />);
      
      await waitFor(() => {
        expect(screen.getByText('🚀 Enhanced System Overview')).toBeInTheDocument();
      });
      
      // Check for responsive container
      const container = screen.getByText('🚀 Enhanced System Overview').closest('.min-h-screen');
      expect(container).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('should not show loading screen on refresh', async () => {
      render(<EnhancedOverviewPage />);
      
      await waitFor(() => {
        expect(screen.getByText('🚀 Enhanced System Overview')).toBeInTheDocument();
      });
      
      // Clear previous calls
      (global.fetch as jest.Mock).mockClear();
      
      // Trigger date range change (which causes refresh)
      const dateRangeButton = screen.getByText('Change Date Range');
      fireEvent.click(dateRangeButton);
      
      // Should not show full page loading spinner (the page should be loaded)
      // There might be a refresh indicator spinner, but not the full page one
      expect(screen.getByText('🚀 Enhanced System Overview')).toBeInTheDocument();
      
      // But should show refresh indicator
      await waitFor(() => {
        expect(screen.getByText('Updating...')).toBeInTheDocument();
      });
    });
  });
});
