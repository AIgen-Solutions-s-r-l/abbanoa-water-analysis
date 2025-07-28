'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { 
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadialBarChart, RadialBar, Cell, PieChart, Pie
} from 'recharts';
import { 
  CloudIcon, 
  CloudRainIcon, 
  SunIcon,
  WindIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  AlertTriangleIcon,
  CalendarIcon,
  MapPinIcon,
  ThermometerIcon,
  DropletIcon,
  ActivityIcon
} from 'lucide-react';

interface WeatherLocation {
  location: string;
  dataPoints: number;
  dateRange: {
    start: string;
    end: string;
  };
}

interface CurrentWeather {
  location: string;
  date: string;
  temperature: {
    current: number | null;
    min: number | null;
    max: number | null;
  };
  humidity: number | null;
  rainfall: number;
  windSpeed: number;
  conditions: string;
}

interface WeatherStatistics {
  overview: {
    totalDays: number;
    averageTemperature: number | null;
    temperatureRange: {
      min: number | null;
      max: number | null;
    };
    totalRainfall: number;
    averageDailyRainfall: number;
    rainyDays: number;
    dryDays: number;
  };
  seasonalPatterns: Array<{
    month: number;
    avgTemperature: number | null;
    totalRainfall: number;
  }>;
}

interface ImpactAnalysis {
  temperatureImpact: Array<{
    range: string;
    days: number;
    relativeConsumption: number;
    unit: string;
  }>;
  rainfallImpact: Array<{
    category: string;
    days: number;
    systemEfficiency: number;
    unit: string;
  }>;
  recommendations: Array<{
    condition: string;
    impact: string;
    action: string;
  }>;
}

const WeatherAnalyticsPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedLocation, setSelectedLocation] = useState<string>('all');
  const [dateRange, setDateRange] = useState('month');
  const [interval, setInterval] = useState('daily');
  const [locations, setLocations] = useState<WeatherLocation[]>([]);
  const [currentWeather, setCurrentWeather] = useState<CurrentWeather[]>([]);
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [statistics, setStatistics] = useState<WeatherStatistics | null>(null);
  const [impactAnalysis, setImpactAnalysis] = useState<ImpactAnalysis | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        setLoading(true);
        
        // Fetch locations
        const locationsRes = await fetch('/api/proxy/v1/weather/locations');
        const locationsData = await locationsRes.json();
        setLocations(locationsData);

        // Fetch current weather
        const currentUrl = selectedLocation === 'all' 
          ? '/api/proxy/v1/weather/current'
          : `/api/proxy/v1/weather/current?location=${selectedLocation}`;
        const currentRes = await fetch(currentUrl);
        const currentData = await currentRes.json();
        setCurrentWeather(currentData);

        // Fetch historical data
        // Use June 2025 as the end date since that's when our data ends
        const endDate = new Date('2025-06-30');
        const startDate = new Date('2025-06-30');
        if (dateRange === 'week') {
          startDate.setDate(startDate.getDate() - 7);
        } else if (dateRange === 'month') {
          startDate.setMonth(startDate.getMonth() - 1);
        } else if (dateRange === 'year') {
          startDate.setFullYear(startDate.getFullYear() - 1);
        }
        
        // Build the URL with optional location parameter
        let historicalUrl = `/api/proxy/v1/weather/historical?start_date=${startDate.toISOString().split('T')[0]}&end_date=${endDate.toISOString().split('T')[0]}&interval=${interval}`;
        if (selectedLocation !== 'all') {
          historicalUrl += `&location=${selectedLocation}`;
        }
        
        const historicalRes = await fetch(historicalUrl);
        const historicalData = await historicalRes.json();
        console.log('📊 Historical weather data:', historicalData);
        
        // Transform the data to ensure it has the right structure
        const transformedData = Array.isArray(historicalData) ? historicalData.map((item: any) => ({
          date: item.date || item.weekStart || item.month,
          temperature: item.avg_temperature_c || item.temperature || 0,
          temperatureMin: item.min_temperature_c || item.temperatureMin || 0,
          temperatureMax: item.max_temperature_c || item.temperatureMax || 0,
          humidity: item.humidity_percent || item.humidity || 0,
          rainfall: item.rainfall_mm || item.rainfall || 0,
          windSpeed: item.avg_wind_speed_kmh || item.windSpeed || 0
        })) : [];
        
        setHistoricalData(transformedData);

        // Fetch statistics
        const statsUrl = selectedLocation === 'all'
          ? '/api/proxy/v1/weather/statistics'
          : `/api/proxy/v1/weather/statistics?location=${selectedLocation}`;
        const statsRes = await fetch(statsUrl);
        const statsData = await statsRes.json();
        setStatistics(statsData);

        // Fetch impact analysis
        const impactRes = await fetch('/api/proxy/v1/weather/impact-analysis');
        const impactData = await impactRes.json();
        setImpactAnalysis(impactData);

      } catch (error) {
        console.error('Error fetching weather data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchWeatherData();
  }, [selectedLocation, dateRange, interval]);

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

  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
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
            {locations.map(loc => (
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
          <Card key={idx} className="p-4">
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
          {/* Statistics Summary */}
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

          {/* Seasonal Patterns */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Seasonal Patterns</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={statistics.seasonalPatterns}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="month" 
                  tickFormatter={(month) => monthNames[month - 1]}
                />
                <YAxis yAxisId="temp" orientation="left" />
                <YAxis yAxisId="rain" orientation="right" />
                <Tooltip 
                  labelFormatter={(month) => monthNames[month - 1]}
                  formatter={(value: any, name: string) => [
                    typeof value === 'number' ? value.toFixed(1) : value,
                    name
                  ]}
                />
                <Legend />
                <Bar yAxisId="rain" dataKey="totalRainfall" name="Rainfall (mm)" fill="#3B82F6" />
                <Line yAxisId="temp" type="monotone" dataKey="avgTemperature" name="Avg Temp (°C)" stroke="#EF4444" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
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
          {/* Temperature Trend */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Temperature Trends</h2>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={historicalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={formatDate} />
                <YAxis />
                <Tooltip 
                  labelFormatter={formatDate}
                  formatter={(value: any) => `${value?.toFixed(1)}°C`}
                />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="temperatureMax" 
                  stackId="1"
                  stroke="#EF4444" 
                  fill="#FEE2E2" 
                  name="Max Temp"
                />
                <Area 
                  type="monotone" 
                  dataKey="temperature" 
                  stackId="2"
                  stroke="#F59E0B" 
                  fill="#FEF3C7" 
                  name="Avg Temp"
                />
                <Area 
                  type="monotone" 
                  dataKey="temperatureMin" 
                  stackId="3"
                  stroke="#3B82F6" 
                  fill="#DBEAFE" 
                  name="Min Temp"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>

          {/* Rainfall and Humidity */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Rainfall & Humidity</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={historicalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={formatDate} />
                <YAxis yAxisId="rain" orientation="left" />
                <YAxis yAxisId="humidity" orientation="right" />
                <Tooltip 
                  labelFormatter={formatDate}
                  formatter={(value: any, name: string) => [
                    typeof value === 'number' ? value.toFixed(1) : value,
                    name
                  ]}
                />
                <Legend />
                <Bar yAxisId="rain" dataKey="rainfall" name="Rainfall (mm)" fill="#3B82F6" />
                <Line 
                  yAxisId="humidity" 
                  type="monotone" 
                  dataKey="humidity" 
                  name="Humidity (%)" 
                  stroke="#10B981" 
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
            </>
          ) : (
            <Card className="p-6">
              <p className="text-center text-gray-500">No historical data available. Select a location and date range to view trends.</p>
            </Card>
          )}
        </div>
      )}

      {activeTab === 'impact' && impactAnalysis && (
        <div className="space-y-6">
          {/* Temperature Impact on Consumption */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Temperature Impact on Water Consumption</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={impactAnalysis.temperatureImpact}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="range" />
                <YAxis />
                <Tooltip formatter={(value: any) => `${value}%`} />
                <Bar dataKey="relativeConsumption" name="Relative Consumption">
                  {impactAnalysis.temperatureImpact.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Rainfall Impact on System */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Rainfall Impact on System Efficiency</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={impactAnalysis.rainfallImpact}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.category}: ${entry.days} days`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="days"
                  >
                    {impactAnalysis.rainfallImpact.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-3">
                {impactAnalysis.rainfallImpact.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-3">
                      <div 
                        className="w-4 h-4 rounded-full"
                        style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                      />
                      <span className="font-medium text-gray-900 dark:text-gray-100">{item.category}</span>
                    </div>
                    <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">{item.systemEfficiency}%</span>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          {/* Recommendations */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Weather-Based Recommendations</h2>
            <div className="space-y-4">
              {impactAnalysis.recommendations.map((rec, idx) => (
                <div key={idx} className="border-l-4 border-blue-500 pl-4 py-3">
                  <div className="flex items-start gap-3">
                    <AlertTriangleIcon className="h-5 w-5 text-amber-500 mt-0.5" />
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{rec.condition}</h3>
                      <p className="text-sm text-gray-600 mt-1">Impact: {rec.impact}</p>
                      <p className="text-sm text-gray-800 mt-2 font-medium">
                        <span className="text-blue-600">Action:</span> {rec.action}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'correlations' && (
        <div className="space-y-6">
          {/* Weather-System Correlations */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Weather-System Performance Correlations</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Temperature vs Consumption */}
              <div>
                <h3 className="text-lg font-medium mb-3">Temperature vs Water Demand</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <RadialBarChart 
                    cx="50%" 
                    cy="50%" 
                    innerRadius="10%" 
                    outerRadius="90%" 
                    barSize={10} 
                    data={[
                      { name: 'Cold Days', value: 95, fill: '#3B82F6' },
                      { name: 'Mild Days', value: 100, fill: '#10B981' },
                      { name: 'Warm Days', value: 115, fill: '#F59E0B' },
                      { name: 'Hot Days', value: 130, fill: '#EF4444' }
                    ]}
                  >
                    <RadialBar dataKey="value" cornerRadius={10} fill="#8884d8" label />
                    <Tooltip />
                  </RadialBarChart>
                </ResponsiveContainer>
              </div>

              {/* Rainfall vs Efficiency */}
              <div>
                <h3 className="text-lg font-medium mb-3">Rainfall vs System Efficiency</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-blue-100 dark:from-gray-800 dark:to-gray-700 rounded-lg border border-blue-200 dark:border-gray-600">
                    <div className="flex items-center gap-3">
                      <SunIcon className="h-6 w-6 text-yellow-500" />
                      <span className="font-medium text-gray-900 dark:text-gray-100">Dry Conditions</span>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-green-600 dark:text-green-400">98%</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Efficiency</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                    <div className="flex items-center gap-3">
                      <CloudRainIcon className="h-6 w-6 text-blue-500" />
                      <span className="font-medium text-gray-900 dark:text-gray-100">Rainy Conditions</span>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">85%</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Efficiency</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          {/* Key Insights */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Key Weather Insights</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 dark:bg-gray-800 p-4 rounded-lg border border-blue-200 dark:border-gray-700">
                <ThermometerIcon className="h-8 w-8 text-blue-600 dark:text-blue-400 mb-2" />
                <h3 className="font-semibold mb-1 text-gray-900 dark:text-gray-100">Temperature Effect</h3>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  Every 10°C increase in temperature correlates with a 15-20% increase in water demand
                </p>
              </div>
              <div className="bg-green-50 dark:bg-gray-800 p-4 rounded-lg border border-green-200 dark:border-gray-700">
                <ActivityIcon className="h-8 w-8 text-green-600 dark:text-green-400 mb-2" />
                <h3 className="font-semibold mb-1 text-gray-900 dark:text-gray-100">Seasonal Patterns</h3>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  Summer months show 40% higher consumption compared to winter baseline
                </p>
              </div>
              <div className="bg-amber-50 dark:bg-gray-800 p-4 rounded-lg border border-amber-200 dark:border-gray-700">
                <CloudRainIcon className="h-8 w-8 text-amber-600 dark:text-amber-400 mb-2" />
                <h3 className="font-semibold mb-1 text-gray-900 dark:text-gray-100">Rain Impact</h3>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  Heavy rainfall events can reduce system efficiency by up to 15% due to infiltration
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default WeatherAnalyticsPage; 