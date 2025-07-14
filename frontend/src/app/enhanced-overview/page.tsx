'use client';

import React, { useState, useEffect } from 'react';
import WaterKPIRibbon from '@/components/water/WaterKPIRibbon';
import FlowAnalyticsChart from '@/components/water/FlowAnalyticsChart';
import NetworkPerformanceAnalytics from '@/components/water/NetworkPerformanceAnalytics';
import SystemHealthGauges from '@/components/water/SystemHealthGauges';
import { WaterCoreMetrics, FlowAnalyticsData, WaterSystemAlert } from '@/lib/types';

// Generate sample data for demonstration
const generateSampleFlowData = (): FlowAnalyticsData[] => {
  const data: FlowAnalyticsData[] = [];
  const nodes = [
    { id: 'NODE_001', name: 'Primary Station' },
    { id: 'NODE_002', name: 'Secondary Station' },
    { id: 'NODE_003', name: 'Distribution A' },
    { id: 'NODE_004', name: 'Distribution B' },
    { id: 'NODE_005', name: 'Junction C' },
  ];
  
  const now = new Date();
  
  for (let i = 0; i < 48; i++) { // Last 24 hours, every 30 minutes
    const timestamp = new Date(now.getTime() - (i * 30 * 60 * 1000));
    
    nodes.forEach(node => {
      // Simulate realistic flow patterns
      const baseFlow = 200 + Math.sin(i * 0.1) * 50; // Daily pattern
      const nodeVariation = Math.sin(nodes.indexOf(node) * 2) * 30;
      const randomVariation = (Math.random() - 0.5) * 20;
      
      data.push({
        timestamp: timestamp.toISOString().slice(11, 16), // HH:MM format
        flowRate: Math.max(0, baseFlow + nodeVariation + randomVariation),
        targetFlow: baseFlow + nodeVariation,
        pressure: 2.5 + Math.sin(i * 0.05) * 0.5 + (Math.random() - 0.5) * 0.2,
        nodeId: node.id,
        nodeName: node.name,
      });
    });
  }
  
  return data.reverse(); // Chronological order
};

const generateSampleMetrics = (): WaterCoreMetrics => ({
  activeNodes: 18,
  totalNodes: 20,
  totalFlowRate: 1247.3,
  averagePressure: 2.8,
  dataQuality: 94.2,
  systemUptime: 99.1,
  energyEfficiency: 0.38,
});

const generateSampleAlerts = (): WaterSystemAlert[] => [
  {
    id: '1',
    type: 'warning',
    title: 'Pressure Drop Detected',
    message: 'Pressure in Distribution B has dropped to 1.9 bar',
    nodeId: 'NODE_004',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    acknowledged: false,
  },
  {
    id: '2',
    type: 'info',
    title: 'Maintenance Scheduled',
    message: 'Routine maintenance for Primary Station scheduled for tomorrow',
    nodeId: 'NODE_001',
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
    acknowledged: true,
  },
];

export default function EnhancedOverviewPage() {
  const [metrics, setMetrics] = useState<WaterCoreMetrics>(generateSampleMetrics());
  const [flowData, setFlowData] = useState<FlowAnalyticsData[]>([]);
  const [alerts] = useState<WaterSystemAlert[]>(generateSampleAlerts());
  const [selectedTimeRange, setSelectedTimeRange] = useState('Last 24 Hours');
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    // Simulate real-time data updates
    const interval = setInterval(() => {
      setLastUpdate(new Date());
      setMetrics(generateSampleMetrics());
      setFlowData(generateSampleFlowData());
    }, 30000); // Update every 30 seconds

    // Initial data load
    setFlowData(generateSampleFlowData());

    return () => clearInterval(interval);
  }, []);

  const getSystemStatusColor = () => {
    if (metrics.systemUptime >= 99.0 && metrics.dataQuality >= 90) return 'text-green-600';
    if (metrics.systemUptime >= 95.0 && metrics.dataQuality >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSystemStatusText = () => {
    if (metrics.systemUptime >= 99.0 && metrics.dataQuality >= 90) return '🟢 System Optimal';
    if (metrics.systemUptime >= 95.0 && metrics.dataQuality >= 70) return '🟡 System Good';
    return '🔴 Attention Required';
  };

  const formatTimeAgo = (timestamp: string) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    if (hours < 1) return 'Just now';
    if (hours === 1) return '1 hour ago';
    return `${hours} hours ago`;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">🚀 Enhanced System Overview</h1>
              <p className="mt-2 text-lg text-gray-600">
                Comprehensive water infrastructure monitoring and analytics
              </p>
            </div>
            <div className="text-right">
              <div className={`text-lg font-semibold ${getSystemStatusColor()}`}>
                {getSystemStatusText()}
              </div>
              <div className="text-sm text-gray-500">
                Last updated: {lastUpdate.toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>

        {/* System Status Banner */}
        <div className="mb-8 bg-gradient-to-r from-blue-50 to-green-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                <span className="text-sm font-medium text-gray-700">Real-time Data Stream Active</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 bg-blue-500 rounded-full mr-2"></div>
                <span className="text-sm font-medium text-gray-700">All Critical Systems Online</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 bg-purple-500 rounded-full mr-2"></div>
                <span className="text-sm font-medium text-gray-700">Enhanced Analytics Enabled</span>
              </div>
            </div>
            
            <select 
              value={selectedTimeRange}
              onChange={(e) => setSelectedTimeRange(e.target.value)}
              className="bg-white border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option>Last 6 Hours</option>
              <option>Last 24 Hours</option>
              <option>Last 3 Days</option>
              <option>Last Week</option>
            </select>
          </div>
        </div>

        {/* Core KPI Metrics */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">📊 Core Performance Indicators</h2>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <WaterKPIRibbon />
          </div>
        </div>

        {/* Advanced Metrics Row */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">📈 Advanced System Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Peak Demand</p>
                  <p className="text-2xl font-semibold text-gray-900">1,456 L/s</p>
                  <p className="text-sm text-green-600">+5.2% vs avg</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Network Efficiency</p>
                  <p className="text-2xl font-semibold text-gray-900">96.7%</p>
                  <p className="text-sm text-blue-600">Target: 95%</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Active Alerts</p>
                  <p className="text-2xl font-semibold text-gray-900">{alerts.filter(a => !a.acknowledged).length}</p>
                  <p className="text-sm text-gray-600">{alerts.length} total</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">SLA Compliance</p>
                  <p className="text-2xl font-semibold text-gray-900">99.8%</p>
                  <p className="text-sm text-green-600">Excellent</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Visual Analytics Section */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 mb-12">
          
          {/* Real-time Flow Analytics */}
          <div className="xl:col-span-2">
            <FlowAnalyticsChart data={flowData} height={500} />
          </div>

          {/* System Health & Alerts */}
          <div className="space-y-6">
            
            {/* System Health Gauges */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">⚡ System Health</h3>
              
              {/* Overall Health Gauge */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">Overall Health</span>
                  <span className="text-lg font-semibold text-green-600">98.5%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div className="bg-green-500 h-3 rounded-full" style={{ width: '98.5%' }}></div>
                </div>
              </div>

              {/* Network Efficiency */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">Network Efficiency</span>
                  <span className="text-lg font-semibold text-blue-600">96.7%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div className="bg-blue-500 h-3 rounded-full" style={{ width: '96.7%' }}></div>
                </div>
              </div>

              {/* Data Integrity */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">Data Integrity</span>
                  <span className="text-lg font-semibold text-purple-600">94.2%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div className="bg-purple-500 h-3 rounded-full" style={{ width: '94.2%' }}></div>
                </div>
              </div>
            </div>

            {/* System Alerts */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">🚨 System Alerts</h3>
              
              {alerts.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <svg className="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p>No active alerts</p>
                  <p className="text-sm">All systems operating normally</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {alerts.slice(0, 3).map((alert) => {
                    const alertColors = {
                      info: 'bg-blue-50 border-blue-200 text-blue-800',
                      warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
                      error: 'bg-red-50 border-red-200 text-red-800',
                      critical: 'bg-red-50 border-red-200 text-red-800',
                    };

                    const alertIcons = {
                      info: '💡',
                      warning: '⚠️',
                      error: '❌',
                      critical: '🚨',
                    };

                    return (
                      <div
                        key={alert.id}
                        className={`p-3 rounded-lg border ${alertColors[alert.type]} ${alert.acknowledged ? 'opacity-60' : ''}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-2">
                            <span className="text-lg">{alertIcons[alert.type]}</span>
                            <div>
                              <p className="font-medium text-sm">{alert.title}</p>
                              <p className="text-xs mt-1">{alert.message}</p>
                              <p className="text-xs mt-1 opacity-75">
                                {formatTimeAgo(alert.timestamp)}
                              </p>
                            </div>
                          </div>
                          {!alert.acknowledged && (
                            <button className="text-xs px-2 py-1 bg-white rounded border">
                              Acknowledge
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* System Health Gauges */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">🏥 System Health Indicators</h2>
          <SystemHealthGauges />
        </div>

        {/* Network Performance Analytics */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">📊 Network Performance Analytics</h2>
          <NetworkPerformanceAnalytics />
        </div>

        {/* Operational Insights */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">💡 Operational Insights</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <span className="text-green-600 text-lg">⚡</span>
                  </div>
                  <div className="ml-3">
                    <h4 className="text-sm font-semibold text-gray-900">Energy Optimization</h4>
                    <p className="text-xs text-gray-600 mt-1">
                      Current efficiency is 5% above target
                    </p>
                  </div>
                </div>
                <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">Low Impact</span>
              </div>
              <p className="text-sm text-gray-700 mt-4">
                System is operating efficiently. Consider maintaining current pump schedules.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                    <span className="text-yellow-600 text-lg">🔧</span>
                  </div>
                  <div className="ml-3">
                    <h4 className="text-sm font-semibold text-gray-900">Maintenance Due</h4>
                    <p className="text-xs text-gray-600 mt-1">
                      3 nodes require scheduled maintenance
                    </p>
                  </div>
                </div>
                <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">Medium Impact</span>
              </div>
              <p className="text-sm text-gray-700 mt-4">
                Schedule maintenance for nodes NODE_003, NODE_007, NODE_012 within the next week.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <span className="text-blue-600 text-lg">📈</span>
                  </div>
                  <div className="ml-3">
                    <h4 className="text-sm font-semibold text-gray-900">Performance Trends</h4>
                    <p className="text-xs text-gray-600 mt-1">
                      Flow patterns show seasonal optimization
                    </p>
                  </div>
                </div>
                <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">Low Impact</span>
              </div>
              <p className="text-sm text-gray-700 mt-4">
                Flow distribution is adapting well to seasonal demand changes.
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
} 