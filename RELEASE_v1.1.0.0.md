# Release v1.1.0.0 - BigQuery Integration & Real-Time Dashboard

**Release Date**: 2025-07-04  
**Version**: 1.1.0.0  
**Type**: Minor Release (Feature Enhancement)

## 🎉 Overview

This release completes the BigQuery integration and transforms the dashboard into a fully functional real-time monitoring system. All synthetic data has been removed, and the system now exclusively displays actual sensor readings from the Selargius water infrastructure.

## 🚀 Key Features

### 1. **Complete BigQuery Integration**
- ✅ Direct access to 19,866+ real sensor readings
- ✅ Automatic Google Cloud credential detection
- ✅ Support for both Application Default Credentials and Service Accounts
- ✅ Fixed authentication errors with proper credential handling

### 2. **Enhanced Dashboard Functionality**
- ✅ **"Last Year" Time Range**: Analyze up to 365 days of historical data
- ✅ **Custom Date Range**: Select any dates between Nov 13, 2024 - Mar 31, 2025
- ✅ **Real-Time Node Status**: Live flow rates and pressure readings
- ✅ **Flow Rate Trends**: Actual sensor data visualization in Overview tab
- ✅ **Success Indicators**: Clear feedback when data loads successfully

### 3. **Improved User Experience**
- ✅ Automatic credential detection in `run_dashboard.sh`
- ✅ Clear data availability notices in sidebar
- ✅ Better error messages with debugging information
- ✅ Optimized performance with direct repository access

## 📊 Technical Improvements

### Architecture
- Removed dependency on broken use case APIs for data fetching
- Direct repository pattern implementation for better performance
- Proper async handling for concurrent data fetching
- Clean separation between ADC and service account authentication

### Code Quality
- Removed all synthetic data generation code
- Fixed sensor reading attribute access (flow_rate, pressure, volume)
- Proper null checks and empty data handling
- Enhanced error handling throughout the application

## 📋 Breaking Changes

None - This release maintains backward compatibility while enhancing functionality.

## 🔧 Installation

```bash
# Update to latest version
git pull origin main
git checkout v1.1.0.0

# Install dependencies
poetry install

# Run the dashboard
./run_dashboard.sh
```

## 📈 Dashboard Usage

1. **Select Time Range**: Now includes "Last Year" option
2. **Choose Custom Range**: Any dates within data availability
3. **Monitor Real Data**: 
   - Sant'Anna: 80-110 L/s flow rate
   - Seneca: ~4.5 bar pressure, 13 L/s flow
   - Selargius Tank: 12-35 L/s flow rate

## 🐛 Bug Fixes

- Fixed MalformedError with Application Default Credentials
- Resolved flow rate trends showing empty charts
- Fixed node status showing hardcoded "No Data"
- Corrected DataFrame pivoting for multiple nodes
- Fixed custom date range handling

## 📚 Documentation

- Updated README.md with comprehensive setup instructions
- Added detailed CHANGELOG.md entries
- Enhanced inline documentation for BigQuery setup

## 🎯 Next Steps

Future enhancements could include:
- Real-time data streaming (beyond 30-minute aggregates)
- Advanced anomaly detection algorithms
- Predictive maintenance features
- Mobile app integration

## 🙏 Acknowledgments

Thanks to the Abbanoa team for providing access to the BigQuery infrastructure and sensor data.

---

For questions or issues, please contact the development team or create an issue in the repository.