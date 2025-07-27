#!/usr/bin/env python3
"""
Batch update script cho tất cả dữ liệu intraday và tạo lại biểu đồ
"""

import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from stock_data_collector import StockDataCollector

class BatchUpdater:
    def __init__(self):
        self.collector = StockDataCollector()
        self.updated_symbols = []
        self.failed_symbols = []
    
    def find_existing_symbols(self):
        """Tìm tất cả mã cổ phiếu đã có trong hệ thống"""
        symbols = []
        stock_dir = Path("stock_analysis")
        
        if stock_dir.exists():
            for item in stock_dir.iterdir():
                if item.is_dir() and (item / "data").exists():
                    symbols.append(item.name)
        
        return sorted(symbols)
    
    def update_intraday_data(self, symbol):
        """Cập nhật dữ liệu intraday cho một mã"""
        try:
            data_dir = Path(f"stock_analysis/{symbol}/data")
            file_path = data_dir / f"{symbol}_intraday_data.json"
            
            print(f"  📊 Fetching intraday data...")
            data = self.collector.get_intraday_data(symbol)
            
            if "error" in data:
                print(f"  ❌ Error: {data['error']}")
                return False
            
            # Backup file cũ
            if file_path.exists():
                backup_path = data_dir / f"{symbol}_intraday_backup_{int(time.time())}.json"
                file_path.rename(backup_path)
            
            # Lưu dữ liệu mới
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            data_points = data.get('data_points', 0)
            print(f"  ✅ Updated: {data_points} data points")
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return False
    
    def regenerate_charts(self, symbol):
        """Tạo lại biểu đồ cho một mã"""
        try:
            chart_script = f"stock_analysis/{symbol}/analysis/create_{symbol.lower()}_charts.py"
            
            if not Path(chart_script).exists():
                print(f"  ⚠️  Chart script not found: {chart_script}")
                return False
            
            print(f"  📈 Regenerating charts...")
            result = subprocess.run(['python', chart_script], 
                                  capture_output=True, text=True, cwd=".")
            
            if result.returncode == 0:
                print(f"  ✅ Charts updated successfully")
                return True
            else:
                print(f"  ❌ Chart generation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error regenerating charts: {str(e)}")
            return False
    
    def update_symbol(self, symbol):
        """Cập nhật đầy đủ cho một mã cổ phiếu"""
        print(f"\n🔄 Updating {symbol}...")
        
        # Cập nhật dữ liệu intraday
        if not self.update_intraday_data(symbol):
            self.failed_symbols.append(symbol)
            return False
        
        # Tạo lại biểu đồ
        if not self.regenerate_charts(symbol):
            print(f"  ⚠️  Data updated but charts failed for {symbol}")
        
        self.updated_symbols.append(symbol)
        return True
    
    def run_batch_update(self):
        """Chạy batch update cho tất cả mã"""
        print("🚀 Starting batch update...")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        symbols = self.find_existing_symbols()
        
        if not symbols:
            print("❌ No existing symbols found")
            return
        
        print(f"📋 Found {len(symbols)} symbols: {', '.join(symbols)}")
        
        start_time = time.time()
        
        for i, symbol in enumerate(symbols, 1):
            print(f"\n--- {i}/{len(symbols)} ---")
            self.update_symbol(symbol)
            
            # Delay giữa các request để tránh rate limit
            if i < len(symbols):
                time.sleep(2)
        
        # Tổng kết
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n" + "="*50)
        print(f"📊 BATCH UPDATE SUMMARY")
        print(f"="*50)
        print(f"⏱️  Duration: {duration:.1f} seconds")
        print(f"✅ Successfully updated: {len(self.updated_symbols)}")
        print(f"❌ Failed: {len(self.failed_symbols)}")
        
        if self.updated_symbols:
            print(f"\n✅ Updated symbols: {', '.join(self.updated_symbols)}")
        
        if self.failed_symbols:
            print(f"\n❌ Failed symbols: {', '.join(self.failed_symbols)}")
        
        print(f"\n🎉 Batch update completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    updater = BatchUpdater()
    updater.run_batch_update()

if __name__ == "__main__":
    main()