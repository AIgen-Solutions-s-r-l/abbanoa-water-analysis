/**
 * React Hook for Consumption Analytics Data
 * Provides easy access to consumption data with loading states and error handling
 */

import { useState, useEffect, useCallback } from 'react';
import { 
  consumptionService, 
  ConsumptionAnalytics, 
  ConsumptionSummary,
  DistrictConsumption,
  ConsumptionTimeline,
  UserSegments,
  PeakDemand,
  ConservationOpportunities,
  HourlyPattern,
  TrendAnalysis,
  NodeAnalysis,
  InfrastructureTypes
} from '@/services/consumption.service';

interface UseConsumptionDataReturn {
  data: ConsumptionAnalytics | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

interface UseConsumptionSummaryReturn {
  data: ConsumptionSummary | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

interface UseDistrictConsumptionReturn {
  data: DistrictConsumption | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

interface UseConsumptionTimelineReturn {
  data: ConsumptionTimeline | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

interface UseUserSegmentsReturn {
  data: UserSegments | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

interface UsePeakDemandReturn {
  data: PeakDemand | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

interface UseConservationOpportunitiesReturn {
  data: ConservationOpportunities | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

interface UseHourlyPatternReturn {
  data: HourlyPattern | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

interface UseTrendAnalysisReturn {
  data: TrendAnalysis | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

interface UseNodeAnalysisReturn {
  data: NodeAnalysis | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

interface UseInfrastructureTypesReturn {
  data: InfrastructureTypes | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

/**
 * Hook for comprehensive consumption analytics data
 */
export function useConsumptionData(autoRefresh: boolean = true): UseConsumptionDataReturn {
  const [data, setData] = useState<ConsumptionAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await consumptionService.getConsumptionAnalytics();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch consumption data');
      console.error('Error in useConsumptionData:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [fetchData, autoRefresh]);

  return {
    data,
    loading,
    error,
    refresh: fetchData
  };
}

/**
 * Hook for consumption summary data only
 */
export function useConsumptionSummary(autoRefresh: boolean = true): UseConsumptionSummaryReturn {
  const [data, setData] = useState<ConsumptionSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await consumptionService.getConsumptionSummary();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch summary data');
      console.error('Error in useConsumptionSummary:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData, autoRefresh]);

  return {
    data,
    loading,
    error,
    refresh: fetchData
  };
}

/**
 * Hook for district consumption data
 */
export function useDistrictConsumption(autoRefresh: boolean = true): UseDistrictConsumptionReturn {
  const [data, setData] = useState<DistrictConsumption | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await consumptionService.getDistrictConsumption();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch district data');
      console.error('Error in useDistrictConsumption:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData, autoRefresh]);

  return {
    data,
    loading,
    error,
    refresh: fetchData
  };
}

/**
 * Hook for consumption timeline data
 */
export function useConsumptionTimeline(autoRefresh: boolean = true): UseConsumptionTimelineReturn {
  const [data, setData] = useState<ConsumptionTimeline | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await consumptionService.getConsumptionTimeline();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch timeline data');
      console.error('Error in useConsumptionTimeline:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData, autoRefresh]);

  return {
    data,
    loading,
    error,
    refresh: fetchData
  };
}

/**
 * Hook for user segments data
 */
export function useUserSegments(autoRefresh: boolean = true): UseUserSegmentsReturn {
  const [data, setData] = useState<UserSegments | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await consumptionService.getUserSegments();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch user segments data');
      console.error('Error in useUserSegments:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData, autoRefresh]);

  return {
    data,
    loading,
    error,
    refresh: fetchData
  };
}

/**
 * Hook for peak demand data
 */
export function usePeakDemand(autoRefresh: boolean = true): UsePeakDemandReturn {
  const [data, setData] = useState<PeakDemand | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await consumptionService.getPeakDemand();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch peak demand data');
      console.error('Error in usePeakDemand:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData, autoRefresh]);

  return {
    data,
    loading,
    error,
    refresh: fetchData
  };
}

/**
 * Hook for conservation opportunities data
 */
export function useConservationOpportunities(autoRefresh: boolean = true): UseConservationOpportunitiesReturn {
  const [data, setData] = useState<ConservationOpportunities | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await consumptionService.getConservationOpportunities();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch conservation opportunities data');
      console.error('Error in useConservationOpportunities:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData, autoRefresh]);

  return {
    data,
    loading,
    error,
    refresh: fetchData
  };
}

/**
 * Hook for hourly pattern data
 */
export function useHourlyPattern(autoRefresh: boolean = true): UseHourlyPatternReturn {
  const [data, setData] = useState<HourlyPattern | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await consumptionService.getHourlyPattern();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch hourly pattern data');
      console.error('Error in useHourlyPattern:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData, autoRefresh]);

  return {
    data,
    loading,
    error,
    refresh: fetchData
  };
}

/**
 * Hook for trend analysis data
 */
export function useTrendAnalysis(autoRefresh: boolean = true): UseTrendAnalysisReturn {
  const [data, setData] = useState<TrendAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await consumptionService.getTrendAnalysis();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch trend analysis data');
      console.error('Error in useTrendAnalysis:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData, autoRefresh]);

  return {
    data,
    loading,
    error,
    refresh: fetchData
  };
}

/**
 * Hook for node analysis data
 */
export function useNodeAnalysis(autoRefresh: boolean = true): UseNodeAnalysisReturn {
  const [data, setData] = useState<NodeAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await consumptionService.getNodeAnalysis();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch node analysis data');
      console.error('Error in useNodeAnalysis:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData, autoRefresh]);

  return {
    data,
    loading,
    error,
    refresh: fetchData
  };
}

/**
 * Hook for infrastructure types data
 */
export function useInfrastructureTypes(autoRefresh: boolean = true): UseInfrastructureTypesReturn {
  const [data, setData] = useState<InfrastructureTypes | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await consumptionService.getInfrastructureTypes();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch infrastructure types data');
      console.error('Error in useInfrastructureTypes:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData, autoRefresh]);

  return {
    data,
    loading,
    error,
    refresh: fetchData
  };
}
