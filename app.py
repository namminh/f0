#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VNSTOCK AUTOMATED DASHBOARD
Flask Web Application for Real-time Stock Analysis Dashboard
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO
import json
import os
import glob
from datetime import datetime, timedelta
import threading
import time
import schedule
from pathlib import Path
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnstock_dashboard_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global configuration
BASE_DIR = Path(__file__).parent
STOCK_ANALYSIS_DIR = BASE_DIR / "stock_analysis"
CONFIG_FILE = BASE_DIR / "automation" / "config" / "stocks_config.json"

class StockDataManager:
    def __init__(self):
        self.load_config()
        self.last_update = {}
        
    def load_config(self):
        """Load stocks configuration"""
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = {"active_stocks": ["VHM", "VIX", "DIG"], "market_hours": {"start": "09:00", "end": "15:00"}}
    
    def get_active_stocks(self):
        """Get list of active stocks"""
        return self.config.get('active_stocks', [])
    
    def get_stock_data(self, symbol):
        """Get latest data for a stock"""
        try:
            # Read intraday data
            data_file = STOCK_ANALYSIS_DIR / symbol / "data" / f"{symbol}_intraday_data.json"
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    intraday_data = json.load(f)
                
                # Calculate basic metrics
                if intraday_data.get('data'):
                    prices = [item['price'] for item in intraday_data['data'][:100]]  # Latest 100 points
                    volumes = [item['volume'] for item in intraday_data['data'][:100]]
                    buy_volumes = sum([item['volume'] for item in intraday_data['data'][:100] if item['match_type'] == 'Buy'])
                    sell_volumes = sum([item['volume'] for item in intraday_data['data'][:100] if item['match_type'] == 'Sell'])
                    total_volume = buy_volumes + sell_volumes
                    
                    return {
                        'symbol': symbol,
                        'current_price': prices[0] if prices else 0,
                        'high_price': max(prices) if prices else 0,
                        'low_price': min(prices) if prices else 0,
                        'total_volume': total_volume,
                        'buy_ratio': (buy_volumes / total_volume * 100) if total_volume > 0 else 0,
                        'sell_ratio': (sell_volumes / total_volume * 100) if total_volume > 0 else 0,
                        'data_points': intraday_data.get('data_points', 0),
                        'last_updated': intraday_data.get('timestamp', 'N/A')
                    }
            return None
        except Exception as e:
            logger.error(f"Error getting stock data for {symbol}: {e}")
            return None
    
    def get_stock_charts(self, symbol):
        """Get available charts for a stock"""
        charts = {}
        charts_dir = STOCK_ANALYSIS_DIR / symbol / "charts"
        
        if charts_dir.exists():
            # Key charts
            key_charts_dir = charts_dir / "key_charts"
            if key_charts_dir.exists():
                charts['key_charts'] = [f.name for f in key_charts_dir.glob("*.png")]
            
            # Technical analysis
            tech_charts_dir = charts_dir / "technical_analysis"  
            if tech_charts_dir.exists():
                charts['technical_analysis'] = [f.name for f in tech_charts_dir.glob("*.png")]
            
            # Financial analysis
            fin_charts_dir = charts_dir / "financial_analysis"
            if fin_charts_dir.exists():
                charts['financial_analysis'] = [f.name for f in fin_charts_dir.glob("*.png")]
                
        return charts
    
    def update_stock_data(self, symbol):
        """Update data for a specific stock"""
        try:
            # Run quick_update.py
            result = subprocess.run([
                'python', 'quick_update.py', symbol
            ], cwd=BASE_DIR, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"Successfully updated {symbol}")
                self.last_update[symbol] = datetime.now()
                return True
            else:
                logger.error(f"Error updating {symbol}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Exception updating {symbol}: {e}")
            return False
    
    def update_stock_charts(self, symbol):
        """Update charts for a specific stock"""
        try:
            commands = [
                f'python stock_analysis/{symbol}/analysis/create_{symbol.lower()}_charts.py',
                f'python stock_analysis/{symbol}/analysis/create_enhanced_{symbol.lower()}_charts.py',
                f'python stock_analysis/{symbol}/analysis/create_financial_charts.py',
                f'python stock_analysis/{symbol}/analysis/create_additional_charts.py'
            ]
            
            success_count = 0
            for cmd in commands:
                try:
                    result = subprocess.run(cmd.split(), cwd=BASE_DIR, capture_output=True, text=True, timeout=120)
                    if result.returncode == 0:
                        success_count += 1
                except:
                    continue
            
            logger.info(f"Updated {success_count}/{len(commands)} chart groups for {symbol}")
            return success_count > 0
        except Exception as e:
            logger.error(f"Exception updating charts for {symbol}: {e}")
            return False

# Initialize data manager
data_manager = StockDataManager()

@app.route('/')
def index():
    """Main dashboard page"""
    stocks = data_manager.get_active_stocks()
    return render_template('dashboard.html', stocks=stocks)

@app.route('/api/stocks')
def get_stocks():
    """API endpoint to get all stocks data"""
    stocks_data = []
    for symbol in data_manager.get_active_stocks():
        stock_data = data_manager.get_stock_data(symbol)
        if stock_data:
            stocks_data.append(stock_data)
    
    return jsonify(stocks_data)

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    """API endpoint to get specific stock data"""
    stock_data = data_manager.get_stock_data(symbol.upper())
    if stock_data:
        return jsonify(stock_data)
    return jsonify({'error': 'Stock not found'}), 404

@app.route('/api/stock/<symbol>/charts')
def get_stock_charts(symbol):
    """API endpoint to get stock charts"""
    charts = data_manager.get_stock_charts(symbol.upper())
    return jsonify(charts)

@app.route('/api/stock/<symbol>/reports')
def get_stock_reports(symbol):
    """API endpoint to get available reports for a stock"""
    try:
        symbol = symbol.upper()
        reports_dir = STOCK_ANALYSIS_DIR / symbol / "reports"
        
        available_reports = []
        if reports_dir.exists():
            for report_file in reports_dir.glob("*.html"):
                available_reports.append({
                    'filename': report_file.name,
                    'url': f'/stock_analysis/{symbol}/reports/{report_file.name}',
                    'size': report_file.stat().st_size,
                    'modified': report_file.stat().st_mtime
                })
        
        return jsonify({
            'symbol': symbol,
            'reports': available_reports,
            'count': len(available_reports)
        })
        
    except Exception as e:
        logger.error(f"Error getting reports for {symbol}: {e}")
        return jsonify({'error': 'Failed to get reports'}), 500

@app.route('/api/update/<symbol>')
def update_stock(symbol):
    """API endpoint to trigger stock update"""
    symbol = symbol.upper()
    success = data_manager.update_stock_data(symbol)
    
    if success:
        # Emit update to all connected clients
        stock_data = data_manager.get_stock_data(symbol)
        if stock_data:
            socketio.emit('stock_updated', stock_data)
        return jsonify({'success': True, 'message': f'{symbol} updated successfully'})
    
    return jsonify({'success': False, 'message': f'Failed to update {symbol}'}), 500

@app.route('/api/update/<symbol>/full')
def update_stock_full(symbol):
    """API endpoint to trigger full stock analysis update"""
    symbol = symbol.upper()
    
    # Update data first
    data_success = data_manager.update_stock_data(symbol)
    
    # Update charts
    charts_success = data_manager.update_stock_charts(symbol)
    
    if data_success or charts_success:
        # Emit update to all connected clients
        stock_data = data_manager.get_stock_data(symbol)
        if stock_data:
            socketio.emit('stock_updated', stock_data)
        return jsonify({
            'success': True, 
            'message': f'{symbol} full analysis completed',
            'data_updated': data_success,
            'charts_updated': charts_success
        })
    
    return jsonify({'success': False, 'message': f'Failed to update {symbol}'}), 500

@app.route('/stock/<symbol>')
def stock_detail(symbol):
    """Stock detail page"""
    symbol = symbol.upper()
    stock_data = data_manager.get_stock_data(symbol)
    charts = data_manager.get_stock_charts(symbol)
    
    if not stock_data:
        return "Stock not found", 404
    
    return render_template('stock_detail.html', 
                         stock=stock_data, 
                         charts=charts,
                         symbol=symbol)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@app.route('/stock_analysis/<path:filename>')
def serve_stock_analysis(filename):
    """Serve files from stock_analysis directory"""
    try:
        logger.info(f"Serving file: {filename}")
        
        # Use absolute path for send_from_directory
        stock_analysis_dir = BASE_DIR / 'stock_analysis'
        full_path = stock_analysis_dir / filename
        
        logger.info(f"Stock analysis dir: {stock_analysis_dir}")
        logger.info(f"Full path: {full_path}")
        logger.info(f"File exists: {full_path.exists()}")
        
        if not full_path.exists():
            logger.error(f"File does not exist: {full_path}")
            return f"File not found: {filename}", 404
            
        # Use absolute path string for send_from_directory
        return send_from_directory(str(stock_analysis_dir), filename)
        
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        return f"File not found: {filename} - {str(e)}", 404

@app.route('/debug/files')
def debug_files():
    """Debug route to check file system"""
    try:
        base_path = BASE_DIR / 'stock_analysis'
        vhm_reports_path = base_path / 'VHM' / 'reports'
        
        debug_info = {
            'base_dir': str(BASE_DIR),
            'stock_analysis_path': str(base_path),
            'stock_analysis_exists': base_path.exists(),
            'vhm_reports_path': str(vhm_reports_path),
            'vhm_reports_exists': vhm_reports_path.exists(),
            'working_directory': os.getcwd()
        }
        
        if vhm_reports_path.exists():
            debug_info['vhm_report_files'] = [f.name for f in vhm_reports_path.glob('*.html')]
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': str(e)})

def auto_update_stocks():
    """Automated stock updates"""
    logger.info("Starting automated stock updates")
    for symbol in data_manager.get_active_stocks():
        try:
            success = data_manager.update_stock_data(symbol)
            if success:
                stock_data = data_manager.get_stock_data(symbol)
                if stock_data:
                    socketio.emit('stock_updated', stock_data)
            time.sleep(10)  # Wait 10 seconds between updates
        except Exception as e:
            logger.error(f"Error in auto update for {symbol}: {e}")

def schedule_updates():
    """Schedule automated updates"""
    # Schedule updates every 5 minutes during market hours
    schedule.every(5).minutes.do(auto_update_stocks)
    
    # Full analysis at market close (15:30)
    schedule.every().day.at("15:30").do(lambda: auto_update_stocks())
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def start_scheduler():
    """Start the background scheduler"""
    scheduler_thread = threading.Thread(target=schedule_updates, daemon=True)
    scheduler_thread.start()
    logger.info("Background scheduler started")

if __name__ == '__main__':
    # Start background scheduler
    start_scheduler()
    
    # Run Flask app
    logger.info("Starting VNStock Dashboard on http://localhost:5000")
    socketio.run(app, host='localhost', port=5000, debug=False)