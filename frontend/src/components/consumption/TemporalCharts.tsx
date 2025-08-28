/**
 * Temporal Charts Component
 * Displays time-based consumption charts and trend analysis
 */

import React from 'react';
import { Card } from '@/components/ui/Card';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  TrendingUpIcon, 
  TrendingDownIcon, 
  MinusIcon,
  Clock,
  ActivityIcon,
  BarChart3Icon
} from 'lucide-react';

interface TemporalChartsProps {
  timelineData: Array<{
    timestamp: string;
    consumption_liters: number;
    forecast_consumption: number;
  }>;
  hourlyPattern: Array<{
    hour: number;
    avg_consumption: number;
    peak_hour: boolean;
    hour_label: string;
    consumption_formatted: string;
  }>;
  trendAnalysis: {
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
  className?: string;
}

export function TemporalCharts({ 
  timelineData, 
  hourlyPattern, 
  trendAnalysis, 
  className = '' 
}: TemporalChartsProps) {
  
  // Format timeline data for charts
  const chartTimelineData = timelineData.map(point => ({
    time: new Date(point.timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    }),
    actual: point.consumption_liters,
    forecast: point.forecast_consumption,
    timestamp: point.timestamp
  }));

  // Format hourly pattern for bar chart
  const chartHourlyData = hourlyPattern.map(point => ({
    hour: point.hour_label,
    consumption: point.avg_consumption,
    isPeak: point.peak_hour,
    formatted: point.consumption_formatted
  }));

  // Colors for charts
  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
  const PEAK_COLOR = '#ef4444';
  const NORMAL_COLOR = '#3b82f6';

  // Custom tooltip for timeline chart
  const TimelineTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900 dark:text-gray-100">{label}</p>
          <p className="text-sm text-blue-600">
            Actual: {payload[0]?.value?.toLocaleString()} L
          </p>
          <p className="text-sm text-green-600">
            Forecast: {payload[1]?.value?.toLocaleString()} L
          </p>
        </div>
      );
    }
    return null;
  };

  // Custom tooltip for hourly chart
  const HourlyTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0]?.payload;
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900 dark:text-gray-100">{label}</p>
          <p className="text-sm text-blue-600">
            Consumption: {data?.formatted}
          </p>
          {data?.isPeak && (
            <p className="text-sm text-red-600 font-medium">Peak Hour</p>
          )}
        </div>
      );
    }
    return null;
  };

  // Get trend icon and color
  const getTrendIcon = () => {
    switch (trendAnalysis.trend_direction) {
      case 'increasing':
        return <TrendingUpIcon className="h-5 w-5 text-green-500" />;
      case 'decreasing':
        return <TrendingDownIcon className="h-5 w-5 text-red-500" />;
      default:
        return <MinusIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getTrendColor = () => {
    switch (trendAnalysis.trend_direction) {
      case 'increasing':
        return 'text-green-600';
      case 'decreasing':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Trend Analysis Summary */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Trend Analysis
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="flex items-center space-x-3">
            {getTrendIcon()}
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Trend</p>
              <p className={`font-medium ${getTrendColor()}`}>
                {trendAnalysis.trend_direction.charAt(0).toUpperCase() + 
                 trendAnalysis.trend_direction.slice(1)}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <ActivityIcon className="h-5 w-5 text-blue-500" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Growth Rate</p>
              <p className="font-medium text-gray-900 dark:text-gray-100">
                {trendAnalysis.growth_rate}%
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <Clock className="h-5 w-5 text-orange-500" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Peak Hour</p>
              <p className="font-medium text-gray-900 dark:text-gray-100">
                {trendAnalysis.peak_hour.toString().padStart(2, '0')}:00
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <BarChart3Icon className="h-5 w-5 text-purple-500" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Daily Variance</p>
              <p className="font-medium text-gray-900 dark:text-gray-100">
                {trendAnalysis.daily_variance}%
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* 24-Hour Consumption Pattern */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          24-Hour Consumption Pattern
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartHourlyData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="hour" 
              tick={{ fontSize: 12 }}
              interval={2}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
            />
            <Tooltip content={<HourlyTooltip />} />
            <Bar 
              dataKey="consumption" 
              fill={NORMAL_COLOR}
              radius={[4, 4, 0, 0]}
            >
              {chartHourlyData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.isPeak ? PEAK_COLOR : NORMAL_COLOR} 
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-4 flex justify-center space-x-6">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded bg-blue-500"></div>
            <span className="text-sm text-gray-600 dark:text-gray-400">Normal Hours</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded bg-red-500"></div>
            <span className="text-sm text-gray-600 dark:text-gray-400">Peak Hours</span>
          </div>
        </div>
      </Card>

      {/* Consumption Timeline with Forecast */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Consumption Timeline with Forecast
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartTimelineData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="time" 
              tick={{ fontSize: 12 }}
              interval={2}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
            />
            <Tooltip content={<TimelineTooltip />} />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="actual" 
              stackId="1"
              stroke="#3b82f6" 
              fill="#3b82f6" 
              fillOpacity={0.6}
              name="Actual Consumption"
            />
            <Area 
              type="monotone" 
              dataKey="forecast" 
              stackId="2"
              stroke="#10b981" 
              fill="#10b981" 
              fillOpacity={0.3}
              name="Forecast"
            />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* Peak vs Valley Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Peak Hour Analysis
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Peak Hour:</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {trendAnalysis.peak_hour.toString().padStart(2, '0')}:00
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Peak Consumption:</span>
              <span className="font-medium text-red-600">
                {(trendAnalysis.peak_consumption / 1000).toFixed(1)}K L
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Valley Hour:</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {trendAnalysis.valley_hour.toString().padStart(2, '0')}:00
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Valley Consumption:</span>
              <span className="font-medium text-blue-600">
                {(trendAnalysis.valley_consumption / 1000).toFixed(1)}K L
              </span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Daily Statistics
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Average Daily:</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {(trendAnalysis.avg_daily_consumption / 1000000).toFixed(1)}M L
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Daily Variance:</span>
              <span className="font-medium text-purple-600">
                {trendAnalysis.daily_variance}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Seasonal Trend:</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {trendAnalysis.seasonal_trend.charAt(0).toUpperCase() + 
                 trendAnalysis.seasonal_trend.slice(1)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Growth Rate:</span>
              <span className={`font-medium ${getTrendColor()}`}>
                {trendAnalysis.growth_rate}%
              </span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
