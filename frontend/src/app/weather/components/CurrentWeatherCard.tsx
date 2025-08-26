import React from 'react';
import { Card } from '@/components/ui/Card';
import { 
  CloudIcon, 
  CloudRainIcon, 
  SunIcon,
  WindIcon,
  MapPinIcon,
  DropletIcon
} from 'lucide-react';
import { CurrentWeather } from '../types';

interface CurrentWeatherCardProps {
  weather: CurrentWeather;
}

export const CurrentWeatherCard: React.FC<CurrentWeatherCardProps> = ({ weather }) => {
  const getWeatherIcon = (conditions: string) => {
    if (conditions.toLowerCase().includes('rain')) {
      return <CloudRainIcon className="h-8 w-8 text-blue-500" />;
    } else if (conditions.toLowerCase().includes('clear')) {
      return <SunIcon className="h-8 w-8 text-yellow-500" />;
    } else {
      return <CloudIcon className="h-8 w-8 text-gray-500" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <Card className="p-4">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <MapPinIcon className="h-4 w-4 text-gray-500" />
            {weather.location}
          </h3>
          <p className="text-sm text-gray-500">{formatDate(weather.date)}</p>
        </div>
        {getWeatherIcon(weather.conditions)}
      </div>
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-2xl font-bold">
            {weather.temperature.current?.toFixed(1) || '--'}°C
          </span>
          <span className="text-sm text-gray-500">
            {weather.temperature.min?.toFixed(1)}° / {weather.temperature.max?.toFixed(1)}°
          </span>
        </div>
        <div className="grid grid-cols-3 gap-2 text-sm">
          <div className="flex flex-col items-center">
            <DropletIcon className="h-4 w-4 text-blue-500 mb-1" />
            <span>{weather.humidity || '--'}%</span>
          </div>
          <div className="flex flex-col items-center">
            <CloudRainIcon className="h-4 w-4 text-blue-600 mb-1" />
            <span>{weather.rainfall}mm</span>
          </div>
          <div className="flex flex-col items-center">
            <WindIcon className="h-4 w-4 text-gray-500 mb-1" />
            <span>{weather.windSpeed}km/h</span>
          </div>
        </div>
      </div>
    </Card>
  );
};
