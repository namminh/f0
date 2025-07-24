#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOMINUS AGENT - Comprehensive Stock Analysis
Workflow tối ưu: MỘT LỆNH DUY NHẤT cho phân tích hoàn chỉnh

Usage: python automation/comprehensive_stock_analysis.py [SYMBOL]
Output: stock_analysis/[SYMBOL]/reports/[SYMBOL]_comprehensive_report.html
"""

import shutil
import sys
import os
import subprocess
import time
from pathlib import Path

def log_step(step, message):
    """Log tiến trình"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] STEP {step}: {message}")

def run_command(command, description):
    """Chạy lệnh với error handling"""
    try:
        log_step("CMD", f"{description}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        # Always print stdout for debugging purposes
        if result.stdout:
            print("--- Child Script STDOUT ---")
            print(result.stdout.strip())
            print("--- End Child Script STDOUT ---")

        if result.returncode == 0:
            print(f"SUCCESS: {description}")
            return True
        else:
            print(f"FAILED: {description}")
            if result.stderr:
                print("--- Child Script STDERR ---")
                print(result.stderr.strip())
                print("--- End Child Script STDERR ---")
            return False
    except Exception as e:
        print(f"ERROR: {description} - {str(e)}")
        return False

def check_and_create_structure(symbol):
    """Kiểm tra và tạo cấu trúc thư mục cho symbol"""
    base_path = Path(f"stock_analysis/{symbol}")
    
    # Tạo các thư mục cần thiết
    directories = [
        "data",
        "charts/key_charts",
        "charts/technical_analysis", 
        "charts/financial_analysis",
        "charts/additional_analysis",
        "analysis",
        "reports"
    ]
    
    for dir_path in directories:
        (base_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    return base_path.exists()

def comprehensive_analysis(symbol):
    """Workflow phân tích comprehensive hoàn chỉnh"""
    
    print("="*60)
    print(f"DOMINUS COMPREHENSIVE ANALYSIS: {symbol}")
    print("="*60)
    
    # BUOC 1: Kiem tra va tao cau truc
    log_step(1, "Kiem tra cau truc thu muc")
    if not check_and_create_structure(symbol):
        print("Khong the tao cau truc thu muc")
        return False
    
    # BUOC 2: Lay du lieu (neu chua co)
    data_file = f"stock_analysis/{symbol}/data/{symbol}_intraday_data.json"
    if not os.path.exists(data_file):
        log_step(2, "Lay du lieu ban dau")
        if not run_command(f"python get_data_for_stock.py {symbol}", 
                          f"Lay du lieu cho {symbol}"):
            return False
    else:
        log_step(2, "Cap nhat du lieu intraday")
        run_command(f"python quick_update.py {symbol}", 
                   f"Cap nhat {symbol}")
    
    # BUOC 3: Tao cac script analysis (neu chua co)
    analysis_path = f"stock_analysis/{symbol}/analysis"
    scripts = [
        f"analyze_{symbol.lower()}_data.py",
        f"create_{symbol.lower()}_charts.py",
        f"create_enhanced_{symbol.lower()}_charts.py", 
        f"create_financial_charts.py",
        f"create_additional_charts.py"
    ]
    
    log_step(3, "Kiem tra analysis scripts")
    for script in scripts:
        if not os.path.exists(f"{analysis_path}/{script}"):
            print(f"WARNING: Missing script: {script}")
    
    # BUOC 4: Tao tat ca bieu do
    log_step(4, "Tao bieu do comprehensive")
    
    chart_commands = [
        (f"python stock_analysis/{symbol}/analysis/create_{symbol.lower()}_charts.py", 
         "3 Key Charts"),
        (f"python stock_analysis/{symbol}/analysis/create_enhanced_{symbol.lower()}_charts.py",
         "5 Technical Charts"),
        (f"python stock_analysis/{symbol}/analysis/create_financial_charts.py",
         "5 Financial Charts"), 
        (f"python stock_analysis/{symbol}/analysis/create_additional_charts.py",
         "5 Additional Charts")
    ]
    
    success_count = 0
    for cmd, desc in chart_commands:
        if run_command(cmd, desc):
            success_count += 1
    
    print(f"Bieu do hoan thanh: {success_count}/4 nhom")
    
    # BUOC 5: Tao bao cao comprehensive
    log_step(5, "Tao bao cao comprehensive")
    
    # Tạo enhanced report trước
    run_command(f"python automation/enhanced_report_generator.py {symbol}",
               "Tao enhanced report")
    
    # Tích hợp biểu đồ vào báo cáo
    run_command(f"python automation/integrate_charts_to_report.py {symbol}",
               "Tich hop bieu do")
    
    # BUOC 6: Copy bao cao vao vi tri chuan
    log_step(6, "To chuc bao cao cuoi cung")
    
    # Copy từ enhanced_reports về stock_analysis
    enhanced_report = f"enhanced_reports/{symbol}_enhanced_investment_report.html"
    final_report = f"stock_analysis/{symbol}/reports/{symbol}_comprehensive_report.html"
    
    if os.path.exists(enhanced_report):
        log_step("CMD", "Copy bao cao chinh")
        shutil.copy(enhanced_report, final_report)
    else:
        print(f"ERROR: Intermediate report file not found at {enhanced_report}")
    
    # Kiểm tra kết quả cuối cùng
    if os.path.exists(final_report):
        print("="*60)
        print("COMPREHENSIVE ANALYSIS HOÀN THÀNH!")
        print(f"Bao cao: {final_report}")
        print(f"Bieu do: stock_analysis/{symbol}/charts/")
        print("="*60)
        return True
    else:
        print("Khong tao duoc bao cao cuoi cung")
        return False

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python automation/comprehensive_stock_analysis.py [SYMBOL]")
        print("Example: python automation/comprehensive_stock_analysis.py VHM")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    
    start_time = time.time()
    success = comprehensive_analysis(symbol)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"\nThoi gian thuc hien: {duration:.1f} giay")
    
    if success:
        print(f"{symbol} COMPREHENSIVE ANALYSIS THANH CONG!")
    else:
        print(f"{symbol} COMPREHENSIVE ANALYSIS THAT BAI!")
        sys.exit(1)

if __name__ == "__main__":
    main()