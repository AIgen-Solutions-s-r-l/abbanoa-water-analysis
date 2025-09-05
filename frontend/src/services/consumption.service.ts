/**
 * Consumption Analytics Service
 * Handles API calls for consumption analytics data
 */

export interface ConsumptionAnalytics {
  data_metadata: {
    total_readings: number;
    active_nodes: number;
    is_real_time: boolean;
    data_source: string;
    latest_timestamp: string;
    earliest_timestamp: string;
    flow_readings: number;
    synthetic_percentage: number;
    data_age_hours: number;
  };
  summary: {
    total_daily_consumption: number;
    total_monthly_consumption: number;
    total_users: number;
    avg_consumption_per_user: number;
    system_efficiency: number;
    water_loss_percentage: number;
  };
  district_consumption: Array<{
    district_id: string;
    district_name: string;
    node_type: string;
    total_users: number;
    daily_consumption_liters: number;
    monthly_consumption_liters: number;
    avg_per_user_daily: number;
    peak_hour: number;
    efficiency_score: number;
  }>;
  consumption_timeline: Array<{
    timestamp: string;
    consumption_liters: number;
    forecast_consumption: number;
  }>;
  user_segments: Array<{
    segment: string;
    user_count: number;
    percentage: number;
    avg_daily_consumption: number;
    trend: string;
  }>;
  peak_demand: {
    daily_peak_time: string;
    daily_peak_consumption: number;
    weekly_peak_day: string;
    monthly_peak_date: string;
    seasonal_peak_month: string;
  };
  conservation_opportunities: Array<{
    opportunity: string;
    potential_savings_liters_daily: number;
    potential_savings_percentage: number;
    implementation_cost: string;
    roi_months: number;
  }>;
}

export interface ConsumptionSummary {
  summary: {
    total_daily_consumption: number;
    total_monthly_consumption: number;
    total_users: number;
    avg_consumption_per_user: number;
    system_efficiency: number;
    water_loss_percentage: number;
  };
  data_metadata: {
    is_real_time: boolean;
    data_source: string;
  };
}

export interface DistrictConsumption {
  district_consumption: Array<{
    district_id: string;
    district_name: string;
    node_type: string;
    total_users: number;
    daily_consumption_liters: number;
    monthly_consumption_liters: number;
    avg_per_user_daily: number;
    peak_hour: number;
    efficiency_score: number;
  }>;
  data_metadata: {
    is_real_time: boolean;
  };
}

export interface ConsumptionTimeline {
  consumption_timeline: Array<{
    timestamp: string;
    consumption_liters: number;
    forecast_consumption: number;
  }>;
  data_metadata: {
    is_real_time: boolean;
  };
}

export interface UserSegments {
  user_segments: Array<{
    segment: string;
    user_count: number;
    percentage: number;
    avg_daily_consumption: number;
    trend: string;
  }>;
  data_metadata: {
    is_real_time: boolean;
  };
}

export interface PeakDemand {
  peak_demand: {
    daily_peak_time: string;
    daily_peak_consumption: number;
    weekly_peak_day: string;
    monthly_peak_date: string;
    seasonal_peak_month: string;
  };
  data_metadata: {
    is_real_time: boolean;
  };
}

export interface ConservationOpportunities {
  conservation_opportunities: Array<{
    opportunity: string;
    potential_savings_liters_daily: number;
    potential_savings_percentage: number;
    implementation_cost: string;
    roi_months: number;
  }>;
  data_metadata: {
    is_real_time: boolean;
  };
}

export interface HourlyPattern {
  hourly_pattern: Array<{
    hour: number;
    avg_consumption: number;
    peak_hour: boolean;
    hour_label: string;
    consumption_formatted: string;
  }>;
  data_metadata: {
    is_real_time: boolean;
  };
}

export interface TrendAnalysis {
  trend_analysis: {
    growth_rate: number;
    trend_direction: 'increasing' | 'decreasing' | 'stable';
    peak_hour: number;
    valley_hour: number;
    daily_variance: number;
    seasonal_trend: string;
    avg_daily_consumption: number;
    peak_consumption: number;
    valley_consumption: number;
  };
  data_metadata: {
    is_real_time: boolean;
  };
}

export interface NodeAnalysis {
  node_analysis: Array<{
    node_id: string;
    node_name: string;
    node_type: string;
    infrastructure_type: string;
    total_users: number;
    daily_consumption_liters: number;
    monthly_consumption_liters: number;
    avg_per_user_daily: number;
    peak_hour: number;
    efficiency_score: number;
    water_loss_percentage: number;
    pressure_avg: number;
    flow_rate_avg: number;
    last_maintenance: string;
    next_maintenance: string;
    status: string;
    alerts: number;
    performance_rating: string;
  }>;
  infrastructure_summary: {
    total_nodes: number;
    main_nodes: number;
    secondary_nodes: number;
    industrial_nodes: number;
    total_users_served: number;
    total_daily_consumption: number;
    avg_efficiency: number;
    avg_water_loss: number;
    operational_nodes: number;
    maintenance_required: number;
  };
  data_metadata: {
    is_real_time: boolean;
  };
}

export interface InfrastructureTypes {
  infrastructure_types: Array<{
    type: string;
    description: string;
    node_count: number;
    total_users: number;
    daily_consumption: number;
    avg_efficiency: number;
    avg_water_loss: number;
    avg_pressure: number;
    avg_flow_rate: number;
    performance_rating: string;
    maintenance_frequency_days: number;
    criticality_level: string;
  }>;
  data_metadata: {
    is_real_time: boolean;
  };
}

class ConsumptionService {
  private baseUrl: string;

  constructor() {
    // Use environment variable or default to local development
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
  }

  /**
   * Fetch comprehensive consumption analytics data
   */
  async getConsumptionAnalytics(): Promise<ConsumptionAnalytics> {
    try {
      const response = await fetch(`${this.baseUrl}/consumption/analytics`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching consumption analytics:', error);
      throw error;
    }
  }

  /**
   * Fetch consumption summary data only
   */
  async getConsumptionSummary(): Promise<ConsumptionSummary> {
    try {
      const response = await fetch(`${this.baseUrl}/consumption/summary`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching consumption summary:', error);
      throw error;
    }
  }

  /**
   * Fetch district consumption data
   */
  async getDistrictConsumption(): Promise<DistrictConsumption> {
    try {
      const response = await fetch(`${this.baseUrl}/consumption/districts`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching district consumption:', error);
      throw error;
    }
  }

  /**
   * Fetch consumption timeline data
   */
  async getConsumptionTimeline(): Promise<ConsumptionTimeline> {
    try {
      const response = await fetch(`${this.baseUrl}/consumption/timeline`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching consumption timeline:', error);
      throw error;
    }
  }

  /**
   * Fetch user segments data
   */
  async getUserSegments(): Promise<UserSegments> {
    try {
      const response = await fetch(`${this.baseUrl}/consumption/segments`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching user segments:', error);
      throw error;
    }
  }

  /**
   * Fetch peak demand data
   */
  async getPeakDemand(): Promise<PeakDemand> {
    try {
      const response = await fetch(`${this.baseUrl}/consumption/peak-demand`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching peak demand:', error);
      throw error;
    }
  }

  /**
   * Fetch conservation opportunities data
   */
  async getConservationOpportunities(): Promise<ConservationOpportunities> {
    try {
      const response = await fetch(`${this.baseUrl}/consumption/conservation`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching conservation opportunities:', error);
      throw error;
    }
  }

  /**
   * Fetch hourly pattern data
   */
  async getHourlyPattern(): Promise<HourlyPattern> {
    try {
      const response = await fetch(`${this.baseUrl}/consumption/hourly-pattern`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching hourly pattern:', error);
      throw error;
    }
  }

  /**
   * Fetch trend analysis data
   */
  async getTrendAnalysis(): Promise<TrendAnalysis> {
    try {
      const response = await fetch(`${this.baseUrl}/consumption/trend-analysis`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching trend analysis:', error);
      throw error;
    }
  }

  /**
   * Fetch node analysis data
   */
  async getNodeAnalysis(): Promise<NodeAnalysis> {
    try {
      const response = await fetch(`${this.baseUrl}/consumption/node-analysis`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching node analysis:', error);
      throw error;
    }
  }

  /**
   * Fetch infrastructure types analysis data
   */
  async getInfrastructureTypes(): Promise<InfrastructureTypes> {
    try {
      const response = await fetch(`${this.baseUrl}/consumption/infrastructure-types`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching infrastructure types:', error);
      throw error;
    }
  }

  /**
   * Format consumption numbers for display
   */
  formatConsumptionNumber(value: number): string {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M L`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K L`;
    }
    return `${value.toFixed(0)} L`;
  }

  /**
   * Format user numbers for display
   */
  formatUserNumber(value: number): string {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`;
    }
    return value.toFixed(0);
  }

  /**
   * Get data freshness indicator
   */
  getDataFreshness(dataMetadata: { is_real_time: boolean; data_age_hours?: number }): {
    status: 'real-time' | 'recent' | 'stale';
    message: string;
  } {
    if (dataMetadata.is_real_time) {
      return { status: 'real-time', message: 'Real-time data' };
    }
    
    const ageHours = dataMetadata.data_age_hours || 0;
    if (ageHours <= 1) {
      return { status: 'recent', message: `Updated ${ageHours.toFixed(1)}h ago` };
    } else if (ageHours <= 24) {
      return { status: 'recent', message: `Updated ${ageHours.toFixed(0)}h ago` };
    } else {
      return { status: 'stale', message: `Updated ${(ageHours / 24).toFixed(1)}d ago` };
    }
  }
}

// Export singleton instance
export const consumptionService = new ConsumptionService();
export default consumptionService;
