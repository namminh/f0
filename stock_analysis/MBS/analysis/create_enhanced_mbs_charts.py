#!/usr/bin/env python3
"""
Enhanced MBS Charts with Technical Indicators
Tạo biểu đồ MBS với các chỉ số kỹ thuật và phân tích chuyên sâu
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# Set Vietnamese font
plt.rcParams['font.family'] = ['Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8')

def create_enhanced_mbs_charts():
    """Tạo biểu đồ MBS nâng cao với chỉ số kỹ thuật"""
    
    # Create directories
    Path("stock_analysis/MBS/charts/key_charts").mkdir(parents=True, exist_ok=True)
    Path("stock_analysis/MBS/charts/technical_analysis").mkdir(parents=True, exist_ok=True)

    # Load data
    try:
        with open("stock_analysis/MBS/data/MBS_intraday_data.json", "r", encoding="utf-8") as f:
            intraday_data = json.load(f)
    except FileNotFoundError:
        print("Khong tim thay du lieu intraday MBS")
        return
    
    if not intraday_data or 'data' not in intraday_data:
        print("Du lieu khong hop le")
        return

    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)
    
    # Create enhanced charts
    create_comprehensive_price_analysis(df)
    create_volume_analysis(df)
    create_technical_indicators(df)
    create_market_sentiment_analysis(df)
    create_trading_summary(df, intraday_data)
    
    print("Enhanced MBS charts created successfully")

def calculate_technical_indicators(df):
    """Tính toán các chỉ số kỹ thuật"""
    # Moving averages
    df['MA5'] = df['price'].rolling(window=min(5, len(df))).mean()
    df['MA10'] = df['price'].rolling(window=min(10, len(df))).mean()
    df['MA20'] = df['price'].rolling(window=min(20, len(df))).mean()
    
    # Bollinger Bands
    window = min(20, len(df))
    df['BB_middle'] = df['price'].rolling(window=window).mean()
    df['BB_std'] = df['price'].rolling(window=window).std()
    df['BB_upper'] = df['BB_middle'] + (df['BB_std'] * 2)
    df['BB_lower'] = df['BB_middle'] - (df['BB_std'] * 2)
    
    # RSI
    delta = df['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=min(14, len(df))).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=min(14, len(df))).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df

def create_comprehensive_price_analysis(df):
    """Tạo biểu đồ phân tích giá toàn diện"""
    df = calculate_technical_indicators(df)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Price with Moving Averages
    ax1.plot(df['time'], df['price'], label='Gia MBS', linewidth=2, color='blue')
    ax1.plot(df['time'], df['MA5'], label='MA5', alpha=0.7, color='orange')
    ax1.plot(df['time'], df['MA10'], label='MA10', alpha=0.7, color='green')
    ax1.plot(df['time'], df['MA20'], label='MA20', alpha=0.7, color='red')
    ax1.set_title('MBS - Gia va Duong trung binh dong', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Gia (VND)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Bollinger Bands
    ax2.plot(df['time'], df['price'], label='Gia MBS', linewidth=2, color='blue')
    ax2.fill_between(df['time'], df['BB_upper'], df['BB_lower'], alpha=0.2, color='gray', label='Bollinger Bands')
    ax2.plot(df['time'], df['BB_upper'], color='red', alpha=0.5, linestyle='--')
    ax2.plot(df['time'], df['BB_lower'], color='red', alpha=0.5, linestyle='--')
    ax2.plot(df['time'], df['BB_middle'], color='orange', alpha=0.7)
    ax2.set_title('MBS - Bollinger Bands', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Gia (VND)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. RSI
    ax3.plot(df['time'], df['RSI'], label='RSI', linewidth=2, color='purple')
    ax3.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
    ax3.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')
    ax3.fill_between(df['time'], 30, 70, alpha=0.1, color='gray')
    ax3.set_title('MBS - RSI (Relative Strength Index)', fontsize=14, fontweight='bold')
    ax3.set_ylabel('RSI')
    ax3.set_ylim(0, 100)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Volume
    colors = ['green' if df.loc[i, 'match_type'] == 'Buy' else 'red' for i in range(len(df))]
    ax4.bar(df['time'], df['volume'], color=colors, alpha=0.6, width=0.001)
    ax4.set_title('MBS - Khoi luong giao dich', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Khoi luong')
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/technical_analysis/comprehensive_price_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_volume_analysis(df):
    """Tạo biểu đồ phân tích khối lượng chi tiết"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Volume over time
    ax1.plot(df['time'], df['volume'], linewidth=1, color='blue', alpha=0.7)
    ax1.fill_between(df['time'], df['volume'], alpha=0.3, color='blue')
    ax1.set_title('MBS - Khoi luong theo thoi gian', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Khoi luong')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Volume by hour
    df['hour'] = df['time'].dt.hour
    volume_by_hour = df.groupby('hour')['volume'].sum()
    bars = ax2.bar(volume_by_hour.index, volume_by_hour.values, color='orange', alpha=0.8)
    ax2.set_title('MBS - Khoi luong theo gio', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Gio')
    ax2.set_ylabel('Khoi luong')
    ax2.grid(True, axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height/1000)}K', ha='center', va='bottom')
    
    # 3. Buy vs Sell volume
    buy_vol = df[df['match_type'] == 'Buy']['volume'].sum()
    sell_vol = df[df['match_type'] == 'Sell']['volume'].sum()
    ax3.pie([buy_vol, sell_vol], labels=['Mua', 'Ban'], colors=['green', 'red'], 
            autopct='%1.1f%%', startangle=90)
    ax3.set_title('MBS - Ty le Mua/Ban', fontsize=14, fontweight='bold')
    
    # 4. Volume distribution
    ax4.hist(df['volume'], bins=30, color='skyblue', alpha=0.7, edgecolor='black')
    ax4.set_title('MBS - Phan bo khoi luong', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Khoi luong')
    ax4.set_ylabel('Tan suat')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/technical_analysis/volume_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_technical_indicators(df):
    """Tạo biểu đồ các chỉ số kỹ thuật MACD, Stochastic, Williams %R"""
    df = calculate_technical_indicators(df)
    
    # Calculate MACD
    exp1 = df['price'].ewm(span=12).mean()
    exp2 = df['price'].ewm(span=26).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
    
    # Calculate Stochastic
    low_min = df['price'].rolling(window=14).min()
    high_max = df['price'].rolling(window=14).max()
    df['%K'] = 100 * ((df['price'] - low_min) / (high_max - low_min))
    df['%D'] = df['%K'].rolling(window=3).mean()
    
    # Calculate Williams %R
    df['Williams_R'] = -100 * ((high_max - df['price']) / (high_max - low_min))
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. MACD
    ax1.plot(df['time'], df['MACD'], label='MACD', color='blue', linewidth=2)
    ax1.plot(df['time'], df['MACD_signal'], label='Signal', color='red', linewidth=2)
    ax1.bar(df['time'], df['MACD_histogram'], label='Histogram', alpha=0.6, color='gray')
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax1.set_title('MBS - MACD', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Stochastic
    ax2.plot(df['time'], df['%K'], label='%K', color='blue', linewidth=2)
    ax2.plot(df['time'], df['%D'], label='%D', color='red', linewidth=2)
    ax2.axhline(y=80, color='red', linestyle='--', alpha=0.7)
    ax2.axhline(y=20, color='green', linestyle='--', alpha=0.7)
    ax2.fill_between(df['time'], 20, 80, alpha=0.1, color='gray')
    ax2.set_title('MBS - Stochastic Oscillator', fontsize=14, fontweight='bold')
    ax2.set_ylim(0, 100)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Williams %R
    ax3.plot(df['time'], df['Williams_R'], label='Williams %R', color='purple', linewidth=2)
    ax3.axhline(y=-20, color='red', linestyle='--', alpha=0.7, label='Overbought')
    ax3.axhline(y=-80, color='green', linestyle='--', alpha=0.7, label='Oversold')
    ax3.fill_between(df['time'], -20, -80, alpha=0.1, color='gray')
    ax3.set_title('MBS - Williams %R', fontsize=14, fontweight='bold')
    ax3.set_ylim(-100, 0)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Price vs Volume correlation
    ax4.scatter(df['price'], df['volume'], alpha=0.6, color='blue')
    ax4.set_title('MBS - Tuong quan Gia vs Khoi luong', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Gia (VND)')
    ax4.set_ylabel('Khoi luong')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/technical_analysis/technical_indicators.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_market_sentiment_analysis(df):
    """Tạo biểu đồ phân tích tâm lý thị trường"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Price momentum
    df['price_change'] = df['price'].pct_change()
    df['momentum'] = df['price_change'].rolling(window=10).mean()
    
    colors = ['green' if x > 0 else 'red' for x in df['momentum']]
    ax1.bar(df['time'], df['momentum'], color=colors, alpha=0.7)
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax1.set_title('MBS - Momentum gia', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Momentum')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Buy pressure vs Sell pressure
    df['hour'] = df['time'].dt.hour
    buy_pressure = df[df['match_type'] == 'Buy'].groupby('hour')['volume'].sum()
    sell_pressure = df[df['match_type'] == 'Sell'].groupby('hour')['volume'].sum()
    
    x = range(len(buy_pressure.index))
    width = 0.35
    ax2.bar([i - width/2 for i in x], buy_pressure.values, width, label='Ap luc mua', color='green', alpha=0.7)
    ax2.bar([i + width/2 for i in x], sell_pressure.values, width, label='Ap luc ban', color='red', alpha=0.7)
    ax2.set_title('MBS - Ap luc mua/ban theo gio', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Gio')
    ax2.set_ylabel('Khoi luong')
    ax2.set_xticks(x)
    ax2.set_xticklabels(buy_pressure.index)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Market sentiment score
    buy_ratio = df['volume'][df['match_type'] == 'Buy'].sum() / df['volume'].sum()
    price_trend = 1 if df['price'].iloc[-1] > df['price'].iloc[0] else 0
    volatility = df['price'].std() / df['price'].mean()
    
    sentiment_score = (buy_ratio * 0.4 + price_trend * 0.4 + (1-volatility) * 0.2) * 100
    
    colors = ['red', 'orange', 'yellow', 'lightgreen', 'green']
    scores = [20, 40, 60, 80, 100]
    score_colors = [colors[i] for i, score in enumerate(scores) if sentiment_score <= score]
    
    ax3.pie([sentiment_score, 100-sentiment_score], labels=[f'Tich cuc {sentiment_score:.1f}%', ''], 
            colors=[score_colors[0] if score_colors else 'gray', 'lightgray'], 
            startangle=90, counterclock=False)
    ax3.set_title('MBS - Chi so tam ly thi truong', fontsize=14, fontweight='bold')
    
    # 4. Trading intensity
    df['intensity'] = df['volume'] / df['volume'].mean()
    ax4.plot(df['time'], df['intensity'], color='purple', linewidth=2)
    ax4.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Trung binh')
    ax4.fill_between(df['time'], df['intensity'], 1, alpha=0.3, color='purple')
    ax4.set_title('MBS - Cuong do giao dich', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Cuong do (so voi TB)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/technical_analysis/market_sentiment.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_trading_summary(df, intraday_data):
    """Tạo biểu đồ tóm tắt giao dịch"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Price range and key levels
    high_price = df['price'].max()
    low_price = df['price'].min()
    current_price = df['price'].iloc[-1]
    avg_price = df['price'].mean()
    
    ax1.axhline(y=high_price, color='red', linestyle='--', alpha=0.7, label=f'Cao nhat: {high_price:.2f}')
    ax1.axhline(y=low_price, color='green', linestyle='--', alpha=0.7, label=f'Thap nhat: {low_price:.2f}')
    ax1.axhline(y=avg_price, color='orange', linestyle='-', alpha=0.7, label=f'Trung binh: {avg_price:.2f}')
    ax1.plot(df['time'], df['price'], color='blue', linewidth=2, label=f'Gia hien tai: {current_price:.2f}')
    
    ax1.set_title('MBS - Muc gia quan trong', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Gia (VND)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Volume profile
    price_ranges = pd.cut(df['price'], bins=10)
    volume_profile = df.groupby(price_ranges)['volume'].sum()
    
    ax2.barh(range(len(volume_profile)), volume_profile.values, color='skyblue', alpha=0.7)
    ax2.set_title('MBS - Profile khoi luong theo gia', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Khoi luong')
    ax2.set_ylabel('Khoang gia')
    ax2.set_yticks(range(len(volume_profile)))
    ax2.set_yticklabels([f'{interval.left:.2f}-{interval.right:.2f}' for interval in volume_profile.index])
    ax2.grid(True, alpha=0.3)
    
    # 3. Trading statistics
    total_volume = df['volume'].sum()
    avg_volume = df['volume'].mean()
    max_volume = df['volume'].max()
    
    stats = ['Tong KL', 'TB KL', 'Max KL', 'So giao dich']
    values = [total_volume/1000000, avg_volume/1000, max_volume/1000, len(df)]
    units = ['M', 'K', 'K', '']
    
    bars = ax3.bar(stats, values, color=['blue', 'green', 'orange', 'purple'], alpha=0.7)
    ax3.set_title('MBS - Thong ke giao dich', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Gia tri')
    
    for i, (bar, unit) in enumerate(zip(bars, units)):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}{unit}', ha='center', va='bottom')
    
    ax3.grid(True, axis='y', alpha=0.3)
    
    # 4. Price distribution
    ax4.hist(df['price'], bins=20, color='lightgreen', alpha=0.7, edgecolor='black')
    ax4.axvline(x=current_price, color='red', linestyle='--', linewidth=2, label=f'Gia hien tai: {current_price:.2f}')
    ax4.axvline(x=avg_price, color='orange', linestyle='-', linewidth=2, label=f'Gia TB: {avg_price:.2f}')
    ax4.set_title('MBS - Phan bo gia', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Gia (VND)')
    ax4.set_ylabel('Tan suat')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/technical_analysis/trading_summary.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    create_enhanced_mbs_charts()