# Twitter Crypto Bot - API Documentation

Documentation for the Twitter Crypto Trading Bot's internal APIs and interfaces.

## Overview

The Twitter Crypto Trading Bot exposes several internal interfaces for:
- Sentiment analysis
- Trading operations
- Logging and monitoring
- Configuration management

## Core APIs

### Sentiment Analysis API

#### `calculate_sentiment(tweets, news_articles)`
Calculates composite sentiment from Twitter and news data.

**Parameters:**
- `tweets` (list): List of tweet objects or text
- `news_articles` (list): List of news article objects or text

**Returns:**
- `float`: Sentiment score between -1 (negative) and 1 (positive)

**Example:**
```python
sentiment = calculate_sentiment(['Bitcoin is going up!', 'Great news about crypto'], ['Market analysis...', 'Price prediction...'])
# Returns: 0.65
```

#### `analyze_feed_sentiment(feed_source)`
Analyzes sentiment for a specific news feed.

**Parameters:**
- `feed_source` (str): URL or identifier of the news feed

**Returns:**
- `dict`: Contains sentiment score and metadata

**Example:**
```python
feed_sentiment = analyze_feed_sentiment('Reuters')
# Returns: {'sentiment': 0.25, 'articles_count': 10, 'timestamp': '2023-01-01T12:00:00Z'}
```

### Trading API

#### `make_trading_decision(sentiment_score, current_price, portfolio_state)`
Makes trading decisions based on sentiment and portfolio data.

**Parameters:**
- `sentiment_score` (float): Current sentiment score
- `current_price` (float): Current cryptocurrency price
- `portfolio_state` (dict): Current portfolio information

**Returns:**
- `tuple`: (decision_type, position_size)

**Example:**
```python
decision, size = make_trading_decision(0.4, 0.08, {'cash': 10000, 'assets': 0})
# Returns: ('BUY', 2000)  # Buy $2000 worth if sentiment > BUY_THRESHOLD
```

#### `execute_order(order_details)`
Executes a trading order.

**Parameters:**
- `order_details` (dict): Details of the order to execute

**Returns:**
- `dict`: Execution confirmation with status

### Logging API

#### `log_sentiment_per_feed(feed_sources, overall_sentiment, timestamp=None)`
Logs sentiment scores for each news feed source.

**Parameters:**
- `feed_sources` (dict): Mapping of feed names to sentiment scores
- `overall_sentiment` (float): Composite sentiment score
- `timestamp` (datetime, optional): Timestamp for the log entry

**Example:**
```python
feed_sentiments = {
    'Reuters': 0.25,
    'BBC': -0.10,
    'CNN': 0.05
}
log_sentiment_per_feed(feed_sentiments, 0.067)
```

#### `get_historical_analysis()`
Retrieves historical sentiment data.

**Returns:**
- `DataFrame`: Historical sentiment data with timestamps and scores

#### `analyze_feed_patterns()`
Analyzes patterns in feed sentiment scores.

**Returns:**
- `dict`: Statistics for each feed source

### Configuration API

#### `load_config(config_file)`
Loads configuration from a file.

**Parameters:**
- `config_file` (str): Path to configuration file

**Returns:**
- `dict`: Configuration settings

#### `validate_config(config)`
Validates configuration settings.

**Parameters:**
- `config` (dict): Configuration dictionary

**Returns:**
- `bool`: True if valid, False otherwise

## Internal Endpoints

### Data Collection Endpoints

#### `fetch_tweets(accounts, count=100)`
Fetches tweets from specified accounts.

**Parameters:**
- `accounts` (list): List of Twitter account handles
- `count` (int): Number of tweets to fetch

**Returns:**
- `list`: List of tweet objects

#### `fetch_news_feeds(feeds)`
Fetches news from specified RSS feeds.

**Parameters:**
- `feeds` (list): List of RSS feed URLs

**Returns:**
- `list`: List of news articles

### Price Data Endpoints

#### `get_current_price(coin_symbol)`
Gets current price for a cryptocurrency.

**Parameters:**
- `coin_symbol` (str): Cryptocurrency symbol (e.g., 'DOGE')

**Returns:**
- `float`: Current price

## Error Handling

The API follows standard error handling patterns:

- Exceptions are raised for invalid inputs
- Network errors are caught and retried with exponential backoff
- API rate limits are respected
- Failed operations are logged for debugging

### Common Error Types

- `InvalidConfigurationError`: Raised when configuration is invalid
- `APIConnectionError`: Raised when API connection fails
- `DataValidationError`: Raised when data validation fails
- `TradingError`: Raised when trading operations fail

## Utilities

### Helper Functions

#### `normalize_sentiment(score)`
Normalizes sentiment score to standard range.

#### `calculate_position_size(portfolio_value, risk_percent)`
Calculates position size based on portfolio value and risk tolerance.

#### `format_trade_log(trade_details)`
Formats trade details for logging.

## Testing Interface

### Mock APIs for Testing

#### `mock_sentiment_api(sentiment_value)`
Creates a mock sentiment API that always returns the specified value.

#### `mock_exchange_api()`
Creates a mock exchange API for paper trading.

## Integration Points

### External APIs Used

- Twitter API v2 (Bearer Token authentication)
- CoinGecko API (for price data)
- RSS feeds from news sources
- Cryptocurrency exchange APIs (for live trading)

### Authentication

Authentication is handled through environment variables as specified in the `.env` file. The bot does not store credentials permanently.

## Versioning

The API follows semantic versioning. Breaking changes will increment the major version number. Backward-compatible additions will increment the minor version number.