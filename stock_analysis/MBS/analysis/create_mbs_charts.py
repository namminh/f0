import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import matplotlib.font_manager as fm

# Thiết lập font cho tiếng Việt
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def create_mbs_charts():
    """Tạo biểu đồ phân tích cho MBS."""
    # Create directories
    Path("stock_analysis/MBS/charts/key_charts").mkdir(parents=True, exist_ok=True)
    Path("stock_analysis/MBS/charts/detailed_charts").mkdir(parents=True, exist_ok=True)

    # Load data
    try:
        with open("stock_analysis/MBS/data/MBS_balance_sheet.json", "r", encoding="utf-8") as f:
            balance_sheet_data = json.load(f)
    except FileNotFoundError:
        balance_sheet_data = None
        
    try:
        with open("stock_analysis/MBS/data/MBS_intraday_data.json", "r", encoding="utf-8") as f:
            intraday_data = json.load(f)
    except FileNotFoundError:
        intraday_data = None
        
    try:
        with open("stock_analysis/MBS/data/MBS_income_statement.json", "r", encoding="utf-8") as f:
            income_statement_data = json.load(f)
    except FileNotFoundError:
        income_statement_data = None
        
    try:
        with open("stock_analysis/MBS/data/MBS_financial_ratios.json", "r", encoding="utf-8") as f:
            financial_ratios_data = json.load(f)
    except FileNotFoundError:
        financial_ratios_data = None

    # Create charts
    if intraday_data:
        create_price_chart(intraday_data)
        create_volume_chart(intraday_data)
        create_buy_sell_chart(intraday_data)
    
    if financial_ratios_data:
        create_financial_charts(financial_ratios_data)
    
    print("Charts created for MBS")

def create_price_chart(intraday_data):
    """Tạo biểu đồ giá trong ngày."""
    if not intraday_data or 'data' not in intraday_data:
        return
        
    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['time'], df['price'], linewidth=1.5, color='#1f77b4')
    plt.title('MBS - Gia trong ngay', fontsize=16, fontweight='bold')
    plt.xlabel('Thoi gian')
    plt.ylabel('Gia (VND)')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/key_charts/price_trend.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_volume_chart(intraday_data):
    """Tạo biểu đồ khối lượng theo giờ."""
    if not intraday_data or 'data' not in intraday_data:
        return
        
    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df['hour'] = df['time'].dt.hour
    
    volume_by_hour = df.groupby('hour')['volume'].sum()
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(volume_by_hour.index, volume_by_hour.values, color='#ff7f0e', alpha=0.8)
    plt.title('MBS - Khoi luong giao dich theo gio', fontsize=16, fontweight='bold')
    plt.xlabel('Gio')
    plt.ylabel('Khoi luong')
    plt.grid(True, axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height/1000)}K', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/key_charts/volume_by_hour.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_buy_sell_chart(intraday_data):
    """Tạo biểu đồ tỷ lệ mua/bán."""
    if not intraday_data or 'data' not in intraday_data:
        return
        
    df = pd.DataFrame(intraday_data['data'])
    
    buy_volume = df[df['match_type'] == 'Buy']['volume'].sum()
    sell_volume = df[df['match_type'] == 'Sell']['volume'].sum()
    
    plt.figure(figsize=(8, 8))
    sizes = [buy_volume, sell_volume]
    labels = ['Mua', 'Ban']
    colors = ['#2ca02c', '#d62728']
    
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title('MBS - Ty le Mua/Ban', fontsize=16, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/key_charts/buy_vs_sell.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_financial_charts(financial_ratios_data):
    """Tạo biểu đồ tài chính."""
    if not financial_ratios_data or 'data' not in financial_ratios_data:
        return
        
    df = pd.DataFrame(financial_ratios_data['data'])
    
    # Lấy dữ liệu năm gần nhất (giả sử index 0 là mới nhất)
    if len(df) > 0:
        latest_data = df.iloc[0]
        
        # Tạo biểu đồ các chỉ số tài chính chính
        plt.figure(figsize=(12, 8))
        
        # Chọn một số chỉ số quan trọng
        key_ratios = ['Chỉ tiêu định giá_P/E', 'Chỉ tiêu định giá_P/B', 
                     'Chỉ tiêu hiệu quả_ROE (%)', 'Chỉ tiêu hiệu quả_ROA (%)']
        
        values = []
        labels = []
        
        for ratio in key_ratios:
            if ratio in latest_data and pd.notna(latest_data[ratio]):
                values.append(float(latest_data[ratio]))
                labels.append(ratio.split('_')[-1])
        
        if values:
            plt.subplot(2, 2, 1)
            plt.bar(labels, values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
            plt.title('MBS - Chi so tai chinh chinh')
            plt.xticks(rotation=45)
            plt.grid(True, axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('stock_analysis/MBS/charts/detailed_charts/financial_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    create_mbs_charts()