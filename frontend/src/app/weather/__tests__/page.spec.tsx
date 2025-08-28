import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import WeatherAnalyticsPage from '../page';

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

describe('WeatherAnalyticsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      // Arrange - Mock API to return error
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      // Act
      render(<WeatherAnalyticsPage />);

      // Assert - Should show loading initially, then handle error gracefully
      expect(screen.getByText('Weather Analytics')).toBeInTheDocument();
      
      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.queryByText(/Loading/)).not.toBeInTheDocument();
      });
    });

    it('should handle missing weather data gracefully', async () => {
      // Arrange - Mock API to return empty data
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => null,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => null,
      });

      // Act
      render(<WeatherAnalyticsPage />);

      // Assert - Should render without crashing
      await waitFor(() => {
        expect(screen.getByText('Weather Analytics')).toBeInTheDocument();
        expect(screen.getByText('Real-time weather monitoring and impact analysis')).toBeInTheDocument();
      });
    });

    it('should handle undefined statistics gracefully', async () => {
      // Arrange - Mock API to return undefined statistics
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => undefined,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => null,
      });

      // Act
      render(<WeatherAnalyticsPage />);

      // Assert - Should render without crashing
      await waitFor(() => {
        expect(screen.getByText('Weather Analytics')).toBeInTheDocument();
      });
    });
  });

  describe('Cagliari Weather Data', () => {
    const mockCagliariLocations = [
      { location: 'Cagliari', dataPoints: 1000, dateRange: { start: '2024-11-01', end: '2025-06-30' } },
      { location: 'Selargius', dataPoints: 950, dateRange: { start: '2024-11-01', end: '2025-06-30' } },
      { location: 'Quartucciu', dataPoints: 920, dateRange: { start: '2024-11-01', end: '2025-06-30' } },
      { location: 'Elmas', dataPoints: 880, dateRange: { start: '2024-11-01', end: '2025-06-30' } }
    ];

    const mockCurrentWeather = [
      {
        location: 'Cagliari',
        date: '2025-08-28',
        temperature: { current: 25.5, min: 20.2, max: 30.1 },
        humidity: 65,
        rainfall: 0,
        windSpeed: 12,
        conditions: 'Clear'
      },
      {
        location: 'Selargius',
        date: '2025-08-28',
        temperature: { current: 24.8, min: 19.5, max: 29.3 },
        humidity: 68,
        rainfall: 0.5,
        windSpeed: 10,
        conditions: 'Light Rain'
      }
    ];

    const mockHistoricalData = [
      {
        date: '2025-08-25',
        avg_temperature_c: 24.2,
        min_temperature_c: 19.1,
        max_temperature_c: 29.3,
        humidity_percent: 62,
        rainfall_mm: 0,
        avg_wind_speed_kmh: 15
      },
      {
        date: '2025-08-26',
        avg_temperature_c: 25.8,
        min_temperature_c: 20.3,
        max_temperature_c: 31.2,
        humidity_percent: 58,
        rainfall_mm: 0,
        avg_wind_speed_kmh: 12
      }
    ];

    const mockStatistics = {
      overview: {
        totalDays: 30,
        averageTemperature: 23.5,
        temperatureRange: { min: 15.2, max: 32.1 },
        totalRainfall: 45.2,
        averageDailyRainfall: 1.5,
        rainyDays: 8,
        dryDays: 22
      },
      seasonalPatterns: [
        { month: 1, avgTemperature: 12.5, totalRainfall: 85.3 },
        { month: 2, avgTemperature: 13.2, totalRainfall: 78.1 },
        { month: 3, avgTemperature: 15.8, totalRainfall: 65.4 }
      ]
    };

    const mockImpactAnalysis = {
      temperatureImpact: [
        { range: 'Cold (<10°C)', days: 45, relativeConsumption: 85, unit: '%' },
        { range: 'Cool (10-15°C)', days: 90, relativeConsumption: 95, unit: '%' },
        { range: 'Mild (15-20°C)', days: 120, relativeConsumption: 100, unit: '%' },
        { range: 'Warm (20-25°C)', days: 60, relativeConsumption: 115, unit: '%' },
        { range: 'Hot (>25°C)', days: 50, relativeConsumption: 130, unit: '%' }
      ],
      rainfallImpact: [
        { category: 'Dry Days', days: 200, systemEfficiency: 98, unit: '%' },
        { category: 'Light Rain', days: 100, systemEfficiency: 95, unit: '%' },
        { category: 'Moderate Rain', days: 50, systemEfficiency: 90, unit: '%' },
        { category: 'Heavy Rain', days: 15, systemEfficiency: 85, unit: '%' }
      ],
      recommendations: [
        {
          condition: 'High Temperature Alert',
          impact: 'Water demand increases by 15-30% during hot weather',
          action: 'Activate peak demand protocols and increase reservoir levels'
        }
      ]
    };

    it('should display Cagliari and district locations', async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockCagliariLocations,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => mockCurrentWeather,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => mockHistoricalData,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => mockStatistics,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => mockImpactAnalysis,
      });

      // Act
      render(<WeatherAnalyticsPage />);

      // Assert
      await waitFor(() => {
        expect(screen.getByText('Weather Analytics')).toBeInTheDocument();
        expect(screen.getByText('Cagliari')).toBeInTheDocument();
        expect(screen.getByText('Selargius')).toBeInTheDocument();
        expect(screen.getByText('Quartucciu')).toBeInTheDocument();
        expect(screen.getByText('Elmas')).toBeInTheDocument();
      });
    });

    it('should display current weather for Cagliari', async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockCagliariLocations,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => mockCurrentWeather,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => mockHistoricalData,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => mockStatistics,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => mockImpactAnalysis,
      });

      // Act
      render(<WeatherAnalyticsPage />);

      // Assert
      await waitFor(() => {
        expect(screen.getByText('25.5°C')).toBeInTheDocument();
        expect(screen.getByText('20.2° / 30.1°')).toBeInTheDocument();
        expect(screen.getByText('65%')).toBeInTheDocument();
        expect(screen.getByText('0mm')).toBeInTheDocument();
        expect(screen.getByText('12km/h')).toBeInTheDocument();
      });
    });

    it('should display weather statistics correctly', async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockCagliariLocations,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => mockCurrentWeather,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => mockHistoricalData,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => mockStatistics,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => mockImpactAnalysis,
      });

      // Act
      render(<WeatherAnalyticsPage />);

      // Assert
      await waitFor(() => {
        expect(screen.getByText('23.5°C')).toBeInTheDocument();
        expect(screen.getByText('15.2°C - 32.1°C')).toBeInTheDocument();
        expect(screen.getByText('45.2mm')).toBeInTheDocument();
        expect(screen.getByText('8 / 30 days')).toBeInTheDocument();
      });
    });
  });

  describe('Tab Navigation', () => {
    it('should switch between tabs correctly', async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => [],
      });

      // Act
      render(<WeatherAnalyticsPage />);

      await waitFor(() => {
        expect(screen.getByText('Overview')).toBeInTheDocument();
      });

      // Click on Trends tab
      fireEvent.click(screen.getByText('Trends'));

      // Assert
      await waitFor(() => {
        expect(screen.getByText('Temperature Trends')).toBeInTheDocument();
      });

      // Click on Impact tab
      fireEvent.click(screen.getByText('Impact'));

      // Assert
      await waitFor(() => {
        expect(screen.getByText('Temperature Impact on Water Consumption')).toBeInTheDocument();
      });

      // Click on Correlations tab
      fireEvent.click(screen.getByText('Correlations'));

      // Assert
      await waitFor(() => {
        expect(screen.getByText('Weather-System Performance Correlations')).toBeInTheDocument();
      });
    });
  });

  describe('Location Selection', () => {
    it('should allow selecting different locations', async () => {
      // Arrange
      const mockLocations = [
        { location: 'Cagliari', dataPoints: 1000, dateRange: { start: '2024-11-01', end: '2025-06-30' } },
        { location: 'Selargius', dataPoints: 950, dateRange: { start: '2024-11-01', end: '2025-06-30' } }
      ];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockLocations,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => null,
      }).mockResolvedValueOnce({
        ok: true,
        json: async () => null,
      });

      // Act
      render(<WeatherAnalyticsPage />);

      // Assert
      await waitFor(() => {
        expect(screen.getByText('All Locations')).toBeInTheDocument();
        expect(screen.getByText('Cagliari')).toBeInTheDocument();
        expect(screen.getByText('Selargius')).toBeInTheDocument();
      });
    });
  });

  describe('Date Range Selection', () => {
    it('should allow selecting different date ranges', async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => [],
      });

      // Act
      render(<WeatherAnalyticsPage />);

      // Assert
      await waitFor(() => {
        expect(screen.getByText('Last Week')).toBeInTheDocument();
        expect(screen.getByText('Last Month')).toBeInTheDocument();
        expect(screen.getByText('Last Year')).toBeInTheDocument();
      });
    });
  });
});
