#!/bin/bash

echo "🔧 Comprehensive linting fix script..."

# Remove unused imports from about page
sed -i '/import.*Calculator.*from/d' src/app/about/page.tsx
sed -i '/import.*Gauge.*from/d' src/app/about/page.tsx
sed -i '/import.*Activity.*from/d' src/app/about/page.tsx

# Remove unused imports from admin page
sed -i '/import.*MailIcon.*from/d' src/app/admin/page.tsx
sed -i '/import.*PhoneIcon.*from/d' src/app/admin/page.tsx

# Remove unused imports from profile page
sed -i '/import.*MailIcon.*from/d' src/app/profile/page.tsx
sed -i '/import.*PhoneIcon.*from/d' src/app/profile/page.tsx

# Remove unused imports from settings page
sed -i '/import.*GlobeIcon.*from/d' src/app/settings/page.tsx
sed -i '/import.*VolumeIcon.*from/d' src/app/settings/page.tsx
sed -i '/import.*WifiIcon.*from/d' src/app/settings/page.tsx

# Remove unused imports from energy-optimization page
sed -i '/import.*MoonIcon.*from/d' src/app/energy-optimization/page.tsx
sed -i '/import.*RadialBarChart.*from/d' src/app/energy-optimization/page.tsx
sed -i '/import.*RadialBar.*from/d' src/app/energy-optimization/page.tsx
sed -i '/import.*Sankey.*from/d' src/app/energy-optimization/page.tsx

# Remove unused imports from ml-analytics page
sed -i '/import.*ActivityIcon.*from/d' src/app/ml-analytics/page.tsx
sed -i '/import.*ZapIcon.*from/d' src/app/ml-analytics/page.tsx
sed -i '/import.*DropletIcon.*from/d' src/app/ml-analytics/page.tsx
sed -i '/import.*LineChart.*from/d' src/app/ml-analytics/page.tsx
sed -i '/import.*Line.*from/d' src/app/ml-analytics/page.tsx
sed -i '/import.*BarChart.*from/d' src/app/ml-analytics/page.tsx
sed -i '/import.*Bar.*from/d' src/app/ml-analytics/page.tsx
sed -i '/import.*Cell.*from/d' src/app/ml-analytics/page.tsx

# Remove unused imports from monitoring page
sed -i '/import.*ActivityIcon.*from/d' src/app/monitoring/page.tsx

# Remove unused imports from infrastructure-map page
sed -i '/import.*Marker.*from/d' src/app/infrastructure-map/page.tsx

# Remove unused imports from water components
sed -i '/import.*Cell.*from/d' src/components/water/FlowAnalyticsChart.tsx
sed -i '/import.*AreaChart.*from/d' src/components/water/NetworkPerformanceAnalytics.tsx
sed -i '/import.*Area.*from/d' src/components/water/NetworkPerformanceAnalytics.tsx
sed -i '/import.*ScatterChart.*from/d' src/components/water/NetworkPerformanceAnalytics.tsx
sed -i '/import.*Scatter.*from/d' src/components/water/NetworkPerformanceAnalytics.tsx
sed -i '/import.*Activity.*from/d' src/components/water/NetworkPerformanceAnalytics.tsx
sed -i '/import.*RadialBarChart.*from/d' src/components/water/SystemHealthGauges.tsx
sed -i '/import.*RadialBar.*from/d' src/components/water/SystemHealthGauges.tsx
sed -i '/import.*Thermometer.*from/d' src/components/water/SystemHealthGauges.tsx

# Remove unused imports from providers
sed -i '/import.*Tenant.*from/d' src/components/providers/AuthProvider.tsx

# Remove unused imports from services
sed -i '/import.*RefreshTokenRequest.*from/d' src/services/auth.service.ts

# Remove unused imports from test files
sed -i '/import.*Anomaly.*from/d' src/services/__tests__/anomaly.service.spec.tsx
sed -i '/import.*RefreshTokenRequest.*from/d' src/services/__tests__/auth.service.int.tsx
sed -i '/import.*DashboardMetrics.*from/d' src/services/__tests__/dashboard.service.spec.tsx

echo "✅ Removed unused imports"
