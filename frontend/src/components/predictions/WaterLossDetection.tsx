'use client';

import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Droplets, TrendingUp, TrendingDown, AlertTriangle, Activity } from 'lucide-react';

interface WaterLossData {
  current_loss_percentage: number;
  predicted_loss_trend: 'increasing' | 'decreasing' | 'stable' | 'unknown';
  leak_probability: number;
  recommended_actions: string[];
  analysis: {
    avg_loss_m3: number;
    max_loss_m3: number;
    night_flow_anomaly: boolean;
  };
}

const ZONES = [
  { id: '1', name: 'Zone 1 - North District' },
  { id: '2', name: 'Zone 2 - South District' },
  { id: '3', name: 'Zone 3 - East District' },
  { id: '4', name: 'Zone 4 - West District' },
  { id: '5', name: 'Zone 5 - Central District' },
];

export default function WaterLossDetection() {
  const [loading, setLoading] = useState(false);
  const [selectedZone, setSelectedZone] = useState('1');
  const [data, setData] = useState<WaterLossData | null>(null);
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  const fetchWaterLossData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `/api/v1/predictions/water-loss?zone_id=${selectedZone}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch water loss data');
      }
      
      const result = await response.json();
      setData(result);
      
      // Generate mock historical data for visualization
      const historical = Array.from({ length: 24 }, (_, i) => ({
        hour: `${i}:00`,
        loss: Math.max(0, result.current_loss_percentage + (Math.random() - 0.5) * 2),
        flowIn: 100 + Math.random() * 20,
        flowOut: 95 + Math.random() * 18,
      }));
      setHistoricalData(historical);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWaterLossData();
  }, [selectedZone]);

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing': return <TrendingUp className="h-5 w-5 text-red-600" />;
      case 'decreasing': return <TrendingDown className="h-5 w-5 text-green-600" />;
      case 'stable': return <Activity className="h-5 w-5 text-blue-600" />;
      default: return <Activity className="h-5 w-5 text-gray-600" />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'increasing': return 'text-red-600';
      case 'decreasing': return 'text-green-600';
      case 'stable': return 'text-blue-600';
      default: return 'text-gray-600';
    }
  };

  const getLeakRiskLevel = (probability: number) => {
    if (probability > 0.7) return { level: 'High', color: 'bg-red-500' };
    if (probability > 0.4) return { level: 'Medium', color: 'bg-yellow-500' };
    return { level: 'Low', color: 'bg-green-500' };
  };

  return (
    <div className="space-y-6">
      <div className="flex gap-4 items-center">
        <Select value={selectedZone} onValueChange={setSelectedZone}>
          <SelectTrigger className="w-64">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {ZONES.map((zone) => (
              <SelectItem key={zone.id} value={zone.id}>
                {zone.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button onClick={fetchWaterLossData} disabled={loading}>
          {loading ? 'Analyzing...' : 'Refresh Analysis'}
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {data && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Current Water Loss</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  <Droplets className="h-6 w-6 text-blue-600" />
                  <div>
                    <div className="text-2xl font-bold">
                      {data.current_loss_percentage.toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-500">
                      of total flow
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Loss Trend</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  {getTrendIcon(data.predicted_loss_trend)}
                  <div>
                    <div className={`text-2xl font-bold capitalize ${getTrendColor(data.predicted_loss_trend)}`}>
                      {data.predicted_loss_trend}
                    </div>
                    <div className="text-sm text-gray-500">
                      predicted trend
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Leak Probability</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">
                      {getLeakRiskLevel(data.leak_probability).level} Risk
                    </span>
                    <span className="text-2xl font-bold">
                      {(data.leak_probability * 100).toFixed(0)}%
                    </span>
                  </div>
                  <Progress 
                    value={data.leak_probability * 100} 
                    className="h-2"
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Average Loss</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  <AlertTriangle className="h-6 w-6 text-orange-600" />
                  <div>
                    <div className="text-2xl font-bold">
                      {data.analysis.avg_loss_m3.toFixed(1)} m³
                    </div>
                    <div className="text-sm text-gray-500">
                      per hour
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>24-Hour Water Loss Pattern</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={historicalData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis label={{ value: 'Loss (%)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="loss" 
                    stroke="#ef4444" 
                    strokeWidth={2}
                    name="Water Loss %"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Flow Balance Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={[
                    { name: 'Flow In', value: 100, fill: '#3b82f6' },
                    { name: 'Flow Out', value: 100 - data.current_loss_percentage, fill: '#10b981' },
                    { name: 'Loss', value: data.current_loss_percentage, fill: '#ef4444' },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value">
                      {[
                        { name: 'Flow In', value: 100, fill: '#3b82f6' },
                        { name: 'Flow Out', value: 100 - data.current_loss_percentage, fill: '#10b981' },
                        { name: 'Loss', value: data.current_loss_percentage, fill: '#ef4444' },
                      ].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Analysis Insights</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${
                    data.analysis.night_flow_anomaly ? 'bg-red-500' : 'bg-green-500'
                  }`} />
                  <span className="text-sm">
                    Night Flow: {data.analysis.night_flow_anomaly ? 'Anomaly Detected' : 'Normal'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500" />
                  <span className="text-sm">
                    Max Loss: {data.analysis.max_loss_m3.toFixed(1)} m³/hour
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${
                    data.current_loss_percentage > 5 ? 'bg-orange-500' : 'bg-green-500'
                  }`} />
                  <span className="text-sm">
                    Status: {data.current_loss_percentage > 5 ? 'Above Threshold' : 'Within Limits'}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>

          {data.recommended_actions.length > 0 && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Recommended Actions</AlertTitle>
              <AlertDescription>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  {data.recommended_actions.map((action, index) => (
                    <li key={index} className="text-sm">{action}</li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}
        </>
      )}
    </div>
  );
}