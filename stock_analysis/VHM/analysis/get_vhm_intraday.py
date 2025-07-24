#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stock_data_collector import StockDataCollector
import json
import pandas as pd
from datetime import datetime

def get_vhm_intraday():
    """Lấy dữ liệu intraday của VHM"""
    
    # Khởi tạo collector
    collector = StockDataCollector(data_source='VCI')
    
    symbol = 'VHM'
    print(f'Dang lay du lieu intraday cho {symbol}...')
    
    # Lấy dữ liệu intraday
    intraday_data = collector.get_intraday_data(symbol, page_size=50000)
    
    if 'error' in intraday_data:
        print(f'Loi: {intraday_data["error"]}')
        return None
    
    # Lưu dữ liệu intraday
    with open('VHM_intraday_data.json', 'w', encoding='utf-8') as f:
        json.dump(intraday_data, f, ensure_ascii=False, indent=2)
    
    print(f'Da lay {intraday_data["data_points"]} ban ghi intraday cho {symbol}')
    
    # Lưu vào CSV để dễ xem
    if "data" in intraday_data and isinstance(intraday_data["data"], list):
        df = pd.DataFrame(intraday_data["data"])
        csv_path = f'{symbol}_intraday.csv'
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f'Da luu du lieu intraday vao {csv_path}')
    
    return intraday_data

if __name__ == "__main__":
    get_vhm_intraday()