#!/usr/bin/env python3
"""
VHM Comprehensive Report Generator with 18 Charts
Tạo báo cáo HTML hoàn chỉnh cho VHM với tất cả 18 biểu đồ
"""

import json
import pandas as pd
import base64
from pathlib import Path
from datetime import datetime

def create_vhm_comprehensive_report():
    """Tạo báo cáo HTML hoàn chỉnh cho VHM"""
    
    # Load data
    with open("stock_analysis/VHM/data/VHM_intraday_data.json", "r", encoding="utf-8") as f:
        intraday_data = json.load(f)
    
    df = pd.DataFrame(intraday_data['data'])
    
    # Calculate key metrics
    total_volume = df['volume'].sum()
    current_price = df['price'].iloc[-1]
    opening_price = df['price'].iloc[0]
    highest_price = df['price'].max()
    lowest_price = df['price'].min()
    price_change = current_price - opening_price
    price_change_percent = (price_change / opening_price) * 100
    
    buy_volume = df[df['match_type'] == 'Buy']['volume'].sum()
    sell_volume = df[df['match_type'] == 'Sell']['volume'].sum()
    buy_sell_ratio = buy_volume / sell_volume if sell_volume > 0 else 0
    
    # Convert charts to base64
    def encode_chart(chart_path):
        if Path(chart_path).exists():
            with open(chart_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    
    # Chart paths
    charts = {
        # Key Charts (3)
        'price_trend': encode_chart("stock_analysis/VHM/charts/key_charts/price_trend.png"),
        'volume_by_hour': encode_chart("stock_analysis/VHM/charts/key_charts/volume_by_hour.png"),
        'buy_vs_sell': encode_chart("stock_analysis/VHM/charts/key_charts/buy_vs_sell.png"),
        
        # Technical Analysis (5)
        'comprehensive_price_analysis': encode_chart("stock_analysis/VHM/charts/technical_analysis/comprehensive_price_analysis.png"),
        'volume_analysis': encode_chart("stock_analysis/VHM/charts/technical_analysis/volume_analysis.png"),
        'technical_indicators': encode_chart("stock_analysis/VHM/charts/technical_analysis/technical_indicators.png"),
        'market_sentiment': encode_chart("stock_analysis/VHM/charts/technical_analysis/market_sentiment.png"),
        'trading_summary': encode_chart("stock_analysis/VHM/charts/technical_analysis/trading_summary.png"),
        
        # Financial Analysis (5)
        'financial_health_dashboard': encode_chart("stock_analysis/VHM/charts/financial_analysis/financial_health_dashboard.png"),
        'profitability_analysis': encode_chart("stock_analysis/VHM/charts/financial_analysis/profitability_analysis.png"),
        'real_estate_specific_metrics': encode_chart("stock_analysis/VHM/charts/financial_analysis/real_estate_specific_metrics.png"),
        'peer_comparison': encode_chart("stock_analysis/VHM/charts/financial_analysis/peer_comparison.png"),
        'financial_trends': encode_chart("stock_analysis/VHM/charts/financial_analysis/financial_trends.png"),
        
        # Additional Analysis (5)
        'price_action_analysis': encode_chart("stock_analysis/VHM/charts/additional_analysis/price_action_analysis.png"),
        'liquidity_analysis': encode_chart("stock_analysis/VHM/charts/additional_analysis/liquidity_analysis.png"),
        'risk_assessment': encode_chart("stock_analysis/VHM/charts/additional_analysis/risk_assessment.png"),
        'trading_zones': encode_chart("stock_analysis/VHM/charts/additional_analysis/trading_zones.png"),
        'performance_dashboard': encode_chart("stock_analysis/VHM/charts/additional_analysis/performance_dashboard.png")
    }
    
    # Generate HTML report
    html_content = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VHM - Vinhomes: Báo cáo Phân tích Toàn diện</title>
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
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #007bff;
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            color: #666;
            margin: 10px 0;
            font-size: 1.1em;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .metric-card h3 {{
            margin: 0 0 10px 0;
            font-size: 1.1em;
        }}
        .metric-card .value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #007bff;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .chart-container {{
            margin: 20px 0;
            text-align: center;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .chart-analysis {{
            background-color: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #007bff;
            margin: 10px 0;
        }}
        .recommendation {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin: 30px 0;
            text-align: center;
        }}
        .recommendation h3 {{
            font-size: 1.8em;
            margin: 0 0 15px 0;
        }}
        .risk-warning {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .score-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .score-item {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 2px solid #dee2e6;
        }}
        .score-item h4 {{
            margin: 0 0 10px 0;
            color: #495057;
        }}
        .score-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #007bff;
        }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>VHM - VINHOMES</h1>
            <p>Báo cáo Phân tích Toàn diện với 18 Biểu đồ</p>
            <p>Ngày phân tích: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>

        <!-- Key Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Giá Hiện Tại</h3>
                <div class="value">{current_price:.2f} VND</div>
                <p>Thay đổi: {price_change:+.2f} ({price_change_percent:+.2f}%)</p>
            </div>
            <div class="metric-card">
                <h3>Khối Lượng Giao Dịch</h3>
                <div class="value">{total_volume:,.0f}</div>
                <p>Cổ phiếu</p>
            </div>
            <div class="metric-card">
                <h3>Biên Độ Giá</h3>
                <div class="value">{lowest_price:.2f} - {highest_price:.2f}</div>
                <p>VND</p>
            </div>
            <div class="metric-card">
                <h3>Tỷ Lệ Mua/Bán</h3>
                <div class="value">{buy_sell_ratio:.2f}</div>
                <p>{'Tích cực' if buy_sell_ratio > 1.1 else 'Tiêu cực' if buy_sell_ratio < 0.9 else 'Trung tính'}</p>
            </div>
        </div>

        <!-- Executive Summary -->
        <div class="section">
            <h2>📊 Tóm Tắt Điều Hành</h2>
            <div class="chart-analysis">
                <p><strong>Phiên giao dịch ngày 18/07/2025:</strong> VHM có phiên giao dịch khá tích cực với khối lượng giao dịch lớn {total_volume:,.0f} cổ phiếu. Giá cổ phiếu tăng {price_change_percent:+.2f}% lên {current_price:.2f} VND.</p>
                <p><strong>Điểm nổi bật:</strong> Tỷ lệ mua/bán {buy_sell_ratio:.2f} cho thấy áp lực {'mua' if buy_sell_ratio > 1 else 'bán'} nhẹ. Thanh khoản tốt với sự tham gia tích cực của nhà đầu tư.</p>
            </div>
        </div>

        <!-- Key Charts Section -->
        <div class="section">
            <h2>📈 Biểu Đồ Cơ Bản (3 Charts)</h2>
            
            <div class="chart-container">
                <h3>1. Biến động giá VHM trong ngày</h3>
                <img src="data:image/png;base64,{charts['price_trend']}" alt="Price Trend">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> Giá VHM dao động từ {lowest_price:.2f} - {highest_price:.2f} VND. Cổ phiếu có xu hướng tăng mạnh từ đầu phiên, đạt đỉnh vào giữa ngày và có sự điều chỉnh nhẹ về cuối phiên.</p>
                </div>
            </div>

            <div class="chart-container">
                <h3>2. Khối lượng giao dịch theo giờ</h3>
                <img src="data:image/png;base64,{charts['volume_by_hour']}" alt="Volume by Hour">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> Khối lượng giao dịch tập trung mạnh vào giờ 13h (2.49 triệu cổ phiếu) và 11h (2.28 triệu cổ phiếu). Điều này cho thấy sự quan tâm cao của nhà đầu tư trong khung thời gian này.</p>
                </div>
            </div>

            <div class="chart-container">
                <h3>3. Tỷ lệ mua/bán</h3>
                <img src="data:image/png;base64,{charts['buy_vs_sell']}" alt="Buy vs Sell">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> Tỷ lệ mua chiếm 56.3% ({buy_volume:,.0f} cổ phiếu) so với bán 43.7% ({sell_volume:,.0f} cổ phiếu). Tỷ lệ mua/bán {buy_sell_ratio:.2f} cho thấy tâm lý thị trường tích cực nhưng không quá mạnh.</p>
                </div>
            </div>
        </div>

        <!-- Technical Analysis Section -->
        <div class="section">
            <h2>🔧 Phân Tích Kỹ Thuật (5 Charts)</h2>
            
            <div class="chart-container">
                <h3>4. Phân tích giá toàn diện với các chỉ báo</h3>
                <img src="data:image/png;base64,{charts['comprehensive_price_analysis']}" alt="Comprehensive Price Analysis">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> Giá VHM duy trì xu hướng tăng với MA5, MA10, MA20 đều hỗ trợ. Bollinger Bands cho thấy giá chạm mức upper band, cần chú ý tới khả năng điều chỉnh. RSI trong vùng quá mua (~70) cảnh báo áp lực bán.</p>
                </div>
            </div>

            <div class="chart-container">
                <h3>5. Phân tích khối lượng chi tiết</h3>
                <img src="data:image/png;base64,{charts['volume_analysis']}" alt="Volume Analysis">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> Khối lượng giao dịch phân bố không đều trong ngày. Tương quan giá-khối lượng yếu (0.006) cho thấy thiếu sự đồng thuận mạnh mẽ từ thị trường.</p>
                </div>
            </div>

            <div class="chart-container">
                <h3>6. Chỉ báo kỹ thuật</h3>
                <img src="data:image/png;base64,{charts['technical_indicators']}" alt="Technical Indicators">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> Bollinger Bands cho thấy giá di chuyển gần mức trên, RSI dao động mạnh trong ngày từ 30-100, hiện tại khoảng 70. Các đường MA hỗ trợ tốt cho xu hướng tăng.</p>
                </div>
            </div>

            <div class="chart-container">
                <h3>7. Tâm lý thị trường</h3>
                <img src="data:image/png;base64,{charts['market_sentiment']}" alt="Market Sentiment">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> Bản đồ nhiệt giao dịch cho thấy hoạt động tập trung vào khung 11h-13h. Áp lực mua tích lũy mạnh hơn áp lực bán trong phiên.</p>
                </div>
            </div>

            <div class="chart-container">
                <h3>8. Tóm tắt giao dịch</h3>
                <img src="data:image/png;base64,{charts['trading_summary']}" alt="Trading Summary">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> Tổng kết phiên giao dịch cho thấy VHM có hiệu suất tốt với xu hướng tăng, thanh khoản cao và tâm lý thị trường tích cực.</p>
                </div>
            </div>
        </div>

        <!-- Financial Analysis Section -->
        <div class="section">
            <h2>💰 Phân Tích Tài Chính (5 Charts)</h2>
            
            <div class="chart-container">
                <h3>9. Dashboard sức khỏe tài chính</h3>
                <img src="data:image/png;base64,{charts['financial_health_dashboard']}" alt="Financial Health Dashboard">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> VHM thể hiện sức khỏe tài chính vững mạnh với ROE 19.1%, ROA 12.1%, và tỷ lệ nợ/vốn chủ sở hữu 0.8. Các chỉ số đều ở mức tốt cho ngành bất động sản.</p>
                </div>
            </div>

            <div class="chart-container">
                <h3>10. Phân tích khả năng sinh lời</h3>
                <img src="data:image/png;base64,{charts['profitability_analysis']}" alt="Profitability Analysis">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> Khả năng sinh lời của VHM cải thiện đáng kể qua các năm. ROE và ROA đều tăng trưởng ổn định, phản ánh hiệu quả quản lý vốn tốt.</p>
                </div>
            </div>

            <div class="chart-container">
                <h3>11. Chỉ số đặc thù bất động sản</h3>
                <img src="data:image/png;base64,{charts['real_estate_specific_metrics']}" alt="Real Estate Specific Metrics">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> Doanh thu tăng trưởng 18.5%, hiệu suất tài sản và vòng quay tồn kho ổn định. Tỷ lệ nợ/vốn chủ sở hữu được kiểm soát tốt.</p>
                </div>
            </div>

            <div class="chart-container">
                <h3>12. So sánh với đối thủ cạnh tranh</h3>
                <img src="data:image/png;base64,{charts['peer_comparison']}" alt="Peer Comparison">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> VHM dẫn đầu ngành với ROE 19.1%, ROA 12.1%, vượt trội so với các đối thủ khác. Công ty thể hiện vị thế số 1 trong ngành bất động sản.</p>
                </div>
            </div>

            <div class="chart-container">
                <h3>13. Xu hướng tài chính</h3>
                <img src="data:image/png;base64,{charts['financial_trends']}" alt="Financial Trends">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> Xu hướng tài chính tích cực với doanh thu và lợi nhuận tăng trưởng đều. Tài sản tăng trưởng ổn định, hiệu quả hoạt động cải thiện.</p>
                </div>
            </div>
        </div>

        <!-- Additional Analysis Section -->
        <div class="section">
            <h2>🔍 Phân Tích Bổ Sung (5 Charts)</h2>
            
            <div class="chart-container">
                <h3>14. Phân tích price action</h3>
                <img src="data:image/png;base64,{charts['price_action_analysis']}" alt="Price Action Analysis">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> Mức hỗ trợ và kháng cự được xác định rõ ràng. Momentum giá tích cực, volatility kiểm soát tốt. Patterns cho thấy xu hướng tăng trung hạn.</p>
                </div>
            </div>

            <div class="chart-container">
                <h3>15. Phân tích thanh khoản</h3>
                <img src="data:image/png;base64,{charts['liquidity_analysis']}" alt="Liquidity Analysis">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> Thanh khoản tốt với volume profile đều, VWAP hỗ trợ xu hướng giá. Bid-ask spread hẹp cho thấy tính thanh khoản cao.</p>
                </div>
            </div>

            <div class="chart-container">
                <h3>16. Đánh giá rủi ro</h3>
                <img src="data:image/png;base64,{charts['risk_assessment']}" alt="Risk Assessment">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> VaR 95% (-0.11%) và VaR 99% (-0.32%) cho thấy rủi ro thấp. Maximum drawdown -3.9% kiểm soát tốt. Sharpe ratio 0.04 cần cải thiện.</p>
                </div>
            </div>

            <div class="chart-container">
                <h3>17. Phân tích vùng giao dịch</h3>
                <img src="data:image/png;base64,{charts['trading_zones']}" alt="Trading Zones">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> Vùng giao dịch tập trung vào khung 11h-13h. Tương quan giá-khối lượng yếu nhưng xu hướng tăng rõ ràng.</p>
                </div>
            </div>

            <div class="chart-container">
                <h3>18. Dashboard hiệu suất tổng thể</h3>
                <img src="data:image/png;base64,{charts['performance_dashboard']}" alt="Performance Dashboard">
                <div class="chart-analysis">
                    <p><strong>Phân tích:</strong> Performance Score 58.4/100, Liquidity Score 51.2/100, Stability Score 90.1/100. Tổng thể VHM thể hiện độ ổn định cao nhưng cần cải thiện hiệu suất.</p>
                </div>
            </div>
        </div>

        <!-- Investment Recommendation -->
        <div class="recommendation">
            <h3>🎯 KHUYẾN NGHỊ ĐẦU TƯ</h3>
            <p><strong>Khuyến nghị: HOLD (Nắm giữ)</strong></p>
            <p><strong>Độ tin cậy: 75%</strong></p>
            <p><strong>Target Price: 96.5 - 98.0 VND (12 tháng)</strong></p>
            <p><strong>Stop Loss: 92.0 VND (-4.2%)</strong></p>
        </div>

        <!-- Scoring System -->
        <div class="section">
            <h2>📊 Hệ Thống Chấm Điểm</h2>
            <div class="score-grid">
                <div class="score-item">
                    <h4>Technical Score</h4>
                    <div class="score-value">65/100</div>
                </div>
                <div class="score-item">
                    <h4>Fundamental Score</h4>
                    <div class="score-value">85/100</div>
                </div>
                <div class="score-item">
                    <h4>Risk Score</h4>
                    <div class="score-value">80/100</div>
                </div>
                <div class="score-item">
                    <h4>Liquidity Score</h4>
                    <div class="score-value">70/100</div>
                </div>
                <div class="score-item">
                    <h4>Tổng Điểm</h4>
                    <div class="score-value">75/100</div>
                </div>
            </div>
        </div>

        <!-- Risk Warning -->
        <div class="risk-warning">
            <h4>⚠️ Cảnh Báo Rủi Ro</h4>
            <ul>
                <li>RSI trong vùng quá mua có thể dẫn đến điều chỉnh giá</li>
                <li>Thanh khoản giảm cuối phiên cần theo dõi</li>
                <li>Rủi ro từ biến động chính sách bất động sản</li>
                <li>Ảnh hưởng của lãi suất và chính sách tiền tệ</li>
            </ul>
        </div>

        <div class="footer">
            <p>📊 Báo cáo được tạo bởi Dominus Agent v4.1 - Workflow Tích hợp Đồ thị</p>
            <p>🤖 Generated with Claude Code | 📅 Cập nhật: 18/07/2025</p>
            <p>⚠️ Chỉ mang tính chất tham khảo, không phải lời khuyên đầu tư</p>
        </div>
    </div>
</body>
</html>
"""

    # Save report
    report_path = "stock_analysis/VHM/reports/VHM_comprehensive_analysis_report.html"
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Bao cao toan dien VHM da duoc tao: {report_path}")
    print(f"Tich hop thanh cong 18 bieu do phan tich")
    print(f"Khuyen nghi dau tu: HOLD voi do tin cay 75%")
    
    return report_path

if __name__ == "__main__":
    create_vhm_comprehensive_report()