#!/usr/bin/env python3
"""
AI-Powered Telegram Trading Bot - Main Entry Point
Similar to TradeMind bot for binary options trading signals
"""

import asyncio
import logging
import threading
import time
from datetime import datetime

from bot.telegram_bot import TradingBot
from ai.signal_generator import SignalGenerator
from web.dashboard import create_web_app
from utils.config import Config
from utils.logger import setup_logging

def run_web_dashboard():
    """Run the web dashboard in a separate thread"""
    try:
        app = create_web_app()
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except Exception as e:
        logging.error(f"Web dashboard error: {e}")

def run_signal_generator(signal_gen):
    """Run the signal generator in a separate thread"""
    try:
        while True:
            signal_gen.generate_automated_signals()
            time.sleep(Config.SIGNAL_GENERATION_INTERVAL)
    except Exception as e:
        logging.error(f"Signal generator error: {e}")

async def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logging.info("🚀 Starting AI-Powered Trading Bot (TradeMind Clone)")
    
    try:
        # Initialize components
        signal_generator = SignalGenerator()
        
        # Start web dashboard in separate thread
        web_thread = threading.Thread(target=run_web_dashboard, daemon=True)
        web_thread.start()
        logging.info("📊 Web dashboard started on port 5000")
        
        # Start signal generator in separate thread
        signal_thread = threading.Thread(
            target=run_signal_generator, 
            args=(signal_generator,), 
            daemon=True
        )
        signal_thread.start()
        logging.info("🤖 Automated signal generation started")
        
        # Check if Telegram bot token is configured
        if Config.TELEGRAM_BOT_TOKEN == '8045125371:AAHyV8-uE9QL6MCPy1pQv_l8rkU2OM90lEU':
            logging.warning("⚠️  Telegram bot token not configured. Web dashboard will run without Telegram bot.")
            logging.info("💻 Access the web dashboard at http://localhost:5000")
            logging.info("🔑 To enable Telegram bot, please set TELEGRAM_BOT_TOKEN environment variable")
            
            # Keep the application running for the web dashboard
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logging.info("🛑 Application stopped by user")
        else:
            # Start Telegram bot
            trading_bot = TradingBot(signal_generator)
            logging.info("📱 Starting Telegram bot...")
            await trading_bot.start()
        
    except KeyboardInterrupt:
        logging.info("🛑 Bot stopped by user")
    except Exception as e:
        logging.error(f"❌ Critical error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
