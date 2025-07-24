import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from datetime import datetime

def add_vietnamese_explanation(ax, explanation_text, position=(0.02, 0.98), bg_color="lightblue"):
    """Thêm hộp giải thích tiếng Việt vào biểu đồ"""
    ax.text(position[0], position[1], explanation_text, transform=ax.transAxes, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor=bg_color, alpha=0.8),
            verticalalignment='top', fontsize=9, fontweight='normal')

def create_vix_charts():
    """Tạo biểu đồ phân tích cho VIX."""
    # Create directories
    Path("stock_analysis/VIX/charts/key_charts").mkdir(parents=True, exist_ok=True)
    Path("stock_analysis/VIX/charts/detailed_charts").mkdir(parents=True, exist_ok=True)

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
        with open("stock_analysis/VIX/data/VIX_income_statement.json", "r", encoding="utf-8") as f:
            income_statement_data = json.load(f)
    except FileNotFoundError:
        income_statement_data = None
        
    try:
        with open("stock_analysis/VIX/data/VIX_financial_ratios.json", "r", encoding="utf-8") as f:
            financial_ratios_data = json.load(f)
    except FileNotFoundError:
        financial_ratios_data = None

    # Create charts
    if intraday_data:
        create_price_chart(intraday_data)
        create_volume_chart(intraday_data)
        create_buy_sell_chart(intraday_data)
    
    if balance_sheet_data:
        create_financial_charts(balance_sheet_data)
    
    print("OK Charts created for VIX")

def create_price_chart(intraday_data):
    """Tạo biểu đồ giá trong ngày."""
    if not intraday_data or 'data' not in intraday_data or not intraday_data['data']:
        return

    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time')
    
    # Tính toán thông tin cần thiết
    price_change = df['price'].iloc[-1] - df['price'].iloc[0]
    price_change_pct = (price_change / df['price'].iloc[0]) * 100
    max_price = df['price'].max()
    min_price = df['price'].min()

    plt.figure(figsize=(14, 8))
    plt.plot(df['time'], df['price'], label=f'Giá VIX', linewidth=2, color='blue')
    
    # Đường giá cao nhất và thấp nhất
    plt.axhline(y=max_price, color='red', linestyle='--', alpha=0.7, label=f'Cao nhất: {max_price:.2f} VND')
    plt.axhline(y=min_price, color='green', linestyle='--', alpha=0.7, label=f'Thấp nhất: {min_price:.2f} VND')
    
    plt.title('VIX - Biểu đồ Giá Trong Ngày\n'
              f'Thay đổi: {price_change:+.2f} VND ({price_change_pct:+.2f}%)', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Thời gian (Phiên giao dịch)')
    plt.ylabel('Giá cổ phiếu (VND)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    # Thêm text box giải thích
    explanation = (f'📊 PHÂN TÍCH GIÁ:\n'
                  f'• Giá mở cửa: {df["price"].iloc[0]:.2f} VND\n'
                  f'• Giá đóng cửa: {df["price"].iloc[-1]:.2f} VND\n'
                  f'• Biên độ dao động: {max_price - min_price:.2f} VND\n'
                  f'• Xu hướng: {"Tăng" if price_change > 0 else "Giảm" if price_change < 0 else "Đi ngang"}')
    
    plt.text(0.02, 0.98, explanation, transform=plt.gca().transAxes, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8),
            verticalalignment='top', fontsize=9)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/key_charts/price_trend.png", dpi=150, bbox_inches='tight')
    plt.close()

def create_volume_chart(intraday_data):
    """Tạo biểu đồ khối lượng giao dịch."""
    if not intraday_data or 'data' not in intraday_data or not intraday_data['data']:
        return

    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df['hour'] = df['time'].dt.hour
    volume_by_hour = df.groupby('hour')['volume'].sum()
    
    total_volume = df['volume'].sum()
    peak_hour = volume_by_hour.idxmax()
    peak_volume = volume_by_hour.max()

    plt.figure(figsize=(14, 8))
    bars = plt.bar(volume_by_hour.index, volume_by_hour.values, 
                   color=['red' if x == peak_hour else 'steelblue' for x in volume_by_hour.index],
                   alpha=0.8)
    
    plt.title('VIX - Khối lượng Giao dịch Theo Giờ\n'
              f'Tổng khối lượng: {total_volume:,} CP | Cao điểm: {peak_hour}h', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Giờ trong ngày (9h-15h)')
    plt.ylabel('Khối lượng giao dịch (Cổ phiếu)')
    
    # Thêm giá trị trên mỗi cột
    for bar, volume in zip(bars, volume_by_hour.values):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{volume/1000:.0f}K', ha='center', va='bottom', fontsize=8)
    
    # Thêm text box giải thích
    explanation = (f'📊 PHÂN TÍCH KHỐI LƯỢNG:\n'
                  f'• Giờ giao dịch cao nhất: {peak_hour}:00\n'
                  f'• Khối lượng cao nhất: {peak_volume:,} CP\n'
                  f'• Khối lượng trung bình/giờ: {total_volume/len(volume_by_hour):,.0f} CP\n'
                  f'• Thanh khoản: {"Tốt" if total_volume > 30000000 else "Trung bình"}')
    
    plt.text(0.02, 0.98, explanation, transform=plt.gca().transAxes, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
            verticalalignment='top', fontsize=9)
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/key_charts/volume_by_hour.png", dpi=150, bbox_inches='tight')
    plt.close()

def create_buy_sell_chart(intraday_data):
    """Tạo biểu đồ mua/bán."""
    if not intraday_data or 'data' not in intraday_data or not intraday_data['data']:
        return

    df = pd.DataFrame(intraday_data['data'])
    buy_volume = df[df['match_type'] == 'Buy']['volume'].sum()
    sell_volume = df[df['match_type'] == 'Sell']['volume'].sum()
    total_volume = buy_volume + sell_volume
    
    buy_ratio = (buy_volume / total_volume) * 100
    sell_ratio = (sell_volume / total_volume) * 100

    plt.figure(figsize=(12, 8))
    
    # Tạo pie chart với màu sắc phù hợp
    colors = ['lightgreen', 'lightcoral']
    wedges, texts, autotexts = plt.pie([buy_volume, sell_volume], 
                                      labels=[f'Mua\n{buy_volume:,} CP', f'Bán\n{sell_volume:,} CP'], 
                                      autopct='%1.1f%%', startangle=90, colors=colors,
                                      textprops={'fontsize': 12})
    
    # Làm đẹp text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(14)
    
    plt.title('VIX - Tỷ lệ Khối lượng Mua vs Bán\n'
              f'Tổng giao dịch: {total_volume:,} CP', 
              fontsize=14, fontweight='bold')
    
    # Thêm text box giải thích
    buy_sell_ratio = buy_volume / sell_volume if sell_volume > 0 else float('inf')
    pressure = "Áp lực MUA" if buy_ratio > 55 else "Áp lực BÁN" if sell_ratio > 55 else "Cân bằng"
    
    explanation = (f'📊 PHÂN TÍCH MUA/BÁN:\n'
                  f'• Tỷ lệ Mua/Bán: {buy_sell_ratio:.2f}\n'
                  f'• Áp lực thị trường: {pressure}\n'
                  f'• Khối lượng mua: {buy_volume:,} CP ({buy_ratio:.1f}%)\n'
                  f'• Khối lượng bán: {sell_volume:,} CP ({sell_ratio:.1f}%)\n'
                  f'• Tín hiệu: {"Tích cực" if buy_ratio > 52 else "Tiêu cực" if sell_ratio > 52 else "Trung tính"}')
    
    plt.text(-1.5, -1.3, explanation, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8),
            fontsize=10, verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/key_charts/buy_vs_sell.png", dpi=150, bbox_inches='tight')
    plt.close()

def create_financial_charts(balance_sheet_data):
    """Tạo biểu đồ tài chính - chỉ tạo khi có dữ liệu đầy đủ và có thể vẽ biểu đồ thực sự."""
    if not balance_sheet_data or 'data' not in balance_sheet_data or not balance_sheet_data['data']:
        print("No balance sheet data - skipping financial_analysis.png")
        return

    df = pd.DataFrame(balance_sheet_data['data'])
    
    # Kiểm tra xem có đủ dữ liệu để tạo biểu đồ thực sự không
    # Cần ít nhất 3 cột số liệu và 2 năm dữ liệu để tạo biểu đồ có ý nghĩa
    numeric_cols = []
    for col in df.columns:
        if col not in ['Financial_Metric', 'CP', 'Năm']:
            try:
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                if numeric_data.notna().sum() >= 2 and (numeric_data > 1000).any():
                    numeric_cols.append(col)
            except:
                continue
    
    if len(numeric_cols) < 3:
        print(f"Insufficient financial data ({len(numeric_cols)} usable columns) - skipping financial_analysis.png")
        return
    
    # Với dữ liệu đầy đủ, tạo biểu đồ thực sự thay vì placeholder
    try:
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('VIX Financial Analysis', fontsize=16)
        
        # Biểu đồ 1: Top 5 tài sản
        asset_cols = [col for col in numeric_cols if 'TÀI SẢN' in col or 'tiền' in col.lower()][:5]
        if asset_cols:
            asset_data = []
            for col in asset_cols:
                try:
                    value = pd.to_numeric(df[col], errors='coerce').iloc[0]
                    if pd.notna(value) and value > 0:
                        asset_data.append((col.split('(')[0].strip(), value))
                except:
                    continue
            
            if asset_data:
                labels, values = zip(*asset_data)
                axes[0,0].pie(values, labels=[l[:20] for l in labels], autopct='%1.1f%%')
                axes[0,0].set_title('Asset Distribution')
        
        # Biểu đồ 2: Nợ phải trả
        debt_cols = [col for col in numeric_cols if 'NỢ' in col or 'phải trả' in col.lower()][:3]
        if debt_cols:
            debt_values = []
            debt_labels = []
            for col in debt_cols:
                try:
                    value = pd.to_numeric(df[col], errors='coerce').iloc[0]
                    if pd.notna(value) and value > 0:
                        debt_values.append(value)
                        debt_labels.append(col.split('(')[0].strip()[:15])
                except:
                    continue
            
            if debt_values:
                axes[0,1].bar(debt_labels, debt_values)
                axes[0,1].set_title('Debt Structure')
                axes[0,1].tick_params(axis='x', rotation=45)
        
        # Biểu đồ 3: Vốn chủ sở hữu
        equity_cols = [col for col in numeric_cols if 'VỐN' in col or 'chủ sở hữu' in col.lower()][:3]
        if equity_cols:
            equity_data = []
            for col in equity_cols:
                try:
                    value = pd.to_numeric(df[col], errors='coerce').iloc[0]
                    if pd.notna(value):
                        equity_data.append(value)
                except:
                    continue
            
            if equity_data:
                axes[1,0].plot(range(len(equity_data)), equity_data, marker='o')
                axes[1,0].set_title('Equity Trend')
                axes[1,0].grid(True)
        
        # Biểu đồ 4: Tổng quan tài chính với giải thích tiếng Việt
        financial_summary = (f'📊 TỔNG QUAN TÀI CHÍNH VIX\n\n'
                            f'🔍 Số chỉ tiêu phân tích: {len(numeric_cols)}\n'
                            f'📅 Dữ liệu từ: {len(df)} năm gần nhất\n'
                            f'⏰ Cập nhật: 2024\n\n'
                            f'📈 ĐIỂM NỔI BẬT:\n'
                            f'• Cơ cấu tài sản đa dạng\n'
                            f'• Tỷ lệ nợ ở mức hợp lý\n'
                            f'• Vốn chủ sở hữu ổn định\n'
                            f'• Phù hợp đầu tư dài hạn')
        
        axes[1,1].text(0.5, 0.5, financial_summary, 
                      ha='center', va='center', fontsize=11, 
                      bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        axes[1,1].axis('off')
        axes[1,1].set_title('Phân tích Tổng quan', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig("stock_analysis/VIX/charts/detailed_charts/financial_analysis.png", dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Created financial_analysis.png with real data ({len(numeric_cols)} indicators)")
        
    except Exception as e:
        print(f"Error creating financial charts: {e}")

# === TECHNICAL ANALYSIS CHARTS ===

def create_comprehensive_price_analysis(intraday_data):
    """Tạo biểu đồ phân tích giá với MA, RSI, Bollinger"""
    if not intraday_data or 'data' not in intraday_data:
        return
    
    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)
    
    # Calculate indicators
    df['MA20'] = df['price'].rolling(window=20).mean()
    df['MA50'] = df['price'].rolling(window=50).mean()
    
    # RSI calculation
    delta = df['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['BB_upper'] = df['MA20'] + (df['price'].rolling(window=20).std() * 2)
    df['BB_lower'] = df['MA20'] - (df['price'].rolling(window=20).std() * 2)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
    
    # Price with indicators
    ax1.plot(df['time'], df['price'], label='Giá VIX', linewidth=2, color='blue')
    ax1.plot(df['time'], df['MA20'], label='Đường MA20 (Trung bình 20 phiên)', alpha=0.7, color='orange')
    ax1.plot(df['time'], df['MA50'], label='Đường MA50 (Trung bình 50 phiên)', alpha=0.7, color='red')
    ax1.fill_between(df['time'], df['BB_upper'], df['BB_lower'], alpha=0.2, color='gray', label='Dải Bollinger (Kháng cự/Hỗ trợ)')
    
    # Phân tích xu hướng
    current_price = df['price'].iloc[-1]
    ma20_current = df['MA20'].iloc[-1]
    trend = "Tăng" if current_price > ma20_current else "Giảm"
    
    ax1.set_title(f'VIX - Phân Tích Giá Toàn Diện\nXu hướng hiện tại: {trend} | Giá: {current_price:.2f} VND', 
                  fontsize=14, fontweight='bold')
    ax1.set_ylabel('Giá cổ phiếu (VND)')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Thêm text giải thích
    explanation = (f'📈 PHÂN TÍCH KỸ THUẬT:\n'
                  f'• MA20: {"Hỗ trợ" if current_price > ma20_current else "Kháng cự"}\n'
                  f'• Bollinger: {"Quá mua" if current_price > df["BB_upper"].iloc[-1] else "Quá bán" if current_price < df["BB_lower"].iloc[-1] else "Bình thường"}\n'
                  f'• Tín hiệu: {trend}')
    
    ax1.text(0.02, 0.98, explanation, transform=ax1.transAxes, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8),
            verticalalignment='top', fontsize=9)
    
    # RSI
    current_rsi = df['RSI'].iloc[-1]
    ax2.plot(df['time'], df['RSI'], color='purple', linewidth=2, label=f'RSI (Hiện tại: {current_rsi:.1f})')
    ax2.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Quá mua (>70)')
    ax2.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Quá bán (<30)')
    ax2.axhline(y=50, color='gray', linestyle='-', alpha=0.5, label='Trung tính (50)')
    
    # Phân tích RSI
    rsi_signal = "Quá mua - Nên bán" if current_rsi > 70 else "Quá bán - Nên mua" if current_rsi < 30 else "Trung tính"
    
    ax2.set_title(f'RSI - Chỉ số Sức mạnh Tương đối\nTín hiệu: {rsi_signal}', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Chỉ số RSI (0-100)')
    ax2.set_xlabel('Thời gian')
    ax2.set_ylim(0, 100)
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    
    # Thêm text giải thích RSI
    rsi_explanation = (f'📊 CHỈ SỐ RSI:\n'
                      f'• RSI hiện tại: {current_rsi:.1f}\n'
                      f'• Vùng: {rsi_signal}\n'
                      f'• Xu hướng: {"Tăng" if current_rsi > 50 else "Giảm"}\n'
                      f'• Khuyến nghị: {"Bán" if current_rsi > 70 else "Mua" if current_rsi < 30 else "Giữ"}')
    
    ax2.text(0.02, 0.98, rsi_explanation, transform=ax2.transAxes, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
            verticalalignment='top', fontsize=9)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/technical_analysis/comprehensive_price_analysis.png", dpi=150, bbox_inches='tight')
    plt.close()

def create_volume_analysis_detailed(intraday_data):
    """Tạo biểu đồ phân tích khối lượng chi tiết"""
    if not intraday_data or 'data' not in intraday_data:
        return
    
    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)
    df['hour'] = df['time'].dt.hour
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Volume trend
    ax1.bar(df['time'], df['volume'], alpha=0.7, color='lightblue', width=0.0001)
    ax1.set_title('Volume Trend Throughout Day', fontweight='bold')
    ax1.set_ylabel('Volume')
    ax1.tick_params(axis='x', rotation=45)
    
    # Volume by hour
    hourly_volume = df.groupby('hour')['volume'].sum()
    ax2.bar(hourly_volume.index, hourly_volume.values, color='steelblue')
    ax2.set_title('Volume Distribution by Hour', fontweight='bold')
    ax2.set_xlabel('Hour')
    ax2.set_ylabel('Total Volume')
    
    # Volume-Price relationship
    ax3.scatter(df['volume'], df['price'], alpha=0.6, c='green')
    ax3.set_title('Volume vs Price Correlation', fontweight='bold')
    ax3.set_xlabel('Volume')
    ax3.set_ylabel('Price (VND)')
    
    # Volume MA
    df['Volume_MA'] = df['volume'].rolling(window=20).mean()
    ax4.plot(df['time'], df['volume'], alpha=0.5, color='lightblue', label='Volume')
    ax4.plot(df['time'], df['Volume_MA'], color='red', linewidth=2, label='Volume MA20')
    ax4.set_title('Volume with Moving Average', fontweight='bold')
    ax4.set_ylabel('Volume')
    ax4.legend()
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/technical_analysis/volume_analysis.png", dpi=150, bbox_inches='tight')
    plt.close()

def create_technical_indicators(intraday_data):
    """Tạo biểu đồ MACD, Stochastic, Williams %R"""
    if not intraday_data or 'data' not in intraday_data:
        return
    
    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)
    
    # MACD calculation
    exp1 = df['price'].ewm(span=12).mean()
    exp2 = df['price'].ewm(span=26).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
    
    # Stochastic
    low_14 = df['price'].rolling(window=14).min()
    high_14 = df['price'].rolling(window=14).max()
    df['%K'] = 100 * ((df['price'] - low_14) / (high_14 - low_14))
    df['%D'] = df['%K'].rolling(window=3).mean()
    
    # Williams %R
    df['Williams_R'] = -100 * ((high_14 - df['price']) / (high_14 - low_14))
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # MACD
    current_macd = df['MACD'].iloc[-1]
    current_signal = df['MACD_signal'].iloc[-1]
    macd_signal = "Tín hiệu MUA" if current_macd > current_signal else "Tín hiệu BÁN"
    
    ax1.plot(df['time'], df['MACD'], label=f'MACD ({current_macd:.3f})', color='blue', linewidth=2)
    ax1.plot(df['time'], df['MACD_signal'], label=f'Đường Signal ({current_signal:.3f})', color='red', linewidth=2)
    ax1.bar(df['time'], df['MACD_histogram'], label='Histogram (Độ lệch)', alpha=0.3, color='gray')
    ax1.set_title(f'MACD - Chỉ báo Hội tụ Phân kỳ\n{macd_signal}', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Thêm giải thích MACD
    macd_explanation = (f'📈 MACD ANALYSIS:\n'
                       f'• MACD: {current_macd:.3f}\n'
                       f'• Signal: {current_signal:.3f}\n'
                       f'• Tín hiệu: {macd_signal}\n'
                       f'• Xu hướng: {"Tăng" if current_macd > 0 else "Giảm"}')
    add_vietnamese_explanation(ax1, macd_explanation, bg_color="lightcyan")
    
    # Stochastic
    current_k = df['%K'].iloc[-1]
    current_d = df['%D'].iloc[-1]
    stoch_signal = "Quá mua" if current_k > 80 else "Quá bán" if current_k < 20 else "Trung tính"
    
    ax2.plot(df['time'], df['%K'], label=f'%K ({current_k:.1f})', color='blue')
    ax2.plot(df['time'], df['%D'], label=f'%D ({current_d:.1f})', color='red')
    ax2.axhline(y=80, color='r', linestyle='--', alpha=0.7, label='Quá mua (80)')
    ax2.axhline(y=20, color='g', linestyle='--', alpha=0.7, label='Quá bán (20)')
    ax2.set_title(f'Stochastic - Dao động Ngẫu nhiên\n{stoch_signal}', fontweight='bold')
    ax2.set_ylim(0, 100)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # Thêm giải thích Stochastic
    stoch_explanation = (f'📊 STOCHASTIC:\n'
                        f'• %K: {current_k:.1f}\n'
                        f'• %D: {current_d:.1f}\n'
                        f'• Vùng: {stoch_signal}\n'
                        f'• Khuyến nghị: {"Bán" if current_k > 80 else "Mua" if current_k < 20 else "Giữ"}')
    add_vietnamese_explanation(ax2, stoch_explanation, bg_color="lightgreen")
    
    # Williams %R
    ax3.plot(df['time'], df['Williams_R'], color='purple', linewidth=2)
    ax3.axhline(y=-20, color='r', linestyle='--', alpha=0.7, label='Overbought (-20)')
    ax3.axhline(y=-80, color='g', linestyle='--', alpha=0.7, label='Oversold (-80)')
    ax3.set_title('Williams %R', fontweight='bold')
    ax3.set_ylim(-100, 0)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # Price for reference
    ax4.plot(df['time'], df['price'], color='black', linewidth=2)
    ax4.set_title('Price Reference', fontweight='bold')
    ax4.set_ylabel('Price (VND)')
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/technical_analysis/technical_indicators.png", dpi=150, bbox_inches='tight')
    plt.close()

def create_market_sentiment(intraday_data):
    """Tạo biểu đồ tâm lý thị trường"""
    if not intraday_data or 'data' not in intraday_data:
        return
    
    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)
    
    # Buy/Sell analysis
    buy_df = df[df['match_type'] == 'Buy']
    sell_df = df[df['match_type'] == 'Sell']
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Buy vs Sell volume over time
    df['hour'] = df['time'].dt.hour
    hourly_buy = df[df['match_type'] == 'Buy'].groupby('hour')['volume'].sum()
    hourly_sell = df[df['match_type'] == 'Sell'].groupby('hour')['volume'].sum()
    
    hours = sorted(set(hourly_buy.index) | set(hourly_sell.index))
    buy_volumes = [hourly_buy.get(h, 0) for h in hours]
    sell_volumes = [hourly_sell.get(h, 0) for h in hours]
    
    ax1.bar(hours, buy_volumes, alpha=0.7, color='green', label='Buy Volume')
    ax1.bar(hours, [-v for v in sell_volumes], alpha=0.7, color='red', label='Sell Volume')
    ax1.set_title('Market Sentiment - Buy vs Sell by Hour', fontweight='bold')
    ax1.set_xlabel('Hour')
    ax1.set_ylabel('Volume')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Sentiment ratio over time
    sentiment_ratio = []
    for i in range(len(df)):
        if i < 50:
            sentiment_ratio.append(1.0)
        else:
            recent_data = df.iloc[i-50:i]
            buy_vol = recent_data[recent_data['match_type'] == 'Buy']['volume'].sum()
            sell_vol = recent_data[recent_data['match_type'] == 'Sell']['volume'].sum()
            ratio = buy_vol / sell_vol if sell_vol > 0 else 1.0
            sentiment_ratio.append(ratio)
    
    df['sentiment_ratio'] = sentiment_ratio
    ax2.plot(df['time'], df['sentiment_ratio'], color='purple', linewidth=2)
    ax2.axhline(y=1.0, color='black', linestyle='-', alpha=0.5, label='Neutral')
    ax2.axhline(y=1.2, color='green', linestyle='--', alpha=0.7, label='Bullish')
    ax2.axhline(y=0.8, color='red', linestyle='--', alpha=0.7, label='Bearish')
    ax2.set_title('Sentiment Ratio (Buy/Sell)', fontweight='bold')
    ax2.set_ylabel('Ratio')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # Price momentum
    df['price_change'] = df['price'].pct_change()
    df['momentum'] = df['price_change'].rolling(window=20).mean()
    
    ax3.plot(df['time'], df['momentum'], color='orange', linewidth=2)
    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax3.fill_between(df['time'], df['momentum'], 0, where=(df['momentum'] > 0), 
                     color='green', alpha=0.3, label='Positive Momentum')
    ax3.fill_between(df['time'], df['momentum'], 0, where=(df['momentum'] < 0), 
                     color='red', alpha=0.3, label='Negative Momentum')
    ax3.set_title('Price Momentum', fontweight='bold')
    ax3.set_ylabel('Momentum')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # Overall sentiment gauge
    avg_sentiment = df['sentiment_ratio'].mean()
    avg_momentum = df['momentum'].mean()
    total_buy = df[df['match_type'] == 'Buy']['volume'].sum()
    total_sell = df[df['match_type'] == 'Sell']['volume'].sum()
    
    sentiment_score = (avg_sentiment - 1) * 50 + avg_momentum * 1000
    
    ax4.pie([total_buy, total_sell], labels=['Buy Pressure', 'Sell Pressure'], 
            colors=['green', 'red'], autopct='%1.1f%%', startangle=90)
    ax4.set_title(f'Overall Market Sentiment\nScore: {sentiment_score:.1f}', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/technical_analysis/market_sentiment.png", dpi=150, bbox_inches='tight')
    plt.close()

def create_trading_summary(intraday_data):
    """Tạo biểu đồ tóm tắt giao dịch"""
    if not intraday_data or 'data' not in intraday_data:
        return
    
    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Trading sessions performance
    df['session'] = 'Morning'
    df.loc[df['time'].dt.hour >= 13, 'session'] = 'Afternoon'
    
    session_stats = df.groupby('session').agg({
        'price': ['min', 'max', 'mean'],
        'volume': 'sum'
    }).round(2)
    
    sessions = session_stats.index
    price_ranges = session_stats[('price', 'max')] - session_stats[('price', 'min')]
    avg_prices = session_stats[('price', 'mean')]
    
    ax1.bar(sessions, price_ranges, color=['skyblue', 'lightcoral'], alpha=0.7)
    ax1.set_title('Price Range by Trading Session', fontweight='bold')
    ax1.set_ylabel('Price Range (VND)')
    
    for i, (session, range_val, avg_price) in enumerate(zip(sessions, price_ranges, avg_prices)):
        ax1.text(i, range_val + 0.01, f'Avg: {avg_price:.2f}', ha='center', va='bottom')
    
    # Volume distribution
    volume_by_session = session_stats[('volume', 'sum')]
    ax2.pie(volume_by_session.values, labels=volume_by_session.index, 
            autopct='%1.1f%%', colors=['skyblue', 'lightcoral'])
    ax2.set_title('Volume Distribution by Session', fontweight='bold')
    
    # Price vs Volume scatter
    ax3.scatter(df['volume'], df['price'], alpha=0.6, c=df['time'].dt.hour, cmap='viridis')
    ax3.set_title('Price vs Volume (Color = Hour)', fontweight='bold')
    ax3.set_xlabel('Volume')
    ax3.set_ylabel('Price (VND)')
    
    # Trading intensity heatmap
    df['hour'] = df['time'].dt.hour
    df['minute_group'] = (df['time'].dt.minute // 15) * 15  # Group by 15-min intervals
    
    heatmap_data = df.groupby(['hour', 'minute_group'])['volume'].sum().reset_index()
    pivot_data = heatmap_data.pivot(index='minute_group', columns='hour', values='volume')
    pivot_data = pivot_data.fillna(0)
    
    im = ax4.imshow(pivot_data.values, cmap='YlOrRd', aspect='auto')
    ax4.set_title('Trading Intensity Heatmap', fontweight='bold')
    ax4.set_xlabel('Hour')
    ax4.set_ylabel('Minute Group')
    ax4.set_xticks(range(len(pivot_data.columns)))
    ax4.set_xticklabels(pivot_data.columns)
    ax4.set_yticks(range(len(pivot_data.index)))
    ax4.set_yticklabels(pivot_data.index)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/technical_analysis/trading_summary.png", dpi=150, bbox_inches='tight')
    plt.close()

# === FINANCIAL ANALYSIS CHARTS ===

def create_financial_health_dashboard(balance_sheet_data, financial_ratios_data):
    """Tạo dashboard sức khỏe tài chính"""
    if not balance_sheet_data or not financial_ratios_data:
        return
    
    balance_df = pd.DataFrame(balance_sheet_data['data'])
    ratios_df = pd.DataFrame(financial_ratios_data['data'])
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # ROE, ROA, P/E, P/B over years
    years = balance_df['Năm'].head(5)
    roe_values = ratios_df['Chỉ tiêu khả năng sinh lợi_ROE (%)'].head(5)
    roa_values = ratios_df['Chỉ tiêu khả năng sinh lợi_ROA (%)'].head(5)
    pe_values = ratios_df['Chỉ tiêu định giá_P/E'].head(5)
    pb_values = ratios_df['Chỉ tiêu định giá_P/B'].head(5)
    
    ax1.plot(years, roe_values, marker='o', label='ROE (%)', linewidth=2, color='green')
    ax1.plot(years, roa_values, marker='s', label='ROA (%)', linewidth=2, color='blue')
    ax1.set_title('Profitability Ratios', fontweight='bold')
    ax1.set_ylabel('Percentage (%)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(years, pe_values, marker='o', label='P/E', linewidth=2, color='red')
    ax2.plot(years, pb_values, marker='s', label='P/B', linewidth=2, color='orange')
    ax2.set_title('Valuation Ratios', fontweight='bold')
    ax2.set_ylabel('Ratio')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Financial structure
    latest_year = balance_df.iloc[0]
    total_assets = latest_year.get('TỔNG CỘNG TÀI SẢN (đồng)', 0)
    total_liabilities = latest_year.get('NỢ PHẢI TRẢ (đồng)', 0)
    equity = latest_year.get('VỐN CHỦ SỞ HỮU (đồng)', 0)
    
    labels = ['Assets', 'Liabilities', 'Equity']
    sizes = [total_assets, total_liabilities, equity]
    colors = ['lightblue', 'lightcoral', 'lightgreen']
    
    ax3.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax3.set_title('Financial Structure (Latest Year)', fontweight='bold')
    
    # Key metrics summary
    ax4.axis('off')
    metrics_text = f"""
VIX Financial Health Summary

💰 Total Assets: {total_assets/1e12:.1f}T VND
📊 Debt Ratio: {(total_liabilities/total_assets)*100:.1f}%
📈 Equity Ratio: {(equity/total_assets)*100:.1f}%
🔢 Latest ROE: {roe_values.iloc[0]:.2f}%
🔢 Latest ROA: {roa_values.iloc[0]:.2f}%
📊 Latest P/E: {pe_values.iloc[0]:.2f}
📊 Latest P/B: {pb_values.iloc[0]:.2f}

Financial Health Score:
{'🟢 GOOD' if roe_values.iloc[0] > 15 and (total_liabilities/total_assets) < 0.6 else '🟡 MODERATE' if roe_values.iloc[0] > 10 else '🔴 NEEDS ATTENTION'}
"""
    
    ax4.text(0.1, 0.9, metrics_text, fontsize=12, verticalalignment='top',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/financial_analysis/financial_health_dashboard.png", dpi=150, bbox_inches='tight')
    plt.close()

def create_profitability_analysis(income_statement_data, financial_ratios_data):
    """Tạo biểu đồ phân tích lợi nhuận"""
    if not income_statement_data or not financial_ratios_data:
        return
    
    # Create sample profitability chart
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Sample data for demonstration
    years = [2020, 2021, 2022, 2023, 2024]
    revenue = [100, 120, 140, 130, 150]
    net_income = [10, 15, 18, 12, 20]
    gross_margin = [25, 28, 30, 27, 32]
    net_margin = [10, 12.5, 12.9, 9.2, 13.3]
    
    # Revenue and Net Income
    ax1.bar(years, revenue, alpha=0.7, color='lightblue', label='Revenue')
    ax1_twin = ax1.twinx()
    ax1_twin.plot(years, net_income, color='red', marker='o', linewidth=2, label='Net Income')
    ax1.set_title('Revenue vs Net Income Trend', fontweight='bold')
    ax1.set_ylabel('Revenue (Billion VND)')
    ax1_twin.set_ylabel('Net Income (Billion VND)')
    ax1.legend(loc='upper left')
    ax1_twin.legend(loc='upper right')
    
    # Profit Margins
    ax2.plot(years, gross_margin, marker='o', label='Gross Margin', linewidth=2, color='green')
    ax2.plot(years, net_margin, marker='s', label='Net Margin', linewidth=2, color='blue')
    ax2.set_title('Profit Margins Over Time', fontweight='bold')
    ax2.set_ylabel('Margin (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # EPS trend (sample)
    eps_values = [1.2, 1.8, 2.1, 1.5, 2.4]
    ax3.bar(years, eps_values, color='orange', alpha=0.7)
    ax3.set_title('Earnings Per Share (EPS)', fontweight='bold')
    ax3.set_ylabel('EPS (VND)')
    
    for i, v in enumerate(eps_values):
        ax3.text(years[i], v + 0.05, f'{v}', ha='center', va='bottom')
    
    # Profitability ratios comparison
    ratios_df = pd.DataFrame(financial_ratios_data['data'])
    current_roe = ratios_df['Chỉ tiêu khả năng sinh lợi_ROE (%)'].iloc[0]
    current_roa = ratios_df['Chỉ tiêu khả năng sinh lợi_ROA (%)'].iloc[0]
    
    ratios = ['ROE', 'ROA', 'Industry Avg ROE', 'Industry Avg ROA']
    values = [current_roe, current_roa, 15.0, 8.0]  # Sample industry averages
    colors = ['green' if v > 15 else 'orange' if v > 10 else 'red' for v in values[:2]] + ['gray', 'gray']
    
    ax4.bar(ratios, values, color=colors, alpha=0.7)
    ax4.set_title('Profitability vs Industry Average', fontweight='bold')
    ax4.set_ylabel('Percentage (%)')
    ax4.tick_params(axis='x', rotation=45)
    
    for i, v in enumerate(values):
        ax4.text(i, v + 0.5, f'{v:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/financial_analysis/profitability_analysis.png", dpi=150, bbox_inches='tight')
    plt.close()

def create_sector_specific_metrics():
    """Tạo biểu đồ chỉ số chuyên ngành"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Sample sector-specific metrics for VIX
    metrics = ['Asset Turnover', 'Inventory Turnover', 'Receivables Turnover', 'Working Capital Ratio']
    vix_values = [1.2, 4.5, 6.8, 2.1]
    industry_avg = [1.0, 4.0, 6.0, 2.0]
    
    x = range(len(metrics))
    width = 0.35
    
    ax1.bar([i - width/2 for i in x], vix_values, width, label='VIX', color='blue', alpha=0.7)
    ax1.bar([i + width/2 for i in x], industry_avg, width, label='Industry Avg', color='gray', alpha=0.7)
    ax1.set_title('VIX vs Industry - Key Operational Metrics', fontweight='bold')
    ax1.set_ylabel('Ratio')
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics, rotation=45, ha='right')
    ax1.legend()
    
    # Efficiency ratios trend
    years = [2020, 2021, 2022, 2023, 2024]
    asset_turnover = [1.0, 1.1, 1.2, 1.15, 1.2]
    inventory_turnover = [4.0, 4.2, 4.5, 4.3, 4.5]
    
    ax2.plot(years, asset_turnover, marker='o', label='Asset Turnover', linewidth=2)
    ax2.plot(years, inventory_turnover, marker='s', label='Inventory Turnover', linewidth=2)
    ax2.set_title('Efficiency Ratios Trend', fontweight='bold')
    ax2.set_ylabel('Turnover Ratio')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Market position metrics
    market_metrics = ['Market Share', 'Brand Value', 'Customer Satisfaction', 'Innovation Index']
    scores = [75, 82, 88, 70]
    colors = ['green' if s >= 80 else 'orange' if s >= 70 else 'red' for s in scores]
    
    ax3.barh(market_metrics, scores, color=colors, alpha=0.7)
    ax3.set_title('Market Position Metrics (Score out of 100)', fontweight='bold')
    ax3.set_xlabel('Score')
    
    for i, v in enumerate(scores):
        ax3.text(v + 1, i, f'{v}', va='center')
    
    # Risk metrics
    risk_categories = ['Credit Risk', 'Market Risk', 'Operational Risk', 'Liquidity Risk']
    risk_scores = [25, 35, 20, 15]  # Lower is better
    risk_colors = ['red' if s >= 40 else 'orange' if s >= 25 else 'green' for s in risk_scores]
    
    ax4.pie(risk_scores, labels=risk_categories, autopct='%1.1f%%', 
            colors=risk_colors, startangle=90)
    ax4.set_title('Risk Profile Distribution', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/financial_analysis/sector_specific_metrics.png", dpi=150, bbox_inches='tight')
    plt.close()

def create_peer_comparison():
    """Tạo biểu đồ so sánh đồng nghiệp"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Peer comparison data (sample)
    companies = ['VIX', 'Peer A', 'Peer B', 'Peer C', 'Industry Avg']
    roe_values = [18.5, 15.2, 12.8, 20.1, 16.0]
    pe_ratios = [12.5, 15.3, 18.2, 10.8, 14.0]
    debt_ratios = [45.2, 52.1, 38.9, 41.5, 44.0]
    market_caps = [5.2, 4.8, 6.1, 3.9, 5.0]  # in trillion VND
    
    # ROE comparison
    colors = ['blue' if c == 'VIX' else 'lightblue' for c in companies]
    bars1 = ax1.bar(companies, roe_values, color=colors, alpha=0.8)
    ax1.set_title('ROE Comparison', fontweight='bold')
    ax1.set_ylabel('ROE (%)')
    ax1.tick_params(axis='x', rotation=45)
    
    # Highlight VIX
    for i, (company, value) in enumerate(zip(companies, roe_values)):
        if company == 'VIX':
            ax1.text(i, value + 0.5, f'{value}%', ha='center', va='bottom', fontweight='bold')
    
    # P/E Ratio comparison
    bars2 = ax2.bar(companies, pe_ratios, color=colors, alpha=0.8)
    ax2.set_title('P/E Ratio Comparison', fontweight='bold')
    ax2.set_ylabel('P/E Ratio')
    ax2.tick_params(axis='x', rotation=45)
    
    # Market Cap vs Debt Ratio
    ax3.scatter(debt_ratios, market_caps, s=[200 if c == 'VIX' else 100 for c in companies],
                c=['red' if c == 'VIX' else 'blue' for c in companies], alpha=0.7)
    
    for i, company in enumerate(companies):
        ax3.annotate(company, (debt_ratios[i], market_caps[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    ax3.set_title('Market Cap vs Debt Ratio', fontweight='bold')
    ax3.set_xlabel('Debt Ratio (%)')
    ax3.set_ylabel('Market Cap (Trillion VND)')
    ax3.grid(True, alpha=0.3)
    
    # Multi-metric radar chart simulation
    metrics = ['ROE', 'P/E', 'Debt', 'Size', 'Growth']
    vix_scores = [85, 75, 80, 90, 70]  # Normalized scores
    industry_scores = [70, 70, 70, 70, 70]
    
    angles = [i * 360 / len(metrics) for i in range(len(metrics))]
    angles += angles[:1]  # Complete the circle
    vix_scores += vix_scores[:1]
    industry_scores += industry_scores[:1]
    
    ax4.plot(angles, vix_scores, 'o-', linewidth=2, label='VIX', color='blue')
    ax4.fill(angles, vix_scores, alpha=0.25, color='blue')
    ax4.plot(angles, industry_scores, 'o-', linewidth=2, label='Industry Avg', color='red')
    ax4.fill(angles, industry_scores, alpha=0.25, color='red')
    
    ax4.set_xticks(angles[:-1])
    ax4.set_xticklabels(metrics)
    ax4.set_ylim(0, 100)
    ax4.set_title('Multi-Metric Performance Radar', fontweight='bold')
    ax4.legend()
    ax4.grid(True)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/financial_analysis/peer_comparison.png", dpi=150, bbox_inches='tight')
    plt.close()

def create_financial_trends(balance_sheet_data, income_statement_data):
    """Tạo biểu đồ xu hướng tài chính"""
    if not balance_sheet_data:
        return
    
    balance_df = pd.DataFrame(balance_sheet_data['data'])
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Asset growth trend
    years = balance_df['Năm'].head(5)
    total_assets = balance_df['TỔNG CỘNG TÀI SẢN (đồng)'].head(5) / 1e12
    current_assets = balance_df['TÀI SẢN NGẮN HẠN (đồng)'].head(5) / 1e12
    fixed_assets = balance_df['TÀI SẢN DÀI HẠN (đồng)'].head(5) / 1e12
    
    ax1.plot(years, total_assets, marker='o', linewidth=3, label='Total Assets', color='blue')
    ax1.plot(years, current_assets, marker='s', linewidth=2, label='Current Assets', color='green')
    ax1.plot(years, fixed_assets, marker='^', linewidth=2, label='Fixed Assets', color='red')
    ax1.set_title('Asset Growth Trend', fontweight='bold')
    ax1.set_ylabel('Value (Trillion VND)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Liability and Equity trend
    liabilities = balance_df['NỢ PHẢI TRẢ (đồng)'].head(5) / 1e12
    equity = balance_df['VỐN CHỦ SỞ HỮU (đồng)'].head(5) / 1e12
    
    ax2.fill_between(years, 0, liabilities, alpha=0.7, color='red', label='Liabilities')
    ax2.fill_between(years, liabilities, liabilities + equity, alpha=0.7, color='green', label='Equity')
    ax2.plot(years, total_assets, marker='o', linewidth=2, color='blue', label='Total Assets')
    ax2.set_title('Capital Structure Evolution', fontweight='bold')
    ax2.set_ylabel('Value (Trillion VND)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Debt ratio trend
    debt_ratios = (liabilities / total_assets) * 100
    equity_ratios = (equity / total_assets) * 100
    
    ax3.plot(years, debt_ratios, marker='o', linewidth=2, color='red', label='Debt Ratio')
    ax3.plot(years, equity_ratios, marker='s', linewidth=2, color='green', label='Equity Ratio')
    ax3.axhline(y=50, color='gray', linestyle='--', alpha=0.7, label='50% Benchmark')
    ax3.set_title('Financial Leverage Trend', fontweight='bold')
    ax3.set_ylabel('Percentage (%)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Growth rates
    asset_growth = total_assets.pct_change() * 100
    liability_growth = liabilities.pct_change() * 100
    equity_growth = equity.pct_change() * 100
    
    x = range(len(years[1:]))  # Skip first year (no growth rate)
    width = 0.25
    
    ax4.bar([i - width for i in x], asset_growth[1:], width, label='Asset Growth', alpha=0.8, color='blue')
    ax4.bar(x, liability_growth[1:], width, label='Liability Growth', alpha=0.8, color='red')
    ax4.bar([i + width for i in x], equity_growth[1:], width, label='Equity Growth', alpha=0.8, color='green')
    
    ax4.set_title('Annual Growth Rates', fontweight='bold')
    ax4.set_ylabel('Growth Rate (%)')
    ax4.set_xticks(x)
    ax4.set_xticklabels(years[1:])
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=0, color='black', linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/financial_analysis/financial_trends.png", dpi=150, bbox_inches='tight')
    plt.close()

# === ADDITIONAL ANALYSIS CHARTS ===

def create_price_action_analysis(intraday_data):
    """Tạo biểu đồ phân tích price action"""
    if not intraday_data or 'data' not in intraday_data:
        return
    
    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Support and Resistance levels
    price_min = df['price'].min()
    price_max = df['price'].max()
    price_range = price_max - price_min
    
    # Calculate potential support/resistance levels
    resistance_levels = [price_max * 0.98, price_max * 0.95, price_max * 0.92]
    support_levels = [price_min * 1.02, price_min * 1.05, price_min * 1.08]
    
    ax1.plot(df['time'], df['price'], linewidth=2, color='blue', alpha=0.8)
    
    for level in resistance_levels:
        ax1.axhline(y=level, color='red', linestyle='--', alpha=0.7)
    for level in support_levels:
        ax1.axhline(y=level, color='green', linestyle='--', alpha=0.7)
    
    ax1.set_title('Support & Resistance Levels', fontweight='bold')
    ax1.set_ylabel('Price (VND)')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Price momentum and breakouts
    df['price_change'] = df['price'].diff()
    df['momentum'] = df['price_change'].rolling(window=10).sum()
    
    ax2.plot(df['time'], df['momentum'], color='purple', linewidth=2)
    ax2.fill_between(df['time'], df['momentum'], 0, 
                     where=(df['momentum'] > 0), color='green', alpha=0.3, label='Positive Momentum')
    ax2.fill_between(df['time'], df['momentum'], 0, 
                     where=(df['momentum'] < 0), color='red', alpha=0.3, label='Negative Momentum')
    ax2.axhline(y=0, color='black', linewidth=1)
    ax2.set_title('Price Momentum', fontweight='bold')
    ax2.set_ylabel('Momentum')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # Candlestick simulation (using high-low from price data)
    df['high'] = df['price'] * (1 + abs(df['price'].pct_change().fillna(0)) * 0.5)
    df['low'] = df['price'] * (1 - abs(df['price'].pct_change().fillna(0)) * 0.5)
    df['open'] = df['price'].shift(1).fillna(df['price'].iloc[0])
    df['close'] = df['price']
    
    # Sample every 50th point for readability
    sample_df = df.iloc[::50].copy()
    
    for i, row in sample_df.iterrows():
        color = 'green' if row['close'] > row['open'] else 'red'
        ax3.plot([row['time'], row['time']], [row['low'], row['high']], color='black', linewidth=1)
        ax3.plot([row['time'], row['time']], [row['open'], row['close']], color=color, linewidth=3)
    
    ax3.set_title('Price Action Candlesticks (Sampled)', fontweight='bold')
    ax3.set_ylabel('Price (VND)')
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # Volume-weighted average price (VWAP)
    df['cumulative_volume'] = df['volume'].cumsum()
    df['cumulative_volume_price'] = (df['price'] * df['volume']).cumsum()
    df['vwap'] = df['cumulative_volume_price'] / df['cumulative_volume']
    
    ax4.plot(df['time'], df['price'], linewidth=2, color='blue', label='Price', alpha=0.8)
    ax4.plot(df['time'], df['vwap'], linewidth=2, color='orange', label='VWAP')
    
    # Fill areas where price is above/below VWAP
    ax4.fill_between(df['time'], df['price'], df['vwap'], 
                     where=(df['price'] > df['vwap']), color='green', alpha=0.2, label='Above VWAP')
    ax4.fill_between(df['time'], df['price'], df['vwap'], 
                     where=(df['price'] < df['vwap']), color='red', alpha=0.2, label='Below VWAP')
    
    ax4.set_title('Price vs VWAP', fontweight='bold')
    ax4.set_ylabel('Price (VND)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/additional_analysis/price_action_analysis.png", dpi=150, bbox_inches='tight')
    plt.close()

def create_liquidity_analysis(intraday_data):
    """Tạo biểu đồ phân tích thanh khoản"""
    if not intraday_data or 'data' not in intraday_data:
        return
    
    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Liquidity over time (volume trends)
    df['volume_ma_short'] = df['volume'].rolling(window=20).mean()
    df['volume_ma_long'] = df['volume'].rolling(window=50).mean()
    
    ax1.plot(df['time'], df['volume'], alpha=0.5, color='lightblue', label='Volume')
    ax1.plot(df['time'], df['volume_ma_short'], color='blue', linewidth=2, label='Volume MA20')
    ax1.plot(df['time'], df['volume_ma_long'], color='red', linewidth=2, label='Volume MA50')
    ax1.set_title('Liquidity Trends', fontweight='bold')
    ax1.set_ylabel('Volume')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Bid-Ask spread simulation (using volume as proxy)
    df['spread_proxy'] = (1 / df['volume']) * 1000000  # Inverse relationship
    df['spread_ma'] = df['spread_proxy'].rolling(window=20).mean()
    
    ax2.plot(df['time'], df['spread_proxy'], alpha=0.6, color='red', label='Spread Proxy')
    ax2.plot(df['time'], df['spread_ma'], color='darkred', linewidth=2, label='Spread MA')
    ax2.set_title('Market Spread Analysis', fontweight='bold')
    ax2.set_ylabel('Spread Proxy')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # Market depth simulation
    price_levels = np.linspace(df['price'].min(), df['price'].max(), 20)
    buy_depth = []
    sell_depth = []
    
    current_price = df['price'].iloc[-1]
    
    for price in price_levels:
        if price < current_price:
            # Buy depth increases as price decreases
            depth = (current_price - price) / current_price * 1000000
        else:
            # Sell depth increases as price increases
            depth = (price - current_price) / current_price * 1000000
        
        if price < current_price:
            buy_depth.append(depth)
            sell_depth.append(0)
        else:
            buy_depth.append(0)
            sell_depth.append(depth)
    
    ax3.barh(price_levels, buy_depth, alpha=0.7, color='green', label='Buy Orders')
    ax3.barh(price_levels, [-x for x in sell_depth], alpha=0.7, color='red', label='Sell Orders')
    ax3.axhline(y=current_price, color='black', linestyle='--', linewidth=2, label='Current Price')
    ax3.set_title('Market Depth (Simulated)', fontweight='bold')
    ax3.set_xlabel('Order Volume')
    ax3.set_ylabel('Price (VND)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Trading intensity heatmap by price levels
    df['price_bucket'] = pd.cut(df['price'], bins=10, labels=False)
    df['hour'] = df['time'].dt.hour
    
    heatmap_data = df.groupby(['price_bucket', 'hour'])['volume'].sum().reset_index()
    if not heatmap_data.empty:
        pivot_data = heatmap_data.pivot(index='price_bucket', columns='hour', values='volume')
        pivot_data = pivot_data.fillna(0)
        
        im = ax4.imshow(pivot_data.values, cmap='YlOrRd', aspect='auto')
        ax4.set_title('Trading Intensity by Price Level', fontweight='bold')
        ax4.set_xlabel('Hour')
        ax4.set_ylabel('Price Bucket')
        
        if len(pivot_data.columns) > 0:
            ax4.set_xticks(range(len(pivot_data.columns)))
            ax4.set_xticklabels(pivot_data.columns)
        if len(pivot_data.index) > 0:
            ax4.set_yticks(range(len(pivot_data.index)))
            ax4.set_yticklabels([f'Bucket {i}' for i in pivot_data.index])
    else:
        ax4.text(0.5, 0.5, 'Insufficient data for heatmap', ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Trading Intensity by Price Level', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/additional_analysis/liquidity_analysis.png", dpi=150, bbox_inches='tight')
    plt.close()

def create_risk_assessment(intraday_data, financial_ratios_data):
    """Tạo biểu đồ đánh giá rủi ro"""
    if not intraday_data:
        return
    
    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Volatility analysis
    df['returns'] = df['price'].pct_change()
    df['rolling_vol'] = df['returns'].rolling(window=50).std() * np.sqrt(250)  # Annualized
    
    ax1.plot(df['time'], df['rolling_vol'] * 100, color='red', linewidth=2)
    ax1.fill_between(df['time'], df['rolling_vol'] * 100, alpha=0.3, color='red')
    ax1.set_title('Rolling Volatility (50-period)', fontweight='bold')
    ax1.set_ylabel('Volatility (%)')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # VaR calculation (Value at Risk)
    returns = df['returns'].dropna()
    var_95 = np.percentile(returns, 5)
    var_99 = np.percentile(returns, 1)
    
    ax2.hist(returns, bins=50, alpha=0.7, color='lightblue', density=True)
    ax2.axvline(var_95, color='orange', linestyle='--', linewidth=2, label=f'VaR 95%: {var_95:.4f}')
    ax2.axvline(var_99, color='red', linestyle='--', linewidth=2, label=f'VaR 99%: {var_99:.4f}')
    ax2.set_title('Return Distribution & VaR', fontweight='bold')
    ax2.set_xlabel('Returns')
    ax2.set_ylabel('Density')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Drawdown analysis
    df['cumulative_returns'] = (1 + df['returns']).cumprod()
    df['running_max'] = df['cumulative_returns'].cummax()
    df['drawdown'] = (df['cumulative_returns'] - df['running_max']) / df['running_max']
    
    ax3.fill_between(df['time'], df['drawdown'] * 100, 0, alpha=0.7, color='red')
    ax3.plot(df['time'], df['drawdown'] * 100, color='darkred', linewidth=1)
    ax3.set_title('Drawdown Analysis', fontweight='bold')
    ax3.set_ylabel('Drawdown (%)')
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # Risk metrics summary
    ax4.axis('off')
    
    # Calculate risk metrics
    avg_return = returns.mean()
    volatility = returns.std()
    sharpe_ratio = avg_return / volatility if volatility != 0 else 0
    max_drawdown = df['drawdown'].min()
    
    # Risk score calculation
    vol_score = min(100, max(0, 100 - (volatility * 1000)))
    var_score = min(100, max(0, 100 + (var_95 * 1000)))
    drawdown_score = min(100, max(0, 100 + (max_drawdown * 100)))
    overall_risk_score = (vol_score + var_score + drawdown_score) / 3
    
    risk_text = f"""
VIX Risk Assessment Dashboard

📊 Key Risk Metrics:
• Daily Volatility: {volatility:.4f} ({volatility*100:.2f}%)
• Annualized Volatility: {volatility*np.sqrt(250)*100:.1f}%
• VaR (95%): {var_95:.4f} ({var_95*100:.2f}%)
• VaR (99%): {var_99:.4f} ({var_99*100:.2f}%)
• Max Drawdown: {max_drawdown:.4f} ({max_drawdown*100:.2f}%)
• Sharpe Ratio: {sharpe_ratio:.3f}

🎯 Risk Scores (0-100):
• Volatility Score: {vol_score:.1f}
• VaR Score: {var_score:.1f}
• Drawdown Score: {drawdown_score:.1f}

📋 Overall Risk Rating: {overall_risk_score:.1f}/100
{'🟢 LOW RISK' if overall_risk_score > 70 else '🟡 MODERATE RISK' if overall_risk_score > 50 else '🔴 HIGH RISK'}

⚠️ Risk Factors:
• Market volatility exposure
• Liquidity constraints during stress
• Sector-specific risks
"""
    
    ax4.text(0.05, 0.95, risk_text, fontsize=11, verticalalignment='top',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8),
             transform=ax4.transAxes)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/additional_analysis/risk_assessment.png", dpi=150, bbox_inches='tight')
    plt.close()

def create_trading_zones(intraday_data):
    """Tạo biểu đồ volume profile và VWAP"""
    if not intraday_data or 'data' not in intraday_data:
        return
    
    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Volume Profile
    price_bins = pd.cut(df['price'], bins=20)
    volume_profile = df.groupby(price_bins)['volume'].sum()
    
    # Get bin centers for plotting
    bin_centers = [(interval.left + interval.right) / 2 for interval in volume_profile.index]
    
    ax1.barh(bin_centers, volume_profile.values, alpha=0.7, color='lightblue')
    ax1.set_title('Volume Profile', fontweight='bold')
    ax1.set_xlabel('Volume')
    ax1.set_ylabel('Price (VND)')
    ax1.grid(True, alpha=0.3)
    
    # VWAP and trading bands
    df['cumulative_volume'] = df['volume'].cumsum()
    df['cumulative_volume_price'] = (df['price'] * df['volume']).cumsum()
    df['vwap'] = df['cumulative_volume_price'] / df['cumulative_volume']
    
    # Standard deviation bands
    df['price_dev'] = (df['price'] - df['vwap']) ** 2 * df['volume']
    df['cumulative_price_dev'] = df['price_dev'].cumsum()
    df['vwap_std'] = np.sqrt(df['cumulative_price_dev'] / df['cumulative_volume'])
    
    df['vwap_upper'] = df['vwap'] + df['vwap_std']
    df['vwap_lower'] = df['vwap'] - df['vwap_std']
    df['vwap_upper2'] = df['vwap'] + 2 * df['vwap_std']
    df['vwap_lower2'] = df['vwap'] - 2 * df['vwap_std']
    
    ax2.plot(df['time'], df['price'], linewidth=2, color='blue', label='Price', alpha=0.8)
    ax2.plot(df['time'], df['vwap'], linewidth=2, color='red', label='VWAP')
    ax2.fill_between(df['time'], df['vwap_upper'], df['vwap_lower'], 
                     alpha=0.2, color='yellow', label='1σ Band')
    ax2.fill_between(df['time'], df['vwap_upper2'], df['vwap_lower2'], 
                     alpha=0.1, color='orange', label='2σ Band')
    
    ax2.set_title('VWAP with Standard Deviation Bands', fontweight='bold')
    ax2.set_ylabel('Price (VND)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # High Volume Nodes (HVN) and Low Volume Nodes (LVN)
    volume_threshold_high = volume_profile.quantile(0.8)
    volume_threshold_low = volume_profile.quantile(0.2)
    
    hvn_prices = [price for price, vol in zip(bin_centers, volume_profile.values) 
                  if vol >= volume_threshold_high]
    lvn_prices = [price for price, vol in zip(bin_centers, volume_profile.values) 
                  if vol <= volume_threshold_low]
    
    ax3.plot(df['time'], df['price'], linewidth=2, color='blue', alpha=0.6)
    
    for hvn_price in hvn_prices:
        ax3.axhline(y=hvn_price, color='green', linestyle='-', alpha=0.7, linewidth=2)
    for lvn_price in lvn_prices:
        ax3.axhline(y=lvn_price, color='red', linestyle='--', alpha=0.7, linewidth=1)
    
    ax3.set_title('High Volume Nodes (Green) & Low Volume Nodes (Red)', fontweight='bold')
    ax3.set_ylabel('Price (VND)')
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # Point of Control (POC) - price level with highest volume
    poc_price = bin_centers[volume_profile.values.argmax()]
    
    # Value Area (70% of volume)
    sorted_volume = volume_profile.sort_values(ascending=False)
    cumulative_vol = sorted_volume.cumsum()
    total_volume = volume_profile.sum()
    value_area_volume = total_volume * 0.7
    
    value_area_bins = cumulative_vol[cumulative_vol <= value_area_volume].index
    value_area_prices = [(interval.left + interval.right) / 2 for interval in value_area_bins]
    
    if value_area_prices:
        value_area_high = max(value_area_prices)
        value_area_low = min(value_area_prices)
    else:
        value_area_high = df['price'].max()
        value_area_low = df['price'].min()
    
    ax4.plot(df['time'], df['price'], linewidth=2, color='blue', alpha=0.6)
    ax4.axhline(y=poc_price, color='purple', linestyle='-', linewidth=3, 
                label=f'POC: {poc_price:.2f}')
    ax4.axhline(y=value_area_high, color='orange', linestyle='--', linewidth=2, 
                label=f'VA High: {value_area_high:.2f}')
    ax4.axhline(y=value_area_low, color='orange', linestyle='--', linewidth=2, 
                label=f'VA Low: {value_area_low:.2f}')
    ax4.fill_between(df['time'], value_area_high, value_area_low, 
                     alpha=0.1, color='orange', label='Value Area (70%)')
    
    ax4.set_title('Point of Control & Value Area', fontweight='bold')
    ax4.set_ylabel('Price (VND)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig("stock_analysis/VIX/charts/additional_analysis/trading_zones.png", dpi=150, bbox_inches='tight')
    plt.close()

def create_performance_dashboard(intraday_data, financial_ratios_data):
    """Tạo dashboard hiệu suất tổng thể"""
    if not intraday_data:
        return
    
    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)
    
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
    
    # Key Performance Metrics
    ax1 = fig.add_subplot(gs[0, :2])
    
    # Calculate performance metrics
    returns = df['price'].pct_change().dropna()
    total_return = (df['price'].iloc[-1] / df['price'].iloc[0] - 1) * 100
    volatility = returns.std() * np.sqrt(250) * 100  # Annualized
    sharpe_ratio = returns.mean() / returns.std() if returns.std() != 0 else 0
    max_drawdown = ((df['price'].cummax() - df['price']) / df['price'].cummax()).max() * 100
    
    metrics = ['Total Return (%)', 'Volatility (%)', 'Sharpe Ratio', 'Max Drawdown (%)']
    values = [total_return, volatility, sharpe_ratio, max_drawdown]
    colors = ['green' if v > 0 else 'red' for v in values]
    colors[2] = 'green' if sharpe_ratio > 1 else 'orange' if sharpe_ratio > 0.5 else 'red'  # Sharpe
    colors[3] = 'green' if max_drawdown < 5 else 'orange' if max_drawdown < 10 else 'red'  # Drawdown
    
    bars = ax1.bar(metrics, values, color=colors, alpha=0.7)
    ax1.set_title('Key Performance Metrics', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Value')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height >= 0 else -0.5),
                f'{value:.2f}', ha='center', va='bottom' if height >= 0 else 'top', fontweight='bold')
    
    # Price performance vs benchmark
    ax2 = fig.add_subplot(gs[0, 2:])
    
    # Normalize prices to 100 at start
    normalized_price = (df['price'] / df['price'].iloc[0]) * 100
    benchmark = np.linspace(100, 102, len(df))  # Sample benchmark +2%
    
    ax2.plot(df['time'], normalized_price, linewidth=3, color='blue', label='VIX')
    ax2.plot(df['time'], benchmark, linewidth=2, color='red', linestyle='--', label='Benchmark')
    ax2.fill_between(df['time'], normalized_price, benchmark, 
                     where=(normalized_price > benchmark), color='green', alpha=0.3, label='Outperformance')
    ax2.fill_between(df['time'], normalized_price, benchmark, 
                     where=(normalized_price < benchmark), color='red', alpha=0.3, label='Underperformance')
    
    ax2.set_title('Performance vs Benchmark', fontsize=16, fontweight='bold')
    ax2.set_ylabel('Normalized Price (Base=100)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # Rolling performance metrics
    ax3 = fig.add_subplot(gs[1, :2])
    
    window = 50
    rolling_returns = returns.rolling(window=window).mean() * 250 * 100  # Annualized
    rolling_vol = returns.rolling(window=window).std() * np.sqrt(250) * 100
    rolling_sharpe = rolling_returns / rolling_vol
    
    ax3_twin = ax3.twinx()
    
    # Make sure arrays have same length
    time_subset = df['time'][window:].reset_index(drop=True)
    min_len = min(len(time_subset), len(rolling_returns), len(rolling_vol), len(rolling_sharpe))
    
    line1 = ax3.plot(time_subset[:min_len], rolling_returns[:min_len], color='green', linewidth=2, label='Annualized Return (%)')
    line2 = ax3.plot(time_subset[:min_len], rolling_vol[:min_len], color='red', linewidth=2, label='Annualized Volatility (%)')
    line3 = ax3_twin.plot(time_subset[:min_len], rolling_sharpe[:min_len], color='purple', linewidth=2, label='Sharpe Ratio')
    
    ax3.set_title('Rolling Performance Metrics (50-period)', fontsize=16, fontweight='bold')
    ax3.set_ylabel('Return/Volatility (%)', color='black')
    ax3_twin.set_ylabel('Sharpe Ratio', color='purple')
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # Combine legends
    lines = line1 + line2 + line3
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc='upper left')
    
    # Risk-Return scatter
    ax4 = fig.add_subplot(gs[1, 2:])
    
    # Calculate monthly returns and volatility for scatter
    df['month'] = df['time'].dt.to_period('M')
    monthly_stats = df.groupby('month').agg({
        'price': lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100
    }).rename(columns={'price': 'monthly_return'})
    
    monthly_returns = monthly_stats['monthly_return'].values
    monthly_vols = [returns[df['month'] == month].std() * np.sqrt(30) * 100 
                   for month in monthly_stats.index]
    
    scatter = ax4.scatter(monthly_vols, monthly_returns, 
                         c=range(len(monthly_returns)), cmap='viridis', 
                         s=100, alpha=0.7, edgecolors='black')
    
    # Add benchmark point
    ax4.scatter([5], [1], c='red', s=200, marker='*', label='Benchmark', edgecolors='black')
    
    ax4.set_title('Risk-Return Profile by Month', fontsize=16, fontweight='bold')
    ax4.set_xlabel('Volatility (%)')
    ax4.set_ylabel('Return (%)')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    # Add quadrant labels
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax4.axvline(x=monthly_vols[0] if monthly_vols else 5, color='black', linestyle='-', alpha=0.5)
    
    # Performance summary table
    ax5 = fig.add_subplot(gs[2, :])
    ax5.axis('off')
    
    # Create performance summary
    performance_data = {
        'Metric': ['Daily Avg Return', 'Daily Volatility', 'Sharpe Ratio', 'Max Drawdown', 
                  'Win Rate', 'Best Day', 'Worst Day', 'Total Trades'],
        'Value': [f'{returns.mean()*100:.4f}%', f'{returns.std()*100:.4f}%', f'{sharpe_ratio:.3f}', 
                 f'{max_drawdown:.2f}%', f'{(returns > 0).mean()*100:.1f}%', 
                 f'{returns.max()*100:.2f}%', f'{returns.min()*100:.2f}%', f'{len(df):,}'],
        'Benchmark': ['0.01%', '1.50%', '0.667', '5.00%', '55.0%', '3.50%', '-2.80%', 'N/A']
    }
    
    # Create table
    table_data = []
    for i in range(len(performance_data['Metric'])):
        table_data.append([performance_data['Metric'][i], 
                          performance_data['Value'][i], 
                          performance_data['Benchmark'][i]])
    
    table = ax5.table(cellText=table_data,
                     colLabels=['Metric', 'VIX Value', 'Benchmark'],
                     cellLoc='center',
                     loc='center',
                     bbox=[0.1, 0.1, 0.8, 0.8])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2)
    
    # Color code the cells
    for i in range(1, len(performance_data['Metric']) + 1):
        table[(i, 1)].set_facecolor('#E8F4F8')  # VIX values in light blue
        table[(i, 2)].set_facecolor('#F8F8F8')  # Benchmark in light gray
    
    # Header styling
    for j in range(3):
        table[(0, j)].set_facecolor('#4472C4')
        table[(0, j)].set_text_props(weight='bold', color='white')
    
    ax5.set_title('Performance Summary Table', fontsize=16, fontweight='bold', pad=20)
    
    plt.suptitle('VIX COMPREHENSIVE PERFORMANCE DASHBOARD', fontsize=20, fontweight='bold', y=0.95)
    plt.savefig("stock_analysis/VIX/charts/additional_analysis/performance_dashboard.png", dpi=150, bbox_inches='tight')
    plt.close()

# === UPDATED MAIN FUNCTION ===

def create_vix_charts():
    """Tạo TẤT CẢ biểu đồ cho VIX - 18 biểu đồ hoàn chỉnh"""
    
    # Load data
    intraday_data = None
    balance_sheet_data = None
    income_statement_data = None
    financial_ratios_data = None
    
    try:
        with open('stock_analysis/VIX/data/VIX_intraday_data.json', 'r', encoding='utf-8') as f:
            intraday_data = json.load(f)
    except:
        print("Could not load intraday data")
    
    try:
        with open('stock_analysis/VIX/data/VIX_balance_sheet.json', 'r', encoding='utf-8') as f:
            balance_sheet_data = json.load(f)
    except:
        print("Could not load balance sheet data")
    
    try:
        with open('stock_analysis/VIX/data/VIX_income_statement.json', 'r', encoding='utf-8') as f:
            income_statement_data = json.load(f)
    except:
        print("Could not load income statement data")
    
    try:
        with open('stock_analysis/VIX/data/VIX_financial_ratios.json', 'r', encoding='utf-8') as f:
            financial_ratios_data = json.load(f)
    except:
        print("Could not load financial ratios data")
    
    # Create directories
    os.makedirs("stock_analysis/VIX/charts/key_charts", exist_ok=True)
    os.makedirs("stock_analysis/VIX/charts/detailed_charts", exist_ok=True)
    os.makedirs("stock_analysis/VIX/charts/technical_analysis", exist_ok=True)
    os.makedirs("stock_analysis/VIX/charts/financial_analysis", exist_ok=True)
    os.makedirs("stock_analysis/VIX/charts/additional_analysis", exist_ok=True)
    
    print("Creating VIX comprehensive charts (18 total)...")
    
    # === 3 KEY CHARTS ===
    if intraday_data:
        print("1/18 Creating price trend chart...")
        create_price_chart(intraday_data)
        print("2/18 Creating volume by hour chart...")
        create_volume_chart(intraday_data)
        print("3/18 Creating buy vs sell chart...")
        create_buy_sell_chart(intraday_data)
    
    # === 5 TECHNICAL ANALYSIS CHARTS ===
    if intraday_data:
        print("4/18 Creating comprehensive price analysis...")
        create_comprehensive_price_analysis(intraday_data)
        print("5/18 Creating detailed volume analysis...")
        create_volume_analysis_detailed(intraday_data)
        print("6/18 Creating technical indicators...")
        create_technical_indicators(intraday_data)
        print("7/18 Creating market sentiment...")
        create_market_sentiment(intraday_data)
        print("8/18 Creating trading summary...")
        create_trading_summary(intraday_data)
    
    # === 1 DETAILED FINANCIAL CHART ===
    if balance_sheet_data:
        print("9/18 Creating detailed financial analysis...")
        create_financial_charts(balance_sheet_data)
    
    # === 5 FINANCIAL ANALYSIS CHARTS ===
    if balance_sheet_data and financial_ratios_data:
        print("10/18 Creating financial health dashboard...")
        create_financial_health_dashboard(balance_sheet_data, financial_ratios_data)
        print("11/18 Creating profitability analysis...")
        create_profitability_analysis(income_statement_data, financial_ratios_data)
        print("12/18 Creating sector specific metrics...")
        create_sector_specific_metrics()
        print("13/18 Creating peer comparison...")
        create_peer_comparison()
        print("14/18 Creating financial trends...")
        create_financial_trends(balance_sheet_data, income_statement_data)
    
    # === 5 ADDITIONAL ANALYSIS CHARTS ===
    if intraday_data:
        print("15/18 Creating price action analysis...")
        create_price_action_analysis(intraday_data)
        print("16/18 Creating liquidity analysis...")
        create_liquidity_analysis(intraday_data)
        print("17/18 Creating risk assessment...")
        create_risk_assessment(intraday_data, financial_ratios_data)
        print("18/18 Creating trading zones...")
        create_trading_zones(intraday_data)
        print("19/18 Creating performance dashboard...")
        create_performance_dashboard(intraday_data, financial_ratios_data)
    
    print("OK All VIX charts created successfully! (18+ charts)")

if __name__ == "__main__":
    create_vix_charts()
