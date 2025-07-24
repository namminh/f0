#!/usr/bin/env python3
"""
Portfolio Manager - Quản lý danh mục cổ phiếu
Sử dụng: python automation/portfolio_manager.py [options]
"""

import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime

class PortfolioManager:
    def __init__(self):
        self.base_dir = Path("stock_analysis")
        self.config_dir = Path("automation/config")
        self.config_file = self.config_dir / "stocks_config.json"
        self.template_dir = Path("automation/templates")
        
    def get_available_stocks(self):
        """Get list of available stocks"""
        if not self.base_dir.exists():
            return []
        
        stocks = []
        for item in self.base_dir.iterdir():
            if item.is_dir() and (item / "data").exists():
                stocks.append(item.name)
        
        return sorted(stocks)
    
    def get_active_stocks(self):
        """Get list of active stocks from config"""
        if not self.config_file.exists():
            return []
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get("active_stocks", [])
    
    def create_stock_structure(self, symbol):
        """Create directory structure for a new stock"""
        symbol = symbol.upper()
        stock_dir = self.base_dir / symbol
        
        if stock_dir.exists():
            print(f"Directory for {symbol} already exists")
            return True
        
        try:
            # Create directories
            (stock_dir / "data").mkdir(parents=True, exist_ok=True)
            (stock_dir / "analysis").mkdir(parents=True, exist_ok=True)
            (stock_dir / "charts" / "key_charts").mkdir(parents=True, exist_ok=True)
            (stock_dir / "charts" / "detailed_charts").mkdir(parents=True, exist_ok=True)
            (stock_dir / "reports").mkdir(parents=True, exist_ok=True)
            
            # Create analysis scripts from templates
            self.create_analysis_scripts(symbol)
            
            print(f"Created directory structure for {symbol}")
            return True
            
        except Exception as e:
            print(f"Error creating structure for {symbol}: {e}")
            return False
    
    def create_analysis_scripts(self, symbol):
        """Create analysis scripts for the stock"""
        symbol_upper = symbol.upper()
        symbol_lower = symbol.lower()
        stock_dir = self.base_dir / symbol_upper / "analysis"
        
        # Create analyze script
        analyze_script = f"""import json
import pandas as pd
import sys
import codecs
from datetime import datetime
import numpy as np

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

def analyze_{symbol_lower}_data():
    \"\"\"Phân tích dữ liệu của {symbol_upper}.\"\"\"
    # Load data
    try:
        with open("stock_analysis/{symbol_upper}/data/{symbol_upper}_balance_sheet.json", "r", encoding="utf-8") as f:
            balance_sheet_data = json.load(f)
    except FileNotFoundError:
        balance_sheet_data = None
    
    try:
        with open("stock_analysis/{symbol_upper}/data/{symbol_upper}_intraday_data.json", "r", encoding="utf-8") as f:
            intraday_data = json.load(f)
    except FileNotFoundError:
        intraday_data = None

    try:
        with open("stock_analysis/{symbol_upper}/data/{symbol_upper}_financial_ratios.json", "r", encoding="utf-8") as f:
            financial_ratios_data = json.load(f)
    except FileNotFoundError:
        financial_ratios_data = None

    # Analysis
    print("=== PHÂN TÍCH CỔ PHIẾU {symbol_upper} ===")

    # Balance Sheet Analysis
    if balance_sheet_data and 'data' in balance_sheet_data and balance_sheet_data['data']:
        print("\\n--- Phân tích Bảng cân đối kế toán ---")
        df_balance_sheet = pd.DataFrame(balance_sheet_data['data'])
        print(df_balance_sheet.head())
    else:
        print("\\n--- Không có dữ liệu Bảng cân đối kế toán để phân tích ---")

    # Financial Ratios Analysis
    if financial_ratios_data and 'data' in financial_ratios_data and financial_ratios_data['data']:
        print("\\n--- Phân tích Tỷ số tài chính ---")
        df_ratios = pd.DataFrame(financial_ratios_data['data'])
        print(df_ratios.head())
    else:
        print("\\n--- Không có dữ liệu Tỷ số tài chính để phân tích ---")

    # Intraday Data Analysis
    if intraday_data and 'data' in intraday_data and intraday_data['data']:
        print("\\n--- Phân tích Dữ liệu trong ngày {symbol_upper} ---")
        df_intraday = pd.DataFrame(intraday_data['data'])
        
        # Convert time to datetime
        df_intraday['time'] = pd.to_datetime(df_intraday['time'])
        df_intraday['hour'] = df_intraday['time'].dt.hour
        
        print(f"Tổng số điểm dữ liệu: {{len(df_intraday)}}")
        print(f"Thời gian giao dịch: {{df_intraday['time'].min()}} đến {{df_intraday['time'].max()}}")
        print(f"Giá cao nhất: {{df_intraday['price'].max():.2f}}")
        print(f"Giá thấp nhất: {{df_intraday['price'].min():.2f}}")
        print(f"Giá trung bình: {{df_intraday['price'].mean():.2f}}")
        print(f"Tổng khối lượng giao dịch: {{df_intraday['volume'].sum():,}}")
        
        # Volume by hour analysis
        volume_by_hour = df_intraday.groupby('hour')['volume'].sum()
        print("\\n--- Khối lượng giao dịch theo giờ ---")
        for hour, volume in volume_by_hour.items():
            print(f"Giờ {{hour:02d}}: {{volume:,}}")
        
        # Buy vs Sell analysis
        buy_volume = df_intraday[df_intraday['match_type'] == 'Buy']['volume'].sum()
        sell_volume = df_intraday[df_intraday['match_type'] == 'Sell']['volume'].sum()
        print(f"\\nKhối lượng mua: {{buy_volume:,}}")
        print(f"Khối lượng bán: {{sell_volume:,}}")
        print(f"Tỷ lệ mua/bán: {{buy_volume/sell_volume:.2f}}" if sell_volume > 0 else "Tỷ lệ mua/bán: N/A")
        
        # Price volatility analysis
        price_std = df_intraday['price'].std()
        price_range = df_intraday['price'].max() - df_intraday['price'].min()
        print(f"\\nĐộ biến động giá (std): {{price_std:.2f}}")
        print(f"Khoảng giá: {{price_range:.2f}}")
        
    else:
        print("\\n--- Không có dữ liệu trong ngày để phân tích ---")

if __name__ == "__main__":
    analyze_{symbol_lower}_data()
"""
        
        with open(stock_dir / f"analyze_{symbol_lower}_data.py", 'w', encoding='utf-8') as f:
            f.write(analyze_script)
        
        # Create charts script
        charts_script = f"""import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def create_{symbol_lower}_charts():
    \"\"\"Tạo biểu đồ phân tích cho {symbol_upper}.\"\"\"
    # Create directories
    Path("stock_analysis/{symbol_upper}/charts/key_charts").mkdir(parents=True, exist_ok=True)
    Path("stock_analysis/{symbol_upper}/charts/detailed_charts").mkdir(parents=True, exist_ok=True)

    # Load data
    try:
        with open("stock_analysis/{symbol_upper}/data/{symbol_upper}_balance_sheet.json", "r", encoding="utf-8") as f:
            balance_sheet_data = json.load(f)
    except FileNotFoundError:
        balance_sheet_data = None
        
    try:
        with open("stock_analysis/{symbol_upper}/data/{symbol_upper}_intraday_data.json", "r", encoding="utf-8") as f:
            intraday_data = json.load(f)
    except FileNotFoundError:
        intraday_data = None
        
    try:
        with open("stock_analysis/{symbol_upper}/data/{symbol_upper}_income_statement.json", "r", encoding="utf-8") as f:
            income_statement_data = json.load(f)
    except FileNotFoundError:
        income_statement_data = None
        
    try:
        with open("stock_analysis/{symbol_upper}/data/{symbol_upper}_financial_ratios.json", "r", encoding="utf-8") as f:
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
    
    print("✅ Charts created for {symbol_upper}")

def create_price_chart(intraday_data):
    \"\"\"Tạo biểu đồ giá trong ngày.\"\"\"
    if not intraday_data or 'data' not in intraday_data or not intraday_data['data']:
        return

    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time')

    plt.figure(figsize=(12, 6))
    plt.plot(df['time'], df['price'], label='Giá')
    plt.title('Biểu đồ giá trong ngày của {symbol_upper}')
    plt.xlabel('Thời gian')
    plt.ylabel('Giá')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("stock_analysis/{symbol_upper}/charts/key_charts/price_trend.png")
    plt.close()

def create_volume_chart(intraday_data):
    \"\"\"Tạo biểu đồ khối lượng giao dịch.\"\"\"
    if not intraday_data or 'data' not in intraday_data or not intraday_data['data']:
        return

    df = pd.DataFrame(intraday_data['data'])
    df['time'] = pd.to_datetime(df['time'])
    df['hour'] = df['time'].dt.hour
    volume_by_hour = df.groupby('hour')['volume'].sum()

    plt.figure(figsize=(12, 6))
    volume_by_hour.plot(kind='bar', title='Khối lượng giao dịch theo giờ - {symbol_upper}')
    plt.xlabel('Giờ')
    plt.ylabel('Khối lượng')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("stock_analysis/{symbol_upper}/charts/key_charts/volume_by_hour.png")
    plt.close()

def create_buy_sell_chart(intraday_data):
    \"\"\"Tạo biểu đồ mua/bán.\"\"\"
    if not intraday_data or 'data' not in intraday_data or not intraday_data['data']:
        return

    df = pd.DataFrame(intraday_data['data'])
    buy_volume = df[df['match_type'] == 'Buy']['volume'].sum()
    sell_volume = df[df['match_type'] == 'Sell']['volume'].sum()

    plt.figure(figsize=(8, 8))
    plt.pie([buy_volume, sell_volume], labels=['Mua', 'Bán'], autopct='%1.1f%%', startangle=90)
    plt.title('Tỷ lệ khối lượng Mua vs. Bán - {symbol_upper}')
    plt.savefig("stock_analysis/{symbol_upper}/charts/key_charts/buy_vs_sell.png")
    plt.close()

def create_financial_charts(balance_sheet_data):
    \"\"\"Tạo biểu đồ tài chính thực sự cho {symbol_upper}.\"\"\"
    # Import template function
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'chart_templates'))
    from financial_chart_template import create_real_financial_chart
    
    # Use real financial chart template
    output_path = "stock_analysis/{symbol_upper}/charts/detailed_charts/financial_analysis.png"
    success = create_real_financial_chart(balance_sheet_data, "{symbol_upper}", output_path)
    
    if not success:
        print("{symbol_upper}: No financial chart created - insufficient data")

if __name__ == "__main__":
    create_{symbol_lower}_charts()
"""
        
        with open(stock_dir / f"create_{symbol_lower}_charts.py", 'w', encoding='utf-8') as f:
            f.write(charts_script)
        
        print(f"Created analysis scripts for {symbol}")
    
    def add_stock_to_config(self, symbol):
        """Add stock to active stocks in config"""
        symbol = symbol.upper()
        
        # Load current config or create default
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            config = {
                "active_stocks": [],
                "update_frequency": {
                    "quick_update": 300,
                    "full_analysis": 1800,
                    "daily_report": "15:30"
                },
                "market_hours": {
                    "start": "09:00",
                    "end": "15:00",
                    "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
                }
            }
        
        # Add stock if not already in list
        if symbol not in config["active_stocks"]:
            config["active_stocks"].append(symbol)
            config["active_stocks"].sort()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            
            print(f"Added {symbol} to active stocks")
        else:
            print(f"{symbol} already in active stocks")
    
    def remove_stock_from_config(self, symbol):
        """Remove stock from active stocks in config"""
        symbol = symbol.upper()
        
        if not self.config_file.exists():
            print("Config file not found")
            return False
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if symbol in config["active_stocks"]:
            config["active_stocks"].remove(symbol)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            
            print(f"Removed {symbol} from active stocks")
            return True
        else:
            print(f"{symbol} not in active stocks")
            return False
    
    def list_stocks(self):
        """List all stocks and their status"""
        available = self.get_available_stocks()
        active = self.get_active_stocks()
        
        print("Stock Portfolio Status")
        print("=" * 40)
        
        if not available:
            print("No stocks found in stock_analysis/")
            return
        
        for stock in available:
            status = "ACTIVE" if stock in active else "Available"
            
            # Check data freshness
            data_file = self.base_dir / stock / "data" / f"{stock}_intraday_data.json"
            if data_file.exists():
                try:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        timestamp = data.get('timestamp', 'Unknown')
                        data_points = data.get('data_points', 0)
                    
                    print(f"{status} {stock} - {data_points:,} points (Updated: {timestamp})")
                except:
                    print(f"{status} {stock} - Data file error")
            else:
                print(f"{status} {stock} - No data")
        
        print(f"\nActive stocks: {len(active)}/{len(available)}")
    
    def create_report_template(self, symbol):
        """Create HTML report template for the stock"""
        symbol = symbol.upper()
        report_file = self.base_dir / symbol / "reports" / f"{symbol}_analysis_report.html"
        
        html_template = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo cáo Phân tích Cổ phiếu {symbol}</title>
    <style>
        body {{
            font-family: sans-serif;
            line-height: 1.6;
            margin: 20px;
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        .chart-container {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
        }}
        .summary {{
            background-color: #f2f2f2;
            padding: 15px;
            border-left: 5px solid #007bff;
            margin-bottom: 20px;
        }}
        .key-metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }}
        .metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #28a745;
        }}
    </style>
</head>
<body>
    <h1>Báo cáo Phân tích Cổ phiếu {symbol}</h1>
    
    <div class="key-metrics">
        <div class="metric-card">
            <h4>Giá hiện tại</h4>
            <div class="metric-value">-- VND</div>
        </div>
        <div class="metric-card">
            <h4>Khối lượng giao dịch</h4>
            <div class="metric-value">--</div>
        </div>
        <div class="metric-card">
            <h4>Biên độ dao động</h4>
            <div class="metric-value">-- VND</div>
        </div>
        <div class="metric-card">
            <h4>Tỷ lệ mua/bán</h4>
            <div class="metric-value">--</div>
        </div>
    </div>

    <div class="summary">
        <h3>Phân tích tổng quan {symbol}</h3>
        <p>Báo cáo phân tích được tạo tự động. Dữ liệu sẽ được cập nhật sau khi chạy phân tích.</p>
    </div>

    <h2>Phân tích Dữ liệu trong ngày</h2>
    <div class="chart-container">
        <img src="../charts/key_charts/price_trend.png" alt="Biểu đồ giá trong ngày của {symbol}">
        <p><em>Biểu đồ giá trong ngày cho thấy xu hướng giao dịch của {symbol}</em></p>
    </div>
    <div class="chart-container">
        <img src="../charts/key_charts/volume_by_hour.png" alt="Biểu đồ khối lượng giao dịch theo giờ">
        <p><em>Phân tích khối lượng giao dịch theo từng giờ trong ngày</em></p>
    </div>
    <div class="chart-container">
        <img src="../charts/key_charts/buy_vs_sell.png" alt="Biểu đồ tỷ lệ khối lượng Mua vs. Bán">
        <p><em>Tỷ lệ khối lượng giao dịch mua và bán</em></p>
    </div>

    <h2>Phân tích Tài chính Chi tiết</h2>
    <div class="chart-container">
        <img src="../charts/detailed_charts/financial_analysis.png" alt="Phân tích tài chính chi tiết của {symbol}">
        <p><em>Phân tích các chỉ số tài chính chính của {symbol}</em></p>
    </div>
    
    <p><small><em>Báo cáo được tạo tự động từ dữ liệu ngày {datetime.now().strftime('%d/%m/%Y')}</em></small></p>

</body>
</html>"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        print(f"Created report template for {symbol}")

def main():
    parser = argparse.ArgumentParser(description='Portfolio Manager')
    parser.add_argument('--add', metavar='SYMBOL', help='Add a new stock to portfolio')
    parser.add_argument('--remove', metavar='SYMBOL', help='Remove stock from active list')
    parser.add_argument('--list', action='store_true', help='List all stocks and status')
    parser.add_argument('--structure', metavar='SYMBOL', help='Create directory structure for stock')
    parser.add_argument('--config', action='store_true', help='Show current configuration')
    
    args = parser.parse_args()
    manager = PortfolioManager()
    
    if args.add:
        symbol = args.add.upper()
        print(f"Adding {symbol} to portfolio...")
        
        # Create structure
        if manager.create_stock_structure(symbol):
            # Add to config
            manager.add_stock_to_config(symbol)
            # Create report template
            manager.create_report_template(symbol)
            print(f"{symbol} successfully added to portfolio")
            print(f"Next step: Run 'python get_data_for_stock.py {symbol}' to fetch initial data")
        else:
            print(f"Failed to add {symbol}")
            
    elif args.remove:
        symbol = args.remove.upper()
        if manager.remove_stock_from_config(symbol):
            print(f"✅ {symbol} removed from active stocks")
            print(f"ℹ️ Directory structure preserved. Use --structure to recreate if needed.")
            
    elif args.structure:
        symbol = args.structure.upper()
        if manager.create_stock_structure(symbol):
            manager.create_report_template(symbol)
            print(f"Directory structure created for {symbol}")
            
    elif args.list:
        manager.list_stocks()
        
    elif args.config:
        if manager.config_file.exists():
            with open(manager.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(json.dumps(config, indent=2, ensure_ascii=False))
        else:
            print("❌ Config file not found")
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()