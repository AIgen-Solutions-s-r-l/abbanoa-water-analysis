'use client';

import React from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export default function AnomaliesPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Anomalies
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Detected anomalies and system irregularities
          </p>
        </div>
        <div className="flex space-x-3">
          <Button variant="secondary" size="sm">
            Filter
          </Button>
          <Button size="sm">
            Run Detection
          </Button>
        </div>
      </div>

      {/* Content */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Anomaly List
          </h3>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p className="mt-2">Anomaly detection and listing will be integrated here</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 