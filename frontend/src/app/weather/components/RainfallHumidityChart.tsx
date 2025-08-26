import React from 'react';
import { Card } from '@/components/ui/Card';
import { 
  ComposedChart, Bar, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { HistoricalWeatherData } from '../types';

interface RainfallHumidityChartProps {
  data: HistoricalWeatherData[];
}

export const RainfallHumidityChart: React.FC<RainfallHumidityChartProps> = ({ data }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">Rainfall & Humidity</h2>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tickFormatter={formatDate} />
          <YAxis yAxisId="rain" orientation="left" />
          <YAxis yAxisId="humidity" orientation="right" />
          <Tooltip 
            labelFormatter={formatDate}
            formatter={(value: any, name: string) => [
              typeof value === 'number' ? value.toFixed(1) : value,
              name
            ]}
          />
          <Legend />
          <Bar yAxisId="rain" dataKey="rainfall" name="Rainfall (mm)" fill="#3B82F6" />
          <Line 
            yAxisId="humidity" 
            type="monotone" 
            dataKey="humidity" 
            name="Humidity (%)" 
            stroke="#10B981" 
            strokeWidth={2}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </Card>
  );
};
