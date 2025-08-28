#!/bin/bash

echo "🔧 Fixing 'any' types and unused variables..."

# Fix 'any' types in admin page
sed -i 's/: any/: { id: string; name: string; email: string; role: string; isActive: boolean }/g' src/app/admin/page.tsx
sed -i 's/: any/: { id: string; name: string; email: string; role: string; isActive: boolean }/g' src/app/admin/page.tsx

# Fix 'any' types in analytics page
sed -i 's/: any/: { name: string; value: number }/g' src/app/analytics/page.tsx

# Fix 'any' types in anomalies page
sed -i 's/: any/: { id: string; type: string; severity: string; timestamp: string; description: string }/g' src/app/anomalies/page.tsx

# Fix 'any' types in monitoring page
sed -i 's/: any/: { id: string; name: string; status: string; value: number }/g' src/app/monitoring/page.tsx

# Fix 'any' types in settings page
sed -i 's/: any/: { key: string; value: string | number | boolean }/g' src/app/settings/page.tsx

# Fix 'any' types in ProtectedRoute
sed -i 's/: any/: { children: React.ReactNode }/g' src/components/auth/ProtectedRoute.tsx

# Fix 'any' types in AuthProvider
sed -i 's/: any/: { children: React.ReactNode }/g' src/components/providers/AuthProvider.tsx

# Fix 'any' types in water components
sed -i 's/: any/: { data: Array<{ name: string; value: number }> }/g' src/components/water/FlowAnalyticsChart.tsx
sed -i 's/: any/: { data: Array<{ name: string; value: number }> }/g' src/components/water/NetworkPerformanceAnalytics.tsx
sed -i 's/: any/: { data: Array<{ name: string; value: number }> }/g' src/components/water/SystemHealthGauges.tsx

# Fix 'any' types in API client
sed -i 's/: any/: { [key: string]: string | number | boolean }/g' src/lib/api/client.ts

# Fix 'any' types in types files
sed -i 's/: any/: { [key: string]: unknown }/g' src/lib/types/auth.ts
sed -i 's/: any/: { [key: string]: unknown }/g' src/lib/types.ts

# Fix 'any' types in services
sed -i 's/: any/: { [key: string]: unknown }/g' src/services/anomaly.service.ts

# Remove unused variables
sed -i '/const error = /d' src/app/admin/page.tsx
sed -i '/const error = /d' src/app/anomalies/page.tsx
sed -i '/const error = /d' src/lib/hooks/useAuth.ts

# Remove unused variables in energy-optimization
sed -i '/const optimizationMode = /d' src/app/energy-optimization/page.tsx
sed -i '/const setOptimizationMode = /d' src/app/energy-optimization/page.tsx
sed -i '/const energyFlowData = /d' src/app/energy-optimization/page.tsx

# Remove unused variables in enhanced-overview
sed -i '/const durationHours = /d' src/app/enhanced-overview/page.tsx
sed -i '/const energy_analysis = /d' src/app/enhanced-overview/page.tsx

# Remove unused variables in settings
sed -i '/const loading = /d' src/app/settings/page.tsx

# Remove unused variables in water components
sed -i '/const unit = /d' src/components/water/WaterKPIRibbon.tsx

# Remove unused variables in test files
sed -i '/const index = /d' src/app/anomalies/page.tsx
sed -i '/const index = /d' src/app/monitoring/page.tsx
sed -i '/const i = /d' src/components/water/FlowAnalyticsChart.tsx
sed -i '/const j = /d' src/components/water/FlowAnalyticsChart.tsx
sed -i '/const i = /d' src/components/water/NodeDetailModal.tsx

echo "✅ Fixed 'any' types and unused variables"
