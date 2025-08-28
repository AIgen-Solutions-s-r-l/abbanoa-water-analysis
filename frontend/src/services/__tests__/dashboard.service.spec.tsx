import { DashboardService } from '../dashboard.service';
import { DashboardMetrics } from '@/lib/types';

// Mock global fetch
global.fetch = jest.fn();

describe('DashboardService', () => {
  let consoleErrorSpy: jest.SpyInstance;

  beforeEach(() => {
    jest.clearAllMocks();
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
  });

  describe('getMetrics', () => {
    it('should fetch and transform dashboard metrics successfully', async () => {
      // Arrange
      const mockApiResponse = {
        network: {
          total_flow_lps: 1234.5,
          average_pressure_bar: 4.2,
          efficiency_percentage: 85.5,
          alert_count: 3,
          energy_consumption_kwh: 5678.9,
          water_quality_index: 92.3,
          total_volume_m3: 98765.4,
          active_nodes: 150,
          anomaly_count: 2,
        },
        last_updated: '2023-12-01T10:00:00Z',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockApiResponse,
      });

      // Act
      const result = await DashboardService.getMetrics();

      // Assert
      expect(global.fetch).toHaveBeenCalledWith('/api/proxy/v1/dashboard/summary');
      expect(result).toEqual({
        totalFlow: 1234.5,
        averagePressure: 4.2,
        networkEfficiency: 85.5,
        activeAlerts: 3,
        energyConsumption: 5678.9,
        waterQuality: 92.3,
        totalConsumption: 98765.4,
        activeConnections: 150,
        anomalies: 2,
        lastUpdate: '2023-12-01T10:00:00Z',
        tenantId: 'default',
      });
    });

    it('should handle missing data with default values', async () => {
      // Arrange
      const mockApiResponse = {
        network: {},
        last_updated: null,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockApiResponse,
      });

      // Act
      const result = await DashboardService.getMetrics();

      // Assert
      expect(result).toEqual({
        totalFlow: 0,
        averagePressure: 0,
        networkEfficiency: 0,
        activeAlerts: 0,
        energyConsumption: 0,
        waterQuality: 0,
        totalConsumption: 0,
        activeConnections: 0,
        anomalies: 0,
        lastUpdate: expect.any(String), // Should be current date ISO string
        tenantId: 'default',
      });
      
      // Verify lastUpdate is a valid ISO date
      expect(result.lastUpdate).toBeDefined();
      if (result.lastUpdate) {
        expect(new Date(result.lastUpdate).toISOString()).toBe(result.lastUpdate);
      }
    });

    it('should throw error when API response is not ok', async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      });

      // Act & Assert
      await expect(DashboardService.getMetrics()).rejects.toThrow(
        'Failed to fetch dashboard data: 500'
      );
      expect(global.fetch).toHaveBeenCalledWith('/api/proxy/v1/dashboard/summary');
    });

    it('should throw error when fetch fails', async () => {
      // Arrange
      const networkError = new Error('Network error');
      (global.fetch as jest.Mock).mockRejectedValueOnce(networkError);

      // Act & Assert
      await expect(DashboardService.getMetrics()).rejects.toThrow('Network error');
    });

    it('should handle different HTTP error codes', async () => {
      // Arrange
      const errorCodes = [400, 401, 403, 404, 500, 502, 503];

      for (const code of errorCodes) {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          status: code,
        });

        // Act & Assert
        await expect(DashboardService.getMetrics()).rejects.toThrow(
          `Failed to fetch dashboard data: ${code}`
        );
      }
    });
  });

  describe('getForecast', () => {
    beforeEach(() => {
      // Mock Date to ensure consistent results
      jest.useFakeTimers();
      jest.setSystemTime(new Date('2023-12-01T10:00:00Z'));
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should return forecast data for default 7 days', async () => {
      // Arrange
      jest.spyOn(Math, 'random')
        .mockReturnValueOnce(0.5)  // First day consumption
        .mockReturnValueOnce(0.7)  // First day confidence
        .mockReturnValueOnce(0.3)  // Second day consumption
        .mockReturnValueOnce(0.9)  // Second day confidence
        .mockReturnValueOnce(0.6)  // Third day consumption
        .mockReturnValueOnce(0.4)  // Third day confidence
        .mockReturnValueOnce(0.2)  // Fourth day consumption
        .mockReturnValueOnce(0.8)  // Fourth day confidence
        .mockReturnValueOnce(0.7)  // Fifth day consumption
        .mockReturnValueOnce(0.5)  // Fifth day confidence
        .mockReturnValueOnce(0.4)  // Sixth day consumption
        .mockReturnValueOnce(0.6)  // Sixth day confidence
        .mockReturnValueOnce(0.8)  // Seventh day consumption
        .mockReturnValueOnce(0.3); // Seventh day confidence

      // Act
      const result = await DashboardService.getForecast();

      // Assert
      expect(result).toHaveLength(7);
      expect(result[0]).toEqual({
        date: '2023-12-01',
        predictedConsumption: 1250000, // 1200000 + 0.5 * 100000
        confidence: expect.closeTo(0.92, 5), // 0.85 + 0.7 * 0.1 (handle floating point precision)
        tenantId: 'default',
      });
      expect(result[6]).toEqual({
        date: '2023-12-07',
        predictedConsumption: 1280000, // 1200000 + 0.8 * 100000
        confidence: expect.closeTo(0.88, 5), // 0.85 + 0.3 * 0.1 (handle floating point precision)
        tenantId: 'default',
      });
    });

    it('should return forecast data for custom number of days', async () => {
      // Arrange
      const days = 14;

      // Act
      const result = await DashboardService.getForecast(days);

      // Assert
      expect(result).toHaveLength(14);
      expect(result[0].date).toBe('2023-12-01');
      expect(result[13].date).toBe('2023-12-14');
      
      // Verify all items have required properties
      result.forEach((item) => {
        expect(item).toHaveProperty('date');
        expect(item).toHaveProperty('predictedConsumption');
        expect(item).toHaveProperty('confidence');
        expect(item).toHaveProperty('tenantId', 'default');
        expect(item.predictedConsumption).toBeGreaterThanOrEqual(1200000);
        expect(item.predictedConsumption).toBeLessThanOrEqual(1300000);
        expect(item.confidence).toBeGreaterThanOrEqual(0.85);
        expect(item.confidence).toBeLessThanOrEqual(0.95);
      });
    });

    it('should return empty array for 0 days', async () => {
      // Act
      const result = await DashboardService.getForecast(0);

      // Assert
      expect(result).toEqual([]);
    });

    it('should handle negative days by returning empty array', async () => {
      // Act
      const result = await DashboardService.getForecast(-5);

      // Assert
      expect(result).toEqual([]);
    });
  });

  describe('getNetworkStatus', () => {
    beforeEach(() => {
      // Mock Date for consistent maintenance dates
      jest.useFakeTimers();
      jest.setSystemTime(new Date('2023-12-01T10:00:00Z'));
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should fetch and transform network status successfully', async () => {
      // Arrange
      const mockApiResponse = {
        network: {
          active_nodes: 145,
        },
        nodes: new Array(150), // Array with 150 items to simulate total nodes
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockApiResponse,
      });

      // Act
      const result = await DashboardService.getNetworkStatus();

      // Assert
      expect(global.fetch).toHaveBeenCalledWith('/api/proxy/v1/dashboard/summary');
      expect(result).toEqual({
        operationalPercentage: 95,
        activeNodes: 145,
        totalNodes: 150,
        lastMaintenance: '2023-11-24T10:00:00.000Z', // 7 days ago
        nextMaintenance: '2023-12-31T10:00:00.000Z', // 30 days later
        tenantId: 'default',
      });
    });

    it('should handle missing data with default values', async () => {
      // Arrange
      const mockApiResponse = {
        network: {},
        nodes: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockApiResponse,
      });

      // Act
      const result = await DashboardService.getNetworkStatus();

      // Assert
      expect(result).toEqual({
        operationalPercentage: 95,
        activeNodes: 0,
        totalNodes: 0,
        lastMaintenance: '2023-11-24T10:00:00.000Z',
        nextMaintenance: '2023-12-31T10:00:00.000Z',
        tenantId: 'default',
      });
    });

    it('should throw error when API response is not ok', async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 403,
        statusText: 'Forbidden',
      });

      // Act & Assert
      await expect(DashboardService.getNetworkStatus()).rejects.toThrow(
        'Failed to fetch dashboard data: 403'
      );
    });

    it('should throw error when fetch fails', async () => {
      // Arrange
      const networkError = new Error('Connection refused');
      (global.fetch as jest.Mock).mockRejectedValueOnce(networkError);

      // Act & Assert
      await expect(DashboardService.getNetworkStatus()).rejects.toThrow('Connection refused');
    });

    it('should handle API response without nodes array', async () => {
      // Arrange
      const mockApiResponse = {
        network: {
          active_nodes: 100,
        },
        // nodes property missing
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockApiResponse,
      });

      // Act
      const result = await DashboardService.getNetworkStatus();

      // Assert
      expect(result.activeNodes).toBe(100);
      expect(result.totalNodes).toBe(0); // Should default to 0 when nodes is undefined
    });
  });
});
