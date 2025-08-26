'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { 
  CurrentWeatherCard,
  WeatherStatisticsCard,
  SeasonalPatternsChart,
  TemperatureTrendsChart,
  RainfallHumidityChart,
  ImpactAnalysisSection,
  CorrelationsSection,
  NoDataMessage
} from './components';
import { useWeatherData } from './hooks/useWeatherData';

const WeatherAnalyticsPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedLocation, setSelectedLocation] = useState<string>('all');
  const [dateRange, setDateRange] = useState('month');
  const [interval, setInterval] = useState('daily');
  
  const {
    locations,
    currentWeather,
    historicalData,
    statistics,
    impactAnalysis,
    loading
  } = useWeatherData(selectedLocation, dateRange, interval);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Check if we have no data at all
  if (!loading && locations.length === 0 && currentWeather.length === 0) {
    return <NoDataMessage />;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Weather Analytics</h1>
          <p className="text-gray-600 mt-1">Real-time weather monitoring and impact analysis</p>
        </div>
        <div className="flex gap-2">
          <select
            value={selectedLocation}
            onChange={(e) => setSelectedLocation(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Locations</option>
            {locations && locations.length > 0 && locations.map(loc => (
              <option key={loc.location} value={loc.location}>
                {loc.location}
              </option>
            ))}
          </select>
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="year">Last Year</option>
          </select>
        </div>
      </div>

      {/* Current Weather Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {currentWeather.map((weather, idx) => (
          <CurrentWeatherCard key={idx} weather={weather} />
        ))}
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <div className="flex space-x-8">
          {['overview', 'trends', 'impact', 'correlations'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && statistics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <WeatherStatisticsCard statistics={statistics} />
          <SeasonalPatternsChart seasonalPatterns={statistics.seasonalPatterns} />
        </div>
      )}

      {activeTab === 'trends' && (
        <div className="space-y-6">
          {/* Controls for trends */}
          <div className="flex justify-end gap-4 mb-4">
            <select
              value={interval}
              onChange={(e) => setInterval(e.target.value)}
              className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
          
          {historicalData.length > 0 ? (
            <>
              <TemperatureTrendsChart data={historicalData} />
              <RainfallHumidityChart data={historicalData} />
            </>
          ) : (
            <Card className="p-6">
              <p className="text-center text-gray-500">No historical data available. Select a location and date range to view trends.</p>
            </Card>
          )}
        </div>
      )}

      {activeTab === 'impact' && impactAnalysis && (
        <ImpactAnalysisSection impactAnalysis={impactAnalysis} />
      )}

      {activeTab === 'correlations' && (
        <CorrelationsSection />
      )}
    </div>
  );
};

export default WeatherAnalyticsPage; 