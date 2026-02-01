#!/usr/bin/env python3
"""
Twitter Sentiment Collector for Crypto Trading Bot
This script connects to Twitter API and collects tweets from specified accounts
"""

import tweepy
import json
import os
import sys
from datetime import datetime
import logging

# Add parent directory to path to import twitter_config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from twitter_config import get_bearer_token

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TwitterSentimentCollector:
    def __init__(self, bearer_token=None, api_key=None, api_secret=None, access_token=None, access_token_secret=None):
        """
        Initialize the Twitter API client
        
        Args:
            bearer_token: Optional Bearer Token. If not provided, will be generated from API Key/Secret
            api_key: Optional API Key (used to generate Bearer Token if bearer_token not provided)
            api_secret: Optional API Secret (used to generate Bearer Token if bearer_token not provided)
            access_token: Optional Access Token (for OAuth 1.0a User Context - not currently used)
            access_token_secret: Optional Access Token Secret (for OAuth 1.0a User Context - not currently used)
        """
        try:
            # Get Bearer Token - use provided one, or get from config (which will generate if needed)
            if bearer_token:
                token_to_use = bearer_token
            elif api_key and api_secret:
                # Generate Bearer Token from provided API Key/Secret directly
                import base64
                import urllib.request
                import urllib.parse
                from urllib.error import HTTPError
                
                credentials = f"{api_key}:{api_secret}"
                encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
                
                url = "https://api.twitter.com/oauth2/token"
                data = urllib.parse.urlencode({'grant_type': 'client_credentials'}).encode('utf-8')
                headers = {
                    'Authorization': f'Basic {encoded_credentials}',
                    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
                }
                
                try:
                    req = urllib.request.Request(url, data=data, headers=headers)
                    response = urllib.request.urlopen(req, timeout=10)
                    response_data = json.loads(response.read().decode('utf-8'))
                    token_to_use = response_data.get('access_token')
                except Exception as e:
                    logger.warning(f"Failed to generate Bearer Token from provided credentials: {e}")
                    token_to_use = None
            else:
                # Try to get Bearer Token from config (will generate if needed)
                token_to_use = get_bearer_token()
            
            if not token_to_use:
                raise ValueError("Unable to get Bearer Token. Please provide bearer_token or api_key/api_secret.")
            
            # Use Bearer Token authentication (recommended for read-only access)
            self.client = tweepy.Client(bearer_token=token_to_use)
            
            logger.info("Successfully initialized Twitter API client with Bearer Token")
        
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API client: {str(e)}")
            raise

    def get_user_id(self, username):
        """
        Get user ID from username
        """
        try:
            user = self.client.get_user(username=username)
            return user.data.id
        except Exception as e:
            logger.error(f"Error getting user ID for {username}: {str(e)}")
            return None

    def get_tweets_from_user(self, username, max_results=10):
        """
        Get recent tweets from a specific user
        """
        try:
            user_id = self.get_user_id(username)
            if not user_id:
                return []
            
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'context_annotations']
            )
            
            if tweets.data:
                return tweets.data
            else:
                logger.info(f"No tweets found for user: {username}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching tweets from {username}: {str(e)}")
            return []

    def get_tweets_from_multiple_accounts(self, usernames, max_results_per_account=10):
        """
        Get tweets from multiple accounts
        """
        all_tweets = []
        for username in usernames:
            logger.info(f"Fetching tweets from: {username}")
            tweets = self.get_tweets_from_user(username, max_results_per_account)
            for tweet in tweets:
                tweet_data = {
                    'username': username,
                    'tweet_text': tweet.text,
                    'created_at': tweet.created_at,
                    'tweet_id': tweet.id,
                    'metrics': tweet.public_metrics if hasattr(tweet, 'public_metrics') else {}
                }
                all_tweets.append(tweet_data)
        
        return all_tweets

    def save_tweets(self, tweets, filename=None):
        """
        Save tweets to a JSON file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"twitter_data_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tweets, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"Saved {len(tweets)} tweets to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving tweets to file: {str(e)}")
            return None


def main():
    """
    Main function to demonstrate usage
    """
    # Get Bearer Token (will be generated from API Key/Secret if needed)
    bearer_token = get_bearer_token()
    
    if not bearer_token:
        print("Error: Unable to get Bearer Token.")
        print("Please ensure either:")
        print("1. TWITTER_BEARER_TOKEN is set in .env, OR")
        print("2. TWITTER_API_KEY and TWITTER_API_SECRET are set in .env")
        return
    
    # Initialize the collector
    collector = TwitterSentimentCollector(bearer_token=bearer_token)
    
    # Define the list of crypto influencer accounts to monitor
    crypto_accounts = [
        'elonmusk',
        'cz_binance', 
        'saylor',
        'VitalikButerin',
        'aantonop',
        'CryptoBae_',
        'CryptoWhale',
        'TheCryptoLark'
    ]
    
    print("Collecting tweets from crypto influencers...")
    
    # Get tweets from multiple accounts
    tweets = collector.get_tweets_from_multiple_accounts(crypto_accounts, max_results_per_account=5)
    
    print(f"Collected {len(tweets)} tweets")
    
    # Save tweets to file
    filename = collector.save_tweets(tweets)
    
    if filename:
        print(f"Tweets saved to {filename}")
        
        # Print sample of collected data
        print("\nSample of collected tweets:")
        for i, tweet in enumerate(tweets[:3]):  # Show first 3 tweets
            print(f"\n{i+1}. @{tweet['username']}: {tweet['tweet_text'][:100]}...")
            print(f"   Created: {tweet['created_at']}")


if __name__ == "__main__":
    main()