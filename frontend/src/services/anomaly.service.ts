import { apiClient } from '@/lib/api/client';
import { Anomaly, FilterOptions } from '@/lib/types';

export class AnomalyService {
  static async getAnomalies(filters?: FilterOptions): Promise<Anomaly[]> {
    const queryParams = new URLSearchParams();
    
    if (filters?.dateRange) {
      queryParams.append('start', filters.dateRange.start);
      queryParams.append('end', filters.dateRange.end);
    }
    
    if (filters?.severity) {
      queryParams.append('severity', filters.severity);
    }
    
    if (filters?.type) {
      queryParams.append('type', filters.type);
    }

    const endpoint = `/anomalies${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await apiClient.get<Anomaly[]>(endpoint);
    return response.data;
  }

  static async getAnomalyById(id: string): Promise<Anomaly> {
    const response = await apiClient.get<Anomaly>(`/anomalies/${id}`);
    return response.data;
  }

  static async resolveAnomaly(id: string): Promise<boolean> {
    const response = await apiClient.put<{ success: boolean }>(`/anomalies/${id}/resolve`);
    return response.data.success;
  }

  static async runDetection(): Promise<{ detected: number; new: number }> {
    const response = await apiClient.post<{ detected: number; new: number }>('/anomalies/detect');
    return response.data;
  }
} 