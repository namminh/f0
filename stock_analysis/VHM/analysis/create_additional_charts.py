#!/usr/bin/env python3
"""
Create Additional Analysis Charts for VHM
Tạo biểu đồ phân tích bổ sung cho VHM
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set font for better compatibility
plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

def create_additional_charts():
    """Tạo các biểu đồ phân tích bổ sung"""
    
    # Create directories
    Path("stock_analysis/VHM/charts/additional_analysis").mkdir(parents=True, exist_ok=True)

    # Load data
    try:
        with open("stock_analysis/VHM/data/VHM_intraday_data.json", "r", encoding="utf-8") as f:
            intraday_data = json.load(f)
    except FileNotFoundError:
        print("Không tìm thấy dữ liệu intraday VHM")
        return

    if not intraday_data or 'data' not in intraday_data:
        print("Dữ liệu không hợp lệ")
        return

    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)

    # Create additional analysis charts
    create_price_action_analysis(df)
    create_liquidity_analysis(df)
    create_risk_assessment(df)
    create_trading_zones(df)
    create_performance_dashboard(df, intraday_data)
    
    print("Additional analysis charts created successfully for VHM")

def create_price_action_analysis(df):
    """Phân tích price action và support/resistance"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Price with support/resistance levels
    ax1.plot(df['time'], df['price'], linewidth=2, color='blue', label='VHM Price')
    
    # Calculate support and resistance levels
    high_price = df['price'].max()
    low_price = df['price'].min()
    price_range = high_price - low_price
    
    # Support levels
    support_1 = low_price + price_range * 0.2
    support_2 = low_price + price_range * 0.4
    resistance_1 = high_price - price_range * 0.2
    resistance_2 = high_price - price_range * 0.4
    
    ax1.axhline(y=support_1, color='green', linestyle='--', alpha=0.7, label='Support 1')
    ax1.axhline(y=support_2, color='green', linestyle=':', alpha=0.7, label='Support 2')
    ax1.axhline(y=resistance_1, color='red', linestyle='--', alpha=0.7, label='Resistance 1')
    ax1.axhline(y=resistance_2, color='red', linestyle=':', alpha=0.7, label='Resistance 2')
    
    ax1.set_title('VHM - Price Action with Support/Resistance', fontweight='bold')
    ax1.set_ylabel('Price (VND)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Price momentum analysis
    df['price_change'] = df['price'].pct_change()
    df['momentum'] = df['price_change'].rolling(window=10).mean()
    
    colors = ['green' if x >= 0 else 'red' for x in df['momentum']]
    ax2.bar(df['time'], df['momentum'], color=colors, alpha=0.7, width=0.0001)
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.8)
    ax2.set_title('VHM - Price Momentum Analysis', fontweight='bold')
    ax2.set_ylabel('Momentum')
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # Candlestick pattern simulation
    df['hour'] = df['time'].dt.hour
    hourly_data = df.groupby('hour').agg({
        'price': ['first', 'max', 'min', 'last'],
        'volume': 'sum'
    }).reset_index()
    
    hourly_data.columns = ['hour', 'open', 'high', 'low', 'close', 'volume']
    
    # Create candlestick-like representation
    for i, row in hourly_data.iterrows():
        color = 'green' if row['close'] >= row['open'] else 'red'
        ax3.plot([row['hour'], row['hour']], [row['low'], row['high']], 
                color='black', linewidth=1)
        ax3.plot([row['hour'], row['hour']], [row['open'], row['close']], 
                color=color, linewidth=4, alpha=0.8)
    
    ax3.set_title('VHM - Hourly Price Patterns', fontweight='bold')
    ax3.set_xlabel('Hour')
    ax3.set_ylabel('Price (VND)')
    ax3.grid(True, alpha=0.3)
    
    # Volatility analysis
    df['volatility'] = df['price'].rolling(window=20).std()
    ax4.plot(df['time'], df['volatility'], color='purple', linewidth=2)
    ax4.fill_between(df['time'], df['volatility'], alpha=0.3, color='purple')
    ax4.set_title('VHM - Price Volatility Analysis', fontweight='bold')
    ax4.set_ylabel('Volatility (VND)')
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VHM/charts/additional_analysis/price_action_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_liquidity_analysis(df):
    """Phân tích thanh khoản thị trường"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Volume profile
    price_bins = pd.cut(df['price'], bins=20)
    volume_by_price = df.groupby(price_bins)['volume'].sum()
    
    ax1.barh(range(len(volume_by_price)), volume_by_price.values, alpha=0.7, color='steelblue')
    ax1.set_yticks(range(len(volume_by_price)))
    ax1.set_yticklabels([f'{interval.left:.1f}-{interval.right:.1f}' for interval in volume_by_price.index])
    ax1.set_title('VHM - Volume Profile by Price Range', fontweight='bold')
    ax1.set_xlabel('Total Volume')
    ax1.grid(True, alpha=0.3)
    
    # VWAP (Volume Weighted Average Price)
    df['vwap'] = (df['price'] * df['volume']).cumsum() / df['volume'].cumsum()
    
    ax2.plot(df['time'], df['price'], label='Price', linewidth=2, color='blue')
    ax2.plot(df['time'], df['vwap'], label='VWAP', linewidth=2, color='orange')
    ax2.fill_between(df['time'], df['price'], df['vwap'], 
                    where=(df['price'] >= df['vwap']), alpha=0.3, color='green', label='Above VWAP')
    ax2.fill_between(df['time'], df['price'], df['vwap'], 
                    where=(df['price'] < df['vwap']), alpha=0.3, color='red', label='Below VWAP')
    ax2.set_title('VHM - Price vs VWAP', fontweight='bold')
    ax2.set_ylabel('Price (VND)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # Liquidity by time
    df['hour'] = df['time'].dt.hour
    liquidity_by_hour = df.groupby('hour').agg({
        'volume': 'sum',
        'price': 'std'
    }).reset_index()
    
    ax3_twin = ax3.twinx()
    
    bars = ax3.bar(liquidity_by_hour['hour'], liquidity_by_hour['volume'], 
                   alpha=0.7, color='lightblue', label='Volume')
    line = ax3_twin.plot(liquidity_by_hour['hour'], liquidity_by_hour['price'], 
                        'ro-', linewidth=2, label='Price Volatility')
    
    ax3.set_xlabel('Hour')
    ax3.set_ylabel('Volume', color='blue')
    ax3_twin.set_ylabel('Price Volatility (VND)', color='red')
    ax3.set_title('VHM - Liquidity and Volatility by Hour', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Market depth simulation
    # Simulate bid-ask spread
    df['bid_ask_spread'] = df['price'] * 0.001  # 0.1% spread assumption
    
    ax4.plot(df['time'], df['bid_ask_spread'], color='red', linewidth=2, label='Bid-Ask Spread')
    ax4.fill_between(df['time'], df['bid_ask_spread'], alpha=0.3, color='red')
    ax4.set_title('VHM - Market Depth (Bid-Ask Spread)', fontweight='bold')
    ax4.set_ylabel('Spread (VND)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VHM/charts/additional_analysis/liquidity_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_risk_assessment(df):
    """Phân tích rủi ro đầu tư"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Value at Risk (VaR) calculation
    returns = df['price'].pct_change().dropna()
    
    # Calculate VaR at different confidence levels
    var_95 = np.percentile(returns, 5)
    var_99 = np.percentile(returns, 1)
    
    ax1.hist(returns, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    ax1.axvline(var_95, color='red', linestyle='--', linewidth=2, label=f'VaR 95%: {var_95:.4f}')
    ax1.axvline(var_99, color='darkred', linestyle='--', linewidth=2, label=f'VaR 99%: {var_99:.4f}')
    ax1.set_title('VHM - Value at Risk (VaR) Distribution', fontweight='bold')
    ax1.set_xlabel('Returns')
    ax1.set_ylabel('Frequency')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Maximum Drawdown
    df['cumulative_returns'] = (1 + df['price'].pct_change()).cumprod()
    df['rolling_max'] = df['cumulative_returns'].expanding().max()
    df['drawdown'] = (df['cumulative_returns'] - df['rolling_max']) / df['rolling_max']
    
    ax2.fill_between(df['time'], df['drawdown'], alpha=0.7, color='red', label='Drawdown')
    ax2.plot(df['time'], df['drawdown'], color='darkred', linewidth=2)
    ax2.set_title('VHM - Maximum Drawdown Analysis', fontweight='bold')
    ax2.set_ylabel('Drawdown (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # Risk metrics summary
    volatility = returns.std() * np.sqrt(252)  # Annualized volatility
    max_drawdown = df['drawdown'].min()
    sharpe_ratio = (returns.mean() * 252) / volatility if volatility > 0 else 0
    
    ax3.axis('off')
    risk_summary = f"""
VHM - RISK ASSESSMENT SUMMARY
═══════════════════════════════════

📊 RISK METRICS:
  • Daily Volatility: {returns.std():.4f}
  • Annualized Volatility: {volatility:.2f}%
  • Value at Risk (95%): {var_95:.4f}
  • Value at Risk (99%): {var_99:.4f}
  • Maximum Drawdown: {max_drawdown:.2%}
  • Sharpe Ratio: {sharpe_ratio:.2f}

🎯 RISK LEVEL:
  • Overall Risk: {'HIGH' if volatility > 0.3 else 'MEDIUM' if volatility > 0.2 else 'LOW'}
  • Tail Risk: {'HIGH' if var_99 < -0.05 else 'MEDIUM' if var_99 < -0.03 else 'LOW'}
  • Drawdown Risk: {'HIGH' if max_drawdown < -0.2 else 'MEDIUM' if max_drawdown < -0.1 else 'LOW'}

⚠️ RISK FACTORS:
  • Real estate market volatility
  • Interest rate sensitivity
  • Regulatory changes
  • Market liquidity risk
    """
    
    ax3.text(0.1, 0.5, risk_summary, ha='left', va='center', fontsize=10,
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8),
             fontfamily='monospace')
    
    # Risk-Return scatter
    rolling_returns = df['price'].pct_change().rolling(window=10).mean()
    rolling_volatility = df['price'].pct_change().rolling(window=10).std()
    
    ax4.scatter(rolling_volatility, rolling_returns, alpha=0.6, color='blue', s=30)
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax4.axvline(x=0, color='black', linestyle='-', alpha=0.5)
    ax4.set_title('VHM - Risk-Return Profile', fontweight='bold')
    ax4.set_xlabel('Risk (Volatility)')
    ax4.set_ylabel('Return')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VHM/charts/additional_analysis/risk_assessment.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_trading_zones(df):
    """Phân tích các vùng giao dịch"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Price zones based on volume
    price_volume_df = df.groupby(pd.cut(df['price'], bins=10))['volume'].sum()
    
    ax1.barh(range(len(price_volume_df)), price_volume_df.values, alpha=0.7, color='steelblue')
    ax1.set_yticks(range(len(price_volume_df)))
    ax1.set_yticklabels([f'{interval.left:.1f}-{interval.right:.1f}' for interval in price_volume_df.index])
    ax1.set_title('VHM - Price Zones by Volume', fontweight='bold')
    ax1.set_xlabel('Total Volume')
    ax1.grid(True, alpha=0.3)
    
    # Time-based trading zones
    df['hour'] = df['time'].dt.hour
    hour_volume = df.groupby('hour')['volume'].sum()
    hour_price_change = df.groupby('hour')['price'].agg(['first', 'last'])
    hour_price_change['change'] = hour_price_change['last'] - hour_price_change['first']
    
    ax2.bar(hour_volume.index, hour_volume.values, alpha=0.7, color='lightcoral')
    ax2.set_title('VHM - Trading Activity by Hour', fontweight='bold')
    ax2.set_xlabel('Hour')
    ax2.set_ylabel('Volume')
    ax2.grid(True, alpha=0.3)
    
    # Volume-Price relationship
    ax3.scatter(df['volume'], df['price'], alpha=0.5, s=30, color='green')
    
    # Add trend line
    z = np.polyfit(df['volume'], df['price'], 1)
    p = np.poly1d(z)
    ax3.plot(df['volume'], p(df['volume']), "r--", alpha=0.8, linewidth=2)
    
    correlation = df['volume'].corr(df['price'])
    ax3.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
             transform=ax3.transAxes, bbox=dict(boxstyle="round", facecolor='wheat', alpha=0.8))
    
    ax3.set_title('VHM - Volume-Price Relationship', fontweight='bold')
    ax3.set_xlabel('Volume')
    ax3.set_ylabel('Price (VND)')
    ax3.grid(True, alpha=0.3)
    
    # Trading intensity heatmap
    df['minute_bucket'] = (df['time'].dt.minute // 15) * 15
    intensity_data = df.groupby(['hour', 'minute_bucket'])['volume'].sum().unstack(fill_value=0)
    
    sns.heatmap(intensity_data, ax=ax4, cmap='YlOrRd', 
                annot=True, fmt='.0f', cbar_kws={'label': 'Volume'},
                xticklabels=['0-15', '15-30', '30-45', '45-60'])
    ax4.set_title('VHM - Trading Intensity Heatmap', fontweight='bold')
    ax4.set_xlabel('Minutes')
    ax4.set_ylabel('Hour')
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VHM/charts/additional_analysis/trading_zones.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_performance_dashboard(df, intraday_data):
    """Tạo dashboard hiệu suất tổng thể"""
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)
    
    # Title
    ax_title = fig.add_subplot(gs[0, :])
    ax_title.axis('off')
    
    # Calculate performance metrics
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
    
    title_text = f"""
VHM - VINHOMES PERFORMANCE DASHBOARD
═══════════════════════════════════════════════════════════════════════════════════════

📊 TRADING PERFORMANCE | 🕐 Updated: {timestamp}

🎯 KEY METRICS:
  • Total Volume: {total_volume:,.0f} shares
  • Price Range: {low_price:.2f} - {high_price:.2f} VND
  • Price Change: {price_change:+.2f} VND ({price_change_pct:+.2f}%)
  • Buy/Sell Ratio: {buy_sell_ratio:.2f}
  • Volatility: {volatility:.2f} VND
    """
    
    ax_title.text(0.5, 0.5, title_text, ha='center', va='center', fontsize=12,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8),
                 fontfamily='monospace')
    
    # Performance gauges
    ax1 = fig.add_subplot(gs[1, 0])
    performance_score = min(100, max(0, 50 + price_change_pct * 10))
    create_performance_gauge(ax1, performance_score, 'Performance Score', 0, 100)
    
    ax2 = fig.add_subplot(gs[1, 1])
    liquidity_score = min(100, (total_volume / 10000000) * 100)
    create_performance_gauge(ax2, liquidity_score, 'Liquidity Score', 0, 100)
    
    ax3 = fig.add_subplot(gs[1, 2])
    volatility_score = min(100, max(0, 100 - (volatility / avg_price) * 1000))
    create_performance_gauge(ax3, volatility_score, 'Stability Score', 0, 100)
    
    # Volume analysis
    ax4 = fig.add_subplot(gs[2, 0])
    hour_volume = df.groupby(df['time'].dt.hour)['volume'].sum()
    bars = ax4.bar(hour_volume.index, hour_volume.values, alpha=0.7, color='steelblue')
    ax4.set_title('Volume by Hour', fontweight='bold')
    ax4.set_xlabel('Hour')
    ax4.set_ylabel('Volume')
    ax4.grid(True, alpha=0.3)
    
    # Price trend
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.plot(df['time'], df['price'], linewidth=2, color='blue')
    ax5.fill_between(df['time'], df['price'], alpha=0.3, color='blue')
    ax5.set_title('Price Trend', fontweight='bold')
    ax5.set_ylabel('Price (VND)')
    ax5.grid(True, alpha=0.3)
    ax5.tick_params(axis='x', rotation=45)
    
    # Summary statistics
    ax6 = fig.add_subplot(gs[2, 2])
    ax6.axis('off')
    
    summary_stats = f"""
SUMMARY STATISTICS:
═══════════════════

📈 PRICE METRICS:
  • Open: {df['price'].iloc[0]:.2f} VND
  • High: {high_price:.2f} VND
  • Low: {low_price:.2f} VND
  • Close: {df['price'].iloc[-1]:.2f} VND
  • Change: {price_change_pct:+.2f}%

📊 VOLUME METRICS:
  • Total: {total_volume:,.0f}
  • Average: {df['volume'].mean():.0f}
  • Peak Hour: {hour_volume.idxmax()}:00

⚖️ MARKET SENTIMENT:
  • Buy Pressure: {buy_volume/total_volume*100:.1f}%
  • Sell Pressure: {sell_volume/total_volume*100:.1f}%
  • Sentiment: {'BULLISH' if buy_sell_ratio > 1.1 else 'BEARISH' if buy_sell_ratio < 0.9 else 'NEUTRAL'}
    """
    
    ax6.text(0.1, 0.5, summary_stats, ha='left', va='center', fontsize=10,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.8),
             fontfamily='monospace')
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VHM/charts/additional_analysis/performance_dashboard.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_performance_gauge(ax, value, title, min_val, max_val):
    """Tạo biểu đồ gauge hiệu suất"""
    theta = np.linspace(0, np.pi, 100)
    
    # Color segments
    colors = ['red', 'orange', 'yellow', 'lightgreen', 'green']
    segments = 5
    
    for i in range(segments):
        start_angle = i * np.pi / segments
        end_angle = (i + 1) * np.pi / segments
        theta_seg = np.linspace(start_angle, end_angle, 20)
        ax.fill_between(theta_seg, 0, 1, color=colors[i], alpha=0.3)
    
    # Value needle
    value_angle = (value - min_val) / (max_val - min_val) * np.pi
    ax.plot([value_angle, value_angle], [0, 0.8], 'black', linewidth=4)
    ax.plot(value_angle, 0.8, 'ro', markersize=8)
    
    # Labels
    ax.text(0.5, -0.3, f'{value:.1f}', ha='center', va='center', fontsize=14, fontweight='bold')
    ax.set_title(title, fontweight='bold', pad=20)
    ax.set_xlim(-0.1, np.pi + 0.1)
    ax.set_ylim(-0.5, 1.1)
    ax.axis('off')

if __name__ == "__main__":
    create_additional_charts()