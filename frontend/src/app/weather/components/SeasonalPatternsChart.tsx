import React from 'react';
import { Card } from '@/components/ui/Card';
import { 
  ComposedChart, Bar, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { WeatherStatistics } from '../types';

interface SeasonalPatternsChartProps {
  seasonalPatterns: WeatherStatistics['seasonalPatterns'];
}

const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

export const SeasonalPatternsChart: React.FC<SeasonalPatternsChartProps> = ({ seasonalPatterns }) => {
  return (
    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">Seasonal Patterns</h2>
      <ResponsiveContainer width="100%" height={250}>
        <ComposedChart data={seasonalPatterns}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="month" 
            tickFormatter={(month) => monthNames[month - 1]}
          />
          <YAxis yAxisId="temp" orientation="left" />
          <YAxis yAxisId="rain" orientation="right" />
          <Tooltip 
            labelFormatter={(month) => monthNames[month - 1]}
            formatter={(value: any, name: string) => [
              typeof value === 'number' ? value.toFixed(1) : value,
              name
            ]}
          />
          <Legend />
          <Bar yAxisId="rain" dataKey="totalRainfall" name="Rainfall (mm)" fill="#3B82F6" />
          <Line yAxisId="temp" type="monotone" dataKey="avgTemperature" name="Avg Temp (°C)" stroke="#EF4444" />
        </ComposedChart>
      </ResponsiveContainer>
    </Card>
  );
};
