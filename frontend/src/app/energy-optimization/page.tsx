'use client';

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { 
  BatteryIcon,
  ZapIcon,
  TrendingDownIcon,
  ActivityIcon,
  ThermometerIcon,
  WindIcon,
  SunIcon,
  MoonIcon,
  AlertCircleIcon,
  CheckCircleIcon,
  PlayIcon,
  PauseIcon,
  SettingsIcon,
  DollarSignIcon,
  LeafIcon
} from 'lucide-react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  RadialBarChart, RadialBar, Sankey,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell, PieChart, Pie
} from 'recharts';

interface EnergyMetrics {
  currentPowerKw: number;
  dailyConsumptionKwh: number;
  dailySavingsKwh: number;
  co2SavedKg: number;
  costSavingsEur: number;
  efficiency: number;
  inertiaStatus: {
    momentum: number;
    coastingTime: number;
    pumpsCoasting: number;
    totalPumps: number;
  };
  thermalStatus: {
    avgExpansion: number;
    energyHarvested: number;
    anomaliesDetected: number;
  };
}

const EnergyOptimizationPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [energyMetrics, setEnergyMetrics] = useState<EnergyMetrics>({
    currentPowerKw: 245.8,
    dailyConsumptionKwh: 4892,
    dailySavingsKwh: 1223,
    co2SavedKg: 489.2,
    costSavingsEur: 183.45,
    efficiency: 87.5,
    inertiaStatus: {
      momentum: 45000,
      coastingTime: 7.5,
      pumpsCoasting: 3,
      totalPumps: 12
    },
    thermalStatus: {
      avgExpansion: 12.5,
      energyHarvested: 2.4,
      anomaliesDetected: 0
    }
  });

  const [optimizationMode, setOptimizationMode] = useState('auto');
  const [isOptimizing, setIsOptimizing] = useState(true);

  // Mock real-time power consumption data
  const [powerHistory, setPowerHistory] = useState<any[]>([]);
  
  useEffect(() => {
    // Simulate real-time data
    const interval = setInterval(() => {
      const now = new Date();
      const newPower = 200 + Math.sin(now.getTime() / 10000) * 50 + Math.random() * 20;
      
      setPowerHistory(prev => {
        const updated = [...prev, {
          time: now.toLocaleTimeString(),
          power: newPower,
          optimized: newPower * 0.75,
          savings: newPower * 0.25
        }];
        return updated.slice(-20); // Keep last 20 points
      });

      // Only update changing values
      setEnergyMetrics(prev => ({
        ...prev,
        currentPowerKw: newPower,
        efficiency: 85 + Math.random() * 10,
        inertiaStatus: {
          ...prev.inertiaStatus,
          coastingTime: 7.5 - (Math.random() * 2)
        }
      }));
    }, 5000); // Reduced frequency to prevent flickering

    return () => clearInterval(interval);
  }, []);

  // Memoize static data to prevent re-creation
  const energyFlowData = useMemo(() => ({
    nodes: [
      { name: 'Grid Power' },
      { name: 'Pumps' },
      { name: 'VSD Optimization' },
      { name: 'Inertia Coasting' },
      { name: 'Thermal Recovery' },
      { name: 'Water Delivered' },
      { name: 'Energy Saved' }
    ],
    links: [
      { source: 0, target: 1, value: 245.8 },
      { source: 1, target: 2, value: 49.2 },
      { source: 1, target: 3, value: 36.9 },
      { source: 1, target: 4, value: 2.4 },
      { source: 1, target: 5, value: 157.3 },
      { source: 2, target: 6, value: 49.2 },
      { source: 3, target: 6, value: 36.9 },
      { source: 4, target: 6, value: 2.4 }
    ]
  }), []);

  const pumpEfficiencyData = useMemo(() => [
    { name: 'PUMP_001', current: 82, optimal: 95, status: 'running' },
    { name: 'PUMP_002', current: 0, optimal: 0, status: 'coasting' },
    { name: 'PUMP_003', current: 78, optimal: 92, status: 'running' },
    { name: 'PUMP_004', current: 0, optimal: 0, status: 'coasting' },
    { name: 'PUMP_005', current: 88, optimal: 94, status: 'running' },
    { name: 'PUMP_006', current: 0, optimal: 0, status: 'coasting' }
  ], []);

  const thermalExpansionData = useMemo(() => [
    { segment: 'North Pipeline', material: 'Steel', expansion: 22, temperature: 28 },
    { segment: 'South Pipeline', material: 'PVC', expansion: 145, temperature: 32 },
    { segment: 'East Pipeline', material: 'HDPE', expansion: 210, temperature: 30 },
    { segment: 'West Pipeline', material: 'Steel', expansion: 18, temperature: 26 }
  ], []);

  const savingsBreakdown = useMemo(() => [
    { name: 'VSD Control', value: 35, color: '#3B82F6' },
    { name: 'Inertia Coasting', value: 25, color: '#10B981' },
    { name: 'Off-Peak Scheduling', value: 20, color: '#F59E0B' },
    { name: 'Thermal Optimization', value: 15, color: '#8B5CF6' },
    { name: 'PAT Recovery', value: 5, color: '#EF4444' }
  ], []);

  const toggleOptimization = useCallback(() => {
    setIsOptimizing(prev => !prev);
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Disclaimer */}
      <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <div className="flex items-start gap-3">
          <AlertCircleIcon className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-1">Demo Mode - Synthetic Data</h3>
            <p className="text-sm text-blue-800 dark:text-blue-200">
              This dashboard is currently displaying synthetic data for demonstration purposes. 
              In a production environment, these metrics would be connected to real-time sensors, 
              SCADA systems, and actual pump controllers. The algorithms and optimization strategies 
              shown are based on real physics and industry best practices.
            </p>
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-3">
              <BatteryIcon className="h-8 w-8 text-green-600" />
              Energy Optimization Center
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              AI-powered energy management for sustainable water infrastructure
            </p>
          </div>
          <div className="flex gap-4">
            <Button
              onClick={toggleOptimization}
              variant={isOptimizing ? 'primary' : 'secondary'}
              className="flex items-center gap-2"
            >
              {isOptimizing ? (
                <>
                  <PauseIcon className="h-4 w-4" />
                  Pause Optimization
                </>
              ) : (
                <>
                  <PlayIcon className="h-4 w-4" />
                  Start Optimization
                </>
              )}
            </Button>
            <Button variant="ghost" className="flex items-center gap-2">
              <SettingsIcon className="h-4 w-4" />
              Settings
            </Button>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
        <Card className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Current Power</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {energyMetrics.currentPowerKw.toFixed(1)} kW
              </p>
              <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                {isOptimizing ? '↓ Optimizing' : 'Not optimized'}
              </p>
            </div>
            <ZapIcon className="h-8 w-8 text-blue-500 opacity-50" />
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Daily Savings</p>
              <p className="text-2xl font-bold text-green-600">
                €{energyMetrics.costSavingsEur.toFixed(2)}
              </p>
              <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                {energyMetrics.dailySavingsKwh} kWh saved
              </p>
            </div>
            <DollarSignIcon className="h-8 w-8 text-green-500 opacity-50" />
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">System Efficiency</p>
              <p className="text-2xl font-bold text-purple-600">
                {energyMetrics.efficiency.toFixed(1)}%
              </p>
              <p className="text-xs text-purple-600 dark:text-purple-400 mt-1">
                Target: 95%
              </p>
            </div>
            <ActivityIcon className="h-8 w-8 text-purple-500 opacity-50" />
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Pumps Coasting</p>
              <p className="text-2xl font-bold text-orange-600">
                {energyMetrics.inertiaStatus.pumpsCoasting}/{energyMetrics.inertiaStatus.totalPumps}
              </p>
              <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
                {energyMetrics.inertiaStatus.coastingTime.toFixed(1)} min remaining
              </p>
            </div>
            <WindIcon className="h-8 w-8 text-orange-500 opacity-50" />
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900/20 dark:to-emerald-800/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">CO₂ Reduced</p>
              <p className="text-2xl font-bold text-emerald-600">
                {energyMetrics.co2SavedKg.toFixed(0)} kg
              </p>
              <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-1">
                Daily reduction
              </p>
            </div>
            <LeafIcon className="h-8 w-8 text-emerald-500 opacity-50" />
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b border-gray-200 dark:border-gray-700">
        {['overview', 'inertia-control', 'thermal-dynamics', 'scheduling', 'analytics'].map((tab) => (
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
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Real-time Power Consumption */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Real-time Power Optimization</h2>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={powerHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis label={{ value: 'Power (kW)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="power"
                  stackId="1"
                  stroke="#EF4444"
                  fill="#FEE2E2"
                  name="Original"
                />
                <Area
                  type="monotone"
                  dataKey="savings"
                  stackId="1"
                  stroke="#10B981"
                  fill="#D1FAE5"
                  name="Saved"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>

          {/* Energy Flow Visualization */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Energy Flow Analysis</h2>
            <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
                Interactive Sankey diagram showing energy distribution and savings
              </p>
              {/* Placeholder for Sankey - would need additional library */}
              <div className="mt-4 grid grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-3xl font-bold text-gray-900 dark:text-gray-100">245.8 kW</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Grid Input</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-blue-600">88.5 kW</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total Saved</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-green-600">157.3 kW</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Effective Use</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-purple-600">64%</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Net Efficiency</p>
                </div>
              </div>
            </div>
          </Card>

          {/* Savings Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Optimization Methods</h3>
              <div style={{ width: '100%', height: 250 }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={savingsBreakdown}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      isAnimationActive={false}
                    >
                      {savingsBreakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: any) => `${value}%`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 space-y-2">
                {savingsBreakdown.map((item, index) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="text-gray-700 dark:text-gray-300">{item.name}</span>
                    </div>
                    <span className="font-semibold text-gray-900 dark:text-gray-100">{item.value}%</span>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Monthly Trend</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={[
                  { month: 'Jan', consumption: 148000, optimized: 111000 },
                  { month: 'Feb', consumption: 142000, optimized: 106500 },
                  { month: 'Mar', consumption: 145000, optimized: 108750 },
                  { month: 'Apr', consumption: 150000, optimized: 105000 },
                  { month: 'May', consumption: 155000, optimized: 100750 },
                  { month: 'Jun', consumption: 160000, optimized: 96000 }
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis label={{ value: 'kWh', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="consumption" stroke="#EF4444" name="Baseline" strokeWidth={2} />
                  <Line type="monotone" dataKey="optimized" stroke="#10B981" name="Optimized" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </div>
        </div>
      )}

      {activeTab === 'inertia-control' && (
        <div className="space-y-6">
          {/* Inertia Status */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Hydraulic Inertia Management</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Network Momentum</p>
                <p className="text-2xl font-bold text-blue-600">
                  {(energyMetrics.inertiaStatus.momentum / 1000).toFixed(1)} ton⋅m/s
                </p>
              </div>
              <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Coasting Potential</p>
                <p className="text-2xl font-bold text-green-600">
                  {energyMetrics.inertiaStatus.coastingTime.toFixed(1)} minutes
                </p>
              </div>
              <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Energy Saved</p>
                <p className="text-2xl font-bold text-purple-600">
                  36.9 kW
                </p>
              </div>
            </div>

            {/* Pump Status Grid */}
            <h3 className="text-lg font-semibold mb-3">Pump Status & Efficiency</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {pumpEfficiencyData.map((pump, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border-2 ${
                    pump.status === 'coasting'
                      ? 'border-green-400 bg-green-50 dark:bg-green-900/20'
                      : 'border-gray-200 bg-gray-50 dark:bg-gray-800'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100">{pump.name}</h4>
                    {pump.status === 'coasting' ? (
                      <WindIcon className="h-5 w-5 text-green-600" />
                    ) : (
                      <ActivityIcon className="h-5 w-5 text-blue-600" />
                    )}
                  </div>
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Status</span>
                      <span className={pump.status === 'coasting' ? 'text-green-600 font-medium' : 'text-blue-600'}>
                        {pump.status.toUpperCase()}
                      </span>
                    </div>
                    {pump.status === 'running' && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">Efficiency</span>
                        <span className="font-medium">{pump.current}%</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Coasting Algorithm Control */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Coasting Algorithm Settings</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div>
                  <h4 className="font-medium">Minimum Pressure Threshold</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Pumps will restart when pressure drops below this value
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    className="w-20 px-3 py-1 border rounded"
                    defaultValue="3.5"
                    step="0.1"
                  />
                  <span className="text-sm">bar</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div>
                  <h4 className="font-medium">Momentum Threshold</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Minimum momentum required to initiate coasting
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    className="w-24 px-3 py-1 border rounded"
                    defaultValue="40000"
                    step="1000"
                  />
                  <span className="text-sm">kg⋅m/s</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'thermal-dynamics' && (
        <div className="space-y-6">
          {/* Thermal Expansion Monitoring */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Thermal Expansion Energy Recovery</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Energy Harvested</p>
                    <p className="text-2xl font-bold text-orange-600">
                      {energyMetrics.thermalStatus.energyHarvested} Wh
                    </p>
                    <p className="text-xs text-orange-600 mt-1">Today</p>
                  </div>
                  <SunIcon className="h-8 w-8 text-orange-500 opacity-50" />
                </div>
              </div>
              
              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Avg Expansion</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {energyMetrics.thermalStatus.avgExpansion} mm/km
                    </p>
                    <p className="text-xs text-blue-600 mt-1">Current</p>
                  </div>
                  <ThermometerIcon className="h-8 w-8 text-blue-500 opacity-50" />
                </div>
              </div>
              
              <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Anomalies</p>
                    <p className="text-2xl font-bold text-green-600">
                      {energyMetrics.thermalStatus.anomaliesDetected}
                    </p>
                    <p className="text-xs text-green-600 mt-1">Detected</p>
                  </div>
                  <CheckCircleIcon className="h-8 w-8 text-green-500 opacity-50" />
                </div>
              </div>
            </div>

            {/* Pipeline Thermal Status */}
            <h3 className="text-lg font-semibold mb-3">Pipeline Thermal Status</h3>
            <div className="space-y-3">
              {thermalExpansionData.map((pipeline, idx) => (
                <div key={idx} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-gray-100">{pipeline.segment}</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Material: {pipeline.material}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-orange-600">{pipeline.temperature}°C</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {pipeline.expansion} μm/m expansion
                      </p>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-red-500 h-2 rounded-full"
                      style={{ width: `${(pipeline.temperature / 40) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Piezoelectric Harvesting Status */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Piezoelectric Energy Harvesting</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={[
                { location: 'Junction A1', power: 0.8, efficiency: 85 },
                { location: 'Junction B2', power: 1.2, efficiency: 92 },
                { location: 'Junction C3', power: 0.5, efficiency: 78 },
                { location: 'Junction D4', power: 0.9, efficiency: 88 }
              ]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="location" />
                <YAxis yAxisId="left" label={{ value: 'Power (W)', angle: -90, position: 'insideLeft' }} />
                <YAxis yAxisId="right" orientation="right" label={{ value: 'Efficiency (%)', angle: 90, position: 'insideRight' }} />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="power" fill="#F59E0B" name="Power Generated" />
                <Bar yAxisId="right" dataKey="efficiency" fill="#10B981" name="Efficiency" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>
      )}

      {activeTab === 'scheduling' && (
        <div className="space-y-6">
          {/* Smart Scheduling */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Intelligent Pump Scheduling</h2>
            
            {/* Energy Price Chart */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-3">Energy Price & Pump Schedule</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={Array.from({ length: 24 }, (_, i) => ({
                  hour: i,
                  price: i >= 7 && i <= 9 || i >= 18 && i <= 21 
                    ? 0.18 + Math.random() * 0.05 
                    : 0.08 + Math.random() * 0.03,
                  pumps: i >= 7 && i <= 9 || i >= 18 && i <= 21 
                    ? 8 + Math.floor(Math.random() * 4)
                    : 3 + Math.floor(Math.random() * 3)
                }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" label={{ value: 'Hour of Day', position: 'insideBottom', offset: -5 }} />
                  <YAxis yAxisId="left" label={{ value: '€/kWh', angle: -90, position: 'insideLeft' }} />
                  <YAxis yAxisId="right" orientation="right" label={{ value: 'Active Pumps', angle: 90, position: 'insideRight' }} />
                  <Tooltip />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="price" stroke="#EF4444" name="Energy Price" strokeWidth={2} />
                  <Line yAxisId="right" type="monotone" dataKey="pumps" stroke="#3B82F6" name="Active Pumps" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Schedule Optimization Settings */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <h4 className="font-medium mb-3">Peak Hours Avoidance</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Morning Peak (7-9 AM)</span>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span className="text-sm text-green-600">Enabled</span>
                    </label>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Evening Peak (6-9 PM)</span>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" defaultChecked />
                      <span className="text-sm text-green-600">Enabled</span>
                    </label>
                  </div>
                </div>
              </div>
              
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <h4 className="font-medium mb-3">Storage Utilization</h4>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Night Filling (11 PM - 5 AM)</span>
                    <span className="text-green-600 font-medium">Active</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Current Storage Level</span>
                    <span className="font-medium">78%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: '78%' }} />
                  </div>
                </div>
              </div>
            </div>
          </Card>

          {/* Predictive Schedule */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Next 24h Optimized Schedule</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead>
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Pumps</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Strategy</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Savings</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {[
                    { time: '00:00-06:00', pumps: '3/12', strategy: 'Storage Filling', savings: '€45' },
                    { time: '06:00-07:00', pumps: '5/12', strategy: 'Ramp Up', savings: '€12' },
                    { time: '07:00-09:00', pumps: '8/12', strategy: 'Peak Demand', savings: '€0' },
                    { time: '09:00-18:00', pumps: '6/12', strategy: 'Optimized Flow', savings: '€78' },
                    { time: '18:00-21:00', pumps: '9/12', strategy: 'Evening Peak', savings: '€5' },
                    { time: '21:00-00:00', pumps: '4/12', strategy: 'Night Mode', savings: '€32' }
                  ].map((row, idx) => (
                    <tr key={idx}>
                      <td className="px-4 py-2 text-sm">{row.time}</td>
                      <td className="px-4 py-2 text-sm font-medium">{row.pumps}</td>
                      <td className="px-4 py-2 text-sm">{row.strategy}</td>
                      <td className="px-4 py-2 text-sm text-green-600 font-medium">{row.savings}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className="space-y-6">
          {/* ROI Dashboard */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Return on Investment Analysis</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Annual Savings</p>
                <p className="text-2xl font-bold text-green-600">€66,892</p>
              </div>
              <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Investment</p>
                <p className="text-2xl font-bold text-blue-600">€180,000</p>
              </div>
              <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Payback Period</p>
                <p className="text-2xl font-bold text-purple-600">2.7 years</p>
              </div>
              <div className="text-center p-4 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">10-Year NPV</p>
                <p className="text-2xl font-bold text-orange-600">€486,230</p>
              </div>
            </div>

            {/* Cumulative Savings Chart */}
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={Array.from({ length: 10 }, (_, i) => ({
                year: 2024 + i,
                cumulative: (i + 1) * 66892 - (i === 0 ? 180000 : 0),
                annual: 66892
              }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis label={{ value: 'Euros (€)', angle: -90, position: 'insideLeft' }} />
                <Tooltip formatter={(value: any) => `€${value.toLocaleString()}`} />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="cumulative"
                  stroke="#10B981"
                  fill="#D1FAE5"
                  name="Cumulative Savings"
                />
                <Area
                  type="monotone"
                  dataKey="annual"
                  stroke="#3B82F6"
                  fill="#DBEAFE"
                  name="Annual Savings"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>

          {/* Environmental Impact */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Environmental Impact</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-6 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg">
                <LeafIcon className="h-12 w-12 text-emerald-600 mx-auto mb-3" />
                <p className="text-3xl font-bold text-emerald-600">178.4</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Tons CO₂/year saved</p>
                <p className="text-xs text-emerald-600 mt-2">Equivalent to 8,920 trees</p>
              </div>
              <div className="text-center p-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <ZapIcon className="h-12 w-12 text-blue-600 mx-auto mb-3" />
                <p className="text-3xl font-bold text-blue-600">446 MWh</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Annual energy saved</p>
                <p className="text-xs text-blue-600 mt-2">Powers 132 homes</p>
              </div>
              <div className="text-center p-6 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <TrendingDownIcon className="h-12 w-12 text-purple-600 mx-auto mb-3" />
                <p className="text-3xl font-bold text-purple-600">25%</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Carbon footprint reduction</p>
                <p className="text-xs text-purple-600 mt-2">Towards net zero</p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default EnergyOptimizationPage; 