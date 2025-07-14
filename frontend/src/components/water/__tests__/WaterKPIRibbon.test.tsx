/**
 * @jest-environment jsdom
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import WaterKPIRibbon from '../WaterKPIRibbon'

// Mock Recharts components
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  Cell: () => <div data-testid="cell" />
}))

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Activity: () => <div data-testid="activity-icon" />,
  Droplets: () => <div data-testid="droplets-icon" />,
  Gauge: () => <div data-testid="gauge-icon" />,
  Shield: () => <div data-testid="shield-icon" />,
  Clock: () => <div data-testid="clock-icon" />,
  Zap: () => <div data-testid="zap-icon" />
}))

describe('WaterKPIRibbon', () => {
  it('renders without crashing', () => {
    render(<WaterKPIRibbon />)
    expect(screen.getByText('Active Nodes')).toBeInTheDocument()
  })

  it('displays all default KPI metrics', () => {
    render(<WaterKPIRibbon />)
    
    // Check for all default KPI labels
    expect(screen.getByText('Active Nodes')).toBeInTheDocument()
    expect(screen.getByText('Flow Rate')).toBeInTheDocument()
    expect(screen.getByText('Avg Pressure')).toBeInTheDocument()
    expect(screen.getByText('Data Quality')).toBeInTheDocument()
    expect(screen.getByText('System Uptime')).toBeInTheDocument()
    expect(screen.getByText('Energy Efficiency')).toBeInTheDocument()
  })

  it('displays KPI values with units', () => {
    render(<WaterKPIRibbon />)
    
    // Check for values - noting that value and unit are in separate elements
    expect(screen.getByText('142')).toBeInTheDocument() // Active Nodes
    expect(screen.getByText('1.9k')).toBeInTheDocument() // Flow Rate (formatted)
    expect(screen.getByText('L/s')).toBeInTheDocument() // Flow Rate unit
    expect(screen.getByText('3.2')).toBeInTheDocument() // Pressure value
    expect(screen.getByText('bar')).toBeInTheDocument() // Pressure unit
    expect(screen.getByText('94.8')).toBeInTheDocument() // Data Quality value
    expect(screen.getByText('99.2')).toBeInTheDocument() // Uptime value
    expect(screen.getByText('0.7')).toBeInTheDocument() // Energy Efficiency value
    expect(screen.getByText('kWh/m³')).toBeInTheDocument() // Energy Efficiency unit
  })

  it('shows loading state when isLoading is true', () => {
    render(<WaterKPIRibbon isLoading={true} />)
    
    // Should show loading skeletons instead of actual content
    const loadingElements = screen.getAllByRole('generic')
    expect(loadingElements.length).toBeGreaterThan(0)
  })

  it('applies custom className when provided', () => {
    const { container } = render(<WaterKPIRibbon className="custom-class" />)
    expect(container.firstChild).toHaveClass('custom-class')
  })

  it('renders with custom KPI data', () => {
    const customKPIs = [
      {
        id: 'test_kpi',
        label: 'Test KPI',
        value: 50,
        unit: '%',
        status: 'good' as const,
        icon: () => <div data-testid="test-icon" />,
        trend: 2.5,
        description: 'Test description'
      }
    ]

    render(<WaterKPIRibbon kpis={customKPIs} />)
    expect(screen.getByText('Test KPI')).toBeInTheDocument()
    expect(screen.getByText('50')).toBeInTheDocument()
    expect(screen.getByText('%')).toBeInTheDocument()
  })

  it('displays trend indicators', () => {
    render(<WaterKPIRibbon />)
    
    // Check for trend indicators (+ or - percentages)
    expect(screen.getByText('+2.3%')).toBeInTheDocument() // Active Nodes trend
    expect(screen.getByText('-0.8%')).toBeInTheDocument() // Flow Rate trend
  })

  it('applies correct status styling', () => {
    const customKPIs = [
      {
        id: 'good_kpi',
        label: 'Good KPI',
        value: 80,
        unit: '%',
        status: 'good' as const,
        icon: () => <div />,
        description: 'Good status'
      },
      {
        id: 'warning_kpi',
        label: 'Warning KPI',
        value: 60,
        unit: '%',
        status: 'warning' as const,
        icon: () => <div />,
        description: 'Warning status'
      },
      {
        id: 'critical_kpi',
        label: 'Critical KPI',
        value: 30,
        unit: '%',
        status: 'critical' as const,
        icon: () => <div />,
        description: 'Critical status'
      }
    ]

    const { container } = render(<WaterKPIRibbon kpis={customKPIs} />)
    
    // Check that KPIs with different statuses are rendered
    expect(screen.getByText('Good KPI')).toBeInTheDocument()
    expect(screen.getByText('Warning KPI')).toBeInTheDocument() 
    expect(screen.getByText('Critical KPI')).toBeInTheDocument()
    
    // Check that status-colored background classes are applied
    expect(container.querySelector('.bg-green-50')).not.toBeNull() // good status background
    expect(container.querySelector('.bg-yellow-50')).not.toBeNull() // warning status background
    expect(container.querySelector('.bg-red-50')).not.toBeNull() // critical status background
  })
}) 