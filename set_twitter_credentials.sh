#!/bin/bash

# Script to set Twitter API credentials

echo "Setting up Twitter API credentials for the trading bot..."
echo "========================================================"

# Prompt for the credentials
read -p "Enter your Twitter Bearer Token: " bearer_token
read -p "Enter your Twitter API Key: " api_key
read -p "Enter your Twitter API Secret: " api_secret
read -p "Enter your Twitter Access Token: " access_token
read -p "Enter your Twitter Access Token Secret: " access_token_secret

# Set the environment variables
export TWITTER_BEARER_TOKEN="$bearer_token"
export TWITTER_API_KEY="$api_key"
export TWITTER_API_SECRET="$api_secret"
export TWITTER_ACCESS_TOKEN="$access_token"
export TWITTER_ACCESS_TOKEN_SECRET="$access_token_secret"

# Update the .env file
if [ -f "/home/gerrit/.openclaw/workspace/.env" ]; then
    # Update existing values
    sed -i "s/TWITTER_BEARER_TOKEN=.*/TWITTER_BEARER_TOKEN=$bearer_token/" /home/gerrit/.openclaw/workspace/.env
    sed -i "s/TWITTER_API_KEY=.*/TWITTER_API_KEY=$api_key/" /home/gerrit/.openclaw/workspace/.env
    sed -i "s/TWITTER_API_SECRET=.*/TWITTER_API_SECRET=$api_secret/" /home/gerrit/.openclaw/workspace/.env
    sed -i "s/TWITTER_ACCESS_TOKEN=.*/TWITTER_ACCESS_TOKEN=$access_token/" /home/gerrit/.openclaw/workspace/.env
    sed -i "s/TWITTER_ACCESS_TOKEN_SECRET=.*/TWITTER_ACCESS_TOKEN_SECRET=$access_token_secret/" /home/gerrit/.openclaw/workspace/.env
    echo "Updated credentials in /home/gerrit/.openclaw/workspace/.env"
else
    # Create new .env file
    cat > /home/gerrit/.openclaw/workspace/.env << EOL
# Twitter API Credentials
TWITTER_BEARER_TOKEN=$bearer_token
TWITTER_API_KEY=$api_key
TWITTER_API_SECRET=$api_secret
TWITTER_ACCESS_TOKEN=$access_token
TWITTER_ACCESS_TOKEN_SECRET=$access_token_secret

# Trading Bot Configuration
TWEETS_PER_ACCOUNT=10
OUTPUT_FILE=twitter_data.json
EOL
    echo "Created /home/gerrit/.openclaw/workspace/.env with credentials"
fi

# Also add to the user's bashrc for persistence in future sessions
if ! grep -q "TWITTER_BEARER_TOKEN" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Twitter API Credentials for Trading Bot" >> ~/.bashrc
    echo "export TWITTER_BEARER_TOKEN='$bearer_token'" >> ~/.bashrc
    echo "export TWITTER_API_KEY='$api_key'" >> ~/.bashrc
    echo "export TWITTER_API_SECRET='$api_secret'" >> ~/.bashrc
    echo "export TWITTER_ACCESS_TOKEN='$access_token'" >> ~/.bashrc
    echo "export TWITTER_ACCESS_TOKEN_SECRET='$access_token_secret'" >> ~/.bashrc
    echo "Added credentials to ~/.bashrc for persistence"
else
    echo "Updating credentials in ~/.bashrc"
    sed -i "s/export TWITTER_BEARER_TOKEN=.*/export TWITTER_BEARER_TOKEN='$bearer_token'/" ~/.bashrc
    sed -i "s/export TWITTER_API_KEY=.*/export TWITTER_API_KEY='$api_key'/" ~/.bashrc
    sed -i "s/export TWITTER_API_SECRET=.*/export TWITTER_API_SECRET='$api_secret'/" ~/.bashrc
    sed -i "s/export TWITTER_ACCESS_TOKEN=.*/export TWITTER_ACCESS_TOKEN='$access_token'/" ~/.bashrc
    sed -i "s/export TWITTER_ACCESS_TOKEN_SECRET=.*/export TWITTER_ACCESS_TOKEN_SECRET='$access_token_secret'/" ~/.bashrc
fi

echo ""
echo "Twitter credentials have been set for this session."
echo "To verify they're set, run: env | grep TWITTER"
echo ""
echo "You can now test the trading bot with:"
echo "python3 /home/gerrit/.openclaw/workspace/crypto_trading_bot.py"