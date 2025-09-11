
// Mock global fetch
global.fetch = jest.fn();

describe('AnomalyService', () => {
  let consoleLogSpy: jest.SpyInstance;

  beforeEach(() => {
    jest.clearAllMocks();
    consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleLogSpy.mockRestore();
  });

  describe('getAnomalies', () => {
    it('should fetch and transform anomalies successfully', async () => {
      // Arrange
      const mockApiResponse = [
        {
          id: 'anomaly-1',
          node_id: 'device-123',
          anomaly_type: 'pressure_drop',
          severity: 'high',
          description: 'Sudden pressure drop detected',
          timestamp: '2023-12-01T10:00:00Z',
          resolved_at: null,
        },
        {
          id: 'anomaly-2',
          node_id: 'device-456',
          anomaly_type: 'flow_spike',
          severity: 'medium',
          description: 'Abnormal flow rate increase',
          timestamp: '2023-12-01T09:30:00Z',
          resolved_at: '2023-12-01T10:00:00Z',
        },
      ];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockApiResponse,
      });

      // Act
      const result = await AnomalyService.getAnomalies();

      // Assert
      expect(global.fetch).toHaveBeenCalledWith('/api/v1/anomalies?hours=168');
      expect(result).toEqual([
        {
          id: 'anomaly-1',
          deviceId: 'device-123',
          type: 'pressure_drop',
          severity: 'high',
          description: 'Sudden pressure drop detected',
          timestamp: '2023-12-01T10:00:00Z',
          resolved: false,
          resolvedAt: null,
          tenantId: 'default',
        },
        {
          id: 'anomaly-2',
          deviceId: 'device-456',
          type: 'flow_spike',
          severity: 'medium',
          description: 'Abnormal flow rate increase',
          timestamp: '2023-12-01T09:30:00Z',
          resolved: true,
          resolvedAt: '2023-12-01T10:00:00Z',
          tenantId: 'default',
        },
      ]);
    });

    it('should handle empty anomalies array', async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => [],
      });

      // Act
      const result = await AnomalyService.getAnomalies();

      // Assert
      expect(result).toEqual([]);
    });

    it('should throw error when API response is not ok', async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      });

      // Act & Assert
      await expect(AnomalyService.getAnomalies()).rejects.toThrow(
        'Failed to fetch anomalies: 500'
      );
    });

    it('should throw error when fetch fails', async () => {
      // Arrange
      const networkError = new Error('Network error');
      (global.fetch as jest.Mock).mockRejectedValueOnce(networkError);

      // Act & Assert
      await expect(AnomalyService.getAnomalies()).rejects.toThrow('Network error');
    });

    it('should handle different severity levels correctly', async () => {
      // Arrange
      const mockApiResponse = [
        { id: '1', node_id: 'd1', anomaly_type: 'type1', severity: 'low', description: 'Low', timestamp: '2023-12-01T10:00:00Z', resolved_at: null },
        { id: '2', node_id: 'd2', anomaly_type: 'type2', severity: 'medium', description: 'Medium', timestamp: '2023-12-01T10:00:00Z', resolved_at: null },
        { id: '3', node_id: 'd3', anomaly_type: 'type3', severity: 'high', description: 'High', timestamp: '2023-12-01T10:00:00Z', resolved_at: null },
        { id: '4', node_id: 'd4', anomaly_type: 'type4', severity: 'critical', description: 'Critical', timestamp: '2023-12-01T10:00:00Z', resolved_at: null },
      ];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockApiResponse,
      });

      // Act
      const result = await AnomalyService.getAnomalies();

      // Assert
      expect(result).toHaveLength(4);
      expect(result[0].severity).toBe('low');
      expect(result[1].severity).toBe('medium');
      expect(result[2].severity).toBe('high');
      expect(result[3].severity).toBe('critical');
    });
  });

  describe('getAnomaly', () => {
    it('should return a specific anomaly by id', async () => {
      // Arrange
      const mockApiResponse = [
        {
          id: 'anomaly-1',
          node_id: 'device-123',
          anomaly_type: 'pressure_drop',
          severity: 'high',
          description: 'Sudden pressure drop detected',
          timestamp: '2023-12-01T10:00:00Z',
          resolved_at: null,
        },
        {
          id: 'anomaly-2',
          node_id: 'device-456',
          anomaly_type: 'flow_spike',
          severity: 'medium',
          description: 'Abnormal flow rate increase',
          timestamp: '2023-12-01T09:30:00Z',
          resolved_at: null,
        },
      ];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockApiResponse,
      });

      // Act
      const result = await AnomalyService.getAnomaly('anomaly-2');

      // Assert
      expect(result).toEqual({
        id: 'anomaly-2',
        deviceId: 'device-456',
        type: 'flow_spike',
        severity: 'medium',
        description: 'Abnormal flow rate increase',
        timestamp: '2023-12-01T09:30:00Z',
        resolved: false,
        resolvedAt: null,
        tenantId: 'default',
      });
    });

    it('should throw error when anomaly is not found', async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => [],
      });

      // Act & Assert
      await expect(AnomalyService.getAnomaly('non-existent')).rejects.toThrow(
        'Anomaly not found'
      );
    });

    it('should handle API error when fetching anomalies', async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      // Act & Assert
      await expect(AnomalyService.getAnomaly('any-id')).rejects.toThrow(
        'Failed to fetch anomalies: 404'
      );
    });
  });

  describe('resolveAnomaly', () => {
    it('should log anomaly resolution', async () => {
      // Act
      await AnomalyService.resolveAnomaly('anomaly-123');

      // Assert
      expect(consoleLogSpy).toHaveBeenCalledWith('Resolving anomaly:', 'anomaly-123');
    });

    it('should handle multiple resolution calls', async () => {
      // Act
      await AnomalyService.resolveAnomaly('anomaly-1');
      await AnomalyService.resolveAnomaly('anomaly-2');
      await AnomalyService.resolveAnomaly('anomaly-3');

      // Assert
      expect(consoleLogSpy).toHaveBeenCalledTimes(3);
      expect(consoleLogSpy).toHaveBeenNthCalledWith(1, 'Resolving anomaly:', 'anomaly-1');
      expect(consoleLogSpy).toHaveBeenNthCalledWith(2, 'Resolving anomaly:', 'anomaly-2');
      expect(consoleLogSpy).toHaveBeenNthCalledWith(3, 'Resolving anomaly:', 'anomaly-3');
    });
  });

  describe('getStats', () => {
    it('should calculate anomaly statistics correctly', async () => {
      // Arrange
      const mockApiResponse = [
        { id: '1', node_id: 'd1', anomaly_type: 'type1', severity: 'critical', description: 'Critical', timestamp: '2023-12-01T10:00:00Z', resolved_at: null },
        { id: '2', node_id: 'd2', anomaly_type: 'type2', severity: 'high', description: 'High', timestamp: '2023-12-01T10:00:00Z', resolved_at: null },
        { id: '3', node_id: 'd3', anomaly_type: 'type3', severity: 'high', description: 'High', timestamp: '2023-12-01T10:00:00Z', resolved_at: '2023-12-01T11:00:00Z' },
        { id: '4', node_id: 'd4', anomaly_type: 'type4', severity: 'medium', description: 'Medium', timestamp: '2023-12-01T10:00:00Z', resolved_at: null },
        { id: '5', node_id: 'd5', anomaly_type: 'type5', severity: 'medium', description: 'Medium', timestamp: '2023-12-01T10:00:00Z', resolved_at: '2023-12-01T11:00:00Z' },
        { id: '6', node_id: 'd6', anomaly_type: 'type6', severity: 'low', description: 'Low', timestamp: '2023-12-01T10:00:00Z', resolved_at: null },
      ];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockApiResponse,
      });

      // Act
      const result = await AnomalyService.getStats();

      // Assert
      expect(result).toEqual({
        total: 6,
        resolved: 2,
        critical: 1, // 1 critical, unresolved
        high: 1,     // 2 high total, 1 resolved
        medium: 1,   // 2 medium total, 1 resolved
        low: 1,      // 1 low, unresolved
        resolutionRate: (2 / 6) * 100,
        tenantId: 'default',
      });
    });

    it('should handle empty anomalies list', async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => [],
      });

      // Act
      const result = await AnomalyService.getStats();

      // Assert
      expect(result).toEqual({
        total: 0,
        resolved: 0,
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
        resolutionRate: 0,
        tenantId: 'default',
      });
    });

    it('should calculate 100% resolution rate when all anomalies are resolved', async () => {
      // Arrange
      const mockApiResponse = [
        { id: '1', node_id: 'd1', anomaly_type: 'type1', severity: 'high', description: 'High', timestamp: '2023-12-01T10:00:00Z', resolved_at: '2023-12-01T11:00:00Z' },
        { id: '2', node_id: 'd2', anomaly_type: 'type2', severity: 'medium', description: 'Medium', timestamp: '2023-12-01T10:00:00Z', resolved_at: '2023-12-01T11:00:00Z' },
        { id: '3', node_id: 'd3', anomaly_type: 'type3', severity: 'low', description: 'Low', timestamp: '2023-12-01T10:00:00Z', resolved_at: '2023-12-01T11:00:00Z' },
      ];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockApiResponse,
      });

      // Act
      const result = await AnomalyService.getStats();

      // Assert
      expect(result).toEqual({
        total: 3,
        resolved: 3,
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
        resolutionRate: 100,
        tenantId: 'default',
      });
    });

    it('should handle API error when fetching anomalies for stats', async () => {
      // Arrange
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 503,
      });

      // Act & Assert
      await expect(AnomalyService.getStats()).rejects.toThrow(
        'Failed to fetch anomalies: 503'
      );
    });
  });
});