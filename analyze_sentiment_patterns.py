#!/usr/bin/env python3
"""
Script to analyze sentiment logs and identify patterns per news feed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sentiment_logger import SentimentLogger

def main():
    print("Analyzing sentiment patterns by news feed...")
    
    # Create logger instance to access historical data
    logger = SentimentLogger()
    
    # Print pattern summary
    logger.print_pattern_summary()
    
    # Additional analysis could be added here
    print("\nFor more detailed analysis, you can use the SentimentLogger class:")
    print("- logger.get_historical_analysis() to get a DataFrame of all logs")
    print("- logger.analyze_feed_patterns() to get statistics per feed")

if __name__ == "__main__":
    main()
