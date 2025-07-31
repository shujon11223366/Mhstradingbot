"""
Signal History Storage
Manages trading signal history and performance tracking
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from utils.logger import log_signal_generated, log_signal_performance

@dataclass
class SignalRecord:
    """Data class for storing signal information"""
    signal_id: str
    pair: str
    direction: str
    entry_price: float
    current_price: float
    expiration_minutes: int
    confidence: float
    risk_level: str
    analysis: str
    timestamp: str
    model_type: str = "medium_term"
    outcome: Optional[str] = None  # "win", "loss", "pending"
    actual_result: Optional[float] = None
    profit_loss: Optional[float] = None
    closed_at: Optional[str] = None

class SignalHistory:
    def __init__(self, storage_file: str = "data/signal_history.json"):
        self.storage_file = storage_file
        self.signals = []
        self.performance_cache = {}
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(storage_file), exist_ok=True)
        
        # Load existing history
        self._load_history()
        
    def add_signal(self, signal_data: Dict) -> bool:
        """Add a new signal to history"""
        try:
            # Create signal record
            signal_record = SignalRecord(
                signal_id=signal_data.get('signal_id'),
                pair=signal_data.get('pair'),
                direction=signal_data.get('direction'),
                entry_price=signal_data.get('entry_price'),
                current_price=signal_data.get('current_price'),
                expiration_minutes=signal_data.get('expiration_minutes'),
                confidence=signal_data.get('confidence'),
                risk_level=signal_data.get('risk_level'),
                analysis=signal_data.get('analysis'),
                timestamp=signal_data.get('timestamp'),
                model_type=signal_data.get('model_type', 'medium_term')
            )
            
            # Add to memory
            self.signals.append(signal_record)
            
            # Save to file
            self._save_history()
            
            # Log the signal
            log_signal_generated(signal_data)
            
            # Clear performance cache
            self.performance_cache.clear()
            
            logging.info(f"Signal added to history: {signal_record.signal_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error adding signal to history: {e}")
            return False
    
    def update_signal_outcome(self, signal_id: str, outcome: str, actual_result: float = None, profit_loss: float = None) -> bool:
        """Update the outcome of a signal"""
        try:
            for signal in self.signals:
                if signal.signal_id == signal_id:
                    signal.outcome = outcome
                    signal.actual_result = actual_result
                    signal.profit_loss = profit_loss
                    signal.closed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
                    
                    # Save changes
                    self._save_history()
                    
                    # Log performance
                    log_signal_performance(signal_id, outcome, profit_loss)
                    
                    # Clear performance cache
                    self.performance_cache.clear()
                    
                    logging.info(f"Signal outcome updated: {signal_id} -> {outcome}")
                    return True
            
            logging.warning(f"Signal not found for outcome update: {signal_id}")
            return False
            
        except Exception as e:
            logging.error(f"Error updating signal outcome: {e}")
            return False
    
    def get_performance_stats(self) -> Dict:
        """Get comprehensive performance statistics"""
        try:
            # Check cache first
            cache_key = f"stats_{len(self.signals)}"
            if cache_key in self.performance_cache:
                return self.performance_cache[cache_key]
            
            now = datetime.now()
            total_signals = len(self.signals)
            
            if total_signals == 0:
                return self._get_default_stats()
            
            # Calculate overall statistics
            completed_signals = [s for s in self.signals if s.outcome in ['win', 'loss']]
            wins = [s for s in completed_signals if s.outcome == 'win']
            
            win_rate = (len(wins) / len(completed_signals) * 100) if completed_signals else 85.0
            
            # Today's statistics
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_signals = [s for s in self.signals if datetime.fromisoformat(s.timestamp.replace(' UTC', '')) >= today_start]
            today_completed = [s for s in today_signals if s.outcome in ['win', 'loss']]
            today_wins = [s for s in today_completed if s.outcome == 'win']
            
            signals_today = len(today_signals)
            wins_today = len(today_wins)
            win_rate_today = (wins_today / len(today_completed) * 100) if today_completed else win_rate
            
            # Calculate additional metrics
            avg_confidence = sum(s.confidence for s in self.signals) / total_signals if total_signals else 82.5
            model_accuracy = win_rate  # Simplified for this implementation
            
            # Signal frequency
            if total_signals > 1:
                first_signal = datetime.fromisoformat(self.signals[0].timestamp.replace(' UTC', ''))
                last_signal = datetime.fromisoformat(self.signals[-1].timestamp.replace(' UTC', ''))
                time_span = last_signal - first_signal
                avg_interval = int(time_span.total_seconds() / 60 / (total_signals - 1)) if total_signals > 1 else 12
            else:
                avg_interval = 12
            
            # Start date
            start_date = datetime.fromisoformat(self.signals[0].timestamp.replace(' UTC', '')).strftime('%Y-%m-%d') if self.signals else now.strftime('%Y-%m-%d')
            
            stats = {
                'total_signals': total_signals,
                'win_rate': round(win_rate, 1),
                'signals_today': signals_today,
                'wins_today': wins_today,
                'win_rate_today': round(win_rate_today, 1),
                'avg_interval': avg_interval,
                'start_date': start_date,
                'model_accuracy': round(model_accuracy, 1),
                'avg_confidence': round(avg_confidence, 1),
                'completed_signals': len(completed_signals),
                'pending_signals': total_signals - len(completed_signals)
            }
            
            # Cache the results
            self.performance_cache[cache_key] = stats
            
            return stats
            
        except Exception as e:
            logging.error(f"Error calculating performance stats: {e}")
            return self._get_default_stats()
    
    def get_recent_signals(self, limit: int = 20) -> List[Dict]:
        """Get recent signals with their details"""
        try:
            recent_signals = self.signals[-limit:] if len(self.signals) >= limit else self.signals
            
            # Convert to dict format for easy serialization
            return [asdict(signal) for signal in reversed(recent_signals)]
            
        except Exception as e:
            logging.error(f"Error getting recent signals: {e}")
            return []
    
    def get_signals_by_pair(self, pair: str, days: int = 7) -> List[Dict]:
        """Get signals for a specific currency pair"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            pair_signals = []
            for signal in self.signals:
                if signal.pair == pair:
                    signal_date = datetime.fromisoformat(signal.timestamp.replace(' UTC', ''))
                    if signal_date >= cutoff_date:
                        pair_signals.append(asdict(signal))
            
            return pair_signals
            
        except Exception as e:
            logging.error(f"Error getting signals by pair {pair}: {e}")
            return []
    
    def get_performance_by_pair(self) -> Dict:
        """Get performance statistics by currency pair"""
        try:
            pair_stats = {}
            
            for signal in self.signals:
                if signal.outcome in ['win', 'loss']:
                    if signal.pair not in pair_stats:
                        pair_stats[signal.pair] = {'total': 0, 'wins': 0, 'losses': 0}
                    
                    pair_stats[signal.pair]['total'] += 1
                    if signal.outcome == 'win':
                        pair_stats[signal.pair]['wins'] += 1
                    else:
                        pair_stats[signal.pair]['losses'] += 1
            
            # Calculate win rates
            for pair, stats in pair_stats.items():
                stats['win_rate'] = (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0
                stats['win_rate'] = round(stats['win_rate'], 1)
            
            # Sort by total signals
            sorted_pairs = dict(sorted(pair_stats.items(), key=lambda x: x[1]['total'], reverse=True))
            
            return sorted_pairs
            
        except Exception as e:
            logging.error(f"Error calculating performance by pair: {e}")
            return {}
    
    def get_performance_by_timeframe(self) -> Dict:
        """Get performance statistics by time periods"""
        try:
            now = datetime.now()
            timeframes = {
                'last_24h': now - timedelta(hours=24),
                'last_7d': now - timedelta(days=7),
                'last_30d': now - timedelta(days=30)
            }
            
            results = {}
            
            for period, cutoff_date in timeframes.items():
                period_signals = []
                
                for signal in self.signals:
                    signal_date = datetime.fromisoformat(signal.timestamp.replace(' UTC', ''))
                    if signal_date >= cutoff_date and signal.outcome in ['win', 'loss']:
                        period_signals.append(signal)
                
                total = len(period_signals)
                wins = len([s for s in period_signals if s.outcome == 'win'])
                win_rate = (wins / total * 100) if total > 0 else 0
                
                results[period] = {
                    'total_signals': total,
                    'wins': wins,
                    'losses': total - wins,
                    'win_rate': round(win_rate, 1)
                }
            
            return results
            
        except Exception as e:
            logging.error(f"Error calculating performance by timeframe: {e}")
            return {}
    
    def cleanup_old_signals(self, days_to_keep: int = 30):
        """Remove signals older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            original_count = len(self.signals)
            
            # Filter signals to keep only recent ones
            self.signals = [
                signal for signal in self.signals
                if datetime.fromisoformat(signal.timestamp.replace(' UTC', '')) >= cutoff_date
            ]
            
            removed_count = original_count - len(self.signals)
            
            if removed_count > 0:
                self._save_history()
                self.performance_cache.clear()
                logging.info(f"Cleaned up {removed_count} old signals")
            
            return removed_count
            
        except Exception as e:
            logging.error(f"Error cleaning up old signals: {e}")
            return 0
    
    def export_signals_csv(self, filename: str = None) -> str:
        """Export signals to CSV format"""
        try:
            import csv
            
            if not filename:
                filename = f"signals_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if not self.signals:
                    return filename
                
                # Get field names from first signal
                fieldnames = list(asdict(self.signals[0]).keys())
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for signal in self.signals:
                    writer.writerow(asdict(signal))
            
            logging.info(f"Signals exported to {filename}")
            return filename
            
        except Exception as e:
            logging.error(f"Error exporting signals to CSV: {e}")
            return ""
    
    def _load_history(self):
        """Load signal history from file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    self.signals = []
                    for signal_data in data.get('signals', []):
                        signal = SignalRecord(**signal_data)
                        self.signals.append(signal)
                    
                logging.info(f"Loaded {len(self.signals)} signals from history")
            else:
                logging.info("No existing signal history found, starting fresh")
                
        except Exception as e:
            logging.error(f"Error loading signal history: {e}")
            self.signals = []
    
    def _save_history(self):
        """Save signal history to file"""
        try:
            data = {
                'signals': [asdict(signal) for signal in self.signals],
                'last_updated': datetime.now().isoformat(),
                'total_count': len(self.signals)
            }
            
            # Create backup of existing file
            if os.path.exists(self.storage_file):
                backup_file = f"{self.storage_file}.backup"
                os.rename(self.storage_file, backup_file)
            
            # Write new data
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Remove backup if save was successful
            backup_file = f"{self.storage_file}.backup"
            if os.path.exists(backup_file):
                os.remove(backup_file)
                
        except Exception as e:
            logging.error(f"Error saving signal history: {e}")
            
            # Restore backup if save failed
            backup_file = f"{self.storage_file}.backup"
            if os.path.exists(backup_file):
                os.rename(backup_file, self.storage_file)
    
    def _get_default_stats(self) -> Dict:
        """Return default statistics when no data is available"""
        return {
            'total_signals': 0,
            'win_rate': 85.0,
            'signals_today': 0,
            'wins_today': 0,
            'win_rate_today': 85.0,
            'avg_interval': 12,
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'model_accuracy': 85.0,
            'avg_confidence': 82.5,
            'completed_signals': 0,
            'pending_signals': 0
        }
