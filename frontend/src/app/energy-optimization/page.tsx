'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { DataUnavailableCard } from '@/components/ui/DataUnavailableCard';
import { 
  BatteryIcon,
  ZapIcon,
  TrendingDownIcon,
  ActivityIcon,
  DollarSignIcon,
  LeafIcon,
  RefreshCw,
  AlertCircleIcon
} from 'lucide-react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell
} from 'recharts';

interface HourlyEnergy {
  hour: number;
  flow_rate: number;
  pressure: number;
  power_kw: number;
  energy_cost: number;
  is_peak: boolean;
  rate_eur_kwh: number;
}

interface DailyStatistics {
  total_energy_kwh: number;
  total_cost_eur: number;
  peak_demand_kw: number;
  average_power_kw: number;
  peak_hours_cost: number;
  off_peak_cost: number;
}

interface OptimizationOpportunity {
  type: string;
  title: string;
  description: string;
  annual_savings_eur: number;
  implementation: string;
  investment_eur: number;
  roi_months: number;
}

interface EnergyOptimizationData {
  current_energy_profile: HourlyEnergy[];
  daily_statistics: DailyStatistics;
  optimization_opportunities: OptimizationOpportunity[];
  projected_annual_savings: number;
}

const EnergyOptimizationPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [energyData, setEnergyData] = useState<EnergyOptimizationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchEnergyData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch('/api/proxy/v1/energy/optimization');
        
        if (response.ok) {
          const data = await response.json();
          setEnergyData(data);
        } else if (response.status === 204) {
          setEnergyData(null);
        } else {
          throw new Error(`Failed to fetch energy data: ${response.status}`);
        }
      } catch (err) {
        console.error('Error fetching energy data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load energy data');
      } finally {
        setLoading(false);
      }
    };

    fetchEnergyData();
    
    // Refresh data every 5 minutes
    const interval = setInterval(fetchEnergyData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 space-y-6">
        <div className="max-w-2xl mx-auto">
          <DataUnavailableCard
            title="Error Loading Energy Data"
            message={error}
            onRetry={() => window.location.reload()}
            variant="error"
            icon={<AlertCircleIcon className="w-12 h-12 text-red-600 dark:text-red-400" />}
          />
        </div>
      </div>
    );
  }

  if (!energyData) {
    return (
      <div className="p-6 space-y-6">
        <div className="max-w-2xl mx-auto">
          <DataUnavailableCard
            title="Energy Optimization Data Not Available"
            message="The energy optimization data is currently not available in the database. This could be because the monitoring systems are being configured or there's no recent energy consumption data to analyze."
            onRetry={() => window.location.reload()}
            variant="info"
            icon={<BatteryIcon className="w-12 h-12 text-blue-600 dark:text-blue-400" />}
          />
        </div>
      </div>
    );
  }

  const { current_energy_profile, daily_statistics, optimization_opportunities, projected_annual_savings } = energyData;

  // Calculate estimated CO2 savings (assuming 0.4 kg CO2 per kWh)
  const co2SavedKg = projected_annual_savings > 0 ? (projected_annual_savings / daily_statistics.total_cost_eur * daily_statistics.total_energy_kwh * 0.4 * 365 / 1000).toFixed(1) : 0;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Energy Optimization</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Monitor and optimize energy consumption across the network</p>
        </div>
        <div className="flex gap-2">
          <Button 
            variant="primary" 
            className="flex items-center gap-2"
            onClick={() => window.location.reload()}
          >
            <RefreshCw className="h-4 w-4" />
            Refresh Data
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Daily Energy</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {daily_statistics.total_energy_kwh.toFixed(0)} kWh
              </p>
              <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                Avg: {daily_statistics.average_power_kw.toFixed(1)} kW
              </p>
            </div>
            <ZapIcon className="h-8 w-8 text-blue-500 opacity-50" />
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Daily Cost</p>
              <p className="text-2xl font-bold text-green-600">
                €{daily_statistics.total_cost_eur.toFixed(2)}
              </p>
              <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                Peak: €{daily_statistics.peak_hours_cost.toFixed(2)}
              </p>
            </div>
            <DollarSignIcon className="h-8 w-8 text-green-500 opacity-50" />
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Potential Savings</p>
              <p className="text-2xl font-bold text-purple-600">
                €{(projected_annual_savings / 365).toFixed(2)}/day
              </p>
              <p className="text-xs text-purple-600 dark:text-purple-400 mt-1">
                €{projected_annual_savings.toFixed(0)}/year
              </p>
            </div>
            <TrendingDownIcon className="h-8 w-8 text-purple-500 opacity-50" />
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900/20 dark:to-emerald-800/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">CO₂ Reduction</p>
              <p className="text-2xl font-bold text-emerald-600">
                {co2SavedKg}t/year
              </p>
              <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-1">
                Potential reduction
              </p>
            </div>
            <LeafIcon className="h-8 w-8 text-emerald-500 opacity-50" />
          </div>
        </Card>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-4 mb-6">
        {['overview', 'opportunities', 'profile'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === tab
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Hourly Energy Consumption</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={current_energy_profile}>
                <defs>
                  <linearGradient id="colorPower" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Area 
                  type="monotone" 
                  dataKey="power_kw" 
                  stroke="#3B82F6" 
                  fillOpacity={1} 
                  fill="url(#colorPower)" 
                  name="Power (kW)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Energy Cost by Hour</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={current_energy_profile}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="energy_cost" name="Cost (€)">
                  {current_energy_profile.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.is_peak ? '#EF4444' : '#10B981'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>
      )}

      {activeTab === 'opportunities' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {optimization_opportunities.map((opportunity, index) => (
            <Card key={index} className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold">{opportunity.title}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {opportunity.type}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-600">
                    €{opportunity.annual_savings_eur.toLocaleString()}/year
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    ROI: {opportunity.roi_months} months
                  </p>
                </div>
              </div>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                {opportunity.description}
              </p>
              <div className="border-t pt-4">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  <strong>Implementation:</strong> {opportunity.implementation}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  <strong>Investment:</strong> €{opportunity.investment_eur.toLocaleString()}
                </p>
              </div>
            </Card>
          ))}
        </div>
      )}

      {activeTab === 'profile' && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">24-Hour Energy Profile</h3>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={current_energy_profile}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line 
                yAxisId="left"
                type="monotone" 
                dataKey="power_kw" 
                stroke="#3B82F6" 
                strokeWidth={2}
                name="Power (kW)"
              />
              <Line 
                yAxisId="left"
                type="monotone" 
                dataKey="flow_rate" 
                stroke="#10B981" 
                strokeWidth={2}
                name="Flow Rate"
              />
              <Line 
                yAxisId="right"
                type="monotone" 
                dataKey="pressure" 
                stroke="#F59E0B" 
                strokeWidth={2}
                name="Pressure"
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      )}
    </div>
  );
};

export default EnergyOptimizationPage;