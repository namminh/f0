@echo off
REM DOMINUS AGENT - 15:00 PM Scheduled Update  
REM Smart mode với báo cáo cuối ngày

cd /d "D:\dominus_agent\VNstock"
python automation\scheduled_updater.py --time 15:00

REM Log kết quả
echo 15:00 PM Update completed at %date% %time% >> automation\logs\batch_execution.log