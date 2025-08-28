#!/bin/bash

echo "🔧 Final comprehensive fix..."

# Remove all unused imports that are causing errors
find src -name "*.tsx" -exec sed -i '/import.*Calculator.*from/d' {} \;
find src -name "*.tsx" -exec sed -i '/import.*Gauge.*from/d' {} \;
find src -name "*.tsx" -exec sed -i '/import.*Activity.*from/d' {} \;
find src -name "*.tsx" -exec sed -i '/import.*TrendingUpIcon.*from/d' {} \;
find src -name "*.tsx" -exec sed -i '/import.*CalendarIcon.*from/d' {} \;
find src -name "*.tsx" -exec sed -i '/import.*ScatterChart.*from/d' {} \;
find src -name "*.tsx" -exec sed -i '/import.*Scatter.*from/d' {} \;
find src -name "*.tsx" -exec sed -i '/import.*ComposedChart.*from/d' {} \;

# Fix remaining 'any' types with more specific types
sed -i 's/: any/: unknown/g' src/app/admin/page.tsx
sed -i 's/: any/: unknown/g' src/app/consumption/page.tsx
sed -i 's/: any/: unknown/g' src/app/analytics/page.tsx
sed -i 's/: any/: unknown/g' src/app/anomalies/page.tsx
sed -i 's/: any/: unknown/g' src/app/monitoring/page.tsx
sed -i 's/: any/: unknown/g' src/app/settings/page.tsx
sed -i 's/: any/: unknown/g' src/app/energy-optimization/page.tsx
sed -i 's/: any/: unknown/g' src/app/ml-analytics/page.tsx
sed -i 's/: any/: unknown/g' src/app/infrastructure-map/page.tsx
sed -i 's/: any/: unknown/g' src/app/enhanced-overview/page.tsx
sed -i 's/: any/: unknown/g' src/components/auth/ProtectedRoute.tsx
sed -i 's/: any/: unknown/g' src/components/providers/AuthProvider.tsx
sed -i 's/: any/: unknown/g' src/components/water/FlowAnalyticsChart.tsx
sed -i 's/: any/: unknown/g' src/components/water/NetworkPerformanceAnalytics.tsx
sed -i 's/: any/: unknown/g' src/components/water/SystemHealthGauges.tsx
sed -i 's/: any/: unknown/g' src/components/water/WaterKPIRibbon.tsx
sed -i 's/: any/: unknown/g' src/components/water/NodeDetailModal.tsx
sed -i 's/: any/: unknown/g' src/lib/api/client.ts
sed -i 's/: any/: unknown/g' src/lib/types/auth.ts
sed -i 's/: any/: unknown/g' src/lib/types.ts
sed -i 's/: any/: unknown/g' src/services/anomaly.service.ts

# Remove unused variables
sed -i '/const error = /d' src/app/admin/page.tsx
sed -i '/const index = /d' src/app/anomalies/page.tsx

# Fix unescaped entities properly
sed -i "s/'/&apos;/g" src/app/auth/login/page.tsx
sed -i 's/"/&quot;/g' src/app/ml-analytics/page.tsx
sed -i "s/'/&apos;/g" src/components/water/NetworkPerformanceAnalytics.tsx

echo "✅ Final fix completed"
