#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOMINUS AGENT - Intraday Analysis (Simple Fast)
Workflow nhanh: Phan tich intraday trong 2 phut

Usage: python automation/intraday_analysis_simple.py [SYMBOL]
Output: stock_analysis/[SYMBOL]/reports/[SYMBOL]_intraday_report.html
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path

def log_step(step, message):
    """Log tien trinh"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] STEP {step}: {message}")

def run_command(command, description):
    """Chay lenh voi error handling"""
    try:
        log_step("CMD", description)
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"SUCCESS: {description}")
            return True
        else:
            print(f"FAILED: {description}")
            return False
    except Exception as e:
        print(f"ERROR: {description} - {str(e)}")
        return False

def create_intraday_report(symbol):
    """Tao bao cao intraday HTML"""
    
    # Doc du lieu intraday
    data_file = f"stock_analysis/{symbol}/data/{symbol}_intraday_data.json"
    
    if not os.path.exists(data_file):
        print(f"Khong tim thay du lieu: {data_file}")
        return False
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Tao noi dung HTML don gian
        html_content = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} - Bao cao Intraday</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2196F3; color: white; padding: 20px; text-align: center; }}
        .metric {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .charts {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin: 20px 0; }}
        .chart {{ text-align: center; }}
        .chart img {{ max-width: 100%; height: 200px; object-fit: contain; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{symbol} - Phan tich Intraday</h1>
        <p>Cap nhat: {data.get('timestamp', 'N/A')}</p>
    </div>
    
    <div class="metric">
        <h3>Thong tin giao dich</h3>
        <p><strong>Tong khoi luong:</strong> {data.get('total_volume', 'N/A'):,} co phieu</p>
        <p><strong>So giao dich:</strong> {data.get('data_points', 'N/A'):,}</p>
        <p><strong>Thoi gian:</strong> {data.get('start_time', 'N/A')} - {data.get('end_time', 'N/A')}</p>
    </div>
    
    <div class="metric">
        <h3>Thong tin gia</h3>
        <p><strong>Gia cao nhat:</strong> {data.get('high_price', 'N/A')} VND</p>
        <p><strong>Gia thap nhat:</strong> {data.get('low_price', 'N/A')} VND</p>
        <p><strong>Gia trung binh:</strong> {data.get('avg_price', 'N/A'):.2f} VND</p>
        <p><strong>Bien dong:</strong> {data.get('price_range', 'N/A')} VND</p>
    </div>
    
    <div class="charts">
        <div class="chart">
            <h4>Xu huong gia</h4>
            <img src="../charts/key_charts/price_trend.png" alt="Price Trend">
        </div>
        <div class="chart">
            <h4>Khoi luong theo gio</h4>
            <img src="../charts/key_charts/volume_by_hour.png" alt="Volume by Hour">
        </div>
        <div class="chart">
            <h4>Ty le mua/ban</h4>
            <img src="../charts/key_charts/buy_vs_sell.png" alt="Buy vs Sell">
        </div>
    </div>
    
    <div class="metric">
        <h3>Khuyen nghi ngan han</h3>
        <p><strong>Xu huong:</strong> Theo doi trong phien</p>
        <p><strong>Entry point:</strong> Quan sat vung support/resistance</p>
        <p><strong>Risk:</strong> Bien dong intraday cao</p>
    </div>
    
    <footer style="text-align: center; margin-top: 40px; color: #666;">
        <p>Dominus Agent - Intraday Analysis System</p>
        <p>Cap nhat: {time.strftime('%d/%m/%Y %H:%M:%S')}</p>
    </footer>
</body>
</html>
        """
        
        # Luu bao cao
        report_file = f"stock_analysis/{symbol}/reports/{symbol}_intraday_report.html"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Bao cao intraday da tao: {report_file}")
        return True
        
    except Exception as e:
        print(f"Loi tao bao cao: {str(e)}")
        return False

def intraday_analysis(symbol):
    """Workflow phan tich intraday nhanh"""
    
    print("="*50)
    print(f"DOMINUS INTRADAY ANALYSIS: {symbol}")
    print("="*50)
    
    # BUOC 1: Cap nhat du lieu intraday
    log_step(1, "Cap nhat du lieu intraday")
    if not run_command(f"python quick_update.py {symbol}", 
                      f"Cap nhat {symbol}"):
        return False
    
    # BUOC 2: Tao 3 bieu do co ban (neu script co san)
    log_step(2, "Tao bieu do co ban")
    chart_script = f"stock_analysis/{symbol}/analysis/create_{symbol.lower()}_charts.py"
    if os.path.exists(chart_script):
        run_command(f"python {chart_script}", "Tao key charts")
    else:
        print(f"WARNING: Script khong ton tai: {chart_script}")
    
    # BUOC 3: Tao bao cao intraday
    log_step(3, "Tao bao cao intraday")
    if not create_intraday_report(symbol):
        return False
    
    print("="*50)
    print("INTRADAY ANALYSIS HOAN THANH!")
    print(f"Bao cao: stock_analysis/{symbol}/reports/{symbol}_intraday_report.html")
    print("="*50)
    return True

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python automation/intraday_analysis_simple.py [SYMBOL]")
        print("Example: python automation/intraday_analysis_simple.py VHM")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    
    start_time = time.time()
    success = intraday_analysis(symbol)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"\nThoi gian thuc hien: {duration:.1f} giay")
    
    if success:
        print(f"{symbol} INTRADAY ANALYSIS THANH CONG!")
    else:
        print(f"{symbol} INTRADAY ANALYSIS THAT BAI!")
        sys.exit(1)

if __name__ == "__main__":
    main()