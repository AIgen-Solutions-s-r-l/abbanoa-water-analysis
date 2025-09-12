'use client';

import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, Cell } from 'recharts';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
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

const ZONES = [
  { id: 'zone_cagliari_centro', name: 'Cagliari Centro' },
  { id: 'zone_cagliari_nord', name: 'Cagliari Nord' },
  { id: 'zone_quartucciu', name: 'Quartucciu' },
  { id: 'zone_selargius', name: 'Selargius' },
];

export default function EnergyOptimization() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [zoneId, setZoneId] = useState('zone_cagliari_nord');
  const [peakRate, setPeakRate] = useState('0.25');
  const [offPeakRate, setOffPeakRate] = useState('0.10');
  const [error, setError] = useState<string | null>(null);

  const runOptimization = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/proxy/v1/predictions/optimize-energy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          zone_id: zoneId,
          tariffs: {
            peak: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            off_peak: [0, 1, 2, 3, 4, 5, 6, 7, 21, 22, 23],
            rates: {
              peak_rate: parseFloat(peakRate),
              off_peak_rate: parseFloat(offPeakRate),
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
          <Label htmlFor="zone">Zone</Label>
          <Select value={zoneId} onValueChange={setZoneId}>
            <SelectTrigger id="zone">
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

          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">Optimized Pumping Schedule (24 hours)</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                <XAxis 
                  dataKey="hour" 
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  axisLine={{ stroke: '#6b7280' }}
                />
                <YAxis 
                  label={{ value: 'Pumping Volume (m³)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#6b7280' } }}
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  axisLine={{ stroke: '#6b7280' }}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '6px',
                    color: '#f9fafb'
                  }}
                />
                <Legend 
                  wrapperStyle={{ color: '#6b7280' }}
                />
                <Bar 
                  dataKey="consumption" 
                  name="Pumping Volume"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.type === 'Peak' ? '#ef4444' : '#10b981'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 flex gap-4 justify-center">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-500 rounded"></div>
                <span className="text-sm text-gray-700 dark:text-gray-300">Peak Hours (Higher Rate)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-500 rounded"></div>
                <span className="text-sm text-gray-700 dark:text-gray-300">Off-Peak Hours (Lower Rate)</span>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
            <h4 className="font-semibold mb-2 text-blue-900 dark:text-blue-100">Optimization Strategy</h4>
            <p className="text-sm text-blue-800 dark:text-blue-200">
              The ML model has optimized the pumping schedule by shifting {result.savings_percentage.toFixed(1)}% 
              of the load from peak hours to off-peak hours, resulting in significant cost savings while 
              maintaining required water supply levels.
            </p>
          </div>

          {/* Mathematical Model Explanation */}
          <div className="bg-gray-50 dark:bg-gray-900/50 p-6 rounded-lg border border-gray-200 dark:border-gray-700 mt-6">
            <h3 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">⚡ Energy Cost Optimization Model</h3>
            <div className="space-y-4 text-sm text-gray-700 dark:text-gray-300">
              
              <div>
                <h4 className="font-semibold text-blue-600 dark:text-blue-400 mb-2">Objective Function</h4>
                <div className="bg-white dark:bg-gray-800 p-4 rounded border">
                  <p className="mb-2">Minimizza il costo totale dell'energia rispettando i vincoli di fornitura:</p>
                  <code className="block bg-gray-100 dark:bg-gray-700 p-2 rounded font-mono text-xs">
                    min C = ∑(t=0 to 23) [P(t) × E(t) × Q(t)]
                  </code>
                  <div className="mt-2 space-y-1">
                    <p><strong>C</strong>: Costo energetico totale giornaliero</p>
                    <p><strong>P(t)</strong>: Prezzo energia all'ora t (€/kWh)</p>
                    <p><strong>E(t)</strong>: Efficienza pompa all'ora t</p>
                    <p><strong>Q(t)</strong>: Volume pompato all'ora t (m³)</p>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-green-600 dark:text-green-400 mb-2">Constraint Optimization</h4>
                <div className="bg-white dark:bg-gray-800 p-4 rounded border">
                  <p className="mb-2">Vincoli operativi per garantire la fornitura:</p>
                  <div className="space-y-2">
                    <code className="block bg-gray-100 dark:bg-gray-700 p-2 rounded font-mono text-xs">
                      ∑(t=0 to 23) Q(t) = D_daily  (Vincolo di domanda)
                    </code>
                    <code className="block bg-gray-100 dark:bg-gray-700 p-2 rounded font-mono text-xs">
                      Q_min ≤ Q(t) ≤ Q_max  ∀t  (Limiti capacità)
                    </code>
                    <code className="block bg-gray-100 dark:bg-gray-700 p-2 rounded font-mono text-xs">
                      |Q(t) - Q(t-1)| ≤ ΔQ_max  (Variazione graduale)
                    </code>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-orange-600 dark:text-orange-400 mb-2">Load Shifting Algorithm</h4>
                <div className="bg-white dark:bg-gray-800 p-4 rounded border">
                  <p className="mb-2">Algoritmo di spostamento del carico dalle ore di punta:</p>
                  <code className="block bg-gray-100 dark:bg-gray-700 p-2 rounded font-mono text-xs">
                    Q_opt(t) = Q_base(t) + β × (P_off - P(t)) × γ(t)
                  </code>
                  <div className="mt-2 space-y-1">
                    <p><strong>Q_base(t)</strong>: Domanda baseline all'ora t</p>
                    <p><strong>β</strong>: Fattore di elasticità del carico</p>
                    <p><strong>P_off</strong>: Prezzo off-peak medio</p>
                    <p><strong>γ(t)</strong>: Fattore di flessibilità operativa</p>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </>
      )}
    </div>
  );
}