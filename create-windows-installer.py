#!/usr/bin/env python3
"""
MAGI Windows Installer Creator
Creates a simple one-click installer for Windows
"""

import os
import sys
import shutil
import json
from pathlib import Path

# Configuration
MAGI_VERSION = "2.0.0"

def create_launcher_script():
    """Create main launcher script for Windows"""
    launcher_content = '''#!/usr/bin/env python3
"""
MAGI Node Launcher for Windows
Auto-detects configuration and starts MAGI node
"""

import os
import sys
import json
import socket
import subprocess
import time

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def find_available_port(start_port=8080):
    """Find available port starting from start_port"""
    for port in range(start_port, start_port + 20):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', port))
            sock.close()
            return port
        except OSError:
            continue
    return 8080

def detect_node_name():
    """Auto-detect node name based on hostname"""
    hostname = socket.gethostname().upper()
    
    # MAGI node names
    magi_nodes = ["GASPAR", "MELCHIOR", "BALTASAR"]
    
    # Check if hostname contains a MAGI node name
    for node in magi_nodes:
        if node in hostname:
            return node
            
    # Default based on IP last octet
    try:
        ip = get_local_ip()
        last_octet = int(ip.split('.')[-1])
        if last_octet % 3 == 0:
            return "GASPAR"
        elif last_octet % 3 == 1:
            return "MELCHIOR"
        else:
            return "BALTASAR"
    except:
        return "GASPAR"

def main():
    print("🧙 Starting MAGI Node...")
    print("=" * 50)
    
    # Auto-detect configuration
    node_name = detect_node_name()
    local_ip = get_local_ip()
    port = find_available_port()
    
    print(f"🏷️  Node Name: {node_name}")
    print(f"🌐 Local IP: {local_ip}")
    print(f"🔌 Port: {port}")
    print("=" * 50)
    
    # Import and start MAGI
    try:
        # Set environment
        os.environ['MAGI_NODE_NAME'] = node_name
        os.environ['MAGI_PORT'] = str(port)
        os.environ['MAGI_IP'] = local_ip
        
        # Start with auto-configuration
        sys.argv = ['magi_launcher.py', node_name]
        
        # Import the main module
        import importlib.util
        spec = importlib.util.spec_from_file_location("magi_node", "magi-node-v2.py")
        magi_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(magi_module)
        
    except ImportError as e:
        print(f"❌ Error importing MAGI: {e}")
        print("Please ensure magi-node-v2.py is in the same directory")
    except KeyboardInterrupt:
        print("\\n🛑 MAGI Node stopped by user")
    except Exception as e:
        print(f"❌ Error starting MAGI: {e}")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
'''
    
    with open("magi_launcher.py", "w") as f:
        f.write(launcher_content)
    print("✅ Launcher script created")

def create_installer_script():
    """Create Windows installer script"""
    installer_content = f'''@echo off
echo ================================================
echo 🧙 MAGI Node Windows Installer v{MAGI_VERSION}
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
set INSTALL_DIR=C:\\Program Files\\MAGI
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

REM Copy files
echo 📁 Copying files...
copy /Y "magi-node-v2.py" "%INSTALL_DIR%\\"
copy /Y "magi_launcher.py" "%INSTALL_DIR%\\"
if exist "power-save-mode.py" (
    copy /Y "power-save-mode.py" "%INSTALL_DIR%\\"
)
if exist "images" (
    xcopy /E /I /Y "images" "%INSTALL_DIR%\\images"
)

REM Create batch launcher
echo 🚀 Creating launcher...
echo @echo off > "%INSTALL_DIR%\\MAGI_Node.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%\\MAGI_Node.bat"
echo python magi_launcher.py >> "%INSTALL_DIR%\\MAGI_Node.bat"

REM Create PowerShell launcher (alternative)
echo 💫 Creating PowerShell launcher...
echo Set-Location -Path "%INSTALL_DIR%" > "%INSTALL_DIR%\\MAGI_Node.ps1"
echo python magi_launcher.py >> "%INSTALL_DIR%\\MAGI_Node.ps1"

REM Create desktop shortcut
echo 🖥️ Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\MAGI Node.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\MAGI_Node.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

REM Create start menu shortcut
echo 📋 Creating start menu entry...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\MAGI" (
    mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\MAGI"
)
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\MAGI\\MAGI Node.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\MAGI_Node.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

REM Install Python dependencies
echo 📦 Installing Python dependencies...
python -m pip install psutil --quiet

REM Create uninstaller
echo 🗑️ Creating uninstaller...
echo @echo off > "%INSTALL_DIR%\\Uninstall_MAGI.bat"
echo echo Uninstalling MAGI Node... >> "%INSTALL_DIR%\\Uninstall_MAGI.bat"
echo rd /s /q "%INSTALL_DIR%" >> "%INSTALL_DIR%\\Uninstall_MAGI.bat"
echo del "%USERPROFILE%\\Desktop\\MAGI Node.lnk" >> "%INSTALL_DIR%\\Uninstall_MAGI.bat"
echo rd /s /q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\MAGI" >> "%INSTALL_DIR%\\Uninstall_MAGI.bat"
echo echo MAGI Node uninstalled >> "%INSTALL_DIR%\\Uninstall_MAGI.bat"
echo pause >> "%INSTALL_DIR%\\Uninstall_MAGI.bat"

echo.
echo ✅ MAGI Node installed successfully!
echo.
echo 🚀 You can now start MAGI Node from:
echo    - Desktop shortcut: "MAGI Node"
echo    - Start Menu: Programs ^> MAGI ^> MAGI Node
echo    - Direct run: %INSTALL_DIR%\\MAGI_Node.bat
echo.
echo 🌐 Access dashboard at: http://localhost:8080
echo 🗑️ To uninstall: %INSTALL_DIR%\\Uninstall_MAGI.bat
echo.
pause
'''
    
    with open("install_magi_windows.bat", "w") as f:
        f.write(installer_content)
    print("✅ Windows installer script created")

def create_portable_launcher():
    """Create portable launcher that doesn't require installation"""
    portable_content = f'''@echo off
title MAGI Node Portable Launcher
echo ================================================
echo 🧙 MAGI Node Portable v{MAGI_VERSION}
echo ================================================
echo Starting MAGI Node from current directory...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ first
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if MAGI files exist
if not exist "magi-node-v2.py" (
    echo ❌ magi-node-v2.py not found in current directory
    pause
    exit /b 1
)

REM Install dependencies if needed
echo 📦 Checking dependencies...
python -c "import psutil" 2>nul
if errorlevel 1 (
    echo Installing psutil...
    python -m pip install psutil
)

REM Create launcher if it doesn't exist
if not exist "magi_launcher.py" (
    echo Creating launcher...
    python -c "
import socket
import os
import sys

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def find_available_port(start_port=8080):
    for port in range(start_port, start_port + 20):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', port))
            sock.close()
            return port
        except OSError:
            continue
    return 8080

def detect_node_name():
    hostname = socket.gethostname().upper()
    magi_nodes = ['GASPAR', 'MELCHIOR', 'BALTASAR']
    for node in magi_nodes:
        if node in hostname:
            return node
    try:
        ip = get_local_ip()
        last_octet = int(ip.split('.')[-1])
        if last_octet %% 3 == 0:
            return 'GASPAR'
        elif last_octet %% 3 == 1:
            return 'MELCHIOR'
        else:
            return 'BALTASAR'
    except:
        return 'GASPAR'

node_name = detect_node_name()
print(f'🧙 Starting MAGI Node: {{node_name}}')
sys.argv = ['portable', node_name]

import importlib.util
spec = importlib.util.spec_from_file_location('magi_node', 'magi-node-v2.py')
magi_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(magi_module)
"
) else (
    python magi_launcher.py
)
'''
    
    with open("MAGI_Portable.bat", "w") as f:
        f.write(portable_content)
    print("✅ Portable launcher created")

def create_simple_installer():
    """Create a simple installer package"""
    print("📦 Creating simple installer package...")
    
    # Create installer directory
    installer_dir = "MAGI_Windows_Installer"
    if os.path.exists(installer_dir):
        shutil.rmtree(installer_dir)
    os.makedirs(installer_dir)
    
    # Copy files
    files_to_copy = [
        "magi-node-v2.py",
        "power-save-mode.py",
        "install_magi_windows.bat",
        "magi_launcher.py",
        "MAGI_Portable.bat"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, installer_dir)
            print(f"   ✅ Copied {file}")
        else:
            print(f"   ⚠️  {file} not found, skipping")
    
    # Copy images if they exist
    if os.path.exists("images"):
        shutil.copytree("images", os.path.join(installer_dir, "images"))
        print("   ✅ Copied images/")
    
    # Create README
    readme_content = f'''# MAGI Node Windows Installer v{MAGI_VERSION}

## 🚀 Quick Start Options

### Option 1: Full Installation (Recommended)
1. Double-click "install_magi_windows.bat"
2. Follow the installation prompts
3. MAGI Node will be installed to C:\\Program Files\\MAGI
4. Desktop and Start Menu shortcuts will be created

### Option 2: Portable Mode
1. Double-click "MAGI_Portable.bat"
2. Runs directly from current folder (no installation)

## 🖥️ Running MAGI Node

After installation, start MAGI Node by:
- Double-clicking the desktop shortcut "MAGI Node"
- Using Start Menu > Programs > MAGI > MAGI Node
- Running C:\\Program Files\\MAGI\\MAGI_Node.bat

## 🌐 Access Dashboard

Once running, access the MAGI dashboard at:
http://localhost:8080

The node will auto-detect its name (GASPAR/MELCHIOR/BALTASAR) and find an available port.

## 📋 Requirements

- Windows 10/11
- Python 3.8+ (download from https://www.python.org/downloads/)
- Internet connection for initial setup

## 🔧 Troubleshooting

1. **Python not found**: Install Python from python.org
2. **Permission denied**: Run as Administrator
3. **Port already in use**: MAGI will auto-find an available port
4. **Dependencies missing**: Installer will auto-install psutil

## 🗑️ Uninstalling

Run: C:\\Program Files\\MAGI\\Uninstall_MAGI.bat

## 📞 Support

Visit: https://github.com/ismaelucky342/MAGI

Version: {MAGI_VERSION}
Created: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}
'''
    
    with open(os.path.join(installer_dir, "README.txt"), "w") as f:
        f.write(readme_content)
    
    # Create quick start guide
    quickstart_content = f'''🧙 MAGI Node Quick Start Guide

1. INSTALL:
   - Double-click "install_magi_windows.bat"
   - OR double-click "MAGI_Portable.bat" for portable mode

2. RUN:
   - Desktop shortcut: "MAGI Node"
   - OR Start Menu > MAGI > MAGI Node

3. ACCESS:
   - Open browser: http://localhost:8080

That's it! 🎉

Problems? Check README.txt
'''
    
    with open(os.path.join(installer_dir, "QUICK_START.txt"), "w") as f:
        f.write(quickstart_content)
    
    print(f"✅ Simple installer package created: {installer_dir}/")
    print(f"📁 Contents:")
    for file in os.listdir(installer_dir):
        print(f"   - {file}")
    
    return True

def main():
    print("=" * 60)
    print("🧙 MAGI Windows Installer Creator v" + MAGI_VERSION)
    print("=" * 60)
    print("Creating Windows installer package...")
    print()
    
    # Create all installer components
    create_launcher_script()
    create_installer_script() 
    create_portable_launcher()
    create_simple_installer()
    
    print("\n" + "=" * 60)
    print("🎉 MAGI Windows Installer Creation Complete!")
    print("=" * 60)
    print("\n📦 Created installer package: MAGI_Windows_Installer/")
    print("\n🚀 Installation options:")
    print("1. Full Install: Double-click 'install_magi_windows.bat'")
    print("2. Portable Mode: Double-click 'MAGI_Portable.bat'")
    print("\n📋 Next steps:")
    print("1. Copy 'MAGI_Windows_Installer' folder to Windows PC")
    print("2. Choose installation method")
    print("3. Access MAGI at http://localhost:8080")
    print("\n✨ Ready for deployment!")

if __name__ == "__main__":
    main()
