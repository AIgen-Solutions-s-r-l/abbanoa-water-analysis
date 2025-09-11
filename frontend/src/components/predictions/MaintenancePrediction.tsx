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
  { id: 'PUMP001', name: 'Main Pump Station 1' },
  { id: 'PUMP002', name: 'Main Pump Station 2' },
  { id: 'VALVE001', name: 'Control Valve A' },
  { id: 'VALVE002', name: 'Control Valve B' },
  { id: 'SENSOR001', name: 'Pressure Sensor Unit 1' },
];

export default function MaintenancePrediction() {
  const [loading, setLoading] = useState(false);
  const [selectedEquipment, setSelectedEquipment] = useState('PUMP001');
  const [data, setData] = useState<MaintenanceData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchMaintenancePrediction = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `/api/v1/predictions/maintenance?equipment_id=${selectedEquipment}`
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
    </div>
  );
}