#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOMINUS AGENT - Quick Stock Analysis
Wrapper script cho Enhanced Stock Analyzer

Usage: python quick_analyze.py [SYMBOL]
Example: python quick_analyze.py VIX
"""

import sys
import subprocess
import os
import codecs
from pathlib import Path

# Fix encoding for Windows
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("USAGE: python quick_analyze.py [SYMBOL]")
        print("EXAMPLE: python quick_analyze.py VIX")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    
    print(f"TARGET: Khoi dong phan tich co phieu {symbol}...")
    
    # Check if data exists
    data_path = Path(f"stock_analysis/{symbol}/data/{symbol}_intraday_data.json")
    if not data_path.exists():
        print(f"WARNING: Chua co du lieu cho {symbol}")
        print(f"LOADING: Dang tai du lieu...")
        
        # Try to get data first
        result = subprocess.run([
            sys.executable, "quick_update.py", symbol
        ], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"ERROR: Khong the tai du lieu cho {symbol}")
            if result.stdout:
                print("STDOUT:", result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            sys.exit(1)
        else:
            print(f"SUCCESS: Da cap nhat du lieu cho {symbol}")
    
    # Run enhanced analyzer
    print(f"RUNNING: Chay phan tich nang cao...")
    result = subprocess.run([
        sys.executable, "automation/enhanced_stock_analyzer.py", symbol
    ], text=True, encoding='utf-8')
    
    if result.returncode == 0:
        report_path = f"stock_analysis/{symbol}/reports/{symbol}_enhanced_report.html"
        if Path(report_path).exists():
            print(f"\nSUCCESS: HOAN THANH!")
            print(f"REPORT: {report_path}")
            print(f"URL: file:///{Path(report_path).absolute()}")
        else:
            print(f"WARNING: Bao cao chua duoc tao")
    else:
        print(f"ERROR: Loi trong qua trinh phan tich")
        sys.exit(1)

if __name__ == "__main__":
    main()