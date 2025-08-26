import React from 'react';
import { Card } from '@/components/ui/Card';
import { WeatherStatistics } from '../types';

interface WeatherStatisticsCardProps {
  statistics: WeatherStatistics;
}

export const WeatherStatisticsCard: React.FC<WeatherStatisticsCardProps> = ({ statistics }) => {
  return (
    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">Weather Statistics</h2>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-3">
          <div>
            <p className="text-sm text-gray-500">Average Temperature</p>
            <p className="text-2xl font-bold">
              {statistics.overview.averageTemperature?.toFixed(1) || '--'}°C
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Temperature Range</p>
            <p className="text-lg">
              {statistics.overview.temperatureRange.min?.toFixed(1)}°C - {statistics.overview.temperatureRange.max?.toFixed(1)}°C
            </p>
          </div>
        </div>
        <div className="space-y-3">
          <div>
            <p className="text-sm text-gray-500">Total Rainfall</p>
            <p className="text-2xl font-bold">
              {statistics.overview.totalRainfall.toFixed(1)}mm
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Rainy Days</p>
            <p className="text-lg">
              {statistics.overview.rainyDays} / {statistics.overview.totalDays} days
            </p>
          </div>
        </div>
      </div>
    </Card>
  );
};
