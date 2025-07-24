@echo off
REM Windows Task Scheduler Script for VNStock Auto Update
REM Chạy file này để bắt đầu tự động cập nhật

echo ====================================
echo VNStock Multi-Stock Auto Updater
echo ====================================

cd /d "%~dp0\.."

echo Starting VNStock automation system...
echo Press Ctrl+C to stop

python automation\multi_stock_updater.py --schedule

pause