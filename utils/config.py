"""
Configuration Management
Central configuration for the trading bot
"""

import os
from typing import Dict, List

class Config:
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8045125371:AAHyV8-uE9QL6MCPy1pQv_l8rkU2OM90lEU')
    
    # API Keys for Market Data
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
    YAHOO_FINANCE_API_KEY = os.getenv('YAHOO_FINANCE_API_KEY', 'demo')
    FOREX_API_KEY = os.getenv('FOREX_API_KEY', 'demo')
    
    # Signal Generation Settings
    SIGNAL_GENERATION_INTERVAL = int(os.getenv('SIGNAL_GENERATION_INTERVAL', '600'))  # 10 minutes
    MIN_SIGNAL_CONFIDENCE = float(os.getenv('MIN_SIGNAL_CONFIDENCE', '70.0'))
    MAX_SIGNALS_PER_HOUR = int(os.getenv('MAX_SIGNALS_PER_HOUR', '8'))
    
    # AI Model Settings
    AI_MODEL_CONFIDENCE_THRESHOLD = float(os.getenv('AI_MODEL_CONFIDENCE_THRESHOLD', '65.0'))
    ML_PREDICTION_TIMEOUT = int(os.getenv('ML_PREDICTION_TIMEOUT', '30'))  # seconds
    
    # Trading Pairs Configuration
    SUPPORTED_PAIRS = [
        'EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'EUR/CHF', 
        'AUD/JPY', 'GBP/JPY', 'EUR/GBP', 'NZD/USD', 'USD/CHF',
        'USD/CAD', 'EUR/JPY'
    ]
    
    # Risk Management
    DEFAULT_RISK_LEVEL = os.getenv('DEFAULT_RISK_LEVEL', 'MEDIUM')
    MAX_DAILY_SIGNALS = int(os.getenv('MAX_DAILY_SIGNALS', '50'))
    
    # Cache Settings
    MARKET_DATA_CACHE_TTL = int(os.getenv('MARKET_DATA_CACHE_TTL', '30'))  # seconds
    ANALYSIS_CACHE_TTL = int(os.getenv('ANALYSIS_CACHE_TTL', '300'))  # 5 minutes
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Web Dashboard Settings
    WEB_PORT = int(os.getenv('WEB_PORT', '5000'))
    WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
    WEB_DEBUG = os.getenv('WEB_DEBUG', 'False').lower() == 'true'
    
    # Market Session Times (UTC)
    MARKET_SESSIONS = {
        'asian': {'start': 23, 'end': 8},
        'european': {'start': 8, 'end': 17},
        'us': {'start': 13, 'end': 22}
    }
    
    # Trading Platform Settings
    BINARY_OPTIONS_PLATFORMS = [
        'Pocket Option',
        'Quotex', 
        'IQ Option',
        'Olymp Trade',
        'Binomo'
    ]
    
    # Expiration Times (in minutes)
    EXPIRATION_TIMES = {
        'scalping': [1, 2, 3, 5],
        'short_term': [5, 10, 15, 20],
        'medium_term': [20, 30, 45, 60],
        'long_term': [60, 120, 180, 240]
    }
    
    # Performance Tracking
    TRACK_SIGNAL_PERFORMANCE = os.getenv('TRACK_SIGNAL_PERFORMANCE', 'True').lower() == 'true'
    PERFORMANCE_HISTORY_DAYS = int(os.getenv('PERFORMANCE_HISTORY_DAYS', '30'))
    
    # Notification Settings
    ENABLE_PERFORMANCE_ALERTS = os.getenv('ENABLE_PERFORMANCE_ALERTS', 'True').lower() == 'true'
    LOW_ACCURACY_THRESHOLD = float(os.getenv('LOW_ACCURACY_THRESHOLD', '75.0'))
    
    # Feature Flags
    ENABLE_ML_PREDICTIONS = os.getenv('ENABLE_ML_PREDICTIONS', 'True').lower() == 'true'
    ENABLE_TECHNICAL_ANALYSIS = os.getenv('ENABLE_TECHNICAL_ANALYSIS', 'True').lower() == 'true'
    ENABLE_SENTIMENT_ANALYSIS = os.getenv('ENABLE_SENTIMENT_ANALYSIS', 'True').lower() == 'true'
    ENABLE_PATTERN_RECOGNITION = os.getenv('ENABLE_PATTERN_RECOGNITION', 'True').lower() == 'true'
    
    # Rate Limiting
    API_RATE_LIMIT_PER_MINUTE = int(os.getenv('API_RATE_LIMIT_PER_MINUTE', '60'))
    USER_COMMAND_RATE_LIMIT = int(os.getenv('USER_COMMAND_RATE_LIMIT', '10'))  # per minute
    
    # Database Settings (if needed in future)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///trading_bot.db')
    
    @classmethod
    def get_trading_session_info(cls) -> Dict:
        """Get current trading session information"""
        from datetime import datetime
        
        current_hour = datetime.now().hour
        active_sessions = []
        
        for session, times in cls.MARKET_SESSIONS.items():
            if times['start'] <= times['end']:
                # Normal session (doesn't cross midnight)
                if times['start'] <= current_hour < times['end']:
                    active_sessions.append(session)
            else:
                # Session crosses midnight (like Asian session)
                if current_hour >= times['start'] or current_hour < times['end']:
                    active_sessions.append(session)
        
        return {
            'current_hour': current_hour,
            'active_sessions': active_sessions,
            'is_peak_time': len(active_sessions) >= 2,
            'next_session_change': cls._get_next_session_change(current_hour)
        }
    
    @classmethod
    def _get_next_session_change(cls, current_hour: int) -> int:
        """Calculate hours until next session change"""
        session_changes = [8, 13, 17, 23]  # Session start/end times
        
        for change_hour in session_changes:
            if current_hour < change_hour:
                return change_hour - current_hour
        
        # Next change is tomorrow's first session
        return 24 - current_hour + session_changes[0]
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        if cls.TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
            issues.append("Telegram bot token not configured")
        
        if cls.MIN_SIGNAL_CONFIDENCE < 50 or cls.MIN_SIGNAL_CONFIDENCE > 95:
            issues.append("MIN_SIGNAL_CONFIDENCE should be between 50-95")
        
        if cls.SIGNAL_GENERATION_INTERVAL < 60:
            issues.append("SIGNAL_GENERATION_INTERVAL should be at least 60 seconds")
        
        if not cls.SUPPORTED_PAIRS:
            issues.append("No supported trading pairs configured")
        
        return issues
    
    @classmethod
    def get_config_summary(cls) -> Dict:
        """Get a summary of current configuration"""
        return {
            'bot_configured': cls.TELEGRAM_BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE',
            'supported_pairs_count': len(cls.SUPPORTED_PAIRS),
            'signal_interval_minutes': cls.SIGNAL_GENERATION_INTERVAL // 60,
            'min_confidence': cls.MIN_SIGNAL_CONFIDENCE,
            'ml_enabled': cls.ENABLE_ML_PREDICTIONS,
            'web_port': cls.WEB_PORT,
            'log_level': cls.LOG_LEVEL
        }
