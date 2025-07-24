#!/usr/bin/env python3
"""
Multi-Stock Updater - Hệ thống cập nhật tự động cho nhiều cổ phiếu
Sử dụng: python automation/multi_stock_updater.py [options]
"""

import sys
import json
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("Warning: 'schedule' module not found. Install with: pip install schedule")

class MultiStockUpdater:
    def __init__(self):
        self.config_file = Path("automation/config/stocks_config.json")
        self.config = self.load_config()
        self.is_running = False
        
    def load_config(self):
        """Load configuration from file"""
        if not self.config_file.exists():
            self.create_default_config()
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_default_config(self):
        """Create default configuration"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        default_config = {
            "active_stocks": ["VIX", "HSG", "VHM", "DIG"],
            "update_frequency": {
                "quick_update": 300,      # 5 minutes
                "full_analysis": 1800,    # 30 minutes
                "daily_report": "15:30"   # End of trading day
            },
            "market_hours": {
                "start": "09:00",
                "end": "15:00",
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
            },
            "parallel_workers": 3,
            "retry_attempts": 2,
            "notification": {
                "enabled": True,
                "success_summary": True,
                "error_alerts": True
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
    
    def is_market_hours(self):
        """Check if current time is within market hours"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%A").lower()
        
        start_time = self.config["market_hours"]["start"]
        end_time = self.config["market_hours"]["end"]
        trading_days = self.config["market_hours"]["days"]
        
        return (current_day in trading_days and 
                start_time <= current_time <= end_time)
    
    def update_single_stock(self, symbol):
        """Update a single stock with retry mechanism"""
        for attempt in range(self.config["retry_attempts"] + 1):
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating {symbol} (attempt {attempt + 1})")
                
                # Quick update
                result = subprocess.run(
                    ["python", "quick_update.py", symbol],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    # Run analysis
                    analysis_result = subprocess.run(
                        ["python", f"stock_analysis/{symbol}/analysis/analyze_{symbol.lower()}_data.py"],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    return {
                        "symbol": symbol,
                        "status": "success",
                        "timestamp": datetime.now().isoformat(),
                        "attempt": attempt + 1,
                        "output": result.stdout.strip()
                    }
                else:
                    raise Exception(f"Update failed: {result.stderr}")
                    
            except Exception as e:
                if attempt == self.config["retry_attempts"]:
                    return {
                        "symbol": symbol,
                        "status": "error",
                        "timestamp": datetime.now().isoformat(),
                        "attempt": attempt + 1,
                        "error": str(e)
                    }
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Retry {symbol} in 30 seconds...")
                    time.sleep(30)
    
    def update_all_stocks(self, parallel=True):
        """Update all active stocks"""
        stocks = self.config["active_stocks"]
        results = []
        
        if parallel and len(stocks) > 1:
            # Parallel execution
            with ThreadPoolExecutor(max_workers=self.config["parallel_workers"]) as executor:
                future_to_stock = {executor.submit(self.update_single_stock, stock): stock for stock in stocks}
                
                for future in as_completed(future_to_stock):
                    result = future.result()
                    results.append(result)
        else:
            # Sequential execution
            for stock in stocks:
                result = self.update_single_stock(stock)
                results.append(result)
        
        return results
    
    def generate_full_analysis(self, symbols=None):
        """Generate full analysis with charts for specified symbols"""
        symbols = symbols or self.config["active_stocks"]
        results = []
        
        for symbol in symbols:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Full analysis for {symbol}")
                
                # Create charts
                chart_result = subprocess.run(
                    ["python", f"stock_analysis/{symbol}/analysis/create_{symbol.lower()}_charts.py"],
                    capture_output=True,
                    text=True,
                    timeout=180
                )
                
                results.append({
                    "symbol": symbol,
                    "charts_status": "success" if chart_result.returncode == 0 else "error",
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "charts_status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    def print_summary(self, results, operation="Update"):
        """Print operation summary"""
        print(f"\n=== {operation} Summary ===")
        success_count = sum(1 for r in results if r.get("status") == "success" or r.get("charts_status") == "success")
        total_count = len(results)
        
        print(f"Total: {total_count}, Success: {success_count}, Failed: {total_count - success_count}")
        
        for result in results:
            symbol = result["symbol"]
            status = result.get("status") or result.get("charts_status", "unknown")
            timestamp = result["timestamp"]
            
            if status == "success":
                print(f"SUCCESS {symbol}: Success at {timestamp}")
            else:
                error = result.get("error", "Unknown error")
                print(f"FAILED {symbol}: Failed - {error}")
        
        print(f"=== End {operation} Summary ===\n")
    
    def quick_update_job(self):
        """Job for quick updates during market hours"""
        if not self.is_market_hours():
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Outside market hours, skipping quick update")
            return
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting scheduled quick update")
        results = self.update_all_stocks(parallel=True)
        self.print_summary(results, "Quick Update")
    
    def full_analysis_job(self):
        """Job for full analysis with charts"""
        if not self.is_market_hours():
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Outside market hours, skipping full analysis")
            return
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting scheduled full analysis")
        
        # Quick update first
        update_results = self.update_all_stocks(parallel=True)
        self.print_summary(update_results, "Data Update")
        
        # Then generate charts
        analysis_results = self.generate_full_analysis()
        self.print_summary(analysis_results, "Chart Generation")
    
    def daily_report_job(self):
        """Job for end-of-day comprehensive report"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting daily report generation")
        
        # Full update and analysis
        update_results = self.update_all_stocks(parallel=True)
        analysis_results = self.generate_full_analysis()
        
        # Generate portfolio report
        try:
            subprocess.run(["python", "automation/report_generator.py", "--portfolio"], timeout=300)
            print("✅ Portfolio report generated")
        except Exception as e:
            print(f"❌ Portfolio report failed: {e}")
        
        self.print_summary(update_results, "Daily Data Update")
        self.print_summary(analysis_results, "Daily Analysis")
    
    def start_scheduler(self):
        """Start the automated scheduler"""
        if not SCHEDULE_AVAILABLE:
            print("❌ Scheduler requires 'schedule' module. Install with: pip install schedule")
            return
            
        print("🚀 Starting Multi-Stock Updater Scheduler")
        print(f"📊 Active stocks: {', '.join(self.config['active_stocks'])}")
        print(f"⏰ Market hours: {self.config['market_hours']['start']} - {self.config['market_hours']['end']}")
        print(f"🔄 Quick updates every {self.config['update_frequency']['quick_update']} seconds")
        print(f"📈 Full analysis every {self.config['update_frequency']['full_analysis']} seconds")
        print(f"📋 Daily report at {self.config['update_frequency']['daily_report']}")
        print("Press Ctrl+C to stop\n")
        
        # Schedule jobs
        schedule.every(self.config['update_frequency']['quick_update']).seconds.do(self.quick_update_job)
        schedule.every(self.config['update_frequency']['full_analysis']).seconds.do(self.full_analysis_job)
        schedule.every().day.at(self.config['update_frequency']['daily_report']).do(self.daily_report_job)
        
        self.is_running = True
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            print("\n🛑 Stopping Multi-Stock Updater...")
            self.is_running = False

def main():
    parser = argparse.ArgumentParser(description='Multi-Stock Updater')
    parser.add_argument('--all', action='store_true', help='Update all stocks once')
    parser.add_argument('--schedule', action='store_true', help='Start scheduler')
    parser.add_argument('--full', action='store_true', help='Full analysis with charts')
    parser.add_argument('--symbols', nargs='+', help='Specific symbols to update')
    parser.add_argument('--config', action='store_true', help='Show current configuration')
    
    args = parser.parse_args()
    updater = MultiStockUpdater()
    
    if args.config:
        print(json.dumps(updater.config, indent=2, ensure_ascii=False))
        return
    
    if args.schedule:
        updater.start_scheduler()
    elif args.all:
        print("🔄 Updating all stocks...")
        results = updater.update_all_stocks(parallel=True)
        updater.print_summary(results)
    elif args.full:
        symbols = args.symbols or updater.config["active_stocks"]
        print(f"📊 Full analysis for: {', '.join(symbols)}")
        
        # Update data first
        update_results = updater.update_all_stocks(parallel=True)
        updater.print_summary(update_results, "Data Update")
        
        # Generate charts
        analysis_results = updater.generate_full_analysis(symbols)
        updater.print_summary(analysis_results, "Chart Generation")
    elif args.symbols:
        print(f"Updating specific stocks: {', '.join(args.symbols)}")
        updater.config["active_stocks"] = args.symbols
        results = updater.update_all_stocks(parallel=True)
        updater.print_summary(results)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()