'use client';

import React from 'react';
import { KPIRibbonProps, KPIMetric } from '@/lib/types';

// Icon components (using simple SVG icons)
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

const TrendNeutralIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
  </svg>
);

const InfoIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

/**
 * Individual KPI Card component
 */
const KPICard: React.FC<{
  metric: KPIMetric;
  showTrends: boolean;
  showTooltips: boolean;
  compact: boolean;
}> = ({ metric, showTrends, showTooltips, compact }) => {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-900',
    green: 'bg-green-50 border-green-200 text-green-900',
    red: 'bg-red-50 border-red-200 text-red-900',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    purple: 'bg-purple-50 border-purple-200 text-purple-900',
    gray: 'bg-gray-50 border-gray-200 text-gray-900',
  };

  const trendColorClasses = {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-gray-600',
  };

  const cardColor = colorClasses[metric.color || 'gray'];
  const trendColor = metric.trend ? trendColorClasses[metric.trend] : 'text-gray-600';

  const TrendIcon = metric.trend === 'up' ? TrendUpIcon : 
                   metric.trend === 'down' ? TrendDownIcon : TrendNeutralIcon;

  return (
    <div className={`relative border rounded-lg p-4 ${cardColor} ${compact ? 'p-3' : 'p-4'}`}>
      {/* Tooltip */}
      {showTooltips && metric.tooltip && (
        <div className="absolute top-2 right-2">
          <div className="group relative">
            <InfoIcon className="w-4 h-4 text-gray-400 cursor-help" />
            <div className="absolute bottom-full right-0 mb-2 w-48 p-2 bg-gray-900 text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
              {metric.tooltip}
            </div>
          </div>
        </div>
      )}

      {/* Label */}
      <div className={`font-medium ${compact ? 'text-xs' : 'text-sm'} mb-1`}>
        {metric.label}
      </div>

      {/* Value */}
      <div className={`font-bold ${compact ? 'text-lg' : 'text-2xl'} mb-1`}>
        {metric.displayValue}
        {metric.unit && (
          <span className={`font-normal ${compact ? 'text-xs' : 'text-sm'} ml-1`}>
            {metric.unit}
          </span>
        )}
      </div>

      {/* Trend */}
      {showTrends && metric.trend && (
        <div className={`flex items-center ${compact ? 'text-xs' : 'text-sm'} ${trendColor}`}>
          <TrendIcon className="w-4 h-4 mr-1" />
          {metric.trendValue !== undefined && (
            <span className="font-medium">
              {metric.trendValue > 0 ? '+' : ''}{metric.trendValue.toFixed(2)}%
            </span>
          )}
          {metric.trendLabel && (
            <span className="ml-1">{metric.trendLabel}</span>
          )}
        </div>
      )}
    </div>
  );
};

/**
 * KPI Ribbon component for displaying key performance indicators
 * Implements task 4.4 requirements for financial metrics display
 */
export const KPIRibbon: React.FC<KPIRibbonProps> = ({
  metrics,
  title,
  showTrends = true,
  showTooltips = true,
  compact = false,
  className = '',
}) => {
  return (
    <div className={`w-full ${className}`}>
      {title && (
        <h3 className={`font-semibold text-gray-900 mb-4 ${compact ? 'text-lg' : 'text-xl'}`}>
          {title}
        </h3>
      )}

      <div className={`grid gap-4 ${
        compact 
          ? 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6'
          : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6'
      }`}>
        {metrics.map((metric) => (
          <KPICard
            key={metric.id}
            metric={metric}
            showTrends={showTrends}
            showTooltips={showTooltips}
            compact={compact}
          />
        ))}
      </div>
    </div>
  );
};

/**
 * Specialized TWR KPI Ribbon for Up/Down Market Performance
 */
export const TWRKPIRibbon: React.FC<{
  upMarketTWR: number;
  downMarketTWR: number;
  upMarketBenchmark?: number;
  downMarketBenchmark?: number;
  totalReturn: number;
  volatility: number;
  sharpeRatio: number;
  maxDrawdown: number;
  className?: string;
  compact?: boolean;
}> = ({
  upMarketTWR,
  downMarketTWR,
  upMarketBenchmark = 0,
  downMarketBenchmark = 0,
  totalReturn,
  volatility,
  sharpeRatio,
  maxDrawdown,
  className = '',
  compact = false,
}) => {
  const metrics: KPIMetric[] = [
    {
      id: 'up-market-twr',
      label: 'Up-Market TWR',
      value: upMarketTWR,
      displayValue: `${upMarketTWR.toFixed(2)}%`,
      trend: upMarketTWR > upMarketBenchmark ? 'up' : upMarketTWR < upMarketBenchmark ? 'down' : 'neutral',
      trendValue: upMarketTWR - upMarketBenchmark,
      color: 'green',
      tooltip: 'Time-weighted return during positive market periods',
    },
    {
      id: 'down-market-twr',
      label: 'Down-Market TWR',
      value: downMarketTWR,
      displayValue: `${downMarketTWR.toFixed(2)}%`,
      trend: downMarketTWR > downMarketBenchmark ? 'up' : downMarketTWR < downMarketBenchmark ? 'down' : 'neutral',
      trendValue: downMarketTWR - downMarketBenchmark,
      color: 'red',
      tooltip: 'Time-weighted return during negative market periods',
    },
    {
      id: 'total-return',
      label: 'Total Return',
      value: totalReturn,
      displayValue: `${totalReturn.toFixed(2)}%`,
      trend: totalReturn > 0 ? 'up' : totalReturn < 0 ? 'down' : 'neutral',
      color: 'blue',
      tooltip: 'Cumulative portfolio return',
    },
    {
      id: 'volatility',
      label: 'Volatility',
      value: volatility,
      displayValue: `${volatility.toFixed(2)}%`,
      color: 'yellow',
      tooltip: 'Standard deviation of returns',
    },
    {
      id: 'sharpe-ratio',
      label: 'Sharpe Ratio',
      value: sharpeRatio,
      displayValue: sharpeRatio.toFixed(2),
      trend: sharpeRatio > 1 ? 'up' : sharpeRatio < 0.5 ? 'down' : 'neutral',
      color: 'purple',
      tooltip: 'Risk-adjusted return measure',
    },
    {
      id: 'max-drawdown',
      label: 'Max Drawdown',
      value: maxDrawdown,
      displayValue: `${maxDrawdown.toFixed(2)}%`,
      trend: 'down', // Drawdown is always negative trend visually
      color: 'gray',
      tooltip: 'Maximum peak-to-trough decline',
    },
  ];

  return (
    <KPIRibbon
      metrics={metrics}
      title="Portfolio Performance Metrics"
      showTrends={true}
      showTooltips={true}
      compact={compact}
      className={className}
    />
  );
};

export default KPIRibbon; 