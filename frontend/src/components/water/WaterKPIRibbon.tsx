'use client'

import React from 'react'
import { Activity, Droplets, Gauge, Shield, Clock, Zap } from 'lucide-react'

export interface WaterKPI {
  id: string
  label: string
  value: number | string
  unit: string
  status: 'good' | 'warning' | 'critical'
  icon: React.ComponentType<any>
  trend?: number // percentage change
  description?: string
}

export interface WaterKPIRibbonProps {
  kpis?: WaterKPI[]
  isLoading?: boolean
  className?: string
}

const defaultKPIs: WaterKPI[] = [
  {
    id: 'active_nodes',
    label: 'Active Nodes',
    value: 142,
    unit: '',
    status: 'good',
    icon: Activity,
    trend: 2.3,
    description: 'Number of operational monitoring nodes'
  },
  {
    id: 'flow_rate',
    label: 'Flow Rate',
    value: 1850.4,
    unit: 'L/s',
    status: 'good',
    icon: Droplets,
    trend: -0.8,
    description: 'Total system flow rate'
  },
  {
    id: 'pressure',
    label: 'Avg Pressure',
    value: 3.2,
    unit: 'bar',
    status: 'warning',
    icon: Gauge,
    trend: -2.1,
    description: 'Average network pressure'
  },
  {
    id: 'data_quality',
    label: 'Data Quality',
    value: 94.8,
    unit: '%',
    status: 'good',
    icon: Shield,
    trend: 1.2,
    description: 'Data completeness and accuracy'
  },
  {
    id: 'uptime',
    label: 'System Uptime',
    value: 99.2,
    unit: '%',
    status: 'good',
    icon: Clock,
    trend: 0.1,
    description: 'System availability percentage'
  },
  {
    id: 'energy_efficiency',
    label: 'Energy Efficiency',
    value: 0.68,
    unit: 'kWh/m³',
    status: 'warning',
    icon: Zap,
    trend: 3.2,
    description: 'Energy consumption per cubic meter'
  }
]

const getStatusColor = (status: WaterKPI['status']) => {
  switch (status) {
    case 'good':
      return 'text-green-600 bg-green-50 border-green-200'
    case 'warning':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    case 'critical':
      return 'text-red-600 bg-red-50 border-red-200'
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

const getTrendColor = (trend?: number) => {
  if (!trend) return 'text-gray-500'
  return trend > 0 ? 'text-green-600' : 'text-red-600'
}

const formatValue = (value: number | string, unit: string) => {
  if (typeof value === 'string') return value
  
  // Format large numbers
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}k`
  }
  
  // Format decimals appropriately
  if (value % 1 === 0) {
    return value.toString()
  }
  
  return value.toFixed(1)
}

const LoadingSkeleton = () => (
  <div className="animate-pulse">
    <div className="h-6 bg-gray-200 rounded w-24 mb-2"></div>
    <div className="h-8 bg-gray-200 rounded w-16 mb-1"></div>
    <div className="h-4 bg-gray-200 rounded w-20"></div>
  </div>
)

const KPICard: React.FC<{ kpi: WaterKPI; isLoading?: boolean }> = ({ kpi, isLoading }) => {
  const Icon = kpi.icon
  
  if (isLoading) {
    return (
      <div className="bg-white p-4 rounded-lg border border-gray-200 min-w-0">
        <LoadingSkeleton />
      </div>
    )
  }

  return (
    <div 
      className={`bg-white p-4 rounded-lg border transition-all duration-200 hover:shadow-md min-w-0 ${getStatusColor(kpi.status)}`}
      title={kpi.description}
    >
      <div className="flex items-center justify-between mb-2">
        <Icon className="w-5 h-5 flex-shrink-0" />
        {kpi.trend !== undefined && (
          <span className={`text-xs font-medium ${getTrendColor(kpi.trend)}`}>
            {kpi.trend > 0 ? '+' : ''}{kpi.trend.toFixed(1)}%
          </span>
        )}
      </div>
      
      <div className="space-y-1">
        <div className="text-2xl font-bold tracking-tight">
          {formatValue(kpi.value, kpi.unit)}
          {kpi.unit && <span className="text-sm font-normal ml-1">{kpi.unit}</span>}
        </div>
        <div className="text-sm font-medium truncate">
          {kpi.label}
        </div>
      </div>
    </div>
  )
}

export const WaterKPIRibbon: React.FC<WaterKPIRibbonProps> = ({ 
  kpis = defaultKPIs, 
  isLoading = false,
  className = ""
}) => {
  return (
    <div className={`w-full ${className}`}>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {kpis.map((kpi) => (
          <KPICard 
            key={kpi.id} 
            kpi={kpi} 
            isLoading={isLoading}
          />
        ))}
      </div>
    </div>
  )
}

export default WaterKPIRibbon 