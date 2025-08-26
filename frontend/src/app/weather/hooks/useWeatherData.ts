import { useState, useEffect } from 'react';
import { 
  WeatherLocation, 
  CurrentWeather, 
  WeatherStatistics, 
  ImpactAnalysis,
  HistoricalWeatherData 
} from '../types';

export const useWeatherData = (selectedLocation: string, dateRange: string, interval: string) => {
  const [locations, setLocations] = useState<WeatherLocation[]>([]);
  const [currentWeather, setCurrentWeather] = useState<CurrentWeather[]>([]);
  const [historicalData, setHistoricalData] = useState<HistoricalWeatherData[]>([]);
  const [statistics, setStatistics] = useState<WeatherStatistics | null>(null);
  const [impactAnalysis, setImpactAnalysis] = useState<ImpactAnalysis | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        setLoading(true);
        
        // Fetch locations
        const locationsRes = await fetch('/api/proxy/v1/weather/locations');
        if (locationsRes.ok) {
          const locationsData = await locationsRes.json();
          setLocations(Array.isArray(locationsData) ? locationsData : []);
        } else {
          console.error('Failed to fetch locations:', locationsRes.status);
          setLocations([]);
        }

        // Fetch current weather
        const currentUrl = selectedLocation === 'all' 
          ? '/api/proxy/v1/weather/current'
          : `/api/proxy/v1/weather/current?location=${selectedLocation}`;
        const currentRes = await fetch(currentUrl);
        if (currentRes.ok) {
          const currentData = await currentRes.json();
          setCurrentWeather(Array.isArray(currentData) ? currentData : []);
        } else {
          console.error('Failed to fetch current weather:', currentRes.status);
          setCurrentWeather([]);
        }

        // Fetch historical data
        const endDate = new Date('2025-06-30');
        const startDate = new Date('2025-06-30');
        if (dateRange === 'week') {
          startDate.setDate(startDate.getDate() - 7);
        } else if (dateRange === 'month') {
          startDate.setMonth(startDate.getMonth() - 1);
        } else if (dateRange === 'year') {
          startDate.setFullYear(startDate.getFullYear() - 1);
        }
        
        let historicalUrl = `/api/proxy/v1/weather/historical?start_date=${startDate.toISOString().split('T')[0]}&end_date=${endDate.toISOString().split('T')[0]}&interval=${interval}`;
        if (selectedLocation !== 'all') {
          historicalUrl += `&location=${selectedLocation}`;
        }
        
        const historicalRes = await fetch(historicalUrl);
        if (historicalRes.ok) {
          const historicalData = await historicalRes.json();
          console.log('📊 Historical weather data:', historicalData);
          
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
        } else {
          console.error('Failed to fetch historical data:', historicalRes.status);
          setHistoricalData([]);
        }

        // Fetch statistics
        const statsUrl = selectedLocation === 'all'
          ? '/api/proxy/v1/weather/statistics'
          : `/api/proxy/v1/weather/statistics?location=${selectedLocation}`;
        const statsRes = await fetch(statsUrl);
        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStatistics(statsData);
        } else if (statsRes.status === 204) {
          setStatistics(null);
        } else {
          console.error('Failed to fetch statistics:', statsRes.status);
          setStatistics(null);
        }

        // Fetch impact analysis
        const impactRes = await fetch('/api/proxy/v1/weather/impact-analysis');
        if (impactRes.ok) {
          const impactData = await impactRes.json();
          setImpactAnalysis(impactData);
        } else if (impactRes.status === 204) {
          setImpactAnalysis(null);
        } else {
          console.error('Failed to fetch impact analysis:', impactRes.status);
          setImpactAnalysis(null);
        }

      } catch (error) {
        console.error('Error fetching weather data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchWeatherData();
  }, [selectedLocation, dateRange, interval]);

  return {
    locations,
    currentWeather,
    historicalData,
    statistics,
    impactAnalysis,
    loading
  };
};
