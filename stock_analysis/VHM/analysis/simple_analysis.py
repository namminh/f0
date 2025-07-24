#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

def analyze_vhm():
    with open('../data/VHM_financial_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=== PHAN TICH DU LIEU TAI CHINH VINHOMES (VHM) ===")
    print()
    
    # 1. Thong tin tong quan
    print("1. THONG TIN TONG QUAN:")
    overview = data['company_overview']['data']
    print(f"   - Ten cong ty: Vinhomes")
    print(f"   - Ma chung khoan: {overview['symbol']}")
    print(f"   - Von dieu le: {overview['charter_capital']:,} VND")
    print(f"   - So co phieu luu hanh: {overview['issue_share']:,} co phieu")
    print(f"   - Nganh: Bat dong san")
    
    # 2. Phan tich bang can doi ke toan
    print()
    print("2. PHAN TICH BANG CAN DOI KE TOAN (2024):")
    balance_sheet = data['balance_sheet']['data']
    current_year = balance_sheet[0]
    
    # Lay cac gia tri quan trong
    total_assets = current_year.get('TONG CONG TAI SAN (dong)', 0)
    current_assets = current_year.get('TAI SAN NGAN HAN (dong)', 0)
    long_term_assets = current_year.get('TAI SAN DAI HAN (dong)', 0)
    total_liabilities = current_year.get('NO PHAI TRA (dong)', 0)
    owner_equity = current_year.get('VON CHU SO HUU (dong)', 0)
    
    # Neu khong co key chinh xac, tim key tuong tu
    if total_assets == 0:
        for key in current_year.keys():
            if 'TONG' in key and 'TAI SAN' in key:
                total_assets = current_year[key]
                break
    
    if current_assets == 0:
        for key in current_year.keys():
            if 'TAI SAN' in key and 'NGAN HAN' in key:
                current_assets = current_year[key]
                break
    
    if long_term_assets == 0:
        for key in current_year.keys():
            if 'TAI SAN' in key and 'DAI HAN' in key:
                long_term_assets = current_year[key]
                break
    
    if total_liabilities == 0:
        for key in current_year.keys():
            if 'NO' in key and 'TRA' in key:
                total_liabilities = current_year[key]
                break
    
    if owner_equity == 0:
        for key in current_year.keys():
            if 'VON' in key and 'CHU' in key:
                owner_equity = current_year[key]
                break
    
    print(f"   - Tong tai san: {total_assets:,} VND")
    print(f"   - Tai san ngan han: {current_assets:,} VND ({current_assets/total_assets*100:.1f}%)")
    print(f"   - Tai san dai han: {long_term_assets:,} VND ({long_term_assets/total_assets*100:.1f}%)")
    print(f"   - Tong no phai tra: {total_liabilities:,} VND")
    print(f"   - Von chu so huu: {owner_equity:,} VND")
    print(f"   - Ty le no/tong tai san: {total_liabilities/total_assets*100:.1f}%")
    
    # 3. Phan tich bao cao ket qua kinh doanh
    print()
    print("3. PHAN TICH BAO CAO KET QUA KINH DOANH:")
    income_statement = data['income_statement']['data']
    
    for item in income_statement:
        metric = str(item['Financial_Metric'])
        if 'doanh thu' in metric.lower() or 'net sales' in metric.lower():
            if '2024' in item and item['2024'] is not None:
                print(f"   - {metric}: {item['2024']:,} VND")
        elif 'loi nhuan' in metric.lower() or 'profit' in metric.lower():
            if '2024' in item and item['2024'] is not None:
                print(f"   - {metric}: {item['2024']:,} VND")
    
    # 4. Phan tich chi so tai chinh
    print()
    print("4. PHAN TICH CHI SO TAI CHINH:")
    financial_ratios = data['financial_ratios']['data']
    
    important_ratios = ['ROE', 'ROA', 'EPS', 'P/E', 'P/B']
    
    for ratio in financial_ratios:
        ratio_name = str(ratio['Ratio_Name'])
        for important in important_ratios:
            if important.lower() in ratio_name.lower():
                if '2024' in ratio and ratio['2024'] is not None:
                    print(f"   - {ratio_name}: {ratio['2024']}")
                break
    
    # 5. Danh gia chung
    print()
    print("5. DANH GIA CHUNG:")
    debt_ratio = total_liabilities / total_assets * 100
    if debt_ratio > 60:
        debt_assessment = "Cao"
    elif debt_ratio > 40:
        debt_assessment = "Trung binh"
    else:
        debt_assessment = "Thap"
    
    print(f"   - Ty le no: {debt_ratio:.1f}% ({debt_assessment})")
    
    current_asset_ratio = current_assets / total_assets * 100
    if current_asset_ratio > 60:
        asset_structure = "Chu yeu tai san ngan han"
    else:
        asset_structure = "Can bang tai san ngan han va dai han"
    
    print(f"   - Cau truc tai san: {asset_structure}")
    print(f"   - Quy mo: Doanh nghiep lon voi tong tai san {total_assets/1000000000000:.1f} nghin ty VND")
    
    print()
    print("=== KET THUC PHAN TICH ===")

if __name__ == "__main__":
    analyze_vhm()