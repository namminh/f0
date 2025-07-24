#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import pandas as pd
from datetime import datetime

def detailed_vhm_analysis():
    """Phân tích chi tiết dữ liệu tài chính VHM và đưa ra nhận định"""
    
    # Đọc dữ liệu
    with open('VHM_financial_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 80)
    print("PHAN TICH CHI TIET TAI CHINH VINHOMES (VHM)")
    print("=" * 80)
    
    # 1. Thông tin tổng quan
    print("\n1. THONG TIN TONG QUAN:")
    overview = data['company_overview']['data']
    print(f"   - Ten cong ty: Vinhomes")
    print(f"   - Ma chung khoan: {overview['symbol']}")
    print(f"   - Von dieu le: {overview['charter_capital']:,} VND")
    print(f"   - So co phieu luu hanh: {overview['issue_share']:,} co phieu")
    print(f"   - Gia tri tren co phieu: {overview['charter_capital']/overview['issue_share']:,.0f} VND/co phieu")
    print(f"   - Nganh: Bat dong san")
    
    # 2. Phân tích bảng cân đối kế toán chi tiết
    print("\n2. PHAN TICH BANG CAN DOI KE TOAN CHI TIET:")
    balance_sheet = data['balance_sheet']['data']
    
    # Tạo DataFrame từ dữ liệu
    df_balance = pd.DataFrame(balance_sheet)
    
    # Lấy dữ liệu năm 2024 và 2023 để so sánh
    recent_years = []
    for _, row in df_balance.iterrows():
        if 'Nam' in row and row['Nam'] == 2024:
            recent_years.append(('2024', row))
        elif 'Nam' in row and row['Nam'] == 2023:
            recent_years.append(('2023', row))
    
    if len(recent_years) >= 2:
        year_2024 = recent_years[0][1]
        year_2023 = recent_years[1][1]
        
        # Các chỉ tiêu quan trọng
        key_metrics = [
            'TONG CONG TAI SAN (dong)',
            'TAI SAN NGAN HAN (dong)', 
            'TAI SAN DAI HAN (dong)',
            'NO PHAI TRA (dong)',
            'VON CHU SO HUU (dong)',
            'Tien va tuong duong tien (dong)',
            'Hang ton kho rong'
        ]
        
        print("   CAC CHI TIEU CHINH (2024 vs 2023):")
        for metric in key_metrics:
            if metric in year_2024 and metric in year_2023:
                val_2024 = year_2024[metric] if year_2024[metric] is not None else 0
                val_2023 = year_2023[metric] if year_2023[metric] is not None else 0
                
                if val_2023 != 0:
                    growth = ((val_2024 - val_2023) / val_2023) * 100
                    print(f"   - {metric}:")
                    print(f"     + 2024: {val_2024:,} VND")
                    print(f"     + 2023: {val_2023:,} VND")
                    print(f"     + Tang truong: {growth:+.1f}%")
                else:
                    print(f"   - {metric}: {val_2024:,} VND (2024)")
    
    # 3. Phân tích báo cáo kết quả kinh doanh
    print("\n3. PHAN TICH BAO CAO KET QUA KINH DOANH:")
    income_statement = data['income_statement']['data']
    
    print("   CAC CHI TIEU DOANH THU VA LOI NHUAN:")
    for item in income_statement:
        metric = str(item['Financial_Metric'])
        if any(keyword in metric.lower() for keyword in ['doanh thu', 'revenue', 'sales']):
            if '2024' in item and item['2024'] is not None:
                val_2024 = item['2024']
                val_2023 = item.get('2023', 0) if item.get('2023') is not None else 0
                
                print(f"   - {metric}:")
                print(f"     + 2024: {val_2024:,} VND")
                if val_2023 != 0:
                    growth = ((val_2024 - val_2023) / val_2023) * 100
                    print(f"     + 2023: {val_2023:,} VND")
                    print(f"     + Tang truong: {growth:+.1f}%")
        
        elif any(keyword in metric.lower() for keyword in ['loi nhuan', 'profit', 'net income']):
            if '2024' in item and item['2024'] is not None:
                val_2024 = item['2024']
                val_2023 = item.get('2023', 0) if item.get('2023') is not None else 0
                
                print(f"   - {metric}:")
                print(f"     + 2024: {val_2024:,} VND")
                if val_2023 != 0:
                    growth = ((val_2024 - val_2023) / val_2023) * 100
                    print(f"     + 2023: {val_2023:,} VND")
                    print(f"     + Tang truong: {growth:+.1f}%")
    
    # 4. Phân tích chỉ số tài chính
    print("\n4. PHAN TICH CHI SO TAI CHINH:")
    financial_ratios = data['financial_ratios']['data']
    
    important_ratios = {
        'roe': 'ROE (Return on Equity)',
        'roa': 'ROA (Return on Assets)', 
        'eps': 'EPS (Earnings per Share)',
        'pe': 'P/E (Price to Earnings)',
        'pb': 'P/B (Price to Book)',
        'debt': 'Debt Ratio',
        'current': 'Current Ratio',
        'quick': 'Quick Ratio'
    }
    
    print("   CAC CHI SO TAI CHINH QUAN TRONG:")
    for ratio in financial_ratios:
        ratio_name = str(ratio['Ratio_Name']).lower()
        
        for key, display_name in important_ratios.items():
            if key in ratio_name:
                val_2024 = ratio.get('2024', 'N/A')
                val_2023 = ratio.get('2023', 'N/A')
                
                print(f"   - {display_name}:")
                print(f"     + 2024: {val_2024}")
                if val_2023 != 'N/A':
                    print(f"     + 2023: {val_2023}")
                break
    
    # 5. Phân tích cash flow
    print("\n5. PHAN TICH LUU CHUYEN TIEN TE:")
    cash_flow = data['cash_flow']['data']
    
    cash_flow_items = [
        'Luu chuyen tien tu hoat dong kinh doanh',
        'Luu chuyen tien tu hoat dong dau tu', 
        'Luu chuyen tien tu hoat dong tai chinh',
        'Luu chuyen tien thuan trong ky'
    ]
    
    for item in cash_flow:
        metric = str(item['Financial_Metric'])
        for cf_item in cash_flow_items:
            if any(word in metric.lower() for word in cf_item.lower().split()):
                if '2024' in item and item['2024'] is not None:
                    val_2024 = item['2024']
                    val_2023 = item.get('2023', 0) if item.get('2023') is not None else 0
                    
                    print(f"   - {metric}:")
                    print(f"     + 2024: {val_2024:,} VND")
                    if val_2023 != 0:
                        print(f"     + 2023: {val_2023:,} VND")
                break
    
    # 6. Nhận định và đánh giá
    print("\n" + "=" * 80)
    print("NHAN DINH VA DANH GIA CHI TIET")
    print("=" * 80)
    
    # Tính toán các chỉ số từ dữ liệu
    if len(recent_years) >= 2:
        year_2024 = recent_years[0][1]
        
        total_assets = year_2024.get('TONG CONG TAI SAN (dong)', 0)
        total_liabilities = year_2024.get('NO PHAI TRA (dong)', 0)
        owner_equity = year_2024.get('VON CHU SO HUU (dong)', 0)
        current_assets = year_2024.get('TAI SAN NGAN HAN (dong)', 0)
        
        print("\n6.1 DANH GIA VE QUY MO VA VI THE:")
        print(f"   - Vinhomes la DN bat dong san lon nhat Viet Nam")
        print(f"   - Tong tai san: {total_assets:,} VND (~{total_assets/1000000000000:.1f} nghin ty)")
        print(f"   - Von chu so huu: {owner_equity:,} VND (~{owner_equity/1000000000000:.1f} nghin ty)")
        print(f"   - Quy mo von dieu le gan 41.1 nghin ty VND")
        
        print("\n6.2 DANH GIA VE CAU TRUC TAI CHINH:")
        if total_assets > 0:
            debt_ratio = (total_liabilities / total_assets) * 100
            equity_ratio = (owner_equity / total_assets) * 100
            
            print(f"   - Ty le no/tong tai san: {debt_ratio:.1f}%")
            print(f"   - Ty le von chu so huu: {equity_ratio:.1f}%")
            
            if debt_ratio > 60:
                print("   - NHAN DINH: Ty le no cao, can chu y rui ro tai chinh")
            elif debt_ratio > 40:
                print("   - NHAN DINH: Ty le no o muc hop ly")
            else:
                print("   - NHAN DINH: Cau truc tai chinh manh, ty le no thap")
        
        print("\n6.3 DANH GIA VE THANH KHOAN:")
        if current_assets > 0:
            current_asset_ratio = (current_assets / total_assets) * 100
            print(f"   - Ty le tai san ngan han: {current_asset_ratio:.1f}%")
            
            if current_asset_ratio > 60:
                print("   - NHAN DINH: Cau truc tai san linh hoat, thanh khoan tot")
            else:
                print("   - NHAN DINH: Can bang giua tai san ngan han va dai han")
    
    print("\n6.4 DANH GIA VE HIEU QUA KINH DOANH:")
    
    # Tìm ROE và ROA
    roe_value = None
    roa_value = None
    eps_value = None
    
    for ratio in financial_ratios:
        ratio_name = str(ratio['Ratio_Name']).lower()
        if 'roe' in ratio_name:
            roe_value = ratio.get('2024', None)
        elif 'roa' in ratio_name:
            roa_value = ratio.get('2024', None)
        elif 'eps' in ratio_name:
            eps_value = ratio.get('2024', None)
    
    if roe_value is not None:
        print(f"   - ROE 2024: {roe_value}%")
        try:
            roe_float = float(roe_value)
            if roe_float > 15:
                print("   - NHAN DINH: ROE cao, hieu qua su dung von chu so huu tot")
            elif roe_float > 10:
                print("   - NHAN DINH: ROE o muc trung binh tot")
            else:
                print("   - NHAN DINH: ROE thap, can cai thien hieu qua")
        except:
            print("   - NHAN DINH: Can xem xet chi tiet gia tri ROE")
    
    if roa_value is not None:
        print(f"   - ROA 2024: {roa_value}%")
        try:
            roa_float = float(roa_value)
            if roa_float > 5:
                print("   - NHAN DINH: ROA tot, hieu qua su dung tai san cao")
            elif roa_float > 2:
                print("   - NHAN DINH: ROA o muc trung binh")
            else:
                print("   - NHAN DINH: ROA thap, can cai thien hieu qua tai san")
        except:
            print("   - NHAN DINH: Can xem xet chi tiet gia tri ROA")
    
    print("\n6.5 NHAN DINH TONG THE:")
    print("   - UU DIEM:")
    print("     + Vi tri dan dau thi truong bat dong san Viet Nam")
    print("     + Quy mo lon voi nhieu du an tren ca nuoc")
    print("     + Thuong hieu manh va uy tin cao")
    print("     + Danh muc du an da dang va chat luong")
    
    print("   - RUI RO CAN LUU Y:")
    print("     + Phu thuoc vao thi truong bat dong san")
    print("     + Chu ky kinh doanh dai")
    print("     + Rui ro tu chinh sach va luat phap")
    print("     + Canh tranh gay gat trong nganh")
    
    print("   - KHUYEN NGHI:")
    print("     + Theo doi tinh hinh thi truong bat dong san")
    print("     + Quan sat cac chi so thanh khoan")
    print("     + Danh gia hieu qua cac du an moi")
    print("     + Xem xet da dang hoa dau tu")
    
    print("\n" + "=" * 80)
    print("KET THUC PHAN TICH CHI TIET")
    print("=" * 80)

if __name__ == "__main__":
    detailed_vhm_analysis()