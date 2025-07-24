import json
import pandas as pd
import sys
import codecs
from datetime import datetime
import numpy as np

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

def analyze_vix_data():
    """Phân tích dữ liệu của VIX."""
    # Load data
    try:
        with open("stock_analysis/VIX/data/VIX_balance_sheet.json", "r", encoding="utf-8") as f:
            balance_sheet_data = json.load(f)
    except FileNotFoundError:
        balance_sheet_data = None
    
    try:
        with open("stock_analysis/VIX/data/VIX_intraday_data.json", "r", encoding="utf-8") as f:
            intraday_data = json.load(f)
    except FileNotFoundError:
        intraday_data = None

    try:
        with open("stock_analysis/VIX/data/VIX_financial_ratios.json", "r", encoding="utf-8") as f:
            financial_ratios_data = json.load(f)
    except FileNotFoundError:
        financial_ratios_data = None

    # Analysis
    print("=== PHÂN TÍCH CỔ PHIẾU VIX ===")

    # Balance Sheet Analysis
    if balance_sheet_data and 'data' in balance_sheet_data and balance_sheet_data['data']:
        print("\n--- Phân tích Bảng cân đối kế toán ---")
        df_balance_sheet = pd.DataFrame(balance_sheet_data['data'])
        print(df_balance_sheet.head())
    else:
        print("\n--- Không có dữ liệu Bảng cân đối kế toán để phân tích ---")

    # Financial Ratios Analysis
    if financial_ratios_data and 'data' in financial_ratios_data and financial_ratios_data['data']:
        print("\n--- Phân tích Tỷ số tài chính ---")
        df_ratios = pd.DataFrame(financial_ratios_data['data'])
        print(df_ratios.head())
    else:
        print("\n--- Không có dữ liệu Tỷ số tài chính để phân tích ---")

    # Intraday Data Analysis
    if intraday_data and 'data' in intraday_data and intraday_data['data']:
        print("\n--- Phân tích Dữ liệu trong ngày VIX ---")
        df_intraday = pd.DataFrame(intraday_data['data'])
        
        # Convert time to datetime
        df_intraday['time'] = pd.to_datetime(df_intraday['time'])
        df_intraday['hour'] = df_intraday['time'].dt.hour
        
        print(f"Tổng số điểm dữ liệu: {len(df_intraday)}")
        print(f"Thời gian giao dịch: {df_intraday['time'].min()} đến {df_intraday['time'].max()}")
        print(f"Giá cao nhất: {df_intraday['price'].max():.2f}")
        print(f"Giá thấp nhất: {df_intraday['price'].min():.2f}")
        print(f"Giá trung bình: {df_intraday['price'].mean():.2f}")
        print(f"Tổng khối lượng giao dịch: {df_intraday['volume'].sum():,}")
        
        # Volume by hour analysis
        volume_by_hour = df_intraday.groupby('hour')['volume'].sum()
        print("\n--- Khối lượng giao dịch theo giờ ---")
        for hour, volume in volume_by_hour.items():
            print(f"Giờ {hour:02d}: {volume:,}")
        
        # Buy vs Sell analysis
        buy_volume = df_intraday[df_intraday['match_type'] == 'Buy']['volume'].sum()
        sell_volume = df_intraday[df_intraday['match_type'] == 'Sell']['volume'].sum()
        print(f"\nKhối lượng mua: {buy_volume:,}")
        print(f"Khối lượng bán: {sell_volume:,}")
        print(f"Tỷ lệ mua/bán: {buy_volume/sell_volume:.2f}" if sell_volume > 0 else "Tỷ lệ mua/bán: N/A")
        
        # Price volatility analysis
        price_std = df_intraday['price'].std()
        price_range = df_intraday['price'].max() - df_intraday['price'].min()
        print(f"\nĐộ biến động giá (std): {price_std:.2f}")
        print(f"Khoảng giá: {price_range:.2f}")
        
    else:
        print("\n--- Không có dữ liệu trong ngày để phân tích ---")

if __name__ == "__main__":
    analyze_vix_data()
