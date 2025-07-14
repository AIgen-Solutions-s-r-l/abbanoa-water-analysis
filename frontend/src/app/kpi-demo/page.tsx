'use client';

import React from 'react';
import WaterKPIRibbon from '@/components/water/WaterKPIRibbon';
import { WaterCoreMetrics } from '@/lib/types';

export default function WaterKPIDemoPage() {
  // Sample water system metrics based on Abbanoa Enhanced Overview
  const sampleMetrics: WaterCoreMetrics = {
    activeNodes: 18,
    totalNodes: 20,
    totalFlowRate: 1247.3, // L/s
    averagePressure: 2.8, // bar
    dataQuality: 94.2, // percentage
    systemUptime: 99.1, // percentage
    energyEfficiency: 0.38, // kWh/m³
  };

  const warningMetrics: WaterCoreMetrics = {
    activeNodes: 15,
    totalNodes: 20,
    totalFlowRate: 856.4,
    averagePressure: 1.7, // Low pressure warning
    dataQuality: 82.1, // Lower quality
    systemUptime: 96.8,
    energyEfficiency: 0.45, // Higher energy consumption
  };

  const criticalMetrics: WaterCoreMetrics = {
    activeNodes: 12,
    totalNodes: 20,
    totalFlowRate: 421.2,
    averagePressure: 1.2, // Critical pressure
    dataQuality: 67.8, // Poor quality
    systemUptime: 92.4,
    energyEfficiency: 0.58, // Poor efficiency
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Water Infrastructure KPI Dashboard
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Enhanced System Overview - Core Performance Indicators for Abbanoa Water Network
          </p>
        </div>

        <div className="space-y-12">
          {/* Optimal System Status */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              🟢 Optimal System Performance
            </h2>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <WaterKPIRibbon
                metrics={sampleMetrics}
                timeRange="Last 24 Hours"
                showTrends={true}
                compact={false}
              />
            </div>
          </section>

          {/* Warning Status */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              🟡 System Warnings Detected
            </h2>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <WaterKPIRibbon
                metrics={warningMetrics}
                timeRange="Last 6 Hours"
                showTrends={true}
                compact={false}
              />
            </div>
          </section>

          {/* Critical Status */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              🔴 Critical System Issues
            </h2>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <WaterKPIRibbon
                metrics={criticalMetrics}
                timeRange="Current Status"
                showTrends={true}
                compact={false}
              />
            </div>
          </section>

          {/* Compact Views */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              Compact Layout Options
            </h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Compact - Normal Operation</h3>
                <WaterKPIRibbon
                  metrics={sampleMetrics}
                  timeRange="Real-time"
                  showTrends={false}
                  compact={true}
                />
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Compact - With Warnings</h3>
                <WaterKPIRibbon
                  metrics={warningMetrics}
                  timeRange="Live"
                  showTrends={false}
                  compact={true}
                />
              </div>
            </div>
          </section>

          {/* Feature Documentation */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              Component Features & Implementation
            </h2>
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="prose max-w-none">
                <h3 className="text-lg font-semibold mb-4">Water Infrastructure KPI Metrics:</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <h4 className="font-semibold text-green-600 mb-2">📊 Core KPIs</h4>
                    <ul className="space-y-1 text-sm">
                      <li><strong>Active Nodes:</strong> Network nodes reporting data</li>
                      <li><strong>Total Flow Rate:</strong> Cumulative water flow (L/s)</li>
                      <li><strong>Average Pressure:</strong> Network pressure (bar)</li>
                      <li><strong>Data Quality:</strong> Sensor data reliability (%)</li>
                      <li><strong>System Uptime:</strong> Operational availability (%)</li>
                      <li><strong>Energy Efficiency:</strong> Power consumption (kWh/m³)</li>
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-blue-600 mb-2">🎯 Status Indicators</h4>
                    <ul className="space-y-1 text-sm">
                      <li><span className="text-green-600">🟢 Good:</span> Within optimal range</li>
                      <li><span className="text-yellow-600">🟡 Warning:</span> Outside normal parameters</li>
                      <li><span className="text-red-600">🔴 Critical:</span> Requires immediate attention</li>
                      <li><strong>Trends:</strong> Real-time change indicators</li>
                      <li><strong>Targets:</strong> Operational benchmarks</li>
                      <li><strong>Tooltips:</strong> Detailed metric explanations</li>
                    </ul>
                  </div>
                </div>

                <h3 className="text-lg font-semibold mt-6 mb-4">API Integration:</h3>
                <div className="bg-gray-100 rounded p-4 text-sm font-mono mb-4">
                  <div className="text-gray-700">
                    {`// Fetching water metrics from Abbanoa API
const waterMetrics = await apiClient.get<WaterCoreMetrics>('/water/metrics');

// Rendering the KPI ribbon
<WaterKPIRibbon 
  metrics={waterMetrics.data}
  timeRange="Last 24 Hours"
  showTrends={true}
  compact={false}
/>`}
                  </div>
                </div>

                <h3 className="text-lg font-semibold mb-4">Enhanced Overview Integration:</h3>
                <ul className="space-y-2">
                  <li>✅ <strong>Migrated from Streamlit:</strong> Core KPI metrics from Enhanced System Overview</li>
                  <li>✅ <strong>Real-time Updates:</strong> Connects to existing FastAPI water management endpoints</li>
                  <li>✅ <strong>Responsive Design:</strong> Works across all screen sizes</li>
                  <li>✅ <strong>Status Color Coding:</strong> Visual health indicators</li>
                  <li>✅ <strong>Operational Thresholds:</strong> Industry-standard water management targets</li>
                  <li>✅ <strong>Accessibility:</strong> Full tooltip descriptions and screen reader support</li>
                  <li>✅ <strong>Performance:</strong> Optimized for real-time dashboard updates</li>
                </ul>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
} 