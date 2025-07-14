'use client';

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { TWRChartProps, TWRDataPoint } from '@/lib/types';

/**
 * Dual-line chart component for displaying Cumulative TWR vs Benchmark performance
 * Implements task 4.3 requirements with Recharts
 */
export const TWRBenchmarkChart: React.FC<TWRChartProps> = ({
  data,
  title = 'Cumulative TWR vs Benchmark',
  height = 400,
  showGrid = true,
  showTooltip = true,
  showLegend = true,
}) => {
  // Custom tooltip formatter
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900">{`Date: ${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p
              key={index}
              className="text-sm"
              style={{ color: entry.color }}
            >
              {`${entry.name}: ${entry.value.toFixed(2)}%`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Custom legend formatter
  const formatLegendValue = (value: string) => {
    return <span className="text-sm font-medium text-gray-700">{value}</span>;
  };

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
          {title}
        </h3>
      )}
      
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <ResponsiveContainer width="100%" height={height}>
          <LineChart
            data={data}
            margin={{
              top: 20,
              right: 30,
              left: 20,
              bottom: 20,
            }}
          >
            {showGrid && (
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="#f0f0f0"
                opacity={0.7}
              />
            )}
            
            <XAxis
              dataKey="date"
              stroke="#6b7280"
              fontSize={12}
              tick={{ fill: '#6b7280' }}
              tickLine={{ stroke: '#6b7280' }}
            />
            
            <YAxis
              stroke="#6b7280"
              fontSize={12}
              tick={{ fill: '#6b7280' }}
              tickLine={{ stroke: '#6b7280' }}
              label={{ 
                value: 'Return (%)', 
                angle: -90, 
                position: 'insideLeft',
                style: { textAnchor: 'middle', fill: '#6b7280' }
              }}
            />

            {/* Zero reference line */}
            <ReferenceLine 
              y={0} 
              stroke="#9ca3af" 
              strokeDasharray="2 2"
              opacity={0.6}
            />

            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            
            {showLegend && (
              <Legend 
                formatter={formatLegendValue}
                wrapperStyle={{
                  paddingTop: '20px',
                }}
              />
            )}

            {/* TWR Line */}
            <Line
              type="monotone"
              dataKey="twr"
              stroke="#3b82f6"
              strokeWidth={2.5}
              name="Portfolio TWR"
              dot={{ fill: '#3b82f6', strokeWidth: 0, r: 3 }}
              activeDot={{ 
                r: 5, 
                stroke: '#3b82f6', 
                strokeWidth: 2,
                fill: '#ffffff'
              }}
            />

            {/* Benchmark Line */}
            <Line
              type="monotone"
              dataKey="benchmark"
              stroke="#10b981"
              strokeWidth={2.5}
              name="Benchmark"
              dot={{ fill: '#10b981', strokeWidth: 0, r: 3 }}
              activeDot={{ 
                r: 5, 
                stroke: '#10b981', 
                strokeWidth: 2,
                fill: '#ffffff'
              }}
              strokeDasharray="5 5"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Performance Summary */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
          <div className="text-blue-600 font-medium">Latest TWR</div>
          <div className="text-blue-900 font-semibold">
            {data.length > 0 ? `${data[data.length - 1].twr.toFixed(2)}%` : 'N/A'}
          </div>
        </div>
        
        <div className="bg-green-50 p-3 rounded-lg border border-green-200">
          <div className="text-green-600 font-medium">Latest Benchmark</div>
          <div className="text-green-900 font-semibold">
            {data.length > 0 ? `${data[data.length - 1].benchmark.toFixed(2)}%` : 'N/A'}
          </div>
        </div>
        
        <div className="bg-gray-50 p-3 rounded-lg border border-gray-200">
          <div className="text-gray-600 font-medium">Active Return</div>
          <div className="text-gray-900 font-semibold">
            {data.length > 0 
              ? `${(data[data.length - 1].twr - data[data.length - 1].benchmark).toFixed(2)}%`
              : 'N/A'
            }
          </div>
        </div>
        
        <div className="bg-purple-50 p-3 rounded-lg border border-purple-200">
          <div className="text-purple-600 font-medium">Data Points</div>
          <div className="text-purple-900 font-semibold">{data.length}</div>
        </div>
      </div>
    </div>
  );
};

export default TWRBenchmarkChart; 