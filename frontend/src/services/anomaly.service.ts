import { apiClient } from '@/lib/api/client';
import { Anomaly } from '@/lib/types';

interface AnomalyStats {
  total: number;
  resolved: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  resolutionRate: number;
  tenantId: string;
}

export class AnomalyService {
  static async getAnomalies(): Promise<Anomaly[]> {
    const response = await apiClient.get<any[]>('/anomalies');
    
    // Transform backend data to match frontend Anomaly type
    return response.data.map(item => ({
      id: item.id,
      deviceId: item.node_id,
      type: item.anomaly_type,
      severity: item.severity as 'low' | 'medium' | 'high' | 'critical',
      description: item.description,
      timestamp: item.timestamp,
      resolved: !!item.resolved_at,
      resolvedAt: item.resolved_at,
      tenantId: 'default'
    }));
  }

  static async getAnomaly(id: string): Promise<Anomaly> {
    // For now, get all anomalies and find the one with matching ID
    const anomalies = await this.getAnomalies();
    const anomaly = anomalies.find(a => a.id === id);
    
    if (!anomaly) {
      throw new Error('Anomaly not found');
    }
    
    return anomaly;
  }

  static async resolveAnomaly(id: string): Promise<void> {
    // This endpoint might not exist in the real backend yet
    // For now, we'll just simulate it
    console.log('Resolving anomaly:', id);
    // await apiClient.put(`/anomalies/${id}/resolve`);
  }

  static async getStats(): Promise<AnomalyStats> {
    const anomalies = await this.getAnomalies();
    
    const total = anomalies.length;
    const resolved = anomalies.filter(a => a.resolved).length;
    const critical = anomalies.filter(a => a.severity === 'critical' && !a.resolved).length;
    const high = anomalies.filter(a => a.severity === 'high' && !a.resolved).length;
    const medium = anomalies.filter(a => a.severity === 'medium' && !a.resolved).length;
    const low = anomalies.filter(a => a.severity === 'low' && !a.resolved).length;
    
    return {
      total,
      resolved,
      critical,
      high,
      medium,
      low,
      resolutionRate: total > 0 ? (resolved / total) * 100 : 0,
      tenantId: 'default'
    };
  }
} 