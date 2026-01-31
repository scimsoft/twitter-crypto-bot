#!/bin/bash

# Setup script for hourly crypto trading bot based on Reuters sentiment

echo "Setting up hourly crypto trading bot..."
echo "======================================"

# Check if required files exist
if [ ! -f "/home/gerrit/.openclaw/workspace/crypto_trading_bot.py" ]; then
    echo "Error: crypto_trading_bot.py not found in workspace"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Add the cron job using crontab command
echo "Adding hourly cron job for the trading bot..."

# Create a temporary crontab file
TEMP_CRON="/tmp/temp_cron_$$.txt"

# Get current crontab
crontab -l > "$TEMP_CRON" 2>/dev/null || echo "# Empty crontab" > "$TEMP_CRON"

# Check if the job already exists
if grep -q "crypto_trading_bot.py" "$TEMP_CRON"; then
    echo "Cron job already exists. Updating..."
    sed -i '/crypto_trading_bot.py/d' "$TEMP_CRON"
fi

# Add the new cron job (runs every hour at minute 0)
echo "0 * * * * /usr/bin/python3 /home/gerrit/.openclaw/workspace/crypto_trading_bot.py >> /home/gerrit/.openclaw/workspace/trading_bot_cron.log 2>&1" >> "$TEMP_CRON"

# Install the new crontab
crontab "$TEMP_CRON"

# Clean up
rm "$TEMP_CRON"

echo "Cron job added successfully!"
echo ""
echo "The trading bot will run every hour at minute 0."
echo ""
echo "To view your cron jobs: crontab -l"
echo "To remove the job: crontab -r"
echo ""
echo "Log file location: /home/gerrit/.openclaw/workspace/trading_bot_cron.log"
echo ""
echo "Important: Make sure to set your Twitter API credentials before the bot runs:"
echo "export TWITTER_BEARER_TOKEN='your_bearer_token'"