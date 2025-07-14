'use client'

import React, { useState } from 'react'
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ScatterChart, Scatter, Cell, Heatmap
} from 'recharts'
import { TrendingUp, Activity, BarChart3, Grid3X3 } from 'lucide-react'

// Types
interface PressureDistribution {
  zone: string
  minPressure: number
  avgPressure: number
  maxPressure: number
  nodeCount: number
  status: 'optimal' | 'warning' | 'critical'
}

interface EfficiencyTrend {
  timestamp: string
  energyEfficiency: number
  waterLoss: number
  pumpEfficiency: number
  operationalCost: number
}

interface DataQualityMetric {
  parameter: string
  completeness: number
  accuracy: number
  timeliness: number
  consistency: number
  overall: number
}

interface NetworkPerformanceAnalyticsProps {
  pressureData?: PressureDistribution[]
  efficiencyData?: EfficiencyTrend[]
  qualityData?: DataQualityMetric[]
  isLoading?: boolean
  className?: string
}

// Mock data
const mockPressureData: PressureDistribution[] = [
  { zone: 'Zone A', minPressure: 2.1, avgPressure: 3.2, maxPressure: 4.1, nodeCount: 24, status: 'optimal' },
  { zone: 'Zone B', minPressure: 1.8, avgPressure: 2.9, maxPressure: 3.8, nodeCount: 18, status: 'warning' },
  { zone: 'Zone C', minPressure: 2.3, avgPressure: 3.4, maxPressure: 4.2, nodeCount: 31, status: 'optimal' },
  { zone: 'Zone D', minPressure: 1.2, avgPressure: 2.1, maxPressure: 2.8, nodeCount: 15, status: 'critical' },
  { zone: 'Zone E', minPressure: 2.0, avgPressure: 3.1, maxPressure: 3.9, nodeCount: 22, status: 'optimal' },
  { zone: 'Zone F', minPressure: 1.9, avgPressure: 2.8, maxPressure: 3.6, nodeCount: 19, status: 'warning' }
]

const mockEfficiencyData: EfficiencyTrend[] = [
  { timestamp: '00:00', energyEfficiency: 0.65, waterLoss: 12.3, pumpEfficiency: 78.2, operationalCost: 145.2 },
  { timestamp: '04:00', energyEfficiency: 0.68, waterLoss: 11.8, pumpEfficiency: 79.1, operationalCost: 142.1 },
  { timestamp: '08:00', energyEfficiency: 0.72, waterLoss: 13.1, pumpEfficiency: 81.3, operationalCost: 148.7 },
  { timestamp: '12:00', energyEfficiency: 0.69, waterLoss: 14.2, pumpEfficiency: 77.8, operationalCost: 152.3 },
  { timestamp: '16:00', energyEfficiency: 0.71, waterLoss: 12.9, pumpEfficiency: 80.5, operationalCost: 147.6 },
  { timestamp: '20:00', energyEfficiency: 0.67, waterLoss: 11.5, pumpEfficiency: 79.7, operationalCost: 143.8 }
]

const mockQualityData: DataQualityMetric[] = [
  { parameter: 'Flow Rate', completeness: 98.5, accuracy: 96.2, timeliness: 99.1, consistency: 94.8, overall: 97.2 },
  { parameter: 'Pressure', completeness: 97.8, accuracy: 98.1, timeliness: 98.7, consistency: 96.3, overall: 97.7 },
  { parameter: 'Temperature', completeness: 95.2, accuracy: 97.4, timeliness: 96.8, consistency: 95.9, overall: 96.3 },
  { parameter: 'pH Level', completeness: 92.1, accuracy: 94.7, timeliness: 93.5, consistency: 91.8, overall: 93.0 },
  { parameter: 'Chlorine', completeness: 89.8, accuracy: 92.3, timeliness: 91.2, consistency: 88.7, overall: 90.5 },
  { parameter: 'Turbidity', completeness: 91.5, accuracy: 93.8, timeliness: 92.4, consistency: 90.2, overall: 92.0 }
]

const TabButton: React.FC<{
  active: boolean
  onClick: () => void
  icon: React.ComponentType<any>
  label: string
}> = ({ active, onClick, icon: Icon, label }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
      active 
        ? 'bg-blue-600 text-white shadow-sm' 
        : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
    }`}
  >
    <Icon className="w-4 h-4" />
    {label}
  </button>
)

const PressureDistributionChart: React.FC<{ data: PressureDistribution[] }> = ({ data }) => {
  const getZoneColor = (status: string) => {
    switch (status) {
      case 'optimal': return '#10B981'
      case 'warning': return '#F59E0B'
      case 'critical': return '#EF4444'
      default: return '#6B7280'
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pressure Range Chart */}
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold mb-4">Pressure Distribution by Zone</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="zone" />
              <YAxis label={{ value: 'Pressure (bar)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="minPressure" fill="#93C5FD" name="Min Pressure" />
              <Bar dataKey="avgPressure" fill="#3B82F6" name="Avg Pressure" />
              <Bar dataKey="maxPressure" fill="#1E40AF" name="Max Pressure" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Zone Status Overview */}
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold mb-4">Zone Status Overview</h3>
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="avgPressure" name="Avg Pressure" />
              <YAxis dataKey="nodeCount" name="Node Count" />
              <Tooltip 
                cursor={{ strokeDasharray: '3 3' }}
                formatter={(value, name) => [value, name]}
                labelFormatter={(label) => `Zone: ${label}`}
              />
              <Scatter dataKey="nodeCount" fill="#8884d8">
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getZoneColor(entry.status)} />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Zone Details Table */}
      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-semibold mb-4">Zone Details</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">Zone</th>
                <th className="text-left py-2">Min Pressure</th>
                <th className="text-left py-2">Avg Pressure</th>
                <th className="text-left py-2">Max Pressure</th>
                <th className="text-left py-2">Nodes</th>
                <th className="text-left py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {data.map((zone) => (
                <tr key={zone.zone} className="border-b">
                  <td className="py-2 font-medium">{zone.zone}</td>
                  <td className="py-2">{zone.minPressure.toFixed(1)} bar</td>
                  <td className="py-2">{zone.avgPressure.toFixed(1)} bar</td>
                  <td className="py-2">{zone.maxPressure.toFixed(1)} bar</td>
                  <td className="py-2">{zone.nodeCount}</td>
                  <td className="py-2">
                    <span 
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        zone.status === 'optimal' ? 'bg-green-100 text-green-800' :
                        zone.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}
                    >
                      {zone.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

const EfficiencyTrendsChart: React.FC<{ data: EfficiencyTrend[] }> = ({ data }) => (
  <div className="space-y-6">
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Energy Efficiency and Water Loss */}
      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-semibold mb-4">Energy Efficiency & Water Loss</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Line 
              yAxisId="left" 
              type="monotone" 
              dataKey="energyEfficiency" 
              stroke="#10B981" 
              strokeWidth={2}
              name="Energy Efficiency (kWh/m³)"
            />
            <Line 
              yAxisId="right" 
              type="monotone" 
              dataKey="waterLoss" 
              stroke="#EF4444" 
              strokeWidth={2}
              name="Water Loss (%)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Pump Efficiency and Operational Cost */}
      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-semibold mb-4">Pump Efficiency & Operational Cost</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Line 
              yAxisId="left" 
              type="monotone" 
              dataKey="pumpEfficiency" 
              stroke="#3B82F6" 
              strokeWidth={2}
              name="Pump Efficiency (%)"
            />
            <Line 
              yAxisId="right" 
              type="monotone" 
              dataKey="operationalCost" 
              stroke="#F59E0B" 
              strokeWidth={2}
              name="Operational Cost (€)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  </div>
)

const DataQualityMatrix: React.FC<{ data: DataQualityMetric[] }> = ({ data }) => {
  const getQualityColor = (value: number) => {
    if (value >= 95) return 'bg-green-500'
    if (value >= 90) return 'bg-yellow-500'
    if (value >= 80) return 'bg-orange-500'
    return 'bg-red-500'
  }

  return (
    <div className="space-y-6">
      {/* Quality Matrix */}
      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-semibold mb-4">Data Quality Matrix</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3">Parameter</th>
                <th className="text-center py-3">Completeness</th>
                <th className="text-center py-3">Accuracy</th>
                <th className="text-center py-3">Timeliness</th>
                <th className="text-center py-3">Consistency</th>
                <th className="text-center py-3">Overall</th>
              </tr>
            </thead>
            <tbody>
              {data.map((metric) => (
                <tr key={metric.parameter} className="border-b">
                  <td className="py-3 font-medium">{metric.parameter}</td>
                  <td className="py-3 text-center">
                    <div className="flex items-center justify-center">
                      <div className={`w-12 h-6 rounded ${getQualityColor(metric.completeness)} flex items-center justify-center text-white text-xs font-medium`}>
                        {metric.completeness.toFixed(1)}%
                      </div>
                    </div>
                  </td>
                  <td className="py-3 text-center">
                    <div className="flex items-center justify-center">
                      <div className={`w-12 h-6 rounded ${getQualityColor(metric.accuracy)} flex items-center justify-center text-white text-xs font-medium`}>
                        {metric.accuracy.toFixed(1)}%
                      </div>
                    </div>
                  </td>
                  <td className="py-3 text-center">
                    <div className="flex items-center justify-center">
                      <div className={`w-12 h-6 rounded ${getQualityColor(metric.timeliness)} flex items-center justify-center text-white text-xs font-medium`}>
                        {metric.timeliness.toFixed(1)}%
                      </div>
                    </div>
                  </td>
                  <td className="py-3 text-center">
                    <div className="flex items-center justify-center">
                      <div className={`w-12 h-6 rounded ${getQualityColor(metric.consistency)} flex items-center justify-center text-white text-xs font-medium`}>
                        {metric.consistency.toFixed(1)}%
                      </div>
                    </div>
                  </td>
                  <td className="py-3 text-center">
                    <div className="flex items-center justify-center">
                      <div className={`w-16 h-8 rounded ${getQualityColor(metric.overall)} flex items-center justify-center text-white text-sm font-bold`}>
                        {metric.overall.toFixed(1)}%
                      </div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Overall Quality Chart */}
      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-semibold mb-4">Overall Data Quality by Parameter</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} layout="horizontal">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[0, 100]} />
            <YAxis dataKey="parameter" type="category" />
            <Tooltip />
            <Bar dataKey="overall" fill="#3B82F6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export const NetworkPerformanceAnalytics: React.FC<NetworkPerformanceAnalyticsProps> = ({
  pressureData = mockPressureData,
  efficiencyData = mockEfficiencyData,
  qualityData = mockQualityData,
  isLoading = false,
  className = ""
}) => {
  const [activeTab, setActiveTab] = useState<'pressure' | 'efficiency' | 'quality'>('pressure')

  const tabs = [
    { id: 'pressure' as const, label: 'Pressure Distribution', icon: BarChart3 },
    { id: 'efficiency' as const, label: 'Efficiency Trends', icon: TrendingUp },
    { id: 'quality' as const, label: 'Data Quality Matrix', icon: Grid3X3 }
  ]

  if (isLoading) {
    return (
      <div className={`w-full ${className}`}>
        <div className="bg-white p-6 rounded-lg border">
          <div className="animate-pulse space-y-4">
            <div className="h-6 bg-gray-200 rounded w-48"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`w-full ${className}`}>
      {/* Tab Navigation */}
      <div className="flex flex-wrap gap-2 mb-6">
        {tabs.map((tab) => (
          <TabButton
            key={tab.id}
            active={activeTab === tab.id}
            onClick={() => setActiveTab(tab.id)}
            icon={tab.icon}
            label={tab.label}
          />
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'pressure' && <PressureDistributionChart data={pressureData} />}
      {activeTab === 'efficiency' && <EfficiencyTrendsChart data={efficiencyData} />}
      {activeTab === 'quality' && <DataQualityMatrix data={qualityData} />}
    </div>
  )
}

export default NetworkPerformanceAnalytics 