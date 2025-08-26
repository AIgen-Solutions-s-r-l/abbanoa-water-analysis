import React from 'react';
import { Card } from '@/components/ui/Card';
import { 
  AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { HistoricalWeatherData } from '../types';

interface TemperatureTrendsChartProps {
  data: HistoricalWeatherData[];
}

export const TemperatureTrendsChart: React.FC<TemperatureTrendsChartProps> = ({ data }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">Temperature Trends</h2>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tickFormatter={formatDate} />
          <YAxis />
          <Tooltip 
            labelFormatter={formatDate}
            formatter={(value: any) => `${value?.toFixed(1)}°C`}
          />
          <Legend />
          <Area 
            type="monotone" 
            dataKey="temperatureMax" 
            stackId="1"
            stroke="#EF4444" 
            fill="#FEE2E2" 
            name="Max Temp"
          />
          <Area 
            type="monotone" 
            dataKey="temperature" 
            stackId="2"
            stroke="#F59E0B" 
            fill="#FEF3C7" 
            name="Avg Temp"
          />
          <Area 
            type="monotone" 
            dataKey="temperatureMin" 
            stackId="3"
            stroke="#3B82F6" 
            fill="#DBEAFE" 
            name="Min Temp"
          />
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  );
};
