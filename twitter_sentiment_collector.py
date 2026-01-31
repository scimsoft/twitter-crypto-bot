#!/usr/bin/env python3
"""
Twitter Sentiment Collector for Crypto Trading Bot
This script connects to Twitter API and collects tweets from specified accounts
"""

import tweepy
import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TwitterSentimentCollector:
    def __init__(self, bearer_token=None, api_key=None, api_secret=None, access_token=None, access_token_secret=None):
        """
        Initialize the Twitter API client
        """
        try:
            # Option 1: Using Bearer Token (recommended for read-only access)
            if bearer_token:
                self.client = tweepy.Client(bearer_token=bearer_token)
            # Option 2: Using OAuth 1.0a User Context (for additional capabilities)
            elif all([api_key, api_secret, access_token, access_token_secret]):
                auth = tweepy.OAuth1UserHandler(
                    api_key, api_secret, access_token, access_token_secret
                )
                self.client = tweepy.Client(
                    bearer_token=bearer_token,
                    consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token=access_token,
                    access_token_secret=access_token_secret
                )
            else:
                raise ValueError("Either bearer_token or all four OAuth credentials must be provided")
            
            logger.info("Successfully initialized Twitter API client")
        
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
    # Load API credentials from environment variables (recommended)
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    
    # If you don't have credentials in environment variables, you can hardcode them temporarily
    # but remember to remove them for security reasons
    # bearer_token = "your_bearer_token_here"
    
    if not bearer_token:
        print("Error: Please set TWITTER_BEARER_TOKEN environment variable")
        print("You can get this from your Twitter Developer account")
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