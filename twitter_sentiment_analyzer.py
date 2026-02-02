#!/usr/bin/env python3
"""
Twitter Sentiment Analyzer
Analyzes sentiment from tweets of specified accounts
"""

import json
import re
from datetime import datetime
import os

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("Warning: vaderSentiment not available. Install with: pip install vaderSentiment")

class TwitterSentimentAnalyzer:
    def __init__(self):
        if VADER_AVAILABLE:
            self.analyzer = SentimentIntensityAnalyzer()
        else:
            self.analyzer = None
            print("Using basic keyword-based sentiment analysis")
    
    def basic_sentiment_analysis(self, text):
        """
        Basic keyword-based sentiment analysis as fallback
        """
        positive_keywords = [
            'good', 'great', 'excellent', 'positive', 'up', 'rise', 'gain', 'profit', 
            'bull', 'buy', 'strong', 'success', 'recovery', 'optimistic', 'hopeful',
            'green', 'gains', 'soar', 'surge', 'boost', 'improve', 'recover', 'advance'
        ]
        
        negative_keywords = [
            'bad', 'terrible', 'poor', 'negative', 'down', 'fall', 'loss', 'crash',
            'bear', 'sell', 'weak', 'failure', 'decline', 'pessimistic', 'worried',
            'red', 'drops', 'plunge', 'drop', 'crisis', 'concern', 'downturn', 'fall'
        ]
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_keywords if word in text_lower)
        neg_count = sum(1 for word in negative_keywords if word in text_lower)
        
        # Calculate compound score (-1 to 1 scale)
        total_words = len(text.split())
        if total_words == 0:
            return {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0}
        
        # Normalize counts
        pos_score = min(pos_count / max(total_words * 0.01, 1), 1.0)
        neg_score = min(neg_count / max(total_words * 0.01, 1), 1.0)
        
        # Compound score (-1 to 1)
        compound = (pos_score - neg_score) / max(pos_score + neg_score, 1.0)
        
        # Distribute remaining score to neutral
        neu_score = max(0.0, 1.0 - abs(compound) - pos_score - neg_score)
        
        return {
            'compound': round(compound, 3),
            'pos': round(pos_score, 3),
            'neu': round(neu_score, 3),
            'neg': round(neg_score, 3)
        }
    
    def analyze_tweet_sentiment(self, tweet_text):
        """
        Analyze sentiment of a single tweet
        """
        if self.analyzer:
            # Use VADER sentiment analyzer
            scores = self.analyzer.polarity_scores(tweet_text)
            return scores
        else:
            # Fallback to basic keyword analysis
            return self.basic_sentiment_analysis(tweet_text)
    
    def analyze_tweets_batch(self, tweets):
        """
        Analyze sentiment for a batch of tweets
        Each tweet should be a dict with at least a 'text' field
        """
        results = []
        
        for tweet in tweets:
            text = tweet.get('text', '') if isinstance(tweet, dict) else str(tweet)
            sentiment = self.analyze_tweet_sentiment(text)
            
            result = {
                'text': text,
                'sentiment': sentiment,
                'classification': self.classify_sentiment(sentiment['compound'])
            }
            
            # If tweet is a dict with additional metadata, include it
            if isinstance(tweet, dict) and 'username' in tweet:
                result['username'] = tweet['username']
            if isinstance(tweet, dict) and 'created_at' in tweet:
                result['created_at'] = tweet['created_at']
            if isinstance(tweet, dict) and 'tweet_id' in tweet:
                result['tweet_id'] = tweet['tweet_id']
            
            results.append(result)
        
        return results
    
    def classify_sentiment(self, compound_score):
        """
        Classify sentiment based on compound score
        """
        if compound_score >= 0.05:
            return 'Positive'
        elif compound_score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    def aggregate_sentiment(self, sentiment_results):
        """
        Aggregate sentiment across multiple tweets
        """
        if not sentiment_results:
            return None
        
        total_compound = sum(r['sentiment']['compound'] for r in sentiment_results)
        avg_compound = total_compound / len(sentiment_results)
        
        positive_count = sum(1 for r in sentiment_results if r['sentiment']['compound'] >= 0.05)
        negative_count = sum(1 for r in sentiment_results if r['sentiment']['compound'] <= -0.05)
        neutral_count = len(sentiment_results) - positive_count - negative_count
        
        return {
            'average_compound': round(avg_compound, 3),
            'total_tweets': len(sentiment_results),
            'positive_tweets': positive_count,
            'negative_tweets': negative_count,
            'neutral_tweets': neutral_count,
            'sentiment_distribution': {
                'positive': round(positive_count / len(sentiment_results), 3),
                'negative': round(negative_count / len(sentiment_results), 3),
                'neutral': round(neutral_count / len(sentiment_results), 3)
            },
            'overall_sentiment': self.classify_sentiment(avg_compound)
        }


def main():
    """
    Main function to demonstrate sentiment analysis
    """
    print("Twitter Sentiment Analyzer")
    print("=" * 30)
    
    # Initialize the analyzer
    analyzer = TwitterSentimentAnalyzer()
    
    # Sample tweets from Reuters (these are examples - you would load actual tweets)
    sample_tweets = [
        "Markets rise as investors show optimism for economic recovery",
        "Global stocks fall amid concerns about inflation",
        "Bitcoin surges past $50,000 as institutional adoption grows",
        "Oil prices drop following OPEC meeting",
        "Tech stocks rally on strong earnings reports"
    ]
    
    print(f"Analyzing sentiment for {len(sample_tweets)} sample tweets from Reuters...")
    
    # Analyze sentiment
    results = analyzer.analyze_tweets_batch(sample_tweets)
    
    # Print individual results
    print("\nIndividual Tweet Analysis:")
    print("-" * 50)
    for i, result in enumerate(results, 1):
        print(f"{i}. Text: {result['text'][:60]}...")
        print(f"   Sentiment: {result['classification']} (Compound: {result['sentiment']['compound']})")
        print(f"   Pos: {result['sentiment']['pos']}, Neu: {result['sentiment']['neu']}, Neg: {result['sentiment']['neg']}")
        print()
    
    # Aggregate results
    aggregate = analyzer.aggregate_sentiment(results)
    print("Aggregate Sentiment Analysis:")
    print("-" * 50)
    print(f"Overall Sentiment: {aggregate['overall_sentiment']}")
    print(f"Average Compound Score: {aggregate['average_compound']}")
    print(f"Total Tweets Analyzed: {aggregate['total_tweets']}")
    print(f"Positive: {aggregate['positive_tweets']} ({aggregate['sentiment_distribution']['positive']*100:.1f}%)")
    print(f"Negative: {aggregate['negative_tweets']} ({aggregate['sentiment_distribution']['negative']*100:.1f}%)")
    print(f"Neutral: {aggregate['neutral_tweets']} ({aggregate['sentiment_distribution']['neutral']*100:.1f}%)")
    
    # Save results to file
    output_filename = f"reuters_sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump({
            'analysis_timestamp': datetime.now().isoformat(),
            'account_analyzed': 'Reuters',
            'individual_results': results,
            'aggregate_results': aggregate
        }, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\nAnalysis results saved to: {output_filename}")


if __name__ == "__main__":
    main()