#!/usr/bin/env python3
"""
VHM Intraday Data Analysis
Phân tích dữ liệu intraday VHM mới nhất
"""

import json
import pandas as pd
import sys
import codecs
from datetime import datetime
import numpy as np

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

def analyze_vhm_intraday():
    """Phân tích dữ liệu intraday VHM."""
    try:
        with open("../data/VHM_intraday_data.json", "r", encoding="utf-8") as f:
            intraday_data = json.load(f)
    except FileNotFoundError:
        print("Không tìm thấy file dữ liệu VHM intraday")
        return

    print("=== PHÂN TÍCH INTRADAY VHM ===")

    if intraday_data and 'data' in intraday_data and intraday_data['data']:
        df_intraday = pd.DataFrame(intraday_data['data'])
        
        # Convert time to datetime
        df_intraday['time'] = pd.to_datetime(df_intraday['time'])
        df_intraday['hour'] = df_intraday['time'].dt.hour
        
        print(f"Tổng số điểm dữ liệu: {len(df_intraday):,}")
        print(f"Thời gian giao dịch: {df_intraday['time'].min()} đến {df_intraday['time'].max()}")
        print(f"Giá cao nhất: {df_intraday['price'].max():.2f} VND")
        print(f"Giá thấp nhất: {df_intraday['price'].min():.2f} VND")
        print(f"Giá trung bình: {df_intraday['price'].mean():.2f} VND")
        print(f"Tổng khối lượng: {df_intraday['volume'].sum():,} cổ phiếu")
        
        # Price change
        first_price = df_intraday.iloc[0]['price']
        last_price = df_intraday.iloc[-1]['price']
        price_change = last_price - first_price
        price_change_pct = (price_change / first_price) * 100
        
        print(f"Giá mở cửa: {first_price:.2f} VND")
        print(f"Giá hiện tại: {last_price:.2f} VND")
        print(f"Thay đổi: {price_change:+.2f} VND ({price_change_pct:+.2f}%)")
        
        # Volume by hour analysis
        volume_by_hour = df_intraday.groupby('hour')['volume'].sum()
        print("\n--- Khối lượng giao dịch theo giờ ---")
        for hour, volume in volume_by_hour.items():
            print(f"Giờ {hour:02d}: {volume:,} cổ phiếu")
        
        # Buy vs Sell analysis
        buy_volume = df_intraday[df_intraday['match_type'] == 'Buy']['volume'].sum()
        sell_volume = df_intraday[df_intraday['match_type'] == 'Sell']['volume'].sum()
        print(f"\nKhối lượng mua: {buy_volume:,}")
        print(f"Khối lượng bán: {sell_volume:,}")
        if sell_volume > 0:
            print(f"Tỷ lệ mua/bán: {buy_volume/sell_volume:.2f}")
        
        # Price volatility
        price_std = df_intraday['price'].std()
        price_range = df_intraday['price'].max() - df_intraday['price'].min()
        volatility_pct = (price_std / df_intraday['price'].mean()) * 100
        
        print(f"\nĐộ biến động giá (std): {price_std:.2f}")
        print(f"Khoảng biến động: {price_range:.2f} VND")
        print(f"Độ biến động (%): {volatility_pct:.2f}%")
        
        # Trading intensity analysis
        peak_hour = volume_by_hour.idxmax()
        peak_volume = volume_by_hour.max()
        print(f"\nGiờ giao dịch sôi động nhất: {peak_hour:02d}h với {peak_volume:,} cổ phiếu")
        
        # Price trend analysis
        price_trend = "Tăng" if price_change > 0 else "Giảm" if price_change < 0 else "Đi ngang"
        momentum = "Mạnh" if abs(price_change_pct) > 2 else "Vừa phải" if abs(price_change_pct) > 0.5 else "Yếu"
        
        print(f"\nXu hướng giá: {price_trend} ({momentum})")
        
        # Data update info
        timestamp = intraday_data.get('timestamp', 'N/A')
        data_points = intraday_data.get('data_points', len(df_intraday))
        print(f"\nCập nhật lúc: {timestamp}")
        print(f"Nguồn dữ liệu: {intraday_data.get('data_source', 'VCI')}")
        
    else:
        print("Không có dữ liệu intraday để phân tích")

if __name__ == "__main__":
    analyze_vhm_intraday()