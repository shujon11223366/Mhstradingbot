"""
Logging Configuration
Centralized logging setup for the trading bot
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from utils.config import Config

def setup_logging():
    """Setup logging configuration for the application"""
    try:
        # Create logs directory if it doesn't exist
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
        
        # Clear any existing handlers
        root_logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler for general logs
        general_log_file = os.path.join(log_dir, 'trading_bot.log')
        file_handler = RotatingFileHandler(
            general_log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
        
        # Error log handler
        error_log_file = os.path.join(log_dir, 'errors.log')
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # Signal log handler (for tracking trading signals)
        signal_log_file = os.path.join(log_dir, 'signals.log')
        signal_handler = RotatingFileHandler(
            signal_log_file,
            maxBytes=20*1024*1024,  # 20MB
            backupCount=10
        )
        signal_handler.setLevel(logging.INFO)
        signal_handler.setFormatter(detailed_formatter)
        
        # Create signal logger
        signal_logger = logging.getLogger('signals')
        signal_logger.addHandler(signal_handler)
        signal_logger.setLevel(logging.INFO)
        signal_logger.propagate = False  # Don't propagate to root logger
        
        # Performance log handler
        performance_log_file = os.path.join(log_dir, 'performance.log')
        performance_handler = RotatingFileHandler(
            performance_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        performance_handler.setLevel(logging.INFO)
        performance_handler.setFormatter(detailed_formatter)
        
        # Create performance logger
        performance_logger = logging.getLogger('performance')
        performance_logger.addHandler(performance_handler)
        performance_logger.setLevel(logging.INFO)
        performance_logger.propagate = False
        
        # Configure specific loggers
        configure_module_loggers()
        
        # Log startup message
        logging.info("=" * 50)
        logging.info("🤖 AI Trading Bot - Logging System Initialized")
        logging.info(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"📝 Log level: {Config.LOG_LEVEL}")
        logging.info(f"📁 Log directory: {os.path.abspath(log_dir)}")
        logging.info("=" * 50)
        
    except Exception as e:
        # Fallback to basic logging if setup fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        logging.error(f"Failed to setup advanced logging: {e}")

def configure_module_loggers():
    """Configure logging levels for specific modules"""
    try:
        # Telegram bot library - reduce verbosity
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('telegram').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        
        # Our module loggers
        logging.getLogger('bot').setLevel(logging.INFO)
        logging.getLogger('ai').setLevel(logging.INFO)
        logging.getLogger('data').setLevel(logging.INFO)
        logging.getLogger('utils').setLevel(logging.INFO)
        
        # Set DEBUG level for development if needed
        if Config.LOG_LEVEL.upper() == 'DEBUG':
            logging.getLogger('ai.signal_generator').setLevel(logging.DEBUG)
            logging.getLogger('ai.market_analyzer').setLevel(logging.DEBUG)
            logging.getLogger('data.market_data').setLevel(logging.DEBUG)
        
    except Exception as e:
        logging.error(f"Error configuring module loggers: {e}")

def log_signal_generated(signal_data: dict):
    """Log when a trading signal is generated"""
    try:
        signal_logger = logging.getLogger('signals')
        
        log_message = (
            f"SIGNAL_GENERATED | "
            f"Pair: {signal_data.get('pair', 'Unknown')} | "
            f"Direction: {signal_data.get('direction', 'Unknown')} | "
            f"Confidence: {signal_data.get('confidence', 0)}% | "
            f"Entry: {signal_data.get('entry_price', 0)} | "
            f"Expiration: {signal_data.get('expiration_minutes', 0)}min | "
            f"Risk: {signal_data.get('risk_level', 'Unknown')} | "
            f"ID: {signal_data.get('signal_id', 'Unknown')}"
        )
        
        signal_logger.info(log_message)
        
    except Exception as e:
        logging.error(f"Error logging signal: {e}")

def log_signal_performance(signal_id: str, actual_outcome: str, profit_loss: float = None):
    """Log the performance outcome of a trading signal"""
    try:
        performance_logger = logging.getLogger('performance')
        
        log_message = (
            f"SIGNAL_OUTCOME | "
            f"ID: {signal_id} | "
            f"Outcome: {actual_outcome} | "
            f"P&L: {profit_loss if profit_loss is not None else 'N/A'}"
        )
        
        performance_logger.info(log_message)
        
    except Exception as e:
        logging.error(f"Error logging signal performance: {e}")

def log_user_interaction(user_id: int, username: str, command: str, success: bool = True):
    """Log user interactions with the bot"""
    try:
        interaction_logger = logging.getLogger('interactions')
        
        status = "SUCCESS" if success else "FAILED"
        log_message = (
            f"USER_INTERACTION | "
            f"User: {user_id} (@{username or 'unknown'}) | "
            f"Command: {command} | "
            f"Status: {status}"
        )
        
        logging.info(log_message)
        
    except Exception as e:
        logging.error(f"Error logging user interaction: {e}")

def log_api_call(api_name: str, endpoint: str, response_time: float, success: bool = True):
    """Log API calls for monitoring"""
    try:
        api_logger = logging.getLogger('api_calls')
        
        status = "SUCCESS" if success else "FAILED"
        log_message = (
            f"API_CALL | "
            f"Service: {api_name} | "
            f"Endpoint: {endpoint} | "
            f"Response Time: {response_time:.3f}s | "
            f"Status: {status}"
        )
        
        logging.info(log_message)
        
    except Exception as e:
        logging.error(f"Error logging API call: {e}")

def log_error_with_context(error: Exception, context: dict = None):
    """Log errors with additional context information"""
    try:
        error_msg = f"ERROR: {str(error)}"
        
        if context:
            context_str = " | ".join([f"{k}: {v}" for k, v in context.items()])
            error_msg += f" | Context: {context_str}"
        
        logging.error(error_msg, exc_info=True)
        
    except Exception as e:
        logging.error(f"Error logging error with context: {e}")

def get_log_statistics():
    """Get statistics about log files"""
    try:
        log_dir = "logs"
        stats = {}
        
        if os.path.exists(log_dir):
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    filepath = os.path.join(log_dir, filename)
                    try:
                        file_size = os.path.getsize(filepath)
                        file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                        
                        stats[filename] = {
                            'size_mb': round(file_size / (1024 * 1024), 2),
                            'last_modified': file_modified.strftime('%Y-%m-%d %H:%M:%S'),
                            'exists': True
                        }
                    except Exception as e:
                        stats[filename] = {
                            'error': str(e),
                            'exists': False
                        }
        
        return stats
        
    except Exception as e:
        logging.error(f"Error getting log statistics: {e}")
        return {}

class TradingBotLogger:
    """Custom logger class for the trading bot with specialized methods"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context"""
        if kwargs:
            context = " | ".join([f"{k}: {v}" for k, v in kwargs.items()])
            message += f" | {context}"
        self.logger.info(message)
    
    def error(self, message: str, error: Exception = None, **kwargs):
        """Log error message with optional exception and context"""
        if kwargs:
            context = " | ".join([f"{k}: {v}" for k, v in kwargs.items()])
            message += f" | {context}"
        
        if error:
            self.logger.error(f"{message} | Error: {str(error)}", exc_info=True)
        else:
            self.logger.error(message)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context"""
        if kwargs:
            context = " | ".join([f"{k}: {v}" for k, v in kwargs.items()])
            message += f" | {context}"
        self.logger.debug(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context"""
        if kwargs:
            context = " | ".join([f"{k}: {v}" for k, v in kwargs.items()])
            message += f" | {context}"
        self.logger.warning(message)

# Factory function to create specialized loggers
def get_logger(name: str) -> TradingBotLogger:
    """Get a specialized logger instance"""
    return TradingBotLogger(name)
