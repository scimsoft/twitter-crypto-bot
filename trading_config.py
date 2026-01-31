"""
Configuration file for the Automated Crypto Trading Bot
"""

# Trading parameters
SENTIMENT_THRESHOLDS = {
    'positive_threshold': 0.1,   # Minimum compound score for LONG signal
    'negative_threshold': -0.1,  # Maximum compound score for SHORT signal
}

# Trading settings
TRADING_SETTINGS = {
    'position_size': 0.01,       # Size of each position (1% of portfolio)
    'max_positions': 10,         # Maximum number of concurrent positions
    'stop_loss_percent': 0.05,   # Stop loss at 5%
    'take_profit_percent': 0.10, # Take profit at 10%
}

# Monitoring settings
MONITORING_SETTINGS = {
    'check_interval_hours': 1,   # Hours between sentiment checks
    'tweets_per_check': 20,      # Number of tweets to analyze per check
    'accounts_to_monitor': ['Reuters'],  # Accounts to monitor
}

# Risk management
RISK_MANAGEMENT = {
    'max_daily_trades': 5,       # Maximum trades per day
    'max_drawdown': 0.15,        # Maximum drawdown before pausing (15%)
    'enable_paper_trading': True, # Set to False for live trading (NOT RECOMMENDED)
}

# Notification settings
NOTIFICATIONS = {
    'email_alerts': False,       # Enable email notifications
    'alert_threshold': 0.2,      # Alert for sentiment swings greater than this
}

# Simulation settings
SIMULATION = {
    'simulate_trades': True,     # Set to False to enable real trading (NOT RECOMMENDED)
    'initial_balance': 10000,    # Initial balance for simulation
}

# Logging settings
LOGGING = {
    'log_level': 'INFO',
    'log_file': '/home/gerrit/.openclaw/workspace/trading_bot.log',
    'backup_count': 5,
}

# Exchange settings (placeholder - would need real exchange integration)
EXCHANGE_SETTINGS = {
    'exchange': 'SIMULATION',    # Options: 'SIMULATION', 'BINANCE', 'COINBASE', etc.
    'api_key': '',               # Your exchange API key
    'api_secret': '',            # Your exchange API secret
    'use_sandbox': True,         # Use exchange sandbox for testing
}