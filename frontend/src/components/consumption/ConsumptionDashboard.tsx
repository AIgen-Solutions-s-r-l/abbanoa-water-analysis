/**
 * Consumption Dashboard Component
 * Displays real consumption analytics data using the consumption service
 */

import React from 'react';
import { useConsumptionData } from '@/hooks/useConsumptionData';
import { consumptionService } from '@/services/consumption.service';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  DropletIcon,
  TrendingUpIcon,
  UsersIcon,
  TargetIcon,
  ActivityIcon,
  Clock,
  RefreshCwIcon,
  AlertCircleIcon
} from 'lucide-react';

interface ConsumptionDashboardProps {
  className?: string;
}

export function ConsumptionDashboard({ className = '' }: ConsumptionDashboardProps) {
  const { data, loading, error, refresh } = useConsumptionData();

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-64 ${className}`}>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex flex-col items-center justify-center h-64 ${className}`}>
        <AlertCircleIcon className="h-12 w-12 text-red-500 mb-4" />
        <p className="text-red-600 mb-4">Error loading consumption data</p>
        <Button onClick={refresh} variant="outline">
          <RefreshCwIcon className="h-4 w-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  if (!data) {
    return (
      <div className={`flex items-center justify-center h-64 ${className}`}>
        <p className="text-gray-500">No consumption data available</p>
      </div>
    );
  }

  const { summary, data_metadata, district_consumption, user_segments, peak_demand } = data;
  const dataFreshness = consumptionService.getDataFreshness(data_metadata);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with data freshness */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            Consumption Analytics
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Comprehensive water consumption insights and demand forecasting
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className={`text-sm px-3 py-1 rounded-full ${
            dataFreshness.status === 'real-time' 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : dataFreshness.status === 'recent'
              ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
              : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
          }`}>
            {dataFreshness.message}
          </div>
          <Button onClick={refresh} variant="outline" size="sm">
            <RefreshCwIcon className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Daily Consumption
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {consumptionService.formatConsumptionNumber(summary.total_daily_consumption)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {data_metadata.data_source} • {dataFreshness.message}
              </p>
            </div>
            <DropletIcon className="h-8 w-8 text-blue-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Users
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {consumptionService.formatUserNumber(summary.total_users)}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {summary.avg_consumption_per_user.toFixed(1)} L/user/day
              </p>
            </div>
            <UsersIcon className="h-8 w-8 text-green-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                System Efficiency
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {(summary.system_efficiency * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {summary.water_loss_percentage}% water loss
              </p>
            </div>
            <TargetIcon className="h-8 w-8 text-yellow-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Peak Demand
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {peak_demand.daily_peak_time}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {consumptionService.formatConsumptionNumber(peak_demand.daily_peak_consumption)}/hr
              </p>
            </div>
            <ActivityIcon className="h-8 w-8 text-red-500" />
          </div>
        </Card>
      </div>

      {/* Data Source Information */}
      <Card className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Data Source
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {data_metadata.data_source}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {data_metadata.total_readings.toLocaleString()} readings from {data_metadata.active_nodes} nodes
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Time Range
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {new Date(data_metadata.earliest_timestamp).toLocaleDateString()} - {new Date(data_metadata.latest_timestamp).toLocaleDateString()}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {data_metadata.flow_readings.toLocaleString()} flow readings
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Data Quality
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {data_metadata.synthetic_percentage === 0 ? '100% Real Data' : `${(100 - data_metadata.synthetic_percentage).toFixed(1)}% Real Data`}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {data_metadata.is_real_time ? 'Real-time updates' : 'Historical analysis'}
            </p>
          </div>
        </div>
      </Card>

      {/* District Overview */}
      {district_consumption && district_consumption.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            District Overview
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {district_consumption.slice(0, 6).map((district) => (
              <div key={district.district_id} className="border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-gray-100">
                  {district.district_name}
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {district.node_type} node
                </p>
                <div className="mt-2 space-y-1">
                  <p className="text-xs text-gray-500">
                    {consumptionService.formatConsumptionNumber(district.daily_consumption_liters)} daily
                  </p>
                  <p className="text-xs text-gray-500">
                    {consumptionService.formatUserNumber(district.total_users)} users
                  </p>
                  <p className="text-xs text-gray-500">
                    Peak: {district.peak_hour}:00
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* User Segments */}
      {user_segments && user_segments.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            User Segments
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {user_segments.map((segment) => (
              <div key={segment.segment} className="border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-gray-100">
                  {segment.segment}
                </h4>
                <p className="text-2xl font-bold text-blue-600">
                  {segment.percentage}%
                </p>
                <div className="mt-2 space-y-1">
                  <p className="text-xs text-gray-500">
                    {consumptionService.formatUserNumber(segment.user_count)} users
                  </p>
                  <p className="text-xs text-gray-500">
                    {segment.avg_daily_consumption} L/day avg
                  </p>
                  <p className="text-xs text-gray-500">
                    Trend: {segment.trend}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
