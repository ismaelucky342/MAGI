@echo off
REM 🧙‍♂️ MAGI Windows Simple Installer - No services, just works!

echo.
echo 🧙‍♂️ ════════════════════════════════════════════════
echo     MAGI Windows Simple Installation
echo ════════════════════════════════════════════════
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo.
    echo 📥 Please install Python from: https://python.org
    echo    ✅ Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ✅ Python found:
python --version

REM Get directory
set "MAGI_HOME=%~dp0"
set "MAGI_HOME=%MAGI_HOME:~0,-1%"

echo 📁 MAGI Directory: %MAGI_HOME%

REM Choose node
echo.
echo 🎯 Choose MAGI Node:
echo    1 = GASPAR   (Multimedia)
echo    2 = MELCHIOR (Backup)  
echo    3 = BALTASAR (Home Automation)
echo.
set /p choice="Choice (1-3): "

if "%choice%"=="1" set "NODE=GASPAR"
if "%choice%"=="2" set "NODE=MELCHIOR" 
if "%choice%"=="3" set "NODE=BALTASAR"
if "%NODE%"=="" set "NODE=GASPAR"

echo ✅ Node: %NODE%

REM Create startup script
echo 🔧 Creating startup script...
(
echo @echo off
echo title 🧙‍♂️ MAGI %NODE%
echo color 0C
echo echo.
echo echo 🧙‍♂️ ═══════════════════════════════════════
echo echo      MAGI %NODE% Starting...
echo echo ═══════════════════════════════════════
echo echo.
echo cd /d "%MAGI_HOME%"
echo python magi-node.py %NODE%
) > "Start-MAGI-%NODE%.bat"

echo ✅ Created: Start-MAGI-%NODE%.bat

REM Create desktop shortcut script
echo 🖥️ Creating desktop access...
(
echo @echo off
echo start http://localhost:8081
echo exit
) > "Open-MAGI-Dashboard.bat"

REM Copy to desktop
copy "Start-MAGI-%NODE%.bat" "%USERPROFILE%\Desktop\" >nul 2>&1
copy "Open-MAGI-Dashboard.bat" "%USERPROFILE%\Desktop\" >nul 2>&1

if exist "%USERPROFILE%\Desktop\Start-MAGI-%NODE%.bat" (
    echo ✅ Desktop shortcuts created
) else (
    echo ⚠️  Desktop shortcuts not created, but files are in MAGI folder
)

REM Add to startup folder (optional)
echo.
set /p autostart="Start MAGI automatically with Windows? (y/n): "
if /i "%autostart%"=="y" (
    set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
    (
    echo @echo off
    echo cd /d "%MAGI_HOME%"
    echo start /min python magi-node.py %NODE%
    ) > "%STARTUP%\MAGI-%NODE%-AutoStart.bat"
    echo ✅ Auto-start enabled
)

REM Firewall rule
echo 🔥 Adding firewall rule...
netsh advfirewall firewall add rule name="MAGI" dir=in action=allow protocol=TCP localport=8081 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Firewall configured
) else (
    echo ⚠️  Run as Administrator to configure firewall
)

echo.
echo 🎉 MAGI %NODE% Ready!
echo ═══════════════════════
echo.
echo 🚀 To Start MAGI:
echo    • Double-click: Start-MAGI-%NODE%.bat
echo    • Or from Desktop shortcut
echo.
echo 🌐 To Open Dashboard:
echo    • Double-click: Open-MAGI-Dashboard.bat  
echo    • Or go to: http://localhost:8081
echo.
echo 🧙‍♂️ Installation Complete!
echo.
pause
