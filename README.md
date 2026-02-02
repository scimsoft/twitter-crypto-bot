# News-Based Crypto Trading Bot

A sophisticated cryptocurrency trading bot that uses sentiment analysis from diverse news feeds to make automated trading decisions.

## 🚀 Features

- **Sentiment Analysis**: Analyzes news feed sentiment to make trading decisions
- **Multi-Coin Support**: Currently configured for DOGE trading
- **Risk Management**: Built-in stop-loss and position sizing controls
- **Simulated Trading**: Paper trading mode for testing strategies
- **Real-time Monitoring**: 15-minute analysis cycles
- **Enhanced Logging**: Per-feed sentiment tracking and analysis
- **Automated Execution**: Cron job integration for continuous operation
- **Keyword Filtering**: Focuses on crypto-relevant articles only
- **Expanded Feed Coverage**: 44+ diverse news sources across categories
- **Content Cleaning**: Removes HTML tags and URLs for better analysis

## 🛠️ Architecture

### Core Components

1. **Sentiment Analysis Engine**
   - News feed analysis (RSS feeds from world news, US news, finance news, and crypto-specific sources)
   - Keyword-based filtering for crypto-relevant content
   - Enhanced logging per news source
   - TextBlob sentiment analysis
   - Content cleaning and preprocessing

2. **Trading Logic**
   - Buy threshold: 0.300 (positive sentiment)
   - Sell threshold: -0.200 (negative sentiment)
   - Position sizing: 20% of portfolio
   - Risk management controls

3. **Data Processing**
   - Real-time price monitoring
   - Sentiment scoring algorithms
   - Trade execution logic

## 📊 Feed Categories

### World News Feeds (6 feeds)
- BBC World News
- Al Jazeera
- Deutsche Welle
- New York Times World
- Financial Times World
- The Guardian World

### US News Feeds (6 feeds)
- New York Times US
- ABC News US
- USA Today Top Stories
- Fox News Latest
- NBC News Top Stories
- Washington Post Business

### Financial News Feeds (15 feeds)
- Reuters Business News
- Reuters Top News
- Reuters Markets News
- CNN Money International
- Financial Times General
- Wall Street Journal
- MarketWatch Top Stories
- CNBC Top Stories
- Investing.com News
- Bloomberg
- The Economist Economics
- Seeking Alpha Market Currents
- Business Insider
- CNN Money Top Stories
- Financial Post

### Crypto News Feeds (17 feeds)
- CoinTelegraph
- CryptoPotato
- Decrypt
- The Block
- Crypto.news
- CoinDesk
- Crypto Coins News (CCN)
- Bitcoin.com
- 99 Bitcoins
- NewsBTC
- Bitcoin Magazine
- Ethereum World News
- CoinCentral
- Live Bitcoin News
- BitsOnline
- CryptoSlate
- CryptoVest

## 📋 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
EXCHANGE_API_KEY=your_exchange_api_key
EXCHANGE_SECRET_KEY=your_exchange_secret_key
COIN_GECKO_API_KEY=your_coin_gecko_api_key
```

### Trading Parameters

- **Initial Capital**: $10,000 (default)
- **Analysis Frequency**: Every 15 minutes
- **Position Size**: 20% of portfolio per trade
- **Stop Loss**: 5% (configurable)
- **Take Profit**: 15% (configurable)

## 🚀 Running the Bot

### Manual Execution
```bash
python3 news_sentiment_trading_bot.py
```

### With the Run Script
```bash
bash run_news_bot.sh
```

### Cron Job
The bot is configured to run every 15 minutes via cron job:
```
*/15 * * * * cd /home/gerrit/.openclaw/workspace/twitter-crypto-bot && /usr/bin/env bash run_news_bot.sh >> /home/gerrit/.openclaw/workspace/twitter-crypto-bot/trading_bot_cron.log 2>&1
```

## 🎯 Keyword Filtering

The bot uses intelligent filtering to analyze sentiment only from articles containing crypto-related keywords:
- Core crypto terms: bitcoin, ethereum, dogecoin, cryptocurrency, crypto, blockchain
- Market terms: market, trading, finance, investment, volatility
- Economic terms: fed, inflation, monetary policy, regulation, adoption
- Technology terms: decentralized, nft, web3, wallet, exchange
- Slang/terms: hodl, fomo, fud, whale

## 📈 Expected Benefits

- **Higher Accuracy**: Sentiment scores reflect actual crypto market conditions
- **Better Responsiveness**: Faster reaction to crypto-specific market-moving news
- **Improved Performance**: Reduced processing of irrelevant articles
- **Better Signal-to-Noise Ratio**: Trading signals based on relevant content only
- **Diversified Information**: Multiple perspectives for comprehensive analysis
- **Enhanced Relevance**: Focus on content that directly impacts crypto markets

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip package manager
- Twitter API access
- Cryptocurrency exchange API access

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd twitter-crypto-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. Run the bot:
   ```bash
   python3 crypto_trading_bot.py
   ```

## ⚙️ Running with Cron

The bot is designed to run continuously using cron jobs:

```bash
# Add to crontab for 15-minute intervals
*/15 * * * * cd /path/to/twitter-crypto-bot && python3 crypto_trading_bot.py
```

## 📊 Enhanced Sentiment Logging

The bot now includes advanced logging that tracks sentiment scores per news feed:

- Individual feed sentiment tracking
- Historical pattern analysis
- Feed reliability metrics
- Consistency scoring

Run `python3 analyze_sentiment_patterns.py` to view feed sentiment patterns.

## 📈 Trading Strategy

### Algorithm

1. **Data Collection**: Gather tweets and news articles
2. **Sentiment Analysis**: Calculate sentiment scores
3. **Decision Making**: Compare against thresholds
4. **Execution**: Place trades (if thresholds met)
5. **Logging**: Record all activities

### Thresholds

- **BUY**: Sentiment ≥ 0.300
- **SELL**: Sentiment ≤ -0.200
- **HOLD**: Between -0.200 and 0.300

## 🛡️ Risk Management

- Position sizing limits
- Stop-loss mechanisms
- Take-profit targets
- Portfolio balance monitoring

## 🧪 Testing & Simulation

The bot includes a simulation mode that allows testing without real money:

- Paper trading functionality
- Historical data testing
- Strategy validation

## 📁 File Structure

```
twitter-crypto-bot/
├── crypto_trading_bot.py        # Main trading bot
├── news_sentiment_trading_bot.py # News sentiment analyzer
├── sentiment_logger.py          # Enhanced logging system
├── analyze_sentiment_patterns.py # Pattern analysis tool
├── run_twitter_bot.sh           # Execution script
├── setup_hourly_trading.sh      # Hourly trading setup
├── setup_reuters_bot.sh         # Reuters bot setup
├── trade_history.json           # Trade history log
├── requirements.txt             # Dependencies
├── .env.example                # Environment template
├── README.md                   # Documentation
└── LICENSE                     # License information
```

## 🔧 Customization

### Modifying Trading Parameters

Edit the configuration in `crypto_trading_bot.py` to adjust:

- Trading thresholds
- Position sizes
- Risk parameters
- Supported coins

### Adding News Sources

Update the news feed configuration to include additional sources for sentiment analysis.

## 🐞 Troubleshooting

### Common Issues

1. **API Rate Limits**: Implement rate limiting and retry logic
2. **Authentication Errors**: Verify API credentials in `.env`
3. **Sentiment Analysis Failures**: Check news feed accessibility
4. **Exchange Connection Issues**: Verify exchange API connectivity

### Logs

- `trade_history.json`: Complete trade history
- `sentiment_by_feed_detailed.log`: Per-feed sentiment logs
- `bot.log`: General operation logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational purposes only. Cryptocurrency trading involves substantial risk. Always test strategies thoroughly before using real funds.