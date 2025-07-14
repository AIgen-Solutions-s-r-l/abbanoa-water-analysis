'use client';

import React from 'react';
import { WaterKPIRibbonProps, WaterCoreMetrics, WaterSystemKPI } from '@/lib/types';

// Icon components for water infrastructure
const WaterDropIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 16.5c0 4.14-3.36 7.5-7.5 7.5s-7.5-3.36-7.5-7.5C5 12.36 12 4 12 4s7 8.36 7 12.5z" />
  </svg>
);

const PressureIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v8m-4-4h8m-8 0a4 4 0 108 0" />
  </svg>
);

const NetworkIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
  </svg>
);

const QualityIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const UptimeIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const EnergyIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
  </svg>
);

const TrendUpIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
  </svg>
);

const TrendDownIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
  </svg>
);

const TrendStableIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
  </svg>
);

/**
 * Individual Water KPI Card component
 */
const WaterKPICard: React.FC<{
  kpi: WaterSystemKPI;
  showTrends: boolean;
  compact: boolean;
}> = ({ kpi, showTrends, compact }) => {
  
  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'good': return 'border-green-200 bg-green-50 text-green-900';
      case 'warning': return 'border-yellow-200 bg-yellow-50 text-yellow-900';
      case 'critical': return 'border-red-200 bg-red-50 text-red-900';
      default: return 'border-blue-200 bg-blue-50 text-blue-900';
    }
  };

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'up': return TrendUpIcon;
      case 'down': return TrendDownIcon;
      default: return TrendStableIcon;
    }
  };

  const getTrendColor = (trend?: string) => {
    switch (trend) {
      case 'up': return 'text-green-600';
      case 'down': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const cardClasses = `relative border rounded-lg ${getStatusColor(kpi.status)} ${compact ? 'p-3' : 'p-4'}`;
  const TrendIcon = getTrendIcon(kpi.trend);
  const trendColor = getTrendColor(kpi.trend);

  return (
    <div className={cardClasses} title={kpi.tooltip}>
      {/* Label */}
      <div className={`font-medium ${compact ? 'text-xs' : 'text-sm'} mb-1`}>
        {kpi.label}
      </div>

      {/* Value */}
      <div className={`font-bold ${compact ? 'text-lg' : 'text-2xl'} mb-1`}>
        {kpi.displayValue}
        {kpi.unit && (
          <span className={`font-normal ${compact ? 'text-xs' : 'text-sm'} ml-1 text-gray-600`}>
            {kpi.unit}
          </span>
        )}
      </div>

      {/* Trend */}
      {showTrends && kpi.trend && (
        <div className={`flex items-center ${compact ? 'text-xs' : 'text-sm'} ${trendColor}`}>
          <TrendIcon className="w-4 h-4 mr-1" />
          {kpi.trendValue !== undefined && (
            <span className="font-medium">
              {kpi.trendValue > 0 ? '+' : ''}{kpi.trendValue.toFixed(1)}%
            </span>
          )}
        </div>
      )}

      {/* Target indicator */}
      {kpi.target && (
        <div className={`text-xs text-gray-500 mt-1`}>
          Target: {kpi.target}
        </div>
      )}
    </div>
  );
};

/**
 * Water Infrastructure KPI Ribbon component
 * Displays the 6 core water management metrics from Enhanced System Overview
 */
export const WaterKPIRibbon: React.FC<WaterKPIRibbonProps> = ({
  metrics,
  timeRange,
  showTrends = true,
  compact = false,
  className = '',
}) => {
  
  // Convert WaterCoreMetrics to WaterSystemKPI array
  const kpis: WaterSystemKPI[] = [
    {
      id: 'active-nodes',
      label: 'Active Nodes',
      value: metrics.activeNodes,
      displayValue: `${metrics.activeNodes}/${metrics.totalNodes}`,
      status: metrics.activeNodes / metrics.totalNodes >= 0.9 ? 'good' : 
              metrics.activeNodes / metrics.totalNodes >= 0.7 ? 'warning' : 'critical',
      tooltip: `${metrics.activeNodes} out of ${metrics.totalNodes} water nodes are currently active and reporting data`,
    },
    {
      id: 'total-flow',
      label: 'Total Flow Rate',
      value: metrics.totalFlowRate,
      displayValue: metrics.totalFlowRate.toFixed(1),
      unit: 'L/s',
      trend: 'stable', // This would come from API in real implementation
      status: metrics.totalFlowRate > 0 ? 'good' : 'critical',
      tooltip: 'Current total water flow rate across all active network nodes',
    },
    {
      id: 'avg-pressure',
      label: 'Avg Pressure',
      value: metrics.averagePressure,
      displayValue: metrics.averagePressure.toFixed(2),
      unit: 'bar',
      trend: 'stable',
      status: metrics.averagePressure >= 2.0 && metrics.averagePressure <= 4.0 ? 'good' :
              metrics.averagePressure >= 1.5 && metrics.averagePressure <= 5.0 ? 'warning' : 'critical',
      target: '2.0-4.0 bar',
      tooltip: 'Average water pressure across the distribution network',
    },
    {
      id: 'data-quality',
      label: 'Data Quality',
      value: metrics.dataQuality,
      displayValue: `${metrics.dataQuality.toFixed(1)}%`,
      trend: metrics.dataQuality >= 95 ? 'up' : metrics.dataQuality >= 85 ? 'stable' : 'down',
      status: metrics.dataQuality >= 90 ? 'good' : 
              metrics.dataQuality >= 70 ? 'warning' : 'critical',
      target: '>90%',
      tooltip: 'Overall quality score of sensor data based on accuracy, completeness, and timeliness',
    },
    {
      id: 'system-uptime',
      label: 'System Uptime',
      value: metrics.systemUptime,
      displayValue: `${metrics.systemUptime.toFixed(2)}%`,
      trend: metrics.systemUptime >= 99.5 ? 'up' : 'stable',
      status: metrics.systemUptime >= 99.0 ? 'good' : 
              metrics.systemUptime >= 95.0 ? 'warning' : 'critical',
      target: '99.5%',
      tooltip: 'Percentage of time the water system has been operational without major disruptions',
    },
    {
      id: 'energy-efficiency',
      label: 'Energy Efficiency',
      value: metrics.energyEfficiency,
      displayValue: metrics.energyEfficiency.toFixed(3),
      unit: 'kWh/m³',
      trend: metrics.energyEfficiency <= 0.40 ? 'up' : 'down',
      status: metrics.energyEfficiency <= 0.40 ? 'good' : 
              metrics.energyEfficiency <= 0.50 ? 'warning' : 'critical',
      target: '<0.40',
      tooltip: 'Energy consumption per cubic meter of water processed through the system',
    },
  ];

  return (
    <div className={`w-full ${className}`}>
      <div className="mb-4 flex items-center justify-between">
        <h3 className={`font-semibold text-gray-900 ${compact ? 'text-lg' : 'text-xl'}`}>
          Core Water System KPIs
        </h3>
        <span className={`text-sm text-gray-600 ${compact ? 'text-xs' : 'text-sm'}`}>
          {timeRange}
        </span>
      </div>

      <div className={`grid gap-4 ${
        compact 
          ? 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-6'
          : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6'
      }`}>
        {kpis.map((kpi) => (
          <WaterKPICard
            key={kpi.id}
            kpi={kpi}
            showTrends={showTrends}
            compact={compact}
          />
        ))}
      </div>
      
      {/* System status summary */}
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">Overall System Status:</span>
          <span className={`text-sm font-semibold ${
            metrics.systemUptime >= 99.0 && metrics.dataQuality >= 90 ? 'text-green-600' :
            metrics.systemUptime >= 95.0 && metrics.dataQuality >= 70 ? 'text-yellow-600' : 'text-red-600'
          }`}>
            {metrics.systemUptime >= 99.0 && metrics.dataQuality >= 90 ? '🟢 Optimal' :
             metrics.systemUptime >= 95.0 && metrics.dataQuality >= 70 ? '🟡 Good' : '🔴 Needs Attention'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default WaterKPIRibbon; 