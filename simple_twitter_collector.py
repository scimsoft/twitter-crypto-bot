#!/usr/bin/env python3
"""
Simple Twitter Data Collector for Crypto Trading Bot
This script demonstrates the basic structure for collecting Twitter data
using only standard Python libraries
"""

import json
import urllib.request
import urllib.parse
from urllib.error import HTTPError
import time
from datetime import datetime
import os

# Load environment variables from .env file
from dotenv import load_dotenv
from urllib.parse import unquote
load_dotenv('/home/gerrit/.openclaw/workspace/.env')

# Get and decode the bearer token
BEARER_TOKEN_RAW = os.getenv('TWITTER_BEARER_TOKEN')
BEARER_TOKEN = unquote(BEARER_TOKEN_RAW) if BEARER_TOKEN_RAW else None

class SimpleTwitterCollector:
    """
    A simple Twitter collector using only standard libraries
    Note: This is for demonstration purposes only.
    For actual Twitter API access, you'll need to use tweepy or similar library
    """
    
    def __init__(self):
        # Twitter API base URL
        self.base_url = "https://api.twitter.com/2"
        
        # Get API credentials from environment variables
        bearer_token_raw = os.getenv('TWITTER_BEARER_TOKEN')
        self.bearer_token = unquote(bearer_token_raw) if bearer_token_raw else None
        
        if not self.bearer_token:
            print("Warning: TWITTER_BEARER_TOKEN environment variable not set.")
            print("You need to set this to access Twitter API")
    
    def _make_request(self, endpoint, params=None):
        """
        Make an authenticated request to Twitter API
        """
        # Prioritize bearer token authentication (app-only)
        if self.bearer_token and len(self.bearer_token) > 50:  # Valid bearer tokens are typically long
            url = f"{self.base_url}{endpoint}"
            if params:
                url += "?" + urllib.parse.urlencode(params)
            
            headers = {
                'Authorization': f'Bearer {self.bearer_token}',
                'Content-Type': 'application/json'
            }
            
            req = urllib.request.Request(url, headers=headers)
        else:
            # Fallback to OAuth 1.0a authentication if we have the necessary credentials
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            
            if api_key and api_secret and access_token and access_token_secret:
                # For OAuth 1.0a, we'd need to use a library like requests_oauthlib
                # Since we're using standard libraries only, we'll prioritize bearer token
                print("Note: Bearer token not valid, but OAuth credentials are available")
                raise Exception("OAuth 1.0a requires additional libraries. Please provide a valid Bearer Token.")
            else:
                raise Exception("No valid authentication method available")
        
        try:
            response = urllib.request.urlopen(req)
            data = response.read()
            return json.loads(data.decode('utf-8'))
        except HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            print(f"Response: {e.read().decode('utf-8')}")
            return None
    
    def get_user_by_username(self, username):
        """
        Get user information by username
        """
        endpoint = f"/users/by/username/{username}"
        params = {
            'user.fields': 'id,name,username,verified,description'
        }
        
        return self._make_request(endpoint, params)
    
    def get_tweets_by_user_id(self, user_id, max_results=10):
        """
        Get tweets by user ID
        """
        endpoint = f"/users/{user_id}/tweets"
        params = {
            'max_results': max_results,
            'tweet.fields': 'created_at,public_metrics,lang'
        }
        
        return self._make_request(endpoint, params)
    
    def get_tweets_from_multiple_accounts(self, usernames, max_results_per_account=10):
        """
        Get tweets from multiple accounts
        """
        all_tweets = []
        
        for username in usernames:
            print(f"Fetching data for user: {username}")
            
            # Get user ID first
            user_data = self.get_user_by_username(username)
            if not user_data or 'data' not in user_data:
                print(f"Could not find user: {username}")
                continue
            
            user_id = user_data['data']['id']
            print(f"Found user ID: {user_id}")
            
            # Get tweets for this user
            tweets_data = self.get_tweets_by_user_id(user_id, max_results_per_account)
            if not tweets_data or 'data' not in tweets_data:
                print(f"No tweets found for user: {username}")
                continue
            
            # Process tweets
            for tweet in tweets_data['data']:
                tweet_info = {
                    'username': username,
                    'user_id': user_id,
                    'tweet_id': tweet['id'],
                    'text': tweet['text'],
                    'created_at': tweet['created_at'],
                    'metrics': tweet.get('public_metrics', {}),
                    'timestamp': datetime.now().isoformat()
                }
                all_tweets.append(tweet_info)
            
            # Be respectful of rate limits
            time.sleep(1)
        
        return all_tweets
    
    def save_tweets(self, tweets, filename=None):
        """
        Save tweets to a JSON file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"collected_tweets_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tweets, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"Saved {len(tweets)} tweets to {filename}")
        return filename


def main():
    """
    Main function demonstrating usage
    """
    # Crypto influencer accounts to monitor
    crypto_accounts = [
        'elonmusk',
        'cz_binance', 
        'saylor',
        'VitalikButerin',
        'aantonop',
        'CryptoBae_',
        'CryptoWhale'
    ]
    
    # Initialize the collector
    collector = SimpleTwitterCollector()
    
    print("Starting Twitter data collection...")
    print(f"Monitoring accounts: {', '.join(crypto_accounts[:3])}...")  # Show first 3
    
    # Collect tweets
    tweets = collector.get_tweets_from_multiple_accounts(
        crypto_accounts, 
        max_results_per_account=5
    )
    
    if tweets:
        print(f"Successfully collected {len(tweets)} tweets")
        
        # Save to file
        filename = collector.save_tweets(tweets)
        print(f"Data saved to: {filename}")
        
        # Display sample
        print("\nSample tweet:")
        if tweets:
            sample_tweet = tweets[0]
            print(f"@{sample_tweet['username']}: {sample_tweet['text'][:100]}...")
    else:
        print("No tweets were collected. This could be due to:")
        print("1. Missing or invalid TWITTER_BEARER_TOKEN")
        print("2. Network connectivity issues")
        print("3. Twitter API rate limiting")
        print("4. The accounts having protected tweets")


if __name__ == "__main__":
    main()