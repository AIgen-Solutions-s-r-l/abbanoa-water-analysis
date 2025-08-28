#!/bin/bash

echo "🌤️ Setting up Real Weather Data Integration"
echo "=============================================="
echo ""

# Check if API key is already set
if [ -n "$OPENWEATHERMAP_API_KEY" ]; then
    echo "✅ OpenWeatherMap API key is already configured"
    echo "Current API key: ${OPENWEATHERMAP_API_KEY:0:8}..."
else
    echo "❌ OpenWeatherMap API key is not configured"
    echo ""
    echo "To get a free API key:"
    echo "1. Go to: https://openweathermap.org/api"
    echo "2. Sign up for a free account"
    echo "3. Get your API key (1000 calls/day free)"
    echo "4. Copy the API key"
    echo ""
    
    read -p "Enter your OpenWeatherMap API key: " api_key
    
    if [ -n "$api_key" ]; then
        echo ""
        echo "Setting up API key..."
        
        # Add to .bashrc for persistence
        echo "export OPENWEATHERMAP_API_KEY=\"$api_key\"" >> ~/.bashrc
        
        # Set for current session
        export OPENWEATHERMAP_API_KEY="$api_key"
        
        echo "✅ API key configured successfully!"
        echo "   - Added to ~/.bashrc for persistence"
        echo "   - Set for current session"
    else
        echo "❌ No API key provided. Will use mock data."
    fi
fi

echo ""
echo "🔧 Installing required dependencies..."

# Check if aiohttp is installed
if ! python3 -c "import aiohttp" 2>/dev/null; then
    echo "Installing aiohttp..."
    pip3 install aiohttp
else
    echo "✅ aiohttp already installed"
fi

# Check if fastapi is installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "Installing fastapi and uvicorn..."
    pip3 install fastapi uvicorn
else
    echo "✅ fastapi already installed"
fi

echo ""
echo "🚀 Starting Production Weather Server..."

# Stop existing weather server if running
pkill -f "test_weather_server.py" 2>/dev/null || true
pkill -f "src/servers/weather_server_prod.py" 2>/dev/null || true

# Start the production weather server
echo "Starting weather server on port 8000..."
python3 src/servers/weather_server_prod.py &

# Wait a moment for server to start
sleep 3

echo ""
echo "🧪 Testing Weather API..."

# Test the API
if curl -s http://localhost:8000/weather/status > /dev/null; then
    echo "✅ Weather server is running!"
    
    # Get API status
    status=$(curl -s http://localhost:8000/weather/status)
    echo "API Status: $status"
    
    # Test current weather
    echo ""
    echo "🌡️ Testing current weather data..."
    current_weather=$(curl -s http://localhost:8000/weather/current | head -c 200)
    echo "Current weather sample: $current_weather..."
    
else
    echo "❌ Weather server failed to start"
    exit 1
fi

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. The production weather server is now running on port 8000"
echo "2. Real weather data will be used if API key is configured"
echo "3. Mock data will be used as fallback if API is unavailable"
echo "4. Test the weather page: https://curator.abbanoa.aigensolutions.it/weather"
echo ""
echo "🔧 To check API status: curl http://localhost:8000/weather/status"
echo "🔧 To view API docs: http://localhost:8000/docs"
echo ""
echo "💡 The server will automatically use real data when API key is available"
echo "   and fall back to realistic mock data when needed."
