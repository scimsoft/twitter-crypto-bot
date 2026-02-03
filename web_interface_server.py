#!/usr/bin/env python3
"""
Web interface server for the News-Based Crypto Trading Bot
Serves real-time data via REST API and HTML interface
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sys
import threading
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global bot instance (will be set when bot is running)
bot_instance = None
bot_data_file = "bot_data.json"  # File to store bot data

# Try to import and set bot instance if running
try:
    from news_sentiment_trading_bot import NewsBasedTradingBot
    # Try to get bot instance from main module if it exists
    import news_sentiment_trading_bot as bot_module
    if hasattr(bot_module, 'bot_instance'):
        bot_instance = bot_module.bot_instance
except ImportError:
    pass

@app.route('/')
def index():
    """Serve the HTML interface"""
    return send_from_directory('.', 'interface.html')

@app.route('/api/data', methods=['GET'])
def get_bot_data():
    """Get current bot data"""
    try:
        # Try to get data from bot instance if available
        if bot_instance:
            data = bot_instance.get_interface_data()
            
            # get_interface_data() now includes total_sentiment, avg_sentiment, and article counts
            # Just add timestamp and bot status
            data["last_update"] = datetime.now().isoformat()
            data["bot_status"] = "running"
            
            return jsonify(data)
        
        # Fallback: try to read from file if bot instance not available
        if os.path.exists(bot_data_file):
            try:
                with open(bot_data_file, 'r') as f:
                    data = json.load(f)
                    # Check if data is recent (within last 60 seconds for sentiment updates)
                    if 'last_update' in data:
                        try:
                            last_update = datetime.fromisoformat(data['last_update'])
                            time_diff = (datetime.now() - last_update).total_seconds()
                            if time_diff < 60:  # Data is fresh (increased to 60 seconds)
                                # Ensure sentiment values are numbers
                                if 'total_sentiment' in data:
                                    data['total_sentiment'] = float(data['total_sentiment']) if data['total_sentiment'] is not None else 0
                                if 'avg_sentiment' in data:
                                    data['avg_sentiment'] = float(data['avg_sentiment']) if data['avg_sentiment'] is not None else 0
                                return jsonify(data)
                            else:
                                # Data is stale, bot might have stopped
                                data['bot_status'] = 'stale'
                                data['message'] = f'Bot data is {int(time_diff)} seconds old. Bot may have stopped.'
                                return jsonify(data)
                        except Exception as e:
                            logger.error(f"Error parsing last_update timestamp: {e}")
                    # Ensure sentiment values are numbers even if no timestamp
                    if 'total_sentiment' in data:
                        data['total_sentiment'] = float(data['total_sentiment']) if data['total_sentiment'] is not None else 0
                    if 'avg_sentiment' in data:
                        data['avg_sentiment'] = float(data['avg_sentiment']) if data['avg_sentiment'] is not None else 0
                    return jsonify(data)
            except Exception as e:
                logger.error(f"Error reading bot_data.json: {e}")
        
        # Return empty data if nothing available (but don't mark as error - just no data yet)
        return jsonify({
            "bot_status": "not_running",
            "message": "Trading bot is not running. Start the bot to see live data.",
            "current_price": 0,
            "portfolio_value": 0,
            "cash_balance": 0,
            "holdings": 0,
            "holdings_value": 0,
            "initial_capital": 0,
            "profit_loss": 0,
            "profit_loss_pct": 0,
            "coin_symbol": "DOGE",
            "sentiment_score": 0,
            "total_sentiment": 0,
            "avg_sentiment": 0,
            "position_size": 0.2,
            "recent_trades": [],
            "total_trades": 0,
            "buy_threshold": 5.0,
            "sell_threshold": -3.0,
            "positive_articles": 0,
            "negative_articles": 0,
            "neutral_articles": 0,
            "article_count": 0,
            "last_update": datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "bot_available": bot_instance is not None,
        "timestamp": datetime.now().isoformat()
    })

def save_bot_data_periodically():
    """Save bot data to file periodically (for fallback)"""
    global bot_instance
    while True:
        try:
            if bot_instance:
                data = bot_instance.get_interface_data()
                
                # get_interface_data() already includes all needed fields
                # Just add timestamp and bot status
                data["last_update"] = datetime.now().isoformat()
                data["bot_status"] = "running"
                
                with open(bot_data_file, 'w') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving bot data: {e}")
        
        time.sleep(5)  # Save every 5 seconds

def start_data_saver():
    """Start the background thread to save bot data"""
    thread = threading.Thread(target=save_bot_data_periodically, daemon=True)
    thread.start()
    return thread

if __name__ == '__main__':
    # Start background thread to save bot data
    start_data_saver()
    
    print("Starting web interface server...")
    print("Open http://localhost:5000 in your browser")
    print("Press Ctrl+C to stop")
    
    # Run Flask server
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
