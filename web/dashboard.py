"""
Web Dashboard
Flask web application for monitoring bot performance
"""

import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from storage.signal_history import SignalHistory
from data.currency_pairs import CurrencyPairs
from data.market_data import MarketDataProvider
from ai.signal_generator import SignalGenerator
from utils.config import Config

def create_web_app():
    """Create and configure Flask web application"""
    import os
    # Get the directory of the current file and go up one level to the root
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config['SECRET_KEY'] = 'trading-bot-dashboard-secret-key'
    
    # Initialize components
    signal_history = SignalHistory()
    currency_pairs = CurrencyPairs()
    market_data = MarketDataProvider()
    signal_generator = SignalGenerator()
    
    @app.route('/')
    def dashboard():
        """Main dashboard page"""
        try:
            return render_template('dashboard.html')
        except Exception as e:
            logging.error(f"Error rendering dashboard: {e}")
            return f"Dashboard Error: {e}", 500
    
    @app.route('/api/stats')
    def api_stats():
        """API endpoint for performance statistics"""
        try:
            stats = signal_history.get_performance_stats()
            config_info = Config.get_config_summary()
            trading_session = Config.get_trading_session_info()
            
            return jsonify({
                'success': True,
                'data': {
                    'performance': stats,
                    'config': config_info,
                    'trading_session': trading_session,
                    'timestamp': datetime.now().isoformat()
                }
            })
        except Exception as e:
            logging.error(f"Error getting stats API: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/signals/recent')
    def api_recent_signals():
        """API endpoint for recent signals"""
        try:
            limit = request.args.get('limit', 20, type=int)
            signals = signal_history.get_recent_signals(limit)
            
            return jsonify({
                'success': True,
                'data': signals,
                'count': len(signals)
            })
        except Exception as e:
            logging.error(f"Error getting recent signals API: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/signals/pair/<pair>')
    def api_signals_by_pair(pair):
        """API endpoint for signals by currency pair"""
        try:
            days = request.args.get('days', 7, type=int)
            signals = signal_history.get_signals_by_pair(pair, days)
            
            return jsonify({
                'success': True,
                'data': signals,
                'pair': pair,
                'days': days,
                'count': len(signals)
            })
        except Exception as e:
            logging.error(f"Error getting signals by pair API: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/performance/pairs')
    def api_performance_by_pairs():
        """API endpoint for performance by currency pairs"""
        try:
            performance = signal_history.get_performance_by_pair()
            
            return jsonify({
                'success': True,
                'data': performance
            })
        except Exception as e:
            logging.error(f"Error getting performance by pairs API: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/performance/timeframes')
    def api_performance_by_timeframes():
        """API endpoint for performance by timeframes"""
        try:
            performance = signal_history.get_performance_by_timeframe()
            
            return jsonify({
                'success': True,
                'data': performance
            })
        except Exception as e:
            logging.error(f"Error getting performance by timeframes API: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/pairs/active')
    def api_active_pairs():
        """API endpoint for active currency pairs"""
        try:
            active_pairs = currency_pairs.get_active_pairs()
            pairs_info = currency_pairs.get_all_pairs_info()
            
            return jsonify({
                'success': True,
                'data': {
                    'active_pairs': active_pairs,
                    'pairs_info': pairs_info
                }
            })
        except Exception as e:
            logging.error(f"Error getting active pairs API: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/market/status')
    def api_market_status():
        """API endpoint for market status"""
        try:
            market_status = market_data.get_market_status()
            
            return jsonify({
                'success': True,
                'data': market_status
            })
        except Exception as e:
            logging.error(f"Error getting market status API: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/signal/generate')
    def api_generate_signal():
        """API endpoint to generate a new signal"""
        try:
            pair = request.args.get('pair')
            signal = None
            
            if pair:
                # Generate signal for specific pair
                import asyncio
                signal = asyncio.run(signal_generator.generate_signal(pair))
            else:
                # Generate signal for optimal pair
                import asyncio
                signal = asyncio.run(signal_generator.generate_signal())
            
            if signal:
                return jsonify({
                    'success': True,
                    'data': signal
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Unable to generate signal at this time'
                }), 500
                
        except Exception as e:
            logging.error(f"Error generating signal API: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/health')
    def api_health():
        """API endpoint for health check"""
        try:
            health_status = {
                'signal_generator': signal_generator.is_healthy(),
                'market_data': market_data.is_healthy(),
                'currency_pairs': currency_pairs.is_data_fresh(),
                'signal_history': len(signal_history.signals) >= 0,  # Always true if accessible
                'timestamp': datetime.now().isoformat()
            }
            
            overall_health = all(health_status.values())
            
            return jsonify({
                'success': True,
                'healthy': overall_health,
                'components': health_status
            })
        except Exception as e:
            logging.error(f"Error getting health status: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/config')
    def api_config():
        """API endpoint for configuration information"""
        try:
            config_summary = Config.get_config_summary()
            config_issues = Config.validate_config()
            
            return jsonify({
                'success': True,
                'data': {
                    'summary': config_summary,
                    'issues': config_issues,
                    'supported_pairs': Config.SUPPORTED_PAIRS,
                    'expiration_times': Config.EXPIRATION_TIMES
                }
            })
        except Exception as e:
            logging.error(f"Error getting config API: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/export/signals')
    def api_export_signals():
        """API endpoint to export signals"""
        try:
            format_type = request.args.get('format', 'csv')
            
            if format_type == 'csv':
                filename = signal_history.export_signals_csv()
                return jsonify({
                    'success': True,
                    'filename': filename,
                    'message': f'Signals exported to {filename}'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Unsupported export format'
                }), 400
                
        except Exception as e:
            logging.error(f"Error exporting signals: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    # Add CORS headers for API endpoints
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    return app

if __name__ == '__main__':
    # For development only
    app = create_web_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
