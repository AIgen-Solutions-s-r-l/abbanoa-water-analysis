import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ConsumptionAnalyticsPage from '../page';

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

// Mock Card components
jest.mock('@/components/ui/Card', () => ({
  Card: ({ children, className }: any) => <div className={className}>{children}</div>,
}));

jest.mock('@/components/ui/Button', () => ({
  Button: ({ children, onClick, variant }: any) => (
    <button onClick={onClick} className={variant}>{children}</button>
  ),
}));

// Mock fetch globally
global.fetch = jest.fn();

describe('ConsumptionAnalyticsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Error Handling for Missing Data', () => {
    it('should handle undefined analyticsData gracefully', async () => {
      // Arrange - Mock API to return undefined
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => undefined,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ anomalies: [] }),
      });

      // Act
      render(<ConsumptionAnalyticsPage />);

      // Assert - Should show error message instead of crashing
      await waitFor(() => {
        expect(screen.getByText('Error loading consumption data')).toBeInTheDocument();
      });
    });

    it('should handle missing summary property in analyticsData', async () => {
      // Arrange - Mock API to return data without summary
      const mockDataWithoutSummary = {
        district_consumption: [],
        consumption_timeline: [],
        user_segments: [],
        peak_demand: {
          daily_peak_time: '18:00',
          daily_peak_consumption: 1000,
          weekly_peak_day: 'Friday',
          monthly_peak_date: '2025-01-15',
          seasonal_peak_month: 'July'
        },
        conservation_opportunities: []
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockDataWithoutSummary,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ anomalies: [] }),
      });

      // Act
      render(<ConsumptionAnalyticsPage />);

      // Assert - Should show error or fallback values
      await waitFor(() => {
        // Component should render without crashing
        expect(screen.getByText('Consumption Analytics')).toBeInTheDocument();
        // Should show fallback or error state for missing summary data
        expect(screen.queryByText(/Daily Consumption/)).toBeInTheDocument();
        // Should not crash when trying to access undefined properties
      });
    });

    it('should handle partial summary data', async () => {
      // Arrange - Mock API to return partial summary
      const mockDataWithPartialSummary = {
        summary: {
          total_users: 1000,
          // Missing other properties like total_daily_consumption
        },
        district_consumption: [],
        consumption_timeline: [],
        user_segments: [],
        peak_demand: {
          daily_peak_time: '18:00',
          daily_peak_consumption: 1000,
          weekly_peak_day: 'Friday',
          monthly_peak_date: '2025-01-15',
          seasonal_peak_month: 'July'
        },
        conservation_opportunities: []
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockDataWithPartialSummary,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ anomalies: [] }),
      });

      // Act
      render(<ConsumptionAnalyticsPage />);

      // Assert
      await waitFor(() => {
        expect(screen.getByText('Consumption Analytics')).toBeInTheDocument();
        // Should show the available data
        expect(screen.getByText('Total Users')).toBeInTheDocument();
        // Should handle missing properties gracefully
        expect(screen.queryByText(/Daily Consumption/)).toBeInTheDocument();
      });
    });
  });

  describe('Valid Data Rendering', () => {
    const mockValidAnalyticsData = {
      summary: {
        total_daily_consumption: 150000,
        total_monthly_consumption: 4500000,
        total_users: 10000,
        avg_consumption_per_user: 15,
        system_efficiency: 0.85,
        water_loss_percentage: 15
      },
      district_consumption: [
        {
          district_id: 'D1',
          district_name: 'District 1',
          total_users: 5000,
          daily_consumption_liters: 75000,
          monthly_consumption_liters: 2250000,
          avg_per_user_daily: 15,
          peak_hour: 18,
          efficiency_score: 0.9
        }
      ],
      consumption_timeline: [
        {
          timestamp: '2025-01-01T10:00:00Z',
          consumption_liters: 6000,
          forecast_consumption: 5800
        }
      ],
      user_segments: [
        {
          segment: 'Residential',
          user_count: 8000,
          percentage: 80,
          avg_daily_consumption: 12,
          trend: 'stable'
        }
      ],
      peak_demand: {
        daily_peak_time: '18:00',
        daily_peak_consumption: 10000,
        weekly_peak_day: 'Friday',
        monthly_peak_date: '2025-01-15',
        seasonal_peak_month: 'July'
      },
      conservation_opportunities: [
        {
          opportunity: 'Leak Detection',
          potential_savings_liters_daily: 5000,
          potential_savings_percentage: 3,
          implementation_cost: 'Low',
          roi_months: 6
        }
      ]
    };

    it('should render all KPI cards with valid data', async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockValidAnalyticsData,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ anomalies: [] }),
      });

      // Act
      render(<ConsumptionAnalyticsPage />);

      // Assert
      await waitFor(() => {
        expect(screen.getByText('Daily Consumption')).toBeInTheDocument();
        expect(screen.getByText('150K L')).toBeInTheDocument();
        expect(screen.getByText('Total Users')).toBeInTheDocument();
        expect(screen.getByText('10K')).toBeInTheDocument();
        expect(screen.getByText('System Efficiency')).toBeInTheDocument();
        expect(screen.getByText('85.0%')).toBeInTheDocument();
        expect(screen.getByText('Peak Demand')).toBeInTheDocument();
        expect(screen.getByText('18:00')).toBeInTheDocument();
      });
    });
  });

  describe('Tab Navigation', () => {
    it('should switch between tabs correctly', async () => {
      // Arrange
      const mockData = {
        summary: {
          total_daily_consumption: 150000,
          total_monthly_consumption: 4500000,
          total_users: 10000,
          avg_consumption_per_user: 15,
          system_efficiency: 0.85,
          water_loss_percentage: 15
        },
        district_consumption: [],
        consumption_timeline: [],
        user_segments: [],
        peak_demand: {
          daily_peak_time: '18:00',
          daily_peak_consumption: 10000,
          weekly_peak_day: 'Friday',
          monthly_peak_date: '2025-01-15',
          seasonal_peak_month: 'July'
        },
        conservation_opportunities: []
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockData,
      });

      // Act
      render(<ConsumptionAnalyticsPage />);

      await waitFor(() => {
        expect(screen.getByText('Overview')).toBeInTheDocument();
      });

      // Click on Districts tab
      fireEvent.click(screen.getByText('Districts'));

      // Assert
      await waitFor(() => {
        expect(screen.getByText('District-wise Consumption Analysis')).toBeInTheDocument();
      });
    });
  });
});
