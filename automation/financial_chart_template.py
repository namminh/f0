import pandas as pd
import matplotlib.pyplot as plt

def create_real_financial_chart(data, symbol, output_path):
    """
    Tạo một biểu đồ tài chính đơn giản.
    """
    if not data or 'data' not in data or not data['data']:
        print(f"{symbol}: No financial data to create chart.")
        return False

    df = pd.DataFrame(data['data'])
    
    if df.empty:
        print(f"{symbol}: Financial data is empty.")
        return False

    # Ví dụ: Vẽ biểu đồ tổng tài sản qua các năm
    if 'TỔNG CỘNG TÀI SẢN (đồng)' in df.columns and 'Năm' in df.columns:
        plt.figure(figsize=(10, 6))
        plt.bar(df['Năm'], df['TỔNG CỘNG TÀI SẢN (đồng)'])
        plt.title(f'Tổng tài sản của {symbol} qua các năm')
        plt.xlabel('Năm')
        plt.ylabel('Tổng tài sản (đồng)')
        plt.grid(True)
        plt.savefig(output_path)
        plt.close()
        print(f"Created financial chart for {symbol} at {output_path}")
        return True
    else:
        print(f"{symbol}: 'Total Assets' or 'year' column not found in financial data.")
        return False
