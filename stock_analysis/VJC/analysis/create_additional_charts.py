import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def create_additional_charts():
    """Tạo các biểu đồ bổ sung cho VJC."""
    Path("stock_analysis/VJC/charts/additional_analysis").mkdir(parents=True, exist_ok=True)

    try:
        with open("stock_analysis/VJC/data/VJC_intraday_data.json", "r", encoding="utf-8") as f:
            intraday_data = json.load(f)
    except FileNotFoundError:
        intraday_data = None

    if intraday_data:
        create_volatility_chart(intraday_data)

    print("Additional charts created for VJC")

def create_volatility_chart(intraday_data):
    """Tạo biểu đồ biến động."""
    if not intraday_data or 'data' not in intraday_data or not intraday_data['data']:
        return

    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time')

    # Calculate rolling volatility
    rolling_std = df['price'].rolling(window=20).std()

    plt.figure(figsize=(12, 6))
    plt.plot(rolling_std.index, rolling_std, label='Biến động 20-phiên')
    plt.title('Biến động giá - VJC')
    plt.xlabel('Thời gian')
    plt.ylabel('Độ lệch chuẩn giá')
    plt.legend()
    plt.grid(True)
    plt.savefig("stock_analysis/VJC/charts/additional_analysis/volatility.png")
    plt.close()

if __name__ == "__main__":
    create_additional_charts()
