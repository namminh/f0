#!/usr/bin/env python3
"""
Enhanced Report Generator - Tạo báo cáo HTML hấp dẫn nhà đầu tư
Sử dụng: python automation/enhanced_report_generator.py [SYMBOL]
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import base64
from jinja2 import Template

class EnhancedReportGenerator:
    def __init__(self):
        self.base_dir = Path("stock_analysis")
        self.reports_dir = Path("enhanced_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
    def load_stock_data(self, symbol):
        """Load comprehensive stock data"""
        symbol = symbol.upper()
        data = {
            'symbol': symbol,
            'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'analysis_date': datetime.now().strftime('%d/%m/%Y'),
            # Initialize all keys to prevent template errors
            'pe_ratio': 'N/A', 'pb_ratio': 'N/A', 'roe': 'N/A', 'roa': 'N/A', 'eps': 'N/A',
            'book_value': 'N/A', 'total_assets': 'N/A', 'total_equity': 'N/A',
            'total_debt': 'N/A', 'revenue': 'N/A', 'net_income': 'N/A', 'gross_profit': 'N/A',
            'current_price': 0, 'price_change': 0, 'price_change_percent': 0,
            'total_volume': 0, 'buy_sell_ratio': 1, 'volatility': 0, 'target_price': 0,
            'time_horizon': 'N/A', 'risk_level': 'N/A', 'confidence_level': 0, 'overall_score': 0,
            'debt_ratio': 'N/A',
            'market_sentiment': 'Trung tính', 'sentiment_color': '#ffc107',
            'recommendation': 'HOLD', 'recommendation_color': '#ffc107',
            'strengths': ['Cần theo dõi thêm'], 'risk_factors': ['Rủi ro thị trường chung']
        }
        
        # Load intraday data
        intraday_file = self.base_dir / symbol / "data" / f"{symbol}_intraday_data.json"
        if intraday_file.exists():
            with open(intraday_file, 'r', encoding='utf-8') as f:
                intraday_data = json.load(f)
                data['intraday_data'] = intraday_data
                
                if 'data' in intraday_data and intraday_data['data']:
                    df = pd.DataFrame(intraday_data['data'])
                    
                    # Basic metrics
                    data['total_data_points'] = len(df)
                    data['current_price'] = df['price'].iloc[-1]
                    data['opening_price'] = df['price'].iloc[0]
                    data['highest_price'] = df['price'].max()
                    data['lowest_price'] = df['price'].min()
                    data['average_price'] = df['price'].mean()
                    data['total_volume'] = df['volume'].sum()
                    
                    # Price change calculation
                    price_change = data['current_price'] - data['opening_price']
                    price_change_percent = (price_change / data['opening_price']) * 100
                    data['price_change'] = price_change
                    data['price_change_percent'] = price_change_percent
                    
                    # Volume analysis
                    df['time'] = pd.to_datetime(df['time'])
                    df['hour'] = df['time'].dt.hour
                    volume_by_hour = df.groupby('hour')['volume'].sum()
                    data['peak_hour'] = volume_by_hour.idxmax()
                    data['peak_volume'] = volume_by_hour.max()
                    
                    # Buy/Sell analysis
                    buy_volume = df[df['match_type'] == 'Buy']['volume'].sum()
                    sell_volume = df[df['match_type'] == 'Sell']['volume'].sum()
                    data['buy_volume'] = buy_volume
                    data['sell_volume'] = sell_volume
                    data['buy_sell_ratio'] = buy_volume / sell_volume if sell_volume > 0 else float('inf')
                    
                    # Volatility
                    data['volatility'] = df['price'].std()
                    data['price_range'] = data['highest_price'] - data['lowest_price']
                    
                    # Market sentiment
                    if data['buy_sell_ratio'] > 1.5:
                        data['market_sentiment'] = 'Rất tích cực'
                        data['sentiment_color'] = '#28a745'
                    elif data['buy_sell_ratio'] > 1.1:
                        data['market_sentiment'] = 'Tích cực'
                        data['sentiment_color'] = '#17a2b8'
                    elif data['buy_sell_ratio'] > 0.9:
                        data['market_sentiment'] = 'Trung tính'
                        data['sentiment_color'] = '#ffc107'
                    else:
                        data['market_sentiment'] = 'Tiêu cực'
                        data['sentiment_color'] = '#dc3545'
        
        # Load financial data
        self.load_financial_data(symbol, data)
        
        # Generate investment recommendation
        self.generate_investment_recommendation(data)
        
        return data
    
    def load_financial_data(self, symbol, data):
        """Load financial ratios and statements"""
        # Financial ratios
        ratios_file = self.base_dir / symbol / "data" / f"{symbol}_financial_ratios.json"
        if ratios_file.exists():
            with open(ratios_file, 'r', encoding='utf-8') as f:
                ratios_data = json.load(f)
                if 'data' in ratios_data and ratios_data['data']:
                    latest_ratios = ratios_data['data'][0]
                    
                    data['pe_ratio'] = latest_ratios.get('pe', 'N/A')
                    data['pb_ratio'] = latest_ratios.get('pb', 'N/A')
                    data['roe'] = latest_ratios.get('roe', 'N/A')
                    data['roa'] = latest_ratios.get('roa', 'N/A')
                    data['eps'] = latest_ratios.get('eps', 'N/A')
                    data['book_value'] = latest_ratios.get('book_value', 'N/A')
        
        # Balance sheet
        balance_file = self.base_dir / symbol / "data" / f"{symbol}_balance_sheet.json"
        if balance_file.exists():
            with open(balance_file, 'r', encoding='utf-8') as f:
                balance_data = json.load(f)
                if 'data' in balance_data and balance_data['data']:
                    latest_balance = balance_data['data'][0]
                    
                    data['total_assets'] = latest_balance.get('total_assets', 'N/A')
                    data['total_equity'] = latest_balance.get('total_equity', 'N/A')
                    data['total_debt'] = latest_balance.get('total_debt', 'N/A')
        
        # Income statement
        income_file = self.base_dir / symbol / "data" / f"{symbol}_income_statement.json"
        if income_file.exists():
            with open(income_file, 'r', encoding='utf-8') as f:
                income_data = json.load(f)
                if 'data' in income_data and income_data['data']:
                    latest_income = income_data['data'][0]
                    
                    data['revenue'] = latest_income.get('revenue', 'N/A')
                    data['net_income'] = latest_income.get('net_income', 'N/A')
                    data['gross_profit'] = latest_income.get('gross_profit', 'N/A')
    
    def generate_investment_recommendation(self, data):
        """Generate sophisticated investment recommendation"""
        # Calculate technical score
        technical_score = 0
        
        # Price momentum (30 points)
        if data.get('price_change_percent', 0) > 5:
            technical_score += 30
        elif data.get('price_change_percent', 0) > 2:
            technical_score += 20
        elif data.get('price_change_percent', 0) > 0:
            technical_score += 10
        
        # Volume analysis (25 points)
        if data.get('total_volume', 0) > 1000000:
            technical_score += 25
        elif data.get('total_volume', 0) > 500000:
            technical_score += 15
        elif data.get('total_volume', 0) > 100000:
            technical_score += 10
        
        # Buy/Sell ratio (25 points)
        buy_sell_ratio = data.get('buy_sell_ratio', 1)
        if buy_sell_ratio > 1.5:
            technical_score += 25
        elif buy_sell_ratio > 1.2:
            technical_score += 20
        elif buy_sell_ratio > 1.0:
            technical_score += 15
        
        # Volatility (20 points - lower is better)
        volatility = data.get('volatility', 0)
        if volatility < 0.5:
            technical_score += 20
        elif volatility < 1.0:
            technical_score += 15
        elif volatility < 2.0:
            technical_score += 10
        
        data['technical_score'] = technical_score
        
        # Calculate fundamental score
        fundamental_score = 0
        
        # ROE (30 points)
        roe = data.get('roe', 0)
        if isinstance(roe, (int, float)) and roe > 15:
            fundamental_score += 30
        elif isinstance(roe, (int, float)) and roe > 10:
            fundamental_score += 20
        elif isinstance(roe, (int, float)) and roe > 5:
            fundamental_score += 10
        
        # P/E ratio (25 points)
        pe_ratio = data.get('pe_ratio', 0)
        if isinstance(pe_ratio, (int, float)) and 10 <= pe_ratio <= 20:
            fundamental_score += 25
        elif isinstance(pe_ratio, (int, float)) and 5 <= pe_ratio < 10:
            fundamental_score += 20
        elif isinstance(pe_ratio, (int, float)) and pe_ratio < 30:
            fundamental_score += 15
        
        # P/B ratio (25 points)
        pb_ratio = data.get('pb_ratio', 0)
        if isinstance(pb_ratio, (int, float)) and pb_ratio < 1.5:
            fundamental_score += 25
        elif isinstance(pb_ratio, (int, float)) and pb_ratio < 2.0:
            fundamental_score += 20
        elif isinstance(pb_ratio, (int, float)) and pb_ratio < 3.0:
            fundamental_score += 15
        
        # ROA (20 points)
        roa = data.get('roa', 0)
        if isinstance(roa, (int, float)) and roa > 10:
            fundamental_score += 20
        elif isinstance(roa, (int, float)) and roa > 5:
            fundamental_score += 15
        elif isinstance(roa, (int, float)) and roa > 2:
            fundamental_score += 10
        
        data['fundamental_score'] = fundamental_score
        
        # Overall score and recommendation
        overall_score = (technical_score + fundamental_score) / 2
        data['overall_score'] = overall_score
        
        # Generate recommendation
        if overall_score >= 80:
            data['recommendation'] = 'STRONG BUY'
            data['recommendation_color'] = '#28a745'
            data['confidence_level'] = 90
            data['target_price'] = data.get('current_price', 0) * 1.25
            data['time_horizon'] = '6-12 tháng'
        elif overall_score >= 65:
            data['recommendation'] = 'BUY'
            data['recommendation_color'] = '#17a2b8'
            data['confidence_level'] = 75
            data['target_price'] = data.get('current_price', 0) * 1.15
            data['time_horizon'] = '12-18 tháng'
        elif overall_score >= 50:
            data['recommendation'] = 'HOLD'
            data['recommendation_color'] = '#ffc107'
            data['confidence_level'] = 60
            data['target_price'] = data.get('current_price', 0) * 1.05
            data['time_horizon'] = '18-24 tháng'
        elif overall_score >= 35:
            data['recommendation'] = 'WEAK SELL'
            data['recommendation_color'] = '#fd7e14'
            data['confidence_level'] = 70
            data['target_price'] = data.get('current_price', 0) * 0.95
            data['time_horizon'] = '6-12 tháng'
        else:
            data['recommendation'] = 'SELL'
            data['recommendation_color'] = '#dc3545'
            data['confidence_level'] = 85
            data['target_price'] = data.get('current_price', 0) * 0.85
            data['time_horizon'] = '3-6 tháng'
        
        # Generate detailed reasoning
        strengths = []
        if technical_score > 70:
            strengths.append("Tín hiệu kỹ thuật tích cực mạnh")
        if fundamental_score > 70:
            strengths.append("Chỉ số tài chính xuất sắc")
        if data.get('buy_sell_ratio', 1) > 1.3:
            strengths.append("Áp lực mua vượt trội")
        if data.get('total_volume', 0) > 1000000:
            strengths.append("Thanh khoản rất tốt")
        if not strengths:
            strengths.append("Cần theo dõi thêm")
        data['strengths'] = strengths
        
        # Risk assessment
        risk_factors = []
        if volatility > 2:
            risk_factors.append("Biến động giá cao")
        if data.get('total_volume', 0) < 100000:
            risk_factors.append("Thanh khoản thấp")
        if data.get('buy_sell_ratio', 1) < 0.8:
            risk_factors.append("Áp lực bán mạnh")
        if not risk_factors:
            risk_factors.append("Rủi ro thị trường chung")
        data['risk_factors'] = risk_factors

        # Overall risk level
        risk_score = (100 - technical_score) * 0.4 + (100 - fundamental_score) * 0.6
        if risk_score > 60:
            data['risk_level'] = "Cao"
        elif risk_score > 40:
            data['risk_level'] = "Trung bình"
        else:
            data['risk_level'] = "Thấp"

        # Debt Ratio
        total_debt = data.get('total_debt')
        total_assets = data.get('total_assets')
        if isinstance(total_debt, (int, float)) and isinstance(total_assets, (int, float)) and total_assets > 0:
            data['debt_ratio'] = (total_debt / total_assets) * 100
        else:
            data['debt_ratio'] = 'N/A'

        # Financial leverage text
        if data['debt_ratio'] == 'N/A':
            data['financial_leverage'] = 'N/A'
        elif data['debt_ratio'] > 60:
            data['financial_leverage'] = 'Cao'
        elif data['debt_ratio'] > 40:
            data['financial_leverage'] = 'Trung bình'
        else:
            data['financial_leverage'] = 'Thấp'
    
    def get_chart_paths(self, symbol):
        """Get all available chart paths"""
        symbol = symbol.upper()
        charts = {}
        
        # Key charts
        key_charts_dir = self.base_dir / symbol / "charts" / "key_charts"
        if key_charts_dir.exists():
            charts['key_charts'] = []
            for chart_file in key_charts_dir.glob("*.png"):
                charts['key_charts'].append({
                    'path': str(chart_file),
                    'name': chart_file.stem.replace('_', ' ').title(),
                    'filename': chart_file.name
                })
        
        # Technical analysis charts
        technical_dir = self.base_dir / symbol / "charts" / "technical_analysis"
        if technical_dir.exists():
            charts['technical_analysis'] = []
            for chart_file in technical_dir.glob("*.png"):
                charts['technical_analysis'].append({
                    'path': str(chart_file),
                    'name': chart_file.stem.replace('_', ' ').title(),
                    'filename': chart_file.name
                })
        
        # Additional analysis charts
        additional_dir = self.base_dir / symbol / "charts" / "additional_analysis"
        if additional_dir.exists():
            charts['additional_analysis'] = []
            for chart_file in additional_dir.glob("*.png"):
                charts['additional_analysis'].append({
                    'path': str(chart_file),
                    'name': chart_file.stem.replace('_', ' ').title(),
                    'filename': chart_file.name
                })
        
        # Financial analysis charts
        financial_dir = self.base_dir / symbol / "charts" / "financial_analysis"
        if financial_dir.exists():
            charts['financial_analysis'] = []
            for chart_file in financial_dir.glob("*.png"):
                charts['financial_analysis'].append({
                    'path': str(chart_file),
                    'name': chart_file.stem.replace('_', ' ').title(),
                    'filename': chart_file.name
                })
        
        return charts
    
    def create_enhanced_html_report(self, symbol):
        """Create enhanced HTML report"""
        symbol = symbol.upper()
        
        # Load data
        data = self.load_stock_data(symbol)
        charts = self.get_chart_paths(symbol)
        
        # HTML template
        html_template = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{data.symbol}} - Báo cáo Phân tích Comprehensive</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: bold;
        }
        .header p {
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 5px solid #2196F3;
        }
        .card h3 {
            margin: 0 0 10px 0;
            color: #2196F3;
            font-size: 1.1em;
        }
        .card .value {
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
            margin: 10px 0;
        }
        .card .change {
            font-size: 1em;
            margin: 5px 0;
        }
        .positive { color: #4CAF50; }
        .negative { color: #f44336; }
        .neutral { color: #FF9800; }
        
        .recommendation {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 30px;
            margin: 20px 30px;
            border-radius: 10px;
            text-align: center;
        }
        .recommendation.sell, .recommendation.weak.sell {
            background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        }
        .recommendation.hold {
            background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
        }
        
        .charts-section {
            padding: 30px;
        }
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin: 20px 0;
        }
        .chart-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .chart-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        .chart-title {
            background: #f8f9fa;
            padding: 15px;
            font-weight: bold;
            color: #333;
            border-bottom: 1px solid #e9ecef;
        }
        
        .analysis-section {
            padding: 30px;
            background: #f8f9fa;
        }
        .analysis-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        .analysis-box {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .analysis-box h3 {
            color: #2196F3;
            margin-top: 0;
            border-bottom: 2px solid #2196F3;
            padding-bottom: 10px;
        }
        
        .footer {
            background: #333;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }
        
        .metric-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .metric-row:last-child {
            border-bottom: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>{{data.symbol}} COMPREHENSIVE ANALYSIS</h1>
            <p>Báo cáo Phân tích Chi tiết - {{data.timestamp}}</p>
        </div>

        <!-- Summary Cards -->
        <div class="summary-cards">
            <div class="card">
                <h3>Giá Hiện tại</h3>
                <div class="value">{{'{:,.2f}'.format(data.current_price)}} VND</div>
                <div class="change {% if data.price_change > 0 %}positive{% elif data.price_change < 0 %}negative{% else %}neutral{% endif %}">
                    {{'{:+.2f}'.format(data.price_change)}} VND ({{'{:+.2f}'.format(data.price_change_percent)}}%)
                </div>
            </div>
            
            <div class="card">
                <h3>Khối lượng GD</h3>
                <div class="value">{{'{:,}'.format(data.total_volume)}}</div>
                <div class="change">Tỷ lệ Mua/Bán: {{'{:.2f}'.format(data.buy_sell_ratio)}}</div>
            </div>
            
            <div class="card">
                <h3>Tổng Tài sản</h3>
                <div class="value">{{'{:,.1f}'.format(data.total_assets/1e12) if data.total_assets != 'N/A' else '--'}}T VND</div>
                <div class="change">Debt Ratio: {{'{:.1f}'.format(data.debt_ratio) if data.debt_ratio != 'N/A' else '--'}}%</div>
            </div>
            
            <div class="card">
                <h3>ROE</h3>
                <div class="value">{{'{:.1f}'.format(data.roe) if data.roe != 'N/A' else '--'}}%</div>
                <div class="change">P/E: {{'{:.1f}'.format(data.pe_ratio) if data.pe_ratio != 'N/A' else '--'}}</div>
            </div>
        </div>

        <!-- Investment Recommendation -->
        <div class="recommendation {{data.recommendation.lower().replace(' ', '-')}}">
            <h2>KHUYẾN NGHỊ ĐẦU TƯ: {{data.recommendation}}</h2>
            <p><strong>Target Price:</strong> {{'{:,.2f}'.format(data.target_price)}} VND ({{'{:+.1f}'.format((data.target_price/data.current_price - 1)*100)}}%)</p>
            <p><strong>Timeframe:</strong> {{data.time_horizon}} | <strong>Risk Level:</strong> {{data.risk_level}} | <strong>Confidence:</strong> {{data.confidence_level}}%</p>
            <p><strong>Xu hướng:</strong> {{'Tăng' if data.price_change > 0 else 'Giảm' if data.price_change < 0 else 'Đi ngang'}} | <strong>Score:</strong> {{'{:.0f}'.format(data.overall_score)}}/100</p>
        </div>

        <!-- Charts Section -->
        <div class="charts-section">
            <h2>Biểu đồ Phân tích (18 Charts - Comprehensive Analysis)</h2>
            
            <!-- Key Charts -->
            <h3>Key Performance Charts (3/18)</h3>
            <div class="charts-grid">
                {% for chart in charts.key_charts %}
                <div class="chart-container">
                    <div class="chart-title">{{chart.name}}</div>
                    <img src="../charts/key_charts/{{chart.filename}}" alt="{{chart.name}}">
                </div>
                {% endfor %}
            </div>
            
            <!-- Technical Analysis Charts -->
            <h3>Technical Analysis Charts (5/18)</h3>
            <div class="charts-grid">
                {% for chart in charts.technical_analysis %}
                <div class="chart-container">
                    <div class="chart-title">{{chart.name}}</div>
                    <img src="../charts/technical_analysis/{{chart.filename}}" alt="{{chart.name}}">
                </div>
                {% endfor %}
            </div>
            
            <!-- Financial Analysis Charts -->
            <h3>Financial Analysis Charts (5/18)</h3>
            <div class="charts-grid">
                {% for chart in charts.financial_analysis %}
                <div class="chart-container">
                    <div class="chart-title">{{chart.name}}</div>
                    <img src="../charts/financial_analysis/{{chart.filename}}" alt="{{chart.name}}">
                </div>
                {% endfor %}
            </div>
            
            <!-- Additional Analysis Charts -->
            <h3>Additional Analysis Charts (5/18)</h3>
            <div class="charts-grid">
                {% for chart in charts.additional_analysis %}
                <div class="chart-container">
                    <div class="chart-title">{{chart.name}}</div>
                    <img src="../charts/additional_analysis/{{chart.filename}}" alt="{{chart.name}}">
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Detailed Analysis -->
        <div class="analysis-section">
            <h2>Phân tích Chi tiết</h2>
            
            <div class="analysis-grid">
                <div class="analysis-box">
                    <h3>Technical Analysis</h3>
                    <div class="metric-row">
                        <span>Volatility (Std Dev):</span>
                        <span>{{'{:.3f}'.format(data.volatility)}}</span>
                    </div>
                    <div class="metric-row">
                        <span>Price Range:</span>
                        <span>{{'{:,.2f}'.format(data.lowest_price)}} - {{'{:,.2f}'.format(data.highest_price)}}</span>
                    </div>
                    <div class="metric-row">
                        <span>Volume Weighted Avg:</span>
                        <span>{{'{:,.2f}'.format(data.average_price)}} VND</span>
                    </div>
                    <div class="metric-row">
                        <span>Data Points:</span>
                        <span>{{'{:,}'.format(data.total_data_points)}}</span>
                    </div>
                </div>
                
                <div class="analysis-box">
                    <h3>Financial Health</h3>
                    <div class="metric-row">
                        <span>Total Assets:</span>
                        <span>{{'{:,.2f}T'.format(data.total_assets/1e12) if data.total_assets != 'N/A' else '--'}} VND</span>
                    </div>
                    <div class="metric-row">
                        <span>Total Liabilities:</span>
                        <span>{{'{:,.2f}T'.format(data.total_debt/1e12) if data.total_debt != 'N/A' else '--'}} VND</span>
                    </div>
                    <div class="metric-row">
                        <span>Equity:</span>
                        <span>{{'{:,.2f}T'.format(data.total_equity/1e12) if data.total_equity != 'N/A' else '--'}} VND</span>
                    </div>
                    <div class="metric-row">
                        <span>Debt/Asset Ratio:</span>
                        <span>{{'{:.1f}'.format(data.debt_ratio) if data.debt_ratio != 'N/A' else '--'}}%</span>
                    </div>
                </div>
                
                <div class="analysis-box">
                    <h3>Profitability Ratios</h3>
                    <div class="metric-row">
                        <span>ROE (Return on Equity):</span>
                        <span>{{'{:.2f}'.format(data.roe) if data.roe != 'N/A' else '--'}}%</span>
                    </div>
                    <div class="metric-row">
                        <span>ROA (Return on Assets):</span>
                        <span>{{'{:.2f}'.format(data.roa) if data.roa != 'N/A' else '--'}}%</span>
                    </div>
                    <div class="metric-row">
                        <span>P/E Ratio:</span>
                        <span>{{'{:.2f}'.format(data.pe_ratio) if data.pe_ratio != 'N/A' else '--'}}</span>
                    </div>
                    <div class="metric-row">
                        <span>P/B Ratio:</span>
                        <span>{{'{:.2f}'.format(data.pb_ratio) if data.pb_ratio != 'N/A' else '--'}}</span>
                    </div>
                </div>
                
                <div class="analysis-box">
                    <h3>Risk Assessment</h3>
                    <div class="metric-row">
                        <span>Price Volatility:</span>
                        <span>{{'Cao' if data.volatility > 2 else 'Trung bình' if data.volatility > 1 else 'Thấp'}}</span>
                    </div>
                    <div class="metric-row">
                        <span>Liquidity:</span>
                        <span>{{'Tốt' if data.total_volume > 1000000 else 'Trung bình' if data.total_volume > 500000 else 'Thấp'}}</span>
                    </div>
                    <div class="metric-row">
                        <span>Financial Leverage:</span>
                        <span>{{data.financial_leverage}}</span>
                    </div>
                    <div class="metric-row">
                        <span>Overall Risk:</span>
                        <span>{{data.risk_level}}</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-box" style="margin-top: 30px;">
                <h3>Key Insights & Summary</h3>
                <p><strong>Điểm mạnh:</strong></p>
                <ul>
                    {% for reason in data.strengths %}
                    <li>{{reason}}</li>
                    {% endfor %}
                </ul>
                
                <p><strong>Điểm cần lưu ý:</strong></p>
                <ul>
                    {% for risk in data.risk_factors %}
                    <li>{{risk}}</li>
                    {% endfor %}
                </ul>
                
                <p><strong>Kết luận:</strong> {{data.symbol}} hiện tại được khuyến nghị {{data.recommendation}} với giá mục tiêu {{'{:,.2f}'.format(data.target_price)}} VND. 
                Mức độ tin cậy {{data.confidence_level}}% dựa trên phân tích kỹ thuật và cơ bản.</p>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Báo cáo được tạo tự động bởi DOMINUS AGENT | VNStock Analysis System v6.0</p>
            <p>Dữ liệu cập nhật: {{data.timestamp}} | Chỉ mang tính chất tham khảo</p>
        </div>
    </div>
</body>
</html>"""
        
        # Render template
        template = Template(html_template)
        rendered_html = template.render(data=data, charts=charts)
        
        # Save report
        print(f"DEBUG: Rendering template for {symbol}...")
        report_file = self.reports_dir / f"{symbol}_enhanced_investment_report.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        print(f"DEBUG: Report file {report_file} should have been created.")
        
        # Also save in original location for compatibility
        original_report_file = self.base_dir / symbol / "reports" / f"{symbol}_enhanced_analysis_report.html"
        original_report_file.parent.mkdir(exist_ok=True)
        with open(original_report_file, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        
        return report_file, data

def main():
    parser = argparse.ArgumentParser(description='Enhanced Report Generator for Stock Analysis')
    parser.add_argument('symbol', nargs='?', help='Stock symbol to generate report for')
    parser.add_argument('--batch', action='store_true', help='Generate reports for all stocks')
    parser.add_argument('--list', action='store_true', help='List available reports')
    
    args = parser.parse_args()
    generator = EnhancedReportGenerator()
    
    if args.list:
        reports = list(generator.reports_dir.glob("*_enhanced_investment_report.html"))
        if reports:
            print(f"📄 Báo cáo Enhanced có sẵn ({len(reports)}):")
            for report in sorted(reports):
                print(f"  {report.name}")
        else:
            print("📄 Chưa có báo cáo Enhanced nào")
    
    elif args.batch:
        # Generate reports for all available stocks
        stocks = [d.name for d in generator.base_dir.iterdir() if d.is_dir() and (d / "data").exists()]
        
        if not stocks:
            print("❌ Không tìm thấy cổ phiếu nào")
            return
        
        print(f"🔄 Tạo báo cáo Enhanced cho {len(stocks)} cổ phiếu...")
        
        success_count = 0
        for symbol in stocks:
            try:
                print(f"\n📊 Đang tạo báo cáo cho {symbol}...")
                report_file, data = generator.create_enhanced_html_report(symbol)
                print(f"✅ Báo cáo tạo thành công: {report_file}")
                print(f"🎯 Khuyến nghị: {data['recommendation']} ({data['confidence_level']}%)")
                success_count += 1
            except Exception as e:
                print(f"❌ Lỗi tạo báo cáo cho {symbol}: {e}")
        
        print(f"\n🎯 Kết quả: {success_count}/{len(stocks)} báo cáo được tạo thành công")
    
    elif args.symbol:
        symbol = args.symbol.upper()
        print(f"Tao bao cao Enhanced cho {symbol}...")
        
        try:
            report_file, data = generator.create_enhanced_html_report(symbol)
            print(f"Bao cao duoc tao: {report_file}")
            print(f"\nKet qua phan tich:")
            print(f"   Khuyen nghi: {data['recommendation']}")
            print(f"   Diem ky thuat: {data['technical_score']}/100")
            print(f"   Diem co ban: {data['fundamental_score']}/100")
            print(f"   Gia muc tieu: {data.get('target_price', 0):.2f} VND")
            print(f"   Thoi gian: {data['time_horizon']}")
            print(f"   Do tin cay: {data['confidence_level']}%")
            
        except Exception as e:
            print(f"Loi tao bao cao cho {symbol}: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()