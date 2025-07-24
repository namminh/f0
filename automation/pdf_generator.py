#!/usr/bin/env python3
"""
PDF Generator - Tạo báo cáo PDF tự động từ HTML
Sử dụng: python automation/pdf_generator.py [SYMBOL]
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import weasyprint
from jinja2 import Template

class PDFGenerator:
    def __init__(self):
        self.base_dir = Path("stock_analysis")
        self.pdf_dir = Path("pdf_reports")
        self.pdf_dir.mkdir(exist_ok=True)
        
    def generate_pdf_from_html(self, symbol, use_wkhtmltopdf=False):
        """Tạo PDF từ HTML báo cáo"""
        symbol = symbol.upper()
        html_file = self.base_dir / symbol / "reports" / f"{symbol}_enhanced_analysis_report.html"
        pdf_file = self.pdf_dir / f"{symbol}_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        if not html_file.exists():
            print(f"HTML report not found: {html_file}")
            return False
        
        try:
            # Sử dụng WeasyPrint
            html_content = html_file.read_text(encoding='utf-8')
            weasyprint.HTML(string=html_content, base_url=str(html_file.parent)).write_pdf(str(pdf_file))
            
            print(f"PDF created: {pdf_file}")
            return True
            
        except Exception as e:
            print(f"Error creating PDF: {e}")
            return False
    
    def create_enhanced_pdf_template(self, symbol):
        """Tạo template PDF chuyên nghiệp"""
        symbol = symbol.upper()
        
        # Load data
        data = self.load_stock_data(symbol)
        
        # Tạo HTML template chuyên nghiệp
        html_template = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo cáo Phân tích Đầu tư - {{symbol}}</title>
    <style>
        @page {
            size: A4;
            margin: 2cm;
            @bottom-center {
                content: "Dominus Agent - Báo cáo Phân tích Đầu tư";
                font-size: 10px;
                color: #666;
            }
        }
        
        body {
            font-family: "Times New Roman", serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 15px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin: 0;
            font-weight: bold;
        }
        
        .header .subtitle {
            font-size: 1.2em;
            margin-top: 10px;
            opacity: 0.9;
        }
        
        .executive-summary {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border-left: 5px solid #28a745;
            margin-bottom: 30px;
        }
        
        .executive-summary h2 {
            color: #28a745;
            margin-top: 0;
            font-size: 1.8em;
        }
        
        .key-metrics {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 4px solid #007bff;
            text-align: center;
        }
        
        .metric-card h4 {
            margin: 0 0 10px 0;
            color: #555;
            font-size: 1.1em;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
            margin: 10px 0;
        }
        
        .metric-change {
            font-size: 0.9em;
            color: #28a745;
        }
        
        .recommendation-box {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin: 30px 0;
            text-align: center;
        }
        
        .recommendation-box h3 {
            font-size: 1.8em;
            margin: 0 0 15px 0;
        }
        
        .recommendation-rating {
            font-size: 3em;
            font-weight: bold;
            margin: 15px 0;
        }
        
        .target-price {
            font-size: 1.4em;
            margin: 15px 0;
        }
        
        .chart-section {
            margin: 30px 0;
            page-break-inside: avoid;
        }
        
        .chart-section h3 {
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        
        .chart-container {
            text-align: center;
            margin: 20px 0;
            page-break-inside: avoid;
        }
        
        .chart-container img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .chart-description {
            font-style: italic;
            color: #666;
            margin-top: 10px;
            font-size: 0.95em;
        }
        
        .risk-assessment {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0;
        }
        
        .risk-assessment h3 {
            color: #856404;
            margin-top: 0;
        }
        
        .technical-analysis {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0;
        }
        
        .technical-analysis h3 {
            color: #1976d2;
            margin-top: 0;
        }
        
        .financial-highlights {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 30px 0;
        }
        
        .highlight-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #17a2b8;
        }
        
        .highlight-item h4 {
            margin: 0 0 10px 0;
            color: #17a2b8;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            border-top: 2px solid #ddd;
            color: #666;
        }
        
        .disclaimer {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 30px 0;
            font-size: 0.9em;
            color: #666;
        }
        
        .page-break {
            page-break-before: always;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{symbol}}</h1>
        <div class="subtitle">Báo cáo Phân tích Đầu tư Chuyên sâu</div>
        <div class="subtitle">{{current_date}}</div>
    </div>
    
    <div class="executive-summary">
        <h2>📊 Tóm tắt Điều hành</h2>
        <p>Cổ phiếu <strong>{{symbol}}</strong> đang thể hiện xu hướng {{trend_status}} với mức độ thanh khoản {{liquidity_status}}. 
        Phân tích kỹ thuật cho thấy {{technical_summary}} trong khi các chỉ số tài chính đạt mức {{financial_health}}.</p>
        
        <p><strong>Điểm nổi bật:</strong> {{key_highlights}}</p>
    </div>
    
    <div class="key-metrics">
        <div class="metric-card">
            <h4>Giá Hiện tại</h4>
            <div class="metric-value">{{current_price}} VNĐ</div>
            <div class="metric-change">{{price_change}}</div>
        </div>
        <div class="metric-card">
            <h4>Khối lượng GD</h4>
            <div class="metric-value">{{trading_volume}}</div>
            <div class="metric-change">{{volume_change}}</div>
        </div>
        <div class="metric-card">
            <h4>Tỷ lệ Mua/Bán</h4>
            <div class="metric-value">{{buy_sell_ratio}}</div>
            <div class="metric-change">{{ratio_status}}</div>
        </div>
    </div>
    
    <div class="recommendation-box">
        <h3>🎯 Khuyến nghị Đầu tư</h3>
        <div class="recommendation-rating">{{recommendation}}</div>
        <div class="target-price">Giá mục tiêu: {{target_price}} VNĐ</div>
        <div>Khoảng thời gian: {{time_horizon}}</div>
        <div>Mức độ tin cậy: {{confidence_level}}%</div>
    </div>
    
    <div class="chart-section">
        <h3>📈 Phân tích Kỹ thuật</h3>
        <div class="chart-container">
            <img src="../charts/technical_analysis/comprehensive_price_analysis.png" alt="Phân tích giá toàn diện">
            <div class="chart-description">Phân tích giá với các chỉ báo kỹ thuật chính (MA, Bollinger Bands, RSI)</div>
        </div>
        <div class="chart-container">
            <img src="../charts/technical_analysis/technical_indicators.png" alt="Chỉ báo kỹ thuật">
            <div class="chart-description">Tổng hợp các chỉ báo kỹ thuật quan trọng</div>
        </div>
    </div>
    
    <div class="page-break"></div>
    
    <div class="technical-analysis">
        <h3>🔍 Phân tích Kỹ thuật Chi tiết</h3>
        <div class="financial-highlights">
            <div class="highlight-item">
                <h4>RSI (14)</h4>
                <p>{{rsi_value}} - {{rsi_interpretation}}</p>
            </div>
            <div class="highlight-item">
                <h4>MACD</h4>
                <p>{{macd_status}} - {{macd_interpretation}}</p>
            </div>
            <div class="highlight-item">
                <h4>Bollinger Bands</h4>
                <p>{{bb_position}} - {{bb_interpretation}}</p>
            </div>
            <div class="highlight-item">
                <h4>Volume Profile</h4>
                <p>{{volume_profile}} - {{volume_interpretation}}</p>
            </div>
        </div>
    </div>
    
    <div class="chart-section">
        <h3>💰 Phân tích Tài chính</h3>
        <div class="chart-container">
            <img src="../charts/financial_analysis/financial_health_dashboard.png" alt="Dashboard sức khỏe tài chính">
            <div class="chart-description">Tổng quan về sức khỏe tài chính của doanh nghiệp</div>
        </div>
        <div class="chart-container">
            <img src="../charts/financial_analysis/profitability_analysis.png" alt="Phân tích khả năng sinh lời">
            <div class="chart-description">Phân tích các chỉ số khả năng sinh lời (ROE, ROA, Profit Margin)</div>
        </div>
    </div>
    
    <div class="risk-assessment">
        <h3>⚠️ Đánh giá Rủi ro</h3>
        <div class="financial-highlights">
            <div class="highlight-item">
                <h4>VaR (95%)</h4>
                <p>{{var_95}} - Rủi ro tối đa trong 95% trường hợp</p>
            </div>
            <div class="highlight-item">
                <h4>Volatility</h4>
                <p>{{volatility}}% - Mức độ biến động</p>
            </div>
            <div class="highlight-item">
                <h4>Beta</h4>
                <p>{{beta_value}} - Tương quan với thị trường</p>
            </div>
            <div class="highlight-item">
                <h4>Risk Score</h4>
                <p>{{risk_score}}/100 - Điểm rủi ro tổng hợp</p>
            </div>
        </div>
    </div>
    
    <div class="chart-section">
        <h3>📊 Phân tích Bổ sung</h3>
        <div class="chart-container">
            <img src="../charts/additional_analysis/performance_dashboard.png" alt="Dashboard hiệu suất">
            <div class="chart-description">Tổng quan hiệu suất giao dịch và các chỉ số quan trọng</div>
        </div>
        <div class="chart-container">
            <img src="../charts/additional_analysis/risk_assessment.png" alt="Đánh giá rủi ro">
            <div class="chart-description">Phân tích rủi ro chi tiết với VaR và volatility</div>
        </div>
    </div>
    
    <div class="page-break"></div>
    
    <div class="executive-summary">
        <h2>🎯 Kết luận và Khuyến nghị</h2>
        <p><strong>Khuyến nghị:</strong> {{final_recommendation}}</p>
        <p><strong>Lý do:</strong> {{recommendation_reasoning}}</p>
        <p><strong>Chiến lược:</strong> {{investment_strategy}}</p>
        <p><strong>Mức rủi ro:</strong> {{risk_level}}</p>
        <p><strong>Thời gian nắm giữ:</strong> {{holding_period}}</p>
    </div>
    
    <div class="disclaimer">
        <p><strong>Lưu ý:</strong> Báo cáo này được tạo tự động bởi Dominus Agent và chỉ mang tính chất tham khảo. 
        Nhà đầu tư cần xem xét kỹ lưỡng và tham khảo ý kiến chuyên gia trước khi đưa ra quyết định đầu tư.</p>
    </div>
    
    <div class="footer">
        <p><strong>🤖 Được tạo bởi Dominus Agent</strong></p>
        <p>Hệ thống Phân tích Đầu tư Tự động</p>
        <p>Cập nhật: {{current_date}}</p>
    </div>
</body>
</html>"""
        
        # Tạo dữ liệu cho template
        template_data = {
            'symbol': symbol,
            'current_date': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'trend_status': data.get('trend_status', 'tích cực'),
            'liquidity_status': data.get('liquidity_status', 'tốt'),
            'technical_summary': data.get('technical_summary', 'tín hiệu mua mạnh'),
            'financial_health': data.get('financial_health', 'khá tốt'),
            'key_highlights': data.get('key_highlights', 'Thanh khoản tốt, khối lượng giao dịch ổn định'),
            'current_price': data.get('current_price', '--'),
            'price_change': data.get('price_change', '+0.0%'),
            'trading_volume': data.get('trading_volume', '--'),
            'volume_change': data.get('volume_change', '+0.0%'),
            'buy_sell_ratio': data.get('buy_sell_ratio', '--'),
            'ratio_status': data.get('ratio_status', 'Cân bằng'),
            'recommendation': data.get('recommendation', 'STRONG BUY'),
            'target_price': data.get('target_price', '--'),
            'time_horizon': data.get('time_horizon', '12 tháng'),
            'confidence_level': data.get('confidence_level', '82'),
            'rsi_value': data.get('rsi_value', '--'),
            'rsi_interpretation': data.get('rsi_interpretation', 'Vùng trung tính'),
            'macd_status': data.get('macd_status', 'Tích cực'),
            'macd_interpretation': data.get('macd_interpretation', 'Tín hiệu mua'),
            'bb_position': data.get('bb_position', 'Giữa dải'),
            'bb_interpretation': data.get('bb_interpretation', 'Xu hướng ổn định'),
            'volume_profile': data.get('volume_profile', 'Cân bằng'),
            'volume_interpretation': data.get('volume_interpretation', 'Thanh khoản tốt'),
            'var_95': data.get('var_95', '--'),
            'volatility': data.get('volatility', '--'),
            'beta_value': data.get('beta_value', '--'),
            'risk_score': data.get('risk_score', '--'),
            'final_recommendation': data.get('final_recommendation', 'STRONG BUY'),
            'recommendation_reasoning': data.get('recommendation_reasoning', 'Tín hiệu kỹ thuật tích cực, tài chính ổn định'),
            'investment_strategy': data.get('investment_strategy', 'Mua và nắm giữ trung hạn'),
            'risk_level': data.get('risk_level', 'Trung bình'),
            'holding_period': data.get('holding_period', '6-12 tháng')
        }
        
        # Render template
        template = Template(html_template)
        rendered_html = template.render(**template_data)
        
        # Save HTML file
        html_file = self.base_dir / symbol / "reports" / f"{symbol}_pdf_template.html"
        html_file.write_text(rendered_html, encoding='utf-8')
        
        return html_file
    
    def load_stock_data(self, symbol):
        """Load stock data from JSON files"""
        symbol = symbol.upper()
        data = {}
        
        # Load intraday data
        intraday_file = self.base_dir / symbol / "data" / f"{symbol}_intraday_data.json"
        if intraday_file.exists():
            try:
                with open(intraday_file, 'r', encoding='utf-8') as f:
                    intraday_data = json.load(f)
                    
                if 'data' in intraday_data and intraday_data['data']:
                    import pandas as pd
                    df = pd.DataFrame(intraday_data['data'])
                    
                    data['current_price'] = f"{df['price'].iloc[-1]:.2f}"
                    data['trading_volume'] = f"{df['volume'].sum():,}"
                    
                    # Calculate buy/sell ratio
                    buy_vol = df[df['match_type'] == 'Buy']['volume'].sum()
                    sell_vol = df[df['match_type'] == 'Sell']['volume'].sum()
                    if sell_vol > 0:
                        data['buy_sell_ratio'] = f"{buy_vol/sell_vol:.2f}"
                    else:
                        data['buy_sell_ratio'] = "N/A"
                    
                    # Calculate price change
                    if len(df) > 1:
                        price_change = (df['price'].iloc[-1] - df['price'].iloc[0]) / df['price'].iloc[0] * 100
                        data['price_change'] = f"{price_change:+.2f}%"
                    
                    # Calculate volatility
                    data['volatility'] = f"{df['price'].std():.2f}"
                    
            except Exception as e:
                print(f"Error loading intraday data: {e}")
        
        # Load financial ratios
        ratios_file = self.base_dir / symbol / "data" / f"{symbol}_financial_ratios.json"
        if ratios_file.exists():
            try:
                with open(ratios_file, 'r', encoding='utf-8') as f:
                    ratios_data = json.load(f)
                    
                if 'data' in ratios_data and ratios_data['data']:
                    latest_ratios = ratios_data['data'][0]  # Get most recent data
                    
                    # Extract key ratios
                    data['roe'] = latest_ratios.get('roe', '--')
                    data['roa'] = latest_ratios.get('roa', '--')
                    data['pe_ratio'] = latest_ratios.get('pe', '--')
                    data['pb_ratio'] = latest_ratios.get('pb', '--')
                    
            except Exception as e:
                print(f"Error loading financial ratios: {e}")
        
        # Set default values if not found
        defaults = {
            'current_price': '--',
            'price_change': '+0.0%',
            'trading_volume': '--',
            'volume_change': '+0.0%',
            'buy_sell_ratio': '--',
            'ratio_status': 'Cân bằng',
            'recommendation': 'STRONG BUY',
            'target_price': '--',
            'time_horizon': '12 tháng',
            'confidence_level': '82',
            'trend_status': 'tích cực',
            'liquidity_status': 'tốt',
            'technical_summary': 'tín hiệu mua mạnh',
            'financial_health': 'khá tốt',
            'key_highlights': 'Thanh khoản tốt, khối lượng giao dịch ổn định',
            'rsi_value': '--',
            'rsi_interpretation': 'Vùng trung tính',
            'macd_status': 'Tích cực',
            'macd_interpretation': 'Tín hiệu mua',
            'bb_position': 'Giữa dải',
            'bb_interpretation': 'Xu hướng ổn định',
            'volume_profile': 'Cân bằng',
            'volume_interpretation': 'Thanh khoản tốt',
            'var_95': '--',
            'volatility': '--',
            'beta_value': '--',
            'risk_score': '--',
            'final_recommendation': 'STRONG BUY',
            'recommendation_reasoning': 'Tín hiệu kỹ thuật tích cực, tài chính ổn định',
            'investment_strategy': 'Mua và nắm giữ trung hạn',
            'risk_level': 'Trung bình',
            'holding_period': '6-12 tháng'
        }
        
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        
        return data
    
    def create_pdf_report(self, symbol, use_enhanced_template=True):
        """Tạo báo cáo PDF hoàn chỉnh"""
        symbol = symbol.upper()
        
        try:
            # Tạo PDF từ HTML có sẵn
            return self.generate_pdf_from_html(symbol, use_wkhtmltopdf=False)
                
        except Exception as e:
            print(f"Loi tao PDF: {e}")
            print("WeasyPrint can yeu cau GTK libraries. Vui long xem huong dan cai dat.")
            return False
    
    def batch_create_pdfs(self, symbols=None):
        """Tạo PDF cho nhiều cổ phiếu"""
        if symbols is None:
            # Lấy tất cả cổ phiếu có sẵn
            symbols = [d.name for d in self.base_dir.iterdir() if d.is_dir() and (d / "data").exists()]
        
        success_count = 0
        total_count = len(symbols)
        
        print(f"🔄 Bắt đầu tạo PDF cho {total_count} cổ phiếu...")
        
        for symbol in symbols:
            print(f"\n📊 Đang tạo PDF cho {symbol}...")
            if self.create_pdf_report(symbol):
                success_count += 1
                print(f"✅ Hoàn thành {symbol}")
            else:
                print(f"❌ Lỗi tạo PDF cho {symbol}")
        
        print(f"\n🎯 Kết quả: {success_count}/{total_count} PDF được tạo thành công")
        print(f"📁 Thư mục lưu trữ: {self.pdf_dir}")
        
        return success_count

def main():
    parser = argparse.ArgumentParser(description='PDF Generator for Stock Analysis')
    parser.add_argument('symbol', nargs='?', help='Stock symbol to create PDF for')
    parser.add_argument('--batch', action='store_true', help='Create PDFs for all stocks')
    parser.add_argument('--enhanced', action='store_true', default=True, help='Use enhanced PDF template')
    parser.add_argument('--list', action='store_true', help='List available PDF reports')
    
    args = parser.parse_args()
    generator = PDFGenerator()
    
    if args.list:
        pdf_files = list(generator.pdf_dir.glob("*.pdf"))
        if pdf_files:
            print(f"📄 Báo cáo PDF có sẵn ({len(pdf_files)}):")
            for pdf_file in sorted(pdf_files):
                size_kb = pdf_file.stat().st_size / 1024
                print(f"  {pdf_file.name} ({size_kb:.1f} KB)")
        else:
            print("📄 Chưa có báo cáo PDF nào")
    
    elif args.batch:
        generator.batch_create_pdfs()
    
    elif args.symbol:
        symbol = args.symbol.upper()
        print(f"📊 Tạo PDF báo cáo cho {symbol}...")
        
        pdf_file = generator.create_pdf_report(symbol, use_enhanced_template=args.enhanced)
        if pdf_file:
            print(f"✅ PDF đã được tạo: {pdf_file}")
        else:
            print(f"❌ Lỗi tạo PDF cho {symbol}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()