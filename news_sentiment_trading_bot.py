#!/usr/bin/env python3
"""
News-Based Crypto Trading Bot
Uses financial news feeds for sentiment analysis instead of Twitter
"""

import requests
import json
import time
import logging
from datetime import datetime
from collections import deque
import statistics
from textblob import TextBlob
import feedparser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsBasedTradingBot:
    def __init__(self, initial_capital=10000, coin_symbol="DOGE"):
        """
        Initialize the news-based trading bot
        """
        # Initialize trading parameters
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.coin_symbol = coin_symbol.upper()
        self.holdings = 0  # Amount of coin held
        self.price_history = deque(maxlen=100)  # Track last 100 prices
        self.trade_history = []  # Track all trades
        self.sentiment_history = deque(maxlen=50)  # Track sentiment scores
        self.portfolio_history = deque(maxlen=100)  # Track portfolio value over time
        
        # Strategy optimization parameters
        self.buy_threshold = 0.3  # Buy when sentiment is above this
        self.sell_threshold = -0.2  # Sell when sentiment is below this
        self.max_position_size = 0.2  # Max 20% of portfolio per trade
        self.stop_loss_pct = 0.05  # 5% stop loss
        self.take_profit_pct = 0.15  # 15% take profit
        
        # World news RSS feeds (focusing on global events, conflicts, and politics)
        self.world_news_feeds = [
            'https://feeds.reuters.com/Reuters/worldNews',
            'https://rss.cnn.com/rss/edition.rss',
            'https://feeds.bbci.co.uk/news/world/rss.xml',
            'https://www.aljazeera.com/xml/rss/all.xml',
            'https://rss.dw.com/xml/rss-en-all',
            'https://www.france24.com/en/rss',
            'https://www.npr.org/sections/news/latest/rss.xml',
            'https://feeds.apnews.com/apnews.xml',
            'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
            'https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml'
        ]
        
        # US news RSS feeds
        self.us_news_feeds = [
            'https://feeds.reuters.com/Reuters/domesticNews',
            'https://rss.cnn.com/rss/edition_us.rss',
            'https://feeds.bbci.co.uk/news/us_and_canada/rss.xml',
            'https://rss.nytimes.com/services/xml/rss/nyt/US.xml',
            'https://www.washingtonpost.com/rss-national.xml',
            'https://abcnews.go.com/abcnews/usheadlines',
            'https://www.nbcnews.com/feed'
        ]
        
        # Conflict/Wars focused feeds
        self.conflict_feeds = [
            'https://www.defensenews.com/arc/outboundfeeds/rss/category/global-navy-news/?outputType=xml',
            'https://foreignpolicy.com/feed/',
            'https://www.euronews.com/rss',
            'https://www.theguardian.com/world/rss'
        ]
        
        # Crypto-specific news sources (still relevant for market impact)
        self.crypto_news_feeds = [
            'https://cointelegraph.com/rss',
            'https://crypto.news/feed/',
            'https://www.coindesk.com/feed/',
            'https://decrypt.co/feed'
        ]
        
        logger.info(f"News-Based Trading Bot initialized with ${initial_capital} in {coin_symbol}")

    def get_current_price(self):
        """
        Get current price of the cryptocurrency from CoinGecko API
        """
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': self.coin_symbol.lower(),
                'vs_currencies': 'usd'
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if self.coin_symbol.lower() in data:
                    price = data[self.coin_symbol.lower()]['usd']
                    self.price_history.append({
                        'price': price,
                        'timestamp': datetime.now().isoformat()
                    })
                    return price
                else:
                    logger.warning(f"Coin {self.coin_symbol} not found in CoinGecko")
                    # Default to $0.10 for DOGE if API fails
                    return 0.10
            else:
                logger.error(f"Failed to get price from CoinGecko: {response.status_code}")
                # Default to $0.10 for DOGE if API fails
                return 0.10
        except Exception as e:
            logger.error(f"Error getting current price: {str(e)}")
            # Default to $0.10 for DOGE if API fails
            return 0.10

    def calculate_portfolio_value(self):
        """
        Calculate total portfolio value (cash + holdings * current price)
        """
        current_price = self.get_current_price()
        total_value = self.current_capital + (self.holdings * current_price)
        self.portfolio_history.append({
            'value': total_value,
            'timestamp': datetime.now().isoformat()
        })
        return total_value

    def analyze_news_sentiment(self):
        """
        Analyze sentiment from world news, US news, and conflict feeds
        """
        # Combine all types of news feeds: world news, US news, conflicts, and crypto-specific
        all_feeds = self.world_news_feeds + self.us_news_feeds + self.conflict_feeds + self.crypto_news_feeds
        
        total_sentiment = 0
        article_count = 0
        positive_articles = 0
        negative_articles = 0
        neutral_articles = 0
        
        for feed_url in all_feeds:
            try:
                # Parse the RSS feed
                feed = feedparser.parse(feed_url)
                
                # Analyze recent articles (last 10)
                articles_to_analyze = feed.entries[:10] if len(feed.entries) > 10 else feed.entries
                
                for entry in articles_to_analyze:
                    title = entry.title if hasattr(entry, 'title') else ""
                    summary = entry.summary if hasattr(entry, 'summary') else ""
                    
                    # Combine title and summary for sentiment analysis
                    text = f"{title} {summary}".lower()
                    
                    # Skip if text is too short
                    if len(text.strip()) < 10:
                        continue
                    
                    # Use TextBlob for sentiment analysis
                    blob = TextBlob(text)
                    sentiment_score = blob.sentiment.polarity  # Range: -1 to 1
                    
                    # Classify sentiment
                    if sentiment_score > 0.1:
                        positive_articles += 1
                    elif sentiment_score < -0.1:
                        negative_articles += 1
                    else:
                        neutral_articles += 1
                    
                    total_sentiment += sentiment_score
                    article_count += 1
                    
                    # Limit to avoid overwhelming with too many articles
                    if article_count >= 50:  # Maximum 50 articles per cycle
                        break
                
                if article_count >= 50:
                    break
                    
            except Exception as e:
                logger.debug(f"Error parsing feed {feed_url}: {str(e)}")
                continue
        
        # Calculate average sentiment
        avg_sentiment = total_sentiment / article_count if article_count > 0 else 0
        self.sentiment_history.append({
            'score': avg_sentiment,
            'timestamp': datetime.now().isoformat(),
            'article_count': article_count,
            'positive_articles': positive_articles,
            'negative_articles': negative_articles,
            'neutral_articles': neutral_articles
        })
        
        logger.info(f"Analyzed {article_count} articles. Avg sentiment: {avg_sentiment:.3f}")
        logger.info(f"Breakdown: {positive_articles} positive, {negative_articles} negative, {neutral_articles} neutral")
        
        return avg_sentiment, positive_articles, negative_articles, neutral_articles

    def generate_signal(self, sentiment_score):
        """
        Generate trading signal based on sentiment and market conditions
        """
        # Adjust thresholds based on market volatility
        current_price = self.get_current_price()
        if len(self.price_history) > 10:
            prices = [p['price'] for p in list(self.price_history)[-10:]]
            volatility = statistics.stdev(prices) / statistics.mean(prices) if len(set(prices)) > 1 else 0.02
            
            # Adjust thresholds based on volatility
            dynamic_buy_threshold = self.buy_threshold * (1 + volatility * 2)
            dynamic_sell_threshold = self.sell_threshold * (1 + volatility * 2)
        else:
            dynamic_buy_threshold = self.buy_threshold
            dynamic_sell_threshold = self.sell_threshold
        
        # Generate signal based on sentiment and thresholds
        if sentiment_score >= dynamic_buy_threshold:
            return 'BUY'
        elif sentiment_score <= dynamic_sell_threshold:
            return 'SELL'
        else:
            return 'HOLD'

    def execute_trade(self, signal, sentiment_score):
        """
        Execute a trade based on the signal
        """
        current_price = self.get_current_price()
        portfolio_value = self.calculate_portfolio_value()
        
        # Calculate position size based on sentiment strength and risk management
        sentiment_strength = abs(sentiment_score)
        position_size_ratio = min(self.max_position_size, sentiment_strength * 0.5)  # Cap at max position size
        
        trade_amount = portfolio_value * position_size_ratio
        
        if signal == 'BUY':
            if self.current_capital >= trade_amount:
                coins_to_buy = trade_amount / current_price
                self.holdings += coins_to_buy
                self.current_capital -= trade_amount
                
                trade_record = {
                    'type': 'BUY',
                    'amount_usd': trade_amount,
                    'coins': coins_to_buy,
                    'price': current_price,
                    'timestamp': datetime.now().isoformat(),
                    'sentiment': sentiment_score
                }
                
                self.trade_history.append(trade_record)
                logger.info(f"BUY executed: {coins_to_buy:.4f} {self.coin_symbol} at ${current_price:.4f}, spent ${trade_amount:.2f}")
                return True
            else:
                logger.info("Insufficient funds to execute BUY")
                return False
                
        elif signal == 'SELL':
            if self.holdings > 0:
                coins_to_sell = min(self.holdings, (trade_amount / current_price))  # Sell portion based on signal strength
                proceeds = coins_to_sell * current_price
                self.holdings -= coins_to_sell
                self.current_capital += proceeds
                
                trade_record = {
                    'type': 'SELL',
                    'amount_usd': proceeds,
                    'coins': coins_to_sell,
                    'price': current_price,
                    'timestamp': datetime.now().isoformat(),
                    'sentiment': sentiment_score
                }
                
                self.trade_history.append(trade_record)
                logger.info(f"SELL executed: {coins_to_sell:.4f} {self.coin_symbol} at ${current_price:.4f}, received ${proceeds:.2f}")
                return True
            else:
                logger.info("No holdings to execute SELL")
                return False
        
        return False  # HOLD signal

    def optimize_strategy(self):
        """
        Optimize trading strategy based on historical performance
        """
        if len(self.trade_history) < 5:
            return  # Need enough trades to optimize
        
        # Analyze recent performance to adjust parameters
        recent_trades = self.trade_history[-10:]  # Last 10 trades
        winning_trades = 0
        total_trades = len(recent_trades)
        
        for i in range(1, len(recent_trades)):
            prev_trade = recent_trades[i-1]
            curr_trade = recent_trades[i]
            
            if prev_trade['type'] == 'BUY' and curr_trade['type'] == 'SELL':
                # Check if this buy/sell pair was profitable
                buy_price = prev_trade['price']
                sell_price = curr_trade['price']
                if sell_price > buy_price:
                    winning_trades += 1
            elif prev_trade['type'] == 'SELL' and curr_trade['type'] == 'BUY':
                # Check if this sell/buy pair was profitable (short position)
                sell_price = prev_trade['price']
                buy_price = curr_trade['price']
                if sell_price > buy_price:
                    winning_trades += 1
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Adjust strategy based on win rate
        if win_rate < 0.4:  # Low win rate, be more conservative
            self.buy_threshold *= 1.1  # Make buying harder
            self.sell_threshold *= 1.1  # Make selling easier
            self.max_position_size *= 0.9  # Reduce position size
        elif win_rate > 0.7:  # High win rate, be more aggressive
            self.buy_threshold *= 0.95  # Make buying easier
            self.sell_threshold *= 0.95  # Make selling harder
            self.max_position_size = min(0.3, self.max_position_size * 1.1)  # Increase position size
        
        logger.info(f"Strategy optimized - Win rate: {win_rate:.2f}, Buy threshold: {self.buy_threshold:.3f}")

    def get_interface_data(self):
        """
        Get data formatted for the trading interface
        """
        current_price = self.get_current_price()
        portfolio_value = self.calculate_portfolio_value()
        
        # Calculate profit/loss
        profit_loss = portfolio_value - self.initial_capital
        profit_loss_pct = (profit_loss / self.initial_capital) * 100
        
        # Get recent sentiment
        recent_sentiment_data = self.sentiment_history[-1] if self.sentiment_history else {'score': 0, 'positive_articles': 0, 'negative_articles': 0, 'neutral_articles': 0}
        recent_sentiment = recent_sentiment_data['score']
        
        # Get recent trades
        recent_trades = self.trade_history[-5:] if self.trade_history else []
        
        # Format interface data
        interface_data = {
            'current_price': current_price,
            'portfolio_value': portfolio_value,
            'cash_balance': self.current_capital,
            'holdings': self.holdings,
            'holdings_value': self.holdings * current_price,
            'initial_capital': self.initial_capital,
            'profit_loss': profit_loss,
            'profit_loss_pct': profit_loss_pct,
            'coin_symbol': self.coin_symbol,
            'sentiment_score': recent_sentiment,
            'position_size': self.max_position_size,
            'recent_trades': recent_trades,
            'total_trades': len(self.trade_history),
            'buy_threshold': self.buy_threshold,
            'sell_threshold': self.sell_threshold,
            'positive_articles': recent_sentiment_data['positive_articles'],
            'negative_articles': recent_sentiment_data['negative_articles'],
            'neutral_articles': recent_sentiment_data['neutral_articles']
        }
        
        return interface_data

    def print_interface(self):
        """
        Print a simple text-based interface with trading information
        """
        data = self.get_interface_data()
        
        print("\n" + "="*70)
        print(f"           NEWS-BASED CRYPTO TRADING BOT INTERFACE")
        print("="*70)
        print(f"Current {data['coin_symbol']} Price:     ${data['current_price']:.6f}")
        print(f"Portfolio Value:          ${data['portfolio_value']:.2f}")
        print(f"Cash Balance:             ${data['cash_balance']:.2f}")
        print(f"Holdings:                 {data['holdings']:.4f} {data['coin_symbol']} (${data['holdings_value']:.2f})")
        print("-"*70)
        print(f"Profit/Loss:              ${data['profit_loss']:.2f} ({data['profit_loss_pct']:+.2f}%)")
        print(f"Initial Capital:          ${data['initial_capital']:.2f}")
        print("-"*70)
        print(f"Current Sentiment:        {data['sentiment_score']:.3f}")
        print(f"Articles Analyzed:        {data['positive_articles']}+ / {data['negative_articles']}- / {data['neutral_articles']}=")
        print(f"Buy Threshold:            {data['buy_threshold']:.3f}")
        print(f"Sell Threshold:           {data['sell_threshold']:.3f}")
        print(f"Position Size:            {(data['position_size']*100):.1f}%")
        print(f"Total Trades:             {data['total_trades']}")
        print("="*70)
        
        if data['recent_trades']:
            print("Recent Trades:")
            for trade in reversed(data['recent_trades']):
                trade_type = trade['type'].ljust(4)
                coins = trade['coins']
                price = trade['price']
                amount = trade['amount_usd']
                print(f"  {trade['timestamp'][11:19]} {trade_type} {coins:.4f} {data['coin_symbol']} @ ${price:.6f} (${amount:.2f})")
        else:
            print("Recent Trades:           None")
        
        print("="*70)

    def run_single_cycle(self):
        """
        Run one complete cycle of the trading bot
        """
        logger.info("Starting trading cycle...")
        
        # Get current price
        current_price = self.get_current_price()
        logger.info(f"Current {self.coin_symbol} price: ${current_price:.6f}")
        
        # Analyze sentiment from news feeds
        sentiment_score, pos_articles, neg_articles, neu_articles = self.analyze_news_sentiment()
        logger.info(f"Average sentiment score: {sentiment_score:.3f}")
        
        # Generate trading signal
        signal = self.generate_signal(sentiment_score)
        logger.info(f"Trading signal: {signal}")
        
        # Execute trade if applicable
        if signal in ['BUY', 'SELL']:
            success = self.execute_trade(signal, sentiment_score)
            if success:
                logger.info(f"{signal} order executed successfully")
            else:
                logger.info(f"{signal} order failed")
        
        # Optimize strategy based on performance
        self.optimize_strategy()
        
        # Print current status
        self.print_interface()
        
        return {
            'price': current_price,
            'sentiment': sentiment_score,
            'signal': signal,
            'portfolio_value': self.calculate_portfolio_value(),
            'articles_breakdown': {
                'positive': pos_articles,
                'negative': neg_articles,
                'neutral': neu_articles
            }
        }

    def run_continuous(self, interval_minutes=15):
        """
        Run the trading bot continuously at specified intervals
        """
        logger.info(f"Starting continuous trading mode (checking every {interval_minutes} minutes)")
        
        while True:
            try:
                self.run_single_cycle()
                logger.info(f"Waiting {interval_minutes} minutes until next cycle...")
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in trading cycle: {str(e)}")
                time.sleep(60)  # Wait a minute before retrying


def main():
    """
    Main function to run the news-based trading bot
    """
    try:
        # Initialize the bot with 10,000 DOGE coins equivalent in USD
        bot = NewsBasedTradingBot(initial_capital=10000, coin_symbol="DOGE")
        
        print("News-Based Crypto Trading Bot is starting...")
        print("This bot uses financial news feeds for sentiment analysis instead of Twitter.")
        print("Press Ctrl+C to stop the bot")
        
        # Run a single cycle for testing
        bot.run_single_cycle()
        
        # Uncomment the line below to run continuously
        # bot.run_continuous(interval_minutes=15)  # Run every 15 minutes
        
    except Exception as e:
        logger.error(f"Error running News-Based Trading Bot: {str(e)}")


if __name__ == "__main__":
    main()