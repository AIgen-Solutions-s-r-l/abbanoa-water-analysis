'use client';

import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Zap, DollarSign, TrendingDown, Clock } from 'lucide-react';

interface OptimizationResult {
  schedule: number[];
  baseline_cost: number;
  optimized_cost: number;
  estimated_savings: number;
  savings_percentage: number;
  peak_hours_usage: number;
  off_peak_hours_usage: number;
}

export default function EnergyOptimization() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [zoneId, setZoneId] = useState('1');
  const [peakRate, setPeakRate] = useState('0.25');
  const [offPeakRate, setOffPeakRate] = useState('0.10');
  const [error, setError] = useState<string | null>(null);

  const runOptimization = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/predictions/optimize-energy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          zone_id: parseInt(zoneId),
          tariffs: {
            peak: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            off_peak: [0, 1, 2, 3, 4, 5, 6, 7, 21, 22, 23],
            rates: {
              peak: parseFloat(peakRate),
              off_peak: parseFloat(offPeakRate),
            },
          },
        }),
      });

      if (!response.ok) {
        throw new Error('Optimization failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const chartData = result
    ? result.schedule.map((value, hour) => ({
        hour: `${hour}:00`,
        consumption: Math.round(value * 100) / 100,
        type: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20].includes(hour)
          ? 'Peak'
          : 'Off-Peak',
      }))
    : [];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <Label htmlFor="zone">Zone ID</Label>
          <Input
            id="zone"
            type="number"
            value={zoneId}
            onChange={(e) => setZoneId(e.target.value)}
            placeholder="Enter zone ID"
          />
        </div>
        <div>
          <Label htmlFor="peak-rate">Peak Rate (€/kWh)</Label>
          <Input
            id="peak-rate"
            type="number"
            step="0.01"
            value={peakRate}
            onChange={(e) => setPeakRate(e.target.value)}
          />
        </div>
        <div>
          <Label htmlFor="off-peak-rate">Off-Peak Rate (€/kWh)</Label>
          <Input
            id="off-peak-rate"
            type="number"
            step="0.01"
            value={offPeakRate}
            onChange={(e) => setOffPeakRate(e.target.value)}
          />
        </div>
      </div>

      <Button onClick={runOptimization} disabled={loading} className="w-full md:w-auto">
        <Zap className="mr-2 h-4 w-4" />
        {loading ? 'Optimizing...' : 'Run Optimization'}
      </Button>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {result && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="h-5 w-5 text-green-600" />
                  <span className="text-sm text-gray-600">Estimated Savings</span>
                </div>
                <div className="text-2xl font-bold text-green-600">
                  €{result.estimated_savings.toFixed(2)}
                </div>
                <div className="text-sm text-gray-500">
                  {result.savings_percentage.toFixed(1)}% reduction
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingDown className="h-5 w-5 text-blue-600" />
                  <span className="text-sm text-gray-600">Baseline Cost</span>
                </div>
                <div className="text-2xl font-bold">
                  €{result.baseline_cost.toFixed(2)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="h-5 w-5 text-orange-600" />
                  <span className="text-sm text-gray-600">Optimized Cost</span>
                </div>
                <div className="text-2xl font-bold text-orange-600">
                  €{result.optimized_cost.toFixed(2)}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="h-5 w-5 text-purple-600" />
                  <span className="text-sm text-gray-600">Peak/Off-Peak</span>
                </div>
                <div className="text-lg font-semibold">
                  {result.peak_hours_usage.toFixed(0)} / {result.off_peak_hours_usage.toFixed(0)}
                </div>
                <div className="text-sm text-gray-500">m³</div>
              </CardContent>
            </Card>
          </div>

          <div className="bg-white p-4 rounded-lg border">
            <h3 className="text-lg font-semibold mb-4">Optimized Pumping Schedule (24 hours)</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis label={{ value: 'Pumping Volume (m³)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Bar 
                  dataKey="consumption" 
                  fill={(entry: any) => entry.type === 'Peak' ? '#ef4444' : '#10b981'}
                  name="Pumping Volume"
                />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 flex gap-4 justify-center">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-500 rounded"></div>
                <span className="text-sm">Peak Hours (Higher Rate)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-500 rounded"></div>
                <span className="text-sm">Off-Peak Hours (Lower Rate)</span>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Optimization Strategy</h4>
            <p className="text-sm text-gray-700">
              The ML model has optimized the pumping schedule by shifting {result.savings_percentage.toFixed(1)}% 
              of the load from peak hours to off-peak hours, resulting in significant cost savings while 
              maintaining required water supply levels.
            </p>
          </div>
        </>
      )}
    </div>
  );
}