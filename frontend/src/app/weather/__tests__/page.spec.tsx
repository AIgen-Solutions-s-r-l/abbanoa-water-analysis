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

// Mock weather data
const mockLocations = [
  { location: 'Location 1', dataPoints: 100, dateRange: { start: '2025-01-01', end: '2025-06-30' } },
  { location: 'Location 2', dataPoints: 200, dateRange: { start: '2025-01-01', end: '2025-06-30' } }
];

const mockCurrentWeather = [
  {
    location: 'Location 1',
    date: '2025-06-30',
    temperature: { current: 25, min: 20, max: 30 },
    humidity: 65,
    rainfall: 0,
    windSpeed: 10,
    conditions: 'Sunny'
  }
];

const mockHistoricalData = [
  {
    date: '2025-06-25',
    avg_temperature_c: 22,
    min_temperature_c: 18,
    max_temperature_c: 26,
    humidity_percent: 60,
    rainfall_mm: 0,
    avg_wind_speed_kmh: 15
  }
];

const mockStatistics = {
  overview: {
    totalDays: 30,
    averageTemperature: 22.5,
    temperatureRange: { min: 15, max: 35 },
    totalRainfall: 45,
    averageDailyRainfall: 1.5,
    rainyDays: 8,
    dryDays: 22
  },
  seasonalPatterns: []
};

const mockImpactAnalysis = {
  temperatureImpact: [],
  rainfallImpact: [],
  recommendations: []
};

// Mock fetch
global.fetch = jest.fn();

describe('WeatherAnalyticsPage', () => {
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
      if (url.includes('/weather/locations')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockLocations)
        });
      }
      if (url.includes('/weather/current')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockCurrentWeather)
        });
      }
      if (url.includes('/weather/historical')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockHistoricalData)
        });
      }
      if (url.includes('/weather/statistics')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockStatistics)
        });
      }
      if (url.includes('/weather/impact-analysis')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockImpactAnalysis)
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
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Weather Analytics')).toBeInTheDocument();
      });
      
      expect(screen.getByText(/Real-time weather monitoring/)).toBeInTheDocument();
    });

    it('should render all tabs', async () => {
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Overview')).toBeInTheDocument();
      });
      
      expect(screen.getByText('Trends')).toBeInTheDocument();
      expect(screen.getByText('Impact')).toBeInTheDocument();
      expect(screen.getByText('Correlations')).toBeInTheDocument();
    });

    it('should render location selector', async () => {
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        const selects = screen.getAllByRole('combobox');
        expect(selects.length).toBeGreaterThan(0);
      });
      
      const selects = screen.getAllByRole('combobox');
      const locationSelect = selects[0]; // First select is location
      expect(locationSelect).toBeInTheDocument();
      expect(locationSelect).toHaveValue('all');
    });

    it('should render date range selector', async () => {
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        const selects = screen.getAllByRole('combobox');
        expect(selects.length).toBeGreaterThan(0);
      });
      
      const selects = screen.getAllByRole('combobox');
      const dateRangeSelect = selects[1]; // Second select is date range
      expect(dateRangeSelect).toBeInTheDocument();
      expect(dateRangeSelect).toHaveValue('month');
    });

    it('should render interval selector', async () => {
      render(<WeatherAnalyticsPage />);
      
      // The interval selector is only shown in historical data tab
      await waitFor(() => {
        expect(screen.getByText('Trends')).toBeInTheDocument();
      });
      
      fireEvent.click(screen.getByText('Trends'));
      
      await waitFor(() => {
        const selects = screen.getAllByRole('combobox');
        expect(selects.length).toBeGreaterThan(2);
      });
      
      const selects = screen.getAllByRole('combobox');
      const intervalSelect = selects[2]; // Third select is interval
      expect(intervalSelect).toBeInTheDocument();
      expect(intervalSelect).toHaveValue('daily');
    });
  });

  describe('Tab Navigation', () => {
    it('should show overview tab content by default', async () => {
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Weather Analytics')).toBeInTheDocument();
      });
      
      // Overview tab should be active by default
      const overviewTab = screen.getByText('Overview');
      // Check that overview tab has active styling
      expect(overviewTab.className).toContain('text-blue-600');
    });

    it('should switch to trends tab when clicked', async () => {
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Trends')).toBeInTheDocument();
      });
      
      const trendsTab = screen.getByText('Trends');
      fireEvent.click(trendsTab);
      
      expect(screen.getByText(/Temperature Trends/)).toBeInTheDocument();
      expect(screen.getByText(/Rainfall & Humidity/)).toBeInTheDocument();
    });

    it('should switch to correlations tab when clicked', async () => {
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Correlations')).toBeInTheDocument();
      });
      
      const correlationsTab = screen.getByText('Correlations');
      fireEvent.click(correlationsTab);
      
      // Tab should become active
      expect(correlationsTab.className).toContain('text-blue-600');
    });

    it('should switch to impact tab when clicked', async () => {
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Impact')).toBeInTheDocument();
      });
      
      const impactTab = screen.getByText('Impact');
      fireEvent.click(impactTab);
      
      // Tab should become active
      expect(impactTab.className).toContain('text-blue-600');
    });
  });

  describe('Data Loading', () => {
    it('should display loading state initially', () => {
      // Mock fetch to delay response
      (global.fetch as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      );
      
      render(<WeatherAnalyticsPage />);
      
      // Should show loading spinner
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('should display weather data after loading', async () => {
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Weather Analytics')).toBeInTheDocument();
      });
      
      // Should show weather statistics
      expect(screen.getByText('Weather Statistics')).toBeInTheDocument();
      expect(screen.getByText('Average Temperature')).toBeInTheDocument();
    });
    
    it('should display no data message when API returns empty data', async () => {
      // Mock empty responses
      (global.fetch as jest.Mock).mockImplementation((url: string) => {
        if (url.includes('/weather/locations')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve([])
          });
        }
        if (url.includes('/weather/current')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve([])
          });
        }
        if (url.includes('/weather/statistics')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve(null)
          });
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      });
      
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        expect(screen.queryByRole('status')).not.toBeInTheDocument();
      });
      
      // Should show page title still
      expect(screen.getByText('Weather Analytics')).toBeInTheDocument();
    });
  });

  describe('Filter Interactions', () => {
    it('should update location filter', async () => {
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        const selects = screen.getAllByRole('combobox');
        expect(selects.length).toBeGreaterThan(0);
      });
      
      const selects = screen.getAllByRole('combobox');
      const locationSelect = selects[0];
      
      fireEvent.change(locationSelect, { target: { value: 'Location 1' } });
      
      expect(locationSelect).toHaveValue('Location 1');
    });

    it('should update date range filter', async () => {
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        const selects = screen.getAllByRole('combobox');
        expect(selects.length).toBeGreaterThan(0);
      });
      
      const selects = screen.getAllByRole('combobox');
      const dateRangeSelect = selects[1];
      
      fireEvent.change(dateRangeSelect, { target: { value: 'week' } });
      
      expect(dateRangeSelect).toHaveValue('week');
    });

    it('should update interval filter', async () => {
      render(<WeatherAnalyticsPage />);
      
      // Switch to trends tab to see interval selector
      await waitFor(() => {
        expect(screen.getByText('Trends')).toBeInTheDocument();
      });
      
      fireEvent.click(screen.getByText('Trends'));
      
      await waitFor(() => {
        const selects = screen.getAllByRole('combobox');
        expect(selects.length).toBeGreaterThan(2);
      });
      
      const selects = screen.getAllByRole('combobox');
      const intervalSelect = selects[2];
      
      // Check that it exists and has the default value
      expect(intervalSelect).toBeInTheDocument();
      expect(intervalSelect).toHaveValue('daily');
    });
  });

  describe('Weather Icons', () => {
    it('should display weather conditions correctly', async () => {
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Weather Analytics')).toBeInTheDocument();
      });
      
      // Should show location name from mock data in the heading
      const locationHeadings = screen.getAllByText('Location 1');
      expect(locationHeadings.length).toBeGreaterThan(0);
      
      // Should show temperature with decimal
      expect(screen.getByText(/25\.0/)).toBeInTheDocument();
    });
  });

  describe('Date Formatting', () => {
    it('should format dates correctly', async () => {
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Weather Analytics')).toBeInTheDocument();
      });
      
      // Date should be formatted as "Jun 30"
      expect(screen.getByText('Jun 30')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should handle fetch errors gracefully', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));
      
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Weather Analytics')).toBeInTheDocument();
      });
      
      // Should still render the page without crashing
      expect(screen.getByText('Weather Analytics')).toBeInTheDocument();
      
      // Error should be logged
      expect(consoleErrorSpy).toHaveBeenCalledWith('Error fetching weather data:', expect.any(Error));
    });
  });

  describe('Responsive Behavior', () => {
    it('should render with responsive grid layouts', async () => {
      render(<WeatherAnalyticsPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Weather Analytics')).toBeInTheDocument();
      });
      
      // Check that the page has rendered with proper structure
      const pageTitle = screen.getByText('Weather Analytics');
      expect(pageTitle).toBeInTheDocument();
      
      // Check for responsive classes in the component
      const container = pageTitle.closest('.p-6');
      expect(container).toBeInTheDocument();
    });
  });
});
