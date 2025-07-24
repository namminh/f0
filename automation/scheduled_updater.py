#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOMINUS AGENT - Scheduled Stock Updater
Hệ thống tự động cập nhật định kỳ cho VNStock

Usage:
    python automation/scheduled_updater.py --time 11:00
    python automation/scheduled_updater.py --time 15:00
    python automation/scheduled_updater.py --mode quick
    python automation/scheduled_updater.py --mode comprehensive
"""

import json
import time
import logging
import argparse
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class ScheduledStockUpdater:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.config_file = self.base_dir / "automation" / "config" / "stocks_config.json"
        self.log_file = self.base_dir / "automation" / "logs" / f"scheduled_update_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Tạo thư mục logs nếu chưa có
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Setup logging - Windows compatible
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load config
        self.load_config()
        
    def load_config(self):
        """Load cấu hình từ stocks_config.json"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self.logger.info(f"SUCCESS Loaded config: {len(self.config['active_stocks'])} active stocks")
        except Exception as e:
            self.logger.error(f"❌ Failed to load config: {e}")
            sys.exit(1)
    
    def is_market_hours(self):
        """Kiểm tra có phải giờ thị trường không"""
        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime('%A').lower()
        
        # Kiểm tra ngày làm việc
        if current_day not in self.config['market_hours']['days']:
            return False
            
        # Kiểm tra giờ thị trường
        start_time = datetime.strptime(self.config['market_hours']['start'], '%H:%M').time()
        end_time = datetime.strptime(self.config['market_hours']['end'], '%H:%M').time()
        
        return start_time <= current_time <= end_time
    
    def run_stock_update(self, symbol, mode='quick'):
        """Cập nhật 1 cổ phiếu"""
        try:
            start_time = time.time()
            
            if mode == 'quick':
                # Quick update - chỉ cập nhật dữ liệu
                cmd = [sys.executable, 'quick_update.py', symbol]
            elif mode == 'smart':
                # Smart analysis - 3 biểu đồ cốt lõi
                cmd = [sys.executable, 'automation/smart_analysis.py', symbol]
            elif mode == 'comprehensive':
                # Comprehensive analysis - 18 biểu đồ đầy đủ
                cmd = [sys.executable, 'automation/comprehensive_stock_analysis.py', symbol]
            else:
                raise ValueError(f"Invalid mode: {mode}")
            
            # Chạy command
            result = subprocess.run(
                cmd,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.logger.info(f"SUCCESS {symbol} updated successfully ({mode}) - {duration:.1f}s")
                return {
                    'symbol': symbol,
                    'status': 'success',
                    'duration': duration,
                    'output': result.stdout
                }
            else:
                self.logger.error(f"ERROR {symbol} failed ({mode}): {result.stderr}")
                return {
                    'symbol': symbol,
                    'status': 'failed',
                    'duration': duration,
                    'error': result.stderr
                }
                
        except Exception as e:
            self.logger.error(f"EXCEPTION updating {symbol}: {e}")
            return {
                'symbol': symbol,
                'status': 'error',
                'error': str(e)
            }
    
    def run_parallel_updates(self, mode='quick'):
        """Cập nhật song song tất cả cổ phiếu"""
        stocks = self.config['active_stocks']
        max_workers = self.config.get('parallel_workers', 3)
        
        self.logger.info(f"STARTING {mode} update for {len(stocks)} stocks (parallel: {max_workers})")
        
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_stock = {
                executor.submit(self.run_stock_update, stock, mode): stock 
                for stock in stocks
            }
            
            # Collect results
            for future in as_completed(future_to_stock):
                result = future.result()
                results.append(result)
        
        total_duration = time.time() - start_time
        
        # Tính toán thống kê
        successful = len([r for r in results if r['status'] == 'success'])
        failed = len([r for r in results if r['status'] in ['failed', 'error']])
        
        self.logger.info(f"COMPLETED Update - Success: {successful}, Failed: {failed}, Total time: {total_duration:.1f}s")
        
        # Log chi tiết
        for result in results:
            if result['status'] == 'success':
                self.logger.info(f"  SUCCESS {result['symbol']}: {result['duration']:.1f}s")
            else:
                self.logger.error(f"  ERROR {result['symbol']}: {result.get('error', 'Unknown error')}")
        
        return results
    
    def scheduled_update_11h(self):
        """Cập nhật lúc 11h - Quick mode"""
        self.logger.info("⏰ 11:00 AM Scheduled Update Started (QUICK MODE)")
        
        if not self.is_market_hours():
            self.logger.warning("⚠️ Outside market hours - skipping update")
            return
        
        results = self.run_parallel_updates(mode='quick')
        
        # Gửi notification nếu có lỗi
        failed_count = len([r for r in results if r['status'] != 'success'])
        if failed_count > 0 and self.config['notification']['error_alerts']:
            self.logger.warning(f"⚠️ 11:00 Update - {failed_count} stocks failed")
        
        self.logger.info("✅ 11:00 AM Update Completed")
    
    def scheduled_update_15h(self):
        """Cập nhật lúc 15h - Smart mode với báo cáo cuối ngày"""
        self.logger.info("⏰ 15:00 PM Scheduled Update Started (SMART MODE)")
        
        if not self.is_market_hours():
            self.logger.warning("⚠️ Outside market hours - skipping update")
            return
        
        results = self.run_parallel_updates(mode='smart')
        
        # Tạo báo cáo cuối ngày
        if self.config['notification']['success_summary']:
            self.generate_daily_summary(results)
        
        self.logger.info("✅ 15:00 PM Update Completed")
    
    def generate_daily_summary(self, results):
        """Tạo báo cáo tóm tắt cuối ngày"""
        try:
            successful = [r for r in results if r['status'] == 'success']
            failed = [r for r in results if r['status'] != 'success']
            
            summary = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.now().strftime('%H:%M:%S'),
                'total_stocks': len(results),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': f"{len(successful)/len(results)*100:.1f}%",
                'successful_stocks': [r['symbol'] for r in successful],
                'failed_stocks': [{'symbol': r['symbol'], 'error': r.get('error', 'Unknown')} for r in failed]
            }
            
            # Lưu báo cáo
            summary_file = self.base_dir / "automation" / "logs" / f"daily_summary_{datetime.now().strftime('%Y%m%d')}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"📋 Daily summary saved: {summary_file}")
            self.logger.info(f"📊 Success rate: {summary['success_rate']} ({summary['successful']}/{summary['total_stocks']})")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate daily summary: {e}")
    
    def run_specific_time(self, target_time):
        """Chạy tại thời điểm cụ thể (được gọi bởi Task Scheduler)"""
        current_time = datetime.now().strftime('%H:%M')
        self.logger.info(f"🔄 Manual execution at {current_time} (target: {target_time})")
        
        if target_time == "11:00":
            self.scheduled_update_11h()
        elif target_time == "15:00":
            self.scheduled_update_15h()
        else:
            # Mặc định smart mode
            self.logger.info(f"⏰ Custom time update: {target_time}")
            results = self.run_parallel_updates(mode='smart')
    
    def run_continuous_monitoring(self):
        """Chạy continuous monitoring (development mode)"""
        self.logger.info("🔄 Starting continuous monitoring mode...")
        
        while True:
            now = datetime.now()
            current_time = now.time()
            
            # Kiểm tra 11:00
            if current_time.hour == 11 and current_time.minute == 0:
                self.scheduled_update_11h()
                time.sleep(60)  # Tránh chạy lại trong cùng phút
            
            # Kiểm tra 15:00
            elif current_time.hour == 15 and current_time.minute == 0:
                self.scheduled_update_15h()
                time.sleep(60)  # Tránh chạy lại trong cùng phút
            
            else:
                time.sleep(30)  # Kiểm tra mỗi 30 giây

def main():
    parser = argparse.ArgumentParser(description='DOMINUS AGENT Scheduled Stock Updater')
    parser.add_argument('--time', help='Target time for update (e.g., 11:00, 15:00)')
    parser.add_argument('--mode', choices=['quick', 'smart', 'comprehensive'], default='smart',
                        help='Update mode')
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring')
    
    args = parser.parse_args()
    
    updater = ScheduledStockUpdater()
    
    if args.continuous:
        updater.run_continuous_monitoring()
    elif args.time:
        updater.run_specific_time(args.time)
    else:
        # Manual mode - chạy ngay với mode đã chọn
        updater.run_parallel_updates(mode=args.mode)

if __name__ == "__main__":
    main()