import json
import sys
import time
from pathlib import Path
from stock_data_collector import StockDataCollector

def get_data_and_save(symbol: str):
    """
    Lấy tất cả dữ liệu cần thiết cho một mã cổ phiếu và lưu vào cấu trúc thư mục.
    """
    print(f"Starting data collection for: {symbol.upper()}")
    collector = StockDataCollector()
    
    # Tạo cấu trúc thư mục
    output_dir = Path(f"stock_analysis/{symbol.upper()}/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Các loại dữ liệu cần lấy
    data_to_fetch = {
        "intraday_data": collector.get_intraday_data,
        "balance_sheet": lambda s: collector.get_financial_statements(s, "balance_sheet"),
        "income_statement": lambda s: collector.get_financial_statements(s, "income_statement"),
        "financial_ratios": collector.get_financial_ratios,
        "historical_prices": lambda s: collector.get_historical_prices(s, "2024-01-01", "2025-03-19", "1D"),
    }
    
    for data_name, fetch_func in data_to_fetch.items():
        print(f"  - Fetching {data_name}...")
        # Thêm độ trễ giữa các request để tránh bị block
        time.sleep(1)
        data = fetch_func(symbol)
        if "error" in data:
            print(f"    ERROR: {data['error']}")
            continue
        
        file_path = output_dir / f"{symbol.upper()}_{data_name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"    -> Saved to: {file_path}")
        
    print(f"Data collection completed for {symbol.upper()}!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide stock symbol.")
        print("Example: python get_data_for_stock.py VIX")
        sys.exit(1)
    
    stock_symbol = sys.argv[1]
    get_data_and_save(stock_symbol)