@echo off
REM VNStock Dashboard Launcher
REM Khởi chạy dashboard với stocks_config.json integration

echo 🚀 Starting VNStock Dashboard...
echo.

cd /d "D:\dominus_agent\VNstock"

echo 📂 Working directory: %CD%
echo ⚙️ Config file: automation\config\stocks_config.json
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

REM Kiểm tra config file
if not exist "automation\config\stocks_config.json" (
    echo ❌ Config file not found: automation\config\stocks_config.json
    echo Please ensure the config file exists.
    pause
    exit /b 1
)

REM Hiển thị stocks từ config
echo 📊 Active stocks in config:
python -c "import json; config=json.load(open('automation/config/stocks_config.json', 'r', encoding='utf-8')); print('   - ' + '\n   - '.join(config['active_stocks']))"
echo.

echo 🌐 Starting Flask server with config integration...
echo 📱 Dashboard will be available at: http://localhost:5000
echo 🔧 Features: Dynamic stock loading from config
echo.
echo Press Ctrl+C to stop the server
echo ===============================================

REM Sử dụng run_dashboard.py để đảm bảo proper setup
python run_dashboard.py

echo.
echo Server stopped.
pause