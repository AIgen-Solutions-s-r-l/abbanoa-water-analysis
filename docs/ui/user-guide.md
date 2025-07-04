# Abbanoa Water Network Forecasting Dashboard - User Guide

## Getting Started

Welcome to the Abbanoa Water Network Forecasting Dashboard! This guide will help you understand how to use the dashboard to visualize and analyze water infrastructure forecasts.

## Dashboard Overview

The dashboard provides:
- **7-day forecasts** for water network metrics
- **Historical context** showing past 30 days of data
- **Interactive filters** for easy parameter selection
- **Confidence intervals** to understand prediction uncertainty
- **Export capabilities** for further analysis

## Using the Forecast Tab

### 1. Selecting Parameters

#### District Selection
- Use the **"Select District"** dropdown in the sidebar
- Available districts: DIST_001, DIST_002, DIST_003
- Each district represents a different water distribution area

#### Metric Selection
- Choose from three key metrics:
  - **Flow Rate (L/s)**: Water flow in liters per second
  - **Reservoir Level (m)**: Water level in meters
  - **Pressure (bar)**: System pressure in bars

#### Forecast Horizon
- Use the slider to select 1-7 days of forecast
- Default is 7 days for maximum visibility
- Shorter horizons typically have higher accuracy

### 2. Understanding the Visualization

#### Chart Elements

```
┌─────────────────────────────────────────────┐
│  Historical Data ——— Forecast - - - - - -   │
│                    ┊                         │
│                    ┊  ╱─────╲ Confidence    │
│         ╱──────────┊─╱       ╲ Interval     │
│    ────╱           ┊          ╲              │
│                    Now                       │
└─────────────────────────────────────────────┘
```

- **Blue Solid Line**: Historical data (past 30 days)
- **Orange Dashed Line**: Forecast predictions
- **Orange Shaded Area**: 80% confidence interval
- **Vertical Dotted Line**: Current time marker

#### Reading the Chart

1. **Historical Trends**: Look at the blue line to understand recent patterns
2. **Forecast Direction**: The orange dashed line shows expected future values
3. **Uncertainty Bands**: Wider bands indicate less certainty in predictions
4. **Hover for Details**: Move your mouse over the chart to see exact values

### 3. Key Metrics Cards

On the right side of the forecast tab:

- **Next Day Forecast**: Tomorrow's predicted value with percentage change
- **Confidence Score**: How reliable the forecast is (Higher is better)
- **Model Info**: Shows ARIMA_PLUS model and last update time

### 4. Display Options

In the sidebar under "Display Options":

- **Show Confidence Interval**: Toggle the uncertainty bands on/off
- **Show Historical Data**: Toggle the historical context on/off
- **Auto-refresh**: Enable automatic data updates every 5 minutes

## Interpreting Confidence Intervals

### What is an 80% Confidence Interval?

The shaded area represents where we expect the actual value to fall 80% of the time:
- **Narrow bands** = High confidence in the prediction
- **Wide bands** = More uncertainty in the prediction

### Why 80% Instead of 95%?

We use 80% confidence intervals because:
- They provide a practical range for operational planning
- They're less conservative than 95% intervals
- They balance precision with usability

### Factors Affecting Confidence

1. **Time Horizon**: Further predictions have wider intervals
2. **Data Variability**: More variable metrics have wider intervals
3. **Seasonal Patterns**: Well-established patterns have narrower intervals

## Exporting Data and Charts

### Export Options

Two export formats are available:

#### CSV Export
- Click **"📥 Download CSV"**
- Includes all forecast data points
- Compatible with Excel and other spreadsheet tools
- Columns: timestamp, district_id, metric, forecast_value, bounds

#### JSON Export
- Click **"📥 Download JSON"**
- Structured data format for developers
- Includes metadata and all forecast details

### Saving Charts

To save the visualization:
1. Hover over the chart
2. Click the camera icon in the top toolbar
3. Choose "Download as PNG"
4. The image saves with your selected parameters in the filename

## Tips and Best Practices

### For Daily Operations

1. **Check Morning Forecasts**: Review all districts at the start of each day
2. **Focus on Anomalies**: Look for unusual spikes or drops in predictions
3. **Compare Districts**: Switch between districts to identify patterns
4. **Monitor Confidence**: Pay extra attention when confidence is low

### For Planning

1. **Use 7-Day Horizon**: Get the full weekly picture for planning
2. **Export Weekly Data**: Create reports by exporting CSV files
3. **Track Trends**: Compare week-over-week patterns
4. **Note Seasonal Changes**: Be aware of typical seasonal variations

### For Analysis

1. **Correlate Metrics**: Check if pressure drops correlate with high flow
2. **Identify Patterns**: Look for daily or weekly cycles
3. **Validate Predictions**: Compare yesterday's forecast with actual values
4. **Document Anomalies**: Export data when unusual patterns occur

## Troubleshooting Common Issues

### Dashboard Not Loading

1. Check your internet connection
2. Refresh the page (Ctrl+R or Cmd+R)
3. Clear browser cache if issues persist
4. Try a different browser

### Data Not Updating

1. Check the "Last updated" timestamp
2. Click the "🔄 Refresh" button
3. Verify Auto-refresh is enabled if desired
4. Check for any error messages

### Chart Appears Blank

1. Verify parameters are selected
2. Check if data exists for the selection
3. Try a different district or metric
4. Contact support if issue persists

### Export Not Working

1. Check browser download settings
2. Ensure pop-ups are not blocked
3. Try a different export format
4. Verify you have disk space

## Keyboard Shortcuts

- **Tab**: Navigate between controls
- **Enter**: Apply selection
- **Esc**: Close dropdowns
- **Space**: Toggle checkboxes

## Mobile Usage

The dashboard is mobile-responsive:
- **Portrait Mode**: Sidebar appears above chart
- **Landscape Mode**: Side-by-side layout
- **Touch Gestures**: Pinch to zoom on charts
- **Simplified UI**: Optimized for smaller screens

## Getting Help

### Information Resources

- **Model Information**: Click the expander in sidebar
- **How to Use**: Step-by-step guide in sidebar
- **System Performance**: Check latency and cache status

### Contact Support

For technical issues or questions:
- GitHub Issues: [Report a Bug](https://github.com/AIgen-Solutions-s-r-l/abbanoa-water-analysis/issues)
- Documentation: [View on GitHub](https://github.com/AIgen-Solutions-s-r-l/abbanoa-water-analysis)

## Glossary

- **ARIMA_PLUS**: Advanced time series forecasting model
- **Confidence Interval**: Range of likely values
- **Flow Rate**: Volume of water per unit time
- **Horizon**: Number of days to forecast
- **MAPE**: Mean Absolute Percentage Error (accuracy metric)
- **Reservoir Level**: Height of water in storage
- **Time Series**: Data points indexed in time order