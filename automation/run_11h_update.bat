@echo off
REM DOMINUS AGENT - 11:00 AM Scheduled Update
REM Quick mode cho giữa phiên giao dịch

cd /d "D:\dominus_agent\VNstock"
python automation\scheduled_updater.py --time 11:00

REM Log kết quả
echo 11:00 AM Update completed at %date% %time% >> automation\logs\batch_execution.log