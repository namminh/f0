@echo off
REM Quick Portfolio Update - Cập nhật nhanh toàn bộ danh mục

echo ====================================
echo VNStock Quick Portfolio Update
echo ====================================

cd /d "%~dp0\.."

echo Updating all active stocks...
python automation\multi_stock_updater.py --all

echo.
echo Update completed!
echo Check reports at: stock_analysis\[SYMBOL]\reports\
pause