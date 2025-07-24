import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import os

def create_financial_charts():
    """Tạo biểu đồ tài chính cho VJC."""
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'automation')))
    from financial_chart_template import create_real_financial_chart

    Path("stock_analysis/VJC/charts/financial_analysis").mkdir(parents=True, exist_ok=True)

    try:
        with open("stock_analysis/VJC/data/VJC_balance_sheet.json", "r", encoding="utf-8") as f:
            balance_sheet_data = json.load(f)
    except FileNotFoundError:
        balance_sheet_data = None

    if balance_sheet_data:
        output_path = "stock_analysis/VJC/charts/financial_analysis/balance_sheet.png"
        create_real_financial_chart(balance_sheet_data, "VJC", output_path)

    print("Financial charts created for VJC")

if __name__ == "__main__":
    create_financial_charts()
