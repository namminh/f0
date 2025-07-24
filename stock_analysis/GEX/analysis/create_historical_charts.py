import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set Vietnamese font
plt.rcParams['font.family'] = ['Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

def create_historical_charts():
    """Tạo biểu đồ lịch sử giá cho GEX"""
    
    # Create directories
    Path("stock_analysis/GEX/charts/historical_analysis").mkdir(parents=True, exist_ok=True)

    # Load historical data
    try:
        with open("stock_analysis/GEX/data/GEX_historical_prices.json", "r", encoding="utf-8") as f:
            historical_data = json.load(f)
    except FileNotFoundError:
        print("Không tìm thấy dữ liệu lịch sử GEX")
        return

    if not historical_data or 'data' not in historical_data:
        print("Dữ liệu lịch sử không hợp lệ")
        return

    # Convert to DataFrame
    df = pd.DataFrame(historical_data['data'])
    
    # Parse datetime column (find 'time' column)
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'])
        df = df.set_index('time')
        df = df.sort_index()
    
    # Standardize column names to match expected format
    column_mapping = {
        'open': 'Open',
        'high': 'High',
        'low': 'Low', 
        'close': 'Close',
        'volume': 'Volume'
    }
    df.rename(columns=column_mapping, inplace=True)
    
    # Drop index column if exists
    if 'index' in df.columns:
        df = df.drop('index', axis=1)

    print(f"Creating historical charts for GEX with {len(df)} data points")
    
    # Create all historical analysis charts
    create_price_trend_analysis(df)
    create_volume_trend_analysis(df)
    create_technical_analysis_historical(df)
    create_performance_analysis(df)
    create_volatility_analysis(df)
    
    print("Historical charts created successfully for GEX")

def create_price_trend_analysis(df):
    """Phân tích xu hướng giá lịch sử"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Candlestick-like price chart
    ax1.plot(df.index, df['Close'], linewidth=2, color='blue', label='Giá đóng cửa')
    ax1.fill_between(df.index, df['Low'], df['High'], alpha=0.2, color='gray', label='Biên độ')
    
    # Moving averages
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    ax1.plot(df.index, df['MA20'], '--', color='orange', alpha=0.8, label='MA20')
    ax1.plot(df.index, df['MA50'], '--', color='red', alpha=0.8, label='MA50')
    
    ax1.set_title('GEX - Xu hướng Giá Lịch sử', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Giá (VND)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Price change percentage
    df['price_change_pct'] = df['Close'].pct_change() * 100
    colors = ['green' if x >= 0 else 'red' for x in df['price_change_pct']]
    ax2.bar(df.index, df['price_change_pct'], color=colors, alpha=0.7, width=1)
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.8)
    ax2.set_title('GEX - Thay đổi Giá Hàng ngày (%)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Thay đổi (%)')
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Price distribution
    ax3.hist(df['Close'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    ax3.axvline(df['Close'].mean(), color='red', linestyle='--', linewidth=2, 
               label=f'TB: {df["Close"].mean():.1f} VND')
    ax3.axvline(df['Close'].median(), color='orange', linestyle='--', linewidth=2,
               label=f'Median: {df["Close"].median():.1f} VND')
    ax3.set_title('GEX - Phân phối Giá', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Giá (VND)')
    ax3.set_ylabel('Tần suất')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Cumulative return
    df['cumulative_return'] = (1 + df['price_change_pct']/100).cumprod()
    ax4.plot(df.index, df['cumulative_return'], linewidth=2, color='green')
    ax4.fill_between(df.index, 1, df['cumulative_return'], alpha=0.3, color='green')
    ax4.axhline(y=1, color='black', linestyle='-', alpha=0.8)
    ax4.set_title('GEX - Tỷ suất Sinh lời Tích lũy', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Tỷ suất tích lũy')
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/GEX/charts/historical_analysis/price_trend_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_volume_trend_analysis(df):
    """Phân tích xu hướng khối lượng lịch sử"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Volume over time
    ax1.bar(df.index, df['Volume'], alpha=0.7, color='steelblue', width=1)
    
    # Volume moving average
    df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
    ax1.plot(df.index, df['Volume_MA20'], color='red', linewidth=2, label='Volume MA20')
    
    ax1.set_title('GEX - Xu hướng Khối lượng Lịch sử', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Khối lượng')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Volume vs Price correlation
    ax2.scatter(df['Volume'], df['Close'], alpha=0.6, color='green', s=20)
    
    # Add trend line
    z = np.polyfit(df['Volume'], df['Close'], 1)
    p = np.poly1d(z)
    ax2.plot(df['Volume'], p(df['Volume']), "r--", alpha=0.8, linewidth=2)
    
    correlation = df['Volume'].corr(df['Close'])
    ax2.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
             transform=ax2.transAxes, bbox=dict(boxstyle="round", facecolor='wheat', alpha=0.8))
    
    ax2.set_title('GEX - Tương quan Khối lượng vs Giá', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Khối lượng')
    ax2.set_ylabel('Giá (VND)')
    ax2.grid(True, alpha=0.3)
    
    # 3. Monthly volume analysis
    df_monthly = df.resample('M').agg({
        'Volume': 'sum',
        'Close': 'last'
    })
    
    ax3.bar(df_monthly.index, df_monthly['Volume'], alpha=0.7, color='lightcoral', width=20)
    ax3.set_title('GEX - Khối lượng Giao dịch Hàng tháng', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Tổng khối lượng')
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Volume distribution
    ax4.hist(df['Volume'], bins=30, alpha=0.7, color='purple', edgecolor='black')
    ax4.axvline(df['Volume'].mean(), color='red', linestyle='--', linewidth=2,
               label=f'TB: {df["Volume"].mean():.0f}')
    ax4.axvline(df['Volume'].median(), color='orange', linestyle='--', linewidth=2,
               label=f'Median: {df["Volume"].median():.0f}')
    ax4.set_title('GEX - Phân phối Khối lượng', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Khối lượng')
    ax4.set_ylabel('Tần suất')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/GEX/charts/historical_analysis/volume_trend_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_technical_analysis_historical(df):
    """Phân tích kỹ thuật lịch sử"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Calculate technical indicators
    df['RSI'] = calculate_rsi(df['Close'])
    df['MACD'], df['Signal'] = calculate_macd(df['Close'])
    df['BB_upper'], df['BB_middle'], df['BB_lower'] = calculate_bollinger_bands(df['Close'])
    
    # 1. Price with Bollinger Bands
    ax1.plot(df.index, df['Close'], label='Giá GEX', linewidth=2, color='blue')
    ax1.fill_between(df.index, df['BB_upper'], df['BB_lower'], alpha=0.2, color='gray')
    ax1.plot(df.index, df['BB_upper'], '--', color='red', alpha=0.7, label='BB Upper')
    ax1.plot(df.index, df['BB_middle'], '--', color='orange', alpha=0.7, label='BB Middle')
    ax1.plot(df.index, df['BB_lower'], '--', color='green', alpha=0.7, label='BB Lower')
    ax1.set_title('GEX - Giá với Bollinger Bands', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Giá (VND)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. RSI
    ax2.plot(df.index, df['RSI'], color='purple', linewidth=2)
    ax2.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Quá mua (70)')
    ax2.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Quá bán (30)')
    ax2.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
    ax2.fill_between(df.index, 30, 70, alpha=0.1, color='gray')
    ax2.set_title('GEX - RSI (Relative Strength Index)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('RSI')
    ax2.set_ylim(0, 100)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. MACD
    ax3.plot(df.index, df['MACD'], label='MACD', linewidth=2, color='blue')
    ax3.plot(df.index, df['Signal'], label='Signal', linewidth=2, color='red')
    ax3.bar(df.index, df['MACD'] - df['Signal'], alpha=0.3, color='green', label='Histogram', width=1)
    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.8)
    ax3.set_title('GEX - MACD', fontsize=14, fontweight='bold')
    ax3.set_ylabel('MACD')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Support and Resistance levels
    ax4.plot(df.index, df['Close'], linewidth=2, color='blue', label='Giá GEX')
    
    # Calculate support and resistance levels
    highs = df['High'].rolling(window=20).max()
    lows = df['Low'].rolling(window=20).min()
    
    ax4.plot(df.index, highs, '--', color='red', alpha=0.7, label='Resistance (20d high)')
    ax4.plot(df.index, lows, '--', color='green', alpha=0.7, label='Support (20d low)')
    ax4.fill_between(df.index, lows, highs, alpha=0.1, color='gray')
    
    ax4.set_title('GEX - Support & Resistance Levels', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Giá (VND)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/GEX/charts/historical_analysis/technical_analysis_historical.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_performance_analysis(df):
    """Phân tích hiệu suất lịch sử"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Monthly returns
    df['monthly_return'] = df['Close'].resample('M').last().pct_change() * 100
    monthly_returns = df['Close'].resample('M').last().pct_change() * 100
    
    colors = ['green' if x >= 0 else 'red' for x in monthly_returns]
    ax1.bar(monthly_returns.index, monthly_returns.values, color=colors, alpha=0.7, width=20)
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.8)
    ax1.set_title('GEX - Tỷ suất Sinh lời Hàng tháng', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Tỷ suất (%)')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Yearly performance
    yearly_performance = df['Close'].resample('Y').agg(['first', 'last'])
    yearly_performance['return'] = (yearly_performance['last'] / yearly_performance['first'] - 1) * 100
    
    colors = ['green' if x >= 0 else 'red' for x in yearly_performance['return']]
    ax2.bar(yearly_performance.index.year, yearly_performance['return'], color=colors, alpha=0.7)
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.8)
    ax2.set_title('GEX - Hiệu suất Hàng năm', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Tỷ suất (%)')
    ax2.grid(True, alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(yearly_performance['return']):
        ax2.text(yearly_performance.index.year[i], v + (1 if v >= 0 else -1), 
                f'{v:.1f}%', ha='center', va='bottom' if v >= 0 else 'top')
    
    # 3. Risk-Return scatter (quarterly)
    quarterly_returns = df['Close'].resample('Q').last().pct_change() * 100
    quarterly_volatility = df['Close'].resample('Q').apply(lambda x: x.pct_change().std() * np.sqrt(252) * 100)
    
    valid_data = pd.DataFrame({
        'return': quarterly_returns,
        'volatility': quarterly_volatility
    }).dropna()
    
    ax3.scatter(valid_data['volatility'], valid_data['return'], alpha=0.7, s=50, color='blue')
    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax3.axvline(x=0, color='black', linestyle='-', alpha=0.5)
    ax3.set_title('GEX - Risk-Return Profile (Quarterly)', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Risk (Volatility %)')
    ax3.set_ylabel('Return (%)')
    ax3.grid(True, alpha=0.3)
    
    # 4. Drawdown analysis
    df['rolling_max'] = df['Close'].expanding().max()
    df['drawdown'] = (df['Close'] - df['rolling_max']) / df['rolling_max'] * 100
    
    ax4.fill_between(df.index, df['drawdown'], 0, alpha=0.7, color='red', label='Drawdown')
    ax4.plot(df.index, df['drawdown'], color='darkred', linewidth=1)
    max_drawdown = df['drawdown'].min()
    ax4.axhline(y=max_drawdown, color='red', linestyle='--', linewidth=2,
               label=f'Max Drawdown: {max_drawdown:.1f}%')
    ax4.set_title('GEX - Drawdown Analysis', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Drawdown (%)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/GEX/charts/historical_analysis/performance_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_volatility_analysis(df):
    """Phân tích độ biến động lịch sử"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Calculate volatility metrics
    df['daily_return'] = df['Close'].pct_change()
    df['volatility_20d'] = df['daily_return'].rolling(window=20).std() * np.sqrt(252) * 100
    df['volatility_60d'] = df['daily_return'].rolling(window=60).std() * np.sqrt(252) * 100
    
    # 1. Rolling volatility
    ax1.plot(df.index, df['volatility_20d'], label='20-day Volatility', linewidth=2, color='blue')
    ax1.plot(df.index, df['volatility_60d'], label='60-day Volatility', linewidth=2, color='red')
    ax1.fill_between(df.index, df['volatility_20d'], alpha=0.3, color='blue')
    ax1.set_title('GEX - Rolling Volatility', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Volatility (%)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Daily returns distribution
    ax2.hist(df['daily_return'].dropna() * 100, bins=50, alpha=0.7, color='skyblue', 
             edgecolor='black', density=True)
    
    # Fit normal distribution
    mu, sigma = df['daily_return'].dropna().mean() * 100, df['daily_return'].dropna().std() * 100
    x = np.linspace(df['daily_return'].min() * 100, df['daily_return'].max() * 100, 100)
    ax2.plot(x, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp(-0.5 * ((x - mu) / sigma) ** 2), 
             'r-', linewidth=2, label=f'Normal (μ={mu:.2f}, σ={sigma:.2f})')
    
    ax2.axvline(mu, color='red', linestyle='--', alpha=0.7, label=f'Mean: {mu:.2f}%')
    ax2.set_title('GEX - Daily Returns Distribution', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Daily Return (%)')
    ax2.set_ylabel('Density')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Volatility vs Volume
    ax3.scatter(df['Volume'], df['volatility_20d'], alpha=0.6, s=30, color='green')
    
    # Add trend line
    valid_data = df[['Volume', 'volatility_20d']].dropna()
    if len(valid_data) > 1:
        z = np.polyfit(valid_data['Volume'], valid_data['volatility_20d'], 1)
        p = np.poly1d(z)
        ax3.plot(valid_data['Volume'], p(valid_data['Volume']), "r--", alpha=0.8, linewidth=2)
        
        correlation = valid_data['Volume'].corr(valid_data['volatility_20d'])
        ax3.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                 transform=ax3.transAxes, bbox=dict(boxstyle="round", facecolor='wheat', alpha=0.8))
    
    ax3.set_title('GEX - Volatility vs Volume', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Volume')
    ax3.set_ylabel('20d Volatility (%)')
    ax3.grid(True, alpha=0.3)
    
    # 4. Volatility regime analysis
    volatility_percentiles = df['volatility_20d'].quantile([0.25, 0.75])
    low_vol = df['volatility_20d'] <= volatility_percentiles[0.25]
    high_vol = df['volatility_20d'] >= volatility_percentiles[0.75]
    
    ax4.fill_between(df.index, 0, 1, where=low_vol, alpha=0.3, color='green', 
                     label='Low Volatility', transform=ax4.get_xaxis_transform())
    ax4.fill_between(df.index, 0, 1, where=high_vol, alpha=0.3, color='red', 
                     label='High Volatility', transform=ax4.get_xaxis_transform())
    ax4.plot(df.index, df['volatility_20d'], color='blue', linewidth=1)
    
    ax4.set_title('GEX - Volatility Regimes', fontsize=14, fontweight='bold')
    ax4.set_ylabel('20d Volatility (%)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/GEX/charts/historical_analysis/volatility_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()

# Technical indicator calculation functions
def calculate_rsi(prices, window=14):
    """Calculate RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD"""
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    return macd, signal_line

def calculate_bollinger_bands(prices, window=20, num_std=2):
    """Calculate Bollinger Bands"""
    rolling_mean = prices.rolling(window=window).mean()
    rolling_std = prices.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return upper_band, rolling_mean, lower_band

if __name__ == "__main__":
    create_historical_charts()