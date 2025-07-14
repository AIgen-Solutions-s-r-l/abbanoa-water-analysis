'use client';

import React from 'react';
import { useAnomalies } from '@/lib/hooks/useAnomalies';
import { Button } from '@/components/ui/Button';

const RecentAnomalies = () => {
  const { anomalies, loading, error, resolveAnomaly } = useAnomalies();

  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
              <div className="flex-1 space-y-1">
                <div className="w-3/4 h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div className="w-1/2 h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-600 dark:text-red-400 py-4">
        Failed to load anomalies: {error}
      </div>
    );
  }

  const recentAnomalies = anomalies.slice(0, 5);

  if (recentAnomalies.length === 0) {
    return (
      <div className="text-center text-gray-500 dark:text-gray-400 py-8">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="mt-2">No anomalies detected</p>
      </div>
    );
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-500';
      case 'high':
        return 'bg-orange-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const handleResolve = async (id: string) => {
    try {
      await resolveAnomaly(id);
    } catch (error) {
      console.error('Failed to resolve anomaly:', error);
    }
  };

  return (
    <div className="space-y-4">
      {recentAnomalies.map((anomaly) => (
        <div
          key={anomaly.id}
          className="flex items-start space-x-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50"
        >
          <div className={`w-3 h-3 rounded-full mt-1 ${getSeverityColor(anomaly.severity)}`}></div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {anomaly.description}
              </p>
              {!anomaly.resolved && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleResolve(anomaly.id)}
                  className="text-xs"
                >
                  Resolve
                </Button>
              )}
            </div>
            <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
              <span className="capitalize">{anomaly.severity}</span>
              <span>•</span>
              <span>{anomaly.type}</span>
              <span>•</span>
              <span>{formatTimestamp(anomaly.timestamp)}</span>
              {anomaly.resolved && (
                <>
                  <span>•</span>
                  <span className="text-green-600 dark:text-green-400">Resolved</span>
                </>
              )}
            </div>
          </div>
        </div>
      ))}
      
      {anomalies.length > 5 && (
        <div className="text-center">
          <Button variant="ghost" size="sm">
            View All Anomalies
          </Button>
        </div>
      )}
    </div>
  );
};

export { RecentAnomalies }; 