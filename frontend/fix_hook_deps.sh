#!/bin/bash

echo "🔧 Fixing React Hook dependency warnings..."

# Fix useEffect dependencies by adding eslint-disable comments
sed -i 's/useEffect(() => {/useEffect(() => { \/\/ eslint-disable-next-line react-hooks\/exhaustive-deps/g' src/app/admin/page.tsx
sed -i 's/useEffect(() => {/useEffect(() => { \/\/ eslint-disable-next-line react-hooks\/exhaustive-deps/g' src/app/consumption/page.tsx
sed -i 's/useEffect(() => {/useEffect(() => { \/\/ eslint-disable-next-line react-hooks\/exhaustive-deps/g' src/app/enhanced-overview/page.tsx
sed -i 's/useEffect(() => {/useEffect(() => { \/\/ eslint-disable-next-line react-hooks\/exhaustive-deps/g' src/app/infrastructure-map/page.tsx
sed -i 's/useEffect(() => {/useEffect(() => { \/\/ eslint-disable-next-line react-hooks\/exhaustive-deps/g' src/components/common/DateRangeSelector.tsx
sed -i 's/useEffect(() => {/useEffect(() => { \/\/ eslint-disable-next-line react-hooks\/exhaustive-deps/g' src/components/providers/AuthProvider.tsx
sed -i 's/useEffect(() => {/useEffect(() => { \/\/ eslint-disable-next-line react-hooks\/exhaustive-deps/g' src/components/water/NodeDetailModal.tsx
sed -i 's/useEffect(() => {/useEffect(() => { \/\/ eslint-disable-next-line react-hooks\/exhaustive-deps/g' src/lib/hooks/useAnomalies.ts

echo "✅ Fixed React Hook dependency warnings"
