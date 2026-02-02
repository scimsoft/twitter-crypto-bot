#!/usr/bin/env python3
"""
Reuters Twitter Sentiment Tracker
Combines Twitter data collection with sentiment analysis for Reuters account
"""

import json
import os
from datetime import datetime
import sys

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv('/home/gerrit/.openclaw/workspace/.env')

# Add the workspace directory to the Python path so we can import our modules
sys.path.insert(0, '/home/gerrit/.openclaw/workspace')

try:
    from twitter_sentiment_analyzer import TwitterSentimentAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError:
    ANALYZER_AVAILABLE = False
    print("Warning: twitter_sentiment_analyzer module not available.")
    print("Please run: pip install vaderSentiment")

try:
    from simple_twitter_collector import SimpleTwitterCollector
    COLLECTOR_AVAILABLE = True
except ImportError:
    COLLECTOR_AVAILABLE = False
    print("Warning: simple_twitter_collector module not available.")

class ReutersSentimentTracker:
    def __init__(self):
        self.sentiment_analyzer = None
        self.twitter_collector = None
        
        if ANALYZER_AVAILABLE:
            self.sentiment_analyzer = TwitterSentimentAnalyzer()
        
        if COLLECTOR_AVAILABLE:
            self.twitter_collector = SimpleTwitterCollector()
    
    def collect_reuters_tweets(self, max_tweets=20):
        """
        Collect tweets from Reuters account
        """
        if not self.twitter_collector:
            print("Twitter collector not available. Please check dependencies.")
            return []
        
        print("Collecting tweets from Reuters account...")
        tweets = self.twitter_collector.get_tweets_from_multiple_accounts(['Reuters'], max_results_per_account=max_tweets)
        print(f"Collected {len(tweets)} tweets from Reuters")
        return tweets
    
    def analyze_reuters_sentiment(self, tweets=None):
        """
        Analyze sentiment of Reuters tweets
        If tweets parameter is None, collect fresh tweets
        """
        if tweets is None:
            tweets = self.collect_reuters_tweets()
        
        if not self.sentiment_analyzer:
            print("Sentiment analyzer not available. Please check dependencies.")
            return None
        
        if not tweets:
            print("No tweets to analyze.")
            return None
        
        print(f"Analyzing sentiment of {len(tweets)} Reuters tweets...")
        sentiment_results = self.sentiment_analyzer.analyze_tweets_batch(tweets)
        
        # Aggregate results
        aggregate = self.sentiment_analyzer.aggregate_sentiment(sentiment_results)
        
        analysis_result = {
            'collection_timestamp': datetime.now().isoformat(),
            'account_analyzed': 'Reuters',
            'total_tweets': len(tweets),
            'individual_results': sentiment_results,
            'aggregate_results': aggregate,
            'tweets_sample': [t['text'] for t in tweets[:5]]  # Include first 5 tweets as sample
        }
        
        return analysis_result
    
    def save_analysis(self, analysis_result, filename=None):
        """
        Save analysis results to a file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reuters_sentiment_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"Analysis saved to: {filename}")
        return filename
    
    def print_summary(self, analysis_result):
        """
        Print a summary of the analysis
        """
        if not analysis_result:
            print("No analysis result to display.")
            return
        
        print("\n" + "="*60)
        print("REUTERS SENTIMENT ANALYSIS SUMMARY")
        print("="*60)
        print(f"Collection Time: {analysis_result['collection_timestamp']}")
        print(f"Account: {analysis_result['account_analyzed']}")
        print(f"Total Tweets Analyzed: {analysis_result['total_tweets']}")
        print(f"Overall Sentiment: {analysis_result['aggregate_results']['overall_sentiment']}")
        print(f"Average Compound Score: {analysis_result['aggregate_results']['average_compound']}")
        print(f"Positive Tweets: {analysis_result['aggregate_results']['positive_tweets']} "
              f"({analysis_result['aggregate_results']['sentiment_distribution']['positive']*100:.1f}%)")
        print(f"Negative Tweets: {analysis_result['aggregate_results']['negative_tweets']} "
              f"({analysis_result['aggregate_results']['sentiment_distribution']['negative']*100:.1f}%)")
        print(f"Neutral Tweets: {analysis_result['aggregate_results']['neutral_tweets']} "
              f"({analysis_result['aggregate_results']['sentiment_distribution']['neutral']*100:.1f}%)")
        
        print("\nSample Tweets Analyzed:")
        print("-" * 40)
        for i, tweet in enumerate(analysis_result['tweets_sample'], 1):
            print(f"{i}. {tweet[:100]}...")


def main():
    """
    Main function to run the Reuters sentiment tracker
    """
    print("Reuters Twitter Sentiment Tracker")
    print("=" * 40)
    
    # Initialize the tracker
    tracker = ReutersSentimentTracker()
    
    # Check if required components are available
    if not ANALYZER_AVAILABLE:
        print("ERROR: Sentiment analyzer not available.")
        print("Please install required packages: pip install vaderSentiment")
        return
    
    if not COLLECTOR_AVAILABLE:
        print("ERROR: Twitter collector not available.")
        print("Please ensure simple_twitter_collector.py is in the workspace.")
        return
    
    # Perform analysis
    analysis_result = tracker.analyze_reuters_sentiment()
    
    if analysis_result:
        # Print summary
        tracker.print_summary(analysis_result)
        
        # Save results
        filename = tracker.save_analysis(analysis_result)
        
        print(f"\nDetailed results saved to: {filename}")
        
        # Based on sentiment, suggest trading direction
        overall_sentiment = analysis_result['aggregate_results']['overall_sentiment']
        avg_compound = analysis_result['aggregate_results']['average_compound']
        
        print("\nTRADING SIGNAL BASED ON SENTIMENT:")
        print("-" * 35)
        if overall_sentiment == 'Positive' and avg_compound > 0.1:
            print("Signal: POTENTIAL LONG POSITION")
            print("Reason: Positive sentiment detected in Reuters news")
        elif overall_sentiment == 'Negative' and avg_compound < -0.1:
            print("Signal: POTENTIAL SHORT POSITION")
            print("Reason: Negative sentiment detected in Reuters news")
        else:
            print("Signal: NEUTRAL/NO CLEAR SIGNAL")
            print("Reason: Mixed or neutral sentiment detected")
    else:
        print("Failed to perform analysis. Please check:")
        print("1. Twitter API credentials are properly set")
        print("2. Internet connectivity")
        print("3. Required packages are installed")


if __name__ == "__main__":
    main()