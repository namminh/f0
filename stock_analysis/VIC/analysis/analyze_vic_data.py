#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import pandas as pd
from datetime import datetime

def analyze_vic_financial_data():
    """Phân tích dữ liệu tài chính VIC"""
    
    # Đọc dữ liệu
    with open('VIC_financial_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=== PHAN TICH DU LIEU TAI CHINH VINGROUP (VIC) ===\n")
    
    # 1. Thong tin tong quan
    print("1. THONG TIN TONG QUAN:")
    overview = data['company_overview']['data']
    print(f"   - Ten cong ty: Tap Doan Vingroup")
    print(f"   - Ma chung khoan: {overview['symbol']}")
    print(f"   - Von dieu le: {overview['charter_capital']:,} VND")
    print(f"   - So co phieu luu hanh: {overview['issue_share']:,} co phieu")
    print(f"   - Nganh: {overview['icb_name3']}")
    print(f"   - Mo ta: {overview['company_profile'][:200]}...")
    
    # 2. Phan tich bang can doi ke toan
    print("\n2. PHAN TICH BANG CAN DOI KE TOAN (2024):")
    balance_sheet = data['balance_sheet']['data']
    current_year = balance_sheet[0]  # Nam 2024
    
    total_assets = current_year['TONG CONG TAI SAN (dong)']
    current_assets = current_year['TAI SAN NGAN HAN (dong)']
    long_term_assets = current_year['TAI SAN DAI HAN (dong)']
    total_liabilities = current_year['NO PHAI TRA (dong)']
    owner_equity = current_year['VON CHU SO HUU (dong)']
    
    print(f"   - Tong tai san: {total_assets:,} VND")
    print(f"   - Tai san ngan han: {current_assets:,} VND ({current_assets/total_assets*100:.1f}%)")
    print(f"   - Tai san dai han: {long_term_assets:,} VND ({long_term_assets/total_assets*100:.1f}%)")
    print(f"   - Tong no phai tra: {total_liabilities:,} VND")
    print(f"   - Von chu so huu: {owner_equity:,} VND")
    print(f"   - Ty le no/tong tai san: {total_liabilities/total_assets*100:.1f}%)")
    
    # 3. Phan tich bao cao ket qua kinh doanh
    print("\n3. PHAN TICH BAO CAO KET QUA KINH DOANH:")
    income_statement = data['income_statement']['data']
    
    # Tim cac chi tieu quan trong
    for item in income_statement:
        metric = item['Financial_Metric']
        if 'doanh thu' in str(metric).lower() or 'net sales' in str(metric).lower():
            print(f"   - {metric}: {item.get('2024', 'N/A'):,} VND")
        elif 'loi nhuan' in str(metric).lower() or 'profit' in str(metric).lower():
            print(f"   - {metric}: {item.get('2024', 'N/A'):,} VND")
    
    # 4. Phan tich chi so tai chinh
    print("\n4. PHAN TICH CHI SO TAI CHINH:")
    financial_ratios = data['financial_ratios']['data']
    
    important_ratios = [
        'ROE', 'ROA', 'EPS', 'P/E', 'P/B', 'Debt to Equity',
        'Current Ratio', 'Quick Ratio', 'Gross Margin', 'Net Margin'
    ]
    
    for ratio in financial_ratios:
        ratio_name = ratio['Ratio_Name']
        for important in important_ratios:
            if important.lower() in str(ratio_name).lower():
                print(f"   - {ratio_name}: {ratio.get('2024', 'N/A')}")
                break
    
    # 5. Phan tich xu huong (so sanh nam gan nhat)
    print("\n5. PHAN TICH XU HUONG:")
    
    # Tinh tang truong tai san
    if len(balance_sheet) > 1:
        prev_year = balance_sheet[1]  # Nam truoc
        prev_assets = prev_year['TONG CONG TAI SAN (dong)']
        asset_growth = ((total_assets - prev_assets) / prev_assets) * 100
        print(f"   - Tang truong tai san: {asset_growth:.1f}%")
    
    # 6. Danh gia chung
    print("\n6. DANH GIA CHUNG:")
    
    # Ty le no
    debt_ratio = total_liabilities / total_assets * 100
    if debt_ratio > 60:
        debt_assessment = "Cao"
    elif debt_ratio > 40:
        debt_assessment = "Trung binh"
    else:
        debt_assessment = "Thap"
    
    print(f"   - Ty le no: {debt_ratio:.1f}% ({debt_assessment})")
    
    # Cau truc tai san
    current_asset_ratio = current_assets / total_assets * 100
    if current_asset_ratio > 60:
        asset_structure = "Chu yeu tai san ngan han"
    else:
        asset_structure = "Can bang tai san ngan han va dai han"
    
    print(f"   - Cau truc tai san: {asset_structure}")
    
    # Quy mo
    print(f"   - Quy mo: Doanh nghiep lon voi tong tai san {total_assets/1000000000000:.1f} nghin ty VND")
    
    print("\n=== KET THUC PHAN TICH ===")

if __name__ == "__main__":
    analyze_vic_financial_data()
