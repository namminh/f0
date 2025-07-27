import json
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from stock_data_collector import StockDataCollector

def get_historical_data(symbol: str, years: int = 3):
    """
    Lấy dữ liệu lịch sử giá của một mã cổ phiếu trong N năm gần nhất.
    """
    print(f"Starting historical data collection for: {symbol.upper()} for the last {years} years.")
    collector = StockDataCollector()
    
    # Tạo cấu trúc thư mục
    output_dir = Path(f"stock_analysis/{symbol.upper()}/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Tính toán ngày bắt đầu và ngày kết thúc
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)
    
    end_date_str = end_date.strftime('%Y-%m-%d')
    start_date_str = start_date.strftime('%Y-%m-%d')

    print(f"Fetching historical prices from {start_date_str} to {end_date_str}...")
    
    data = collector.get_historical_prices(symbol, start_date_str, end_date_str, "1D")
    
    if "error" in data:
        print(f"    ERROR: {data['error']}")
        return
        
    file_path = output_dir / f"{symbol.upper()}_historical_{years}years.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        # Convert Timestamp objects to strings
        if 'data' in data and isinstance(data['data'], list):
            for row in data['data']:
                if 'time' in row and hasattr(row['time'], 'isoformat'):
                    row['time'] = row['time'].isoformat()

        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"    -> Saved to: {file_path}")
        
    print(f"Historical data collection completed for {symbol.upper()}!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide stock symbol.")
        print("Example: python get_historical_data.py VIX --years=3")
        sys.exit(1)
    
    stock_symbol = sys.argv[1]
    num_years = 3
    if '--years' in sys.argv:
        try:
            num_years = int(sys.argv[sys.argv.index('--years') + 1])
        except (ValueError, IndexError):
            print("Invalid value for --years. Using default value of 3.")

    get_historical_data(stock_symbol, num_years)
