# Twitter Crypto Trading Bot

An automated crypto trading bot that analyzes Twitter sentiment to make trading decisions.

## Overview

This bot monitors Twitter accounts of crypto influencers and analyzes the sentiment of their tweets to make informed trading decisions. It runs hourly and tracks sentiment trends across major crypto personalities.

## Features

- Hourly sentiment analysis of crypto influencer tweets
- Automated trading signal generation based on sentiment
- Integration with Twitter API for real-time data
- Configurable trading parameters
- Detailed logging and analytics

## Prerequisites

- Python 3.7+
- Twitter Developer Account
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd twitter-crypto-bot
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Twitter API credentials:
   ```bash
   ./set_twitter_credentials.sh
   ```

## Configuration

Create a `.env` file with your Twitter API credentials:

```env
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

## Usage

Run the bot manually:
```bash
python crypto_trading_bot.py
```

Or set up a cron job to run it hourly:
```bash
0 * * * * /path/to/run_twitter_bot.sh
```

## Files

- `crypto_trading_bot.py` - Main trading bot logic
- `twitter_sentiment_analyzer.py` - Sentiment analysis functions
- `simple_twitter_collector.py` - Twitter data collection
- `reuters_sentiment_tracker.py` - Reuters sentiment tracking
- `set_twitter_credentials.sh` - Script to set up credentials
- `run_twitter_bot.sh` - Wrapper script for cron jobs

## Security

⚠️ **Important**: Never commit your `.env` file or any files containing API keys to version control. The `.gitignore` file is configured to exclude these sensitive files.

## Contributing

Feel free to fork this repository and submit pull requests for improvements.

## License

[Specify your license here]