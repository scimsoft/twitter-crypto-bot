#!/usr/bin/env python3
"""
Manual startup script for the crypto trading bot
"""

import os
import sys
import subprocess

def check_environment():
    """
    Check if the environment is properly set up
    """
    # Check if required files exist
    required_files = [
        '/home/gerrit/.openclaw/workspace/crypto_trading_bot.py',
        '/home/gerrit/.openclaw/workspace/reuters_sentiment_tracker.py',
        '/home/gerrit/.openclaw/workspace/twitter_sentiment_analyzer.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    # Check for required environment variables (will generate Bearer Token from API Key/Secret if needed)
    try:
        sys.path.insert(0, '/home/gerrit/.openclaw/workspace/twitter-crypto-bot')
        from twitter_config import get_bearer_token
        bearer_token = get_bearer_token()
        if not bearer_token:
            print("Error: Unable to get Twitter Bearer Token.")
            print("Please ensure either:")
            print("1. TWITTER_BEARER_TOKEN is set in .env, OR")
            print("2. TWITTER_API_KEY and TWITTER_API_SECRET are set in .env")
            return False
    except ImportError:
        if not os.getenv('TWITTER_BEARER_TOKEN'):
            print("TWITTER_BEARER_TOKEN environment variable not set")
            print("Please set your Twitter API credentials")
            return False
    
    return True

def main():
    """
    Main function to start the trading bot
    """
    print("Starting Crypto Trading Bot Manually")
    print("=" * 40)
    
    if not check_environment():
        print("\nEnvironment check failed. Please fix the issues above.")
        return
    
    # Path to the main bot script
    bot_script = "/home/gerrit/.openclaw/workspace/crypto_trading_bot.py"
    
    print(f"Starting trading bot from: {bot_script}")
    print("Press Ctrl+C to stop the bot")
    
    try:
        # Run the bot script
        result = subprocess.run([sys.executable, bot_script], check=True)
        
        if result.returncode == 0:
            print("Bot completed successfully")
        else:
            print(f"Bot exited with code: {result.returncode}")
    
    except subprocess.CalledProcessError as e:
        print(f"Error running bot: {e}")
    except KeyboardInterrupt:
        print("\nBot interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()