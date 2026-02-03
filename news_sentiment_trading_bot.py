#!/usr/bin/env python3
"""
News-Based Crypto Trading Bot
Uses world news feeds for sentiment analysis instead of Twitter
"""

from sentiment_logger import SentimentLogger
import requests
import json
import time
import logging
import os
import sys
import threading
from datetime import datetime
from collections import deque
import statistics
from textblob import TextBlob
import feedparser

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
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
        self.feed_error_counts = {}  # Track error counts for each feed URL
        self.removed_feeds_file = "removed_feeds.json"  # File to store removed feed URLs
        self.removed_feeds = set()  # Set of removed feed URLs
        self.bot_data_file = "bot_data.json"  # File to store bot data for web interface
        self.state_file = "bot_state.json"  # File to store bot state (holdings, capital, etc.)
        self.interface_running = False  # Flag to control auto-updating interface
        self.last_update_time = None  # Track last interface update

        # Load previously removed feeds
        self._load_removed_feeds()
        
        # Load bot state (holdings, capital, trade history)
        self._load_bot_state()
        
        # Start background thread to save bot data for web interface
        self._start_data_saver()

        # Strategy optimization parameters
        # Using total_sentiment (sum) instead of average, so thresholds are higher
        self.buy_threshold = 5.0  # Buy when total_sentiment is above this
        self.sell_threshold = -3.0  # Sell when total_sentiment is below this
        self.max_position_size = 0.2  # Max 20% of portfolio per trade
        self.stop_loss_pct = 0.05  # 5% stop loss
        self.take_profit_pct = 0.15  # 15% take profit

        # World news RSS feeds (focusing on global events, conflicts, and politics)
        world_news_feeds_raw = [
            "https://feeds.bbci.co.uk/news/world/rss.xml",
            "https://www.aljazeera.com/xml/rss/all.xml",
            "https://rss.dw.com/xml/rss-en-all",
            "https://www.france24.com/en/rss",
            "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
            "https://www.tabnak.ir/fa/rss/allnews",
            "https://lenta.ru/rss/",
            "https://www.ft.com/world?format=rss",
            "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
            "https://www.financialsamurai.com/feed/",
        ]
        
        # US news RSS feeds
        us_news_feeds_raw = [
            "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
            "https://abcnews.go.com/abcnews/usheadlines",
        ]

        # Conflict/Wars focused feeds
        conflict_feeds_raw = [
            "https://www.defensenews.com/arc/outboundfeeds/rss/category/global-navy-news/?outputType=xml",
            "https://www.euronews.com/rss",
            "https://www.theguardian.com/world/rss",
        ]

        # Crypto-specific news sources (removed - not relevant to world events)
        crypto_news_feeds_raw = [
            "http://rss.cnn.com/rss/money_topstories.rss",
            "http://thehill.com/rss/syndicator/19110",
            "http://feeds.feedburner.com/DrudgeReportFeed",
            "https://www.chron.com/rss/feed/News-270.php",
            "https://www.usnews.com/rss/money",
            "https://www.theatlantic.com/feed/all/",
            "http://news.com.au/feed",
            "http://www.chinadaily.com.cn/rss/world_rss.xml",
            "http://indianexpress.com/section/world/feed/",
            "https://www.sfgate.com/rss/feed/Business-and-Technology-News-448.php",
            "http://variety.com/feed/",
            "http://www.globaltimes.cn/rss/outbrain.xml",
            "http://news.yahoo.com/rss",
            "http://rss.cnn.com/rss/cnn_topstories.rss",
            "http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
            "http://feeds.foxnews.com/foxnews/latest",
            "http://feeds.nbcnews.com/feeds/topstories",
            "http://feeds.washingtonpost.com/rss/business",
            "http://abcnews.go.com/abcnews/topstories",
            "http://rssfeeds.usatoday.com/usatoday-NewsTopStories",
            "http://www.latimes.com/rss2.0.xml",
            "https://www.yahoo.com/news/rss/finance",
            "http://feeds.bbci.co.uk/news/rss.xml",
            "https://www.theguardian.com/business/economics/rss",
            "http://www.dailymail.co.uk/articles.rss",
            "https://www.forbes.com/real-time/feed2/",
            "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
            "https://www.huffingtonpost.com/section/front-page/feed",
            "http://feeds2.feedburner.com/businessinsider",
            "https://www.rt.com/rss/",
            "https://feeds.feedburner.com/NDTV-LatestNews",
            "https://gadgets.ndtv.com/rss/feeds",
            "http://www.telegraph.co.uk/rss.xml",
            "http://www.independent.co.uk/rss",
            "https://gizmodo.com/rss",
            "http://www.wsj.com/xml/rss/3_7031.xml",
            "http://feeds.reuters.com/reuters/topNews",
            "https://live.engadget.com/rss.xml",
            "https://www.investing.com/rss/news.rss",
            "https://nypost.com/feed/",
            "http://time.com/feed/",
            "https://www.thesun.co.uk/feed/",
            "https://asia.nikkei.com/rss/feed/nar",
            "https://www.cbsnews.com/latest/rss/main",
            "http://feeds.mashable.com/Mashable",
            "https://www.wired.com/rss/",
            "http://feeds.arstechnica.com/arstechnica/index/",
            "https://feeds.feedburner.com/CoinDesk",
            "http://feeds.marketwatch.com/marketwatch/topstories/",
            "http://rss.dw.com/xml/rss-en-all",
            "https://www.entrepreneur.com/latest.rss",
            "https://seekingalpha.com/market_currents.xml",
            "https://www.ft.com/?format=rss",
            "http://www.firstpost.com/feed",
            "http://fortune.com/feed/",
            "https://www.androidauthority.com/feed/",
            "https://qz.com/feed/",
            "http://feeds.smh.com.au/rssheadlines/top.xml",
            "http://www.economist.com/sections/economics/rss.xml",
            "https://news.bitcoin.com/feed/",
            "https://www.vanityfair.com/feed/rss",
            "https://cointelegraph.com/feed",
            "http://rss.nzherald.co.nz/rss/xml/nzhtsrsscid_000000698.xml",
            "http://feeds2.feedburner.com/thenextweb",
            "https://www.theglobeandmail.com/?service=rss&feed=topstories",
            "https://www.ccn.com/feed/",
            "http://www.scmp.com/rss/91/feed",
            "https://www.prnewswire.com/rss/all-news-releases-from-PR-newswire-news.rss",
            "https://boingboing.net/feed",
            "https://wccftech.com/feed/",
            "https://www.inverse.com/feed/articles/1.rss",
            "https://99bitcoins.com/feed/",
            "https://www.technologyreview.com/stories.rss",
            "https://www.which.co.uk/news/feed/",
            "https://rss.dailyfx.com/feeds/all",
            "https://themerkle.com/feed/",
            "http://www.newsbtc.com/feed/",
            "https://hacked.com/feed",
            "https://nextshark.com/feed/",
            "http://business.financialpost.com/feed",
            "http://abc13.com/feed/",
            "http://vancouversun.com/feed",
            "https://bitcoinmagazine.com/feed",
            "http://www.valuewalk.com/feed/",
            "http://www.dailynews.com/feed/",
            "https://www.moneyweb.co.za/feed",
            "https://coincentral.com/feed/",
            "http://ethereumworldnews.com/feed/",
            "https://www.coinspeaker.com/feed/",
            "https://www.profitconfidential.com/feed/",
            "http://reneweconomy.com.au/feed/",
            "https://cryptovest.com/feed",
            "https://www.smartcompany.com.au/feed/",
            "http://www.livebitcoinnews.com/feed",
            "https://www.bitsonline.com/feed/",
            "http://www.sci-news.com/feed",
            "https://stocknewsjournal.com/feed/",
            "https://oracletimes.com/feed/",
            "http://www.bankingtech.com/feed",
            "https://www.influencive.com/feed/",
            "https://stocknewsgazette.com/feed/",
            "https://etfdailynews.com/feed/",
            "https://71republic.com/feed/",
            "https://news4c.com/feed/",
            "https://flintdaily.com/feed/",
            "https://solarindustrymag.com/feed",
            "https://finnewsdaily.com/feed",
            "https://cryptoslate.com/feed/",
            "https://www.techllog.com/feed/",
            "http://cryptocrimson.com/feed",
        ]
        
        # Filter out removed feeds from all feed lists
        self.world_news_feeds = [f for f in world_news_feeds_raw if f not in self.removed_feeds]
        self.us_news_feeds = [f for f in us_news_feeds_raw if f not in self.removed_feeds]
        self.conflict_feeds = [f for f in conflict_feeds_raw if f not in self.removed_feeds]
        self.crypto_news_feeds = [f for f in crypto_news_feeds_raw if f not in self.removed_feeds]
        
        if self.removed_feeds:
            logger.info(f"Filtered out {len(self.removed_feeds)} previously removed feed(s)")

        logger.info(
            f"News-Based Trading Bot initialized with ${initial_capital} in {coin_symbol}"
        )

    def _load_removed_feeds(self):
        """
        Load previously removed feed URLs from file
        """
        if os.path.exists(self.removed_feeds_file):
            try:
                with open(self.removed_feeds_file, 'r') as f:
                    removed_list = json.load(f)
                    self.removed_feeds = set(removed_list)
                    logger.info(f"Loaded {len(self.removed_feeds)} removed feed(s) from {self.removed_feeds_file}")
            except Exception as e:
                logger.warning(f"Failed to load removed feeds file: {e}")
                self.removed_feeds = set()
        else:
            self.removed_feeds = set()

    def _save_removed_feeds(self):
        """
        Save removed feed URLs to file
        """
        try:
            with open(self.removed_feeds_file, 'w') as f:
                json.dump(list(self.removed_feeds), f, indent=2)
            logger.info(f"Saved {len(self.removed_feeds)} removed feed(s) to {self.removed_feeds_file}")
        except Exception as e:
            logger.error(f"Failed to save removed feeds file: {e}")

    def _save_bot_state(self):
        """
        Save bot state (holdings, capital, trade history) to file for persistence
        """
        try:
            state = {
                "initial_capital": self.initial_capital,
                "current_capital": self.current_capital,
                "holdings": self.holdings,
                "coin_symbol": self.coin_symbol,
                "trade_history": self.trade_history,
                "price_history": list(self.price_history),
                "sentiment_history": list(self.sentiment_history),
                "portfolio_history": list(self.portfolio_history),
                "buy_threshold": self.buy_threshold,
                "sell_threshold": self.sell_threshold,
                "max_position_size": self.max_position_size,
                "last_saved": datetime.now().isoformat(),
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            logger.debug(f"Saved bot state to {self.state_file}")
        except Exception as e:
            logger.error(f"Failed to save bot state: {e}")

    def _load_bot_state(self):
        """
        Load bot state from file if it exists
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                # Restore state
                if "current_capital" in state:
                    self.current_capital = float(state["current_capital"])
                    logger.info(f"Loaded current capital: ${self.current_capital:.2f}")
                
                if "holdings" in state:
                    self.holdings = float(state["holdings"])
                    logger.info(f"Loaded holdings: {self.holdings:.4f} {self.coin_symbol}")
                
                if "initial_capital" in state:
                    # Preserve the original initial capital
                    self.initial_capital = float(state["initial_capital"])
                
                if "trade_history" in state:
                    self.trade_history = state["trade_history"]
                    logger.info(f"Loaded {len(self.trade_history)} previous trades")
                
                if "price_history" in state and state["price_history"]:
                    self.price_history = deque(state["price_history"], maxlen=100)
                
                if "sentiment_history" in state and state["sentiment_history"]:
                    self.sentiment_history = deque(state["sentiment_history"], maxlen=50)
                
                if "portfolio_history" in state and state["portfolio_history"]:
                    self.portfolio_history = deque(state["portfolio_history"], maxlen=100)
                
                if "buy_threshold" in state:
                    self.buy_threshold = float(state["buy_threshold"])
                
                if "sell_threshold" in state:
                    self.sell_threshold = float(state["sell_threshold"])
                
                if "max_position_size" in state:
                    self.max_position_size = float(state["max_position_size"])
                
                logger.info(f"Bot state loaded from {self.state_file}")
                logger.info(f"Resuming with: ${self.current_capital:.2f} cash, {self.holdings:.4f} {self.coin_symbol} holdings")
                
            except Exception as e:
                logger.warning(f"Failed to load bot state: {e}. Starting fresh.")
        else:
            logger.info("No previous bot state found. Starting fresh.")

    def _save_bot_data_for_web_interface(self):
        """
        Save bot data to JSON file for web interface access
        Builds data dict directly to ensure current state is captured.
        Uses latest sentiment from sentiment_history.
        """
        try:
            current_price = self.get_current_price()
            portfolio_value = self.calculate_portfolio_value()
            profit_loss = portfolio_value - self.initial_capital
            profit_loss_pct = (profit_loss / self.initial_capital) * 100 if self.initial_capital > 0 else 0
            
            # Get recent sentiment data with total_sentiment
            recent_sentiment_data = (
                self.sentiment_history[-1]
                if self.sentiment_history
                else {
                    "score": 0,
                    "total_sentiment": 0,
                    "positive_articles": 0,
                    "negative_articles": 0,
                    "neutral_articles": 0,
                    "article_count": 0,
                }
            )
            
            # Get recent trades directly from trade_history
            recent_trades = list(self.trade_history[-5:]) if self.trade_history else []
            
            # Build the data dict directly with current state
            data = {
                "current_price": current_price,
                "portfolio_value": portfolio_value,
                "cash_balance": self.current_capital,
                "holdings": self.holdings,
                "holdings_value": self.holdings * current_price,
                "initial_capital": self.initial_capital,
                "profit_loss": profit_loss,
                "profit_loss_pct": profit_loss_pct,
                "coin_symbol": self.coin_symbol,
                "sentiment_score": float(recent_sentiment_data.get("score", 0)),
                "total_sentiment": float(recent_sentiment_data.get("total_sentiment", 0)),
                "avg_sentiment": float(recent_sentiment_data.get("score", 0)),
                "position_size": self.max_position_size,
                "recent_trades": recent_trades,
                "total_trades": len(self.trade_history),
                "buy_threshold": self.buy_threshold,
                "sell_threshold": self.sell_threshold,
                "positive_articles": recent_sentiment_data.get("positive_articles", 0),
                "negative_articles": recent_sentiment_data.get("negative_articles", 0),
                "neutral_articles": recent_sentiment_data.get("neutral_articles", 0),
                "article_count": recent_sentiment_data.get("article_count", 0),
                "last_update": datetime.now().isoformat(),
                "bot_status": "running"
            }
            
            with open(self.bot_data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.debug(f"Error saving bot data for web interface: {e}")

    def _save_bot_data_for_web_interface_with_sentiment(self, total_sentiment, avg_sentiment, 
                                                         pos_articles, neg_articles, neu_articles, article_count):
        """
        Save bot data to JSON file with explicit sentiment values (for immediate save after cycle)
        This method builds the data dict directly to ensure we capture the latest state.
        """
        try:
            current_price = self.get_current_price()
            portfolio_value = self.calculate_portfolio_value()
            profit_loss = portfolio_value - self.initial_capital
            profit_loss_pct = (profit_loss / self.initial_capital) * 100 if self.initial_capital > 0 else 0
            
            # Get recent trades directly from trade_history
            recent_trades = list(self.trade_history[-5:]) if self.trade_history else []
            
            # Build the data dict directly with current state
            data = {
                "current_price": current_price,
                "portfolio_value": portfolio_value,
                "cash_balance": self.current_capital,
                "holdings": self.holdings,
                "holdings_value": self.holdings * current_price,
                "initial_capital": self.initial_capital,
                "profit_loss": profit_loss,
                "profit_loss_pct": profit_loss_pct,
                "coin_symbol": self.coin_symbol,
                "sentiment_score": float(avg_sentiment) if avg_sentiment is not None else 0.0,
                "total_sentiment": float(total_sentiment) if total_sentiment is not None else 0.0,
                "avg_sentiment": float(avg_sentiment) if avg_sentiment is not None else 0.0,
                "position_size": self.max_position_size,
                "recent_trades": recent_trades,
                "total_trades": len(self.trade_history),
                "buy_threshold": self.buy_threshold,
                "sell_threshold": self.sell_threshold,
                "positive_articles": int(pos_articles) if pos_articles is not None else 0,
                "negative_articles": int(neg_articles) if neg_articles is not None else 0,
                "neutral_articles": int(neu_articles) if neu_articles is not None else 0,
                "article_count": int(article_count) if article_count is not None else 0,
                "last_update": datetime.now().isoformat(),
                "bot_status": "running"
            }
            
            with open(self.bot_data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved bot data: Cash=${self.current_capital:.2f}, Holdings={self.holdings:.4f}, Trades={len(self.trade_history)}")
        except Exception as e:
            logger.error(f"Error saving bot data with sentiment: {e}")

    def _save_bot_data_periodically(self):
        """
        Background thread to save bot data periodically
        """
        while True:
            try:
                self._save_bot_data_for_web_interface()
                # Also save state periodically (less frequently)
                self._save_bot_state()
            except Exception as e:
                logger.debug(f"Error in periodic bot data save: {e}")
            time.sleep(5)  # Save every 5 seconds

    def _start_data_saver(self):
        """
        Start background thread to save bot data for web interface
        """
        thread = threading.Thread(target=self._save_bot_data_periodically, daemon=True)
        thread.start()
        return thread

    def get_current_price(self):
        """
        Get current price of the cryptocurrency from multiple free APIs to avoid rate limits
        """
        # List of free APIs to try in order
        apis_to_try = [
            self._get_price_coingecko,
            self._get_price_coinpaprika,
            self._get_price_crypto_compare,
            self._get_price_binance,
        ]

        for api_func in apis_to_try:
            try:
                price = api_func()
                if price and price > 0:
                    self.price_history.append(
                        {"price": price, "timestamp": datetime.now().isoformat()}
                    )
                    return price
            except Exception as e:
                logger.debug(f"Error using {api_func.__name__}: {str(e)}")
                continue

        # If all APIs fail, return a default price for DOGE
        logger.warning("All price APIs failed, using default price")
        return 0.10

    def _get_price_coingecko(self):
        """Get price from CoinGecko API"""
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": self.coin_symbol.lower(), "vs_currencies": "usd"}

        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if self.coin_symbol.lower() in data:
                return data[self.coin_symbol.lower()]["usd"]
        elif response.status_code == 429:
            raise Exception("CoinGecko rate limit exceeded")
        else:
            raise Exception(f"CoinGecko returned status code {response.status_code}")

    def _get_price_coinpaprika(self):
        """Get price from Coinpaprika API"""
        url = f"https://api.coinpaprika.com/v1/tickers/{self.coin_symbol.lower()}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data["quotes"]["USD"]["price"]
        else:
            raise Exception(f"Coinpaprika returned status code {response.status_code}")

    def _get_price_crypto_compare(self):
        """Get price from CryptoCompare API"""
        url = f"https://min-api.cryptocompare.com/data/price"
        params = {"fsym": self.coin_symbol.upper(), "tsyms": "USD"}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "USD" in data:
                return data["USD"]
        else:
            raise Exception(
                f"CryptoCompare returned status code {response.status_code}"
            )

    def _get_price_binance(self):
        """Get price from Binance API"""
        url = f"https://api.binance.com/api/v3/ticker/price"
        params = {"symbol": f"{self.coin_symbol.upper()}USDT"}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return float(data["price"])
        else:
            raise Exception(f"Binance returned status code {response.status_code}")

    def calculate_portfolio_value(self):
        """
        Calculate total portfolio value (cash + holdings * current price)
        """
        current_price = self.get_current_price()
        total_value = self.current_capital + (self.holdings * current_price)
        self.portfolio_history.append(
            {"value": total_value, "timestamp": datetime.now().isoformat()}
        )
        return total_value

    def analyze_news_sentiment(self):
        """
        Analyze sentiment from world news, US news, and conflict feeds
        """
        # Combine all types of news feeds: world news, US news, and conflicts
        # all_feeds = self.world_news_feeds + self.us_news_feeds + self.conflict_feeds + self.crypto_news_feeds
        all_feeds = self.crypto_news_feeds.copy()  # Use copy to avoid modifying original during iteration

        total_sentiment = 0
        article_count = 0
        positive_articles = 0
        negative_articles = 0
        neutral_articles = 0
        feeds_to_remove = []  # Track feeds that should be removed

        for feed_url in all_feeds:
            try:
                # Fetch the RSS feed with timeout
                try:
                    response = requests.get(feed_url, timeout=10)
                    response.raise_for_status()
                    # Parse the RSS feed content
                    feed = feedparser.parse(response.content)
                    # Reset error count on successful fetch
                    if feed_url in self.feed_error_counts:
                        self.feed_error_counts[feed_url] = 0
                except requests.RequestException as e:
                    # Increment error count
                    self.feed_error_counts[feed_url] = self.feed_error_counts.get(feed_url, 0) + 1
                    error_count = self.feed_error_counts[feed_url]
                    logger.warning(f"Failed to fetch feed {feed_url} (error #{error_count}): {e}")
                    
                    # Mark for removal if error count reaches 2
                    if error_count >= 2:
                        feeds_to_remove.append(feed_url)
                        logger.info(f"Removing feed {feed_url} after {error_count} consecutive errors")
                    continue

                # Analyze only the first article from each feed
                articles_to_analyze = feed.entries[:1] if feed.entries else []

                for entry in articles_to_analyze:
                    title = entry.title if hasattr(entry, "title") else ""
                    summary = entry.summary if hasattr(entry, "summary") else ""

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
                    if article_count >= 250:  # Maximum 50 articles per cycle
                        break

                if article_count >= 250:
                    break

            except Exception as e:
                # Increment error count
                self.feed_error_counts[feed_url] = self.feed_error_counts.get(feed_url, 0) + 1
                error_count = self.feed_error_counts[feed_url]
                logger.debug(f"Error parsing feed {feed_url} (error #{error_count}): {str(e)}")
                
                # Mark for removal if error count reaches 2
                if error_count >= 2:
                    feeds_to_remove.append(feed_url)
                    logger.info(f"Removing feed {feed_url} after {error_count} consecutive errors")
                continue
        
        # Remove feeds that have failed 2 times
        if feeds_to_remove:
            for feed_url in feeds_to_remove:
                if feed_url in self.world_news_feeds:
                    self.world_news_feeds.remove(feed_url)
                if feed_url in self.us_news_feeds:
                    self.us_news_feeds.remove(feed_url)
                if feed_url in self.conflict_feeds:
                    self.conflict_feeds.remove(feed_url)
                if feed_url in self.crypto_news_feeds:
                    self.crypto_news_feeds.remove(feed_url)
                # Add to removed feeds set for persistence
                self.removed_feeds.add(feed_url)
                # Clean up error count tracking
                if feed_url in self.feed_error_counts:
                    del self.feed_error_counts[feed_url]
            
            # Save removed feeds to file for persistence
            self._save_removed_feeds()

        # Calculate average sentiment
        avg_sentiment = total_sentiment / article_count if article_count > 0 else 0
        self.sentiment_history.append(
            {
                "score": avg_sentiment,  # Keep avg for backward compatibility/display
                "total_sentiment": total_sentiment,  # Store total_sentiment for threshold comparison
                "timestamp": datetime.now().isoformat(),
                "article_count": article_count,
                "positive_articles": positive_articles,
                "negative_articles": negative_articles,
                "neutral_articles": neutral_articles,
            }
        )

        logger.info(
            f"Analyzed {article_count} articles. Avg sentiment: {avg_sentiment:.3f}"
        )

        logger.info(
            f"Breakdown: {positive_articles} positive, {negative_articles} negative, {neutral_articles} neutral"
        )

        logger.info(
            f"total sentiment: {total_sentiment}"
        )

        return total_sentiment, avg_sentiment, positive_articles, negative_articles, neutral_articles

    def generate_signal(self, total_sentiment):
        """
        Generate trading signal based on total_sentiment (sum of all sentiment scores) and market conditions
        Uses total_sentiment instead of average sentiment for threshold comparison
        """
        # Adjust thresholds based on market volatility
        current_price = self.get_current_price()
        if len(self.price_history) > 10:
            prices = [p["price"] for p in list(self.price_history)[-10:]]
            volatility = (
                statistics.stdev(prices) / statistics.mean(prices)
                if len(set(prices)) > 1
                else 0.02
            )

            # Adjust thresholds based on volatility (less aggressive adjustment)
            # Reduced multiplier from 2 to 0.5 to make volatility adjustment less aggressive
            volatility_multiplier = 0.5
            dynamic_buy_threshold = self.buy_threshold * (1 + volatility * volatility_multiplier)
            dynamic_sell_threshold = self.sell_threshold * (1 + volatility * volatility_multiplier)
            logger.info(f"Volatility: {volatility:.4f}, Dynamic buy threshold: {dynamic_buy_threshold:.3f}, Dynamic sell threshold: {dynamic_sell_threshold:.3f}")
        else:
            dynamic_buy_threshold = self.buy_threshold
            dynamic_sell_threshold = self.sell_threshold
            logger.info(f"Using base thresholds - Buy: {dynamic_buy_threshold:.3f}, Sell: {dynamic_sell_threshold:.3f}")

        # Generate signal based on total_sentiment and thresholds
        logger.info(f"Comparing total_sentiment ({total_sentiment:.3f}) against thresholds (Buy: {dynamic_buy_threshold:.3f}, Sell: {dynamic_sell_threshold:.3f})")
        if total_sentiment >= dynamic_buy_threshold:
            return "BUY"
        elif total_sentiment <= dynamic_sell_threshold:
            return "SELL"
        else:
            return "HOLD"

    def execute_trade(self, signal, sentiment_score):
        """
        Execute a trade based on the signal
        """
        current_price = self.get_current_price()
        portfolio_value = self.calculate_portfolio_value()

        # Calculate position size based on sentiment strength and risk management
        sentiment_strength = abs(sentiment_score)
        position_size_ratio = min(
            self.max_position_size, sentiment_strength * 0.5
        )  # Cap at max position size

        trade_amount = portfolio_value * position_size_ratio

        if signal == "BUY":
            if self.current_capital >= trade_amount:
                coins_to_buy = trade_amount / current_price
                self.holdings += coins_to_buy
                self.current_capital -= trade_amount

                trade_record = {
                    "type": "BUY",
                    "amount_usd": trade_amount,
                    "coins": coins_to_buy,
                    "price": current_price,
                    "timestamp": datetime.now().isoformat(),
                    "sentiment": sentiment_score,
                }

                self.trade_history.append(trade_record)
                logger.info(
                    f"BUY executed: {coins_to_buy:.4f} {self.coin_symbol} at ${current_price:.4f}, spent ${trade_amount:.2f}"
                )
                # Save state after trade
                self._save_bot_state()
                return True
            else:
                logger.info("Insufficient funds to execute BUY")
                return False

        elif signal == "SELL":
            if self.holdings > 0:
                coins_to_sell = min(
                    self.holdings, (trade_amount / current_price)
                )  # Sell portion based on signal strength
                proceeds = coins_to_sell * current_price
                self.holdings -= coins_to_sell
                self.current_capital += proceeds

                trade_record = {
                    "type": "SELL",
                    "amount_usd": proceeds,
                    "coins": coins_to_sell,
                    "price": current_price,
                    "timestamp": datetime.now().isoformat(),
                    "sentiment": sentiment_score,
                }

                self.trade_history.append(trade_record)
                logger.info(
                    f"SELL executed: {coins_to_sell:.4f} {self.coin_symbol} at ${current_price:.4f}, received ${proceeds:.2f}"
                )
                # Save state after trade
                self._save_bot_state()
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
            prev_trade = recent_trades[i - 1]
            curr_trade = recent_trades[i]

            if prev_trade["type"] == "BUY" and curr_trade["type"] == "SELL":
                # Check if this buy/sell pair was profitable
                buy_price = prev_trade["price"]
                sell_price = curr_trade["price"]
                if sell_price > buy_price:
                    winning_trades += 1
            elif prev_trade["type"] == "SELL" and curr_trade["type"] == "BUY":
                # Check if this sell/buy pair was profitable (short position)
                sell_price = prev_trade["price"]
                buy_price = curr_trade["price"]
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
            self.max_position_size = min(
                0.3, self.max_position_size * 1.1
            )  # Increase position size

        logger.info(
            f"Strategy optimized - Win rate: {win_rate:.2f}, Buy threshold: {self.buy_threshold:.3f}"
        )
        
        # Save state after optimization
        self._save_bot_state()

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
        recent_sentiment_data = (
            self.sentiment_history[-1]
            if self.sentiment_history
            else {
                "score": 0,
                "total_sentiment": 0,
                "positive_articles": 0,
                "negative_articles": 0,
                "neutral_articles": 0,
                "article_count": 0,
            }
        )
        recent_sentiment = recent_sentiment_data.get("score", 0)
        total_sentiment = recent_sentiment_data.get("total_sentiment", 0)
        # Use score as avg_sentiment, or calculate from total_sentiment if available
        if total_sentiment != 0 and recent_sentiment_data.get("article_count", 0) > 0:
            avg_sentiment = total_sentiment / recent_sentiment_data.get("article_count", 1)
        else:
            avg_sentiment = recent_sentiment

        # Get recent trades
        recent_trades = self.trade_history[-5:] if self.trade_history else []

        # Format interface data
        interface_data = {
            "current_price": current_price,
            "portfolio_value": portfolio_value,
            "cash_balance": self.current_capital,
            "holdings": self.holdings,
            "holdings_value": self.holdings * current_price,
            "initial_capital": self.initial_capital,
            "profit_loss": profit_loss,
            "profit_loss_pct": profit_loss_pct,
            "coin_symbol": self.coin_symbol,
            "sentiment_score": float(recent_sentiment) if recent_sentiment is not None else 0.0,
            "total_sentiment": float(total_sentiment) if total_sentiment is not None else 0.0,
            "avg_sentiment": float(avg_sentiment) if avg_sentiment is not None else 0.0,
            "position_size": self.max_position_size,
            "recent_trades": recent_trades,
            "total_trades": len(self.trade_history),
            "buy_threshold": self.buy_threshold,
            "sell_threshold": self.sell_threshold,
            "positive_articles": recent_sentiment_data.get("positive_articles", 0),
            "negative_articles": recent_sentiment_data.get("negative_articles", 0),
            "neutral_articles": recent_sentiment_data.get("neutral_articles", 0),
            "article_count": recent_sentiment_data.get("article_count", 0),
        }

        return interface_data

    def print_interface(self):
        """
        Print a simple text-based interface with trading information
        """
        data = self.get_interface_data()

        print("\n" + "=" * 70)
        print(f"           NEWS-BASED CRYPTO TRADING BOT INTERFACE")
        print("=" * 70)
        print(f"Current {data['coin_symbol']} Price:     ${data['current_price']:.6f}")
        print(f"Portfolio Value:          ${data['portfolio_value']:.2f}")
        print(f"Cash Balance:             ${data['cash_balance']:.2f}")
        print(
            f"Holdings:                 {data['holdings']:.4f} {data['coin_symbol']} (${data['holdings_value']:.2f})"
        )
        print("-" * 70)
        print(
            f"Profit/Loss:              ${data['profit_loss']:.2f} ({data['profit_loss_pct']:+.2f}%)"
        )
        print(f"Initial Capital:          ${data['initial_capital']:.2f}")
        print("-" * 70)
        recent_sentiment_data = (
            self.sentiment_history[-1]
            if self.sentiment_history
            else {"total_sentiment": 0, "score": 0}
        )
        total_sent = recent_sentiment_data.get("total_sentiment", recent_sentiment_data.get("score", 0))
        
        print(f"Total Sentiment:          {total_sent:.3f} (used for thresholds)")
        print(f"Average Sentiment:        {data['sentiment_score']:.3f}")
        print(
            f"Articles Analyzed:        {data['positive_articles']}+ / {data['negative_articles']}- / {data['neutral_articles']}="
        )
        print(f"Buy Threshold:            {data['buy_threshold']:.3f} (total_sentiment)")
        print(f"Sell Threshold:           {data['sell_threshold']:.3f} (total_sentiment)")
        print(f"Position Size:            {(data['position_size']*100):.1f}%")
        print(f"Total Trades:             {data['total_trades']}")
        print("=" * 70)

        if data["recent_trades"]:
            print("Recent Trades:")
            for trade in reversed(data["recent_trades"]):
                trade_type = trade["type"].ljust(4)
                coins = trade["coins"]
                price = trade["price"]
                amount = trade["amount_usd"]
                print(
                    f"  {trade['timestamp'][11:19]} {trade_type} {coins:.4f} {data['coin_symbol']} @ ${price:.6f} (${amount:.2f})"
                )
        else:
            print("Recent Trades:           None")

        print("=" * 70)

    def run_single_cycle(self):
        """
        Run one complete cycle of the trading bot
        """
        logger.info("Starting trading cycle...")

        # Get current price
        current_price = self.get_current_price()
        logger.info(f"Current {self.coin_symbol} price: ${current_price:.6f}")

        # Analyze sentiment from news feeds
        total_sentiment, avg_sentiment, pos_articles, neg_articles, neu_articles = (
            self.analyze_news_sentiment()
        )
        # Calculate article count from the breakdown
        article_count = pos_articles + neg_articles + neu_articles
        logger.info(f"Total sentiment: {total_sentiment:.3f}, Average sentiment: {avg_sentiment:.3f}")

        # Generate trading signal using total_sentiment
        signal = self.generate_signal(total_sentiment)
        logger.info(f"Trading signal: {signal}")

        # Execute trade if applicable
        # Use avg_sentiment for position sizing (normalized), total_sentiment is used for signal generation
        if signal in ["BUY", "SELL"]:
            success = self.execute_trade(signal, avg_sentiment)
            if success:
                logger.info(f"{signal} order executed successfully")
            else:
                logger.info(f"{signal} order failed")

        # Optimize strategy based on performance
        self.optimize_strategy()

        # Save bot data for web interface immediately after cycle with latest sentiment
        # Pass the current cycle's sentiment data to ensure we save the latest values
        self._save_bot_data_for_web_interface_with_sentiment(
            total_sentiment, avg_sentiment, pos_articles, neg_articles, neu_articles, article_count
        )

        # Print current status (only if interface is not auto-updating)
        if not self.interface_running:
            self.print_interface()

        return {
            "price": current_price,
            "total_sentiment": total_sentiment,
            "avg_sentiment": avg_sentiment,
            "signal": signal,
            "portfolio_value": self.calculate_portfolio_value(),
            "articles_breakdown": {
                "positive": pos_articles,
                "negative": neg_articles,
                "neutral": neu_articles,
            },
        }

    def run_continuous(self, interval_minutes=15, auto_update_interface=False, interface_update_seconds=5):
        """
        Run the trading bot continuously at specified intervals
        
        Args:
            interval_minutes: Minutes between trading cycles
            auto_update_interface: If True, start auto-updating interface (terminal)
            interface_update_seconds: Seconds between interface updates
        """
        logger.info(
            f"Starting continuous trading mode (checking every {interval_minutes} minutes)"
        )

        # Start auto-updating interface if requested
        if auto_update_interface:
            logger.info(f"Starting auto-updating interface (updates every {interface_update_seconds} seconds)")
            self.start_auto_updating_interface(update_interval_seconds=interface_update_seconds)
            # Give interface time to initialize
            time.sleep(1)

        while True:
            try:
                self.run_single_cycle()
                logger.info(f"Waiting {interval_minutes} minutes until next cycle...")
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                self.interface_running = False
                break
            except Exception as e:
                logger.error(f"Error in trading cycle: {str(e)}")
                time.sleep(60)  # Wait a minute before retrying


def main():
    """
    Main function to run the news-based trading bot
    """
    global bot_instance
    try:
        # Initialize the bot with 10,000 DOGE coins equivalent in USD
        bot = NewsBasedTradingBot(initial_capital=10000, coin_symbol="DOGE")
        bot_instance = bot  # Set global instance for web server

        print("News-Based Crypto Trading Bot is starting...")
        print(
            "This bot uses world news feeds for sentiment analysis instead of Twitter."
        )
        print("Press Ctrl+C to stop the bot")
        print("\nTo start the web interface, run: python3 web_interface_server.py")

        # Run a single cycle for testing
        bot.run_single_cycle()

        # Run continuously with 15-minute intervals
        # auto_update_interface=False because we're using web interface instead
        bot.run_continuous(interval_minutes=15, auto_update_interface=False)

    except Exception as e:
        logger.error(f"Error running News-Based Trading Bot: {str(e)}")

# Global bot instance for web server access
bot_instance = None

if __name__ == "__main__":
    main()
