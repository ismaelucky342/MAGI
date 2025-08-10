@echo off
echo ================================================
echo 🧙 MAGI Node Windows Installer v2.0.0
echo ================================================
echo Installing MAGI Node...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ first
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create installation directory
set INSTALL_DIR=C:\Program Files\MAGI
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

REM Copy files
echo 📁 Copying files...
copy /Y "magi-node-v2.py" "%INSTALL_DIR%\"
copy /Y "magi_launcher.py" "%INSTALL_DIR%\"
if exist "power-save-mode.py" (
    copy /Y "power-save-mode.py" "%INSTALL_DIR%\"
)
if exist "images" (
    xcopy /E /I /Y "images" "%INSTALL_DIR%\images"
)

REM Create batch launcher
echo 🚀 Creating launcher...
echo @echo off > "%INSTALL_DIR%\MAGI_Node.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%\MAGI_Node.bat"
echo python magi_launcher.py >> "%INSTALL_DIR%\MAGI_Node.bat"

REM Create PowerShell launcher (alternative)
echo 💫 Creating PowerShell launcher...
echo Set-Location -Path "%INSTALL_DIR%" > "%INSTALL_DIR%\MAGI_Node.ps1"
echo python magi_launcher.py >> "%INSTALL_DIR%\MAGI_Node.ps1"

REM Create desktop shortcut
echo 🖥️ Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\MAGI Node.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\MAGI_Node.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

REM Create start menu shortcut
echo 📋 Creating start menu entry...
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\MAGI" (
    mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\MAGI"
)
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\MAGI\MAGI Node.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\MAGI_Node.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

REM Install Python dependencies
echo 📦 Installing Python dependencies...
python -m pip install psutil --quiet

REM Create uninstaller
echo 🗑️ Creating uninstaller...
echo @echo off > "%INSTALL_DIR%\Uninstall_MAGI.bat"
echo echo Uninstalling MAGI Node... >> "%INSTALL_DIR%\Uninstall_MAGI.bat"
echo rd /s /q "%INSTALL_DIR%" >> "%INSTALL_DIR%\Uninstall_MAGI.bat"
echo del "%USERPROFILE%\Desktop\MAGI Node.lnk" >> "%INSTALL_DIR%\Uninstall_MAGI.bat"
echo rd /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\MAGI" >> "%INSTALL_DIR%\Uninstall_MAGI.bat"
echo echo MAGI Node uninstalled >> "%INSTALL_DIR%\Uninstall_MAGI.bat"
echo pause >> "%INSTALL_DIR%\Uninstall_MAGI.bat"

echo.
echo ✅ MAGI Node installed successfully!
echo.
echo 🚀 You can now start MAGI Node from:
echo    - Desktop shortcut: "MAGI Node"
echo    - Start Menu: Programs ^> MAGI ^> MAGI Node
echo    - Direct run: %INSTALL_DIR%\MAGI_Node.bat
echo.
echo 🌐 Access dashboard at: http://localhost:8080
echo 🗑️ To uninstall: %INSTALL_DIR%\Uninstall_MAGI.bat
echo.
pause
