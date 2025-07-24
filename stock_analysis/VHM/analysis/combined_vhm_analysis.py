#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def combined_vhm_analysis():
    """Phân tích kết hợp dữ liệu intraday và tài chính VHM"""
    
    print("=" * 80)
    print("PHAN TICH KET HOP DU LIEU INTRADAY VA TAI CHINH VHM")
    print("=" * 80)
    
    # Đọc dữ liệu tài chính
    with open('VHM_financial_data.json', 'r', encoding='utf-8') as f:
        financial_data = json.load(f)
    
    # Đọc dữ liệu intraday
    with open('VHM_intraday_data.json', 'r', encoding='utf-8') as f:
        intraday_data = json.load(f)
    
    # 1. Phân tích dữ liệu intraday
    print("\n1. PHAN TICH DU LIEU INTRADAY NGAY 17/07/2025:")
    
    df_intraday = pd.DataFrame(intraday_data['data'])
    df_intraday['time'] = pd.to_datetime(df_intraday['time'])
    df_intraday = df_intraday.sort_values('time')
    
    # Thông tin cơ bản
    print(f"   - Tong so giao dich: {len(df_intraday):,} giao dich")
    print(f"   - Thoi gian dau tien: {df_intraday['time'].min()}")
    print(f"   - Thoi gian cuoi cung: {df_intraday['time'].max()}")
    print(f"   - Gia cao nhat: {df_intraday['price'].max():,.1f} VND")
    print(f"   - Gia thap nhat: {df_intraday['price'].min():,.1f} VND")
    print(f"   - Gia dong cua: {df_intraday['price'].iloc[-1]:,.1f} VND")
    
    # Phân tích khối lượng
    total_volume = df_intraday['volume'].sum()
    total_value = (df_intraday['price'] * df_intraday['volume']).sum()
    avg_price = total_value / total_volume if total_volume > 0 else 0
    
    print(f"   - Tong khoi luong: {total_volume:,} co phieu")
    print(f"   - Tong gia tri: {total_value:,.0f} VND")
    print(f"   - Gia trung binh: {avg_price:,.1f} VND")
    
    # Phân tích lệnh mua/bán
    buy_orders = df_intraday[df_intraday['match_type'] == 'Buy']
    sell_orders = df_intraday[df_intraday['match_type'] == 'Sell']
    
    print(f"   - Lenh mua: {len(buy_orders):,} ({len(buy_orders)/len(df_intraday)*100:.1f}%)")
    print(f"   - Lenh ban: {len(sell_orders):,} ({len(sell_orders)/len(df_intraday)*100:.1f}%)")
    
    if len(buy_orders) > 0 and len(sell_orders) > 0:
        buy_volume = buy_orders['volume'].sum()
        sell_volume = sell_orders['volume'].sum()
        buy_value = (buy_orders['price'] * buy_orders['volume']).sum()
        sell_value = (sell_orders['price'] * sell_orders['volume']).sum()
        
        print(f"   - Khoi luong mua: {buy_volume:,} co phieu")
        print(f"   - Khoi luong ban: {sell_volume:,} co phieu")
        print(f"   - Gia tri mua: {buy_value:,.0f} VND")
        print(f"   - Gia tri ban: {sell_value:,.0f} VND")
        
        # Áp lực mua/bán
        if buy_volume > sell_volume:
            pressure = "AP LUC MUA"
            ratio = buy_volume / sell_volume
        elif sell_volume > buy_volume:
            pressure = "AP LUC BAN"
            ratio = sell_volume / buy_volume
        else:
            pressure = "CAN BANG"
            ratio = 1.0
        
        print(f"   - Ap luc thi truong: {pressure} (ty le: {ratio:.2f})")
    
    # 2. Phân tích biến động giá theo thời gian
    print("\n2. PHAN TICH BIEN DONG GIA:")
    
    # Resample dữ liệu theo phút
    df_intraday.set_index('time', inplace=True)
    df_minute = df_intraday.resample('1min').agg({
        'price': ['first', 'last', 'min', 'max'],
        'volume': 'sum'
    }).dropna()
    
    # Flatten column names
    df_minute.columns = ['open', 'close', 'low', 'high', 'volume']
    df_minute = df_minute.dropna()
    
    if len(df_minute) > 0:
        # Tính volatility
        df_minute['price_change'] = df_minute['close'].pct_change()
        volatility = df_minute['price_change'].std() * 100
        
        print(f"   - Bien dong gia (volatility): {volatility:.2f}%")
        print(f"   - Bien dong gia lon nhat: {df_minute['price_change'].max()*100:.2f}%")
        print(f"   - Bien dong gia nho nhat: {df_minute['price_change'].min()*100:.2f}%")
        
        # Phân tích trend
        price_start = df_minute['close'].iloc[0]
        price_end = df_minute['close'].iloc[-1]
        total_change = ((price_end - price_start) / price_start) * 100
        
        print(f"   - Gia mo cua: {price_start:.1f} VND")
        print(f"   - Gia dong cua: {price_end:.1f} VND")
        print(f"   - Bien dong tong: {total_change:+.2f}%")
        
        if total_change > 0:
            trend = "TANG GIA"
        elif total_change < 0:
            trend = "GIAM GIA"
        else:
            trend = "KHONG DOI"
        
        print(f"   - Xu huong: {trend}")
    
    # 3. Kết hợp với dữ liệu tài chính
    print("\n3. KET HOP VOI DU LIEU TAI CHINH:")
    
    # Lấy thông tin tài chính
    overview = financial_data['company_overview']['data']
    balance_sheet = financial_data['balance_sheet']['data'][0]  # 2024
    
    # Tính market cap tạm thời
    current_price = df_intraday['price'].iloc[-1]
    shares_outstanding = overview['issue_share']
    market_cap = current_price * shares_outstanding
    
    # Tính P/E, P/B từ dữ liệu tài chính
    book_value_per_share = balance_sheet['VỐN CHỦ SỞ HỮU (đồng)'] / shares_outstanding
    pb_ratio = current_price / book_value_per_share
    
    print(f"   - Gia hien tai: {current_price:.1f} VND")
    print(f"   - So co phieu luu hanh: {shares_outstanding:,}")
    print(f"   - Von hoa thi truong uoc tinh: {market_cap:,.0f} VND")
    print(f"   - Gia tri so sach/co phieu: {book_value_per_share:.0f} VND")
    print(f"   - P/B ratio uoc tinh: {pb_ratio:.2f}")
    
    # 4. Phân tích thanh khoản
    print("\n4. PHAN TICH THANH KHOAN:")
    
    # Thanh khoản theo giờ
    df_intraday_reset = df_intraday.reset_index()
    df_intraday_reset['hour'] = df_intraday_reset['time'].dt.hour
    
    hourly_volume = df_intraday_reset.groupby('hour')['volume'].sum()
    hourly_value = df_intraday_reset.groupby('hour').apply(lambda x: (x['price'] * x['volume']).sum())
    
    print("   THANH KHOAN THEO GIO:")
    for hour in sorted(hourly_volume.index):
        if hour >= 9 and hour <= 15:  # Giờ giao dịch
            print(f"   - {hour:02d}h: {hourly_volume[hour]:,} co phieu, {hourly_value[hour]:,.0f} VND")
    
    # Tính tỷ lệ thanh khoản
    daily_volume_percent = (total_volume / shares_outstanding) * 100
    print(f"   - Ty le thanh khoan: {daily_volume_percent:.4f}% co phieu luu hanh")
    
    # 5. Nhận định tổng hợp
    print("\n" + "=" * 80)
    print("NHAN DINH TONG HOP")
    print("=" * 80)
    
    print("\n5.1 DANH GIA HOAT DONG GIAO DICH:")
    if daily_volume_percent > 0.1:
        liquidity_assessment = "Thanh khoan tot"
    elif daily_volume_percent > 0.05:
        liquidity_assessment = "Thanh khoan trung binh"
    else:
        liquidity_assessment = "Thanh khoan yeu"
    
    print(f"   - Thanh khoan: {liquidity_assessment}")
    print(f"   - Hoat dong giao dich: {'Soi dong' if len(df_intraday) > 1000 else 'Binh thuong'}")
    
    print("\n5.2 DANH GIA GIA:")
    if volatility > 3:
        volatility_assessment = "Bien dong manh"
    elif volatility > 1:
        volatility_assessment = "Bien dong trung binh"
    else:
        volatility_assessment = "On dinh"
    
    print(f"   - Bien dong: {volatility_assessment}")
    print(f"   - Xu huong: {trend}")
    
    print("\n5.3 DANH GIA DINH GIA:")
    if pb_ratio > 3:
        valuation = "Co the dinh gia cao"
    elif pb_ratio > 1.5:
        valuation = "Dinh gia hop ly"
    else:
        valuation = "Co the dinh gia thap"
    
    print(f"   - Dinh gia (P/B): {valuation}")
    
    print("\n5.4 KHUYEN NGHI DAUER TU:")
    
    # Tổng hợp các yếu tố
    positive_factors = []
    negative_factors = []
    
    if trend == "TANG GIA":
        positive_factors.append("Xu huong tang gia")
    elif trend == "GIAM GIA":
        negative_factors.append("Xu huong giam gia")
    
    if liquidity_assessment == "Thanh khoan tot":
        positive_factors.append("Thanh khoan tot")
    elif liquidity_assessment == "Thanh khoan yeu":
        negative_factors.append("Thanh khoan yeu")
    
    if volatility_assessment == "Bien dong manh":
        negative_factors.append("Bien dong cao, rui ro")
    elif volatility_assessment == "On dinh":
        positive_factors.append("Gia on dinh")
    
    print("   YEU TO TICH CUC:")
    for factor in positive_factors:
        print(f"   + {factor}")
    
    print("   YEU TO TIEU CUC:")
    for factor in negative_factors:
        print(f"   - {factor}")
    
    # Đưa ra khuyến nghị
    score = len(positive_factors) - len(negative_factors)
    
    if score > 0:
        recommendation = "TICH CUC - Co the xem xet mua"
    elif score < 0:
        recommendation = "TIEU CUC - Can than"
    else:
        recommendation = "TRUNG TINH - Theo doi"
    
    print(f"\n   KHUYEN NGHI: {recommendation}")
    
    print("\n" + "=" * 80)
    print("KET THUC PHAN TICH KET HOP")
    print("=" * 80)

if __name__ == "__main__":
    combined_vhm_analysis()