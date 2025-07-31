"""
Telegram Bot Implementation
Handles user interactions and signal delivery
"""

import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

from utils.config import Config
from bot.commands import BotCommands

class TradingBot:
    def __init__(self, signal_generator):
        self.signal_generator = signal_generator
        self.commands = BotCommands(signal_generator)
        self.subscribers = set()  # Users subscribed to auto signals
        self.app = None
        
    async def start(self):
        """Start the Telegram bot"""
        try:
            # Create application
            self.app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
            
            # Add command handlers
            self.app.add_handler(CommandHandler("start", self.start_command))
            self.app.add_handler(CommandHandler("help", self.help_command))
            self.app.add_handler(CommandHandler("signal", self.get_signal_command))
            self.app.add_handler(CommandHandler("pairs", self.list_pairs_command))
            self.app.add_handler(CommandHandler("subscribe", self.subscribe_command))
            self.app.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
            self.app.add_handler(CommandHandler("stats", self.stats_command))
            self.app.add_handler(CommandHandler("status", self.status_command))
            
            # Add callback query handler for inline keyboards
            self.app.add_handler(CallbackQueryHandler(self.button_callback))
            
            # Add message handler for general messages
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Start the bot
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
            
            logging.info("✅ Telegram bot is running...")
            
            # Keep the bot running
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            logging.error(f"❌ Failed to start Telegram bot: {e}")
            raise

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 **Welcome to AI Trading Bot!** 🤖

🎯 **Advanced AI-Powered Binary Options Signals**
📈 **90%+ Success Rate** | 🕒 **24/7 Live Signals**

**🚀 Available Commands:**
/signal - Get instant AI trading signal
/pairs - View supported currency pairs  
/subscribe - Auto-receive signals
/unsubscribe - Stop auto signals
/stats - View performance statistics
/status - Check bot status
/help - Show this help menu

**💡 Features:**
✅ Real-time market analysis
✅ AI-powered predictions
✅ Multi-currency support
✅ Risk assessment
✅ Optimal entry points
✅ Expiration recommendations

**🔥 Ready to start trading?**
Use /signal to get your first AI-generated signal!

*This bot is inspired by TradeMind AI*
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Get Signal", callback_data="get_signal")],
            [InlineKeyboardButton("📈 Subscribe to Auto Signals", callback_data="subscribe")],
            [InlineKeyboardButton("💰 View Pairs", callback_data="pairs")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📚 **AI Trading Bot Help Guide**

**🎯 Main Commands:**

/signal - Generate instant AI trading signal
• Get clear BUY or SELL recommendations
• Receive optimal entry point prices
• View risk assessment and expiration times

/pairs - View supported currency pairs
• EUR/CHF, AUD/JPY, GBP/USD and more
• See current market conditions
• Get pair-specific recommendations

/subscribe - Enable automatic signals
• Receive BUY/SELL signals every 5-15 minutes
• Get notifications for high-probability trades
• 24/7 automated signal delivery

/stats - Performance statistics
• View signal accuracy rates
• See historical performance
• Track success metrics

**💡 How it works:**
1. Our AI analyzes real-time market data
2. Machine learning models predict price movements
3. Risk assessment evaluates trade quality
4. You receive clear BUY/SELL signals with entry prices

**⚠️ Disclaimer:**
Trading involves risk. This bot provides educational signals only.
Always trade responsibly and never risk more than you can afford to lose.

Need more help? Contact @trademind_help
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def get_signal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /signal command - show time frame options"""
        try:
            # Create inline keyboard with time frame options
            keyboard = [
                [
                    InlineKeyboardButton("1 min", callback_data="signal_1m"),
                    InlineKeyboardButton("5 min", callback_data="signal_5m"),
                    InlineKeyboardButton("15 min", callback_data="signal_15m")
                ],
                [
                    InlineKeyboardButton("30 min", callback_data="signal_30m"),
                    InlineKeyboardButton("1 hour", callback_data="signal_1h"),
                    InlineKeyboardButton("4 hours", callback_data="signal_4h")
                ],
                [InlineKeyboardButton("📊 Quick Signal (Auto)", callback_data="signal_auto")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = """
🕒 **Choose Signal Timeframe**

Select your preferred expiration time for the trading signal:

⚡ **Short Term:** 1-5 minutes (High frequency)
📈 **Medium Term:** 15-30 minutes (Balanced)
📊 **Long Term:** 1-4 hours (Trend following)

**Quick Signal** uses AI to select optimal timeframe automatically.

After selecting timeframe, you can choose your preferred currency pair.
            """
            
            await update.message.reply_text(
                message, 
                reply_markup=reply_markup, 
                parse_mode='Markdown'
            )
                
        except Exception as e:
            logging.error(f"Error showing signal options: {e}")
            await update.message.reply_text("❌ Error showing signal options. Please try again later.")

    async def list_pairs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pairs command"""
        pairs_info = await self.commands.get_currency_pairs()
        await update.message.reply_text(pairs_info, parse_mode='Markdown')

    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command"""
        user_id = update.effective_user.id
        self.subscribers.add(user_id)
        
        message = """
✅ **Successfully Subscribed to Auto Signals!**

🔔 You will now receive:
• Automatic trading signals every 5-15 minutes
• High-probability trade opportunities
• Real-time market analysis updates
• AI-powered recommendations

📱 Signals will be delivered directly to this chat
⚡ Active 24/7 - even while you sleep!

Use /unsubscribe to stop auto signals anytime.
        """
        await update.message.reply_text(message, parse_mode='Markdown')

    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command"""
        user_id = update.effective_user.id
        self.subscribers.discard(user_id)
        
        await update.message.reply_text(
            "✅ Successfully unsubscribed from auto signals.\n"
            "You can still use /signal to get manual signals anytime!"
        )

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        stats = await self.commands.get_performance_stats()
        await update.message.reply_text(stats, parse_mode='Markdown')

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status = await self.commands.get_bot_status()
        await update.message.reply_text(status, parse_mode='Markdown')

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "get_signal":
            # Show timeframe options
            keyboard = [
                [
                    InlineKeyboardButton("1 min", callback_data="signal_1m"),
                    InlineKeyboardButton("5 min", callback_data="signal_5m"),
                    InlineKeyboardButton("15 min", callback_data="signal_15m")
                ],
                [
                    InlineKeyboardButton("30 min", callback_data="signal_30m"),
                    InlineKeyboardButton("1 hour", callback_data="signal_1h"),
                    InlineKeyboardButton("4 hours", callback_data="signal_4h")
                ],
                [InlineKeyboardButton("📊 Quick Signal (Auto)", callback_data="signal_auto")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🕒 **Choose Signal Timeframe:**\n\n"
                "⚡ **Short:** 1-5 min (High frequency)\n"
                "📈 **Medium:** 15-30 min (Balanced)\n"
                "📊 **Long:** 1-4 hours (Trend following)",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        elif query.data.startswith("signal_"):
            # Store timeframe and show pair selection
            timeframe = query.data.replace("signal_", "")
            context.user_data['selected_timeframe'] = timeframe
            await self._show_pair_selection(query, context)
            
        elif query.data.startswith("pair_"):
            # Handle pair selection and generate signal
            pair = query.data.replace("pair_", "").replace("_", "/")
            timeframe = context.user_data.get('selected_timeframe', 'auto')
            await self.generate_signal_with_timeframe_and_pair(query, context, timeframe, pair)
                
        elif query.data == "subscribe":
            user_id = query.from_user.id
            self.subscribers.add(user_id)
            await query.edit_message_text(
                "✅ Successfully subscribed to auto signals!\n"
                "You'll receive AI-powered trading signals automatically."
            )
            
        elif query.data == "pairs":
            pairs_info = await self.commands.get_currency_pairs()
            await query.edit_message_text(pairs_info, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle general text messages"""
        text = update.message.text.lower()
        
        if any(word in text for word in ['signal', 'trade', 'buy', 'sell']):
            await update.message.reply_text(
                "💡 Use /signal to get an AI-powered trading signal!\n"
                "Or /subscribe for automatic signals every few minutes."
            )
        elif any(word in text for word in ['help', 'how', 'what']):
            await update.message.reply_text(
                "📚 Use /help to see all available commands and features!"
            )
        else:
            await update.message.reply_text(
                "🤖 I'm an AI trading bot! Use /help to see what I can do for you."
            )

    async def _show_pair_selection(self, query, context):
        """Show currency pair selection options"""
        try:
            # Create keyboard with popular currency pairs
            keyboard = [
                [
                    InlineKeyboardButton("EUR/USD", callback_data="pair_EUR_USD"),
                    InlineKeyboardButton("GBP/USD", callback_data="pair_GBP_USD"),
                    InlineKeyboardButton("USD/JPY", callback_data="pair_USD_JPY")
                ],
                [
                    InlineKeyboardButton("AUD/USD", callback_data="pair_AUD_USD"),
                    InlineKeyboardButton("EUR/GBP", callback_data="pair_EUR_GBP"),
                    InlineKeyboardButton("EUR/JPY", callback_data="pair_EUR_JPY")
                ],
                [
                    InlineKeyboardButton("GBP/JPY", callback_data="pair_GBP_JPY"),
                    InlineKeyboardButton("USD/CHF", callback_data="pair_USD_CHF"),
                    InlineKeyboardButton("NZD/USD", callback_data="pair_NZD_USD")
                ],
                [
                    InlineKeyboardButton("EUR/CHF", callback_data="pair_EUR_CHF"),
                    InlineKeyboardButton("AUD/JPY", callback_data="pair_AUD_JPY"),
                    InlineKeyboardButton("CAD/JPY", callback_data="pair_CAD_JPY")
                ],
                [InlineKeyboardButton("🎲 Auto Select (AI Chooses)", callback_data="pair_AUTO")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            timeframe = context.user_data.get('selected_timeframe', 'auto')
            timeframe_display = {"1m": "1 minute", "5m": "5 minutes", "15m": "15 minutes", 
                               "30m": "30 minutes", "1h": "1 hour", "4h": "4 hours", "auto": "Auto"}.get(timeframe, timeframe)
            
            message = f"""
💱 **Choose Currency Pair**

Selected timeframe: **{timeframe_display}**

Select your preferred currency pair for the trading signal:

🌟 **Major Pairs:** EUR/USD, GBP/USD, USD/JPY
📈 **Cross Pairs:** EUR/GBP, GBP/JPY, EUR/JPY  
⚡ **Volatile Pairs:** AUD/JPY, GBP/JPY, EUR/CHF

Let AI auto-select the most optimal pair based on current market conditions.
            """
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logging.error(f"Error showing pair selection: {e}")
            await query.edit_message_text("❌ Error showing pair options. Please try again.")

    async def generate_signal_with_timeframe_and_pair(self, query, context, timeframe, pair):
        """Generate signal with specific timeframe and pair"""
        try:
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
            
            # Map timeframe codes to minutes
            timeframe_map = {
                "1m": 1, "5m": 5, "15m": 15, "30m": 30,
                "1h": 60, "4h": 240, "auto": None
            }
            
            expiration_minutes = timeframe_map.get(timeframe, None)
            selected_pair = None if pair == "AUTO" else pair
            
            # Generate signal with specific timeframe and pair
            signal = await self.commands.generate_signal_with_timeframe_and_pair(expiration_minutes, selected_pair)
            
            if signal:
                await self.send_formatted_signal(query.message.chat_id, signal, context)
            else:
                await query.edit_message_text("❌ Unable to generate signal at this time. Please try again later.")
                
        except Exception as e:
            logging.error(f"Error generating signal with timeframe {timeframe} and pair {pair}: {e}")
            await query.edit_message_text("❌ Error generating signal. Please try again later.")

    async def generate_signal_with_timeframe(self, query, context, timeframe):
        """Generate signal with specific timeframe (legacy method)"""
        try:
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
            
            # Map timeframe codes to minutes
            timeframe_map = {
                "1m": 1,
                "5m": 5,
                "15m": 15,
                "30m": 30,
                "1h": 60,
                "4h": 240,
                "auto": None  # Let AI choose optimal timeframe
            }
            
            expiration_minutes = timeframe_map.get(timeframe, None)
            
            # Generate signal with specific timeframe
            signal = await self.commands.generate_signal_with_timeframe(expiration_minutes)
            
            if signal:
                await self.send_formatted_signal(query.message.chat_id, signal, context)
            else:
                await query.edit_message_text("❌ Unable to generate signal at this time. Please try again later.")
                
        except Exception as e:
            logging.error(f"Error generating signal with timeframe {timeframe}: {e}")
            await query.edit_message_text("❌ Error generating signal. Please try again later.")

    async def send_formatted_signal(self, chat_id, signal, context):
        """Send a beautifully formatted trading signal"""
        # Convert CALL/PUT to BUY/SELL terminology with enhanced visuals
        if signal['direction'] == 'CALL':
            # Green background effect for BUY
            action_header = "🟢🟢🟢 **B U Y** 🟢🟢🟢"
            action_text = "📈 **Action:** 🔥 **BUY** 🔥"
            direction_banner = "🚀💚 **BULLISH SIGNAL** 💚🚀"
            action_emoji = "⬆️💹"
        else:
            # Red background effect for SELL  
            action_header = "🔴🔴🔴 **S E L L** 🔴🔴🔴"
            action_text = "📉 **Action:** 🎯 **SELL** 🎯"
            direction_banner = "⚡🔻 **BEARISH SIGNAL** 🔻⚡"
            action_emoji = "⬇️📉"
        
        # Enhanced risk level display
        risk_emojis = {
            "LOW": "🟢🛡️ LOW RISK 🛡️🟢", 
            "MEDIUM": "🟡⚠️ MEDIUM RISK ⚠️🟡", 
            "HIGH": "🔴🚨 HIGH RISK 🚨🔴"
        }
        risk_display = risk_emojis.get(signal['risk_level'], "⚪ UNKNOWN RISK")
        
        # Enhanced confidence bar with colors
        confidence = signal['confidence']
        if confidence >= 80:
            confidence_color = "🟢"
            confidence_desc = "VERY HIGH"
        elif confidence >= 70:
            confidence_color = "🟡"
            confidence_desc = "HIGH"
        elif confidence >= 60:
            confidence_color = "🟠"
            confidence_desc = "MEDIUM"
        else:
            confidence_color = "🔴"
            confidence_desc = "LOW"
            
        confidence_bar = "█" * int(confidence / 10) + "░" * (10 - int(confidence / 10))
        
        signal_message = f"""
🎯 **AI TRADING SIGNAL** 🎯
{'='*30}

{action_header}
{direction_banner}

💱 **PAIR:** `{signal['pair']}`
{action_text} {action_emoji}

💰 **Entry Price:** `${signal['entry_price']:.5f}`
⏰ **Expiration:** `{signal['expiration_minutes']} minutes`

{confidence_color} **Confidence:** {confidence}% ({confidence_desc})
`{confidence_bar}`

⚠️ **Risk Level:** {risk_display}

📊 **AI Analysis:**
_{signal['analysis']}_

🕒 **Generated:** {signal['timestamp']}
{'='*30}
*⚡ Trade wisely | Not financial advice*
        """
        
        # Add inline keyboard for quick actions
        keyboard = [
            [InlineKeyboardButton("📊 New Signal", callback_data="get_signal")],
            [InlineKeyboardButton("📈 Subscribe", callback_data="subscribe")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=chat_id, 
            text=signal_message, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def broadcast_signal_to_subscribers(self, signal):
        """Broadcast signal to all subscribers"""
        if not self.subscribers:
            return
            
        for user_id in self.subscribers.copy():  # Use copy to avoid modification during iteration
            try:
                await self.send_formatted_signal(user_id, signal, self.app.bot)
            except Exception as e:
                logging.warning(f"Failed to send signal to user {user_id}: {e}")
                # Remove user if they blocked the bot
                if "blocked" in str(e).lower():
                    self.subscribers.discard(user_id)
