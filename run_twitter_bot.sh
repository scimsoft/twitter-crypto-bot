#!/bin/bash

# Change to the twitter-crypto-bot directory
cd /home/gerrit/.openclaw/workspace/twitter-crypto-bot

# Source the environment variables
export $(grep -v '^#' /home/gerrit/.openclaw/workspace/twitter-crypto-bot/.env | xargs)

# Run the Python script
/usr/bin/env python3 /home/gerrit/.openclaw/workspace/twitter-crypto-bot/crypto_trading_bot.py