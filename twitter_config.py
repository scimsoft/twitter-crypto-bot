"""
Configuration file for Twitter API credentials
Store your API keys here and import them into your main script
"""

import os
from dotenv import load_dotenv
from urllib.parse import unquote

# Load environment variables from .env file
load_dotenv('/home/gerrit/.openclaw/workspace/.env')

# Twitter API Credentials
# Get these from your Twitter Developer account at https://developer.twitter.com/
TWITTER_BEARER_TOKEN_RAW = os.getenv('TWITTER_BEARER_TOKEN', 'YOUR_BEARER_TOKEN_HERE')
TWITTER_BEARER_TOKEN = unquote(TWITTER_BEARER_TOKEN_RAW)  # Decode URL-encoded characters
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', 'YOUR_API_KEY_HERE')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', 'YOUR_API_SECRET_HERE')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN_HERE')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', 'YOUR_ACCESS_TOKEN_SECRET_HERE')

# List of crypto influencer accounts to monitor
CRYPTO_ACCOUNTS = [
    'elonmusk',
    'cz_binance', 
    'saylor',
    'VitalikButerin',
    'aantonop',
    'CryptoBae_',
    'CryptoWhale',
    'TheCryptoLark',
    'naval',
    'btcsunday',
    'coinbureau',
    'cryptobull',
    'CryptoHayes',
    'WuBlockchain',
    'APompliano',
    'CryptoMichNL',
    'bitboy_crypto'
]

# Number of tweets to fetch per account
TWEETS_PER_ACCOUNT = int(os.getenv('TWEETS_PER_ACCOUNT', '10'))

# File to save collected tweets
OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'twitter_data.json')