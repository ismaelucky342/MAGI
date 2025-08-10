@echo off
REM 🧙‍♂️ MAGI Windows Installer - Ultra-Simple Setup
REM Installs MAGI as Windows Service with desktop shortcut

echo.
echo 🧙‍♂️ ═══════════════════════════════════════════════════════════════
echo     MAGI Windows Installation - Distributed Monitoring System
echo ═══════════════════════════════════════════════════════════════
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.6+ from https://python.org
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found:
python --version

REM Get current directory
set "MAGI_HOME=%~dp0"
set "MAGI_HOME=%MAGI_HOME:~0,-1%"

echo 📁 Installation directory: %MAGI_HOME%

REM Ask for node name
echo.
echo 🎯 Choose your MAGI node:
echo    1. GASPAR  - Multimedia ^& Entertainment Node
echo    2. MELCHIOR - Backup ^& Storage Node
echo    3. BALTASAR - Home Automation Node
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" set "MAGI_NODE=GASPAR"
if "%choice%"=="2" set "MAGI_NODE=MELCHIOR"
if "%choice%"=="3" set "MAGI_NODE=BALTASAR"

if "%MAGI_NODE%"=="" (
    echo ❌ Invalid choice. Defaulting to GASPAR
    set "MAGI_NODE=GASPAR"
)

echo ✅ Selected node: %MAGI_NODE%

REM Test MAGI file
if not exist "%MAGI_HOME%\magi-node.py" (
    echo ❌ magi-node.py not found in %MAGI_HOME%
    echo    Please run this installer from the MAGI directory
    pause
    exit /b 1
)

echo ✅ magi-node.py found

REM Create Windows service wrapper
echo 🔧 Creating Windows service wrapper...

set "SERVICE_NAME=MAGI_%MAGI_NODE%"
set "SERVICE_SCRIPT=%MAGI_HOME%\magi-service.py"

REM Create Python service wrapper
(
echo import sys
echo import os
echo import time
echo import subprocess
echo import win32serviceutil
echo import win32service
echo import win32event
echo import servicemanager
echo.
echo class MAGIService^(win32serviceutil.ServiceFramework^):
echo     _svc_name_ = "%SERVICE_NAME%"
echo     _svc_display_name_ = "🧙‍♂️ MAGI %MAGI_NODE% Monitoring Node"
echo     _svc_description_ = "MAGI Distributed Monitoring System - %MAGI_NODE% Node"
echo.
echo     def __init__^(self, args^):
echo         win32serviceutil.ServiceFramework.__init__^(self, args^)
echo         self.hWaitStop = win32event.CreateEvent^(None, 0, 0, None^)
echo         self.process = None
echo.
echo     def SvcStop^(self^):
echo         self.ReportServiceStatus^(win32service.SERVICE_STOP_PENDING^)
echo         if self.process:
echo             self.process.terminate^(^)
echo         win32event.SetEvent^(self.hWaitStop^)
echo.
echo     def SvcDoRun^(self^):
echo         servicemanager.LogMsg^(servicemanager.EVENTLOG_INFORMATION_TYPE,
echo                               servicemanager.PYS_SERVICE_STARTED,
echo                               ^(self._svc_name_, ''^^)
echo         self.main^(^)
echo.
echo     def main^(self^):
echo         os.chdir^(r"%MAGI_HOME%"^)
echo         while True:
echo             try:
echo                 self.process = subprocess.Popen^([
echo                     sys.executable, "magi-node.py", "%MAGI_NODE%"
echo                 ]^)
echo                 self.process.wait^(^)
echo             except Exception as e:
echo                 servicemanager.LogErrorMsg^(f"MAGI service error: {e}"^)
echo                 time.sleep^(5^)
echo.
echo             rc = win32event.WaitForSingleObject^(self.hWaitStop, 5000^)
echo             if rc == win32event.WAIT_OBJECT_0:
echo                 break
echo.
echo if __name__ == '__main__':
echo     win32serviceutil.HandleCommandLine^(MAGIService^)
) > "%SERVICE_SCRIPT%"

echo ✅ Service wrapper created

REM Create simple batch launcher (backup method)
echo 🔧 Creating launcher scripts...

set "LAUNCHER_SCRIPT=%MAGI_HOME%\start-magi-%MAGI_NODE%.bat"
(
echo @echo off
echo title 🧙‍♂️ MAGI %MAGI_NODE% Node
echo cd /d "%MAGI_HOME%"
echo echo 🧙‍♂️ Starting MAGI %MAGI_NODE%...
echo echo 🌐 Dashboard: http://localhost:8081
echo echo.
echo python magi-node.py %MAGI_NODE%
echo pause
) > "%LAUNCHER_SCRIPT%"

echo ✅ Launcher script created: %LAUNCHER_SCRIPT%

REM Create auto-start batch file
set "AUTOSTART_SCRIPT=%MAGI_HOME%\magi-autostart.bat"
(
echo @echo off
echo REM Auto-start MAGI service
echo cd /d "%MAGI_HOME%"
echo start /min python magi-node.py %MAGI_NODE%
echo exit
) > "%AUTOSTART_SCRIPT%"

REM Create desktop shortcut
echo 🖥️ Creating desktop shortcut...

set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\MAGI %MAGI_NODE%.lnk"

REM Create VBS script to make shortcut
set "VBS_SCRIPT=%TEMP%\magi_shortcut.vbs"
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%SHORTCUT%"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "http://localhost:8081"
echo oLink.Description = "🧙‍♂️ MAGI %MAGI_NODE% Dashboard"
echo oLink.WorkingDirectory = "%MAGI_HOME%"
echo oLink.Save
) > "%VBS_SCRIPT%"

cscript //nologo "%VBS_SCRIPT%" >nul 2>&1
del "%VBS_SCRIPT%" >nul 2>&1

if exist "%SHORTCUT%" (
    echo ✅ Desktop shortcut created
) else (
    echo ⚠️  Desktop shortcut creation failed, but launcher script is available
)

REM Add to Windows startup (optional)
echo.
set /p startup="Add MAGI to Windows startup? (y/n): "
if /i "%startup%"=="y" (
    set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
    copy "%AUTOSTART_SCRIPT%" "%STARTUP_FOLDER%\MAGI_%MAGI_NODE%.bat" >nul
    echo ✅ Added to Windows startup
)

REM Try to install as Windows service (requires pywin32)
echo.
echo 🔧 Attempting to install Windows service...
pip install pywin32 >nul 2>&1
if %errorlevel% equ 0 (
    python "%SERVICE_SCRIPT%" install >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Windows service installed: %SERVICE_NAME%
        net start "%SERVICE_NAME%" >nul 2>&1
        if %errorlevel% equ 0 (
            echo ✅ Service started successfully
        ) else (
            echo ⚠️  Service installed but failed to start
            echo    Use the launcher script instead
        )
    ) else (
        echo ⚠️  Service installation failed
        echo    Use the launcher script instead
    )
) else (
    echo ⚠️  pywin32 installation failed
    echo    Service installation skipped
)

REM Configure Windows Firewall
echo 🔥 Configuring Windows Firewall...
netsh advfirewall firewall add rule name="MAGI %MAGI_NODE%" dir=in action=allow protocol=TCP localport=8081 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Firewall rule added for port 8081
) else (
    echo ⚠️  Firewall rule creation failed ^(may need admin rights^)
    echo    Manually allow port 8081 in Windows Firewall if needed
)

REM Final test
echo.
echo 🧪 Testing MAGI installation...
timeout /t 2 /nobreak >nul
start /b python "%MAGI_HOME%\magi-node.py" %MAGI_NODE% >nul 2>&1
timeout /t 3 /nobreak >nul

curl -s http://localhost:8081/api/info >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ MAGI is responding correctly
    taskkill /f /im python.exe >nul 2>&1
) else (
    echo ⚠️  Test connection failed, but installation completed
)

echo.
echo 🎉 MAGI %MAGI_NODE% Installation Complete!
echo ════════════════════════════════════════
echo.
echo 🚀 Quick Start Options:
echo    1. Double-click: "%LAUNCHER_SCRIPT%"
echo    2. Desktop shortcut: "MAGI %MAGI_NODE%"
echo    3. Command line: python magi-node.py %MAGI_NODE%
echo.
echo 🌐 Dashboard URL: http://localhost:8081
echo 📁 Installation: %MAGI_HOME%
echo.
echo 🔧 Management:
echo    Start service: net start "%SERVICE_NAME%"
echo    Stop service:  net stop "%SERVICE_NAME%"
echo.
echo 🧙‍♂️ The MAGI system is ready for Windows!
echo.
pause
