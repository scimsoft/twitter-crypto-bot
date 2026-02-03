#!/bin/bash
# Script to run the enhanced news-based crypto trading bot

cd /home/gerrit/.openclaw/workspace/twitter-crypto-bot

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Run the news-based trading bot
python3 news_sentiment_trading_bot.py