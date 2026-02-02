#!/usr/bin/env python3
"""
Trade Monitor for Enhanced Crypto Trading Bot
Monitors for new trades and sends updates
"""

import time
import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradeMonitor:
    def __init__(self, initial_capital=10000, coin_symbol="DOGE"):
        self.initial_capital = initial_capital
        self.coin_symbol = coin_symbol
        self.last_trade_count = 0
        self.last_portfolio_value = initial_capital
        self.last_cash_balance = initial_capital
        self.last_holdings = 0
        self.trades_file = "trade_history.json"
        
        # Load existing trade history if available
        self.trade_history = self.load_trade_history()
        
        logger.info(f"Trade Monitor initialized for {coin_symbol} trading bot")
    
    def load_trade_history(self):
        """Load existing trade history from file"""
        if os.path.exists(self.trades_file):
            try:
                with open(self.trades_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_trade_history(self, trade_history):
        """Save trade history to file"""
        with open(self.trades_file, 'w') as f:
            json.dump(trade_history, f, indent=2)
    
    def get_current_status(self):
        """Get current trading status"""
        # For this monitoring script, we'll simulate checking the bot status
        # In a real scenario, this would connect to the running bot instance
        
        # Create a mock status - in reality, this would interface with the running bot
        status = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_value': self.last_portfolio_value,
            'cash_balance': self.last_cash_balance,
            'holdings': self.last_holdings,
            'trade_count': len(self.trade_history),
            'profit_loss': self.last_portfolio_value - self.initial_capital,
            'profit_loss_pct': ((self.last_portfolio_value - self.initial_capital) / self.initial_capital) * 100
        }
        return status
    
    def check_for_new_trades(self):
        """Check if there are new trades since last check"""
        # In a real implementation, this would interface with the trading bot
        # to get the latest trade history
        
        # For now, we'll simulate by checking if the trade history file has been updated
        current_trade_count = len(self.trade_history)
        
        if current_trade_count > self.last_trade_count:
            new_trades = self.trade_history[self.last_trade_count:]
            self.last_trade_count = current_trade_count
            
            for trade in new_trades:
                self.send_trade_update(trade)
            
            return True, new_trades
        else:
            return False, []
    
    def send_trade_update(self, trade):
        """Format and send trade update"""
        trade_type = trade.get('type', 'UNKNOWN')
        coins = trade.get('coins', 0)
        price = trade.get('price', 0)
        amount_usd = trade.get('amount_usd', 0)
        timestamp = trade.get('timestamp', 'UNKNOWN')
        
        print("\n" + "="*50)
        print("🚨 TRADE EXECUTION ALERT 🚨")
        print("="*50)
        print(f"TRADE TYPE: {trade_type}")
        print(f"COINS: {coins:.4f} {self.coin_symbol}")
        print(f"PRICE: ${price:.6f}")
        print(f"AMOUNT: ${amount_usd:.2f}")
        print(f"TIME: {timestamp}")
        print("="*50)
        
        logger.info(f"New trade executed: {trade_type} {coins:.4f} {self.coin_symbol} at ${price:.6f}")
    
    def send_status_update(self):
        """Send a general status update"""
        status = self.get_current_status()
        
        print("\n" + "="*50)
        print("📊 PORTFOLIO STATUS UPDATE")
        print("="*50)
        print(f"PORTFOLIO VALUE: ${status['portfolio_value']:.2f}")
        print(f"CASH BALANCE: ${status['cash_balance']:.2f}")
        print(f"HOLDINGS: {status['holdings']:.4f} {self.coin_symbol}")
        print(f"PROFIT/LOSS: ${status['profit_loss']:.2f} ({status['profit_loss_pct']:+.2f}%)")
        print(f"TOTAL TRADES: {status['trade_count']}")
        print(f"TIME: {status['timestamp']}")
        print("="*50)
        
        logger.info(f"Status update: Portfolio ${status['portfolio_value']:.2f}, P/L ${status['profit_loss']:.2f}")
    
    def run_monitor(self, check_interval_minutes=15):
        """Run the trade monitor continuously"""
        logger.info(f"Starting trade monitor (checking every {check_interval_minutes} minutes)")
        
        # Send initial status update
        self.send_status_update()
        
        while True:
            try:
                has_new_trades, new_trades = self.check_for_new_trades()
                
                if has_new_trades:
                    for trade in new_trades:
                        self.send_trade_update(trade)
                
                # Sleep for the specified interval
                time.sleep(check_interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Trade monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in trade monitor: {str(e)}")
                time.sleep(60)  # Wait a minute before retrying


def main():
    """Main function to run the trade monitor"""
    try:
        # Initialize the trade monitor
        monitor = TradeMonitor(initial_capital=10000, coin_symbol="DOGE")
        
        print("Trade Monitor is starting...")
        print("This will monitor for new trades and send updates when they occur.")
        print("Press Ctrl+C to stop the monitor.")
        
        # Run the monitor (checking every 15 minutes)
        monitor.run_monitor(check_interval_minutes=15)
        
    except Exception as e:
        logger.error(f"Error running Trade Monitor: {str(e)}")


if __name__ == "__main__":
    main()