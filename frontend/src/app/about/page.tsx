'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { 
  Calculator, 
  TrendingUp, 
  Droplets, 
  Gauge, 
  Zap, 
  Activity,
  AlertTriangle,
  BarChart3,
  BookOpen
} from 'lucide-react';

export default function AboutPage() {
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BookOpen },
    { id: 'energy', label: 'Energy Calculations', icon: Zap },
    { id: 'flow', label: 'Flow & Pressure', icon: Droplets },
    { id: 'efficiency', label: 'Efficiency Metrics', icon: TrendingUp },
    { id: 'anomalies', label: 'Anomaly Detection', icon: AlertTriangle },
    { id: 'consumption', label: 'Consumption Analysis', icon: BarChart3 }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            About Abbanoa Water Management System
          </h1>
          <p className="mt-2 text-lg text-gray-600 dark:text-gray-400">
            Understanding the calculations and methodologies behind our analytics
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="mb-8 border-b border-gray-200 dark:border-gray-700">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center py-2 px-1 border-b-2 font-medium text-sm
                    ${activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                    }
                  `}
                >
                  <Icon className="w-5 h-5 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="space-y-8">
          
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <Card className="p-6">
                <h2 className="text-2xl font-semibold mb-4">System Overview</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  The Abbanoa Water Management System is a comprehensive platform designed to monitor, analyze, and optimize 
                  water distribution networks. It combines real-time sensor data with advanced analytics to provide actionable 
                  insights for operational efficiency.
                </p>
                
                <h3 className="text-xl font-semibold mb-3 mt-6">Key Features</h3>
                <ul className="list-disc list-inside space-y-2 text-gray-600 dark:text-gray-400">
                  <li>Real-time monitoring of flow rates, pressure, and water quality</li>
                  <li>Energy consumption tracking and optimization</li>
                  <li>Predictive analytics for demand forecasting</li>
                  <li>Anomaly detection and alert management</li>
                  <li>Consumption pattern analysis</li>
                  <li>Network efficiency calculations</li>
                </ul>

                <h3 className="text-xl font-semibold mb-3 mt-6">Data Sources</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Our system integrates data from:
                </p>
                <ul className="list-disc list-inside space-y-2 mt-2 text-gray-600 dark:text-gray-400">
                  <li>IoT sensors deployed across the water network</li>
                  <li>SCADA systems for pump and valve control</li>
                  <li>Weather data for demand prediction</li>
                  <li>Historical consumption patterns</li>
                  <li>Maintenance and operational logs</li>
                </ul>
              </Card>
            </div>
          )}

          {/* Energy Calculations Tab */}
          {activeTab === 'energy' && (
            <div className="space-y-6">
              <Card className="p-6">
                <h2 className="text-2xl font-semibold mb-4">⚡ Energy Consumption Calculations</h2>
                
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mb-6">
                  <h3 className="text-lg font-semibold mb-2">Primary Formula</h3>
                  <code className="block bg-white dark:bg-gray-800 p-3 rounded text-sm">
                    Power (kW) = Flow Rate (m³/h) × Pressure (bar) × 2.75 / 100
                  </code>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                    This empirical formula provides a conservative estimate of pump power consumption, 
                    accounting for typical pump and motor efficiencies.
                  </p>
                </div>

                <h3 className="text-xl font-semibold mb-3">Detailed Breakdown</h3>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold">1. Theoretical Power Requirement</h4>
                    <code className="block bg-gray-100 dark:bg-gray-800 p-2 rounded text-sm mt-1">
                      P_hydraulic = ρ × g × H × Q / η
                    </code>
                    <ul className="list-disc list-inside mt-2 text-sm text-gray-600 dark:text-gray-400">
                      <li>ρ = Water density (1000 kg/m³)</li>
                      <li>g = Gravitational acceleration (9.81 m/s²)</li>
                      <li>H = Head in meters (1 bar ≈ 10.2 m)</li>
                      <li>Q = Flow rate (m³/s)</li>
                      <li>η = Overall efficiency (pump × motor)</li>
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-semibold">2. Efficiency Factors</h4>
                    <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400">
                      <li>Pump efficiency: 65-75% (typical centrifugal pumps)</li>
                      <li>Motor efficiency: 90-95% (modern electric motors)</li>
                      <li>Combined efficiency: ~70% (0.70 × 0.93)</li>
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-semibold">3. Cost Calculations</h4>
                    <code className="block bg-gray-100 dark:bg-gray-800 p-2 rounded text-sm mt-1">
                      Daily Cost = Power (kW) × 24 hours × Energy Rate (€/kWh)
                    </code>
                    <code className="block bg-gray-100 dark:bg-gray-800 p-2 rounded text-sm mt-1">
                      Cost per m³ = Energy Cost / Total Volume Delivered
                    </code>
                  </div>

                  <div>
                    <h4 className="font-semibold">4. Time-of-Use Optimization</h4>
                    <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400">
                      <li>Peak hours (08:00-20:00): €0.25/kWh</li>
                      <li>Off-peak hours (20:00-08:00): €0.15/kWh</li>
                      <li>Potential savings: 15-30% through load shifting</li>
                    </ul>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h2 className="text-2xl font-semibold mb-4">Example Calculation</h2>
                <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded">
                  <p className="font-mono text-sm">
                    Given: Flow = 300 m³/h, Pressure = 5 bar<br/>
                    Power = 300 × 5 × 2.75 / 100 = 41.25 kW<br/>
                    Daily Energy = 41.25 × 24 = 990 kWh<br/>
                    Daily Cost = 990 × €0.20 = €198<br/>
                    Cost per m³ = €198 / (300 × 24) = €0.0275/m³
                  </p>
                </div>
              </Card>
            </div>
          )}

          {/* Flow & Pressure Tab */}
          {activeTab === 'flow' && (
            <div className="space-y-6">
              <Card className="p-6">
                <h2 className="text-2xl font-semibold mb-4">💧 Flow & Pressure Calculations</h2>
                
                <h3 className="text-xl font-semibold mb-3">Flow Rate Metrics</h3>
                <div className="space-y-3">
                  <div>
                    <h4 className="font-semibold">Total System Flow</h4>
                    <code className="block bg-gray-100 dark:bg-gray-800 p-2 rounded text-sm mt-1">
                      Q_total = Σ(Q_node) for all active nodes
                    </code>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      Measured in L/s (liters per second) or m³/h
                    </p>
                  </div>

                  <div>
                    <h4 className="font-semibold">Volume Calculations</h4>
                    <code className="block bg-gray-100 dark:bg-gray-800 p-2 rounded text-sm mt-1">
                      Daily Volume = Flow Rate (m³/h) × 24 hours
                    </code>
                  </div>

                  <div>
                    <h4 className="font-semibold">Velocity in Pipes</h4>
                    <code className="block bg-gray-100 dark:bg-gray-800 p-2 rounded text-sm mt-1">
                      v = Q / A = 4Q / (π × D²)
                    </code>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      Optimal velocity: 0.6-2.0 m/s to minimize friction losses
                    </p>
                  </div>
                </div>

                <h3 className="text-xl font-semibold mb-3 mt-6">Pressure Analysis</h3>
                <div className="space-y-3">
                  <div>
                    <h4 className="font-semibold">Pressure Zones</h4>
                    <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400">
                      <li>Optimal: 3.0-5.0 bar (residential areas)</li>
                      <li>Warning: 2.0-3.0 bar or 5.0-6.0 bar</li>
                      <li>Critical: &lt;2.0 bar or &gt;6.0 bar</li>
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-semibold">Pressure Loss Calculation</h4>
                    <code className="block bg-gray-100 dark:bg-gray-800 p-2 rounded text-sm mt-1">
                      ΔP = f × (L/D) × (ρv²/2)
                    </code>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      Darcy-Weisbach equation for friction losses
                    </p>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Efficiency Metrics Tab */}
          {activeTab === 'efficiency' && (
            <div className="space-y-6">
              <Card className="p-6">
                <h2 className="text-2xl font-semibold mb-4">📊 System Efficiency Metrics</h2>
                
                <div className="space-y-6">
                  <div>
                    <h3 className="text-xl font-semibold mb-3">1. Network Efficiency</h3>
                    <code className="block bg-gray-100 dark:bg-gray-800 p-2 rounded text-sm">
                      Network Efficiency = (Water Delivered / Water Produced) × 100%
                    </code>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                      Target: &gt;92% (industry best practice)
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold mb-3">2. Water Loss Rate</h3>
                    <code className="block bg-gray-100 dark:bg-gray-800 p-2 rounded text-sm">
                      Water Loss = Water Produced - Water Delivered - Authorized Unbilled
                    </code>
                    <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                      <p>Components:</p>
                      <ul className="list-disc list-inside ml-4">
                        <li>Real losses: Leaks, bursts (physical water loss)</li>
                        <li>Apparent losses: Meter errors, unauthorized use</li>
                      </ul>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold mb-3">3. Pump Efficiency</h3>
                    <code className="block bg-gray-100 dark:bg-gray-800 p-2 rounded text-sm">
                      η_pump = (Theoretical Power / Actual Power) × 100%
                    </code>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                      Monitoring pump efficiency helps identify maintenance needs
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold mb-3">4. Infrastructure Leakage Index (ILI)</h3>
                    <code className="block bg-gray-100 dark:bg-gray-800 p-2 rounded text-sm">
                      ILI = Current Annual Real Losses / Unavoidable Annual Real Losses
                    </code>
                    <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                      <p>Performance categories:</p>
                      <ul className="list-disc list-inside ml-4">
                        <li>ILI &lt; 2: Excellent</li>
                        <li>ILI 2-4: Good</li>
                        <li>ILI 4-8: Poor</li>
                        <li>ILI &gt; 8: Very poor</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Anomaly Detection Tab */}
          {activeTab === 'anomalies' && (
            <div className="space-y-6">
              <Card className="p-6">
                <h2 className="text-2xl font-semibold mb-4">🚨 Anomaly Detection Algorithms</h2>
                
                <div className="space-y-6">
                  <div>
                    <h3 className="text-xl font-semibold mb-3">1. Statistical Process Control</h3>
                    <code className="block bg-gray-100 dark:bg-gray-800 p-2 rounded text-sm">
                      Anomaly if: |value - μ| &gt; k × σ
                    </code>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                      Where μ is the mean, σ is standard deviation, and k is typically 2-3
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold mb-3">2. Flow-Pressure Correlation</h3>
                    <code className="block bg-gray-100 dark:bg-gray-800 p-2 rounded text-sm">
                      Expected: Q₂/Q₁ = (P₂/P₁)^0.5
                    </code>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                      Deviations from this relationship may indicate leaks or blockages
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold mb-3">3. Pattern Recognition</h3>
                    <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400">
                      <li><strong>Sudden drops:</strong> Pipe burst (flow ↑, pressure ↓)</li>
                      <li><strong>Gradual decline:</strong> Growing leak</li>
                      <li><strong>Pressure spikes:</strong> Valve closure or pump issues</li>
                      <li><strong>Night flow increase:</strong> New leak development</li>
                    </ul>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold mb-3">4. Consumption Anomalies</h3>
                    <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                      <p><strong>Zero consumption:</strong> Meter failure or supply interruption</p>
                      <p><strong>Excessive use:</strong> &gt;3σ above historical average</p>
                      <p><strong>Unusual patterns:</strong> Consumption at odd hours</p>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Consumption Analysis Tab */}
          {activeTab === 'consumption' && (
            <div className="space-y-6">
              <Card className="p-6">
                <h2 className="text-2xl font-semibold mb-4">📈 Consumption Analysis</h2>
                
                <div className="space-y-6">
                  <div>
                    <h3 className="text-xl font-semibold mb-3">1. Demand Forecasting</h3>
                    <code className="block bg-gray-100 dark:bg-gray-800 p-2 rounded text-sm">
                      Forecast = Base + Seasonal + Weather + Trend + Events
                    </code>
                    <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                      <p>Factors considered:</p>
                      <ul className="list-disc list-inside ml-4">
                        <li>Historical patterns (time series analysis)</li>
                        <li>Temperature correlation (↑1°C = ↑2-3% consumption)</li>
                        <li>Day of week patterns</li>
                        <li>Holiday effects</li>
                        <li>Special events (tourism, festivals)</li>
                      </ul>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold mb-3">2. User Segmentation</h3>
                    <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                      <p><strong>Residential:</strong> 150-200 L/person/day</p>
                      <p><strong>Commercial:</strong> Variable based on business type</p>
                      <p><strong>Industrial:</strong> Process-dependent consumption</p>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold mb-3">3. Peak Demand Analysis</h3>
                    <code className="block bg-gray-100 dark:bg-gray-800 p-2 rounded text-sm">
                      Peak Factor = Peak Hour Demand / Average Hour Demand
                    </code>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                      Typical peak factors: 1.5-2.5 for residential areas
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold mb-3">4. Conservation Opportunities</h3>
                    <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                      <p><strong>Pressure management:</strong> -1 bar = -10% consumption</p>
                      <p><strong>Leak reduction:</strong> Fix 1 L/s leak = save 86.4 m³/day</p>
                      <p><strong>Demand management:</strong> Smart meters + pricing</p>
                    </div>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h2 className="text-2xl font-semibold mb-4">Data Quality Metrics</h2>
                <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
                  <p><strong>Completeness:</strong> % of expected data points received</p>
                  <p><strong>Accuracy:</strong> % within calibrated sensor tolerance</p>
                  <p><strong>Timeliness:</strong> Average data latency &lt; 5 minutes</p>
                  <p><strong>Consistency:</strong> Cross-validation between related sensors</p>
                </div>
              </Card>
            </div>
          )}

        </div>

        {/* Footer */}
        <div className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
          <p className="text-center text-gray-500 dark:text-gray-400">
            Abbanoa Water Management System - Version 2.0 | Last updated: December 2024
          </p>
        </div>

      </div>
    </div>
  );
} 