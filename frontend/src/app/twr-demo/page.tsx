'use client';

import React from 'react';
import TWRBenchmarkChart from '@/components/charts/TWRBenchmarkChart';
import { TWRDataPoint } from '@/lib/types';

// Sample TWR data for demonstration
const generateSampleTWRData = (): TWRDataPoint[] => {
  const data: TWRDataPoint[] = [];
  const startDate = new Date('2023-01-01');
  let twrValue = 0;
  let benchmarkValue = 0;

  for (let i = 0; i < 12; i++) {
    const date = new Date(startDate);
    date.setMonth(date.getMonth() + i);
    
    // Simulate monthly returns with some volatility
    const monthlyTWR = (Math.random() - 0.4) * 3; // -1.2% to 1.8% monthly
    const monthlyBenchmark = (Math.random() - 0.45) * 2.5; // -1.125% to 1.375% monthly
    
    twrValue += monthlyTWR;
    benchmarkValue += monthlyBenchmark;
    
    data.push({
      date: date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' }),
      twr: Number(twrValue.toFixed(2)),
      benchmark: Number(benchmarkValue.toFixed(2)),
      period: `Month ${i + 1}`,
    });
  }

  return data;
};

export default function TWRDemoPage() {
  const sampleData = generateSampleTWRData();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            TWR vs Benchmark Chart Demo
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Interactive demonstration of the Cumulative Time-Weighted Return chart component
          </p>
        </div>

        <div className="space-y-8">
          {/* Main Chart */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <TWRBenchmarkChart 
              data={sampleData}
              title="Portfolio Performance vs S&P 500 Benchmark"
              height={500}
              showGrid={true}
              showTooltip={true}
              showLegend={true}
            />
          </div>

          {/* Chart Variations */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <TWRBenchmarkChart 
                data={sampleData}
                title="Compact View"
                height={300}
                showGrid={false}
                showLegend={false}
              />
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <TWRBenchmarkChart 
                data={sampleData.slice(-6)} // Last 6 months
                title="Recent Performance (6 Months)"
                height={300}
                showGrid={true}
                showTooltip={true}
                showLegend={true}
              />
            </div>
          </div>

          {/* Data Table */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Sample Data</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Portfolio TWR (%)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Benchmark (%)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Active Return (%)
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {sampleData.map((point, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {point.date}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {point.twr.toFixed(2)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {point.benchmark.toFixed(2)}%
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                        point.twr - point.benchmark >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {(point.twr - point.benchmark).toFixed(2)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 