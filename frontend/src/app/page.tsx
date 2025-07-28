'use client';

import React from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { MetricsGrid } from '@/components/features/dashboard/MetricsGrid';
import { RecentAnomalies } from '@/components/features/dashboard/RecentAnomalies';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

function DashboardContent() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Dashboard
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Water management system overview
          </p>
        </div>
        <div className="flex space-x-3">
          <Button variant="secondary" size="sm">
            Refresh Data
          </Button>
          <Button size="sm">
            Run Anomaly Detection
          </Button>
        </div>
      </div>

      {/* Metrics Grid */}
      <MetricsGrid />

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Anomalies */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Recent Anomalies
            </h3>
          </CardHeader>
          <CardContent>
            <RecentAnomalies />
          </CardContent>
        </Card>

        {/* System Status */}
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              System Status
            </h3>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Cache Status
                </span>
                <span className="text-sm text-green-600 dark:text-green-400">
                  Active
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Database Connection
                </span>
                <span className="text-sm text-green-600 dark:text-green-400">
                  Connected
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Last Data Sync
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  2 minutes ago
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  // TEMPORARY: MVP Demo mode - bypass ProtectedRoute in development
  if (process.env.NODE_ENV === 'development') {
    return <DashboardContent />;
  }
  
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
