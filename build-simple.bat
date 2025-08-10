@echo off
REM 🧙‍♂️ MAGI Simple EXE Builder - Ultra Easy
REM Just double-click this file to create Windows executables!

title 🧙‍♂️ MAGI EXE Builder

echo.
echo 🧙‍♂️ ═════════════════════════════════════════════════
echo      MAGI Simple EXE Builder
echo      Creating Windows executables... 
echo ═════════════════════════════════════════════════
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

echo ✅ Python found
python --version

REM Install PyInstaller
echo.
echo 🔧 Installing PyInstaller...
pip install pyinstaller >nul 2>&1

REM Check source file
if not exist "magi-node.py" (
    echo ❌ magi-node.py not found!
    echo Please run this from the MAGI folder
    pause
    exit /b 1
)

echo ✅ Source file found

REM Create dist folder
if not exist "dist" mkdir dist

echo.
echo 🏗️  Building executables...
echo    This may take a few minutes...

REM Build GASPAR
echo.
echo 🧙‍♂️ Building MAGI-GASPAR.exe...
pyinstaller --onefile --name "MAGI-GASPAR" --distpath=dist magi-node.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ GASPAR build failed
) else (
    echo ✅ MAGI-GASPAR.exe created
)

REM Build MELCHIOR  
echo 🧙‍♂️ Building MAGI-MELCHIOR.exe...
pyinstaller --onefile --name "MAGI-MELCHIOR" --distpath=dist magi-node.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ MELCHIOR build failed
) else (
    echo ✅ MAGI-MELCHIOR.exe created
)

REM Build BALTASAR
echo 🧙‍♂️ Building MAGI-BALTASAR.exe...
pyinstaller --onefile --name "MAGI-BALTASAR" --distpath=dist magi-node.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ BALTASAR build failed
) else (
    echo ✅ MAGI-BALTASAR.exe created
)

REM Create launchers
echo.
echo 🔧 Creating launchers...

REM GASPAR launcher
(
echo @echo off
echo title 🧙‍♂️ MAGI GASPAR
echo echo 🧙‍♂️ Starting MAGI GASPAR...
echo echo 🌐 Dashboard: http://localhost:8081
echo echo.
echo MAGI-GASPAR.exe GASPAR
echo pause
) > "dist\Start-GASPAR.bat"

REM MELCHIOR launcher
(
echo @echo off
echo title 🧙‍♂️ MAGI MELCHIOR
echo echo 🧙‍♂️ Starting MAGI MELCHIOR...
echo echo 🌐 Dashboard: http://localhost:8081
echo echo.
echo MAGI-MELCHIOR.exe MELCHIOR
echo pause
) > "dist\Start-MELCHIOR.bat"

REM BALTASAR launcher
(
echo @echo off
echo title 🧙‍♂️ MAGI BALTASAR
echo echo 🧙‍♂️ Starting MAGI BALTASAR...
echo echo 🌐 Dashboard: http://localhost:8081
echo echo.
echo MAGI-BALTASAR.exe BALTASAR
echo pause
) > "dist\Start-BALTASAR.bat"

REM Dashboard opener
(
echo @echo off
echo start http://localhost:8081
) > "dist\Dashboard.bat"

echo ✅ Launchers created

REM Create simple README
(
echo 🧙‍♂️ MAGI Windows Executables
echo ═══════════════════════════════
echo.
echo 🚀 Quick Start:
echo    1. Choose your node:
echo       - Start-GASPAR.bat
echo       - Start-MELCHIOR.bat  
echo       - Start-BALTASAR.bat
echo.
echo    2. Open dashboard:
echo       - Dashboard.bat
echo       - Or go to: http://localhost:8081
echo.
echo 💡 These files work on ANY Windows computer!
echo    No Python installation needed.
echo.
echo 🧙‍♂️ The MAGI system is ready!
) > "dist\README.txt"

echo ✅ README created

REM Show results
echo.
echo 🎉 Build Complete!
echo ═══════════════════
echo.
echo 📁 Files created in 'dist' folder:
dir dist /b
echo.
echo 🚀 To use:
echo    1. Copy 'dist' folder to any Windows PC
echo    2. Double-click Start-GASPAR.bat (or MELCHIOR/BALTASAR)
echo    3. Open Dashboard.bat
echo.
echo 💾 Executable sizes:
for %%f in (dist\*.exe) do echo    %%~nf: %%~zf bytes

echo.
echo 🧙‍♂️ MAGI is now portable! 
echo.
pause

REM Open dist folder
start dist
