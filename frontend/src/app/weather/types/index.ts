export interface WeatherLocation {
  location: string;
  dataPoints: number;
  dateRange: {
    start: string;
    end: string;
  };
}

export interface CurrentWeather {
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

export interface WeatherStatistics {
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

export interface ImpactAnalysis {
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

export interface HistoricalWeatherData {
  date: string;
  temperature: number;
  temperatureMin: number;
  temperatureMax: number;
  humidity: number;
  rainfall: number;
  windSpeed: number;
}
