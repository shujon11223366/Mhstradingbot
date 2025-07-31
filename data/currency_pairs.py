"""
Currency Pairs Management
Handles currency pair information and market data
"""

import logging
import random
from datetime import datetime
from typing import Dict, List

class CurrencyPairs:
    def __init__(self):
        self.pairs_data = self._initialize_pairs_data()
        self.market_sessions = self._get_market_sessions()
        
    def _initialize_pairs_data(self) -> Dict:
        """Initialize currency pairs with their characteristics"""
        return {
            'major': [
                {
                    'pair': 'EUR/USD',
                    'name': 'Euro / US Dollar',
                    'base_volume': 1.8,
                    'avg_spread': 0.0001,
                    'volatility': 0.65,
                    'trading_sessions': ['european', 'us'],
                    'popularity': 0.95
                },
                {
                    'pair': 'GBP/USD',
                    'name': 'British Pound / US Dollar', 
                    'base_volume': 1.5,
                    'avg_spread': 0.0002,
                    'volatility': 0.75,
                    'trading_sessions': ['european', 'us'],
                    'popularity': 0.90
                },
                {
                    'pair': 'USD/JPY',
                    'name': 'US Dollar / Japanese Yen',
                    'base_volume': 1.6,
                    'avg_spread': 0.0001,
                    'volatility': 0.60,
                    'trading_sessions': ['asian', 'us'],
                    'popularity': 0.88
                },
                {
                    'pair': 'AUD/USD',
                    'name': 'Australian Dollar / US Dollar',
                    'base_volume': 1.2,
                    'avg_spread': 0.0002,
                    'volatility': 0.70,
                    'trading_sessions': ['asian', 'us'],
                    'popularity': 0.75
                }
            ],
            'cross': [
                {
                    'pair': 'EUR/CHF',
                    'name': 'Euro / Swiss Franc',
                    'base_volume': 1.4,
                    'avg_spread': 0.0003,
                    'volatility': 0.85,
                    'trading_sessions': ['european'],
                    'popularity': 0.80
                },
                {
                    'pair': 'AUD/JPY',
                    'name': 'Australian Dollar / Japanese Yen',
                    'base_volume': 1.3,
                    'avg_spread': 0.0003,
                    'volatility': 0.90,
                    'trading_sessions': ['asian'],
                    'popularity': 0.85
                },
                {
                    'pair': 'GBP/JPY',
                    'name': 'British Pound / Japanese Yen',
                    'base_volume': 1.1,
                    'avg_spread': 0.0004,
                    'volatility': 0.95,
                    'trading_sessions': ['european', 'asian'],
                    'popularity': 0.78
                },
                {
                    'pair': 'EUR/GBP',
                    'name': 'Euro / British Pound',
                    'base_volume': 1.0,
                    'avg_spread': 0.0002,
                    'volatility': 0.55,
                    'trading_sessions': ['european'],
                    'popularity': 0.72
                }
            ],
            'exotic': [
                {
                    'pair': 'NZD/USD',
                    'name': 'New Zealand Dollar / US Dollar',
                    'base_volume': 0.8,
                    'avg_spread': 0.0005,
                    'volatility': 0.80,
                    'trading_sessions': ['asian', 'us'],
                    'popularity': 0.60
                },
                {
                    'pair': 'USD/CHF',
                    'name': 'US Dollar / Swiss Franc',
                    'base_volume': 0.9,
                    'avg_spread': 0.0004,
                    'volatility': 0.65,
                    'trading_sessions': ['european', 'us'],
                    'popularity': 0.65
                },
                {
                    'pair': 'USD/CAD',
                    'name': 'US Dollar / Canadian Dollar',
                    'base_volume': 1.0,
                    'avg_spread': 0.0003,
                    'volatility': 0.70,
                    'trading_sessions': ['us'],
                    'popularity': 0.68
                },
                {
                    'pair': 'EUR/JPY',
                    'name': 'Euro / Japanese Yen',
                    'base_volume': 1.1,
                    'avg_spread': 0.0003,
                    'volatility': 0.75,
                    'trading_sessions': ['european', 'asian'],
                    'popularity': 0.70
                }
            ]
        }
    
    def _get_market_sessions(self) -> Dict:
        """Get current market session information"""
        current_hour = datetime.now().hour
        
        return {
            'asian': {
                'active': 23 <= current_hour or current_hour < 8,
                'timezone': 'Tokyo',
                'peak_hours': [0, 1, 2, 3, 4, 5, 6, 7]
            },
            'european': {
                'active': 8 <= current_hour < 17,
                'timezone': 'London', 
                'peak_hours': [8, 9, 10, 11, 12, 13, 14, 15, 16]
            },
            'us': {
                'active': 13 <= current_hour < 22,
                'timezone': 'New York',
                'peak_hours': [13, 14, 15, 16, 17, 18, 19, 20, 21]
            }
        }
    
    def get_active_pairs(self) -> List[str]:
        """Get list of currently active currency pairs"""
        try:
            active_pairs = []
            current_sessions = [name for name, info in self.market_sessions.items() if info['active']]
            
            for category in self.pairs_data.values():
                for pair_info in category:
                    # Check if pair has active trading sessions
                    pair_sessions = pair_info['trading_sessions']
                    if any(session in current_sessions for session in pair_sessions):
                        active_pairs.append(pair_info['pair'])
            
            # If no sessions are active (unlikely), return all major pairs
            if not active_pairs:
                active_pairs = [pair['pair'] for pair in self.pairs_data['major']]
            
            return active_pairs
            
        except Exception as e:
            logging.error(f"Error getting active pairs: {e}")
            return ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD']  # Fallback
    
    def get_high_volume_pairs(self) -> List[str]:
        """Get currency pairs with high trading volume"""
        try:
            high_volume_pairs = []
            
            for category in self.pairs_data.values():
                for pair_info in category:
                    # Calculate current volume based on session activity
                    current_volume = self._calculate_current_volume(pair_info)
                    
                    if current_volume > 1.0:  # High volume threshold
                        high_volume_pairs.append(pair_info['pair'])
            
            # Sort by volume (simulated)
            high_volume_pairs.sort(key=lambda p: self._get_pair_info(p)['base_volume'], reverse=True)
            
            return high_volume_pairs[:8]  # Return top 8
            
        except Exception as e:
            logging.error(f"Error getting high volume pairs: {e}")
            return ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD']
    
    def get_all_pairs_info(self) -> Dict:
        """Get detailed information about all currency pairs"""
        try:
            pairs_info = {}
            
            for category, pairs in self.pairs_data.items():
                pairs_info[category] = []
                
                for pair_info in pairs:
                    current_volume = self._calculate_current_volume(pair_info)
                    
                    enhanced_info = {
                        'pair': pair_info['pair'],
                        'name': pair_info['name'],
                        'volume': current_volume,
                        'volatility': pair_info['volatility'],
                        'spread': pair_info['avg_spread'],
                        'popularity': pair_info['popularity'],
                        'active': pair_info['pair'] in self.get_active_pairs(),
                        'recommended': current_volume > 1.2 and pair_info['volatility'] > 0.7
                    }
                    
                    pairs_info[category].append(enhanced_info)
                
                # Sort by volume within category
                pairs_info[category].sort(key=lambda x: x['volume'], reverse=True)
            
            return pairs_info
            
        except Exception as e:
            logging.error(f"Error getting all pairs info: {e}")
            return {}
    
    def _calculate_current_volume(self, pair_info: Dict) -> float:
        """Calculate current trading volume for a pair"""
        try:
            base_volume = pair_info['base_volume']
            trading_sessions = pair_info['trading_sessions']
            
            # Volume multiplier based on active sessions
            volume_multiplier = 1.0
            
            for session in trading_sessions:
                if self.market_sessions[session]['active']:
                    volume_multiplier += 0.3  # 30% boost per active session
            
            # Add some randomness for realism
            random_factor = random.uniform(0.8, 1.2)
            
            # Consider popularity
            popularity_factor = 0.5 + (pair_info['popularity'] * 0.5)
            
            final_volume = base_volume * volume_multiplier * random_factor * popularity_factor
            
            return round(final_volume, 2)
            
        except Exception as e:
            logging.error(f"Error calculating current volume: {e}")
            return pair_info.get('base_volume', 1.0)
    
    def _get_pair_info(self, pair: str) -> Dict:
        """Get information for a specific currency pair"""
        try:
            for category in self.pairs_data.values():
                for pair_info in category:
                    if pair_info['pair'] == pair:
                        return pair_info
            
            # Return default info if pair not found
            return {
                'pair': pair,
                'name': pair,
                'base_volume': 1.0,
                'avg_spread': 0.0002,
                'volatility': 0.6,
                'trading_sessions': ['european', 'us'],
                'popularity': 0.5
            }
            
        except Exception as e:
            logging.error(f"Error getting pair info for {pair}: {e}")
            return {}
    
    def get_recommended_pairs(self) -> List[Dict]:
        """Get recommended currency pairs for trading"""
        try:
            recommended = []
            
            for category in self.pairs_data.values():
                for pair_info in category:
                    current_volume = self._calculate_current_volume(pair_info)
                    
                    # Recommendation criteria
                    if (current_volume > 1.1 and 
                        pair_info['volatility'] > 0.6 and 
                        pair_info['popularity'] > 0.7):
                        
                        recommendation = {
                            'pair': pair_info['pair'],
                            'name': pair_info['name'],
                            'volume': current_volume,
                            'volatility': pair_info['volatility'],
                            'popularity': pair_info['popularity'],
                            'score': self._calculate_recommendation_score(pair_info, current_volume),
                            'reasons': self._get_recommendation_reasons(pair_info, current_volume)
                        }
                        
                        recommended.append(recommendation)
            
            # Sort by score
            recommended.sort(key=lambda x: x['score'], reverse=True)
            
            return recommended[:5]  # Top 5 recommendations
            
        except Exception as e:
            logging.error(f"Error getting recommended pairs: {e}")
            return []
    
    def _calculate_recommendation_score(self, pair_info: Dict, current_volume: float) -> float:
        """Calculate recommendation score for a pair"""
        try:
            # Weighted scoring
            volume_score = min(current_volume / 2.0, 1.0) * 0.3
            volatility_score = pair_info['volatility'] * 0.3
            popularity_score = pair_info['popularity'] * 0.2
            
            # Session bonus
            session_bonus = 0.0
            for session in pair_info['trading_sessions']:
                if self.market_sessions[session]['active']:
                    session_bonus += 0.1
            
            total_score = volume_score + volatility_score + popularity_score + session_bonus
            
            return round(min(total_score, 1.0), 2)
            
        except Exception as e:
            logging.error(f"Error calculating recommendation score: {e}")
            return 0.5
    
    def _get_recommendation_reasons(self, pair_info: Dict, current_volume: float) -> List[str]:
        """Get reasons for recommending a pair"""
        try:
            reasons = []
            
            if current_volume > 1.5:
                reasons.append("High trading volume")
            
            if pair_info['volatility'] > 0.8:
                reasons.append("High volatility - good for scalping")
            elif pair_info['volatility'] > 0.6:
                reasons.append("Moderate volatility - balanced risk")
            
            if pair_info['popularity'] > 0.85:
                reasons.append("Very popular among traders")
            
            active_sessions = [s for s in pair_info['trading_sessions'] 
                             if self.market_sessions[s]['active']]
            if len(active_sessions) > 1:
                reasons.append("Multiple active trading sessions")
            elif len(active_sessions) == 1:
                reasons.append(f"Active {active_sessions[0]} session")
            
            if pair_info['avg_spread'] < 0.0002:
                reasons.append("Low spread costs")
            
            return reasons[:3]  # Limit to 3 main reasons
            
        except Exception as e:
            logging.error(f"Error getting recommendation reasons: {e}")
            return ["Good trading opportunity"]
    
    def is_data_fresh(self) -> bool:
        """Check if currency pair data is fresh"""
        # For this implementation, data is always considered fresh
        # In a real system, this would check last update timestamps
        return True
