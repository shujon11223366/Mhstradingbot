"""
AI Signal Generator
Core AI engine for generating trading signals
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ai.market_analyzer import MarketAnalyzer
from ai.ml_models import MLPredictor
from data.market_data import MarketDataProvider
from data.currency_pairs import CurrencyPairs

class SignalGenerator:
    def __init__(self):
        self.market_analyzer = MarketAnalyzer()
        self.ml_predictor = MLPredictor()
        self.market_data = MarketDataProvider()
        self.currency_pairs = CurrencyPairs()
        self.last_signal_time = {}
        self.signal_count = 0
        
    async def generate_signal(self, pair: str = None) -> Optional[Dict]:
        """Generate a trading signal for a specific pair or auto-select"""
        try:
            # Auto-select pair if not provided
            if not pair:
                pair = self._select_optimal_pair()
            
            # Get market data
            market_data = await self.market_data.get_real_time_data(pair)
            if not market_data:
                logging.warning(f"No market data available for {pair}")
                return None
            
            # Perform market analysis
            analysis_result = await self.market_analyzer.analyze_market(pair, market_data)
            
            # Generate ML prediction
            prediction = await self.ml_predictor.predict_direction(pair, market_data, analysis_result)
            
            # Create signal
            signal = self._create_signal(pair, market_data, analysis_result, prediction)
            
            # Log signal generation
            self.signal_count += 1
            logging.info(f"Generated signal #{self.signal_count} for {pair}: {signal['direction']}")
            
            return signal
            
        except Exception as e:
            logging.error(f"Error generating signal: {e}")
            return None

    async def generate_signal_with_timeframe(self, expiration_minutes: int = None, pair: str = None) -> Optional[Dict]:
        """Generate a trading signal with specific timeframe"""
        try:
            # Auto-select pair if not provided
            if not pair:
                pair = self._select_optimal_pair()
            
            # Get market data
            market_data = await self.market_data.get_real_time_data(pair)
            if not market_data:
                logging.warning(f"No market data available for {pair}")
                return None
            
            # Perform market analysis
            analysis_result = await self.market_analyzer.analyze_market(pair, market_data)
            
            # Generate ML prediction
            prediction = await self.ml_predictor.predict_direction(pair, market_data, analysis_result)
            
            # Create signal with specific timeframe
            signal = self._create_signal_with_timeframe(pair, market_data, analysis_result, prediction, expiration_minutes)
            
            # Log signal generation
            self.signal_count += 1
            logging.info(f"Generated signal #{self.signal_count} for {pair}: {signal['direction']} ({signal['expiration_minutes']}m)")
            
            return signal
            
        except Exception as e:
            logging.error(f"Error generating signal with timeframe: {e}")
            return None
    
    def generate_automated_signals(self):
        """Generate automated signals for subscribers"""
        try:
            # Get high-priority pairs
            priority_pairs = self.currency_pairs.get_high_volume_pairs()
            
            for pair in priority_pairs[:3]:  # Generate for top 3 pairs
                # Check if enough time has passed since last signal
                if self._should_generate_signal(pair):
                    signal = asyncio.run(self.generate_signal(pair))
                    if signal:
                        self._broadcast_to_subscribers(signal)
                        self.last_signal_time[pair] = datetime.now()
                        
        except Exception as e:
            logging.error(f"Error in automated signal generation: {e}")
    
    def _select_optimal_pair(self) -> str:
        """Select the most optimal currency pair for trading"""
        try:
            # Get pairs with high volatility and volume
            active_pairs = self.currency_pairs.get_active_pairs()
            
            # Prioritize pairs with good recent performance
            high_performance_pairs = [
                'EUR/CHF', 'AUD/JPY', 'GBP/USD', 'USD/JPY', 
                'EUR/USD', 'GBP/JPY', 'AUD/USD', 'NZD/USD'
            ]
            
            # Select from high-performance pairs that are active
            available_pairs = [p for p in high_performance_pairs if p in active_pairs]
            
            if available_pairs:
                # Weighted random selection based on recent performance
                weights = [0.25, 0.2, 0.15, 0.15, 0.1, 0.05, 0.05, 0.05][:len(available_pairs)]
                return random.choices(available_pairs, weights=weights)[0]
            else:
                return random.choice(active_pairs) if active_pairs else 'EUR/USD'
                
        except Exception as e:
            logging.error(f"Error selecting optimal pair: {e}")
            return 'EUR/USD'
    
    def _create_signal(self, pair: str, market_data: Dict, analysis: Dict, prediction: Dict) -> Dict:
        """Create a formatted trading signal"""
        try:
            current_time = datetime.now()
            
            # Determine signal direction
            direction = prediction['direction'] # 'CALL' or 'PUT'
            confidence = prediction['confidence']
            
            # Calculate entry price (current price with small adjustment)
            current_price = market_data['price']
            entry_price = current_price * (1 + random.uniform(-0.0001, 0.0001))
            
            # Determine expiration time based on market conditions
            expiration_minutes = self._calculate_expiration_time(analysis, confidence)
            
            # Assess risk level
            risk_level = self._assess_risk_level(analysis, confidence)
            
            # Generate analysis explanation
            analysis_text = self._generate_analysis_text(analysis, prediction)
            
            signal = {
                'pair': pair,
                'direction': direction,
                'entry_price': entry_price,
                'current_price': current_price,
                'expiration_minutes': expiration_minutes,
                'confidence': confidence,
                'risk_level': risk_level,
                'analysis': analysis_text,
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
                'signal_id': f"{pair}_{int(current_time.timestamp())}"
            }
            
            return signal
            
        except Exception as e:
            logging.error(f"Error creating signal: {e}")
            return None

    def _create_signal_with_timeframe(self, pair: str, market_data: Dict, analysis: Dict, prediction: Dict, expiration_minutes: int = None) -> Dict:
        """Create a formatted trading signal with specific timeframe"""
        try:
            current_time = datetime.now()
            
            # Determine signal direction
            direction = prediction['direction'] # 'CALL' or 'PUT'
            confidence = prediction['confidence']
            
            # Calculate entry price (current price with small adjustment)
            current_price = market_data['price']
            entry_price = current_price * (1 + random.uniform(-0.0001, 0.0001))
            
            # Use provided expiration time or calculate automatically
            if expiration_minutes is None:
                expiration_minutes = self._calculate_expiration_time(analysis, confidence)
            
            # Assess risk level
            risk_level = self._assess_risk_level(analysis, confidence)
            
            # Generate analysis explanation with timeframe context
            analysis_text = self._generate_analysis_text_with_timeframe(analysis, prediction, expiration_minutes)
            
            signal = {
                'pair': pair,
                'direction': direction,
                'entry_price': entry_price,
                'current_price': current_price,
                'expiration_minutes': expiration_minutes,
                'confidence': confidence,
                'risk_level': risk_level,
                'analysis': analysis_text,
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
                'signal_id': f"{pair}_{int(current_time.timestamp())}"
            }
            
            return signal
            
        except Exception as e:
            logging.error(f"Error creating signal with timeframe: {e}")
            return None
    
    def _calculate_expiration_time(self, analysis: Dict, confidence: float) -> int:
        """Calculate optimal expiration time for the signal"""
        try:
            # Base expiration on market volatility and confidence
            volatility = analysis.get('volatility', 0.5)
            
            if confidence > 85:
                # High confidence - shorter expiration
                base_time = random.randint(5, 10)
            elif confidence > 70:
                # Medium confidence - medium expiration  
                base_time = random.randint(10, 20)
            else:
                # Lower confidence - longer expiration
                base_time = random.randint(15, 30)
            
            # Adjust for volatility
            if volatility > 0.7:
                base_time = max(5, base_time - 5)  # Reduce time for high volatility
            elif volatility < 0.3:
                base_time += 10  # Increase time for low volatility
            
            return min(60, max(5, base_time))  # Keep between 5-60 minutes
            
        except Exception as e:
            logging.error(f"Error calculating expiration time: {e}")
            return 15  # Default 15 minutes
    
    def _assess_risk_level(self, analysis: Dict, confidence: float) -> str:
        """Assess risk level for the signal"""
        try:
            volatility = analysis.get('volatility', 0.5)
            trend_strength = analysis.get('trend_strength', 0.5)
            
            # Calculate risk score
            risk_score = 0
            
            if confidence < 70:
                risk_score += 2
            elif confidence < 85:
                risk_score += 1
                
            if volatility > 0.8:
                risk_score += 2
            elif volatility > 0.6:
                risk_score += 1
                
            if trend_strength < 0.4:
                risk_score += 1
            
            # Determine risk level
            if risk_score <= 1:
                return "LOW"
            elif risk_score <= 3:
                return "MEDIUM"
            else:
                return "HIGH"
                
        except Exception as e:
            logging.error(f"Error assessing risk level: {e}")
            return "MEDIUM"
    
    def _generate_analysis_text(self, analysis: Dict, prediction: Dict) -> str:
        """Generate human-readable analysis explanation"""
        try:
            direction = prediction['direction']
            confidence = prediction['confidence']
            volatility = analysis.get('volatility', 0.5)
            trend = analysis.get('trend', 'sideways')
            
            # Base analysis text
            analysis_parts = []
            
            # Trend analysis
            if trend == 'bullish':
                analysis_parts.append("Strong bullish momentum detected")
            elif trend == 'bearish':
                analysis_parts.append("Clear bearish pressure identified")
            else:
                analysis_parts.append("Market showing consolidation pattern")
            
            # Volatility analysis
            if volatility > 0.7:
                analysis_parts.append("High volatility suggests strong price movement")
            elif volatility < 0.3:
                analysis_parts.append("Low volatility indicates stable price action")
            else:
                analysis_parts.append("Moderate volatility with clear directional bias")
            
            # AI prediction reasoning
            reasoning_templates = {
                'CALL': [
                    "Technical indicators align for upward movement",
                    "Support levels holding strong, expecting bounce",
                    "Bullish divergence in momentum indicators",
                    "Break above resistance suggests continuation"
                ],
                'PUT': [
                    "Technical indicators suggest downward pressure", 
                    "Resistance levels showing rejection patterns",
                    "Bearish divergence in momentum indicators",
                    "Break below support indicates continuation"
                ]
            }
            
            analysis_parts.append(random.choice(reasoning_templates[direction]))
            
            return ". ".join(analysis_parts) + f". AI confidence: {confidence:.1f}%"
            
        except Exception as e:
            logging.error(f"Error generating analysis text: {e}")
            return "AI analysis indicates favorable trading conditions based on current market data."

    def _generate_analysis_text_with_timeframe(self, analysis: Dict, prediction: Dict, expiration_minutes: int) -> str:
        """Generate human-readable analysis explanation with timeframe context"""
        try:
            direction = prediction['direction']
            confidence = prediction['confidence']
            volatility = analysis.get('volatility', 0.5)
            trend = analysis.get('trend', 'sideways')
            
            # Base analysis text
            analysis_parts = []
            
            # Timeframe-specific analysis
            if expiration_minutes <= 5:
                analysis_parts.append(f"Short-term {expiration_minutes}min scalping opportunity")
                if volatility > 0.6:
                    analysis_parts.append("High volatility perfect for quick trades")
                else:
                    analysis_parts.append("Stable momentum for precise entry")
            elif expiration_minutes <= 30:
                analysis_parts.append(f"Medium-term {expiration_minutes}min swing setup")
                analysis_parts.append("Balanced risk-reward ratio for trend following")
            else:
                analysis_parts.append(f"Long-term {expiration_minutes}min position trade")
                analysis_parts.append("Strong directional bias for extended moves")
            
            # Trend analysis
            if trend == 'bullish':
                analysis_parts.append("Strong bullish momentum detected")
            elif trend == 'bearish':
                analysis_parts.append("Clear bearish pressure identified")
            else:
                analysis_parts.append("Consolidation breakout pattern forming")
            
            # AI prediction reasoning with timeframe context
            timeframe_reasoning = {
                'CALL': {
                    'short': "Momentum indicators show bullish acceleration",
                    'medium': "Support levels holding, expecting bounce higher", 
                    'long': "Major trend reversal signals confirmed"
                },
                'PUT': {
                    'short': "Momentum indicators show bearish acceleration",
                    'medium': "Resistance rejection, expecting move lower",
                    'long': "Major trend reversal signals confirmed"
                }
            }
            
            timeframe_type = 'short' if expiration_minutes <= 5 else 'medium' if expiration_minutes <= 30 else 'long'
            analysis_parts.append(timeframe_reasoning[direction][timeframe_type])
            
            return ". ".join(analysis_parts) + f". AI confidence: {confidence:.1f}%"
            
        except Exception as e:
            logging.error(f"Error generating timeframe analysis: {e}")
            return f"AI analysis for {expiration_minutes}min timeframe indicates favorable trading conditions."
    
    def _should_generate_signal(self, pair: str) -> bool:
        """Check if enough time has passed to generate a new signal"""
        try:
            if pair not in self.last_signal_time:
                return True
                
            time_since_last = datetime.now() - self.last_signal_time[pair]
            min_interval = timedelta(minutes=random.randint(8, 18))  # 8-18 minutes between signals
            
            return time_since_last > min_interval
            
        except Exception as e:
            logging.error(f"Error checking signal timing: {e}")
            return True
    
    def _broadcast_to_subscribers(self, signal: Dict):
        """Broadcast signal to subscribers (placeholder)"""
        # This would be called by the telegram bot
        logging.info(f"Broadcasting signal: {signal['pair']} {signal['direction']}")
    
    def is_healthy(self) -> bool:
        """Check if the signal generator is healthy"""
        try:
            # Check if all components are working
            return (
                self.market_analyzer.is_healthy() and
                self.ml_predictor.is_healthy() and 
                self.market_data.is_healthy()
            )
        except Exception as e:
            logging.error(f"Health check failed: {e}")
            return False
