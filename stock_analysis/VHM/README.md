# Phân tích cổ phiếu VHM

## Cấu trúc thư mục

### 📁 data/
- `VHM_financial_data.json`: Dữ liệu tài chính đầy đủ
- `VHM_intraday_data.json`: Dữ liệu giao dịch trong ngày
- `VHM_intraday.csv`: Dữ liệu intraday dạng CSV
- `VHM_data.json`: Dữ liệu tổng hợp

### 📊 charts/
- `detailed_charts/`: Biểu đồ chi tiết (6 biểu đồ)
  - `price_intraday.png`: Biến động giá trong ngày
  - `volume_analysis.png`: Phân tích khối lượng
  - `buy_sell_analysis.png`: Áp lực mua/bán
  - `liquidity_analysis.png`: Thanh khoản
  - `financial_analysis.png`: Phân tích tài chính
  - `comparison_analysis.png`: So sánh tổng hợp

- `key_charts/`: Biểu đồ quan trọng (3 biểu đồ)
  - `price_trend.png`: Xu hướng giá
  - `volume_by_hour.png`: Khối lượng theo giờ
  - `buy_vs_sell.png`: Mua vs bán

### 📋 reports/
- `VHM_analysis_report.html`: Báo cáo HTML tổng hợp

### 🔍 analysis/
- `run_vhm_analysis.py`: Script lấy dữ liệu tài chính
- `get_vhm_intraday.py`: Script lấy dữ liệu intraday
- `final_vhm_analysis.py`: Phân tích tổng hợp
- `combined_vhm_analysis.py`: Phân tích kết hợp
- `vhm_chart_analysis.py`: Tạo biểu đồ

## Cách sử dụng

1. **Xem báo cáo**: Mở file `reports/VHM_analysis_report.html`
2. **Xem biểu đồ**: Vào thư mục `charts/`
3. **Xem dữ liệu**: Vào thư mục `data/`
4. **Chạy phân tích**: Vào thư mục `analysis/`

## Kết quả phân tích

### Tóm tắt (VHM)
- **Khuyến nghị**: TÍCH CỰC - Có thể xem xét mua
- **Xu hướng**: Tăng giá +4.61%
- **Thanh khoản**: Tốt (0.18% cổ phiếu lưu hành)
- **Áp lực**: Mua > Bán (56.3% vs 43.7%)

### Điểm mạnh
- Xu hướng tăng giá rõ ràng
- Thanh khoản tốt
- Hoạt động giao dịch sôi động
- Tăng trưởng tài chính ổn định

### Cần lưu ý
- Theo dõi tỷ lệ nợ (60.9%)
- Biến động thị trường BDS
- Tình hình kinh tế vĩ mô
