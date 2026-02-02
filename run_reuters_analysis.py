#!/usr/bin/env python3
"""
Runner script for Reuters sentiment analysis
This script sets up the environment and runs the analysis
"""

import os
import sys
from datetime import datetime

def check_dependencies():
    """
    Check if required dependencies are available
    """
    missing_deps = []
    
    try:
        import tweepy
    except ImportError:
        missing_deps.append("tweepy")
    
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    except ImportError:
        missing_deps.append("vaderSentiment")
    
    try:
        import pandas
    except ImportError:
        missing_deps.append("pandas")
    
    return missing_deps

def main():
    print("Reuters Twitter Sentiment Analysis Runner")
    print("=" * 45)
    
    # Check dependencies
    missing_deps = check_dependencies()
    
    if missing_deps:
        print(f"Missing dependencies: {', '.join(missing_deps)}")
        print("\nTo install required packages, run:")
        print("pip install tweepy vaderSentiment pandas numpy requests")
        print("\nOr if using Python 3 specifically:")
        print("python3 -m pip install tweepy vaderSentiment pandas numpy requests")
        return
    
    # Import the tracker
    try:
        from reuters_sentiment_tracker import ReutersSentimentTracker
    except ImportError as e:
        print(f"Error importing ReutersSentimentTracker: {e}")
        print("Make sure all required files are in the workspace directory.")
        return
    
    # Check if Twitter credentials are set
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    if not bearer_token:
        print("TWITTER_BEARER_TOKEN environment variable not set!")
        print("Please set your Twitter API credentials before running this script.")
        print("Example: export TWITTER_BEARER_TOKEN='your_actual_token'")
        return
    
    print("Starting Reuters sentiment analysis...")
    
    # Initialize and run the tracker
    tracker = ReutersSentimentTracker()
    analysis_result = tracker.analyze_reuters_sentiment()
    
    if analysis_result:
        tracker.print_summary(analysis_result)
        
        # Save results
        filename = tracker.save_analysis(analysis_result)
        print(f"\nAnalysis completed at {datetime.now()}")
        print(f"Results saved to: {filename}")
    else:
        print("Analysis failed. Please check the error messages above.")

if __name__ == "__main__":
    main()