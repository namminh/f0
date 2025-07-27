#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOMINUS AGENT - Enhanced Stock Analyzer
Sub-agent tối ưu cho phân tích cổ phiếu và tạo báo cáo

Usage: python automation/enhanced_stock_analyzer.py [SYMBOL]
Output: 
- Charts: stock_analysis/[SYMBOL]/charts/
- Report: stock_analysis/[SYMBOL]/reports/[SYMBOL]_enhanced_report.html
"""

import json
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
import codecs
warnings.filterwarnings('ignore')

# Fix encoding for Windows
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

# Set matplotlib backend to avoid GUI issues
plt.switch_backend('Agg')

class EnhancedStockAnalyzer:
    def __init__(self, symbol):
        self.symbol = symbol.upper()
        self.base_path = Path(f"stock_analysis/{self.symbol}")
        self.data_path = self.base_path / "data"
        self.charts_path = self.base_path / "charts"
        self.reports_path = self.base_path / "reports"
        
        # Tạo thư mục nếu chưa có
        self.charts_path.mkdir(parents=True, exist_ok=True)
        self.reports_path.mkdir(parents=True, exist_ok=True)
        (self.charts_path / "key_charts").mkdir(exist_ok=True)
        (self.charts_path / "technical_analysis").mkdir(exist_ok=True)
        (self.charts_path / "financial_analysis").mkdir(exist_ok=True)
        (self.charts_path / "additional_analysis").mkdir(exist_ok=True)
        
        # Load data
        self.data = self._load_all_data()
        
    def _load_all_data(self):
        """Load tất cả dữ liệu cần thiết"""
        data = {}
        
        # Load intraday data
        intraday_file = self.data_path / f"{self.symbol}_intraday_data.json"
        if intraday_file.exists():
            with open(intraday_file, 'r', encoding='utf-8') as f:
                data['intraday'] = json.load(f)
        
        # Load financial data
        for file_type in ['balance_sheet', 'income_statement', 'financial_ratios']:
            file_path = self.data_path / f"{self.symbol}_{file_type}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data[file_type] = json.load(f)
        
        return data
    
    def analyze_data(self):
        """Phân tích dữ liệu và tạo insights"""
        analysis = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': self.symbol,
            'data_availability': {},
            'key_metrics': {},
            'technical_analysis': {},
            'financial_analysis': {},
            'recommendations': []
        }
        
        # Check data availability
        for key in ['intraday', 'balance_sheet', 'income_statement', 'financial_ratios']:
            analysis['data_availability'][key] = key in self.data and bool(self.data[key])
        
        # Analyze intraday data
        if 'intraday' in self.data and self.data['intraday']:
            analysis.update(self._analyze_intraday())
        
        # Analyze financial data
        if 'financial_ratios' in self.data and self.data['financial_ratios']:
            analysis.update(self._analyze_financial())
        
        return analysis
    
    def _analyze_intraday(self):
        """Phân tích dữ liệu intraday"""
        intraday_data = self.data['intraday']
        if not intraday_data or 'data' not in intraday_data:
            return {}
        
        df = pd.DataFrame(intraday_data['data'])
        df['time'] = pd.to_datetime(df['time'])
        df['hour'] = df['time'].dt.hour
        
        # Tính toán metrics
        analysis = {
            'key_metrics': {
                'total_data_points': len(df),
                'trading_start': df['time'].min(),
                'trading_end': df['time'].max(),
                'opening_price': df['price'].iloc[0],
                'closing_price': df['price'].iloc[-1],
                'highest_price': df['price'].max(),
                'lowest_price': df['price'].min(),
                'average_price': df['price'].mean(),
                'total_volume': df['volume'].sum(),
                'price_change': df['price'].iloc[-1] - df['price'].iloc[0],
                'price_change_percent': ((df['price'].iloc[-1] - df['price'].iloc[0]) / df['price'].iloc[0]) * 100,
                'volatility': df['price'].std(),
                'price_range': df['price'].max() - df['price'].min()
            },
            'technical_analysis': {
                'trend': 'Tăng' if df['price'].iloc[-1] > df['price'].iloc[0] else 'Giảm' if df['price'].iloc[-1] < df['price'].iloc[0] else 'Đi ngang',
                'volume_by_hour': df.groupby('hour')['volume'].sum().to_dict(),
                'buy_volume': df[df['match_type'] == 'Buy']['volume'].sum() if 'match_type' in df.columns else 0,
                'sell_volume': df[df['match_type'] == 'Sell']['volume'].sum() if 'match_type' in df.columns else 0,
            }
        }
        
        # Tính buy/sell ratio
        if analysis['technical_analysis']['sell_volume'] > 0:
            analysis['technical_analysis']['buy_sell_ratio'] = analysis['technical_analysis']['buy_volume'] / analysis['technical_analysis']['sell_volume']
        else:
            analysis['technical_analysis']['buy_sell_ratio'] = float('inf')
        
        return analysis
    
    def _analyze_financial(self):
        """Phân tích dữ liệu tài chính"""
        ratios_data = self.data['financial_ratios']
        if not ratios_data or 'data' not in ratios_data:
            return {}
        
        df = pd.DataFrame(ratios_data['data'])
        latest = df.iloc[0] if not df.empty else {}
        
        financial_analysis = {
            'financial_analysis': {
                'pe_ratio': latest.get('pe', 'N/A'),
                'pb_ratio': latest.get('pb', 'N/A'),
                'roe': latest.get('roe', 'N/A'),
                'roa': latest.get('roa', 'N/A'),
                'debt_to_equity': latest.get('debtEquity', 'N/A'),
                'current_ratio': latest.get('currentRatio', 'N/A'),
                'quick_ratio': latest.get('quickRatio', 'N/A')
            }
        }
        
        return financial_analysis
    
    def create_charts(self):
        """Tạo tất cả biểu đồ cần thiết"""
        charts_created = []
        
        if 'intraday' in self.data and self.data['intraday']:
            # Key charts
            charts_created.extend(self._create_key_charts())
            
            # Technical analysis charts
            charts_created.extend(self._create_technical_charts())
        
        if any(key in self.data for key in ['balance_sheet', 'income_statement', 'financial_ratios']):
            # Financial analysis charts
            charts_created.extend(self._create_financial_charts())
        
        return charts_created
    
    def _create_key_charts(self):
        """Tạo 3 biểu đồ chính"""
        charts = []
        intraday_data = self.data['intraday']
        df = pd.DataFrame(intraday_data['data'])
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        
        # 1. Price Trend Chart
        plt.figure(figsize=(14, 8))
        plt.plot(df['time'], df['price'], linewidth=2, color='#2E86AB')
        
        # Add price levels
        max_price = df['price'].max()
        min_price = df['price'].min()
        plt.axhline(y=max_price, color='red', linestyle='--', alpha=0.7, label=f'Cao nhất: {max_price:.2f}')
        plt.axhline(y=min_price, color='green', linestyle='--', alpha=0.7, label=f'Thấp nhất: {min_price:.2f}')
        
        price_change = df['price'].iloc[-1] - df['price'].iloc[0]
        price_change_pct = (price_change / df['price'].iloc[0]) * 100
        
        plt.title(f'{self.symbol} - Biểu đồ Giá Trong Ngày\nThay đổi: {price_change:+.2f} VND ({price_change_pct:+.2f}%)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Thời gian', fontsize=12)
        plt.ylabel('Giá (VND)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        chart_path = self.charts_path / "key_charts" / "price_trend.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts.append(str(chart_path))
        
        # 2. Volume by Hour Chart
        df['hour'] = df['time'].dt.hour
        volume_by_hour = df.groupby('hour')['volume'].sum()
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(volume_by_hour.index, volume_by_hour.values, color='#A23B72', alpha=0.8)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}',
                    ha='center', va='bottom', fontsize=9)
        
        plt.title(f'{self.symbol} - Khối lượng Giao dịch Theo Giờ', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Giờ', fontsize=12)
        plt.ylabel('Khối lượng', fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        chart_path = self.charts_path / "key_charts" / "volume_by_hour.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts.append(str(chart_path))
        
        # 3. Buy vs Sell Chart
        if 'match_type' in df.columns:
            buy_volume = df[df['match_type'] == 'Buy']['volume'].sum()
            sell_volume = df[df['match_type'] == 'Sell']['volume'].sum()
            
            plt.figure(figsize=(10, 8))
            labels = ['Khối lượng Mua', 'Khối lượng Bán']
            sizes = [buy_volume, sell_volume]
            colors = ['#2E8B57', '#DC143C']
            explode = (0.05, 0.05)
            
            wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, explode=explode,
                                             autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*sum(sizes)):,})',
                                             startangle=90, textprops={'fontsize': 12})
            
            plt.title(f'{self.symbol} - Tỷ lệ Mua/Bán\nTổng KL: {sum(sizes):,}', 
                     fontsize=16, fontweight='bold', pad=20)
            
            chart_path = self.charts_path / "key_charts" / "buy_vs_sell.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            charts.append(str(chart_path))
        
        return charts
    
    def _create_technical_charts(self):
        """Tạo biểu đồ phân tích kỹ thuật"""
        charts = []
        intraday_data = self.data['intraday']
        df = pd.DataFrame(intraday_data['data'])
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        
        # Technical Indicators Chart
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Moving Averages
        df['MA5'] = df['price'].rolling(window=5).mean()
        df['MA10'] = df['price'].rolling(window=10).mean()
        
        ax1.plot(df['time'], df['price'], label='Giá', linewidth=2, color='blue')
        ax1.plot(df['time'], df['MA5'], label='MA5', color='orange', alpha=0.8)
        ax1.plot(df['time'], df['MA10'], label='MA10', color='red', alpha=0.8)
        ax1.set_title('Giá và Đường MA')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Volume Analysis
        ax2.bar(df['time'], df['volume'], alpha=0.6, color='purple')
        ax2.set_title('Khối lượng Giao dịch')
        ax2.grid(True, alpha=0.3)
        
        # Price Distribution
        ax3.hist(df['price'], bins=20, alpha=0.7, color='green', edgecolor='black')
        ax3.axvline(df['price'].mean(), color='red', linestyle='--', label=f'Trung bình: {df["price"].mean():.2f}')
        ax3.set_title('Phân phối Giá')
        ax3.set_xlabel('Giá')
        ax3.set_ylabel('Tần suất')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Price vs Volume Correlation
        ax4.scatter(df['volume'], df['price'], alpha=0.6, color='brown')
        ax4.set_title('Tương quan Giá - Khối lượng')
        ax4.set_xlabel('Khối lượng')
        ax4.set_ylabel('Giá')
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle(f'{self.symbol} - Phân tích Kỹ thuật', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        chart_path = self.charts_path / "technical_analysis" / "technical_indicators.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        charts.append(str(chart_path))
        
        return charts
    
    def _create_financial_charts(self):
        """Tạo biểu đồ phân tích tài chính"""
        charts = []
        
        if 'financial_ratios' in self.data and self.data['financial_ratios']:
            ratios_data = self.data['financial_ratios']
            df = pd.DataFrame(ratios_data['data'])
            
            if not df.empty:
                # Financial Ratios Dashboard
                fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
                
                # PE & PB Ratios
                if 'pe' in df.columns and 'pb' in df.columns:
                    pe_values = pd.to_numeric(df['pe'], errors='coerce').dropna()
                    pb_values = pd.to_numeric(df['pb'], errors='coerce').dropna()
                    
                    if not pe_values.empty and not pb_values.empty:
                        ax1.plot(pe_values.index, pe_values.values, marker='o', label='P/E', color='blue')
                        ax1_twin = ax1.twinx()
                        ax1_twin.plot(pb_values.index, pb_values.values, marker='s', label='P/B', color='red')
                        ax1.set_title('P/E và P/B Ratios')
                        ax1.set_ylabel('P/E Ratio', color='blue')
                        ax1_twin.set_ylabel('P/B Ratio', color='red')
                        ax1.grid(True, alpha=0.3)
                
                # ROE & ROA
                if 'roe' in df.columns and 'roa' in df.columns:
                    roe_values = pd.to_numeric(df['roe'], errors='coerce').dropna()
                    roa_values = pd.to_numeric(df['roa'], errors='coerce').dropna()
                    
                    if not roe_values.empty and not roa_values.empty:
                        ax2.plot(roe_values.index, roe_values.values, marker='o', label='ROE', color='green')
                        ax2.plot(roa_values.index, roa_values.values, marker='s', label='ROA', color='orange')
                        ax2.set_title('ROE và ROA (%)')
                        ax2.set_ylabel('Tỷ lệ (%)')
                        ax2.legend()
                        ax2.grid(True, alpha=0.3)
                
                # Debt to Equity
                if 'debtEquity' in df.columns:
                    debt_equity = pd.to_numeric(df['debtEquity'], errors='coerce').dropna()
                    if not debt_equity.empty:
                        ax3.bar(range(len(debt_equity)), debt_equity.values, color='purple', alpha=0.7)
                        ax3.set_title('Debt to Equity Ratio')
                        ax3.set_ylabel('Tỷ lệ')
                        ax3.grid(True, alpha=0.3)
                
                # Current & Quick Ratios
                if 'currentRatio' in df.columns and 'quickRatio' in df.columns:
                    current_ratio = pd.to_numeric(df['currentRatio'], errors='coerce').dropna()
                    quick_ratio = pd.to_numeric(df['quickRatio'], errors='coerce').dropna()
                    
                    if not current_ratio.empty and not quick_ratio.empty:
                        x = range(min(len(current_ratio), len(quick_ratio)))
                        width = 0.35
                        ax4.bar([i - width/2 for i in x], current_ratio.values[:len(x)], width, label='Current Ratio', color='cyan', alpha=0.7)
                        ax4.bar([i + width/2 for i in x], quick_ratio.values[:len(x)], width, label='Quick Ratio', color='magenta', alpha=0.7)
                        ax4.set_title('Current vs Quick Ratio')
                        ax4.set_ylabel('Tỷ lệ')
                        ax4.legend()
                        ax4.grid(True, alpha=0.3)
                
                plt.suptitle(f'{self.symbol} - Phân tích Tài chính', fontsize=16, fontweight='bold')
                plt.tight_layout()
                
                chart_path = self.charts_path / "financial_analysis" / "financial_ratios.png"
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                charts.append(str(chart_path))
        
        return charts
    
    def generate_report(self, analysis, charts_created):
        """Tạo báo cáo HTML hoàn chỉnh"""
        
        # Get relative paths for images
        charts_html = ""
        for chart_path in charts_created:
            rel_path = os.path.relpath(chart_path, self.reports_path)
            chart_name = Path(chart_path).stem.replace('_', ' ').title()
            charts_html += f"""
            <div class="chart-container">
                <h3>{chart_name}</h3>
                <img src="{rel_path}" alt="{chart_name}" style="max-width: 100%; height: auto;">
            </div>
            """
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis)
        recommendations_html = "".join([f"<li>{rec}</li>" for rec in recommendations])
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.symbol} - Báo cáo Phân tích Cổ phiếu</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: 300;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 1.1em;
                }}
                .content {{
                    padding: 30px;
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .metric-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #667eea;
                }}
                .metric-card h3 {{
                    margin: 0 0 10px 0;
                    color: #667eea;
                    font-size: 1.1em;
                }}
                .metric-value {{
                    font-size: 1.8em;
                    font-weight: bold;
                    color: #333;
                }}
                .metric-label {{
                    font-size: 0.9em;
                    color: #666;
                    margin-top: 5px;
                }}
                .charts-section {{
                    margin: 30px 0;
                }}
                .chart-container {{
                    margin: 30px 0;
                    text-align: center;
                }}
                .chart-container h3 {{
                    color: #667eea;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                }}
                .recommendations {{
                    background: #e8f4fd;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #2196F3;
                }}
                .recommendations h3 {{
                    color: #2196F3;
                    margin-top: 0;
                }}
                .recommendations ul {{
                    padding-left: 20px;
                }}
                .recommendations li {{
                    margin: 10px 0;
                    line-height: 1.6;
                }}
                .section {{
                    margin: 30px 0;
                    padding: 20px;
                    background: #fafafa;
                    border-radius: 8px;
                }}
                .section h2 {{
                    color: #667eea;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                }}
                .positive {{ color: #4CAF50; }}
                .negative {{ color: #f44336; }}
                .neutral {{ color: #FF9800; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Báo cáo Phân tích Cổ phiếu {self.symbol}</h1>
                    <p>Được tạo lúc: {analysis.get('timestamp', 'N/A')}</p>
                </div>
                
                <div class="content">
                    <div class="section">
                        <h2>Thong tin Co ban</h2>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <h3>Giá Hiện tại</h3>
                                <div class="metric-value">{analysis.get('key_metrics', {}).get('closing_price', 'N/A')}</div>
                                <div class="metric-label">VND</div>
                            </div>
                            <div class="metric-card">
                                <h3>Thay đổi</h3>
                                <div class="metric-value {'positive' if analysis.get('key_metrics', {}).get('price_change', 0) > 0 else 'negative' if analysis.get('key_metrics', {}).get('price_change', 0) < 0 else 'neutral'}">
                                    {analysis.get('key_metrics', {}).get('price_change_percent', 'N/A')}%
                                </div>
                                <div class="metric-label">
                                    ({analysis.get('key_metrics', {}).get('price_change', 'N/A')} VND)
                                </div>
                            </div>
                            <div class="metric-card">
                                <h3>Khối lượng</h3>
                                <div class="metric-value">{analysis.get('key_metrics', {}).get('total_volume', 'N/A'):,}</div>
                                <div class="metric-label">Cổ phiếu</div>
                            </div>
                            <div class="metric-card">
                                <h3>Biên độ</h3>
                                <div class="metric-value">{analysis.get('key_metrics', {}).get('price_range', 'N/A')}</div>
                                <div class="metric-label">VND</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>Phan tich Ky thuat</h2>
                        <p><strong>Xu hướng:</strong> {analysis.get('technical_analysis', {}).get('trend', 'N/A')}</p>
                        <p><strong>Tỷ lệ Mua/Bán:</strong> {analysis.get('technical_analysis', {}).get('buy_sell_ratio', 'N/A'):.2f}</p>
                        <p><strong>Độ biến động:</strong> {analysis.get('key_metrics', {}).get('volatility', 'N/A'):.2f}</p>
                    </div>
                    
                    <div class="section">
                        <h2>Phan tich Tai chinh</h2>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <h3>P/E Ratio</h3>
                                <div class="metric-value">{analysis.get('financial_analysis', {}).get('pe_ratio', 'N/A')}</div>
                            </div>
                            <div class="metric-card">
                                <h3>P/B Ratio</h3>
                                <div class="metric-value">{analysis.get('financial_analysis', {}).get('pb_ratio', 'N/A')}</div>
                            </div>
                            <div class="metric-card">
                                <h3>ROE</h3>
                                <div class="metric-value">{analysis.get('financial_analysis', {}).get('roe', 'N/A')}</div>
                                <div class="metric-label">%</div>
                            </div>
                            <div class="metric-card">
                                <h3>ROA</h3>
                                <div class="metric-value">{analysis.get('financial_analysis', {}).get('roa', 'N/A')}</div>
                                <div class="metric-label">%</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="charts-section">
                        <h2>Bieu do Phan tich</h2>
                        {charts_html}
                    </div>
                    
                    <div class="recommendations">
                        <h3>Khuyen nghi Dau tu</h3>
                        <ul>
                            {recommendations_html}
                        </ul>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        report_path = self.reports_path / f"{self.symbol}_enhanced_report.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)
    
    def _generate_recommendations(self, analysis):
        """Tạo khuyến nghị đầu tư dựa trên phân tích"""
        recommendations = []
        
        # Price trend analysis
        if 'technical_analysis' in analysis:
            trend = analysis['technical_analysis'].get('trend', '')
            if trend == 'Tăng':
                recommendations.append("Xu huong gia tich cuc trong phien giao dich")
            elif trend == 'Giảm':
                recommendations.append("Xu huong gia giam, can than trong")
            else:
                recommendations.append("Gia di ngang, cho tin hieu ro rang hon")
        
        # Volume analysis
        if 'key_metrics' in analysis:
            total_volume = analysis['key_metrics'].get('total_volume', 0)
            if total_volume > 100000:
                recommendations.append("Khoi luong giao dich tot, thanh khoan cao")
            else:
                recommendations.append("Khoi luong giao dich thap, can chu y thanh khoan")
        
        # Buy/Sell ratio analysis
        if 'technical_analysis' in analysis:
            buy_sell_ratio = analysis['technical_analysis'].get('buy_sell_ratio', 0)
            if buy_sell_ratio > 1.2:
                recommendations.append("Ap luc mua manh hon ap luc ban")
            elif buy_sell_ratio < 0.8:
                recommendations.append("Ap luc ban manh hon ap luc mua")
            else:
                recommendations.append("Can bang giua luc mua va luc ban")
        
        # Financial health
        if 'financial_analysis' in analysis:
            pe_ratio = analysis['financial_analysis'].get('pe_ratio', 'N/A')
            if pe_ratio != 'N/A' and isinstance(pe_ratio, (int, float)):
                if pe_ratio < 15:
                    recommendations.append("P/E thap, co the la co hoi dau tu")
                elif pe_ratio > 25:
                    recommendations.append("P/E cao, can can nhac rui ro")
        
        # Default recommendation if no specific ones
        if not recommendations:
            recommendations.append("Can theo doi them du lieu de dua ra khuyen nghi chinh xac")
        
        return recommendations
    
    def run_full_analysis(self):
        """Chạy phân tích hoàn chỉnh"""
        print(f"STARTING: Bat dau phan tich co phieu {self.symbol}")
        
        # Step 1: Analyze data
        print("ANALYZING: Phan tich du lieu...")
        analysis = self.analyze_data()
        
        # Step 2: Create charts
        print("CHARTING: Tao bieu do...")
        charts_created = self.create_charts()
        
        # Step 3: Generate report
        print("REPORTING: Tao bao cao...")
        report_path = self.generate_report(analysis, charts_created)
        
        # Summary
        print(f"\nCOMPLETED: Hoan thanh phan tich {self.symbol}")
        print(f"CHARTS: Da tao {len(charts_created)} bieu do")
        print(f"REPORT: {report_path}")
        
        return {
            'symbol': self.symbol,
            'analysis': analysis,
            'charts_created': charts_created,
            'report_path': report_path,
            'success': True
        }

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python automation/enhanced_stock_analyzer.py [SYMBOL]")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    
    try:
        analyzer = EnhancedStockAnalyzer(symbol)
        result = analyzer.run_full_analysis()
        
        if result['success']:
            print(f"\nSUCCESS: THANH CONG!")
            print(f"Detail report: {result['report_path']}")
        else:
            print(f"\nERROR: Khong the hoan thanh phan tich")
            sys.exit(1)
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()