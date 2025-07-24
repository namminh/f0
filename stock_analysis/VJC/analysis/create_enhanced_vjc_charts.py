import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def create_enhanced_vjc_charts():
    """Tạo biểu đồ phân tích nâng cao cho VJC."""
    # Create directories
    Path("stock_analysis/VJC/charts/detailed_charts").mkdir(parents=True, exist_ok=True)

    # Load data
    try:
        with open("stock_analysis/VJC/data/VJC_intraday_data.json", "r", encoding="utf-8") as f:
            intraday_data = json.load(f)
    except FileNotFoundError:
        intraday_data = None

    # Create charts
    if intraday_data:
        create_candlestick_chart(intraday_data)
        create_moving_average_chart(intraday_data)
    
    print("Enhanced charts created for VJC")

def create_candlestick_chart(intraday_data):
    """Tạo biểu đồ nến."""
    if not intraday_data or 'data' not in intraday_data or not intraday_data['data']:
        return

    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time')
    
    # Resample to 15-minute intervals
    ohlc = df['price'].resample('15Min').ohlc()

    if ohlc.empty:
        return

    plt.figure(figsize=(15, 7))
    # Đây là một cách đơn giản hóa, thư viện mplfinance sẽ tốt hơn
    plt.plot(ohlc.index, ohlc['close'], label='Close')
    plt.title('Biểu đồ nến (giản lược) - VJC')
    plt.xlabel('Thời gian')
    plt.ylabel('Giá')
    plt.legend()
    plt.grid(True)
    plt.savefig("stock_analysis/VJC/charts/detailed_charts/candlestick.png")
    plt.close()

def create_moving_average_chart(intraday_data):
    """Tạo biểu đồ đường trung bình động."""
    if not intraday_data or 'data' not in intraday_data or not intraday_data['data']:
        return

    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time')

    df['MA20'] = df['price'].rolling(window=20).mean()
    df['MA50'] = df['price'].rolling(window=50).mean()

    plt.figure(figsize=(12, 6))
    plt.plot(df['time'], df['price'], label='Giá')
    plt.plot(df['time'], df['MA20'], label='MA20')
    plt.plot(df['time'], df['MA50'], label='MA50')
    plt.title('Đường trung bình động - VJC')
    plt.xlabel('Thời gian')
    plt.ylabel('Giá')
    plt.legend()
    plt.grid(True)
    plt.savefig("stock_analysis/VJC/charts/detailed_charts/moving_averages.png")
    plt.close()

if __name__ == "__main__":
    create_enhanced_vjc_charts()
