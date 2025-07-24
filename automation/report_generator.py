import argparse
import shutil
from pathlib import Path

def generate_report(symbol, comprehensive=False):
    """Tạo báo cáo cho một mã cổ phiếu."""
    report_dir = Path(f"stock_analysis/{symbol.upper()}/reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    if comprehensive:
        source_report = report_dir / f"{symbol.upper()}_comprehensive_report.html"
        dest_report = report_dir / f"{symbol.upper()}_final_comprehensive_report.html"
    else:
        source_report = report_dir / f"{symbol.upper()}_analysis_report.html"
        dest_report = report_dir / f"{symbol.upper()}_final_analysis_report.html"

    if source_report.exists():
        shutil.copy(source_report, dest_report)
        print(f"Generated report: {dest_report}")
    else:
        print(f"Source report not found: {source_report}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate stock reports.')
    parser.add_argument("symbol", help="Stock symbol")
    parser.add_argument("--comprehensive", action="store_true", help="Generate comprehensive report")
    args = parser.parse_args()

    generate_report(args.symbol, args.comprehensive)
