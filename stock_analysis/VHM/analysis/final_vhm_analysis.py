#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sys
import os

def comprehensive_vhm_analysis():
    """Phân tích toàn diện VHM với dữ liệu thực tế"""
    
    # Đọc dữ liệu
    with open('VHM_financial_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 80)
    print("PHAN TICH TOAN DIEN VINHOMES (VHM) - 2024")
    print("=" * 80)
    
    # 1. Thông tin cơ bản
    overview = data['company_overview']['data']
    print("\n1. THONG TIN CO BAN:")
    print(f"   - Ten cong ty: {overview.get('symbol', 'VHM')} - Vinhomes")
    print(f"   - Von dieu le: {overview.get('charter_capital', 0):,} VND")
    print(f"   - So co phieu luu hanh: {overview.get('issue_share', 0):,} co phieu")
    print(f"   - Gia tri tren co phieu: {overview.get('charter_capital', 0) / overview.get('issue_share', 1):,.0f} VND")
    print(f"   - Nganh: Bat dong san")
    
    # 2. Phân tích bảng cân đối kế toán
    print("\n2. PHAN TICH BANG CAN DOI KE TOAN:")
    balance_sheet = data['balance_sheet']['data']
    
    # Dữ liệu năm 2024
    data_2024 = balance_sheet[0]  # Năm 2024
    data_2023 = balance_sheet[1]  # Năm 2023
    
    # Các chỉ tiêu chính 2024
    total_assets_2024 = data_2024.get('TỔNG CỘNG TÀI SẢN (đồng)', 0)
    current_assets_2024 = data_2024.get('TÀI SẢN NGẮN HẠN (đồng)', 0)
    long_term_assets_2024 = data_2024.get('TÀI SẢN DÀI HẠN (đồng)', 0)
    total_liabilities_2024 = data_2024.get('NỢ PHẢI TRẢ (đồng)', 0)
    owner_equity_2024 = data_2024.get('VỐN CHỦ SỞ HỮU (đồng)', 0)
    cash_2024 = data_2024.get('Tiền và tương đương tiền (đồng)', 0)
    inventory_2024 = data_2024.get('Hàng tồn kho ròng', 0)
    
    # Các chỉ tiêu chính 2023
    total_assets_2023 = data_2023.get('TỔNG CỘNG TÀI SẢN (đồng)', 0)
    current_assets_2023 = data_2023.get('TÀI SẢN NGẮN HẠN (đồng)', 0)
    total_liabilities_2023 = data_2023.get('NỢ PHẢI TRẢ (đồng)', 0)
    owner_equity_2023 = data_2023.get('VỐN CHỦ SỞ HỮU (đồng)', 0)
    cash_2023 = data_2023.get('Tiền và tương đương tiền (đồng)', 0)
    
    print("   CAC CHI TIEU CHINH (2024):")
    print(f"   - Tong tai san: {total_assets_2024:,} VND ({total_assets_2024/1000000000000:.1f} nghin ty)")
    print(f"   - Tai san ngan han: {current_assets_2024:,} VND ({current_assets_2024/total_assets_2024*100:.1f}%)")
    print(f"   - Tai san dai han: {long_term_assets_2024:,} VND ({long_term_assets_2024/total_assets_2024*100:.1f}%)")
    print(f"   - Tong no phai tra: {total_liabilities_2024:,} VND ({total_liabilities_2024/total_assets_2024*100:.1f}%)")
    print(f"   - Von chu so huu: {owner_equity_2024:,} VND ({owner_equity_2024/total_assets_2024*100:.1f}%)")
    print(f"   - Tien mat va tuong duong: {cash_2024:,} VND")
    print(f"   - Hang ton kho: {inventory_2024:,} VND")
    
    print("\n   SO SANH VOI NAM 2023:")
    
    # Tính tăng trưởng
    asset_growth = ((total_assets_2024 - total_assets_2023) / total_assets_2023) * 100
    equity_growth = ((owner_equity_2024 - owner_equity_2023) / owner_equity_2023) * 100
    debt_growth = ((total_liabilities_2024 - total_liabilities_2023) / total_liabilities_2023) * 100
    cash_growth = ((cash_2024 - cash_2023) / cash_2023) * 100
    
    print(f"   - Tang truong tai san: {asset_growth:+.1f}%")
    print(f"   - Tang truong von chu so huu: {equity_growth:+.1f}%")
    print(f"   - Tang truong no phai tra: {debt_growth:+.1f}%")
    print(f"   - Tang truong tien mat: {cash_growth:+.1f}%")
    
    # 3. Phân tích báo cáo kết quả kinh doanh
    print("\n3. PHAN TICH BAO CAO KET QUA KINH DOANH:")
    income_statement = data['income_statement']['data']
    
    # Tìm các chỉ tiêu quan trọng
    revenue_2024 = None
    revenue_2023 = None
    net_profit_2024 = None
    net_profit_2023 = None
    
    for item in income_statement:
        metric = str(item.get('Financial_Metric', ''))
        if 'doanh thu' in metric.lower() or 'thuần' in metric.lower():
            revenue_2024 = item.get('2024', 0)
            revenue_2023 = item.get('2023', 0)
        elif 'lợi nhuận sau thuế' in metric.lower() or 'lợi nhuận ròng' in metric.lower():
            net_profit_2024 = item.get('2024', 0)
            net_profit_2023 = item.get('2023', 0)
    
    # Hiển thị một số chỉ tiêu từ dữ liệu
    print("   CAC CHI TIEU KINH DOANH CHINH:")
    for item in income_statement[:5]:  # Lấy 5 chỉ tiêu đầu
        metric = str(item.get('Financial_Metric', ''))
        val_2024 = item.get('2024', 0)
        val_2023 = item.get('2023', 0)
        
        if val_2024 is not None and val_2024 != 0:
            print(f"   - {metric}:")
            print(f"     + 2024: {val_2024:,} VND")
            if val_2023 is not None and val_2023 != 0:
                growth = ((val_2024 - val_2023) / val_2023) * 100
                print(f"     + 2023: {val_2023:,} VND")
                print(f"     + Tang truong: {growth:+.1f}%")
    
    # 4. Phân tích chỉ số tài chính
    print("\n4. PHAN TICH CHI SO TAI CHINH:")
    financial_ratios = data['financial_ratios']['data']
    
    print("   CAC CHI SO QUAN TRONG:")
    for ratio in financial_ratios:
        ratio_name = str(ratio.get('Ratio_Name', ''))
        val_2024 = ratio.get('2024', 'N/A')
        val_2023 = ratio.get('2023', 'N/A')
        
        # Chỉ hiển thị một số chỉ số quan trọng
        if any(keyword in ratio_name.lower() for keyword in ['roe', 'roa', 'eps', 'p/e', 'debt', 'current']):
            print(f"   - {ratio_name}:")
            print(f"     + 2024: {val_2024}")
            if val_2023 != 'N/A':
                print(f"     + 2023: {val_2023}")
    
    # 5. Nhận định chi tiết
    print("\n" + "=" * 80)
    print("NHAN DINH CHI TIET VA DANH GIA")
    print("=" * 80)
    
    print("\n5.1 DANH GIA QUY MO VA VI THE:")
    print("   - Vinhomes la cong ty phat trien bat dong san hang dau Viet Nam")
    print(f"   - Quy mo tai san: {total_assets_2024/1000000000000:.1f} nghin ty VND")
    print(f"   - Von chu so huu: {owner_equity_2024/1000000000000:.1f} nghin ty VND")
    print(f"   - Von hoa thi truong uoc tinh: Rat lon trong nganh BDS")
    
    print("\n5.2 DANH GIA CAU TRUC TAI CHINH:")
    debt_ratio = (total_liabilities_2024 / total_assets_2024) * 100
    print(f"   - Ty le no/tai san: {debt_ratio:.1f}%")
    
    if debt_ratio > 70:
        print("   - NHAN DINH: Ty le no cao, rui ro tai chinh")
    elif debt_ratio > 50:
        print("   - NHAN DINH: Ty le no trung binh, can theo doi")
    else:
        print("   - NHAN DINH: Cau truc tai chinh on dinh")
    
    print("\n5.3 DANH GIA THANH KHOAN:")
    cash_ratio = (cash_2024 / current_assets_2024) * 100
    print(f"   - Ty le tien mat/tai san ngan han: {cash_ratio:.1f}%")
    print(f"   - Tang truong tien mat: {cash_growth:+.1f}%")
    
    if cash_growth > 50:
        print("   - NHAN DINH: Thanh khoan cai thien manh, tich cuc")
    elif cash_growth > 0:
        print("   - NHAN DINH: Thanh khoan cai thien")
    else:
        print("   - NHAN DINH: Thanh khoan giam, can chu y")
    
    print("\n5.4 DANH GIA HIEU QUA KINH DOANH:")
    print(f"   - Tang truong tai san: {asset_growth:+.1f}%")
    print(f"   - Tang truong von chu so huu: {equity_growth:+.1f}%")
    
    if asset_growth > 15:
        print("   - NHAN DINH: Tang truong tai san manh")
    elif asset_growth > 5:
        print("   - NHAN DINH: Tang truong tai san on dinh")
    else:
        print("   - NHAN DINH: Tang truong tai san cham")
    
    print("\n5.5 DANH GIA TONG THE:")
    print("\n   DIEM MANH:")
    print("   + Vi tri dan dau trong nganh bat dong san")
    print("   + Quy mo tai san lon va tang truong")
    print("   + Danh muc du an phong phu tren ca nuoc")
    print("   + Thuong hieu uy tin va chat luong")
    print("   + Thanh khoan cai thien ro ret")
    
    print("\n   DIEM YEU VA RUI RO:")
    print("   + Phu thuoc vao chu ky thi truong BDS")
    print("   + Ty le no cao, rui ro tai chinh")
    print("   + Canh tranh gay gat trong nganh")
    print("   + Rui ro chinh sach va phap ly")
    print("   + Chu ky dau tu dai, hoi von lon")
    
    print("\n   KHUYEN NGHI DAU TU:")
    print("   + PHU HOP CHO: Nha dau tu dai han, chiu duoc rui ro")
    print("   + THEO DOI: Chi so thanh khoan, ty le no, tien do du an")
    print("   + CHU Y: Bien dong thi truong BDS va chinh sach")
    print("   + DANH GIA: Trung binh -> Tich cuc (tuy thuoc vao thi truong)")
    
    print("\n" + "=" * 80)
    print("KET THUC PHAN TICH TOAN DIEN VHM")
    print("=" * 80)

if __name__ == "__main__":
    comprehensive_vhm_analysis()