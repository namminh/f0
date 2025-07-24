#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VND Charts Creator - Updated to use real financial analysis
"""

import matplotlib.pyplot as plt
import pandas as pd
import json
import os

def load_data():
    """Load VND data from JSON files."""
    data = {}
    
    # Load intraday data
    intraday_file = "stock_analysis/VND/data/VND_intraday_data.json"
    if os.path.exists(intraday_file):
        with open(intraday_file, 'r', encoding='utf-8') as f:
            data['intraday'] = json.load(f)
    
    # Load balance sheet data
    balance_file = "stock_analysis/VND/data/VND_financial_data.json"
    if os.path.exists(balance_file):
        with open(balance_file, 'r', encoding='utf-8') as f:
            financial_data = json.load(f)
            data['balance_sheet'] = financial_data.get('balance_sheet', {})
    
    return data

def create_vnd_charts():
    """Tạo tất cả biểu đồ cho VND."""
    data = load_data()
    
    # Tạo thư mục charts nếu chưa có
    os.makedirs("stock_analysis/VND/charts/key_charts", exist_ok=True)
    os.makedirs("stock_analysis/VND/charts/detailed_charts", exist_ok=True)
    
    # Tạo key charts
    if 'intraday' in data:
        create_price_chart(data['intraday'])
        create_volume_chart(data['intraday'])
        create_buy_sell_chart(data['intraday'])
    
    # Tạo financial chart với template mới
    if 'balance_sheet' in data:
        create_financial_charts(data['balance_sheet'])
    
    print("Charts created for VND")

def create_price_chart(intraday_data):
    """Tạo biểu đồ giá trong ngày."""
    if not intraday_data or 'data' not in intraday_data or not intraday_data['data']:
        return

    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time')

    plt.figure(figsize=(12, 6))
    plt.plot(df['time'], df['price'], linewidth=2, color='blue')
    plt.title('Xu hướng giá trong ngày - VND')
    plt.xlabel('Thời gian')
    plt.ylabel('Giá (VND)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("stock_analysis/VND/charts/key_charts/price_trend.png")
    plt.close()

def create_volume_chart(intraday_data):
    """Tạo biểu đồ khối lượng theo giờ."""
    if not intraday_data or 'data' not in intraday_data or not intraday_data['data']:
        return

    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df['hour'] = df['time'].dt.hour

    volume_by_hour = df.groupby('hour')['volume'].sum()

    plt.figure(figsize=(12, 6))
    volume_by_hour.plot(kind='bar', title='Khối lượng giao dịch theo giờ - VND')
    plt.xlabel('Giờ')
    plt.ylabel('Khối lượng')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("stock_analysis/VND/charts/key_charts/volume_by_hour.png")
    plt.close()

def create_buy_sell_chart(intraday_data):
    """Tạo biểu đồ mua/bán."""
    if not intraday_data or 'data' not in intraday_data or not intraday_data['data']:
        return

    df = pd.DataFrame(intraday_data['data'])
    buy_volume = df[df['match_type'] == 'Buy']['volume'].sum()
    sell_volume = df[df['match_type'] == 'Sell']['volume'].sum()

    plt.figure(figsize=(8, 8))
    plt.pie([buy_volume, sell_volume], labels=['Mua', 'Bán'], autopct='%1.1f%%', startangle=90)
    plt.title('Tỷ lệ khối lượng Mua vs. Bán - VND')
    plt.savefig("stock_analysis/VND/charts/key_charts/buy_vs_sell.png")
    plt.close()

def create_financial_charts(balance_sheet_data):
    """Tạo biểu đồ tài chính thực sự cho VND."""
    # Import template function
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'chart_templates'))
    from financial_chart_template import create_real_financial_chart
    
    # Use real financial chart template
    output_path = "stock_analysis/VND/charts/detailed_charts/financial_analysis.png"
    success = create_real_financial_chart(balance_sheet_data, "VND", output_path)
    
    if not success:
        print("VND: No financial chart created - insufficient data")

if __name__ == "__main__":
    create_vnd_charts()
