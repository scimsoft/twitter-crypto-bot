#!/bin/bash

# Change to the twitter-crypto-bot directory
cd /home/gerrit/.openclaw/workspace/twitter-crypto-bot

# Source the environment variables
export $(grep -v '^#' /home/gerrit/.openclaw/workspace/twitter-crypto-bot/.env | xargs)

# Run the NEW Python script with 15-minute intervals using world news feeds
# This will run a single cycle each time the cron job triggers (every 15 minutes)
/usr/bin/env python3 -c "
import sys
sys.path.append('/home/gerrit/.openclaw/workspace/twitter-crypto-bot')
from news_sentiment_trading_bot import NewsBasedTradingBot
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize and run a single cycle
bot = NewsBasedTradingBot(initial_capital=10000, coin_symbol='DOGE')
bot.run_single_cycle()
"