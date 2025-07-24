import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def create_historical_charts():
    """Tạo biểu đồ lịch sử cho VJC."""
    Path("stock_analysis/VJC/charts/historical_analysis").mkdir(parents=True, exist_ok=True)

    try:
        with open("stock_analysis/VJC/data/VJC_historical_3years.json", "r", encoding="utf-8") as f:
            historical_data = json.load(f)
    except FileNotFoundError:
        historical_data = None

    if historical_data:
        create_historical_price_chart(historical_data)

    print("Historical charts created for VJC")

def create_historical_price_chart(historical_data):
    """Tạo biểu đồ giá lịch sử."""
    if not historical_data or 'data' not in historical_data or not historical_data['data']:
        return

    df = pd.DataFrame(historical_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time')

    plt.figure(figsize=(12, 6))
    plt.plot(df['time'], df['Close'], label='Giá đóng cửa')
    plt.title('Biểu đồ giá lịch sử (3 năm) - VJC')
    plt.xlabel('Thời gian')
    plt.ylabel('Giá')
    plt.legend()
    plt.grid(True)
    plt.savefig("stock_analysis/VJC/charts/historical_analysis/historical_price.png")
    plt.close()

if __name__ == "__main__":
    create_historical_charts()
