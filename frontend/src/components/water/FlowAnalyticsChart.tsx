'use client';

import React, { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from 'recharts';
import { FlowAnalyticsData } from '@/lib/types';

interface FlowAnalyticsChartProps {
  data: FlowAnalyticsData[];
  height?: number;
  className?: string;
}

interface TabButtonProps {
  isActive: boolean;
  onClick: () => void;
  children: React.ReactNode;
}

const TabButton: React.FC<TabButtonProps> = ({ isActive, onClick, children }) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 text-sm font-medium rounded-t-lg border-b-2 transition-colors ${
      isActive
        ? 'text-blue-600 border-blue-600 bg-blue-50 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-400'
        : 'text-gray-500 dark:text-gray-400 border-transparent hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
    }`}
  >
    {children}
  </button>
);

/**
 * Real-time Flow Analytics Chart Component
 * Replicates the advanced flow visualization from Streamlit Enhanced Overview
 */
export const FlowAnalyticsChart: React.FC<FlowAnalyticsChartProps> = ({
  data,
  height = 400,
  className = '',
}) => {
  const [activeTab, setActiveTab] = useState<'timeseries' | 'distribution' | 'correlation'>('timeseries');

  // Get unique nodes for color assignment from property names
  const uniqueNodesSet = new Set<string>();
  data.forEach(entry => {
    Object.keys(entry).forEach(key => {
      if (key.startsWith('node') && !key.includes('_')) {
        uniqueNodesSet.add(key.replace('node', ''));
      }
    });
  });
  const uniqueNodes = Array.from(uniqueNodesSet);
  const colors = [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', 
    '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
  ];

  // Custom tooltip for time series
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{`Time: ${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p
              key={index}
              className="text-sm"
              style={{ color: entry.color }}
            >
              {`${entry.name}: ${entry.value.toFixed(2)} L/s`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Prepare data for distribution analysis (box plot simulation with bars)
  const getDistributionData = () => {
    const distributionData = uniqueNodes.map(nodeId => {
      // Extract flow rates for this node from all timestamps
      const flowRates = data
        .map(d => (d as any)[`node${nodeId}`])
        .filter(rate => rate !== undefined && rate !== null);
      
      if (flowRates.length === 0) return null;
      
      flowRates.sort((a, b) => a - b);
      const q1 = flowRates[Math.floor(flowRates.length * 0.25)];
      const median = flowRates[Math.floor(flowRates.length * 0.5)];
      const q3 = flowRates[Math.floor(flowRates.length * 0.75)];
      const min = Math.min(...flowRates);
      const max = Math.max(...flowRates);
      const avg = flowRates.reduce((a, b) => a + b, 0) / flowRates.length;
      
      // Get node name from any timestamp that has it
      const nodeName = (data.find(d => (d as any)[`${nodeId}_name`]) as any)?.[`${nodeId}_name`] || `Node ${nodeId}`;
      
      return {
        nodeId,
        nodeName,
        min,
        q1,
        median,
        q3,
        max,
        avg,
        count: flowRates.length
      };
    }).filter(Boolean);
    
    return distributionData;
  };

  // Calculate correlation matrix
  const getCorrelationData = () => {
    if (uniqueNodes.length < 2) return [];
    
    // Group data by timestamp
    const timeGroups = data.reduce((acc, curr) => {
      if (!acc[curr.timestamp]) {
        acc[curr.timestamp] = {};
      }
      acc[curr.timestamp][curr.nodeId] = curr.flowRate;
      return acc;
    }, {} as Record<string, Record<string, number>>);
    
    // Calculate correlation coefficients
    const correlations = [];
    for (let i = 0; i < uniqueNodes.length; i++) {
      for (let j = 0; j < uniqueNodes.length; j++) {
        const nodeA = uniqueNodes[i];
        const nodeB = uniqueNodes[j];
        
        const pairs = Object.values(timeGroups)
          .filter(group => group[nodeA] !== undefined && group[nodeB] !== undefined)
          .map(group => [group[nodeA], group[nodeB]]);
        
        if (pairs.length < 2) {
          correlations.push({
            nodeA,
            nodeB,
            correlation: nodeA === nodeB ? 1 : 0,
            x: i,
            y: j
          });
          continue;
        }
        
        // Calculate Pearson correlation
        const n = pairs.length;
        const sumA = pairs.reduce((sum, [a]) => sum + a, 0);
        const sumB = pairs.reduce((sum, [, b]) => sum + b, 0);
        const sumAB = pairs.reduce((sum, [a, b]) => sum + a * b, 0);
        const sumA2 = pairs.reduce((sum, [a]) => sum + a * a, 0);
        const sumB2 = pairs.reduce((sum, [, b]) => sum + b * b, 0);
        
        const numerator = n * sumAB - sumA * sumB;
        const denominator = Math.sqrt((n * sumA2 - sumA * sumA) * (n * sumB2 - sumB * sumB));
        
        const correlation = denominator === 0 ? 0 : numerator / denominator;
        
        correlations.push({
          nodeA,
          nodeB,
          correlation: Math.round(correlation * 100) / 100,
          x: i,
          y: j
        });
      }
    }
    
    return correlations;
  };

  const renderTimeSeriesTab = () => (
    <div className="h-full">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="timestamp"
            stroke="#6b7280"
            fontSize={12}
            tick={{ fill: '#6b7280' }}
          />
          <YAxis
            stroke="#6b7280"
            fontSize={12}
            tick={{ fill: '#6b7280' }}
            label={{ 
              value: 'Flow Rate (L/s)', 
              angle: -90, 
              position: 'insideLeft',
              style: { textAnchor: 'middle' }
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {uniqueNodes.map((nodeId, index) => {
            // Get node name from the first entry that has this node's name
            const nodeName = (data.find(d => (d as any)[`${nodeId}_name`]) as any)?.[`${nodeId}_name`] || `Node ${nodeId}`;
            
            return (
              <Line
                key={nodeId}
                type="monotone"
                dataKey={`node${nodeId}`}
                stroke={colors[index % colors.length]}
                strokeWidth={2}
                name={nodeName}
                dot={{ fill: colors[index % colors.length], strokeWidth: 0, r: 3 }}
                activeDot={{ r: 5, stroke: colors[index % colors.length], strokeWidth: 2 }}
                connectNulls={false}
              />
            );
          })}
        </LineChart>
      </ResponsiveContainer>
      
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        {uniqueNodes.slice(0, 4).map((nodeId, index) => {
          // Calculate average flow for this node from the new data structure
          const flowRates = data
            .map(d => (d as any)[`node${nodeId}`])
            .filter(rate => rate !== undefined && rate !== null && !isNaN(rate));
          
          const avgFlow = flowRates.length > 0 
            ? flowRates.reduce((sum, rate) => sum + rate, 0) / flowRates.length 
            : 0;
          
          // Get node name from the data structure
          const nodeName = (data.find(d => (d as any)[`${nodeId}_name`]) as any)?.[`${nodeId}_name`] || `Node ${nodeId}`;
          
          return (
            <div key={nodeId} className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
              <div className="flex items-center mb-1">
                <div 
                  className="w-3 h-3 rounded-full mr-2" 
                  style={{ backgroundColor: colors[index % colors.length] }}
                />
                <span className="font-medium text-gray-700 dark:text-gray-300">{nodeName}</span>
              </div>
              <div className="text-gray-600 dark:text-gray-400">
                Avg: {flowRates.length > 0 ? avgFlow.toFixed(1) : '0.0'} L/s
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  const renderDistributionTab = () => {
    const distributionData = getDistributionData();
    
    return (
      <div className="h-full">
        <ResponsiveContainer width="100%" height={height}>
          <BarChart data={distributionData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="nodeName"
              stroke="#6b7280"
              fontSize={12}
              tick={{ fill: '#6b7280' }}
            />
            <YAxis
              stroke="#6b7280"
              fontSize={12}
              tick={{ fill: '#6b7280' }}
              label={{ 
                value: 'Flow Rate (L/s)', 
                angle: -90, 
                position: 'insideLeft',
                style: { textAnchor: 'middle' }
              }}
            />
            <Tooltip 
              formatter={(value: number, name: string) => [
                `${value.toFixed(2)} L/s`, 
                name === 'avg' ? 'Average Flow' : 
                name === 'max' ? 'Maximum Flow' : 
                name === 'min' ? 'Minimum Flow' : name
              ]}
            />
            <Legend />
            
            <Bar dataKey="avg" fill="#3b82f6" name="Average Flow" />
            <Bar dataKey="max" fill="#10b981" name="Maximum Flow" />
            <Bar dataKey="min" fill="#f59e0b" name="Minimum Flow" />
          </BarChart>
        </ResponsiveContainer>
        
        <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
          <p><strong>Distribution Analysis:</strong> Shows flow rate statistics for each node including average, maximum, and minimum values.</p>
        </div>
      </div>
    );
  };

  const renderCorrelationTab = () => {
    const correlationData = getCorrelationData();
    
    if (uniqueNodes.length < 2) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center text-gray-500 dark:text-gray-400">
            <p className="text-lg font-medium">Correlation Analysis Unavailable</p>
            <p>Need multiple nodes for correlation analysis</p>
          </div>
        </div>
      );
    }
    
    return (
      <div className="h-full">
        <div className="mb-4">
          <h4 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">Node Flow Correlation Matrix</h4>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Correlation coefficients between flow rates of different nodes. 
            Values closer to 1 indicate strong positive correlation, closer to -1 indicate negative correlation.
          </p>
        </div>
        
        {/* Simple correlation table */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-600">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Node</th>
                {uniqueNodes.map(nodeId => (
                  <th key={nodeId} className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    {nodeId.slice(-4)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-600">
              {uniqueNodes.map((nodeA, i) => (
                <tr key={nodeA}>
                  <td className="px-4 py-2 text-sm font-medium text-gray-900 dark:text-gray-100">{nodeA.slice(-4)}</td>
                  {uniqueNodes.map((nodeB, j) => {
                    const corr = correlationData.find(c => c.nodeA === nodeA && c.nodeB === nodeB);
                    const correlation = corr?.correlation || 0;
                    const cellColor = 
                      correlation > 0.7 ? 'bg-green-100 text-green-800' :
                      correlation > 0.3 ? 'bg-blue-100 text-blue-800' :
                      correlation < -0.3 ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800';
                    
                    return (
                      <td key={nodeB} className={`px-4 py-2 text-sm ${cellColor}`}>
                        {correlation.toFixed(2)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
          <div className="flex space-x-4">
            <span className="flex items-center">
              <div className="w-3 h-3 bg-green-100 dark:bg-green-800 rounded mr-1"></div>
              Strong Positive (&gt;0.7)
            </span>
            <span className="flex items-center">
              <div className="w-3 h-3 bg-blue-100 dark:bg-blue-800 rounded mr-1"></div>
              Moderate (0.3-0.7)
            </span>
            <span className="flex items-center">
              <div className="w-3 h-3 bg-gray-100 dark:bg-gray-700 rounded mr-1"></div>
              Weak (-0.3-0.3)
            </span>
            <span className="flex items-center">
              <div className="w-3 h-3 bg-red-100 dark:bg-red-800 rounded mr-1"></div>
              Negative (&lt;-0.3)
            </span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={`w-full ${className}`}>
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Real-time Flow Analytics</h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Advanced flow monitoring with time series analysis, distribution statistics, and correlation insights
        </p>
      </div>
      
      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-4">
        <nav className="-mb-px flex space-x-8">
          <TabButton
            isActive={activeTab === 'timeseries'}
            onClick={() => setActiveTab('timeseries')}
          >
            Time Series
          </TabButton>
          <TabButton
            isActive={activeTab === 'distribution'}
            onClick={() => setActiveTab('distribution')}
          >
            Distribution
          </TabButton>
          <TabButton
            isActive={activeTab === 'correlation'}
            onClick={() => setActiveTab('correlation')}
          >
            Correlation
          </TabButton>
        </nav>
      </div>
      
      {/* Tab Content */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        {activeTab === 'timeseries' && renderTimeSeriesTab()}
        {activeTab === 'distribution' && renderDistributionTab()}
        {activeTab === 'correlation' && renderCorrelationTab()}
      </div>
    </div>
  );
};

export default FlowAnalyticsChart; 