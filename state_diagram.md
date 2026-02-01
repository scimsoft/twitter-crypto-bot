# State Event Diagram: Twitter Crypto Trading Bot

## Overview
This diagram represents the state transitions and event flows of the Twitter Crypto Trading Bot system, specifically focusing on the `NewsBasedTradingBot` implementation which uses news feeds for sentiment analysis.

## System States

```
[STARTUP] --> Initialize Environment Variables
    |
    v
[INITIALIZATION] --> Load Configuration
    |
    v
[READY] --> Wait for Cycle Trigger
    |
    v
[ANALYZE_PRICES] --> Fetch Current Cryptocurrency Prices
    |
    v
[ANALYZE_NEWS_SENTIMENT] --> Parse RSS Feeds and Analyze Sentiment
    |
    v
[GENERATE_SIGNAL] --> Determine BUY/SELL/HOLD Based on Sentiment
    |
    v
[EXECUTE_TRADE] --> Perform Trade Operation
    |
    v
[OPTIMIZE_STRATEGY] --> Adjust Parameters Based on Performance
    |
    v
[UPDATE_INTERFACE] --> Refresh Display Information
    |
    v
[WAIT_INTERVAL] --> Sleep Until Next Cycle
    |
    v
[READY] --> (Loop back to cycle trigger)
```

## Detailed State Transitions

### 1. STARTUP State
- **Entry**: Program execution begins
- **Activities**:
  - Import required libraries
  - Set up logging configuration
  - Load environment variables
- **Exit Condition**: Initialization successful

### 2. INITIALIZATION State
- **Entry**: After successful startup
- **Activities**:
  - Load trading parameters from config
  - Initialize trading variables (capital, holdings, thresholds)
  - Set up news RSS feed lists
  - Configure data structures (deques for history tracking)
- **Exit Condition**: All parameters loaded successfully

### 3. READY State
- **Entry**: After initialization
- **Activities**:
  - Monitor for cycle trigger (timer-based)
  - Wait for specified interval (default 15 minutes)
- **Transitions**:
  - Timer expires → ANALYZE_PRICES
  - Manual trigger → ANALYZE_PRICES

### 4. ANALYZE_PRICES State
- **Entry**: Cycle triggered
- **Activities**:
  - Attempt to fetch current price from multiple APIs (CoinGecko, Coinpaprika, CryptoCompare, Binance)
  - Handle API failures gracefully with fallbacks
  - Update price history deque
- **Transitions**:
  - Success → ANALYZE_NEWS_SENTIMENT
  - Failure → ANALYZE_NEWS_SENTIMENT (with default price)

### 5. ANALYZE_NEWS_SENTIMENT State
- **Entry**: After price analysis
- **Activities**:
  - Parse world news RSS feeds
  - Parse US news RSS feeds
  - Parse conflict/war RSS feeds
  - Parse crypto-specific RSS feeds
  - Apply TextBlob sentiment analysis to each article
  - Calculate aggregate sentiment score
  - Count positive/negative/neutral articles
  - Update sentiment history deque
- **Transitions**:
  - Always → GENERATE_SIGNAL

### 6. GENERATE_SIGNAL State
- **Entry**: After sentiment analysis
- **Activities**:
  - Adjust thresholds based on market volatility
  - Compare sentiment score to dynamic buy/sell thresholds
  - Generate BUY/SELL/HOLD signal
- **Transitions**:
  - BUY signal → EXECUTE_TRADE
  - SELL signal → EXECUTE_TRADE
  - HOLD signal → OPTIMIZE_STRATEGY

### 7. EXECUTE_TRADE State
- **Entry**: When BUY or SELL signal generated
- **Activities**:
  - Calculate position size based on sentiment strength
  - Validate sufficient funds/holdings
  - Update portfolio (cash and holdings)
  - Record trade in history
  - Log trade execution
- **Transitions**:
  - Always → OPTIMIZE_STRATEGY

### 8. OPTIMIZE_STRATEGY State
- **Entry**: After trade execution (or HOLD)
- **Activities**:
  - Analyze recent trade performance
  - Calculate win rate from last 10 trades
  - Adjust trading parameters (thresholds, position size) based on performance
  - Apply conservative or aggressive strategy based on win rate
- **Transitions**:
  - Always → UPDATE_INTERFACE

### 9. UPDATE_INTERFACE State
- **Entry**: After strategy optimization
- **Activities**:
  - Calculate current portfolio metrics
  - Format data for display
  - Print text-based interface with current status
  - Show recent trades and performance metrics
- **Transitions**:
  - Always → WAIT_INTERVAL

### 10. WAIT_INTERVAL State
- **Entry**: After interface update
- **Activities**:
  - Sleep for configured interval (default 15 minutes)
  - Handle interruption (Ctrl+C)
- **Transitions**:
  - Interval elapsed → READY
  - Interrupted → SHUTDOWN

## Error Handling States

### API_ERROR State
- **Trigger**: API call failure
- **Response**: Use alternative API or default values
- **Transition**: Return to original flow

### NETWORK_ERROR State
- **Trigger**: Network connectivity issue
- **Response**: Retry after delay or use cached data
- **Transition**: Return to original flow

### SHUTDOWN State
- **Trigger**: Keyboard interrupt (Ctrl+C) or system shutdown
- **Activities**:
  - Clean up resources
  - Save trade history
  - Close log files
- **Exit**: Program termination

## Events and Triggers

- **TIMER_EXPIRED**: Initiates new trading cycle
- **MANUAL_TRIGGER**: Forces immediate cycle execution
- **INTERRUPT_RECEIVED**: Stops the bot gracefully
- **API_RATE_LIMIT**: Triggers fallback to alternative API
- **INSUFFICIENT_FUNDS**: Prevents trade execution
- **PERFORMANCE_METRICS**: Triggers strategy optimization

## Data Flow

The system maintains several data structures that flow between states:
- `price_history`: Deque storing recent price data
- `sentiment_history`: Deque storing sentiment analysis results
- `trade_history`: List of executed trades
- `portfolio_history`: Deque storing portfolio value over time
- Configuration parameters loaded from `trading_config.json`

## Concurrency Considerations

- Single-threaded execution model
- Blocking operations (API calls, sleep) handled sequentially
- Logging is thread-safe but single-threaded in this implementation