def main():
    """
    Main function to run the enhanced trading bot
    """
    try:
        # Initialize the bot with 10,000 DOGE coins equivalent in USD
        bot = EnhancedTradingBot(initial_capital=10000, coin_symbol="DOGE")
        
        print("Enhanced Crypto Trading Bot is starting...")
        print("Press Ctrl+C to stop the bot")
        
        # Run a single cycle for testing
        bot.run_single_cycle()
        
        # Run with configurable interval from config file
        bot.run_continuous()
        
    except Exception as e:
        logger.error(f"Error running Enhanced Trading Bot: {str(e)}")