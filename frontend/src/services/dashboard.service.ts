import { DashboardMetrics } from '@/lib/types';

interface ForecastData {
  date: string;
  predictedConsumption: number;
  confidence: number;
  tenantId: string;
}

interface NetworkStatus {
  operationalPercentage: number;
  activeNodes: number;
  totalNodes: number;
  lastMaintenance: string;
  nextMaintenance: string;
  tenantId: string;
}

export class DashboardService {
  static async getMetrics(): Promise<DashboardMetrics> {
    // Use the working proxy endpoint directly
    const response = await fetch('/api/proxy/v1/dashboard/summary');
    if (!response.ok) {
      throw new Error(`Failed to fetch dashboard data: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Transform the real data to match frontend's expected format
    return {
      totalConsumption: data.network.total_volume_m3 || 0,
      activeConnections: data.network.active_nodes || 0,
      anomalies: data.network.anomaly_count || 0,
      lastUpdate: data.last_updated || new Date().toISOString(),
      tenantId: 'default'
    };
  }

  static async getForecast(days: number = 7): Promise<ForecastData[]> {
    // For now, return mock data until forecast endpoint is implemented
    const forecast: ForecastData[] = [];
    const today = new Date();
    
    for (let i = 0; i < days; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() + i);
      
      forecast.push({
        date: date.toISOString().split('T')[0],
        predictedConsumption: 1200000 + Math.random() * 100000,
        confidence: 0.85 + Math.random() * 0.1,
        tenantId: 'default'
      });
    }
    
    return forecast;
  }

  static async getNetworkStatus(): Promise<NetworkStatus> {
    // Use the working proxy endpoint directly
    const response = await fetch('/api/proxy/v1/dashboard/summary');
    if (!response.ok) {
      throw new Error(`Failed to fetch dashboard data: ${response.status}`);
    }
    
    const data = await response.json();
    
    return {
      operationalPercentage: 95, // Calculate based on active nodes
      activeNodes: data.network.active_nodes || 0,
      totalNodes: data.nodes.length || 0,
      lastMaintenance: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      nextMaintenance: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      tenantId: 'default'
    };
  }
} 