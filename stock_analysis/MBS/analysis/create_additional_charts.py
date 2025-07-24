#!/usr/bin/env python3
"""
Additional Analysis Charts for MBS
Tạo 5 biểu đồ phân tích bổ sung cho MBS
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

def create_additional_charts():
    """Tạo 5 biểu đồ phân tích bổ sung cho MBS"""
    
    # Create directory
    Path("stock_analysis/MBS/charts/additional_analysis").mkdir(parents=True, exist_ok=True)

    # Load data
    try:
        with open("stock_analysis/MBS/data/MBS_intraday_data.json", "r", encoding="utf-8") as f:
            intraday_data = json.load(f)
    except FileNotFoundError:
        print("Khong tim thay du lieu intraday MBS")
        return
    
    try:
        with open("stock_analysis/MBS/data/MBS_financial_ratios.json", "r", encoding="utf-8") as f:
            financial_ratios = json.load(f)
    except FileNotFoundError:
        financial_ratios = None

    if not intraday_data or 'data' not in intraday_data:
        print("Du lieu khong hop le")
        return

    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)

    # Create additional analysis charts
    create_price_action_analysis(df)
    create_liquidity_analysis(df)
    create_risk_assessment(df, financial_ratios)
    create_trading_zones(df)
    create_performance_dashboard(df, intraday_data, financial_ratios)
    
    print("Additional analysis charts created successfully")

def create_price_action_analysis(df):
    """Tạo biểu đồ phân tích price action - Support/Resistance, momentum"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Support and Resistance levels
    high_price = df['price'].max()
    low_price = df['price'].min()
    price_range = high_price - low_price
    
    # Tính các mức support/resistance
    resistance_1 = high_price
    resistance_2 = high_price - price_range * 0.25
    support_1 = low_price + price_range * 0.25
    support_2 = low_price
    
    ax1.plot(df['time'], df['price'], linewidth=2, color='blue', label='Gia MBS')
    ax1.axhline(y=resistance_1, color='red', linestyle='--', alpha=0.7, label=f'Resistance 1: {resistance_1:.2f}')
    ax1.axhline(y=resistance_2, color='orange', linestyle='--', alpha=0.7, label=f'Resistance 2: {resistance_2:.2f}')
    ax1.axhline(y=support_1, color='green', linestyle='--', alpha=0.7, label=f'Support 1: {support_1:.2f}')
    ax1.axhline(y=support_2, color='darkgreen', linestyle='--', alpha=0.7, label=f'Support 2: {support_2:.2f}')
    
    ax1.set_title('MBS - Muc Support/Resistance', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Gia (VND)')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Price momentum với moving averages
    df['MA5'] = df['price'].rolling(window=5).mean()
    df['MA10'] = df['price'].rolling(window=10).mean()
    df['momentum'] = df['price'] - df['MA10']
    
    ax2.plot(df['time'], df['momentum'], linewidth=2, color='purple', label='Momentum')
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax2.fill_between(df['time'], df['momentum'], 0, alpha=0.3, color='purple')
    
    ax2.set_title('MBS - Momentum gia', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Momentum (VND)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Price volatility analysis
    df['returns'] = df['price'].pct_change()
    df['volatility'] = df['returns'].rolling(window=20).std() * np.sqrt(252)
    
    ax3.plot(df['time'], df['volatility'] * 100, linewidth=2, color='red', label='Volatility')
    ax3.fill_between(df['time'], df['volatility'] * 100, alpha=0.3, color='red')
    
    ax3.set_title('MBS - Do bien dong (Volatility)', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Volatility (%)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Price bands với percentage từ MA
    df['upper_band'] = df['MA10'] * 1.02  # 2% trên MA10
    df['lower_band'] = df['MA10'] * 0.98  # 2% dưới MA10
    
    ax4.plot(df['time'], df['price'], linewidth=2, color='blue', label='Gia MBS')
    ax4.plot(df['time'], df['MA10'], linewidth=1, color='orange', label='MA10')
    ax4.fill_between(df['time'], df['upper_band'], df['lower_band'], alpha=0.2, color='gray', label='Trading Band (±2%)')
    
    ax4.set_title('MBS - Trading Bands', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Gia (VND)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/additional_analysis/price_action_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_liquidity_analysis(df):
    """Tạo biểu đồ phân tích thanh khoản - market depth, liquidity patterns"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Volume-Price relationship
    ax1.scatter(df['price'], df['volume'], alpha=0.6, color='blue', s=30)
    
    # Thêm trendline
    if len(df) > 1:
        z = np.polyfit(df['price'], df['volume'], 1)
        p = np.poly1d(z)
        ax1.plot(df['price'], p(df['price']), "r--", alpha=0.8, label='Xu huong')
    
    ax1.set_title('MBS - Tuong quan Gia vs Khoi luong', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Gia (VND)')
    ax1.set_ylabel('Khoi luong')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Liquidity by time (volume intensity)
    df['hour'] = df['time'].dt.hour
    df['minute'] = df['time'].dt.minute
    df['time_bucket'] = df['hour'] * 60 + df['minute']
    
    liquidity_by_time = df.groupby('time_bucket')['volume'].mean()
    ax2.plot(liquidity_by_time.index, liquidity_by_time.values, linewidth=2, color='green')
    ax2.fill_between(liquidity_by_time.index, liquidity_by_time.values, alpha=0.3, color='green')
    
    ax2.set_title('MBS - Thanh khoan theo thoi gian', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Thoi gian (phut tu 0h)')
    ax2.set_ylabel('Khoi luong trung binh')
    ax2.grid(True, alpha=0.3)
    
    # 3. Bid-Ask spread simulation (dựa trên price volatility)
    df['price_change'] = df['price'].diff().abs()
    df['spread_estimate'] = df['price_change'] / df['price'] * 10000  # basis points
    
    ax3.plot(df['time'], df['spread_estimate'], linewidth=1, color='red', alpha=0.7)
    ax3.set_title('MBS - Uoc tinh Bid-Ask Spread', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Spread (basis points)')
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Market depth simulation
    price_levels = np.linspace(df['price'].min(), df['price'].max(), 20)
    volume_at_levels = []
    
    for level in price_levels:
        nearby_trades = df[abs(df['price'] - level) <= (df['price'].max() - df['price'].min()) * 0.02]
        volume_at_levels.append(nearby_trades['volume'].sum())
    
    ax4.barh(range(len(price_levels)), volume_at_levels, color='skyblue', alpha=0.7)
    ax4.set_title('MBS - Do sau thi truong (Market Depth)', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Tong khoi luong')
    ax4.set_ylabel('Muc gia')
    ax4.set_yticks(range(0, len(price_levels), 3))
    ax4.set_yticklabels([f'{price_levels[i]:.2f}' for i in range(0, len(price_levels), 3)])
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/additional_analysis/liquidity_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_risk_assessment(df, financial_ratios):
    """Tạo biểu đồ đánh giá rủi ro - VaR, volatility, drawdown"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Value at Risk (VaR) analysis
    df['returns'] = df['price'].pct_change().dropna()
    returns = df['returns'].dropna()
    
    if len(returns) > 0:
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        
        ax1.hist(returns, bins=30, alpha=0.7, color='blue', edgecolor='black')
        ax1.axvline(x=var_95, color='orange', linestyle='--', linewidth=2, label=f'VaR 95%: {var_95:.4f}')
        ax1.axvline(x=var_99, color='red', linestyle='--', linewidth=2, label=f'VaR 99%: {var_99:.4f}')
        ax1.set_title('MBS - Phan bo loi nhuan & VaR', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Loi nhuan (%)')
        ax1.set_ylabel('Tan suat')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    
    # 2. Rolling volatility
    df['rolling_vol'] = df['returns'].rolling(window=20).std() * np.sqrt(252) * 100
    
    ax2.plot(df['time'], df['rolling_vol'], linewidth=2, color='red')
    ax2.fill_between(df['time'], df['rolling_vol'], alpha=0.3, color='red')
    ax2.set_title('MBS - Do bien dong lan truyen (Rolling Volatility)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Volatility (%)')
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Drawdown analysis
    df['cumulative_returns'] = (1 + df['returns']).cumprod()
    df['peak'] = df['cumulative_returns'].expanding().max()
    df['drawdown'] = (df['cumulative_returns'] - df['peak']) / df['peak'] * 100
    
    ax3.fill_between(df['time'], df['drawdown'], 0, alpha=0.7, color='red', label='Drawdown')
    ax3.plot(df['time'], df['drawdown'], linewidth=1, color='darkred')
    ax3.set_title('MBS - Drawdown Analysis', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Drawdown (%)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Risk metrics summary
    if len(returns) > 0:
        max_drawdown = df['drawdown'].min()
        volatility = returns.std() * np.sqrt(252) * 100
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        # Financial risk metrics
        debt_equity = 0
        if financial_ratios and 'data' in financial_ratios:
            ratios_df = pd.DataFrame(financial_ratios['data'])
            if len(ratios_df) > 0 and 'Chỉ tiêu đòn bẩy_Debt/Equity' in ratios_df.columns:
                debt_equity = pd.to_numeric(ratios_df['Chỉ tiêu đòn bẩy_Debt/Equity'].iloc[0], errors='coerce')
                if pd.isna(debt_equity):
                    debt_equity = 0
        
        risk_metrics = ['Max Drawdown', 'Volatility', 'Sharpe Ratio', 'Debt/Equity']
        risk_values = [abs(max_drawdown), volatility, sharpe_ratio, debt_equity]
        risk_colors = ['red', 'orange', 'green' if sharpe_ratio > 0 else 'red', 'red' if debt_equity > 1 else 'green']
        
        bars = ax4.bar(risk_metrics, risk_values, color=risk_colors, alpha=0.7)
        ax4.set_title('MBS - Chi so rui ro tong hop', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Gia tri')
        
        # Add value labels
        for bar, value in zip(bars, risk_values):
            ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(risk_values) * 0.01,
                    f'{value:.2f}', ha='center', va='bottom')
        
        ax4.grid(True, alpha=0.3)
        ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/additional_analysis/risk_assessment.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_trading_zones(df):
    """Tạo biểu đồ vùng giao dịch - Volume profile, VWAP"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. VWAP (Volume Weighted Average Price)
    df['vwap'] = (df['price'] * df['volume']).cumsum() / df['volume'].cumsum()
    
    ax1.plot(df['time'], df['price'], linewidth=2, color='blue', label='Gia MBS')
    ax1.plot(df['time'], df['vwap'], linewidth=2, color='red', label='VWAP')
    ax1.fill_between(df['time'], df['price'], df['vwap'], 
                     where=(df['price'] >= df['vwap']), alpha=0.3, color='green', label='Tren VWAP')
    ax1.fill_between(df['time'], df['price'], df['vwap'], 
                     where=(df['price'] < df['vwap']), alpha=0.3, color='red', label='Duoi VWAP')
    
    ax1.set_title('MBS - VWAP Analysis', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Gia (VND)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Volume Profile (horizontal)
    price_bins = pd.cut(df['price'], bins=20)
    volume_profile = df.groupby(price_bins)['volume'].sum()
    
    # Get midpoints of bins
    bin_centers = [interval.mid for interval in volume_profile.index]
    
    ax2.barh(bin_centers, volume_profile.values, height=(max(bin_centers) - min(bin_centers))/20, 
             color='skyblue', alpha=0.7)
    ax2.set_title('MBS - Volume Profile', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Khoi luong')
    ax2.set_ylabel('Gia (VND)')
    ax2.grid(True, alpha=0.3)
    
    # 3. Trading zones based on volume
    high_volume_threshold = df['volume'].quantile(0.8)
    df['high_volume'] = df['volume'] > high_volume_threshold
    
    # Plot price with high volume zones highlighted
    ax3.plot(df['time'], df['price'], linewidth=1, color='blue', alpha=0.7)
    high_vol_times = df[df['high_volume']]['time']
    high_vol_prices = df[df['high_volume']]['price']
    ax3.scatter(high_vol_times, high_vol_prices, color='red', s=50, alpha=0.8, label='Vung khoi luong cao')
    
    ax3.set_title('MBS - Vung giao dich theo khoi luong', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Gia (VND)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Support/Resistance based on volume
    # Tìm các vùng giá có volume cao nhất
    top_volume_bins = volume_profile.nlargest(5)
    
    ax4.plot(df['time'], df['price'], linewidth=2, color='blue', label='Gia MBS')
    
    colors = ['red', 'orange', 'yellow', 'lightgreen', 'lightblue']
    for i, (price_range, volume) in enumerate(top_volume_bins.items()):
        price_level = price_range.mid
        ax4.axhline(y=price_level, color=colors[i], linestyle='--', alpha=0.7, 
                   label=f'Vol zone {i+1}: {price_level:.2f}')
    
    ax4.set_title('MBS - Vung gia quan trong theo Volume', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Gia (VND)')
    ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/additional_analysis/trading_zones.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_performance_dashboard(df, intraday_data, financial_ratios):
    """Tạo dashboard hiệu suất tổng thể"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Performance metrics
    if len(df) > 1:
        total_return = (df['price'].iloc[-1] - df['price'].iloc[0]) / df['price'].iloc[0] * 100
        max_gain = (df['price'].max() - df['price'].iloc[0]) / df['price'].iloc[0] * 100
        max_loss = (df['price'].min() - df['price'].iloc[0]) / df['price'].iloc[0] * 100
        
        performance_metrics = ['Loi nhuan hien tai', 'Loi nhuan toi da', 'Thua lo toi da']
        performance_values = [total_return, max_gain, max_loss]
        colors = ['green' if x > 0 else 'red' for x in performance_values]
        
        bars = ax1.bar(performance_metrics, performance_values, color=colors, alpha=0.7)
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax1.set_title('MBS - Hieu suat giao dich', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Ty le (%)')
        
        for bar, value in zip(bars, performance_values):
            ax1.text(bar.get_x() + bar.get_width()/2., 
                    bar.get_height() + (0.5 if value > 0 else -1),
                    f'{value:.2f}%', ha='center', va='bottom' if value > 0 else 'top')
        
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
    
    # 2. Volume efficiency
    df['volume_efficiency'] = df['price'].diff().abs() / df['volume'] * 1000000  # price change per million shares
    
    ax2.plot(df['time'], df['volume_efficiency'], linewidth=2, color='purple')
    ax2.set_title('MBS - Hieu qua khoi luong', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Thay doi gia / Trieu co phieu')
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Trading intensity vs market
    avg_volume = df['volume'].mean()
    df['intensity'] = df['volume'] / avg_volume
    
    intensity_colors = ['green' if x > 1.5 else 'orange' if x > 1 else 'red' for x in df['intensity']]
    ax3.scatter(df['time'], df['intensity'], c=intensity_colors, alpha=0.6, s=30)
    ax3.axhline(y=1, color='black', linestyle='--', alpha=0.7, label='Trung binh')
    ax3.axhline(y=1.5, color='green', linestyle='--', alpha=0.7, label='Cao')
    ax3.set_title('MBS - Cuong do giao dich', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Cuong do (vs trung binh)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Overall score
    # Tính điểm tổng hợp
    liquidity_score = min(100, (df['volume'].mean() / 1000000) * 10)  # 10 points per million
    volatility = df['price'].std() / df['price'].mean() * 100
    volatility_score = max(0, 100 - volatility * 10)  # Lower volatility = higher score
    trend_score = 100 if total_return > 0 else 50 if total_return > -2 else 25
    
    fundamental_score = 50
    if financial_ratios and 'data' in financial_ratios:
        ratios_df = pd.DataFrame(financial_ratios['data'])
        if len(ratios_df) > 0 and 'Chỉ tiêu hiệu quả_ROE (%)' in ratios_df.columns:
            roe = pd.to_numeric(ratios_df['Chỉ tiêu hiệu quả_ROE (%)'].iloc[0], errors='coerce')
            if not pd.isna(roe):
                fundamental_score = min(100, max(0, roe * 5))  # ROE to score conversion
    
    scores = {
        'Thanh khoan': liquidity_score,
        'On dinh': volatility_score, 
        'Xu huong': trend_score,
        'Co ban': fundamental_score
    }
    
    overall_score = sum(scores.values()) / len(scores)
    
    categories = list(scores.keys())
    values = list(scores.values())
    colors = ['green' if v > 70 else 'orange' if v > 50 else 'red' for v in values]
    
    bars = ax4.bar(categories, values, color=colors, alpha=0.7)
    ax4.axhline(y=70, color='green', linestyle='--', alpha=0.7, label='Tot (>70)')
    ax4.axhline(y=50, color='orange', linestyle='--', alpha=0.7, label='Trung binh (>50)')
    ax4.set_title(f'MBS - Diem tong hop: {overall_score:.1f}/100', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Diem')
    ax4.set_ylim(0, 100)
    ax4.legend()
    
    for bar, value in zip(bars, values):
        ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                f'{value:.0f}', ha='center', va='bottom')
    
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/additional_analysis/performance_dashboard.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    create_additional_charts()