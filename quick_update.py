#!/usr/bin/env python3
"""
Script nhanh để cập nhật dữ liệu intraday cho một hoặc nhiều mã cổ phiếu
Sử dụng: python quick_update.py [SYMBOL1] [SYMBOL2] ...
Ví dụ: python quick_update.py VIX HSG
"""

import sys
import json
from pathlib import Path
from stock_data_collector import StockDataCollector
from datetime import datetime

def quick_update_intraday(symbols):
    """
    Cập nhật nhanh dữ liệu intraday
    """
    collector = StockDataCollector()
    
    for symbol in symbols:
        symbol = symbol.upper()
        data_dir = Path(f"stock_analysis/{symbol}/data")
        
        if not data_dir.exists():
            print(f"Directory not found: {data_dir}")
            continue
        
        print(f"Updating {symbol}...")
        
        try:
            # Lấy dữ liệu mới
            data = collector.get_intraday_data(symbol)
            
            if "error" in data:
                print(f"Error: {data['error']}")
                continue
            
            # Lưu file
            file_path = data_dir / f"{symbol}_intraday_data.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            # Hiển thị thông tin
            data_points = data.get('data_points', 0)
            timestamp = data.get('timestamp', datetime.now().isoformat())
            
            print(f"Success {symbol}: {data_points} data points")
            print(f"   Updated: {timestamp}")
            
        except Exception as e:
            print(f"Error updating {symbol}: {str(e)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_update.py [SYMBOL1] [SYMBOL2] ...")
        print("Example: python quick_update.py VIX HSG")
        
        # Tự động tìm tất cả mã có sẵn
        stock_dir = Path("stock_analysis")
        if stock_dir.exists():
            available = []
            for item in stock_dir.iterdir():
                if item.is_dir() and (item / "data").exists():
                    available.append(item.name)
            
            if available:
                print(f"\nAvailable symbols: {', '.join(sorted(available))}")
                choice = input("Update all? (y/n): ").strip().lower()
                if choice == 'y':
                    quick_update_intraday(available)
        return
    
    symbols = sys.argv[1:]
    quick_update_intraday(symbols)

if __name__ == "__main__":
    main()