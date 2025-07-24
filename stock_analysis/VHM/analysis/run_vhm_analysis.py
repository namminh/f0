#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stock_data_collector import StockDataCollector
import json

def main():
    # Khởi tạo collector
    collector = StockDataCollector(data_source='VCI')
    
    # Lấy báo cáo tài chính VHM
    print('Dang lay bao cao tai chinh VHM...')
    
    # Thu thập dữ liệu
    results = {}
    symbol = 'VHM'
    
    # Lấy thông tin tổng quan
    print('1. Lay thong tin tong quan...')
    results['company_overview'] = collector.get_company_overview(symbol)
    
    # Lấy bảng cân đối kế toán
    print('2. Lay bang can doi ke toan...')
    results['balance_sheet'] = collector.get_financial_statements(symbol, 'balance_sheet')
    
    # Lấy báo cáo kết quả kinh doanh
    print('3. Lay bao cao ket qua kinh doanh...')
    results['income_statement'] = collector.get_financial_statements(symbol, 'income_statement')
    
    # Lấy báo cáo lưu chuyển tiền tệ
    print('4. Lay bao cao luu chuyen tien te...')
    results['cash_flow'] = collector.get_financial_statements(symbol, 'cash_flow')
    
    # Lấy chỉ số tài chính
    print('5. Lay chi so tai chinh...')
    results['financial_ratios'] = collector.get_financial_ratios(symbol)
    
    # Lưu kết quả
    with open('VHM_financial_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print('Hoan thanh! Du lieu da duoc luu vao VHM_financial_data.json')
    
    # In tóm tắt
    print("\n=== TOM TAT KET QUA ===")
    for key, value in results.items():
        if 'error' in value:
            print(f"{key}: LOI - {value['error']}")
        else:
            print(f"{key}: THANH CONG - {len(value.get('data', []))} records")

if __name__ == "__main__":
    main()