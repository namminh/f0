#!/usr/bin/env python3
"""
Enhanced VND Charts with Technical Indicators
Tạo biểu đồ VND với các chỉ số kỹ thuật và phân tích chuyên sâu
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

def create_enhanced_vic_charts():
    """Tạo biểu đồ VND nâng cao với chỉ số kỹ thuật"""
    
    # Create directories
    Path("stock_analysis/VND/charts/key_charts").mkdir(parents=True, exist_ok=True)
    Path("stock_analysis/VND/charts/detailed_charts").mkdir(parents=True, exist_ok=True)
    Path("stock_analysis/VND/charts/technical_analysis").mkdir(parents=True, exist_ok=True)

    # Load data
    try:
        with open("stock_analysis/VND/data/VND_intraday_data.json", "r", encoding="utf-8") as f:
            intraday_data = json.load(f)
    except FileNotFoundError:
        print("Không tìm thấy dữ liệu intraday VND")
        return
    
    try:
        with open("stock_analysis/VND/data/VND_financial_data.json", "r", encoding="utf-8") as f:
            financial_data = json.load(f)
    except FileNotFoundError:
        financial_data = None

    if not intraday_data or 'data' not in intraday_data:
        print("Dữ liệu không hợp lệ")
        return

    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)
    
    # Create enhanced charts
    create_comprehensive_price_analysis(df)
    create_volume_analysis(df)
    create_technical_indicators(df)
    create_market_sentiment_analysis(df)
    create_financial_overview(financial_data)
    create_trading_summary(df, intraday_data)
    
    print("Enhanced VND charts created successfully")

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
    ax1.plot(df['time'], df['price'], label='Giá VND', linewidth=2, color='blue')
    ax1.plot(df['time'], df['MA5'], label='MA5', alpha=0.7, color='orange')
    ax1.plot(df['time'], df['MA10'], label='MA10', alpha=0.7, color='green')
    ax1.plot(df['time'], df['MA20'], label='MA20', alpha=0.7, color='red')
    ax1.set_title('VND - Giá và Đường trung bình động', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Giá (VND)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Bollinger Bands
    ax2.plot(df['time'], df['price'], label='Giá VND', linewidth=2, color='blue')
    ax2.fill_between(df['time'], df['BB_upper'], df['BB_lower'], alpha=0.2, color='gray', label='Bollinger Bands')
    ax2.plot(df['time'], df['BB_upper'], '--', color='red', alpha=0.7, label='BB Upper')
    ax2.plot(df['time'], df['BB_middle'], '--', color='orange', alpha=0.7, label='BB Middle')
    ax2.plot(df['time'], df['BB_lower'], '--', color='green', alpha=0.7, label='BB Lower')
    ax2.set_title('VND - Bollinger Bands', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Giá (VND)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. RSI
    ax3.plot(df['time'], df['RSI'], color='purple', linewidth=2)
    ax3.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Quá mua (70)')
    ax3.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Quá bán (30)')
    ax3.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
    ax3.fill_between(df['time'], 30, 70, alpha=0.1, color='gray')
    ax3.set_title('VND - Chỉ số RSI', fontsize=14, fontweight='bold')
    ax3.set_ylabel('RSI')
    ax3.set_ylim(0, 100)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Price Performance
    first_price = df['price'].iloc[0]
    df['price_change_pct'] = ((df['price'] - first_price) / first_price) * 100
    
    colors = ['green' if x >= 0 else 'red' for x in df['price_change_pct']]
    for i in range(len(df)):
        ax4.fill_between(df['time'].iloc[i:i+1], 0, df['price_change_pct'].iloc[i:i+1], alpha=0.6, color=colors[i])
    ax4.plot(df['time'], df['price_change_pct'], color='darkblue', linewidth=2)
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.8)
    ax4.set_title('VND - Biến động giá so với mở cửa (%)', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Thay đổi (%)')
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VND/charts/technical_analysis/comprehensive_price_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_volume_analysis(df):
    """Phân tích khối lượng giao dịch"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Volume over time
    df['hour'] = df['time'].dt.hour
    df['minute'] = df['time'].dt.minute
    
    # Volume by time
    ax1.bar(df['time'], df['volume'], alpha=0.7, color='steelblue', width=0.0001)
    ax1.set_title('VND - Khối lượng giao dịch theo thời gian', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Khối lượng')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)
    
    # 2. Volume by hour
    volume_by_hour = df.groupby('hour')['volume'].sum()
    bars = ax2.bar(volume_by_hour.index, volume_by_hour.values, alpha=0.8, color='lightcoral')
    ax2.set_title('VND - Khối lượng giao dịch theo giờ', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Giờ')
    ax2.set_ylabel('Tổng khối lượng')
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height/1000)}K', ha='center', va='bottom')
    
    # 3. Volume vs Price correlation
    ax3.scatter(df['volume'], df['price'], alpha=0.6, color='green', s=20)
    ax3.set_title('VND - Tương quan Khối lượng vs Giá', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Khối lượng')
    ax3.set_ylabel('Giá (VND)')
    ax3.grid(True, alpha=0.3)
    
    # Add correlation coefficient
    correlation = df['volume'].corr(df['price'])
    ax3.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
             transform=ax3.transAxes, bbox=dict(boxstyle="round", facecolor='wheat', alpha=0.5))
    
    # 4. Buy vs Sell volume
    buy_data = df[df['match_type'] == 'Buy']
    sell_data = df[df['match_type'] == 'Sell']
    
    buy_vol_hourly = buy_data.groupby('hour')['volume'].sum()
    sell_vol_hourly = sell_data.groupby('hour')['volume'].sum()
    
    x = list(set(buy_vol_hourly.index) | set(sell_vol_hourly.index))
    buy_volumes = [buy_vol_hourly.get(hour, 0) for hour in x]
    sell_volumes = [sell_vol_hourly.get(hour, 0) for hour in x]
    
    width = 0.35
    ax4.bar([i - width/2 for i in x], buy_volumes, width, label='Mua', alpha=0.8, color='green')
    ax4.bar([i + width/2 for i in x], sell_volumes, width, label='Bán', alpha=0.8, color='red')
    ax4.set_title('VND - Khối lượng Mua vs Bán theo giờ', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Giờ')
    ax4.set_ylabel('Khối lượng')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VND/charts/technical_analysis/volume_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_technical_indicators(df):
    """Tạo biểu đồ các chỉ số kỹ thuật"""
    df = calculate_technical_indicators(df)
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12))
    
    # Price with Bollinger Bands
    ax1.plot(df['time'], df['price'], label='Giá VND', linewidth=2, color='blue')
    ax1.fill_between(df['time'], df['BB_upper'], df['BB_lower'], alpha=0.2, color='gray')
    ax1.plot(df['time'], df['BB_upper'], '--', color='red', alpha=0.7, label='BB Upper')
    ax1.plot(df['time'], df['BB_middle'], '--', color='orange', alpha=0.7, label='BB Middle')
    ax1.plot(df['time'], df['BB_lower'], '--', color='green', alpha=0.7, label='BB Lower')
    ax1.set_title('VND - Giá với Bollinger Bands', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Giá (VND)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # RSI
    ax2.plot(df['time'], df['RSI'], color='purple', linewidth=2)
    ax2.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Quá mua (70)')
    ax2.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Quá bán (30)')
    ax2.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
    ax2.fill_between(df['time'], 30, 70, alpha=0.1, color='gray')
    ax2.set_title('VND - RSI (Relative Strength Index)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('RSI')
    ax2.set_ylim(0, 100)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Moving Averages
    ax3.plot(df['time'], df['price'], label='Giá VND', linewidth=2, color='blue')
    ax3.plot(df['time'], df['MA5'], label='MA5', alpha=0.7, color='orange')
    ax3.plot(df['time'], df['MA10'], label='MA10', alpha=0.7, color='green')
    ax3.plot(df['time'], df['MA20'], label='MA20', alpha=0.7, color='red')
    ax3.set_title('VND - Đường trung bình động', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Thời gian')
    ax3.set_ylabel('Giá (VND)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VND/charts/technical_analysis/technical_indicators.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_market_sentiment_analysis(df):
    """Phân tích tâm lý thị trường"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
    
    # 1. Buy/Sell pressure over time
    df['cumulative_volume'] = df['volume'].cumsum()
    buy_df = df[df['match_type'] == 'Buy'].copy()
    sell_df = df[df['match_type'] == 'Sell'].copy()
    
    if not buy_df.empty:
        buy_df['cumulative_buy'] = buy_df['volume'].cumsum()
        ax1.plot(buy_df['time'], buy_df['cumulative_buy'], color='green', label='Tích lũy mua', linewidth=2)
    
    if not sell_df.empty:
        sell_df['cumulative_sell'] = sell_df['volume'].cumsum()
        ax1.plot(sell_df['time'], sell_df['cumulative_sell'], color='red', label='Tích lũy bán', linewidth=2)
    
    ax1.set_title('VND - Áp lực Mua/Bán tích lũy', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Khối lượng tích lũy')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Price momentum
    df['price_change'] = df['price'].diff()
    df['momentum'] = df['price_change'].rolling(window=min(10, len(df))).mean()
    
    colors = ['green' if x >= 0 else 'red' for x in df['momentum']]
    for i in range(len(df)):
        if not pd.isna(df['momentum'].iloc[i]):
            ax2.bar(df['time'].iloc[i], df['momentum'].iloc[i], 
                   color=colors[i], alpha=0.7, width=0.0001)
    
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.8)
    ax2.set_title('VND - Momentum giá (10-period)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Momentum')
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Volume distribution
    ax3.hist(df['volume'], bins=20, alpha=0.7, color='steelblue', edgecolor='black')
    ax3.axvline(df['volume'].mean(), color='red', linestyle='--', linewidth=2, label=f'TB: {df["volume"].mean():.0f}')
    ax3.axvline(df['volume'].median(), color='orange', linestyle='--', linewidth=2, label=f'Median: {df["volume"].median():.0f}')
    ax3.set_title('VND - Phân phối khối lượng giao dịch', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Khối lượng')
    ax3.set_ylabel('Tần suất')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Trading intensity heatmap
    df['hour'] = df['time'].dt.hour
    df['minute_group'] = (df['time'].dt.minute // 15) * 15  # Group by 15-minute intervals
    
    intensity_matrix = df.groupby(['hour', 'minute_group'])['volume'].sum().unstack(fill_value=0)
    
    sns.heatmap(intensity_matrix, ax=ax4, cmap='YlOrRd', 
                annot=True, fmt='.0f', cbar_kws={'label': 'Khối lượng'})
    ax4.set_title('VND - Bản đồ nhiệt giao dịch', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Phút')
    ax4.set_ylabel('Giờ')
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VND/charts/technical_analysis/market_sentiment.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_financial_overview(financial_data):
    """Tạo tổng quan tài chính"""
    if not financial_data:
        # Create a placeholder chart
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, 'VND - Dữ liệu tài chính\nĐang xử lý...', 
                ha='center', va='center', fontsize=16,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
        ax.set_title('VND - Tổng quan Tài chính', fontsize=16, fontweight='bold')
        ax.axis('off')
        plt.savefig("stock_analysis/VND/charts/detailed_charts/financial_overview.png", dpi=300, bbox_inches='tight')
        plt.close()
        return
    
    # Process financial data if available
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Placeholder financial analysis
    ax1.text(0.5, 0.5, 'P/E Ratio\nAnalysis', ha='center', va='center', fontsize=14,
             bbox=dict(boxstyle="round", facecolor='lightgreen', alpha=0.7))
    ax1.set_title('P/E Ratio', fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    ax2.text(0.5, 0.5, 'P/B Ratio\nAnalysis', ha='center', va='center', fontsize=14,
             bbox=dict(boxstyle="round", facecolor='lightcoral', alpha=0.7))
    ax2.set_title('P/B Ratio', fontsize=14, fontweight='bold')
    ax2.axis('off')
    
    ax3.text(0.5, 0.5, 'ROE\nAnalysis', ha='center', va='center', fontsize=14,
             bbox=dict(boxstyle="round", facecolor='lightyellow', alpha=0.7))
    ax3.set_title('ROE', fontsize=14, fontweight='bold')
    ax3.axis('off')
    
    ax4.text(0.5, 0.5, 'Revenue\nAnalysis', ha='center', va='center', fontsize=14,
             bbox=dict(boxstyle="round", facecolor='lightsteelblue', alpha=0.7))
    ax4.set_title('Revenue', fontsize=14, fontweight='bold')
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VND/charts/detailed_charts/financial_overview.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_trading_summary(df, intraday_data):
    """Tạo tóm tắt giao dịch"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    
    # Calculate summary statistics
    total_volume = df['volume'].sum()
    avg_price = df['price'].mean()
    high_price = df['price'].max()
    low_price = df['price'].min()
    price_change = df['price'].iloc[-1] - df['price'].iloc[0]
    price_change_pct = (price_change / df['price'].iloc[0]) * 100
    
    buy_volume = df[df['match_type'] == 'Buy']['volume'].sum()
    sell_volume = df[df['match_type'] == 'Sell']['volume'].sum()
    buy_sell_ratio = buy_volume / sell_volume if sell_volume > 0 else 0
    
    volatility = df['price'].std()
    timestamp = intraday_data.get('timestamp', 'N/A')
    
    # Create summary text
    summary_text = f"""
VND - TỔNG KẾT GIAO DỊCH INTRADAY
{datetime.now().strftime('%d/%m/%Y')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 THÔNG TIN GIAO DỊCH:
   • Tổng khối lượng: {total_volume:,.0f} cổ phiếu
   • Số điểm dữ liệu: {len(df):,}
   • Thời gian: {df['time'].min().strftime('%H:%M')} - {df['time'].max().strftime('%H:%M')}

💰 THÔNG TIN GIÁ:
   • Giá cao nhất: {high_price:.2f} VND
   • Giá thấp nhất: {low_price:.2f} VND  
   • Giá trung bình: {avg_price:.2f} VND
   • Thay đổi: {price_change:+.2f} VND ({price_change_pct:+.2f}%)

📈 PHÂN TÍCH GIAO DỊCH:
   • Khối lượng mua: {buy_volume:,.0f} ({buy_volume/total_volume*100:.1f}%)
   • Khối lượng bán: {sell_volume:,.0f} ({sell_volume/total_volume*100:.1f}%)
   • Tỷ lệ mua/bán: {buy_sell_ratio:.2f}

📊 CHỈ SỐ KỸ THUẬT:
   • Độ biến động (σ): {volatility:.2f}
   • Biên độ dao động: {high_price - low_price:.2f} VND
   • Tính thanh khoản: {'Cao' if total_volume > 1000000 else 'Trung bình' if total_volume > 500000 else 'Thấp'}

🎯 NHẬN ĐỊNH:
   • Xu hướng: {'TĂNG' if price_change > 0 else 'GIẢM' if price_change < 0 else 'ĐỨNG YÊN'}
   • Áp lực: {'MUA' if buy_sell_ratio > 1.1 else 'BÁN' if buy_sell_ratio < 0.9 else 'CÂN BẰNG'}
   • Biến động: {'CAO' if volatility > avg_price * 0.02 else 'THẤP'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ Cập nhật: {timestamp}
📊 Nguồn: {intraday_data.get('data_source', 'VCI')}
    """
    
    ax.text(0.5, 0.5, summary_text, ha='center', va='center', fontsize=11,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8),
            fontfamily='monospace')
    
    plt.savefig("stock_analysis/VND/charts/technical_analysis/trading_summary.png", dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    create_enhanced_vic_charts()
