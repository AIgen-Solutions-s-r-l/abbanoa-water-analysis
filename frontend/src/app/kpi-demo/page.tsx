'use client';

import React from 'react';
import { KPIRibbon, TWRKPIRibbon } from '@/components/ui/KPIRibbon';
import { KPIMetric } from '@/lib/types';

export default function KPIDemoPage() {
  // Sample general KPI metrics
  const generalMetrics: KPIMetric[] = [
    {
      id: 'aum',
      label: 'Assets Under Management',
      value: 125000000,
      displayValue: '$125.0M',
      trend: 'up',
      trendValue: 5.2,
      trendLabel: 'vs last month',
      color: 'blue',
      tooltip: 'Total value of assets managed by the portfolio',
    },
    {
      id: 'active-positions',
      label: 'Active Positions',
      value: 48,
      displayValue: '48',
      trend: 'neutral',
      color: 'green',
      tooltip: 'Number of active investment positions',
    },
    {
      id: 'cash-position',
      label: 'Cash Position',
      value: 8.5,
      displayValue: '8.5%',
      trend: 'down',
      trendValue: -1.2,
      color: 'yellow',
      tooltip: 'Percentage of portfolio held in cash',
    },
    {
      id: 'expense-ratio',
      label: 'Expense Ratio',
      value: 0.75,
      displayValue: '0.75%',
      color: 'purple',
      tooltip: 'Annual operating expenses as percentage of AUM',
    },
  ];

  // Sample performance metrics
  const performanceMetrics: KPIMetric[] = [
    {
      id: 'ytd-return',
      label: 'YTD Return',
      value: 12.8,
      displayValue: '+12.8%',
      trend: 'up',
      trendValue: 12.8,
      color: 'green',
      tooltip: 'Year-to-date portfolio return',
    },
    {
      id: 'annualized-return',
      label: '3Y Annualized',
      value: 9.4,
      displayValue: '+9.4%',
      trend: 'up',
      color: 'blue',
      tooltip: 'Annualized return over the last 3 years',
    },
    {
      id: 'best-month',
      label: 'Best Month',
      value: 8.2,
      displayValue: '+8.2%',
      color: 'green',
      tooltip: 'Best single month performance',
    },
    {
      id: 'worst-month',
      label: 'Worst Month',
      value: -5.1,
      displayValue: '-5.1%',
      color: 'red',
      tooltip: 'Worst single month performance',
    },
  ];

  // Sample risk metrics
  const riskMetrics: KPIMetric[] = [
    {
      id: 'beta',
      label: 'Beta',
      value: 0.92,
      displayValue: '0.92',
      trend: 'down',
      trendValue: -0.05,
      color: 'purple',
      tooltip: 'Measure of portfolio volatility relative to the market',
    },
    {
      id: 'correlation',
      label: 'Correlation',
      value: 0.85,
      displayValue: '0.85',
      color: 'blue',
      tooltip: 'Correlation with benchmark index',
    },
    {
      id: 'tracking-error',
      label: 'Tracking Error',
      value: 3.2,
      displayValue: '3.2%',
      color: 'yellow',
      tooltip: 'Standard deviation of active returns',
    },
    {
      id: 'var',
      label: 'VaR (95%)',
      value: -2.8,
      displayValue: '-2.8%',
      color: 'red',
      tooltip: '95% Value at Risk - maximum expected loss',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            KPI Ribbon Component Demo
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Interactive demonstration of the KPI Ribbon component for financial metrics display
          </p>
        </div>

        <div className="space-y-12">
          {/* TWR-specific KPI Ribbon */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              TWR Performance Metrics
            </h2>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <TWRKPIRibbon
                upMarketTWR={15.2}
                downMarketTWR={-3.8}
                upMarketBenchmark={12.1}
                downMarketBenchmark={-5.2}
                totalReturn={8.7}
                volatility={14.3}
                sharpeRatio={1.42}
                maxDrawdown={-8.9}
                compact={false}
              />
            </div>
          </section>

          {/* General Portfolio Metrics */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              Portfolio Overview
            </h2>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <KPIRibbon
                metrics={generalMetrics}
                title="Portfolio Summary"
                showTrends={true}
                showTooltips={true}
                compact={false}
              />
            </div>
          </section>

          {/* Performance Metrics */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              Performance Analysis
            </h2>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <KPIRibbon
                metrics={performanceMetrics}
                title="Return Metrics"
                showTrends={true}
                showTooltips={true}
                compact={false}
              />
            </div>
          </section>

          {/* Risk Metrics */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              Risk Assessment
            </h2>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <KPIRibbon
                metrics={riskMetrics}
                title="Risk Indicators"
                showTrends={true}
                showTooltips={true}
                compact={false}
              />
            </div>
          </section>

          {/* Compact Variations */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              Compact Layouts
            </h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Compact TWR Metrics</h3>
                <TWRKPIRibbon
                  upMarketTWR={15.2}
                  downMarketTWR={-3.8}
                  totalReturn={8.7}
                  volatility={14.3}
                  sharpeRatio={1.42}
                  maxDrawdown={-8.9}
                  compact={true}
                />
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Compact Performance</h3>
                <KPIRibbon
                  metrics={performanceMetrics.slice(0, 4)}
                  showTrends={false}
                  showTooltips={true}
                  compact={true}
                />
              </div>
            </div>
          </section>

          {/* Component Features */}
          <section>
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              Component Features
            </h2>
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="prose max-w-none">
                <h3 className="text-lg font-semibold mb-4">Key Features:</h3>
                <ul className="space-y-2">
                  <li>✅ <strong>Responsive Grid Layout:</strong> Adapts to different screen sizes</li>
                  <li>✅ <strong>Trend Indicators:</strong> Visual up/down/neutral trend arrows</li>
                  <li>✅ <strong>Color-coded Cards:</strong> Different colors for metric categories</li>
                  <li>✅ <strong>Interactive Tooltips:</strong> Hover for detailed explanations</li>
                  <li>✅ <strong>Compact Mode:</strong> Space-efficient layout option</li>
                  <li>✅ <strong>Customizable:</strong> Flexible props for different use cases</li>
                  <li>✅ <strong>TWR Specialization:</strong> Pre-configured for Time-Weighted Returns</li>
                  <li>✅ <strong>TypeScript Support:</strong> Full type safety and IntelliSense</li>
                </ul>

                <h3 className="text-lg font-semibold mt-6 mb-4">Usage Examples:</h3>
                <div className="bg-gray-100 rounded p-4 text-sm font-mono">
                  <div className="text-gray-700">
                    {`// Basic KPI Ribbon
<KPIRibbon metrics={metrics} title="Portfolio Metrics" />

// TWR-specific ribbon
<TWRKPIRibbon 
  upMarketTWR={15.2} 
  downMarketTWR={-3.8}
  totalReturn={8.7}
  volatility={14.3}
  sharpeRatio={1.42}
  maxDrawdown={-8.9}
/>

// Compact mode
<KPIRibbon metrics={metrics} compact={true} />`}
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
} 