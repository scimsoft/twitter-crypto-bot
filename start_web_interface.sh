#!/bin/bash

# Script to start the trading bot with web interface

echo "Starting News-Based Crypto Trading Bot with Web Interface..."
echo "============================================================"

# Kill any existing bot and web server processes
echo "Cleaning up any existing processes..."
pkill -f "python3 web_interface_server.py" 2>/dev/null
pkill -f "python3 news_sentiment_trading_bot.py" 2>/dev/null
# Wait for processes to terminate
sleep 1

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Flask is not installed. Attempting to install dependencies..."
    echo "If installation fails due to permissions, please run manually:"
    echo "  pip3 install --user flask flask-cors"
    echo "  OR"
    echo "  sudo pip3 install flask flask-cors"
    echo ""
    
    # Try user installation first
    pip3 install --user flask flask-cors 2>/dev/null || {
        echo "User installation failed. Trying system-wide installation..."
        pip3 install flask flask-cors 2>/dev/null || {
            echo "ERROR: Could not install Flask. Please install manually:"
            echo "  pip3 install --user flask flask-cors"
            exit 1
        }
    }
fi

# Start the web server in background
echo "Starting web interface server on http://localhost:5000"
python3 web_interface_server.py &
WEB_SERVER_PID=$!

# Wait a moment for server to start
sleep 2

# Start the trading bot (this will block)
echo "Starting trading bot..."
echo "Web interface available at: http://localhost:5000"
echo "Press Ctrl+C to stop both bot and web server"
echo ""

python3 news_sentiment_trading_bot.py

# Cleanup: kill web server when bot stops
echo ""
echo "Stopping web server..."
kill $WEB_SERVER_PID 2>/dev/null

echo "Both bot and web server stopped."
