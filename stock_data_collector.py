import json
import time
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import numpy as np
from vnstock import Vnstock

# Ignore warnings
warnings.filterwarnings("ignore")

class StockDataCollector:
    """
    Công cụ thu thập dữ liệu chứng khoán Việt Nam
    Đơn giản hóa từ StockAnalysisTool để tập trung vào việc lấy dữ liệu
    """
    
    def __init__(self, data_source: str = "VCI"):
        """
        Khởi tạo collector
        
        Args:
            data_source: Nguồn dữ liệu (VCI, TCBS, DNSE)
        """
        self.data_source = data_source
        self.max_retries = 3
        
    def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """
        Lấy thông tin tổng quan công ty
        
        Args:
            symbol: Mã cổ phiếu
            
        Returns:
            Dict chứa thông tin công ty
        """
        for attempt in range(self.max_retries):
            try:
                stock = Vnstock().stock(symbol=symbol, source=self.data_source)
                df_overview = stock.company.overview()
                
                if df_overview is None or df_overview.empty:
                    return {"error": f"Không có dữ liệu tổng quan cho {symbol}"}
                
                # Chuyển đổi dữ liệu
                overview_data = df_overview.iloc[0].to_dict()
                
                # Xử lý NaN values
                for key, value in overview_data.items():
                    if pd.isna(value):
                        overview_data[key] = None
                
                return {
                    "symbol": symbol,
                    "data_source": self.data_source,
                    "data": overview_data,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return {"error": f"Lỗi khi lấy dữ liệu tổng quan {symbol}: {str(e)}"}
    
    def get_historical_prices(self, symbol: str, start_date: str, end_date: str, 
                            interval: str = "1D") -> Dict[str, Any]:
        """
        Lấy dữ liệu giá lịch sử
        
        Args:
            symbol: Mã cổ phiếu
            start_date: Ngày bắt đầu (YYYY-MM-DD)
            end_date: Ngày kết thúc (YYYY-MM-DD)
            interval: Khoảng thời gian (1D, 1H, etc.)
            
        Returns:
            Dict chứa dữ liệu giá lịch sử
        """
        for attempt in range(self.max_retries):
            try:
                stock = Vnstock().stock(symbol=symbol, source=self.data_source)
                df_history = stock.quote.history(
                    start=start_date, 
                    end=end_date, 
                    interval=interval
                )
                
                if df_history is None or df_history.empty:
                    return {"error": f"Không có dữ liệu giá lịch sử cho {symbol}"}
                
                # Xử lý dữ liệu
                df_copy = df_history.copy()
                
                # Đảm bảo có DatetimeIndex
                if not isinstance(df_copy.index, pd.DatetimeIndex):
                    # Tìm cột datetime
                    datetime_cols = [col for col in df_copy.columns 
                                   if pd.api.types.is_datetime64_any_dtype(df_copy[col])]
                    if datetime_cols:
                        df_copy = df_copy.set_index(datetime_cols[0])
                    else:
                        return {"error": f"Không tìm thấy cột thời gian cho {symbol}"}
                
                # Chuẩn hóa tên cột
                rename_mapping = {
                    'open': 'Open',
                    'high': 'High', 
                    'low': 'Low',
                    'close': 'Close',
                    'volume': 'Volume'
                }
                df_copy.rename(columns=rename_mapping, inplace=True)
                
                # Sắp xếp theo thời gian
                df_copy = df_copy.sort_index()
                
                # Chuyển đổi sang format JSON
                df_json = df_copy.reset_index()
                
                # Convert datetime column to string
                if hasattr(df_json.iloc[:, 0], 'dt'):
                    df_json.iloc[:, 0] = df_json.iloc[:, 0].dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    # Handle Timestamp objects
                    df_json.iloc[:, 0] = df_json.iloc[:, 0].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if hasattr(x, 'strftime') else str(x))
                
                df_json.columns = [df_json.columns[0]] + df_json.columns[1:].tolist()
                
                # Xử lý NaN values và Timestamp objects
                df_json = df_json.replace({np.nan: None})
                
                # Convert any remaining Timestamp objects to strings
                for col in df_json.columns:
                    if df_json[col].dtype == 'object':
                        df_json[col] = df_json[col].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if hasattr(x, 'strftime') else x)
                
                return {
                    "symbol": symbol,
                    "data_source": self.data_source,
                    "start_date": start_date,
                    "end_date": end_date,
                    "interval": interval,
                    "data_points": len(df_json),
                    "data": df_json.to_dict(orient="records"),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return {"error": f"Lỗi khi lấy dữ liệu giá lịch sử {symbol}: {str(e)}"}
    
    def get_intraday_data(self, symbol: str, page_size: int = 10000) -> Dict[str, Any]:
        """
        Lấy dữ liệu giao dịch trong ngày
        
        Args:
            symbol: Mã cổ phiếu
            page_size: Số lượng bản ghi
            
        Returns:
            Dict chứa dữ liệu intraday
        """
        for attempt in range(self.max_retries):
            try:
                stock = Vnstock().stock(symbol=symbol, source=self.data_source)
                df_intraday = stock.quote.intraday(page_size=page_size, show_log=False)
                
                if df_intraday is None or df_intraday.empty:
                    return {"error": f"Không có dữ liệu intraday cho {symbol}"}
                
                # Xử lý dữ liệu
                df_copy = df_intraday.copy()
                
                # Đảm bảo có cột time
                if 'time' not in df_copy.columns:
                    time_cols = [col for col in df_copy.columns 
                               if 'time' in col.lower() or 'date' in col.lower()]
                    if time_cols:
                        df_copy.rename(columns={time_cols[0]: 'time'}, inplace=True)
                    else:
                        return {"error": f"Không tìm thấy cột thời gian cho {symbol}"}
                
                # Chuyển đổi thời gian
                df_copy['time'] = pd.to_datetime(df_copy['time'])
                
                # Chuẩn hóa timezone
                if df_copy['time'].dt.tz is not None:
                    df_copy['time'] = df_copy['time'].dt.tz_convert('Asia/Ho_Chi_Minh')
                else:
                    df_copy['time'] = df_copy['time'].dt.tz_localize('Asia/Ho_Chi_Minh')
                
                # Sắp xếp theo thời gian
                df_copy = df_copy.sort_values('time')
                
                # Chuyển đổi sang format JSON
                df_copy['time'] = df_copy['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                df_copy = df_copy.replace({np.nan: None})
                
                return {
                    "symbol": symbol,
                    "data_source": self.data_source,
                    "data_points": len(df_copy),
                    "data": df_copy.to_dict(orient="records"),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return {"error": f"Lỗi khi lấy dữ liệu intraday {symbol}: {str(e)}"}
    
    def get_financial_statements(self, symbol: str, statement_type: str, 
                               period: str = "year", lang: str = "vi") -> Dict[str, Any]:
        """
        Lấy báo cáo tài chính
        
        Args:
            symbol: Mã cổ phiếu
            statement_type: Loại báo cáo (balance_sheet, income_statement, cash_flow)
            period: Kỳ báo cáo (year, quarter)
            lang: Ngôn ngữ (vi, en)
            
        Returns:
            Dict chứa báo cáo tài chính
        """
        for attempt in range(self.max_retries):
            try:
                stock = Vnstock().stock(symbol=symbol, source=self.data_source)
                
                # Lấy dữ liệu theo loại báo cáo
                if statement_type == "balance_sheet":
                    df = stock.finance.balance_sheet(period=period, lang=lang)
                elif statement_type == "income_statement":
                    df = stock.finance.income_statement(period=period, lang=lang, dropna=False)
                elif statement_type == "cash_flow":
                    df = stock.finance.cash_flow(period=period, lang=lang, dropna=False)
                else:
                    return {"error": f"Loại báo cáo không hợp lệ: {statement_type}"}
                
                if df is None or df.empty:
                    return {"error": f"Không có dữ liệu {statement_type} cho {symbol}"}
                
                # Xử lý dữ liệu
                df_copy = df.copy()
                
                # Xử lý MultiIndex
                if isinstance(df_copy.index, pd.MultiIndex):
                    df_copy.index = ['_'.join(map(str, idx)) for idx in df_copy.index]
                
                # Xử lý MultiIndex cho columns
                if isinstance(df_copy.columns, pd.MultiIndex):
                    df_copy.columns = ['_'.join(map(str, col)) for col in df_copy.columns]
                
                # Reset index
                df_reset = df_copy.reset_index()
                
                # Chuẩn hóa tên cột đầu tiên
                if len(df_reset.columns) > 0:
                    df_reset.rename(columns={df_reset.columns[0]: 'Financial_Metric'}, inplace=True)
                
                # Chuyển đổi dữ liệu số
                for col in df_reset.columns[1:]:
                    if df_reset[col].dtype == 'object':
                        df_reset[col] = pd.to_numeric(df_reset[col], errors='coerce')
                
                # Xử lý NaN values
                df_reset = df_reset.replace({np.nan: None})
                
                return {
                    "symbol": symbol,
                    "data_source": self.data_source,
                    "statement_type": statement_type,
                    "period": period,
                    "language": lang,
                    "data": df_reset.to_dict(orient="records"),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return {"error": f"Lỗi khi lấy {statement_type} cho {symbol}: {str(e)}"}
    
    def get_financial_ratios(self, symbol: str, period: str = "year", 
                           lang: str = "vi") -> Dict[str, Any]:
        """
        Lấy chỉ số tài chính
        
        Args:
            symbol: Mã cổ phiếu
            period: Kỳ báo cáo (year, quarter)
            lang: Ngôn ngữ (vi, en)
            
        Returns:
            Dict chứa chỉ số tài chính
        """
        for attempt in range(self.max_retries):
            try:
                stock = Vnstock().stock(symbol=symbol, source=self.data_source)
                df = stock.finance.ratio(period=period, lang=lang, dropna=False)
                
                if df is None or df.empty:
                    return {"error": f"Không có dữ liệu chỉ số tài chính cho {symbol}"}
                
                # Xử lý dữ liệu
                df_copy = df.copy()
                
                # Xử lý MultiIndex
                if isinstance(df_copy.index, pd.MultiIndex):
                    df_copy.index = ['_'.join(map(str, idx)) for idx in df_copy.index]
                
                # Xử lý MultiIndex cho columns
                if isinstance(df_copy.columns, pd.MultiIndex):
                    df_copy.columns = ['_'.join(map(str, col)) for col in df_copy.columns]
                
                # Reset index
                df_reset = df_copy.reset_index()
                
                # Chuẩn hóa tên cột đầu tiên
                if len(df_reset.columns) > 0:
                    df_reset.rename(columns={df_reset.columns[0]: 'Ratio_Name'}, inplace=True)
                
                # Chuyển đổi dữ liệu số
                for col in df_reset.columns[1:]:
                    if df_reset[col].dtype == 'object':
                        # Làm sạch dữ liệu
                        cleaned = df_reset[col].astype(str).str.replace('x', '').str.replace(r'[^\d\.,-]', '', regex=True)
                        df_reset[col] = pd.to_numeric(cleaned, errors='coerce')
                
                # Xử lý NaN values
                df_reset = df_reset.replace({np.nan: None})
                
                return {
                    "symbol": symbol,
                    "data_source": self.data_source,
                    "period": period,
                    "language": lang,
                    "data": df_reset.to_dict(orient="records"),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return {"error": f"Lỗi khi lấy chỉ số tài chính {symbol}: {str(e)}"}
    
    def collect_all_data(self, symbols: List[str], output_dir: str = "data_output") -> Dict[str, Any]:
        """
        Thu thập toàn bộ dữ liệu cho danh sách mã cổ phiếu
        
        Args:
            symbols: Danh sách mã cổ phiếu
            output_dir: Thư mục lưu kết quả
            
        Returns:
            Dict chứa tất cả dữ liệu
        """
        results = {}
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        for symbol in symbols:
            print(f"Đang thu thập dữ liệu cho {symbol}...")
            
            symbol_data = {
                "symbol": symbol,
                "company_overview": self.get_company_overview(symbol),
                "historical_prices": self.get_historical_prices(
                    symbol, 
                    (datetime.now().replace(year=datetime.now().year - 1)).strftime('%Y-%m-%d'),
                    datetime.now().strftime('%Y-%m-%d')
                ),
                "intraday_data": self.get_intraday_data(symbol),
                "balance_sheet": self.get_financial_statements(symbol, "balance_sheet"),
                "income_statement": self.get_financial_statements(symbol, "income_statement"),
                "cash_flow": self.get_financial_statements(symbol, "cash_flow"),
                "financial_ratios": self.get_financial_ratios(symbol),
                "collected_at": datetime.now().isoformat()
            }
            
            results[symbol] = symbol_data
            
            # Lưu dữ liệu riêng cho từng mã
            with open(Path(output_dir) / f"{symbol}_data.json", 'w', encoding='utf-8') as f:
                json.dump(symbol_data, f, ensure_ascii=False, indent=2)
            
            # Delay giữa các request
            time.sleep(1)
        
        # Lưu tất cả dữ liệu
        with open(Path(output_dir) / "all_data.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return results
    
    def save_to_csv(self, symbol: str, data_type: str, data: Dict[str, Any], 
                   output_dir: str = "data_output") -> bool:
        """
        Lưu dữ liệu ra file CSV
        
        Args:
            symbol: Mã cổ phiếu
            data_type: Loại dữ liệu
            data: Dữ liệu cần lưu
            output_dir: Thư mục lưu
            
        Returns:
            True nếu thành công
        """
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            if "data" in data and isinstance(data["data"], list):
                df = pd.DataFrame(data["data"])
                csv_path = Path(output_dir) / f"{symbol}_{data_type}.csv"
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                print(f"Đã lưu {csv_path}")
                return True
            else:
                print(f"Không có dữ liệu phù hợp để lưu CSV cho {symbol} - {data_type}")
                return False
                
        except Exception as e:
            print(f"Lỗi khi lưu CSV cho {symbol} - {data_type}: {str(e)}")
            return False

def main():
    """Ví dụ sử dụng"""
    # Khởi tạo collector
    collector = StockDataCollector(data_source="VCI")
    
    # Danh sách mã cổ phiếu
    symbols = ["VCB", "VIC", "VHM", "TCB", "BID"]
    
    # Thu thập dữ liệu
    print("Bắt đầu thu thập dữ liệu...")
    results = collector.collect_all_data(symbols)
    
    # Lưu dữ liệu ra CSV
    for symbol in symbols:
        if symbol in results:
            collector.save_to_csv(symbol, "historical_prices", results[symbol]["historical_prices"])
            collector.save_to_csv(symbol, "balance_sheet", results[symbol]["balance_sheet"])
            collector.save_to_csv(symbol, "income_statement", results[symbol]["income_statement"])
            collector.save_to_csv(symbol, "financial_ratios", results[symbol]["financial_ratios"])
    
    print("Hoàn thành thu thập dữ liệu!")

if __name__ == "__main__":
    main()