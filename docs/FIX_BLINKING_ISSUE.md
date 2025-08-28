# Fixed Page Blinking Issue

## Problem
The Enhanced Overview page was blinking/flashing every time data was refreshed (every 30 seconds), causing a poor user experience.

## Root Cause
The `loadRealData` function was setting `setLoading(true)` on every data refresh, which caused the entire page to show a loading screen and then re-render with new data, creating a blinking effect.

## Solution Implemented

### 1. **Separated Initial Load from Refreshes**
- Added `isInitialLoad` parameter to `loadRealData` function
- Only show full loading screen on initial page load
- Subsequent refreshes don't blank out the page

### 2. **Added Subtle Refresh Indicator**
- New `isRefreshing` state for background updates
- Shows a small, unobtrusive "Updating..." indicator in the top-right corner
- Users can see data is being refreshed without interrupting their view

### 3. **Reduced Refresh Frequency**
- Changed from 30 seconds to 2 minutes (120 seconds)
- Less aggressive refreshing reduces potential for disruption

## Changes Made

### Code Changes:
```typescript
// Added isInitialLoad parameter
const loadRealData = async (customDateRange?: {...}, isInitialLoad: boolean = false) => {
  // Only show loading screen on initial load
  if (isInitialLoad) {
    setLoading(true);
  } else {
    setIsRefreshing(true);
  }
  ...
}

// Updated all calls to loadRealData
loadRealData({...}, true);   // Initial load
loadRealData({...}, false);  // Refreshes

// Added subtle refresh indicator
{isRefreshing && (
  <div className="fixed top-4 right-4 ...">
    <div className="animate-spin ..."></div>
    <span>Updating...</span>
  </div>
)}
```

## Result
- No more page blinking during data refreshes
- Users see a subtle indicator when data is updating
- Better overall user experience
- Data still refreshes automatically every 2 minutes

## Visual Behavior
1. **Initial Load**: Shows full loading screen (expected behavior)
2. **Data Refresh**: Shows small "Updating..." indicator in top-right
3. **User Interaction**: Page remains fully interactive during refreshes
