'use client';

import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { TrendingUp, AlertCircle, Calendar } from 'lucide-react';

interface PredictionData {
  predictions: number[];
  confidence_interval: {
    lower: number[];
    upper: number[];
  };
  accuracy_score: number;
  method: string;
  seasonal_factors: number[];
}

export default function PeakDemandForecast() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<PredictionData | null>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  const [selectedZone, setSelectedZone] = useState('1');
  const [forecastDays, setForecastDays] = useState('7');
  const [error, setError] = useState<string | null>(null);

  const fetchPredictions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `/api/proxy/v1/predictions/peak-demand?zone_id=${selectedZone}&days=${forecastDays}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch predictions');
      }
      
      const result = await response.json();
      setData(result);
      
      // Transform data for chart
      const transformed = result.predictions.map((value: number, index: number) => {
        const date = new Date();
        date.setHours(date.getHours() + index);
        return {
          time: date.toISOString().slice(0, 16).replace('T', ' '),
          demand: Math.round(value * 100) / 100,
          lower: Math.round(result.confidence_interval.lower[index] * 100) / 100,
          upper: Math.round(result.confidence_interval.upper[index] * 100) / 100,
        };
      });
      
      setChartData(transformed);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPredictions();
  }, [selectedZone, forecastDays]);

  return (
    <div className="space-y-4">
      <div className="flex gap-4 items-end">
        <div>
          <label className="text-sm font-medium mb-2 block">Zone</label>
          <Select value={selectedZone} onValueChange={setSelectedZone}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">Zone 1</SelectItem>
              <SelectItem value="2">Zone 2</SelectItem>
              <SelectItem value="3">Zone 3</SelectItem>
              <SelectItem value="4">Zone 4</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div>
          <label className="text-sm font-medium mb-2 block">Forecast Period</label>
          <Select value={forecastDays} onValueChange={setForecastDays}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">1 Day</SelectItem>
              <SelectItem value="3">3 Days</SelectItem>
              <SelectItem value="7">7 Days</SelectItem>
              <SelectItem value="14">14 Days</SelectItem>
              <SelectItem value="30">30 Days</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <Button onClick={fetchPredictions} disabled={loading}>
          {loading ? 'Loading...' : 'Refresh'}
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {data && (
        <>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-5 w-5 text-blue-600" />
                <span className="text-sm text-gray-600">Accuracy Score</span>
              </div>
              <div className="text-2xl font-bold text-blue-600">
                {(data.accuracy_score * 100).toFixed(1)}%
              </div>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Calendar className="h-5 w-5 text-green-600" />
                <span className="text-sm text-gray-600">Forecast Period</span>
              </div>
              <div className="text-2xl font-bold text-green-600">
                {forecastDays} Days
              </div>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="h-5 w-5 text-purple-600" />
                <span className="text-sm text-gray-600">Method</span>
              </div>
              <div className="text-lg font-semibold text-purple-600">
                {data.method.replace('_', ' ').toUpperCase()}
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg border">
            <h3 className="text-lg font-semibold mb-4">Demand Forecast with Confidence Intervals</h3>
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={chartData.slice(0, parseInt(forecastDays) * 24)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="time" 
                  tick={{ fontSize: 12 }}
                  interval={Math.floor(chartData.length / 8)}
                />
                <YAxis 
                  label={{ value: 'Demand (m³/h)', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="upper"
                  stroke="#8884d8"
                  fill="#8884d8"
                  fillOpacity={0.2}
                  name="Upper Bound"
                />
                <Area
                  type="monotone"
                  dataKey="lower"
                  stroke="#8884d8"
                  fill="white"
                  fillOpacity={1}
                  name="Lower Bound"
                />
                <Line
                  type="monotone"
                  dataKey="demand"
                  stroke="#2563eb"
                  strokeWidth={2}
                  dot={false}
                  name="Predicted Demand"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white p-4 rounded-lg border">
            <h3 className="text-lg font-semibold mb-4">Seasonal Factors (24-hour pattern)</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart 
                data={data.seasonal_factors.map((factor, hour) => ({
                  hour: `${hour}:00`,
                  factor: factor
                }))}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis 
                  label={{ value: 'Factor', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="factor"
                  stroke="#10b981"
                  strokeWidth={2}
                  name="Seasonal Factor"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}