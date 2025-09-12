'use client';

import React, { useState, useEffect } from 'react';
import { RadialBarChart, RadialBar, Legend, ResponsiveContainer, PolarAngleAxis } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertTriangle, CheckCircle, Clock, Wrench, Activity } from 'lucide-react';

interface MaintenanceData {
  risk_score: 'low' | 'medium' | 'high' | 'critical';
  days_to_maintenance: number;
  failure_probability: number;
  confidence: number;
  risk_factors: Array<{
    factor: string;
    severity: string;
    days_to_failure?: number;
    anomaly_rate?: number;
    age_score?: number;
  }>;
  recommendations: string[];
}

const EQUIPMENT_LIST = [
  { id: 'cagliari_pump_01', name: 'Cagliari Centro - Pump Station' },
  { id: 'cagliari_pump_02', name: 'Cagliari Nord - Pump Station' },
  { id: 'quartucciu_valve_01', name: 'Quartucciu - Control Valve' },
  { id: 'selargius_valve_01', name: 'Selargius - Control Valve' },
  { id: 'centro_sensor_01', name: 'Centro - Pressure Sensor' },
];

export default function MaintenancePrediction() {
  const [loading, setLoading] = useState(false);
  const [selectedEquipment, setSelectedEquipment] = useState('cagliari_pump_01');
  const [data, setData] = useState<MaintenanceData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchMaintenancePrediction = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `/api/proxy/v1/predictions/maintenance?equipment_id=${selectedEquipment}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch maintenance prediction');
      }
      
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMaintenancePrediction();
  }, [selectedEquipment]);

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-600 bg-green-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'high': return 'text-orange-600 bg-orange-50';
      case 'critical': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case 'low': return <CheckCircle className="h-6 w-6 text-green-600" />;
      case 'medium': return <Clock className="h-6 w-6 text-yellow-600" />;
      case 'high': return <AlertTriangle className="h-6 w-6 text-orange-600" />;
      case 'critical': return <AlertTriangle className="h-6 w-6 text-red-600" />;
      default: return <Activity className="h-6 w-6 text-gray-600" />;
    }
  };

  const gaugeData = data ? [
    {
      name: 'Failure Risk',
      value: data.failure_probability * 100,
      fill: data.risk_score === 'critical' ? '#ef4444' : 
            data.risk_score === 'high' ? '#f97316' : 
            data.risk_score === 'medium' ? '#eab308' : '#10b981',
    },
  ] : [];

  return (
    <div className="space-y-6">
      <div className="flex gap-4 items-center">
        <Select value={selectedEquipment} onValueChange={setSelectedEquipment}>
          <SelectTrigger className="w-64">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {EQUIPMENT_LIST.map((eq) => (
              <SelectItem key={eq.id} value={eq.id}>
                {eq.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button onClick={fetchMaintenancePrediction} disabled={loading}>
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Risk Assessment</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  {getRiskIcon(data.risk_score)}
                  <div>
                    <div className={`text-2xl font-bold capitalize ${getRiskColor(data.risk_score).split(' ')[0]}`}>
                      {data.risk_score}
                    </div>
                    <div className="text-sm text-gray-500">
                      {(data.confidence * 100).toFixed(0)}% confidence
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Time to Maintenance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  <Wrench className="h-6 w-6 text-blue-600" />
                  <div>
                    <div className="text-2xl font-bold">
                      {data.days_to_maintenance} days
                    </div>
                    <div className="text-sm text-gray-500">
                      Recommended window
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Failure Probability</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={120}>
                  <RadialBarChart 
                    cx="50%" 
                    cy="50%" 
                    innerRadius="60%" 
                    outerRadius="90%" 
                    barSize={10} 
                    data={gaugeData}
                  >
                    <PolarAngleAxis
                      type="number"
                      domain={[0, 100]}
                      dataKey="value"
                      angleAxisId={0}
                      tick={false}
                    />
                    <RadialBar
                      background
                      dataKey="value"
                      cornerRadius={10}
                      fill={gaugeData[0]?.fill}
                    />
                    <text 
                      x="50%" 
                      y="50%" 
                      textAnchor="middle" 
                      dominantBaseline="middle" 
                      className="text-2xl font-bold"
                    >
                      {(data.failure_probability * 100).toFixed(0)}%
                    </text>
                  </RadialBarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {data.risk_factors.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Risk Factors Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {data.risk_factors.map((factor, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <Badge 
                          variant={factor.severity === 'high' ? 'destructive' : 'secondary'}
                        >
                          {factor.severity}
                        </Badge>
                        <span className="font-medium capitalize">
                          {factor.factor.replace('_', ' ')}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">
                        {factor.days_to_failure && (
                          <span>{factor.days_to_failure.toFixed(0)} days to critical</span>
                        )}
                        {factor.anomaly_rate && (
                          <span>{(factor.anomaly_rate * 100).toFixed(1)}% anomaly rate</span>
                        )}
                        {factor.age_score && (
                          <span>Age score: {(factor.age_score * 100).toFixed(0)}%</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Recommended Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {data.recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    <span className="text-sm">{rec}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Mathematical Model Explanation */}
      <div className="bg-gray-50 dark:bg-gray-900/50 p-6 rounded-lg border border-gray-200 dark:border-gray-700 mt-6">
        <h3 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">🔧 Predictive Maintenance Model</h3>
        <div className="space-y-4 text-sm text-gray-700 dark:text-gray-300">
          
          <div>
            <h4 className="font-semibold text-blue-600 dark:text-blue-400 mb-2">Hazard Function</h4>
            <div className="bg-white dark:bg-gray-800 p-4 rounded border">
              <p className="mb-2">Funzione di rischio per predire il tempo al guasto:</p>
              <code className="block bg-gray-100 dark:bg-gray-700 p-2 rounded font-mono text-xs">
                h(t) = h_0 × exp(β_1×P(t) + β_2×V(t) + β_3×T(t) + β_4×Age)
              </code>
              <div className="mt-2 space-y-1">
                <p><strong>h(t)</strong>: Tasso di guasto istantaneo</p>
                <p><strong>h_0</strong>: Tasso di guasto baseline</p>
                <p><strong>P(t)</strong>: Variazione di pressione</p>
                <p><strong>V(t)</strong>: Livello vibrazione</p>
                <p><strong>T(t)</strong>: Temperatura operativa</p>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-orange-600 dark:text-orange-400 mb-2">Weibull Reliability Model</h4>
            <div className="bg-white dark:bg-gray-800 p-4 rounded border">
              <p className="mb-2">Distribuzione di Weibull per modellare l'affidabilità:</p>
              <code className="block bg-gray-100 dark:bg-gray-700 p-2 rounded font-mono text-xs">
                R(t) = exp(-(λ × t)^β)
              </code>
              <div className="mt-2 space-y-1">
                <p><strong>R(t)</strong>: Probabilità di sopravvivenza al tempo t</p>
                <p><strong>λ</strong>: Parametro di scala</p>
                <p><strong>β</strong>: Parametro di forma (shape parameter)</p>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-red-600 dark:text-red-400 mb-2">Degradation Index</h4>
            <div className="bg-white dark:bg-gray-800 p-4 rounded border">
              <p className="mb-2">Indice di degrado basato sui sensori per quantificare l'usura:</p>
              <code className="block bg-gray-100 dark:bg-gray-700 p-2 rounded font-mono text-xs">
                DI(t) = w_1×σ_P + w_2×|ΔV| + w_3×max(T-T_nominal, 0) + w_4×(Age/Age_design)
              </code>
              <div className="mt-2 space-y-1">
                <p><strong>σ_P</strong>: Deviazione standard pressione</p>
                <p><strong>|ΔV|</strong>: Variazione assoluta vibrazione</p>
                <p><strong>T_nominal</strong>: Temperatura operativa nominale</p>
                <p><strong>w_i</strong>: Pesi ottimizzati per tipo equipaggiamento</p>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-green-600 dark:text-green-400 mb-2">Maintenance Scheduling</h4>
            <div className="bg-white dark:bg-gray-800 p-4 rounded border">
              <p className="mb-2">Ottimizzazione della schedulazione manutenzione:</p>
              <code className="block bg-gray-100 dark:bg-gray-700 p-2 rounded font-mono text-xs">
                t_opt = arg min [C_maint×R(t) + C_failure×(1-R(t)) + C_downtime]
              </code>
              <div className="mt-2 space-y-1">
                <p><strong>C_maint</strong>: Costo manutenzione preventiva</p>
                <p><strong>C_failure</strong>: Costo guasto imprevisto</p>
                <p><strong>C_downtime</strong>: Costo per fermo impianto</p>
                <p><strong>t_opt</strong>: Tempo ottimale per manutenzione</p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}