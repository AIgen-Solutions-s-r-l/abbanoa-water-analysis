'use client'

import React from 'react'
import { 
  PieChart, Pie, Cell, ResponsiveContainer,
  RadialBarChart, RadialBar, Legend
} from 'recharts'
import { 
  Activity, Droplets, Zap, Settings, 
  AlertTriangle, CheckCircle, XCircle, 
  Thermometer, Gauge, Shield
} from 'lucide-react'

// Types
interface HealthGauge {
  id: string
  name: string
  value: number
  maxValue: number
  unit: string
  status: 'excellent' | 'good' | 'warning' | 'critical'
  icon: React.ComponentType<any>
  description: string
  lastUpdated: string
}

interface SystemHealthGaugesProps {
  gauges?: HealthGauge[]
  isLoading?: boolean
  className?: string
}

// Mock data
const mockGauges: HealthGauge[] = [
  {
    id: 'overall_health',
    name: 'Overall System Health',
    value: 87,
    maxValue: 100,
    unit: '%',
    status: 'good',
    icon: Activity,
    description: 'Overall system performance and reliability',
    lastUpdated: '2 minutes ago'
  },
  {
    id: 'water_quality',
    name: 'Water Quality Index',
    value: 94,
    maxValue: 100,
    unit: '%',
    status: 'excellent',
    icon: Droplets,
    description: 'Chemical and biological water quality indicators',
    lastUpdated: '5 minutes ago'
  },
  {
    id: 'pump_health',
    name: 'Pump System Health',
    value: 78,
    maxValue: 100,
    unit: '%',
    status: 'warning',
    icon: Settings,
    description: 'Pump operational efficiency and condition',
    lastUpdated: '3 minutes ago'
  },
  {
    id: 'energy_efficiency',
    name: 'Energy Efficiency',
    value: 82,
    maxValue: 100,
    unit: '%',
    status: 'good',
    icon: Zap,
    description: 'Energy consumption optimization level',
    lastUpdated: '1 minute ago'
  },
  {
    id: 'pressure_stability',
    name: 'Pressure Stability',
    value: 91,
    maxValue: 100,
    unit: '%',
    status: 'excellent',
    icon: Gauge,
    description: 'Network pressure consistency and stability',
    lastUpdated: '4 minutes ago'
  },
  {
    id: 'network_security',
    name: 'Network Security',
    value: 96,
    maxValue: 100,
    unit: '%',
    status: 'excellent',
    icon: Shield,
    description: 'System security and data protection level',
    lastUpdated: '6 minutes ago'
  }
]

const getStatusColor = (status: HealthGauge['status']) => {
  switch (status) {
    case 'excellent': return { color: '#10B981', bg: 'bg-green-50 dark:bg-green-900/20', text: 'text-green-700 dark:text-green-400' }
    case 'good': return { color: '#3B82F6', bg: 'bg-blue-50 dark:bg-blue-900/20', text: 'text-blue-700 dark:text-blue-400' }
    case 'warning': return { color: '#F59E0B', bg: 'bg-yellow-50 dark:bg-yellow-900/20', text: 'text-yellow-700 dark:text-yellow-400' }
    case 'critical': return { color: '#EF4444', bg: 'bg-red-50 dark:bg-red-900/20', text: 'text-red-700 dark:text-red-400' }
    default: return { color: '#6B7280', bg: 'bg-gray-50 dark:bg-gray-800', text: 'text-gray-700 dark:text-gray-300' }
  }
}

const getStatusIcon = (status: HealthGauge['status']) => {
  switch (status) {
    case 'excellent': return CheckCircle
    case 'good': return CheckCircle
    case 'warning': return AlertTriangle
    case 'critical': return XCircle
    default: return Activity
  }
}

const CircularGauge: React.FC<{ gauge: HealthGauge }> = ({ gauge }) => {
  const statusConfig = getStatusColor(gauge.status)
  const StatusIcon = getStatusIcon(gauge.status)
  const percentage = (gauge.value / gauge.maxValue) * 100
  
  // Data for the gauge
  const data = [
    {
      name: gauge.name,
      value: percentage,
      fill: statusConfig.color
    }
  ]
  
  const emptyData = [
    {
      name: 'remaining',
      value: 100 - percentage,
      fill: '#E5E7EB'
    }
  ]

  return (
    <div className={`bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-md dark:hover:shadow-lg transition-shadow ${statusConfig.bg}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <gauge.icon className={`w-5 h-5 ${statusConfig.text}`} />
          <h3 className="font-semibold text-gray-800 dark:text-gray-200">{gauge.name}</h3>
        </div>
        <StatusIcon className={`w-5 h-5 ${statusConfig.text}`} />
      </div>
      
      <div className="relative">
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={emptyData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              startAngle={90}
              endAngle={450}
              dataKey="value"
            >
              <Cell fill="#E5E7EB" />
            </Pie>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              startAngle={90}
              endAngle={90 + (percentage * 3.6)}
              dataKey="value"
            >
              <Cell fill={statusConfig.color} />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        
        {/* Center value display */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">
              {gauge.value}{gauge.unit}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400 capitalize">
              {gauge.status}
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-4 space-y-2">
        <p className="text-sm text-gray-600 dark:text-gray-400">{gauge.description}</p>
        <p className="text-xs text-gray-500 dark:text-gray-500">Updated {gauge.lastUpdated}</p>
      </div>
    </div>
  )
}

const OverallHealthSummary: React.FC<{ gauges: HealthGauge[] }> = ({ gauges }) => {
  const healthCounts = gauges.reduce((acc, gauge) => {
    acc[gauge.status] = (acc[gauge.status] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const averageHealth = Math.round(
    gauges.reduce((sum, gauge) => sum + (gauge.value / gauge.maxValue) * 100, 0) / gauges.length
  )

  const summaryData = [
    { name: 'Excellent', value: healthCounts.excellent || 0, fill: '#10B981' },
    { name: 'Good', value: healthCounts.good || 0, fill: '#3B82F6' },
    { name: 'Warning', value: healthCounts.warning || 0, fill: '#F59E0B' },
    { name: 'Critical', value: healthCounts.critical || 0, fill: '#EF4444' }
  ].filter(item => item.value > 0)

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
      <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">System Health Summary</h3>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Overall Health Score */}
        <div className="text-center">
          <div className="text-4xl font-bold text-gray-800 dark:text-gray-200 mb-2">
            {averageHealth}%
          </div>
          <div className="text-lg text-gray-600 dark:text-gray-400 mb-4">Overall Health Score</div>
          
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${
            averageHealth >= 90 ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400' :
            averageHealth >= 75 ? 'bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-400' :
            averageHealth >= 60 ? 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-400' :
            'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-400'
          }`}>
            {averageHealth >= 90 ? <CheckCircle className="w-4 h-4" /> :
             averageHealth >= 60 ? <AlertTriangle className="w-4 h-4" /> :
             <XCircle className="w-4 h-4" />}
            <span className="font-medium">
              {averageHealth >= 90 ? 'Excellent' :
               averageHealth >= 75 ? 'Good' :
               averageHealth >= 60 ? 'Warning' :
               'Critical'}
            </span>
          </div>
        </div>

        {/* Status Distribution */}
        <div>
          <h4 className="font-medium mb-3 text-gray-900 dark:text-gray-100">Component Status Distribution</h4>
          <ResponsiveContainer width="100%" height={150}>
            <PieChart>
              <Pie
                data={summaryData}
                cx="50%"
                cy="50%"
                outerRadius={60}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {summaryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Component Count Summary */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { status: 'excellent', label: 'Excellent', count: healthCounts.excellent || 0, color: 'text-green-600 dark:text-green-400' },
          { status: 'good', label: 'Good', count: healthCounts.good || 0, color: 'text-blue-600 dark:text-blue-400' },
          { status: 'warning', label: 'Warning', count: healthCounts.warning || 0, color: 'text-yellow-600 dark:text-yellow-400' },
          { status: 'critical', label: 'Critical', count: healthCounts.critical || 0, color: 'text-red-600 dark:text-red-400' }
        ].map((item) => (
          <div key={item.status} className="text-center">
            <div className={`text-2xl font-bold ${item.color}`}>
              {item.count}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">{item.label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

const LoadingSkeleton = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {[...Array(6)].map((_, index) => (
      <div key={index} className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700 animate-pulse">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-5 h-5 bg-gray-200 dark:bg-gray-600 rounded"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-32"></div>
        </div>
        <div className="w-full h-48 bg-gray-200 dark:bg-gray-600 rounded mb-4"></div>
        <div className="space-y-2">
          <div className="h-3 bg-gray-200 dark:bg-gray-600 rounded w-full"></div>
          <div className="h-3 bg-gray-200 dark:bg-gray-600 rounded w-24"></div>
        </div>
      </div>
    ))}
  </div>
)

export const SystemHealthGauges: React.FC<SystemHealthGaugesProps> = ({
  gauges = mockGauges,
  isLoading = false,
  className = ""
}) => {
  if (isLoading) {
    return (
      <div className={`w-full ${className}`}>
        <LoadingSkeleton />
      </div>
    )
  }

  return (
    <div className={`w-full space-y-6 ${className}`}>
      {/* Overall Summary */}
      <OverallHealthSummary gauges={gauges} />
      
      {/* Individual Gauges */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {gauges.map((gauge) => (
          <CircularGauge key={gauge.id} gauge={gauge} />
        ))}
      </div>
    </div>
  )
}

export default SystemHealthGauges 