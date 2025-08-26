import React from 'react';
import { Card } from '@/components/ui/Card';
import { CloudIcon, RefreshCw as RefreshCwIcon } from 'lucide-react';

export const NoDataMessage: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="max-w-2xl mx-auto">
        <Card className="p-8">
          <div className="flex flex-col items-center justify-center text-center space-y-4">
            <div className="rounded-full bg-blue-100 p-6">
              <CloudIcon className="w-12 h-12 text-blue-600" />
            </div>
            <h2 className="text-2xl font-semibold text-gray-900">
              Weather Data Not Available
            </h2>
            <p className="text-gray-600 max-w-md">
              The weather monitoring data is currently not available. This could be because the weather stations are offline or the data collection system is being maintained.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors duration-200 flex items-center gap-2"
            >
              <RefreshCwIcon className="w-4 h-4" />
              Refresh Page
            </button>
            <div className="text-sm text-gray-500 mt-4">
              Please contact your system administrator if this issue persists.
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
