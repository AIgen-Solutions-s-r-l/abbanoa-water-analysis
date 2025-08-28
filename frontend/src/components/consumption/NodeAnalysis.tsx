/**
 * Node Analysis Component
 * Displays detailed node-specific and infrastructure type analysis
 */

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts';
import { 
  ActivityIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
  Clock,
  Gauge,
  Users,
  DropletIcon,
  Settings,
  TrendingUpIcon,
  TrendingDownIcon,
  MinusIcon
} from 'lucide-react';

interface NodeAnalysisProps {
  nodeAnalysis: Array<{
    node_id: string;
    node_name: string;
    node_type: string;
    infrastructure_type: string;
    total_users: number;
    daily_consumption_liters: number;
    monthly_consumption_liters: number;
    avg_per_user_daily: number;
    peak_hour: number;
    efficiency_score: number;
    water_loss_percentage: number;
    pressure_avg: number;
    flow_rate_avg: number;
    last_maintenance: string;
    next_maintenance: string;
    status: string;
    alerts: number;
    performance_rating: string;
  }>;
  infrastructureSummary: {
    total_nodes: number;
    main_nodes: number;
    secondary_nodes: number;
    industrial_nodes: number;
    total_users_served: number;
    total_daily_consumption: number;
    avg_efficiency: number;
    avg_water_loss: number;
    operational_nodes: number;
    maintenance_required: number;
  };
  infrastructureTypes: Array<{
    type: string;
    description: string;
    node_count: number;
    total_users: number;
    daily_consumption: number;
    avg_efficiency: number;
    avg_water_loss: number;
    avg_pressure: number;
    avg_flow_rate: number;
    performance_rating: string;
    maintenance_frequency_days: number;
    criticality_level: string;
  }>;
  className?: string;
}

export function NodeAnalysis({ 
  nodeAnalysis, 
  infrastructureSummary, 
  infrastructureTypes, 
  className = '' 
}: NodeAnalysisProps) {
  const [selectedNodeType, setSelectedNodeType] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('efficiency');

  // Filter nodes by type
  const filteredNodes = selectedNodeType === 'all' 
    ? nodeAnalysis 
    : nodeAnalysis.filter(node => node.node_type === selectedNode);

  // Sort nodes
  const sortedNodes = [...filteredNodes].sort((a, b) => {
    switch (sortBy) {
      case 'efficiency':
        return b.efficiency_score - a.efficiency_score;
      case 'consumption':
        return b.daily_consumption_liters - a.daily_consumption_liters;
      case 'users':
        return b.total_users - a.total_users;
      case 'alerts':
        return b.alerts - a.alerts;
      default:
        return 0;
    }
  });

  // Colors for charts
  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
  const PERFORMANCE_COLORS = {
    excellent: '#10b981',
    good: '#3b82f6',
    fair: '#f59e0b',
    poor: '#ef4444'
  };

  // Get performance icon and color
  const getPerformanceIcon = (rating: string) => {
    switch (rating) {
      case 'excellent':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'good':
        return <TrendingUpIcon className="h-5 w-5 text-blue-500" />;
      case 'fair':
        return <MinusIcon className="h-5 w-5 text-yellow-500" />;
      case 'poor':
        return <TrendingDownIcon className="h-5 w-5 text-red-500" />;
      default:
        return <MinusIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  // Get criticality color
  const getCriticalityColor = (level: string) => {
    switch (level) {
      case 'critical':
        return 'text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-200';
      case 'high':
        return 'text-orange-600 bg-orange-100 dark:bg-orange-900 dark:text-orange-200';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-200';
      case 'low':
        return 'text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-200';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  // Format consumption numbers
  const formatConsumption = (value: number) => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M L`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K L`;
    }
    return `${value.toFixed(0)} L`;
  };

  // Custom tooltip for node charts
  const NodeTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0]?.payload;
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900 dark:text-gray-100">{data?.node_name}</p>
          <p className="text-sm text-blue-600">
            Efficiency: {(data?.efficiency_score * 100).toFixed(1)}%
          </p>
          <p className="text-sm text-red-600">
            Water Loss: {data?.water_loss_percentage}%
          </p>
          <p className="text-sm text-gray-600">
            Users: {data?.total_users.toLocaleString()}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Infrastructure Summary */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Infrastructure Overview
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {infrastructureSummary.total_nodes}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Nodes</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {infrastructureSummary.operational_nodes}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Operational</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {infrastructureSummary.total_users_served.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Users Served</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {(infrastructureSummary.avg_efficiency * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Avg Efficiency</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {infrastructureSummary.maintenance_required}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Maintenance Required</div>
          </div>
        </div>
      </Card>

      {/* Node Type Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Node Type Distribution
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={[
                  { name: 'Main', value: infrastructureSummary.main_nodes, color: '#3b82f6' },
                  { name: 'Secondary', value: infrastructureSummary.secondary_nodes, color: '#10b981' },
                  { name: 'Industrial', value: infrastructureSummary.industrial_nodes, color: '#f59e0b' }
                ]}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {[
                  { name: 'Main', value: infrastructureSummary.main_nodes, color: '#3b82f6' },
                  { name: 'Secondary', value: infrastructureSummary.secondary_nodes, color: '#10b981' },
                  { name: 'Industrial', value: infrastructureSummary.industrial_nodes, color: '#f59e0b' }
                ].map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            Infrastructure Types Performance
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={infrastructureTypes} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="type" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="avg_efficiency" fill="#3b82f6" name="Efficiency" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Node Analysis Table */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Node Analysis
          </h3>
          <div className="flex space-x-2">
            <select
              value={selectedNodeType}
              onChange={(e) => setSelectedNodeType(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm"
            >
              <option value="all">All Types</option>
              <option value="main">Main</option>
              <option value="secondary">Secondary</option>
              <option value="industrial">Industrial</option>
            </select>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm"
            >
              <option value="efficiency">Sort by Efficiency</option>
              <option value="consumption">Sort by Consumption</option>
              <option value="users">Sort by Users</option>
              <option value="alerts">Sort by Alerts</option>
            </select>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Node
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Performance
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Efficiency
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Water Loss
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Users
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Alerts
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              {sortedNodes.map((node) => (
                <tr key={node.node_id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {node.node_name}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {node.node_id}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getCriticalityColor(node.infrastructure_type)}`}>
                      {node.node_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getPerformanceIcon(node.performance_rating)}
                      <span className="ml-2 text-sm text-gray-900 dark:text-gray-100">
                        {node.performance_rating}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {(node.efficiency_score * 100).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {node.water_loss_percentage}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {node.total_users.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {node.alerts > 0 ? (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                        <AlertTriangleIcon className="h-3 w-3 mr-1" />
                        {node.alerts}
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                        <CheckCircleIcon className="h-3 w-3 mr-1" />
                        0
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      node.status === 'operational' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    }`}>
                      {node.status === 'operational' ? (
                        <CheckCircleIcon className="h-3 w-3 mr-1" />
                      ) : (
                        <AlertTriangleIcon className="h-3 w-3 mr-1" />
                      )}
                      {node.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Infrastructure Types Details */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Infrastructure Types Analysis
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {infrastructureTypes.map((infraType) => (
            <div key={infraType.type} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900 dark:text-gray-100">
                  {infraType.description}
                </h4>
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getCriticalityColor(infraType.criticality_level)}`}>
                  {infraType.criticality_level}
                </span>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Nodes:</span>
                  <span className="text-gray-900 dark:text-gray-100">{infraType.node_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Users:</span>
                  <span className="text-gray-900 dark:text-gray-100">{infraType.total_users.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Daily Consumption:</span>
                  <span className="text-gray-900 dark:text-gray-100">{formatConsumption(infraType.daily_consumption)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Efficiency:</span>
                  <span className="text-gray-900 dark:text-gray-100">{(infraType.avg_efficiency * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Water Loss:</span>
                  <span className="text-gray-900 dark:text-gray-100">{infraType.avg_water_loss}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Performance:</span>
                  <span className="text-gray-900 dark:text-gray-100">{infraType.performance_rating}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
