'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { TrendingUp, Zap, Wrench, Droplets } from 'lucide-react';
import PeakDemandForecast from '@/components/predictions/PeakDemandForecast';
import EnergyOptimization from '@/components/predictions/EnergyOptimization';
import MaintenancePrediction from '@/components/predictions/MaintenancePrediction';
import WaterLossDetection from '@/components/predictions/WaterLossDetection';

export default function PredictionsPage() {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">ML Predictions</h1>
        <p className="text-gray-600">
          Advanced machine learning predictions for water infrastructure optimization
        </p>
      </div>

      <Tabs defaultValue="demand" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="demand" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Peak Demand
          </TabsTrigger>
          <TabsTrigger value="energy" className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Energy Optimization
          </TabsTrigger>
          <TabsTrigger value="maintenance" className="flex items-center gap-2">
            <Wrench className="h-4 w-4" />
            Maintenance
          </TabsTrigger>
          <TabsTrigger value="waterloss" className="flex items-center gap-2">
            <Droplets className="h-4 w-4" />
            Water Loss
          </TabsTrigger>
        </TabsList>

        <TabsContent value="demand" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Peak Demand Forecast</CardTitle>
              <CardDescription>
                Predict water demand patterns for the next 7-30 days using ML models
              </CardDescription>
            </CardHeader>
            <CardContent>
              <PeakDemandForecast />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="energy" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Energy Cost Optimization</CardTitle>
              <CardDescription>
                Optimize pump scheduling to minimize energy costs based on tariff structures
              </CardDescription>
            </CardHeader>
            <CardContent>
              <EnergyOptimization />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="maintenance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Predictive Maintenance</CardTitle>
              <CardDescription>
                AI-powered equipment health monitoring and failure prediction
              </CardDescription>
            </CardHeader>
            <CardContent>
              <MaintenancePrediction />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="waterloss" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Water Loss Detection</CardTitle>
              <CardDescription>
                Identify potential leaks and water loss patterns using ML analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <WaterLossDetection />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}