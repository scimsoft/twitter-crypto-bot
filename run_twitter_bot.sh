#!/bin/bash

# Change to the twitter-crypto-bot directory
cd /home/gerrit/.openclaw/workspace/twitter-crypto-bot

# Source the environment variables
export $(grep -v '^#' /home/gerrit/.openclaw/workspace/twitter-crypto-bot/.env | xargs)

# Run the NEW Python script with 15-minute intervals using world news feeds
/usr/bin/env python3 /home/gerrit/.openclaw/workspace/twitter-crypto-bot/news_sentiment_trading_bot.py