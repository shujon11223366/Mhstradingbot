# replit.md

## Overview

This is an AI-powered Telegram trading bot that generates binary options trading signals using machine learning models and technical analysis. The bot is designed similar to TradeMind bot, providing automated trading signals through Telegram while offering a web dashboard for monitoring performance.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Web Dashboard**: Flask-based web application with Bootstrap UI
- **Static Assets**: CSS/JavaScript files for interactive dashboard
- **Real-time Updates**: JavaScript-based auto-refresh functionality with 30-second intervals
- **Responsive Design**: Mobile-friendly interface using Bootstrap framework

### Backend Architecture
- **Main Application**: Python asyncio-based main loop coordinating all components
- **Telegram Bot**: python-telegram-bot library handling user interactions
- **AI Engine**: Multi-layered AI system with market analysis and ML predictions
- **Threading Model**: Separate threads for web dashboard and signal generation

### AI/ML Components
- **Signal Generator**: Core AI engine coordinating analysis and predictions
- **Market Analyzer**: Technical analysis using indicators and pattern recognition
- **ML Models**: RandomForestClassifier models for different time horizons
- **Feature Engineering**: Extracts trading features from market data and analysis

## Key Components

### 1. Telegram Bot (`bot/`)
- **TradingBot**: Main bot class handling user interactions
- **BotCommands**: Command processing and response generation
- **Features**: Signal generation, subscription management, pair listings, statistics

### 2. AI Engine (`ai/`)
- **SignalGenerator**: Orchestrates market analysis and ML predictions
- **MarketAnalyzer**: Technical analysis, trend detection, volatility analysis
- **MLPredictor**: Machine learning models for price direction prediction

### 3. Data Management (`data/`)
- **MarketDataProvider**: Real-time market data from multiple APIs (Alpha Vantage, Yahoo Finance)
- **CurrencyPairs**: Currency pair management and market session tracking
- **Caching**: Time-based caching for market data and analysis results

### 4. Storage (`storage/`)
- **SignalHistory**: JSON-based signal storage with performance tracking
- **File-based Storage**: Persistent storage using JSON files
- **Performance Metrics**: Win/loss tracking and statistical analysis

### 5. Web Dashboard (`web/`, `templates/`, `static/`)
- **Flask Application**: RESTful API endpoints for dashboard data
- **Real-time Monitoring**: Live statistics and signal history
- **Interactive Charts**: Chart.js integration for data visualization

### 6. Utilities (`utils/`)
- **Configuration**: Environment-based configuration management
- **Logging**: Centralized logging with rotating file handlers

## Data Flow

1. **Signal Generation Flow**:
   - Market data fetched from external APIs
   - Technical analysis performed on price data
   - ML models predict price direction
   - Signal created with confidence scoring
   - Signal distributed via Telegram and stored in history

2. **User Interaction Flow**:
   - Telegram commands trigger bot responses
   - Bot queries AI engine for new signals
   - Real-time data displayed in web dashboard
   - Performance metrics calculated and cached

3. **Data Persistence Flow**:
   - Signals stored in JSON format
   - Market data cached temporarily
   - Performance statistics calculated on-demand
   - Log files rotated automatically

## External Dependencies

### APIs and Services
- **Telegram Bot API**: User interaction and message delivery
- **Alpha Vantage API**: Primary market data source
- **Yahoo Finance API**: Secondary market data source
- **Exchange Rate API**: Fallback market data source

### Python Libraries
- **Machine Learning**: scikit-learn, numpy
- **Web Framework**: Flask
- **Telegram Integration**: python-telegram-bot
- **HTTP Requests**: requests library
- **Async Processing**: asyncio

### Data Sources
- **Real-time Market Data**: Multiple API providers with fallback mechanisms
- **Currency Pair Information**: Static configuration with dynamic updates
- **Technical Indicators**: Calculated from price data

## Deployment Strategy

### Environment Configuration
- **Environment Variables**: All sensitive data (API keys, tokens) via env vars
- **Configuration Management**: Centralized config class with defaults
- **Multi-environment Support**: Development/production configurations

### Application Structure
- **Single Entry Point**: main.py orchestrates all components
- **Modular Design**: Separate modules for AI, bot, web, and utilities
- **Threading**: Web dashboard and signal generation run in separate threads
- **Error Handling**: Comprehensive exception handling with logging

### Scalability Considerations
- **Caching Strategy**: Multiple cache layers for performance
- **Rate Limiting**: Configurable signal generation intervals
- **Resource Management**: Automatic cleanup and rotation of logs/data
- **Monitoring**: Web dashboard provides real-time system health

### Storage Requirements
- **File System**: JSON files for signal history and configuration
- **Logs Directory**: Rotating log files with size limits
- **Static Assets**: CSS/JS files for web interface
- **No Database**: Currently uses file-based storage (Drizzle/Postgres can be added later)

## Notes

- The application uses JSON file storage but is structured to easily accommodate database integration
- Signal generation intervals and confidence thresholds are configurable
- The system includes comprehensive error handling and fallback mechanisms
- Web dashboard provides real-time monitoring without requiring database setup