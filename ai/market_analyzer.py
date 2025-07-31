"""
Market Analyzer
Advanced market analysis using technical indicators and patterns
"""

import logging
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class MarketAnalyzer:
    def __init__(self):
        self.analysis_cache = {}
        self.last_analysis_time = {}
        
    async def analyze_market(self, pair: str, market_data: Dict) -> Dict:
        """Perform comprehensive market analysis"""
        try:
            # Check cache first
            if self._is_analysis_cached(pair):
                return self.analysis_cache[pair]
            
            analysis = {}
            
            # Technical Analysis
            analysis['technical'] = self._technical_analysis(market_data)
            
            # Trend Analysis
            analysis['trend'] = self._trend_analysis(market_data)
            analysis['trend_strength'] = self._calculate_trend_strength(market_data)
            
            # Volatility Analysis
            analysis['volatility'] = self._volatility_analysis(market_data)
            
            # Support/Resistance Levels
            analysis['support_resistance'] = self._find_support_resistance(market_data)
            
            # Market Sentiment
            analysis['sentiment'] = self._market_sentiment_analysis(pair, market_data)
            
            # Volume Analysis
            analysis['volume_analysis'] = self._volume_analysis(market_data)
            
            # Pattern Recognition
            analysis['patterns'] = self._pattern_recognition(market_data)
            
            # Overall Market Score
            analysis['market_score'] = self._calculate_market_score(analysis)
            
            # Cache the analysis
            self.analysis_cache[pair] = analysis
            self.last_analysis_time[pair] = datetime.now()
            
            return analysis
            
        except Exception as e:
            logging.error(f"Error in market analysis for {pair}: {e}")
            return self._get_default_analysis()
    
    def _technical_analysis(self, market_data: Dict) -> Dict:
        """Perform technical indicator analysis"""
        try:
            # Simulate technical indicators
            price_data = market_data.get('price_history', [market_data['price']] * 20)
            current_price = market_data['price']
            
            # Moving Averages
            ma20 = np.mean(price_data[-20:]) if len(price_data) >= 20 else current_price
            ma50 = np.mean(price_data[-50:]) if len(price_data) >= 50 else current_price
            
            # RSI simulation
            rsi = random.uniform(20, 80)
            
            # MACD simulation
            macd_signal = random.choice(['bullish', 'bearish', 'neutral'])
            
            # Bollinger Bands
            bb_position = random.uniform(0.1, 0.9)  # Position within bands
            
            return {
                'ma20': ma20,
                'ma50': ma50,
                'ma_signal': 'bullish' if ma20 > ma50 else 'bearish',
                'rsi': rsi,
                'rsi_signal': 'oversold' if rsi < 30 else 'overbought' if rsi > 70 else 'neutral',
                'macd_signal': macd_signal,
                'bb_position': bb_position,
                'bb_signal': 'oversold' if bb_position < 0.2 else 'overbought' if bb_position > 0.8 else 'neutral'
            }
            
        except Exception as e:
            logging.error(f"Error in technical analysis: {e}")
            return {}
    
    def _trend_analysis(self, market_data: Dict) -> str:
        """Analyze market trend direction"""
        try:
            price_data = market_data.get('price_history', [market_data['price']] * 10)
            
            if len(price_data) < 3:
                return 'sideways'
            
            # Calculate trend based on recent price action
            recent_change = (price_data[-1] - price_data[-3]) / price_data[-3]
            
            if recent_change > 0.001:  # 0.1% increase
                return 'bullish'
            elif recent_change < -0.001:  # 0.1% decrease
                return 'bearish'
            else:
                return 'sideways'
                
        except Exception as e:
            logging.error(f"Error in trend analysis: {e}")
            return 'sideways'
    
    def _calculate_trend_strength(self, market_data: Dict) -> float:
        """Calculate the strength of the current trend"""
        try:
            # Simulate trend strength based on price momentum
            price_change = market_data.get('price_change_24h', 0)
            volume = market_data.get('volume', 0.5)
            
            # Normalize trend strength (0-1 scale)
            momentum_factor = min(abs(price_change) * 100, 1.0)
            volume_factor = min(volume, 1.0)
            
            trend_strength = (momentum_factor + volume_factor) / 2
            return min(max(trend_strength, 0.1), 1.0)
            
        except Exception as e:
            logging.error(f"Error calculating trend strength: {e}")
            return 0.5
    
    def _volatility_analysis(self, market_data: Dict) -> float:
        """Analyze market volatility"""
        try:
            # Calculate volatility based on price data
            price_data = market_data.get('price_history', [market_data['price']] * 20)
            
            if len(price_data) < 2:
                return 0.5
            
            # Calculate standard deviation of price changes
            price_changes = []
            for i in range(1, len(price_data)):
                change = (price_data[i] - price_data[i-1]) / price_data[i-1]
                price_changes.append(change)
            
            if not price_changes:
                return 0.5
            
            volatility = np.std(price_changes) * 100  # Convert to percentage
            
            # Normalize to 0-1 scale
            normalized_volatility = min(volatility / 2.0, 1.0)  # Assume 2% is high volatility
            
            return max(normalized_volatility, 0.1)
            
        except Exception as e:
            logging.error(f"Error in volatility analysis: {e}")
            return 0.5
    
    def _find_support_resistance(self, market_data: Dict) -> Dict:
        """Identify support and resistance levels"""
        try:
            current_price = market_data['price']
            price_data = market_data.get('price_history', [current_price] * 20)
            
            # Simple support/resistance calculation
            high_prices = [p * random.uniform(1.001, 1.005) for p in price_data[-10:]]
            low_prices = [p * random.uniform(0.995, 0.999) for p in price_data[-10:]]
            
            resistance = max(high_prices)
            support = min(low_prices)
            
            # Distance to levels
            resistance_distance = (resistance - current_price) / current_price
            support_distance = (current_price - support) / current_price
            
            return {
                'resistance': resistance,
                'support': support,
                'resistance_distance': resistance_distance,
                'support_distance': support_distance,
                'near_resistance': resistance_distance < 0.002,  # Within 0.2%
                'near_support': support_distance < 0.002
            }
            
        except Exception as e:
            logging.error(f"Error finding support/resistance: {e}")
            return {}
    
    def _market_sentiment_analysis(self, pair: str, market_data: Dict) -> Dict:
        """Analyze overall market sentiment"""
        try:
            # Simulate market sentiment factors
            news_sentiment = random.uniform(-1, 1)  # -1 (very bearish) to 1 (very bullish)
            market_fear_greed = random.uniform(0, 100)  # Fear & Greed index
            
            # Economic calendar impact
            economic_impact = random.choice(['positive', 'negative', 'neutral'])
            
            # Overall sentiment score
            sentiment_score = (news_sentiment + (market_fear_greed - 50) / 50) / 2
            
            sentiment_label = 'bullish' if sentiment_score > 0.2 else 'bearish' if sentiment_score < -0.2 else 'neutral'
            
            return {
                'news_sentiment': news_sentiment,
                'fear_greed_index': market_fear_greed,
                'economic_impact': economic_impact,
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label
            }
            
        except Exception as e:
            logging.error(f"Error in sentiment analysis: {e}")
            return {'sentiment_label': 'neutral', 'sentiment_score': 0}
    
    def _volume_analysis(self, market_data: Dict) -> Dict:
        """Analyze trading volume patterns"""
        try:
            current_volume = market_data.get('volume', 0.5)
            volume_history = market_data.get('volume_history', [current_volume] * 10)
            
            # Calculate average volume
            avg_volume = np.mean(volume_history) if volume_history else current_volume
            
            # Volume trend
            volume_trend = 'increasing' if current_volume > avg_volume * 1.2 else 'decreasing' if current_volume < avg_volume * 0.8 else 'stable'
            
            # Volume strength
            volume_strength = min(current_volume / max(avg_volume, 0.1), 2.0)
            
            return {
                'current_volume': current_volume,
                'average_volume': avg_volume,
                'volume_trend': volume_trend,
                'volume_strength': volume_strength,
                'high_volume': current_volume > avg_volume * 1.5
            }
            
        except Exception as e:
            logging.error(f"Error in volume analysis: {e}")
            return {'volume_trend': 'stable', 'volume_strength': 1.0}
    
    def _pattern_recognition(self, market_data: Dict) -> Dict:
        """Recognize chart patterns"""
        try:
            # Simulate pattern recognition
            patterns = [
                'double_top', 'double_bottom', 'head_shoulders', 'triangle',
                'flag', 'pennant', 'wedge', 'channel', 'none'
            ]
            
            detected_pattern = random.choice(patterns)
            pattern_strength = random.uniform(0.3, 0.9) if detected_pattern != 'none' else 0
            
            # Pattern implications
            bullish_patterns = ['double_bottom', 'triangle', 'flag', 'pennant']
            bearish_patterns = ['double_top', 'head_shoulders', 'wedge']
            
            if detected_pattern in bullish_patterns:
                pattern_signal = 'bullish'
            elif detected_pattern in bearish_patterns:
                pattern_signal = 'bearish'
            else:
                pattern_signal = 'neutral'
            
            return {
                'detected_pattern': detected_pattern,
                'pattern_strength': pattern_strength,
                'pattern_signal': pattern_signal,
                'pattern_confidence': pattern_strength * 100
            }
            
        except Exception as e:
            logging.error(f"Error in pattern recognition: {e}")
            return {'detected_pattern': 'none', 'pattern_signal': 'neutral'}
    
    def _calculate_market_score(self, analysis: Dict) -> float:
        """Calculate overall market analysis score"""
        try:
            score = 0.5  # Neutral starting point
            
            # Technical indicators weight
            technical = analysis.get('technical', {})
            if technical.get('ma_signal') == 'bullish':
                score += 0.1
            elif technical.get('ma_signal') == 'bearish':
                score -= 0.1
            
            if technical.get('rsi_signal') == 'oversold':
                score += 0.05
            elif technical.get('rsi_signal') == 'overbought':
                score -= 0.05
            
            # Trend analysis weight
            trend = analysis.get('trend', 'sideways')
            trend_strength = analysis.get('trend_strength', 0.5)
            
            if trend == 'bullish':
                score += 0.15 * trend_strength
            elif trend == 'bearish':
                score -= 0.15 * trend_strength
            
            # Sentiment weight
            sentiment = analysis.get('sentiment', {})
            sentiment_score = sentiment.get('sentiment_score', 0)
            score += sentiment_score * 0.1
            
            # Pattern weight
            patterns = analysis.get('patterns', {})
            pattern_signal = patterns.get('pattern_signal', 'neutral')
            pattern_strength = patterns.get('pattern_strength', 0)
            
            if pattern_signal == 'bullish':
                score += 0.1 * pattern_strength
            elif pattern_signal == 'bearish':
                score -= 0.1 * pattern_strength
            
            # Normalize to 0-1 range
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logging.error(f"Error calculating market score: {e}")
            return 0.5
    
    def _is_analysis_cached(self, pair: str) -> bool:
        """Check if analysis is cached and still valid"""
        try:
            if pair not in self.analysis_cache or pair not in self.last_analysis_time:
                return False
            
            # Cache valid for 5 minutes
            cache_age = datetime.now() - self.last_analysis_time[pair]
            return cache_age < timedelta(minutes=5)
            
        except Exception as e:
            logging.error(f"Error checking analysis cache: {e}")
            return False
    
    def _get_default_analysis(self) -> Dict:
        """Return default analysis in case of errors"""
        return {
            'trend': 'sideways',
            'trend_strength': 0.5,
            'volatility': 0.5,
            'market_score': 0.5,
            'sentiment': {'sentiment_label': 'neutral'},
            'patterns': {'pattern_signal': 'neutral'}
        }
    
    def is_healthy(self) -> bool:
        """Check if market analyzer is healthy"""
        return True  # Simple health check
