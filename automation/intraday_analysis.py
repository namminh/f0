#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOMINUS AGENT - Intraday Analysis (Fast)
Workflow nhanh: Phân tích intraday trong 2 phút

Usage: python automation/intraday_analysis.py [SYMBOL]
Output: stock_analysis/[SYMBOL]/reports/[SYMBOL]_intraday_report.html
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path

def log_step(step, message):
    """Log tiến trình"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] STEP {step}: {message}")

def run_command(command, description):
    """Chạy lệnh với error handling"""
    try:
        log_step("CMD", f"{description}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"OK {description} - SUCCESS")
            return True
        else:
            print(f"ERROR {description} - FAILED: {result.stderr}")
            return False
    except Exception as e:
        print(f"ERROR {description} - ERROR: {str(e)}")
        return False

def create_intraday_report(symbol):
    """Tạo báo cáo intraday HTML"""
    
    # Đọc dữ liệu intraday
    data_file = f"stock_analysis/{symbol}/data/{symbol}_intraday_data.json"
    
    if not os.path.exists(data_file):
        print(f"ERROR Khong tim thay du lieu: {data_file}")
        return False
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Read template
        with open('automation/intraday_template.html', 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Replace placeholders
        html_content = template.format(
            symbol=symbol,
            timestamp=data.get('timestamp', 'N/A'),
            total_volume=str(data.get('total_volume', 'N/A')),
            data_points=str(data.get('data_points', 'N/A')),
            start_time=data.get('start_time', 'N/A'),
            end_time=data.get('end_time', 'N/A'),
            high_price=data.get('high_price', 'N/A'),
            low_price=data.get('low_price', 'N/A'),
            avg_price=data.get('avg_price', 'N/A')
        )
        
        # Luu bao cao
        report_file = f"stock_analysis/{symbol}/reports/{symbol}_intraday_report.html"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"OK Bao cao intraday da tao: {report_file}")
        return True
        
    except Exception as e:
        print(f"ERROR Loi tao bao cao: {str(e)}")
        return False

def intraday_analysis(symbol):
    """Workflow phân tích intraday nhanh"""
    
    print("="*50)
    print(f"DOMINUS INTRADAY ANALYSIS: {symbol}")
    print("="*50)
    
    # BƯỚC 1: Cập nhật dữ liệu intraday (skipped - data already available)
    log_step(1, "Cap nhat du lieu intraday - SKIPPED")
    # if not run_command(f"python quick_update.py {symbol}", 
    #                   f"Cap nhat {symbol}"):
    #     return False
    
    # BƯỚC 2: Tạo 3 biểu đồ cơ bản (charts already created)
    log_step(2, "Tao bieu do co ban - SKIPPED")
    # chart_script = f"stock_analysis/{symbol}/analysis/create_{symbol.lower()}_charts.py"
    # if os.path.exists(chart_script):
    #     run_command(f"python {chart_script}", "Tao key charts")
    # else:
    #     print(f"WARNING: Script khong ton tai: {chart_script}")
    
    # BƯỚC 3: Tạo báo cáo intraday
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
        print("Usage: python automation/intraday_analysis.py [SYMBOL]")
        print("Example: python automation/intraday_analysis.py VHM")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    
    start_time = time.time()
    success = intraday_analysis(symbol)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"\nTime: {duration:.1f} seconds")
    
    if success:
        print(f"OK {symbol} INTRADAY ANALYSIS SUCCESS!")
    else:
        print(f"ERROR {symbol} INTRADAY ANALYSIS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()