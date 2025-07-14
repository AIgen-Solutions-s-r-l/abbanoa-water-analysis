import { apiClient } from '@/lib/api/client';
import { DashboardMetrics, MonitoringData, CacheStatus, FilterOptions } from '@/lib/types';

export class DashboardService {
  static async getMetrics(): Promise<DashboardMetrics> {
    const response = await apiClient.get<DashboardMetrics>('/dashboard/metrics');
    return response.data;
  }

  static async getMonitoringData(filters?: FilterOptions): Promise<MonitoringData[]> {
    const queryParams = new URLSearchParams();
    
    if (filters?.dateRange) {
      queryParams.append('start', filters.dateRange.start);
      queryParams.append('end', filters.dateRange.end);
    }
    
    if (filters?.deviceId) {
      queryParams.append('device_id', filters.deviceId);
    }

    const endpoint = `/dashboard/monitoring${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await apiClient.get<MonitoringData[]>(endpoint);
    return response.data;
  }

  static async getCacheStatus(): Promise<CacheStatus> {
    const response = await apiClient.get<CacheStatus>('/cache/status');
    return response.data;
  }

  static async refreshCache(): Promise<boolean> {
    const response = await apiClient.post<{ success: boolean }>('/cache/refresh');
    return response.data.success;
  }
} 