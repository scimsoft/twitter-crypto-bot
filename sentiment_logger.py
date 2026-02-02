import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path

class SentimentLogger:
    """
    Enhanced logging system for tracking sentiment scores per news feed
    """
    
    def __init__(self, log_file: str = "sentiment_by_feed_log.json"):
        self.log_file = log_file
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Setup logging configuration"""
        logger = logging.getLogger('SentimentByFeed')
        logger.setLevel(logging.INFO)
        
        # Create file handler for detailed logs
        fh = logging.FileHandler(f'sentiment_by_feed_detailed.log')
        fh.setLevel(logging.INFO)
        
        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        # Add handlers to logger
        if not logger.handlers:
            logger.addHandler(fh)
            logger.addHandler(ch)
            
        return logger
    
    def log_sentiment_per_feed(self, 
                              feed_sources: Dict[str, float], 
                              overall_sentiment: float,
                              timestamp: Optional[datetime] = None) -> None:
        """
        Log sentiment scores for each news feed source
        
        Args:
            feed_sources: Dictionary mapping feed names to their sentiment scores
            overall_sentiment: The aggregated sentiment score
            timestamp: Optional timestamp (uses current time if not provided)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        log_entry = {
            'timestamp': timestamp.isoformat(),
            'overall_sentiment': overall_sentiment,
            'feed_sentiments': feed_sources.copy(),
            'total_feeds_analyzed': len(feed_sources)
        }
        
        # Append to JSON log file
        self._append_to_json_log(log_entry)
        
        # Log to detailed log
        self.logger.info(f"Sentiment Analysis - Overall: {overall_sentiment:.3f}, Feeds analyzed: {len(feed_sources)}")
        for feed, score in feed_sources.items():
            self.logger.info(f"  {feed}: {score:.3f}")
    
    def _append_to_json_log(self, log_entry: dict) -> None:
        """Append log entry to JSON file"""
        log_path = Path(self.log_file)
        
        # Read existing logs if file exists
        existing_logs = []
        if log_path.exists():
            try:
                with open(log_path, 'r') as f:
                    existing_logs = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                existing_logs = []
        
        # Append new entry
        existing_logs.append(log_entry)
        
        # Write back to file
        with open(log_path, 'w') as f:
            json.dump(existing_logs, f, indent=2)
    
    def get_historical_analysis(self) -> pd.DataFrame:
        """
        Retrieve historical sentiment data for analysis
        
        Returns:
            DataFrame with columns: timestamp, overall_sentiment, and individual feed scores
        """
        log_path = Path(self.log_file)
        if not log_path.exists():
            return pd.DataFrame()
        
        try:
            with open(log_path, 'r') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return pd.DataFrame()
        
        # Convert logs to DataFrame
        rows = []
        for log in logs:
            row = {'timestamp': log['timestamp'], 'overall_sentiment': log['overall_sentiment']}
            for feed, score in log['feed_sentiments'].items():
                row[f'{feed}_sentiment'] = score
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def analyze_feed_patterns(self) -> Dict[str, Dict]:
        """
        Analyze patterns in feed sentiment scores
        
        Returns:
            Dictionary with statistics for each feed source
        """
        df = self.get_historical_analysis()
        if df.empty:
            return {}
        
        # Get all feed columns (those ending with '_sentiment')
        feed_cols = [col for col in df.columns if col.endswith('_sentiment')]
        
        patterns = {}
        for col in feed_cols:
            feed_name = col.replace('_sentiment', '')
            feed_data = df[col].dropna()
            
            if len(feed_data) > 0:
                patterns[feed_name] = {
                    'mean': float(feed_data.mean()),
                    'std': float(feed_data.std()),
                    'min': float(feed_data.min()),
                    'max': float(feed_data.max()),
                    'count': int(len(feed_data)),
                    'consistency_score': float(1 - feed_data.std() / (abs(feed_data.mean()) + 0.001)) if feed_data.mean() != 0 else 0
                }
        
        return patterns
    
    def print_pattern_summary(self) -> None:
        """Print a summary of feed sentiment patterns"""
        patterns = self.analyze_feed_patterns()
        
        if not patterns:
            print("No historical data available for pattern analysis.")
            return
        
        print("\n=== FEED SENTIMENT PATTERNS ANALYSIS ===")
        print(f"{'Feed Source':<30} {'Mean':<8} {'Std Dev':<8} {'Consistency':<12} {'Count':<6}")
        print("-" * 70)
        
        for feed, stats in sorted(patterns.items(), key=lambda x: x[1]['consistency_score'], reverse=True):
            print(f"{feed:<30} {stats['mean']:<8.3f} {stats['std']:<8.3f} {stats['consistency_score']:<12.3f} {stats['count']:<6}")
        
        print("\nConsistency Score Explanation:")
        print("- Close to 1.0: Highly consistent sentiment")
        print("- Close to 0.0: Highly variable sentiment")


# Example usage
if __name__ == "__main__":
    # Example of how to use the SentimentLogger
    logger = SentimentLogger()
    
    # Example feed sentiments
    sample_feeds = {
        "Reuters": 0.25,
        "BBC": -0.15,
        "CNN": 0.05,
        "AlJazeera": -0.10,
        "DW": 0.15
    }
    
    # Log the sentiment
    logger.log_sentiment_per_feed(sample_feeds, 0.04)
    
    # Print pattern analysis
    logger.print_pattern_summary()