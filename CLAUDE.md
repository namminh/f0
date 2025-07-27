# VNStock Automation System - Agent Instructions

## Hệ thống Tự động Phân tích Cổ phiếu VNStock

Đây là hướng dẫn hoàn chỉnh để Claude agent có thể làm việc hiệu quả với hệ thống VNStock.

## 🎯 Mục tiêu hệ thống
- Tự động cập nhật dữ liệu intraday cho nhiều cổ phiếu
- Tạo phân tích và biểu đồ tự động
- Tạo báo cáo HTML cho từng cổ phiếu
- Quản lý và theo dõi danh mục cổ phiếu

## 📁 Cấu trúc thư mục chuẩn

```
VNstock/
├── stock_analysis/
│   ├── [SYMBOL]/                    # VD: VIX, HSG, VCB
│   │   ├── data/
│   │   │   ├── [SYMBOL]_intraday_data.json
│   │   │   ├── [SYMBOL]_balance_sheet.json
│   │   │   ├── [SYMBOL]_income_statement.json
│   │   │   └── [SYMBOL]_financial_ratios.json
│   │   ├── analysis/
│   │   │   ├── analyze_[symbol]_data.py
│   │   │   └── create_[symbol]_charts.py
│   │   ├── charts/
│   │   │   ├── key_charts/           # 3 biểu đồ chính
│   │   │   └── detailed_charts/      # 6 biểu đồ chi tiết
│   │   └── reports/
│   │       └── [SYMBOL]_analysis_report.html
│   └── config/
│       ├── stocks_config.json       # Cấu hình cổ phiếu
│       └── update_schedule.json     # Lịch cập nhật
├── automation/
│   ├── multi_stock_updater.py       # Script cập nhật nhiều CP
│   ├── portfolio_manager.py         # Quản lý danh mục
│   └── report_generator.py          # Tạo báo cáo tổng hợp
├── stock_data_collector.py          # Core data collector
├── quick_update.py                  # Cập nhật nhanh
├── batch_update.py                  # Cập nhật đầy đủ
└── CLAUDE.md                        # File này
```

## 🔧 Core Commands - Lệnh cơ bản

### 1. Phân tích hoàn chỉnh (MỚI - KHUYẾN NGHỊ)
```bash
# Phân tích nâng cao 1 cổ phiếu (bao gồm cập nhật data + tạo charts + báo cáo HTML)
python quick_analyze.py VIX

# Output: stock_analysis/VIX/reports/VIX_enhanced_report.html
```

### 2. Cập nhật dữ liệu (CŨ)
```bash
# Cập nhật 1 cổ phiếu
python quick_update.py VIX

# Cập nhật nhiều cổ phiếu
python quick_update.py VIX HSG VCB

# Cập nhật tất cả cổ phiếu có sẵn
python quick_update.py

# Cập nhật đầy đủ với biểu đồ
python batch_update.py
```

### 2. Tạo phân tích cho cổ phiếu mới
```bash
# Lấy dữ liệu ban đầu
python get_data_for_stock.py [SYMBOL]

# Tạo cấu trúc thư mục và files
python automation/portfolio_manager.py --add [SYMBOL]
```

### 3. Chạy phân tích
```bash
# Phân tích 1 cổ phiếu
python stock_analysis/[SYMBOL]/analysis/analyze_[symbol]_data.py

# Tạo biểu đồ
python stock_analysis/[SYMBOL]/analysis/create_[symbol]_charts.py

# Tạo báo cáo tổng hợp
python automation/report_generator.py
```

## 🤖 Agent Workflow - Quy trình cho Agent

### Khi user yêu cầu phân tích 1 cổ phiếu:
1. **MỚI - Phân tích nâng cao**: `python quick_analyze.py [SYMBOL]`
2. **Cũ - Cập nhật cơ bản**: `python quick_update.py [SYMBOL]`
3. **Cũ - Phân tích thủ công**: `python stock_analysis/[SYMBOL]/analysis/analyze_[symbol]_data.py`

### Khi user yêu cầu thêm cổ phiếu mới:
1. Chạy `python automation/portfolio_manager.py --add [SYMBOL]`
2. Chạy `python get_data_for_stock.py [SYMBOL]`
3. Kiểm tra cấu trúc thư mục đã tạo
4. Test cập nhật: `python quick_update.py [SYMBOL]`

### Khi user yêu cầu cập nhật toàn bộ danh mục:
1. Chạy `python automation/multi_stock_updater.py --all`
2. Chạy `python automation/report_generator.py`
3. Báo cáo tổng quan

### Khi user yêu cầu tự động hóa:
1. Chạy `python automation/multi_stock_updater.py --schedule`
2. Hoặc setup Windows Task Scheduler với `automation/windows_scheduler.bat`

## 📊 Data Analysis Standards

### Intraday Analysis Format:
- **Thời gian giao dịch**: Start - End time
- **Số điểm dữ liệu**: Total data points
- **Giá**: Min, Max, Average
- **Khối lượng**: Total volume, by hour breakdown
- **Tỷ lệ mua/bán**: Buy/Sell ratio
- **Độ biến động**: Standard deviation

### Chart Requirements:
**Key Charts (3):**
1. `price_trend.png` - Biểu đồ giá theo thời gian
2. `volume_by_hour.png` - Khối lượng theo giờ
3. `buy_vs_sell.png` - Tỷ lệ mua/bán

**Detailed Charts (6):**
1. `financial_analysis.png` - Phân tích tài chính
2. `income_statement_analysis.png` - Kết quả kinh doanh
3. `financial_ratios_analysis.png` - Tỷ số tài chính
4. `price_volume_correlation.png` - Tương quan giá/khối lượng
5. `volatility_analysis.png` - Phân tích độ biến động
6. `technical_indicators.png` - Chỉ báo kỹ thuật

## 🔄 Error Handling

### Common Issues & Solutions:
1. **File not found**: Chạy `python get_data_for_stock.py [SYMBOL]`
2. **No data**: Kiểm tra symbol có đúng không, thử lại sau
3. **Unicode error**: Files đã được fix encoding UTF-8
4. **Permission error**: Chạy với quyền administrator

### Debug Commands:
```bash
# Kiểm tra danh sách cổ phiếu có sẵn
python -c "from pathlib import Path; print([d.name for d in Path('stock_analysis').iterdir() if d.is_dir()])"

# Kiểm tra dữ liệu mới nhất
python -c "import json; print(json.load(open('stock_analysis/VIX/data/VIX_intraday_data.json'))['timestamp'])"

# Test data collector
python -c "from stock_data_collector import StockDataCollector; print(StockDataCollector().get_intraday_data('VIX')['data_points'])"
```

## 🎨 Report Generation

### HTML Report Structure:
- **Key Metrics Cards**: 4 metrics chính
- **Intraday Summary**: Phân tích ngày hôm nay
- **Charts Display**: Hiển thị tất cả biểu đồ
- **Technical Analysis**: Phân tích kỹ thuật
- **Recommendations**: Khuyến nghị đầu tư

### Auto-Update Report:
```bash
# Cập nhật báo cáo cho 1 cổ phiếu
python automation/report_generator.py --symbol VIX

# Tạo báo cáo tổng hợp
python automation/report_generator.py --portfolio
```

## 🔐 Configuration Management

### stocks_config.json format:
```json
{
  "active_stocks": ["VIX", "HSG", "VCB", "TCB"],
  "update_frequency": {
    "intraday": 300,
    "full_analysis": 3600
  },
  "market_hours": {
    "start": "09:00",
    "end": "15:00"
  }
}
```

## 🚀 Performance Tips

1. **Nhanh nhất**: `quick_update.py` cho cập nhật dữ liệu
2. **Đầy đủ nhất**: `batch_update.py` cho phân tích hoàn chỉnh
3. **Tự động**: `multi_stock_updater.py --schedule` cho việc dài hạn
4. **Batch processing**: Cập nhật nhiều cổ phiếu cùng lúc

## 📝 Agent Response Templates

### Khi cập nhật thành công:
```
✅ [SYMBOL] updated successfully
📊 Data points: [NUMBER]
💰 Current price: [PRICE] VND
📈 Volume: [VOLUME]
🔄 Updated: [TIMESTAMP]
```

### Khi có lỗi:
```
❌ Error updating [SYMBOL]: [ERROR_MESSAGE]
🔧 Suggested fix: [SOLUTION]
```

### Khi tạo báo cáo:
```
📋 Analysis completed for [SYMBOL]
📈 Charts generated: [COUNT] files
📊 Report available: stock_analysis/[SYMBOL]/reports/[SYMBOL]_analysis_report.html
```

## 🎯 Success Metrics

Agent được coi là thành công khi:
- Cập nhật dữ liệu không lỗi
- Tạo được đầy đủ biểu đồ
- Báo cáo HTML hiển thị chính xác
- Timestamps được cập nhật
- Performance data chính xác

---

**📌 Lưu ý quan trọng:**
- Luôn chạy từ thư mục gốc VNstock/
- Kiểm tra file paths trước khi chạy
- Backup dữ liệu quan trọng
- Monitor API rate limits
- Kiểm tra market hours trước khi cập nhật

**🔗 Files liên quan:**
- `stock_data_collector.py` - Core functionality
- `automation/multi_stock_updater.py` - Multi-stock automation
- `automation/portfolio_manager.py` - Portfolio management
- `automation/report_generator.py` - Report generation