#!/usr/bin/env python3
"""
Automated Crypto Trading Bot based on Reuters Twitter Sentiment
Executes trades based on hourly sentiment analysis
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
import threading
import logging

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv('/home/gerrit/.openclaw/workspace/.env')

# Add the workspace directory to the Python path
sys.path.insert(0, '/home/gerrit/.openclaw/workspace')

try:
    from reuters_sentiment_tracker import ReutersSentimentTracker
    BOT_AVAILABLE = True
except ImportError:
    BOT_AVAILABLE = False
    print("Warning: ReutersSentimentTracker module not available.")
    print("Please ensure all required files are in the workspace.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/gerrit/.openclaw/workspace/trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutomatedCryptoTradingBot:
    def __init__(self):
        self.tracker = None
        self.is_running = False
        self.trade_history = []
        self.last_analysis_time = None
        self.interval_seconds = 3600  # 1 hour
        
        if BOT_AVAILABLE:
            self.tracker = ReutersSentimentTracker()
    
    def calculate_trade_signal(self, sentiment_data):
        """
        Calculate trade signal based on sentiment data
        Returns: 'LONG', 'SHORT', or 'HOLD'
        """
        if not sentiment_data:
            return 'HOLD'
        
        aggregate = sentiment_data.get('aggregate_results', {})
        overall_sentiment = aggregate.get('overall_sentiment', 'Neutral')
        avg_compound = aggregate.get('average_compound', 0.0)
        
        # Define thresholds for trading signals
        positive_threshold = 0.1
        negative_threshold = -0.1
        
        if overall_sentiment == 'Positive' and avg_compound > positive_threshold:
            return 'LONG'
        elif overall_sentiment == 'Negative' and avg_compound < negative_threshold:
            return 'SHORT'
        else:
            return 'HOLD'
    
    def execute_trade(self, signal, sentiment_data):
        """
        Execute a trade based on the signal
        NOTE: This is a simulation - no real trading occurs
        """
        if signal == 'HOLD':
            logger.info("No trade executed - HOLD signal")
            return None
        
        timestamp = datetime.now().isoformat()
        
        # Create a simulated trade record
        trade = {
            'timestamp': timestamp,
            'signal': signal,
            'sentiment_score': sentiment_data['aggregate_results']['average_compound'],
            'positive_tweets': sentiment_data['aggregate_results']['positive_tweets'],
            'negative_tweets': sentiment_data['aggregate_results']['negative_tweets'],
            'neutral_tweets': sentiment_data['aggregate_results']['neutral_tweets'],
            'status': 'SIMULATED'  # In a real system, this would be 'EXECUTED'
        }
        
        # Log the trade
        logger.info(f"TRADE EXECUTED: {signal} signal with sentiment {trade['sentiment_score']}")
        
        # Add to trade history
        self.trade_history.append(trade)
        
        # Save trade history
        self.save_trade_history()
        
        return trade
    
    def save_trade_history(self):
        """
        Save trade history to file
        """
        filename = '/home/gerrit/.openclaw/workspace/trade_history.json'
        
        # Load existing history if file exists
        existing_history = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    existing_history = json.load(f)
            except:
                existing_history = []
        
        # Combine with new trades
        all_trades = existing_history + self.trade_history[-10:]  # Keep last 10 trades
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(all_trades, f, indent=2, default=str)
        
        logger.info(f"Trade history updated with {len(self.trade_history[-10:])} new trades")
    
    def perform_analysis_and_trade(self):
        """
        Perform sentiment analysis and execute corresponding trade
        """
        logger.info("Starting Reuters sentiment analysis...")
        
        try:
            # Perform sentiment analysis
            sentiment_data = self.tracker.analyze_reuters_sentiment()
            
            if not sentiment_data:
                logger.error("Failed to get sentiment data")
                return
            
            # Calculate trade signal
            signal = self.calculate_trade_signal(sentiment_data)
            
            logger.info(f"Sentiment analysis complete. Signal: {signal}")
            logger.info(f"Average compound score: {sentiment_data['aggregate_results']['average_compound']}")
            
            # Execute trade based on signal
            trade = self.execute_trade(signal, sentiment_data)
            
            if trade:
                logger.info(f"Trade executed: {trade}")
            else:
                logger.info("No trade executed (HOLD signal)")
            
            # Update last analysis time
            self.last_analysis_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Error during analysis and trading: {str(e)}")
    
    def start_hourly_monitoring(self):
        """
        Start the hourly monitoring loop
        """
        if not self.tracker:
            logger.error("Trading bot not available - missing dependencies")
            return
        
        logger.info("Starting hourly Reuters sentiment monitoring...")
        self.is_running = True
        
        # Perform initial analysis
        self.perform_analysis_and_trade()
        
        # Schedule subsequent analyses
        while self.is_running:
            try:
                # Wait for the next interval
                time.sleep(self.interval_seconds)
                
                # Perform analysis and trading
                if self.is_running:
                    self.perform_analysis_and_trade()
                    
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received - stopping bot")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(60)  # Wait a minute before retrying
    
    def stop(self):
        """
        Stop the trading bot
        """
        logger.info("Stopping trading bot...")
        self.is_running = False
    
    def get_status(self):
        """
        Get current status of the bot
        """
        return {
            'is_running': self.is_running,
            'last_analysis': self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            'trade_count': len(self.trade_history),
            'next_analysis_in': self.interval_seconds - (time.time() - self.last_analysis_time.timestamp()) if self.last_analysis_time else self.interval_seconds
        }


def main():
    """
    Main function to run the trading bot
    """
    print("Automated Crypto Trading Bot based on Reuters Sentiment")
    print("=" * 55)
    
    # Check dependencies
    if not BOT_AVAILABLE:
        print("ERROR: Required modules not available.")
        print("Please ensure all files are in the workspace and dependencies are installed.")
        return
    
    # Check if Twitter credentials are set
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    if not bearer_token:
        print("TWITTER_BEARER_TOKEN environment variable not set!")
        print("Please set your Twitter API credentials before running this bot.")
        return
    
    # Initialize the bot
    bot = AutomatedCryptoTradingBot()
    
    print("Starting hourly monitoring of Reuters sentiment for crypto trading...")
    print("Press Ctrl+C to stop the bot")
    
    try:
        # Start the hourly monitoring
        bot.start_hourly_monitoring()
    except KeyboardInterrupt:
        print("\nShutting down trading bot...")
        bot.stop()
        print("Bot stopped.")
    except Exception as e:
        print(f"Error running bot: {str(e)}")
        logger.error(f"Error running bot: {str(e)}")


if __name__ == "__main__":
    main()