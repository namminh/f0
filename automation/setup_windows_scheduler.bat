@echo off
REM DOMINUS AGENT - Setup Windows Task Scheduler
REM Tự động tạo các task cho 11:00 và 15:00

echo 🚀 Setting up Windows Task Scheduler for DOMINUS AGENT...
echo.

REM Xóa task cũ nếu có
schtasks /delete /tn "DOMINUS_AGENT_11H" /f >nul 2>&1
schtasks /delete /tn "DOMINUS_AGENT_15H" /f >nul 2>&1

echo ⏰ Creating 11:00 AM task (Quick Update)...
schtasks /create ^
    /tn "DOMINUS_AGENT_11H" ^
    /tr "\"D:\dominus_agent\VNstock\automation\run_11h_update.bat\"" ^
    /sc daily ^
    /st 11:00 ^
    /ru SYSTEM ^
    /rl highest ^
    /f

if %errorlevel%==0 (
    echo ✅ 11:00 AM task created successfully
) else (
    echo ❌ Failed to create 11:00 AM task
)

echo.
echo ⏰ Creating 15:00 PM task (Smart Update + Daily Report)...
schtasks /create ^
    /tn "DOMINUS_AGENT_15H" ^
    /tr "\"D:\dominus_agent\VNstock\automation\run_15h_update.bat\"" ^
    /sc daily ^
    /st 15:00 ^
    /ru SYSTEM ^
    /rl highest ^
    /f

if %errorlevel%==0 (
    echo ✅ 15:00 PM task created successfully
) else (
    echo ❌ Failed to create 15:00 PM task
)

echo.
echo 📋 Listing created tasks:
schtasks /query /tn "DOMINUS_AGENT_11H" /fo table
schtasks /query /tn "DOMINUS_AGENT_15H" /fo table

echo.
echo 🎯 Setup completed! Tasks will run automatically at:
echo    - 11:00 AM: Quick update cho tất cả cổ phiếu trong config
echo    - 15:00 PM: Smart analysis + báo cáo cuối ngày
echo.
echo 🔧 To manually run:
echo    schtasks /run /tn "DOMINUS_AGENT_11H"
echo    schtasks /run /tn "DOMINUS_AGENT_15H"
echo.
echo 🗑️ To remove:
echo    schtasks /delete /tn "DOMINUS_AGENT_11H" /f
echo    schtasks /delete /tn "DOMINUS_AGENT_15H" /f
echo.

pause