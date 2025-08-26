import React from 'react';
import { Card } from '@/components/ui/Card';
import { 
  BarChart, Bar, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import { AlertTriangleIcon } from 'lucide-react';
import { ImpactAnalysis } from '../types';

interface ImpactAnalysisSectionProps {
  impactAnalysis: ImpactAnalysis;
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export const ImpactAnalysisSection: React.FC<ImpactAnalysisSectionProps> = ({ impactAnalysis }) => {
  return (
    <div className="space-y-6">
      {/* Temperature Impact on Consumption */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Temperature Impact on Water Consumption</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={impactAnalysis.temperatureImpact}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="range" />
            <YAxis />
            <Tooltip formatter={(value: any) => `${value}%`} />
            <Bar dataKey="relativeConsumption" name="Relative Consumption">
              {impactAnalysis.temperatureImpact.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Card>

      {/* Rainfall Impact on System */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Rainfall Impact on System Efficiency</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={impactAnalysis.rainfallImpact}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.category}: ${entry.days} days`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="days"
              >
                {impactAnalysis.rainfallImpact.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-3">
            {impactAnalysis.rainfallImpact.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <div 
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                  />
                  <span className="font-medium text-gray-900 dark:text-gray-100">{item.category}</span>
                </div>
                <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">{item.systemEfficiency}%</span>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Recommendations */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Weather-Based Recommendations</h2>
        <div className="space-y-4">
          {impactAnalysis.recommendations.map((rec, idx) => (
            <div key={idx} className="border-l-4 border-blue-500 pl-4 py-3">
              <div className="flex items-start gap-3">
                <AlertTriangleIcon className="h-5 w-5 text-amber-500 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{rec.condition}</h3>
                  <p className="text-sm text-gray-600 mt-1">Impact: {rec.impact}</p>
                  <p className="text-sm text-gray-800 mt-2 font-medium">
                    <span className="text-blue-600">Action:</span> {rec.action}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
