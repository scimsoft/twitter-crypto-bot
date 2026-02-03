# News-Based Crypto Trading Bot

An automated cryptocurrency trading bot that uses sentiment analysis from world news feeds to make trading decisions. The bot analyzes news articles, calculates sentiment scores, and executes trades based on configurable thresholds.

## Features

- 📰 **News-Based Sentiment Analysis**: Analyzes articles from multiple RSS feeds
- 🤖 **Automated Trading**: Executes BUY/SELL orders based on sentiment thresholds
- 💾 **State Persistence**: Saves holdings, capital, and trade history - resumes after restart
- 🌐 **Web Interface**: Real-time dashboard with auto-updating interface (every 5 seconds)
- 📊 **Portfolio Tracking**: Monitors portfolio value, profit/loss, and trade history
- ⚙️ **Strategy Optimization**: Automatically adjusts thresholds based on performance

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Install Dependencies

```bash
pip3 install --user -r requirements.txt
```

If you encounter permission errors, try:
```bash
sudo pip3 install -r requirements.txt
```

### Install Web Interface Dependencies

The web interface requires Flask and Flask-CORS:

```bash
pip3 install --user flask flask-cors
```

Or with sudo:
```bash
sudo pip3 install flask flask-cors
```

## Quick Start

### Option 1: Run with Web Interface (Recommended)

```bash
./start_web_interface.sh
```

**Note:** The startup script automatically kills any existing bot/web server processes before starting new ones to prevent conflicts.

Then open your browser to: **http://localhost:5000**

**Important:** If you don't see recent trades or updated data, try a hard refresh (`Ctrl+Shift+R` or `Cmd+Shift+R`) to clear browser cache.

### Option 2: Run in Background with nohup

To run the bot in the background and keep it running after closing the terminal:

```bash
nohup ./start_web_interface.sh > bot.log 2>&1 &
```

This will:
- Start both the trading bot and web interface
- Run in the background
- Save output to `bot.log`
- Continue running after you close the terminal

To stop the bot:
```bash
# Find the process
ps aux | grep start_web_interface

# Kill the process (replace PID with actual process ID)
kill <PID>
```

Or kill all Python processes (be careful):
```bash
pkill -f news_sentiment_trading_bot
pkill -f web_interface_server
```

### Option 3: Run Separately

**Terminal 1 - Start the web server:**
```bash
python3 web_interface_server.py
```

**Terminal 2 - Start the trading bot:**
```bash
python3 news_sentiment_trading_bot.py
```

## Configuration

### Trading Parameters

Edit `news_sentiment_trading_bot.py` to adjust:

- `buy_threshold`: Total sentiment threshold to trigger BUY (default: 5.0)
- `sell_threshold`: Total sentiment threshold to trigger SELL (default: -3.0)
- `max_position_size`: Maximum percentage of portfolio per trade (default: 20%)
- `initial_capital`: Starting capital in USD (default: $10,000)
- `coin_symbol`: Cryptocurrency to trade (default: DOGE)

### News Feeds

The bot uses RSS feeds from various news sources. Failed feeds are automatically removed after 2 consecutive errors. Removed feeds are saved to `removed_feeds.json`.

## Web Interface

The web interface provides real-time monitoring of:

- 💰 Portfolio value and cash balance
- 🪙 Current holdings
- 📊 Profit/Loss tracking
- 🧠 Sentiment scores (total and average)
- 📰 Articles analyzed (positive/negative/neutral breakdown)
- 📈 Current price
- 📝 Recent trades
- ⚙️ Trading parameters and thresholds

### Accessing the Web Interface

1. Start the bot (see Quick Start above)
2. Open your browser to: **http://localhost:5000**
3. The interface auto-updates every 5 seconds

### Web Interface Features

- **Auto-updating**: Refreshes every 5 seconds automatically
- **Real-time data**: Shows live trading bot data (trades, holdings, cash balance)
- **Status indicators**: Shows if bot is running, waiting, or has errors
- **Trade history**: Displays recent trades with timestamps, amounts, and sentiment scores
- **Article breakdown**: Shows sentiment analysis results (positive/negative/neutral counts)
- **Portfolio tracking**: Real-time portfolio value, profit/loss, and holdings

**Note:** The interface saves bot data immediately after each trading cycle, ensuring trades and holdings are always up-to-date.

## State Persistence

The bot automatically saves its state to `bot_state.json`:

- **Current capital**: Available cash
- **Holdings**: Amount of cryptocurrency owned
- **Trade history**: All previous trades
- **Price history**: Recent price data
- **Sentiment history**: Recent sentiment scores
- **Trading parameters**: Buy/sell thresholds, position size

**State is saved:**
- After every trade (BUY or SELL) - immediately saves to both `bot_state.json` and `bot_data.json`
- After strategy optimization
- Every 5 seconds (background thread)
- After each trading cycle completes (with latest sentiment and trade data)

**On restart**, the bot automatically loads previous state from `bot_state.json` and continues from where it left off.

**Data Files:**
- `bot_state.json`: Complete bot state (holdings, capital, full trade history, sentiment history)
- `bot_data.json`: Current state for web interface (updated every 5 seconds and after each cycle)

## How It Works

1. **News Analysis**: Bot fetches articles from RSS feeds (one article per feed)
2. **Sentiment Calculation**: Analyzes each article using TextBlob sentiment analysis
3. **Total Sentiment**: Sums all sentiment scores (range typically -63 to +63 for 63 articles)
4. **Trading Decision**: 
   - BUY if total_sentiment ≥ buy_threshold (default: 5.0)
   - SELL if total_sentiment ≤ sell_threshold (default: -3.0)
   - HOLD otherwise
5. **Trade Execution**: Executes trades based on sentiment strength and position sizing
6. **Strategy Optimization**: Adjusts thresholds based on win rate

## File Structure

- `news_sentiment_trading_bot.py` - Main trading bot
- `web_interface_server.py` - Flask web server for dashboard
- `interface.html` - Web interface dashboard
- `start_web_interface.sh` - Startup script
- `bot_state.json` - Saved bot state (holdings, capital, trades)
- `bot_data.json` - Current bot data for web interface
- `removed_feeds.json` - List of failed RSS feeds

## Troubleshooting

### Flask Not Installed

If you see `ModuleNotFoundError: No module named 'flask'`:

```bash
pip3 install --user flask flask-cors
```

### Port Already in Use

If port 5000 is already in use, edit `web_interface_server.py`:

```python
app.run(host='0.0.0.0', port=5000, ...)  # Change 5000 to another port
```

### Bot Data Not Showing in Web Interface

1. Make sure the trading bot is running
2. Check that `bot_data.json` exists and is being updated
3. Check browser console (F12) for errors
4. Verify the web server is running on port 5000
5. **If trades/holdings not showing**: Try a hard refresh (`Ctrl+Shift+R` or `Cmd+Shift+R`) - the browser may be caching old data
6. Check the API directly: `curl http://localhost:5000/api/data` to verify data is being served correctly

### Bot Not Resuming State

- Check that `bot_state.json` exists
- Verify file permissions
- Check logs for loading errors

### Feed Errors

Failed RSS feeds are automatically removed after 2 consecutive errors. To manually remove feeds, edit `removed_feeds.json` or delete it to reset.

## Logs

- Bot logs: Check terminal output or `bot.log` if using nohup
- Web server logs: Check terminal output
- Trading activity: Displayed in web interface and terminal

## Stopping the Bot

### If running in foreground:
Press `Ctrl+C`

### If running with nohup:
```bash
# Find process
ps aux | grep news_sentiment_trading_bot

# Kill process
kill <PID>
```

### If using startup script:
The script handles cleanup automatically when stopped with Ctrl+C

### Kill All Processes:
The startup script automatically kills existing processes, but you can manually kill them:
```bash
pkill -f news_sentiment_trading_bot.py
pkill -f web_interface_server.py
```

## Notes

- The bot uses **total sentiment** (sum of all sentiment scores) for threshold comparison, not average sentiment
- Sentiment thresholds are adjusted based on market volatility
- Failed RSS feeds are automatically removed and persisted after 2 consecutive errors
- All state is saved automatically - you can restart anytime without losing progress
- Trade data, holdings, and cash balance are saved immediately after each trade
- The web interface reads from `bot_data.json` which is updated every 5 seconds and after each trading cycle
- If the web interface shows stale data, do a hard refresh (`Ctrl+Shift+R`) to clear browser cache

## Support

For issues or questions, check the logs and ensure all dependencies are installed correctly.
