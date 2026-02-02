# Changelog

All notable changes to the News-Based Crypto Trading Bot project will be documented in this file.

## [Unreleased] - YYYY-MM-DD

### Added
- Enhanced sentiment logging system that tracks sentiment scores per news feed
- Pattern analysis tool to identify consistency in feed sentiment
- Detailed logging for debugging and analysis
- Per-feed sentiment tracking in both JSON and text formats

### Changed
- Improved error handling for API failures
- Better logging structure for easier debugging
- More detailed status reporting

### Fixed
- Fixed issue with sentiment data not being properly recorded
- Improved reliability of news feed collection

## [1.1.0] - 2026-02-02

### Added
- Per-feed sentiment tracking system
- Analysis tools for identifying feed patterns
- Enhanced logging capabilities
- Pattern analysis functionality

### Changed
- Refactored sentiment analysis to support per-feed tracking
- Updated logging system to include detailed per-feed data
- Improved error handling for news feed collection

## [1.0.0] - 2026-01-31

### Added
- Initial Twitter Crypto Trading Bot implementation
- Sentiment analysis from Twitter and news feeds
- Automated trading based on sentiment thresholds
- Simulation mode for paper trading
- Basic logging and monitoring
- Cron job integration
- Trade history tracking

### Features
- Multi-coin support (starting with DOGE)
- Risk management controls
- 15-minute analysis cycles
- Twitter API integration
- News feed analysis
- Portfolio tracking
- Threshold-based trading logic

### Architecture
- Modular design with separate components
- Configuration via environment variables
- JSON-based trade history
- Error handling and logging