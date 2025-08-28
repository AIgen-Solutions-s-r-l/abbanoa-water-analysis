# Real Weather Data Integration Setup Guide

## 🌤️ Overview

This guide explains how to set up real weather data integration for the Abbanoa Water Infrastructure system using OpenWeatherMap API.

## 📋 Current Status

- ✅ **Production Weather Server**: `weather_server_prod.py` - Ready to use real API data
- ✅ **Fallback System**: Automatically uses mock data when API is unavailable
- ✅ **Multiple Locations**: Cagliari and 7 surrounding districts
- ✅ **Complete API Coverage**: All weather endpoints functional

## 🚀 Quick Setup

### Step 1: Get OpenWeatherMap API Key

1. Go to [OpenWeatherMap API](https://openweathermap.org/api)
2. Sign up for a free account
3. Get your API key (1000 calls/day free)
4. Copy the API key

### Step 2: Configure API Key

```bash
# Set API key for current session
export OPENWEATHERMAP_API_KEY="your_api_key_here"

# Make it permanent (add to ~/.bashrc)
echo 'export OPENWEATHERMAP_API_KEY="your_api_key_here"' >> ~/.bashrc
```

### Step 3: Start Production Weather Server

```bash
# Stop any existing weather servers
pkill -f "test_weather_server.py" 2>/dev/null || true
pkill -f "weather_server_prod.py" 2>/dev/null || true

# Start production server
python3 weather_server_prod.py
```

### Step 4: Test Integration

```bash
# Check API status
curl http://localhost:8002/weather/status

# Test current weather
curl http://localhost:8002/weather/current

# Test historical data
curl "http://localhost:8002/weather/historical?start_date=2025-01-01&end_date=2025-01-05"
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENWEATHERMAP_API_KEY` | Your OpenWeatherMap API key | Yes (for real data) |

### Server Configuration

- **Port**: 8002 (configurable in `weather_server_prod.py`)
- **Host**: 0.0.0.0 (accessible from all interfaces)
- **CORS**: Enabled for frontend integration

### Available Locations

The system monitors weather for these locations in Cagliari:

1. **Cagliari** (39.2238, 9.1217)
2. **Selargius** (39.2556, 9.1639)
3. **Quartucciu** (39.2539, 9.1753)
4. **Elmas** (39.2667, 9.0500)
5. **Assemini** (39.2833, 9.0000)
6. **Capoterra** (39.1833, 8.9667)
7. **Sestu** (39.3000, 9.0833)
8. **Monserrato** (39.2500, 9.1333)

## 📊 API Endpoints

### Current Weather
```
GET /weather/current?location={location}
```

### Historical Data
```
GET /weather/historical?start_date={YYYY-MM-DD}&end_date={YYYY-MM-DD}&interval={daily|weekly|monthly}&location={location}
```

### Weather Statistics
```
GET /weather/statistics?location={location}
```

### Impact Analysis
```
GET /weather/impact-analysis
```

### API Status
```
GET /weather/status
```

## 🔄 Data Sources

### Real Weather Data (When API Key Available)
- **Source**: OpenWeatherMap API
- **Coverage**: Current weather, forecasts
- **Update Frequency**: Real-time
- **Limits**: 1000 calls/day (free tier)

### Mock Data (Fallback)
- **Source**: Realistic synthetic data
- **Coverage**: Current, historical, statistics
- **Update Frequency**: Generated on-demand
- **Limits**: None

## 🛠️ Integration with Frontend

The production weather server is designed to work seamlessly with the existing frontend:

1. **Same API Structure**: All endpoints match the frontend expectations
2. **Automatic Fallback**: Uses mock data when real API is unavailable
3. **CORS Enabled**: Frontend can access the API directly
4. **Error Handling**: Graceful degradation when API fails

## 📈 Monitoring and Logging

### Log Levels
- **INFO**: Normal operations
- **WARNING**: API failures, fallback to mock data
- **ERROR**: Critical failures

### Status Endpoint
Check `/weather/status` to monitor:
- API key configuration
- Data source (Real vs Mock)
- Available locations
- Endpoint health

## 🔒 Security Considerations

1. **API Key Protection**: Store API key in environment variables
2. **Rate Limiting**: OpenWeatherMap enforces 1000 calls/day limit
3. **CORS Configuration**: Configured for specific domains
4. **Error Handling**: No sensitive data exposed in error messages

## 🚨 Troubleshooting

### Common Issues

1. **"No weather API key provided"**
   - Solution: Set `OPENWEATHERMAP_API_KEY` environment variable

2. **"Failed to get real weather data"**
   - Solution: Check API key validity and network connectivity
   - System will automatically fall back to mock data

3. **Port already in use**
   - Solution: Change port in `weather_server_prod.py` or stop conflicting service

4. **Import errors**
   - Solution: Install required packages: `apt install python3-aiohttp python3-fastapi python3-uvicorn`

### Testing Commands

```bash
# Test API key configuration
python3 -c "import os; print('API Key:', 'SET' if os.environ.get('OPENWEATHERMAP_API_KEY') else 'NOT SET')"

# Test weather integration
python3 -c "import sys; sys.path.append('scripts'); import weather_integration; print('Integration OK')"

# Test server startup
python3 weather_server_prod.py
```

## 📝 Migration from Test Server

To switch from the test weather server to the production server:

1. **Stop test server**:
   ```bash
   pkill -f "test_weather_server.py"
   ```

2. **Start production server**:
   ```bash
   python3 weather_server_prod.py
   ```

3. **Update nginx configuration** (if needed):
   - Point `/api/weather/` proxy to port 8002 instead of 8000

4. **Test integration**:
   ```bash
   curl https://curator.abbanoa.aigensolutions.it/api/weather/status
   ```

## 🎯 Next Steps

1. **Get API Key**: Sign up for OpenWeatherMap API
2. **Configure Environment**: Set the API key
3. **Start Production Server**: Use `weather_server_prod.py`
4. **Monitor Usage**: Check API call limits
5. **Scale Up**: Consider paid plans for higher limits

## 📞 Support

For issues with:
- **API Integration**: Check this guide and troubleshooting section
- **OpenWeatherMap**: Contact their support
- **System Integration**: Check logs and status endpoints
