# News-Based Crypto Bot Setup Guide

Complete guide to set up and run the News-Based Crypto Trading Bot.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git
- Twitter Developer Account (with API access)
- Cryptocurrency Exchange Account (with API access)

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/twitter-crypto-bot.git
cd twitter-crypto-bot
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If requirements.txt doesn't exist, install the required packages:

```bash
pip install tweepy requests textblob python-dotenv pandas numpy
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file with your API credentials:

```env
# Twitter API Credentials
TWITTER_BEARER_TOKEN=your_bearer_token_here

# Exchange API Credentials (for real trading)
EXCHANGE_API_KEY=your_exchange_api_key
EXCHANGE_SECRET_KEY=your_exchange_secret_key

# Optional: CoinGecko API for price data
COIN_GECKO_API_KEY=your_coin_gecko_api_key

# Bot Configuration
BOT_MODE=simulation  # Change to 'live' for real trading
INITIAL_CAPITAL=10000
```

### 5. Verify Configuration

Run the configuration test:

```bash
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('TWITTER_BEARER_TOKEN exists:', bool(os.getenv('TWITTER_BEARER_TOKEN')))
print('Bot mode:', os.getenv('BOT_MODE', 'simulation'))
print('Initial capital:', os.getenv('INITIAL_CAPITAL', '10000'))
"
```

### 6. Test Sentiment Analysis

Test the enhanced sentiment logging system:

```bash
python3 -c "
from sentiment_logger import SentimentLogger
logger = SentimentLogger()
print('SentimentLogger initialized successfully')
print('Available methods:', [method for method in dir(logger) if not method.startswith('_')])
"
```

### 7. Run Initial Test

```bash
python3 crypto_trading_bot.py --test
```

## Configuration Options

### Trading Parameters

Edit the trading parameters in the main bot file:

```python
# Trading thresholds
BUY_THRESHOLD = 0.3  # Buy when sentiment >= 0.3
SELL_THRESHOLD = -0.2  # Sell when sentiment <= -0.2
POSITION_SIZE_PERCENT = 20  # Use 20% of portfolio per trade
STOP_LOSS_PERCENT = 5  # Stop loss at 5%
TAKE_PROFIT_PERCENT = 10  # Take profit at 10%
```

### News Sources

Configure news sources in the sentiment analysis section:

```python
NEWS_SOURCES = {
    'Reuters': 'https://www.reuters.com/search/news?blob=cryptocurrency',
    'BBC': 'https://www.bbc.com/search?q=cryptocurrency',
    'CNN': 'https://edition.cnn.com/search?q=cryptocurrency',
    # Add more sources as needed
}
```

## Running the Bot

### Single Run

```bash
python3 crypto_trading_bot.py
```

### Continuous Operation with Cron

Add to your crontab for 15-minute intervals:

```bash
crontab -e
```

Add this line:
```
*/15 * * * * cd /path/to/twitter-crypto-bot && source venv/bin/activate && python3 crypto_trading_bot.py >> /path/to/bot.log 2>&1
```

### Using the Run Script

Execute using the provided script:

```bash
chmod +x run_twitter_bot.sh
./run_twitter_bot.sh
```

## Enhanced Sentiment Analysis

### View Feed Patterns

Analyze sentiment patterns across different news sources:

```bash
python3 analyze_sentiment_patterns.py
```

This will show:
- Mean sentiment per feed
- Standard deviation
- Consistency scores
- Historical trends

### Logging Configuration

The bot logs sentiment scores per feed in:
- `sentiment_by_feed_log.json` - Structured JSON data
- `sentiment_by_feed_detailed.log` - Detailed text logs

## Monitoring and Maintenance

### Check Bot Status

```bash
# Check if bot is running
ps aux | grep crypto_trading_bot

# Check recent logs
tail -f bot.log
```

### View Trade History

```bash
# View recent trades
cat trade_history.json | python -m json.tool
```

### Performance Metrics

Monitor these key metrics:
- Portfolio value over time
- Number of executed trades
- Win/loss ratio
- Average return per trade

## Troubleshooting

### Common Issues

1. **Twitter API Authentication Error**
   - Verify TWITTER_BEARER_TOKEN is correct
   - Check Twitter Developer account status
   - Ensure proper API access level

2. **Rate Limiting**
   - Implement exponential backoff
   - Reduce analysis frequency
   - Use caching mechanisms

3. **News Feed Access Issues**
   - Verify RSS feed URLs
   - Check for rate limiting by news sites
   - Implement proper headers for requests

4. **Exchange Connection Problems**
   - Verify API keys and permissions
   - Check network connectivity
   - Ensure proper IP whitelisting

### Debug Mode

Run in debug mode for detailed output:

```bash
python3 crypto_trading_bot.py --debug
```

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for all sensitive data
3. **Implement proper error handling** to avoid exposing credentials
4. **Regularly rotate API keys**
5. **Monitor API usage** to stay within limits

## Updating the Bot

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart the bot
# If using systemd: sudo systemctl restart openclaw-twitter-bot
# If using cron: The next scheduled run will use new code
```

## Backup and Recovery

### Backup Configuration

```bash
# Backup configuration files
tar -czf backup-$(date +%Y%m%d).tar.gz .env *.json *.log
```

### Recovery Process

1. Restore configuration files
2. Verify credentials
3. Start the bot
4. Monitor initial operations

## Performance Optimization

### Resource Usage

Monitor resource usage:
```bash
# Monitor CPU and memory
top -p $(pgrep -f crypto_trading_bot)
```

### Log Rotation

Set up log rotation to prevent disk space issues:
```bash
# Add to /etc/logrotate.d/twitter-crypto-bot
/path/to/bot/*.log {
    weekly
    rotate 10
    compress
    delaycompress
    missingok
    notifempty
}
```

This completes the setup guide for the Twitter Crypto Trading Bot. For additional support, refer to the main README or contact the development team.