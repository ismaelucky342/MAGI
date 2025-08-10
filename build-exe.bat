@echo off
REM 🧙‍♂️ MAGI EXE Builder for Windows
REM Creates standalone executable with PyInstaller

echo.
echo 🧙‍♂️ ═══════════════════════════════════════════════════════════════
echo     MAGI EXE Builder - Creating Windows Executable
echo ═══════════════════════════════════════════════════════════════
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found:
python --version

REM Install PyInstaller if not present
echo 🔧 Installing PyInstaller...
pip install pyinstaller pillow requests >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Failed to install PyInstaller
    pause
    exit /b 1
)

echo ✅ PyInstaller installed

REM Check if magi-node.py exists
if not exist "magi-node.py" (
    echo ❌ magi-node.py not found in current directory
    pause
    exit /b 1
)

echo ✅ magi-node.py found

REM Create icon if ImageMagick available
echo 🎨 Creating icon...
if exist "magi-icon.svg" (
    REM Try to convert SVG to ICO
    convert magi-icon.svg -resize 256x256 magi-icon.ico >nul 2>&1
    if exist "magi-icon.ico" (
        echo ✅ Icon created: magi-icon.ico
        set "ICON_OPTION=--icon=magi-icon.ico"
    ) else (
        echo ⚠️  Icon conversion failed, using default
        set "ICON_OPTION="
    )
) else (
    echo ⚠️  magi-icon.svg not found, using default icon
    set "ICON_OPTION="
)

REM Create version info file
echo 🔧 Creating version info...
(
echo VSVersionInfo^(
echo   ffi=FixedFileInfo^(
echo     filevers=^(1,0,0,0^),
echo     prodvers=^(1,0,0,0^),
echo     mask=0x3f,
echo     flags=0x0,
echo     OS=0x40004,
echo     fileType=0x1,
echo     subtype=0x0,
echo     date=^(0, 0^)
echo   ^),
echo   kids=[
echo     StringFileInfo^(
echo       [
echo       StringTable^(
echo         u'040904B0',
echo         [StringStruct^(u'CompanyName', u'MAGI Project'^),
echo         StringStruct^(u'FileDescription', u'MAGI Distributed Monitoring System'^),
echo         StringStruct^(u'FileVersion', u'1.0.0.0'^),
echo         StringStruct^(u'InternalName', u'MAGI'^),
echo         StringStruct^(u'LegalCopyright', u'Copyright © 2025 MAGI Project'^),
echo         StringStruct^(u'OriginalFilename', u'MAGI.exe'^),
echo         StringStruct^(u'ProductName', u'MAGI Distributed Monitoring'^),
echo         StringStruct^(u'ProductVersion', u'1.0.0.0'^)^]^)
echo       ^]^),
echo     VarFileInfo^([VarStruct^(u'Translation', [1033, 1200]^)^]^)
echo   ^]
echo ^)
) > version.txt

echo ✅ Version info created

REM Build GASPAR executable
echo 🧙‍♂️ Building MAGI GASPAR executable...
pyinstaller --onefile --windowed --name "MAGI-GASPAR" %ICON_OPTION% --version-file=version.txt --distpath=dist --workpath=build --specpath=build magi-node.py
if %errorlevel% neq 0 (
    echo ❌ Failed to build GASPAR executable
    pause
    exit /b 1
)

echo ✅ GASPAR executable created

REM Build MELCHIOR executable  
echo 🧙‍♂️ Building MAGI MELCHIOR executable...
pyinstaller --onefile --windowed --name "MAGI-MELCHIOR" %ICON_OPTION% --version-file=version.txt --distpath=dist --workpath=build --specpath=build magi-node.py
if %errorlevel% neq 0 (
    echo ❌ Failed to build MELCHIOR executable
    pause
    exit /b 1
)

echo ✅ MELCHIOR executable created

REM Build BALTASAR executable
echo 🧙‍♂️ Building MAGI BALTASAR executable...
pyinstaller --onefile --windowed --name "MAGI-BALTASAR" %ICON_OPTION% --version-file=version.txt --distpath=dist --workpath=build --specpath=build magi-node.py
if %errorlevel% neq 0 (
    echo ❌ Failed to build BALTASAR executable
    pause
    exit /b 1
)

echo ✅ BALTASAR executable created

REM Build universal installer executable
echo 🧙‍♂️ Building Universal Installer executable...
pyinstaller --onefile --name "MAGI-Installer" %ICON_OPTION% --version-file=version.txt --distpath=dist --workpath=build --specpath=build install-universal.py
if %errorlevel% neq 0 (
    echo ❌ Failed to build installer executable
    pause
    exit /b 1
)

echo ✅ Installer executable created

REM Create launchers with arguments
echo 🔧 Creating node launchers...

REM GASPAR launcher
(
echo @echo off
echo title 🧙‍♂️ MAGI GASPAR Node
echo echo 🧙‍♂️ Starting MAGI GASPAR...
echo echo 🌐 Dashboard: http://localhost:8081
echo echo.
echo "%~dp0MAGI-GASPAR.exe" GASPAR
echo pause
) > "dist\Start-MAGI-GASPAR.bat"

REM MELCHIOR launcher
(
echo @echo off
echo title 🧙‍♂️ MAGI MELCHIOR Node
echo echo 🧙‍♂️ Starting MAGI MELCHIOR...
echo echo 🌐 Dashboard: http://localhost:8081
echo echo.
echo "%~dp0MAGI-MELCHIOR.exe" MELCHIOR
echo pause
) > "dist\Start-MAGI-MELCHIOR.bat"

REM BALTASAR launcher
(
echo @echo off
echo title 🧙‍♂️ MAGI BALTASAR Node
echo echo 🧙‍♂️ Starting MAGI BALTASAR...
echo echo 🌐 Dashboard: http://localhost:8081
echo echo.
echo "%~dp0MAGI-BALTASAR.exe" BALTASAR
echo pause
) > "dist\Start-MAGI-BALTASAR.bat"

REM Dashboard opener
(
echo @echo off
echo echo 🌐 Opening MAGI Dashboard...
echo start http://localhost:8081
echo exit
) > "dist\Open-MAGI-Dashboard.bat"

echo ✅ Launcher scripts created

REM Copy additional files
echo 📁 Copying additional files...
if exist "README-Windows.md" copy "README-Windows.md" "dist\" >nul
if exist "magi.conf" copy "magi.conf" "dist\" >nul
if exist "magi-icon.svg" copy "magi-icon.svg" "dist\" >nul
if exist "magi-icon.ico" copy "magi-icon.ico" "dist\" >nul

echo ✅ Additional files copied

REM Create distribution README
(
echo # 🧙‍♂️ MAGI Windows Executables
echo.
echo This folder contains standalone MAGI executables for Windows.
echo No Python installation required!
echo.
echo ## 🚀 Quick Start
echo.
echo 1. Choose your node:
echo    - Double-click `Start-MAGI-GASPAR.bat` for multimedia node
echo    - Double-click `Start-MAGI-MELCHIOR.bat` for backup node  
echo    - Double-click `Start-MAGI-BALTASAR.bat` for automation node
echo.
echo 2. Open dashboard:
echo    - Double-click `Open-MAGI-Dashboard.bat`
echo    - Or go to: http://localhost:8081
echo.
echo ## 📁 Files
echo.
echo - `MAGI-*.exe` - Standalone executables
echo - `Start-MAGI-*.bat` - Easy launchers
echo - `Open-MAGI-Dashboard.bat` - Dashboard opener
echo - `MAGI-Installer.exe` - Universal installer
echo.
echo ## 🔧 Advanced Usage
echo.
echo Run directly from command line:
echo ```
echo MAGI-GASPAR.exe GASPAR
echo MAGI-MELCHIOR.exe MELCHIOR
echo MAGI-BALTASAR.exe BALTASAR
echo ```
echo.
echo 🧙‍♂️ The MAGI system is ready for deployment!
) > "dist\README.txt"

echo ✅ Distribution README created

REM Show results
echo.
echo 🎉 MAGI Windows Executables Created Successfully!
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📁 Location: %cd%\dist\
echo.
echo 📋 Created files:
dir dist\*.exe dist\*.bat /b
echo.
echo 💾 Executable sizes:
for %%f in (dist\*.exe) do (
    echo    %%~nf: %%~zf bytes
)
echo.
echo 🚀 Distribution ready! Copy the 'dist' folder to any Windows machine.
echo 🌐 No Python installation required on target machines!
echo.
echo 🧙‍♂️ The MAGI system is now portable!
pause
