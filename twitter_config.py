"""
Configuration file for Twitter API credentials
Store your API keys here and import them into your main script
"""

import os
import json
import base64
import urllib.request
import urllib.parse
from urllib.error import HTTPError
from dotenv import load_dotenv
from urllib.parse import unquote

# Load environment variables from .env file
load_dotenv('/home/gerrit/.openclaw/workspace/twitter-crypto-bot/.env')

# Twitter API Credentials
# Get these from your Twitter Developer account at https://developer.twitter.com/
TWITTER_BEARER_TOKEN_RAW = os.getenv('TWITTER_BEARER_TOKEN', 'YOUR_BEARER_TOKEN_HERE')
TWITTER_BEARER_TOKEN = unquote(TWITTER_BEARER_TOKEN_RAW).strip() if TWITTER_BEARER_TOKEN_RAW and TWITTER_BEARER_TOKEN_RAW != 'YOUR_BEARER_TOKEN_HERE' else None
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', 'YOUR_API_KEY_HERE')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', 'YOUR_API_SECRET_HERE')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN_HERE')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', 'YOUR_ACCESS_TOKEN_SECRET_HERE')


def get_bearer_token():
    """
    Get Bearer Token for Twitter API authentication.
    Prioritizes generating a fresh token from API Key and Secret if available,
    otherwise falls back to using the stored Bearer Token.
    
    Returns:
        str: Bearer Token for Twitter API authentication, or None if unavailable
    """
    # Prioritize generating Bearer Token from API Key and Secret (more reliable)
    if TWITTER_API_KEY and TWITTER_API_SECRET and \
       TWITTER_API_KEY != 'YOUR_API_KEY_HERE' and TWITTER_API_SECRET != 'YOUR_API_SECRET_HERE':
        generated_token = generate_bearer_token_from_credentials()
        if generated_token:
            return generated_token
    
    # Fall back to stored Bearer Token if available
    if TWITTER_BEARER_TOKEN and len(TWITTER_BEARER_TOKEN) > 50:
        return TWITTER_BEARER_TOKEN
    
    return None


def generate_bearer_token_from_credentials():
    """
    Generate a Bearer Token from API Key and Secret using OAuth 2.0 Application-Only authentication.
    
    Returns:
        str: Bearer Token, or None if generation fails
    """
    if not TWITTER_API_KEY or not TWITTER_API_SECRET:
        return None
    
    # Encode API Key and Secret in base64
    credentials = f"{TWITTER_API_KEY}:{TWITTER_API_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    
    # Make request to get Bearer Token
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
        
        if 'access_token' in response_data:
            return response_data['access_token']
        else:
            print(f"Warning: Failed to generate Bearer Token. Response: {response_data}")
            return None
            
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_data = json.loads(error_body)
            error_msg = error_data.get('error_description', error_data.get('error', 'Unknown error'))
        except:
            error_msg = error_body
        
        print(f"Error generating Bearer Token: HTTP {e.code} - {error_msg}")
        return None
        
    except Exception as e:
        print(f"Error generating Bearer Token: {str(e)}")
        return None

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