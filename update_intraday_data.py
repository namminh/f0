import json
import time
from datetime import datetime
from pathlib import Path
from stock_data_collector import StockDataCollector

def update_intraday_data(symbols):
    """
    Cập nhật dữ liệu intraday cho danh sách mã cổ phiếu
    
    Args:
        symbols: Danh sách mã cổ phiếu cần cập nhật
    """
    collector = StockDataCollector()
    
    print(f"Starting intraday data update at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Symbols to update: {', '.join(symbols)}")
    
    for symbol in symbols:
        try:
            print(f"\n--- Updating {symbol} ---")
            
            # Kiểm tra thư mục tồn tại
            data_dir = Path(f"stock_analysis/{symbol}/data")
            if not data_dir.exists():
                print(f"Directory {data_dir} does not exist, skipping {symbol}")
                continue
            
            # Lấy dữ liệu intraday mới
            print(f"Fetching intraday data for {symbol}...")
            intraday_data = collector.get_intraday_data(symbol)
            
            if "error" in intraday_data:
                print(f"ERROR: {intraday_data['error']}")
                continue
            
            # Lưu dữ liệu
            file_path = data_dir / f"{symbol}_intraday_data.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(intraday_data, f, ensure_ascii=False, indent=4)
            
            print(f"Updated: {file_path}")
            print(f"Data points: {intraday_data.get('data_points', 'N/A')}")
            
            # Tạo backup file cũ với timestamp
            backup_path = data_dir / f"{symbol}_intraday_data_backup_{int(time.time())}.json"
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        json.dump(backup_data, f, ensure_ascii=False, indent=4)
                except:
                    pass  # Ignore backup errors
            
            # Delay giữa các request
            time.sleep(1)
            
        except Exception as e:
            print(f"Error updating {symbol}: {str(e)}")
            continue
    
    print(f"\nIntraday data update completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def update_and_regenerate_charts(symbols):
    """
    Cập nhật dữ liệu intraday và tạo lại biểu đồ
    
    Args:
        symbols: Danh sách mã cổ phiếu
    """
    # Cập nhật dữ liệu intraday
    update_intraday_data(symbols)
    
    # Tạo lại biểu đồ cho từng mã
    for symbol in symbols:
        try:
            chart_script = f"stock_analysis/{symbol}/analysis/create_{symbol.lower()}_charts.py"
            if Path(chart_script).exists():
                print(f"\nRegenerating charts for {symbol}...")
                import subprocess
                result = subprocess.run(['python', chart_script], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Charts updated successfully for {symbol}")
                else:
                    print(f"Error updating charts for {symbol}: {result.stderr}")
            else:
                print(f"Chart script not found for {symbol}: {chart_script}")
        except Exception as e:
            print(f"Error regenerating charts for {symbol}: {str(e)}")

def main():
    """
    Main function - cập nhật dữ liệu cho tất cả mã cổ phiếu trong hệ thống
    """
    # Danh sách mã cổ phiếu hiện có trong hệ thống
    existing_symbols = []
    
    # Tìm tất cả thư mục cổ phiếu
    stock_analysis_dir = Path("stock_analysis")
    if stock_analysis_dir.exists():
        for item in stock_analysis_dir.iterdir():
            if item.is_dir() and item.name not in ['__pycache__', '.git']:
                # Kiểm tra có thư mục data không
                if (item / "data").exists():
                    existing_symbols.append(item.name)
    
    if not existing_symbols:
        print("No existing stock symbols found in stock_analysis directory")
        return
    
    print(f"Found existing symbols: {', '.join(existing_symbols)}")
    
    # Cập nhật dữ liệu và tạo lại biểu đồ
    update_and_regenerate_charts(existing_symbols)

if __name__ == "__main__":
    main()