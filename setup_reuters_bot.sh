#!/bin/bash

# Setup script for Reuters Twitter Sentiment Trading Bot

echo "Setting up Reuters Twitter Sentiment Trading Bot..."
echo "=================================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip for Python 3..."
    python3 -m ensurepip --upgrade
    if [ $? -ne 0 ]; then
        echo "Error: Could not install pip. Installing via apt..."
        sudo apt update && sudo apt install -y python3-pip
        if [ $? -ne 0 ]; then
            echo "Error: Could not install pip. Please install it manually."
            exit 1
        fi
    fi
fi

echo "Installing required Python packages..."
pip3 install --user -r requirements.txt

if [ $? -eq 0 ]; then
    echo "Packages installed successfully!"
else
    echo "Error installing packages. Trying alternative method..."
    python3 -m pip install --user tweepy vaderSentiment pandas numpy requests
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Get your Twitter API credentials from https://developer.twitter.com/"
echo "2. Set your environment variables:"
echo "   export TWITTER_BEARER_TOKEN='your_bearer_token'"
echo "   export TWITTER_API_KEY='your_api_key'"
echo "   export TWITTER_API_SECRET='your_api_secret'"
echo "   export TWITTER_ACCESS_TOKEN='your_access_token'"
echo "   export TWITTER_ACCESS_TOKEN_SECRET='your_access_token_secret'"
echo ""
echo "3. Run the analysis with:"
echo "   python3 run_reuters_analysis.py"
echo ""