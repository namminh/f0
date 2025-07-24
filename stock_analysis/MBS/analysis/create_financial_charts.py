#!/usr/bin/env python3
"""
Financial Analysis Charts for MBS
Tạo 5 biểu đồ phân tích tài chính cho MBS
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from datetime import datetime

# Set Vietnamese font
plt.rcParams['font.family'] = ['Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8')

def create_financial_charts():
    """Tạo 5 biểu đồ phân tích tài chính cho MBS"""
    
    # Create directory
    Path("stock_analysis/MBS/charts/financial_analysis").mkdir(parents=True, exist_ok=True)

    # Load data
    try:
        with open("stock_analysis/MBS/data/MBS_financial_ratios.json", "r", encoding="utf-8") as f:
            financial_ratios = json.load(f)
    except FileNotFoundError:
        financial_ratios = None
    
    try:
        with open("stock_analysis/MBS/data/MBS_balance_sheet.json", "r", encoding="utf-8") as f:
            balance_sheet = json.load(f)
    except FileNotFoundError:
        balance_sheet = None
    
    try:
        with open("stock_analysis/MBS/data/MBS_income_statement.json", "r", encoding="utf-8") as f:
            income_statement = json.load(f)
    except FileNotFoundError:
        income_statement = None

    # Create financial charts
    create_financial_health_dashboard(financial_ratios)
    create_profitability_analysis(financial_ratios, income_statement)
    create_banking_specific_metrics(financial_ratios)
    create_peer_comparison(financial_ratios)
    create_financial_trends(financial_ratios)
    
    print("Financial analysis charts created successfully")

def create_financial_health_dashboard(financial_ratios):
    """Tạo dashboard sức khỏe tài chính - ROE, ROA, P/E, P/B"""
    if not financial_ratios or 'data' not in financial_ratios:
        print("No financial ratios data available")
        return
    
    df = pd.DataFrame(financial_ratios['data'])
    if len(df) == 0:
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # ROE và ROA
    roe_col = 'Chỉ tiêu hiệu quả_ROE (%)'
    roa_col = 'Chỉ tiêu hiệu quả_ROA (%)'
    
    if roe_col in df.columns and roa_col in df.columns:
        years = range(len(df))
        roe_values = pd.to_numeric(df[roe_col], errors='coerce').fillna(0)
        roa_values = pd.to_numeric(df[roa_col], errors='coerce').fillna(0)
        
        ax1.plot(years, roe_values, marker='o', linewidth=3, label='ROE (%)', color='blue')
        ax1.plot(years, roa_values, marker='s', linewidth=3, label='ROA (%)', color='green')
        ax1.set_title('MBS - ROE & ROA', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Ty le (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    
    # P/E và P/B
    pe_col = 'Chỉ tiêu định giá_P/E'
    pb_col = 'Chỉ tiêu định giá_P/B'
    
    if pe_col in df.columns and pb_col in df.columns:
        pe_values = pd.to_numeric(df[pe_col], errors='coerce').fillna(0)
        pb_values = pd.to_numeric(df[pb_col], errors='coerce').fillna(0)
        
        ax2.bar(range(len(pe_values)), pe_values, alpha=0.7, label='P/E', color='orange')
        ax2_twin = ax2.twinx()
        ax2_twin.plot(range(len(pb_values)), pb_values, 'ro-', linewidth=2, label='P/B', color='red')
        ax2.set_title('MBS - P/E & P/B Ratios', fontsize=14, fontweight='bold')
        ax2.set_ylabel('P/E Ratio')
        ax2_twin.set_ylabel('P/B Ratio')
        ax2.legend(loc='upper left')
        ax2_twin.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
    
    # Current ratio và Quick ratio (nếu có)
    current_ratio_col = 'Chỉ tiêu thanh khoản_Current Ratio'
    if current_ratio_col in df.columns:
        current_values = pd.to_numeric(df[current_ratio_col], errors='coerce').fillna(0)
        ax3.bar(range(len(current_values)), current_values, color='green', alpha=0.7)
        ax3.set_title('MBS - Ty le thanh khoan', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Ty le')
        ax3.grid(True, alpha=0.3)
    
    # Debt to Equity
    debt_equity_col = 'Chỉ tiêu đòn bẩy_Debt/Equity'
    if debt_equity_col in df.columns:
        debt_values = pd.to_numeric(df[debt_equity_col], errors='coerce').fillna(0)
        colors = ['red' if x > 1 else 'green' for x in debt_values]
        ax4.bar(range(len(debt_values)), debt_values, color=colors, alpha=0.7)
        ax4.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Nguong rui ro')
        ax4.set_title('MBS - Ty le No/Von chu so huu', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Ty le')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/financial_analysis/financial_health_dashboard.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_profitability_analysis(financial_ratios, income_statement):
    """Tạo biểu đồ phân tích lợi nhuận - Biên lợi nhuận, EPS"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    if financial_ratios and 'data' in financial_ratios:
        df_ratios = pd.DataFrame(financial_ratios['data'])
        
        # Net Profit Margin
        npm_col = 'Chỉ tiêu lợi nhuận_Net Profit Margin (%)'
        if npm_col in df_ratios.columns:
            npm_values = pd.to_numeric(df_ratios[npm_col], errors='coerce').fillna(0)
            ax1.plot(range(len(npm_values)), npm_values, marker='o', linewidth=3, color='blue')
            ax1.set_title('MBS - Bien loi nhuan rong', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Ty le (%)')
            ax1.grid(True, alpha=0.3)
        
        # EPS
        eps_col = 'Chỉ tiêu cơ bản_EPS'
        if eps_col in df_ratios.columns:
            eps_values = pd.to_numeric(df_ratios[eps_col], errors='coerce').fillna(0)
            colors = ['green' if x > 0 else 'red' for x in eps_values]
            ax2.bar(range(len(eps_values)), eps_values, color=colors, alpha=0.7)
            ax2.set_title('MBS - Thu nhap tren co phieu (EPS)', fontsize=14, fontweight='bold')
            ax2.set_ylabel('EPS (VND)')
            ax2.grid(True, alpha=0.3)
    
    # Revenue and Profit trends (if income statement available)
    if income_statement and 'data' in income_statement:
        df_income = pd.DataFrame(income_statement['data'])
        
        # Revenue trend
        revenue_cols = [col for col in df_income.columns if 'revenue' in col.lower() or 'doanh thu' in col.lower()]
        if revenue_cols:
            revenue_col = revenue_cols[0]
            revenue_values = pd.to_numeric(df_income[revenue_col], errors='coerce').fillna(0)
            ax3.plot(range(len(revenue_values)), revenue_values/1000000000, marker='o', linewidth=3, color='green')
            ax3.set_title('MBS - Xu huong doanh thu', fontsize=14, fontweight='bold')
            ax3.set_ylabel('Doanh thu (ty VND)')
            ax3.grid(True, alpha=0.3)
        
        # Profit trend
        profit_cols = [col for col in df_income.columns if 'profit' in col.lower() or 'loi nhuan' in col.lower()]
        if profit_cols:
            profit_col = profit_cols[0]
            profit_values = pd.to_numeric(df_income[profit_col], errors='coerce').fillna(0)
            ax4.plot(range(len(profit_values)), profit_values/1000000000, marker='s', linewidth=3, color='purple')
            ax4.set_title('MBS - Xu huong loi nhuan', fontsize=14, fontweight='bold')
            ax4.set_ylabel('Loi nhuan (ty VND)')
            ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/financial_analysis/profitability_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_banking_specific_metrics(financial_ratios):
    """Tạo biểu đồ chỉ số đặc thù ngành ngân hàng"""
    if not financial_ratios or 'data' not in financial_ratios:
        return
    
    df = pd.DataFrame(financial_ratios['data'])
    if len(df) == 0:
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # NIM - Net Interest Margin (nếu có)
    nim_cols = [col for col in df.columns if 'interest' in col.lower() or 'lai suat' in col.lower()]
    if nim_cols:
        nim_values = pd.to_numeric(df[nim_cols[0]], errors='coerce').fillna(0)
        ax1.bar(range(len(nim_values)), nim_values, color='blue', alpha=0.7)
        ax1.set_title('MBS - Bien lai suat rong (NIM)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Ty le (%)')
        ax1.grid(True, alpha=0.3)
    
    # Cost to Income Ratio
    cost_income_cols = [col for col in df.columns if 'cost' in col.lower() and 'income' in col.lower()]
    if cost_income_cols:
        cost_values = pd.to_numeric(df[cost_income_cols[0]], errors='coerce').fillna(0)
        colors = ['green' if x < 50 else 'orange' if x < 70 else 'red' for x in cost_values]
        ax2.bar(range(len(cost_values)), cost_values, color=colors, alpha=0.7)
        ax2.axhline(y=50, color='green', linestyle='--', alpha=0.7, label='Tot (<50%)')
        ax2.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Cao (>70%)')
        ax2.set_title('MBS - Ty le Chi phi/Thu nhap', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Ty le (%)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    # Loan to Deposit Ratio (nếu có)
    loan_deposit_cols = [col for col in df.columns if 'loan' in col.lower() or 'cho vay' in col.lower()]
    if loan_deposit_cols:
        loan_values = pd.to_numeric(df[loan_deposit_cols[0]], errors='coerce').fillna(0)
        ax3.plot(range(len(loan_values)), loan_values, marker='o', linewidth=3, color='purple')
        ax3.set_title('MBS - Ty le Cho vay/Tien gui', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Ty le (%)')
        ax3.grid(True, alpha=0.3)
    
    # Capital Adequacy Ratio (CAR)
    car_cols = [col for col in df.columns if 'capital' in col.lower() or 'von' in col.lower()]
    if car_cols:
        car_values = pd.to_numeric(df[car_cols[0]], errors='coerce').fillna(0)
        colors = ['green' if x > 12 else 'orange' if x > 8 else 'red' for x in car_values]
        ax4.bar(range(len(car_values)), car_values, color=colors, alpha=0.7)
        ax4.axhline(y=8, color='red', linestyle='--', alpha=0.7, label='Toi thieu (8%)')
        ax4.axhline(y=12, color='green', linestyle='--', alpha=0.7, label='Tot (12%)')
        ax4.set_title('MBS - Ty le Du no von (CAR)', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Ty le (%)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/financial_analysis/real_estate_specific_metrics.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_peer_comparison(financial_ratios):
    """Tạo biểu đồ so sánh với đồng nghiệp"""
    if not financial_ratios or 'data' not in financial_ratios:
        return
    
    df = pd.DataFrame(financial_ratios['data'])
    if len(df) == 0:
        return
    
    # Lấy dữ liệu năm gần nhất
    latest = df.iloc[0] if len(df) > 0 else None
    if latest is None:
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # So sánh P/E với trung bình ngành (giả định)
    industry_pe = 12.5  # P/E trung bình ngành ngân hàng
    mbs_pe = pd.to_numeric(latest.get('Chỉ tiêu định giá_P/E', 0), errors='coerce')
    
    companies = ['MBS', 'Nganh NH']
    pe_values = [mbs_pe, industry_pe]
    colors = ['blue', 'gray']
    
    bars = ax1.bar(companies, pe_values, color=colors, alpha=0.7)
    ax1.set_title('MBS vs Nganh - P/E Ratio', fontsize=14, fontweight='bold')
    ax1.set_ylabel('P/E Ratio')
    
    for bar, value in zip(bars, pe_values):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                f'{value:.1f}', ha='center', va='bottom')
    
    ax1.grid(True, alpha=0.3)
    
    # So sánh ROE
    industry_roe = 15.0  # ROE trung bình ngành
    mbs_roe = pd.to_numeric(latest.get('Chỉ tiêu hiệu quả_ROE (%)', 0), errors='coerce')
    
    roe_values = [mbs_roe, industry_roe]
    colors = ['green' if mbs_roe > industry_roe else 'orange', 'gray']
    
    bars = ax2.bar(companies, roe_values, color=colors, alpha=0.7)
    ax2.set_title('MBS vs Nganh - ROE', fontsize=14, fontweight='bold')
    ax2.set_ylabel('ROE (%)')
    
    for bar, value in zip(bars, roe_values):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                f'{value:.1f}%', ha='center', va='bottom')
    
    ax2.grid(True, alpha=0.3)
    
    # So sánh P/B
    industry_pb = 1.8  # P/B trung bình ngành
    mbs_pb = pd.to_numeric(latest.get('Chỉ tiêu định giá_P/B', 0), errors='coerce')
    
    pb_values = [mbs_pb, industry_pb]
    colors = ['purple', 'gray']
    
    bars = ax3.bar(companies, pb_values, color=colors, alpha=0.7)
    ax3.set_title('MBS vs Nganh - P/B Ratio', fontsize=14, fontweight='bold')
    ax3.set_ylabel('P/B Ratio')
    
    for bar, value in zip(bars, pb_values):
        ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                f'{value:.2f}', ha='center', va='bottom')
    
    ax3.grid(True, alpha=0.3)
    
    # Tổng hợp điểm đánh giá
    pe_score = 5 if mbs_pe < industry_pe else 3
    roe_score = 5 if mbs_roe > industry_roe else 3
    pb_score = 5 if mbs_pb < industry_pb else 3
    total_score = (pe_score + roe_score + pb_score) / 3
    
    metrics = ['P/E', 'ROE', 'P/B', 'Tong diem']
    scores = [pe_score, roe_score, pb_score, total_score]
    colors = ['green' if s >= 4 else 'orange' if s >= 3 else 'red' for s in scores]
    
    bars = ax4.bar(metrics, scores, color=colors, alpha=0.7)
    ax4.set_title('MBS - Diem danh gia so voi nganh', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Diem (1-5)')
    ax4.set_ylim(0, 5)
    
    for bar, score in zip(bars, scores):
        ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.05,
                f'{score:.1f}', ha='center', va='bottom')
    
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/financial_analysis/peer_comparison.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def create_financial_trends(financial_ratios):
    """Tạo biểu đồ xu hướng tài chính"""
    if not financial_ratios or 'data' not in financial_ratios:
        return
    
    df = pd.DataFrame(financial_ratios['data'])
    if len(df) == 0:
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    years = list(range(len(df)))
    
    # ROE trend
    roe_col = 'Chỉ tiêu hiệu quả_ROE (%)'
    if roe_col in df.columns:
        roe_values = pd.to_numeric(df[roe_col], errors='coerce').fillna(0)
        ax1.plot(years, roe_values, marker='o', linewidth=3, color='blue', markersize=8)
        ax1.fill_between(years, roe_values, alpha=0.3, color='blue')
        
        # Thêm trendline
        if len(years) > 1:
            z = np.polyfit(years, roe_values, 1)
            p = np.poly1d(z)
            ax1.plot(years, p(years), "--", color='red', alpha=0.7, label='Xu huong')
        
        ax1.set_title('MBS - Xu huong ROE', fontsize=14, fontweight='bold')
        ax1.set_ylabel('ROE (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    
    # P/E trend
    pe_col = 'Chỉ tiêu định giá_P/E'
    if pe_col in df.columns:
        pe_values = pd.to_numeric(df[pe_col], errors='coerce').fillna(0)
        ax2.plot(years, pe_values, marker='s', linewidth=3, color='green', markersize=8)
        ax2.fill_between(years, pe_values, alpha=0.3, color='green')
        
        ax2.set_title('MBS - Xu huong P/E', fontsize=14, fontweight='bold')
        ax2.set_ylabel('P/E Ratio')
        ax2.grid(True, alpha=0.3)
    
    # EPS trend
    eps_col = 'Chỉ tiêu cơ bản_EPS'
    if eps_col in df.columns:
        eps_values = pd.to_numeric(df[eps_col], errors='coerce').fillna(0)
        colors = ['green' if x > 0 else 'red' for x in eps_values]
        bars = ax3.bar(years, eps_values, color=colors, alpha=0.7)
        
        # Thêm đường xu hướng
        if len(years) > 1:
            z = np.polyfit(years, eps_values, 1)
            p = np.poly1d(z)
            ax3.plot(years, p(years), "--", color='orange', linewidth=2, label='Xu huong')
        
        ax3.set_title('MBS - Xu huong EPS', fontsize=14, fontweight='bold')
        ax3.set_ylabel('EPS (VND)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    # Growth rates
    if len(df) > 1:
        roe_growth = 0
        pe_growth = 0
        eps_growth = 0
        
        if roe_col in df.columns:
            roe_values = pd.to_numeric(df[roe_col], errors='coerce').fillna(0)
            roe_growth = ((roe_values.iloc[0] - roe_values.iloc[-1]) / roe_values.iloc[-1] * 100) if roe_values.iloc[-1] != 0 else 0
        
        if pe_col in df.columns:
            pe_values = pd.to_numeric(df[pe_col], errors='coerce').fillna(0)
            pe_growth = ((pe_values.iloc[0] - pe_values.iloc[-1]) / pe_values.iloc[-1] * 100) if pe_values.iloc[-1] != 0 else 0
        
        eps_col = 'Chỉ tiêu cơ bản_EPS'
        if eps_col in df.columns:
            eps_values = pd.to_numeric(df[eps_col], errors='coerce').fillna(0)
            eps_growth = ((eps_values.iloc[0] - eps_values.iloc[-1]) / eps_values.iloc[-1] * 100) if eps_values.iloc[-1] != 0 else 0
        
        metrics = ['ROE', 'P/E', 'EPS']
        growth_rates = [roe_growth, pe_growth, eps_growth]
        colors = ['green' if x > 0 else 'red' for x in growth_rates]
        
        bars = ax4.bar(metrics, growth_rates, color=colors, alpha=0.7)
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax4.set_title('MBS - Ty le tang truong', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Tang truong (%)')
        
        for bar, rate in zip(bars, growth_rates):
            ax4.text(bar.get_x() + bar.get_width()/2., 
                    bar.get_height() + (1 if rate > 0 else -3),
                    f'{rate:.1f}%', ha='center', va='bottom' if rate > 0 else 'top')
        
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('stock_analysis/MBS/charts/financial_analysis/financial_trends.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    create_financial_charts()