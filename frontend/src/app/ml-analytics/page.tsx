'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { 
  BrainIcon,
  AlertTriangleIcon,
  TrendingUpIcon,
  ActivityIcon,
  ZapIcon,
  DropletIcon,
  RefreshCwIcon,
  TargetIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  InfoIcon
} from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, Cell
} from 'recharts';

interface MLSummary {
  models_active: number;
  anomalies_last_24h: number;
  accuracy_metrics: {
    anomaly_detection: number;
    demand_forecast: number;
    maintenance_prediction: number;
  };
  last_training: string;
  predictions_available: {
    anomaly_detection: boolean;
    demand_forecast: boolean;
    predictive_maintenance: boolean;
    water_quality: boolean;
  };
}

interface AnomalyResult {
  timestamp: string;
  anomaly_score: number;
  types: string[];
  metrics: {
    flow_rate: number;
    pressure: number;
    temperature: number;
  };
  severity: string;
}

interface DemandPrediction {
  timestamp: string;
  predicted_flow: number;
  confidence: number;
  hour_of_day: number;
  is_weekend: boolean;
}

const MLAnalyticsPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [mlSummary, setMlSummary] = useState<MLSummary | null>(null);
  const [selectedNode, setSelectedNode] = useState('DIST_001');
  const [selectedDistrict, setSelectedDistrict] = useState('DIST_001');
  const [loading, setLoading] = useState(false);
  const [anomalies, setAnomalies] = useState<AnomalyResult[]>([]);
  const [demandPredictions, setDemandPredictions] = useState<DemandPrediction[]>([]);
  const [modelTraining, setModelTraining] = useState(false);

  useEffect(() => {
    fetchMLSummary();
  }, []);

  const fetchMLSummary = async () => {
    try {
      const response = await fetch('/api/proxy/v1/ml/dashboard-summary');
      const data = await response.json();
      setMlSummary(data.summary);
    } catch (error) {
      console.error('Error fetching ML summary:', error);
    }
  };

  const trainModel = async () => {
    setModelTraining(true);
    try {
      const response = await fetch(
        `/api/proxy/v1/ml/train-anomaly-detector?node_id=${selectedNode}&days=7`,
        { method: 'POST' }
      );
      const data = await response.json();
      alert(`Model trained successfully! ${data.message}`);
      fetchMLSummary();
    } catch (error) {
      console.error('Error training model:', error);
      alert('Error training model');
    } finally {
      setModelTraining(false);
    }
  };

  const detectAnomalies = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/proxy/v1/ml/detect-anomalies?node_id=${selectedNode}&hours=24`
      );
      const data = await response.json();
      console.log('Anomaly detection response:', data);
      setAnomalies(data.anomalies || []);
      
      // Show a message if no anomalies found
      if (!data.anomalies || data.anomalies.length === 0) {
        console.log('No anomalies detected in the recent data');
      }
    } catch (error) {
      console.error('Error detecting anomalies:', error);
    } finally {
      setLoading(false);
    }
  };

  const predictDemand = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/proxy/v1/ml/predict-demand?district_id=${selectedDistrict}&hours_ahead=24`
      );
      const data = await response.json();
      setDemandPredictions(data.predictions || []);
    } catch (error) {
      console.error('Error predicting demand:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAnomalyIcon = (types: string[]) => {
    if (types.includes('LOW_PRESSURE')) return <AlertTriangleIcon className="h-5 w-5 text-red-500" />;
    if (types.includes('HIGH_FLOW')) return <TrendingUpIcon className="h-5 w-5 text-orange-500" />;
    if (types.includes('NIGHT_CONSUMPTION')) return <ClockIcon className="h-5 w-5 text-yellow-500" />;
    return <InfoIcon className="h-5 w-5 text-blue-500" />;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const accuracyData = mlSummary ? [
    { name: 'Anomaly Detection', value: mlSummary.accuracy_metrics.anomaly_detection * 100 },
    { name: 'Demand Forecast', value: mlSummary.accuracy_metrics.demand_forecast * 100 },
    { name: 'Maintenance', value: mlSummary.accuracy_metrics.maintenance_prediction * 100 }
  ] : [];

  const COLORS = ['#10B981', '#F59E0B', '#3B82F6', '#EF4444'];

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-3">
          <BrainIcon className="h-8 w-8 text-blue-600" />
          ML Analytics & Predictions
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          AI-powered insights for water infrastructure optimization
        </p>
      </div>

      {/* Summary Cards */}
      {mlSummary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Active Models</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {mlSummary.models_active}
                </p>
              </div>
              <BrainIcon className="h-8 w-8 text-blue-500 opacity-50" />
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Anomalies (24h)</p>
                <p className="text-2xl font-bold text-red-600">
                  {mlSummary.anomalies_last_24h}
                </p>
              </div>
              <AlertTriangleIcon className="h-8 w-8 text-red-500 opacity-50" />
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Avg Accuracy</p>
                <p className="text-2xl font-bold text-green-600">
                  {Math.round(
                    (mlSummary.accuracy_metrics.anomaly_detection +
                     mlSummary.accuracy_metrics.demand_forecast +
                     mlSummary.accuracy_metrics.maintenance_prediction) / 3 * 100
                  )}%
                </p>
              </div>
              <TargetIcon className="h-8 w-8 text-green-500 opacity-50" />
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Last Training</p>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {formatTimestamp(mlSummary.last_training)}
                </p>
              </div>
              <RefreshCwIcon className="h-8 w-8 text-purple-500 opacity-50" />
            </div>
          </Card>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b border-gray-200 dark:border-gray-700">
        {['overview', 'anomaly-detection', 'demand-forecast', 'maintenance'].map((tab) => (
          <button
            key={tab}
            className={`pb-3 px-1 ${
              activeTab === tab
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900'
            }`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && mlSummary && (
        <div className="space-y-6">
          {/* Model Accuracy */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Model Performance</h2>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={accuracyData}>
                <PolarGrid strokeDasharray="3 3" />
                <PolarAngleAxis dataKey="name" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="Accuracy"
                  dataKey="value"
                  stroke="#3B82F6"
                  fill="#3B82F6"
                  fillOpacity={0.6}
                />
                <Tooltip formatter={(value: any) => `${value.toFixed(1)}%`} />
              </RadarChart>
            </ResponsiveContainer>
          </Card>

          {/* Available Predictions */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Available Predictions</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(mlSummary.predictions_available).map(([key, available]) => (
                <div key={key} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  {available ? (
                    <CheckCircleIcon className="h-6 w-6 text-green-500" />
                  ) : (
                    <XCircleIcon className="h-6 w-6 text-gray-400" />
                  )}
                  <span className="text-sm font-medium capitalize">
                    {key.replace(/_/g, ' ')}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'anomaly-detection' && (
        <div className="space-y-6">
          {/* Controls */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Anomaly Detection</h2>
            <div className="flex gap-4 items-end">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Node Selection
                </label>
                <select
                  value={selectedNode}
                  onChange={(e) => setSelectedNode(e.target.value)}
                  className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="DIST_001">District 001</option>
                  <option value="DIST_002">District 002</option>
                  <option value="PUMP_001">Pump Station 001</option>
                  <option value="VALVE_001">Valve Station 001</option>
                </select>
              </div>
              <Button onClick={trainModel} disabled={modelTraining} variant="secondary">
                {modelTraining ? 'Training...' : 'Train Model'}
              </Button>
              <Button onClick={detectAnomalies} disabled={loading}>
                {loading ? 'Detecting...' : 'Detect Anomalies'}
              </Button>
            </div>
          </Card>

          {/* Anomaly Results */}
          {anomalies.length > 0 ? (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
                Detected Anomalies ({anomalies.length})
              </h3>
              <div className="space-y-3">
                {anomalies.slice(0, 10).map((anomaly, idx) => (
                  <div
                    key={idx}
                    className={`p-4 rounded-lg border ${
                      anomaly.severity === 'high'
                        ? 'border-red-300 bg-red-50 dark:bg-red-900/20'
                        : 'border-yellow-300 bg-yellow-50 dark:bg-yellow-900/20'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        {getAnomalyIcon(anomaly.types)}
                        <div>
                          <p className="font-medium text-gray-900 dark:text-gray-100">
                            {anomaly.types.join(', ')}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {formatTimestamp(anomaly.timestamp)}
                          </p>
                          <div className="mt-2 text-sm">
                            <span className="font-medium">Metrics:</span>{' '}
                            Flow: {anomaly.metrics.flow_rate.toFixed(1)} L/s,{' '}
                            Pressure: {anomaly.metrics.pressure.toFixed(1)} bar,{' '}
                            Temp: {anomaly.metrics.temperature.toFixed(1)}°C
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-600">Score</p>
                        <p className="text-lg font-bold text-red-600">
                          {anomaly.anomaly_score.toFixed(3)}
                        </p>
                      </div>
                    </div>
                                  </div>
              ))}
              </div>
            </Card>
          ) : (
            <Card className="p-6">
              <div className="text-center py-8">
                <AlertTriangleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  No Anomalies Detected
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Click "Detect Anomalies" to analyze recent sensor data for unusual patterns.
                </p>
              </div>
            </Card>
          )}
        </div>
      )}

      {activeTab === 'demand-forecast' && (
        <div className="space-y-6">
          {/* Controls */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Demand Forecasting</h2>
            <div className="flex gap-4 items-end">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  District Selection
                </label>
                <select
                  value={selectedDistrict}
                  onChange={(e) => setSelectedDistrict(e.target.value)}
                  className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="DIST_001">District 001 - Centro</option>
                  <option value="DIST_002">District 002 - Industrial</option>
                  <option value="DIST_003">District 003 - Residential</option>
                </select>
              </div>
              <Button onClick={predictDemand} disabled={loading}>
                {loading ? 'Predicting...' : 'Predict Demand (24h)'}
              </Button>
            </div>
          </Card>

          {/* Demand Chart */}
          {demandPredictions.length > 0 && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">24-Hour Demand Forecast</h3>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={demandPredictions}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(timestamp) => new Date(timestamp).getHours() + ':00'}
                  />
                  <YAxis label={{ value: 'Flow Rate (L/s)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip 
                    labelFormatter={(timestamp) => formatTimestamp(timestamp)}
                    formatter={(value: any) => [`${value.toFixed(1)} L/s`, 'Predicted Flow']}
                  />
                  <Area
                    type="monotone"
                    dataKey="predicted_flow"
                    stroke="#3B82F6"
                    fill="#3B82F6"
                    fillOpacity={0.3}
                  />
                  <Legend />
                </AreaChart>
              </ResponsiveContainer>
              
              {/* Peak Hours */}
              <div className="mt-4 grid grid-cols-2 gap-4">
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Peak Hours</p>
                  <p className="text-lg font-bold text-blue-600">7-9 AM, 7-9 PM</p>
                </div>
                <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Weekend Reduction</p>
                  <p className="text-lg font-bold text-green-600">-10%</p>
                </div>
              </div>
            </Card>
          )}
        </div>
      )}

      {activeTab === 'maintenance' && (
        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Predictive Maintenance</h2>
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mb-4">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <InfoIcon className="inline h-4 w-4 mr-1" />
                This feature analyzes equipment performance patterns to predict maintenance needs
                before failures occur.
              </p>
            </div>
            
            {/* Mock maintenance predictions */}
            <div className="space-y-4">
              {[
                { equipment: 'PUMP_001', risk: 0.78, priority: 'high', action: 'Schedule inspection within 48h' },
                { equipment: 'VALVE_003', risk: 0.45, priority: 'medium', action: 'Plan maintenance within 2 weeks' },
                { equipment: 'SENSOR_012', risk: 0.92, priority: 'critical', action: 'Immediate calibration required' },
                { equipment: 'PUMP_004', risk: 0.23, priority: 'low', action: 'Continue monitoring' }
              ].map((item, idx) => (
                <div key={idx} className={`p-4 rounded-lg border ${
                  item.priority === 'critical' ? 'border-red-300 bg-red-50' :
                  item.priority === 'high' ? 'border-orange-300 bg-orange-50' :
                  item.priority === 'medium' ? 'border-yellow-300 bg-yellow-50' :
                  'border-green-300 bg-green-50'
                } dark:bg-opacity-20`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-gray-900 dark:text-gray-100">{item.equipment}</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{item.action}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-600 dark:text-gray-400">Risk Score</p>
                      <p className={`text-2xl font-bold ${
                        item.risk > 0.7 ? 'text-red-600' :
                        item.risk > 0.4 ? 'text-yellow-600' :
                        'text-green-600'
                      }`}>
                        {(item.risk * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default MLAnalyticsPage; 