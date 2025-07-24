import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def create_gex_charts():
    """Tạo biểu đồ phân tích cho GEX."""
    # Create directories
    Path("stock_analysis/GEX/charts/key_charts").mkdir(parents=True, exist_ok=True)
    Path("stock_analysis/GEX/charts/detailed_charts").mkdir(parents=True, exist_ok=True)

    # Load data
    try:
        with open("stock_analysis/GEX/data/GEX_balance_sheet.json", "r", encoding="utf-8") as f:
            balance_sheet_data = json.load(f)
    except FileNotFoundError:
        balance_sheet_data = None
        
    try:
        with open("stock_analysis/GEX/data/GEX_intraday_data.json", "r", encoding="utf-8") as f:
            intraday_data = json.load(f)
    except FileNotFoundError:
        intraday_data = None
        
    try:
        with open("stock_analysis/GEX/data/GEX_income_statement.json", "r", encoding="utf-8") as f:
            income_statement_data = json.load(f)
    except FileNotFoundError:
        income_statement_data = None
        
    try:
        with open("stock_analysis/GEX/data/GEX_financial_ratios.json", "r", encoding="utf-8") as f:
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
    
    print("Charts created for GEX")

def create_price_chart(intraday_data):
    """Tạo biểu đồ giá trong ngày."""
    if not intraday_data or 'data' not in intraday_data or not intraday_data['data']:
        return

    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time')

    plt.figure(figsize=(12, 6))
    plt.plot(df['time'], df['price'], label='Giá')
    plt.title('Biểu đồ giá trong ngày của GEX')
    plt.xlabel('Thời gian')
    plt.ylabel('Giá')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("stock_analysis/GEX/charts/key_charts/price_trend.png")
    plt.close()

def create_volume_chart(intraday_data):
    """Tạo biểu đồ khối lượng giao dịch."""
    if not intraday_data or 'data' not in intraday_data or not intraday_data['data']:
        return

    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df['hour'] = df['time'].dt.hour
    volume_by_hour = df.groupby('hour')['volume'].sum()

    plt.figure(figsize=(12, 6))
    volume_by_hour.plot(kind='bar', title='Khối lượng giao dịch theo giờ - GEX')
    plt.xlabel('Giờ')
    plt.ylabel('Khối lượng')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("stock_analysis/GEX/charts/key_charts/volume_by_hour.png")
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
    plt.title('Tỷ lệ khối lượng Mua vs. Bán - GEX')
    plt.savefig("stock_analysis/GEX/charts/key_charts/buy_vs_sell.png")
    plt.close()

def create_financial_charts(balance_sheet_data):
    """Tạo biểu đồ tài chính cơ bản cho GEX."""
    if not balance_sheet_data or 'data' not in balance_sheet_data:
        print("GEX: No financial data available for chart creation")
        return
    
    # Create simple financial overview chart
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.text(0.5, 0.5, f'GEX - Financial Data Available\n{len(balance_sheet_data["data"])} periods of data', 
            ha='center', va='center', fontsize=14, 
            bbox=dict(boxstyle="round", facecolor='lightgreen', alpha=0.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('GEX - Financial Overview', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig("stock_analysis/GEX/charts/detailed_charts/financial_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("GEX: Basic financial chart created")

if __name__ == "__main__":
    create_gex_charts()
