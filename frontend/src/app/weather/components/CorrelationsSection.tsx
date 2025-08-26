import React from 'react';
import { Card } from '@/components/ui/Card';
import { 
  RadialBarChart, RadialBar,
  Tooltip, ResponsiveContainer
} from 'recharts';
import { 
  SunIcon,
  CloudRainIcon,
  ThermometerIcon,
  ActivityIcon
} from 'lucide-react';

export const CorrelationsSection: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Weather-System Correlations */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Weather-System Performance Correlations</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Temperature vs Consumption */}
          <div>
            <h3 className="text-lg font-medium mb-3">Temperature vs Water Demand</h3>
            <ResponsiveContainer width="100%" height={250}>
              <RadialBarChart 
                cx="50%" 
                cy="50%" 
                innerRadius="10%" 
                outerRadius="90%" 
                barSize={10} 
                data={[
                  { name: 'Cold Days', value: 95, fill: '#3B82F6' },
                  { name: 'Mild Days', value: 100, fill: '#10B981' },
                  { name: 'Warm Days', value: 115, fill: '#F59E0B' },
                  { name: 'Hot Days', value: 130, fill: '#EF4444' }
                ]}
              >
                <RadialBar dataKey="value" cornerRadius={10} fill="#8884d8" label />
                <Tooltip />
              </RadialBarChart>
            </ResponsiveContainer>
          </div>

          {/* Rainfall vs Efficiency */}
          <div>
            <h3 className="text-lg font-medium mb-3">Rainfall vs System Efficiency</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-blue-100 dark:from-gray-800 dark:to-gray-700 rounded-lg border border-blue-200 dark:border-gray-600">
                <div className="flex items-center gap-3">
                  <SunIcon className="h-6 w-6 text-yellow-500" />
                  <span className="font-medium text-gray-900 dark:text-gray-100">Dry Conditions</span>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">98%</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Efficiency</p>
                </div>
              </div>
              <div className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                <div className="flex items-center gap-3">
                  <CloudRainIcon className="h-6 w-6 text-blue-500" />
                  <span className="font-medium text-gray-900 dark:text-gray-100">Rainy Conditions</span>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">85%</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Efficiency</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Key Insights */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Key Weather Insights</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 dark:bg-gray-800 p-4 rounded-lg border border-blue-200 dark:border-gray-700">
            <ThermometerIcon className="h-8 w-8 text-blue-600 dark:text-blue-400 mb-2" />
            <h3 className="font-semibold mb-1 text-gray-900 dark:text-gray-100">Temperature Effect</h3>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              Every 10°C increase in temperature correlates with a 15-20% increase in water demand
            </p>
          </div>
          <div className="bg-green-50 dark:bg-gray-800 p-4 rounded-lg border border-green-200 dark:border-gray-700">
            <ActivityIcon className="h-8 w-8 text-green-600 dark:text-green-400 mb-2" />
            <h3 className="font-semibold mb-1 text-gray-900 dark:text-gray-100">Seasonal Patterns</h3>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              Summer months show 40% higher consumption compared to winter baseline
            </p>
          </div>
          <div className="bg-amber-50 dark:bg-gray-800 p-4 rounded-lg border border-amber-200 dark:border-gray-700">
            <CloudRainIcon className="h-8 w-8 text-amber-600 dark:text-amber-400 mb-2" />
            <h3 className="font-semibold mb-1 text-gray-900 dark:text-gray-100">Rain Impact</h3>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              Heavy rainfall events can reduce system efficiency by up to 15% due to infiltration
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};
