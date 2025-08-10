#!/usr/bin/env python3
"""
🧙‍♂️ MAGI Universal Installer - Works on Linux, Windows, and macOS
One installer to rule them all!
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def print_banner():
    print("""
🧙‍♂️ ═══════════════════════════════════════════════════════════════
    MAGI Universal Installer - Cross-Platform Setup
    
    Automatically detects your OS and installs MAGI accordingly
    Linux | Windows | macOS - All supported!
═══════════════════════════════════════════════════════════════
""")

def detect_system():
    """Detect the operating system"""
    system = platform.system().lower()
    print(f"🖥️  Detected OS: {platform.system()} ({platform.architecture()[0]})")
    print(f"🐍 Python: {platform.python_version()}")
    return system

def check_prerequisites():
    """Check if Python and required tools are available"""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 6):
        print(f"❌ Python {major}.{minor} detected. Python 3.6+ required.")
        return False
    
    print(f"✅ Python {major}.{minor} - Compatible")
    return True

def get_node_choice():
    """Get user's node choice"""
    nodes = {
        "1": "GASPAR",
        "2": "MELCHIOR", 
        "3": "BALTASAR"
    }
    
    print("\n🎯 Choose your MAGI node:")
    print("   1. GASPAR  - Multimedia & Entertainment Node")
    print("   2. MELCHIOR - Backup & Storage Node")
    print("   3. BALTASAR - Home Automation Node")
    
    while True:
        choice = input("\nEnter choice (1-3): ").strip()
        if choice in nodes:
            return nodes[choice]
        print("❌ Invalid choice. Please enter 1, 2, or 3.")

def install_linux(node_name):
    """Install MAGI on Linux"""
    print("🐧 Installing for Linux...")
    
    # Check if systemd is available
    has_systemd = shutil.which('systemctl') is not None
    
    if has_systemd:
        print("✅ systemd detected - Installing as user service")
        
        # Run the user service installer
        if os.path.exists('./install-user-service.sh'):
            subprocess.run(['bash', './install-user-service.sh'], 
                         input=f"{node_name}\n", text=True)
        else:
            print("❌ install-user-service.sh not found")
            install_fallback(node_name)
    else:
        print("⚠️  systemd not available - Installing basic setup")
        install_fallback(node_name)

def install_windows(node_name):
    """Install MAGI on Windows"""
    print("🪟 Installing for Windows...")
    
    # Check if PowerShell is available
    has_powershell = shutil.which('powershell') is not None
    
    if has_powershell and os.path.exists('./Install-MAGI.ps1'):
        print("✅ PowerShell detected - Running modern installer")
        subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', 
                       '-File', './Install-MAGI.ps1', '-NodeName', node_name])
    elif os.path.exists('./install-windows-simple.bat'):
        print("✅ Running simple batch installer")
        # We need to create a response file for the batch script
        choice_map = {"GASPAR": "1", "MELCHIOR": "2", "BALTASAR": "3"}
        choice = choice_map.get(node_name, "1")
        
        subprocess.run(['cmd', '/c', 'install-windows-simple.bat'], 
                      input=f"{choice}\n", text=True)
    else:
        print("❌ Windows installers not found")
        install_fallback(node_name)

def install_macos(node_name):
    """Install MAGI on macOS"""
    print("🍎 Installing for macOS...")
    
    # Check if launchctl is available
    has_launchctl = shutil.which('launchctl') is not None
    
    if has_launchctl:
        print("✅ launchctl detected - Installing as user service")
        install_macos_service(node_name)
    else:
        print("⚠️  launchctl not available - Installing basic setup")
        install_fallback(node_name)

def install_macos_service(node_name):
    """Install MAGI as macOS launchd service"""
    home_dir = Path.home()
    launch_agents_dir = home_dir / "Library" / "LaunchAgents"
    launch_agents_dir.mkdir(exist_ok=True)
    
    current_dir = Path.cwd()
    service_name = f"com.magi.{node_name.lower()}"
    
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{service_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{current_dir}/magi-node-v2.py</string>
        <string>{node_name}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{current_dir}</string>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{home_dir}/Library/Logs/magi-{node_name.lower()}.log</string>
    <key>StandardErrorPath</key>
    <string>{home_dir}/Library/Logs/magi-{node_name.lower()}-error.log</string>
</dict>
</plist>"""
    
    plist_file = launch_agents_dir / f"{service_name}.plist"
    plist_file.write_text(plist_content)
    
    # Load the service
    subprocess.run(['launchctl', 'load', str(plist_file)])
    
    print(f"✅ macOS service installed: {service_name}")
    print(f"📝 Service file: {plist_file}")
    print(f"📋 Control commands:")
    print(f"   Start:  launchctl start {service_name}")
    print(f"   Stop:   launchctl stop {service_name}")
    print(f"   Unload: launchctl unload {plist_file}")

def install_fallback(node_name):
    """Fallback installation for any system"""
    print("🔧 Installing basic MAGI setup...")
    
    # Create a simple launcher script
    current_dir = Path.cwd()
    
    if platform.system().lower() == 'windows':
        launcher_file = current_dir / f"start-magi-{node_name.lower()}.bat"
        launcher_content = f"""@echo off
title 🧙‍♂️ MAGI {node_name}
cd /d "{current_dir}"
python magi-node-v2.py {node_name}
pause
"""
    else:
        launcher_file = current_dir / f"start-magi-{node_name.lower()}.sh"
        launcher_content = f"""#!/bin/bash
echo "🧙‍♂️ Starting MAGI {node_name}..."
cd "{current_dir}"
python3 magi-node-v2.py {node_name}
"""
    
    launcher_file.write_text(launcher_content)
    
    if not platform.system().lower() == 'windows':
        os.chmod(launcher_file, 0o755)
    
    print(f"✅ Launcher created: {launcher_file}")
    print(f"🚀 To start MAGI: {launcher_file}")
    print(f"🌐 Dashboard: http://localhost:8081")

def create_desktop_shortcut(node_name):
    """Create desktop shortcut (cross-platform)"""
    try:
        if platform.system().lower() == 'windows':
            desktop = Path.home() / "Desktop"
            shortcut_file = desktop / f"MAGI {node_name}.url"
            shortcut_content = """[InternetShortcut]
URL=http://localhost:8081
IconFile=shell32.dll
IconIndex=13
"""
            shortcut_file.write_text(shortcut_content)
            print(f"✅ Desktop shortcut created: {shortcut_file}")
        
        elif platform.system().lower() == 'darwin':  # macOS
            desktop = Path.home() / "Desktop"
            shortcut_file = desktop / f"MAGI {node_name}.url"
            shortcut_content = f"""[InternetShortcut]
URL=http://localhost:8081
"""
            shortcut_file.write_text(shortcut_content)
            print(f"✅ Desktop shortcut created: {shortcut_file}")
        
        else:  # Linux
            desktop = Path.home() / "Desktop"
            if not desktop.exists():
                desktop = Path.home() / ".local" / "share" / "applications"
                desktop.mkdir(parents=True, exist_ok=True)
            
            shortcut_file = desktop / f"magi-{node_name.lower()}.desktop"
            current_dir = Path.cwd()
            icon_path = current_dir / "magi-icon.svg"
            
            shortcut_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=🧙‍♂️ MAGI {node_name}
Comment=MAGI Distributed Monitoring - {node_name} Node
Exec=xdg-open http://localhost:8081
Icon={icon_path if icon_path.exists() else 'applications-system'}
Terminal=false
Categories=System;Monitor;Network;
"""
            shortcut_file.write_text(shortcut_content)
            os.chmod(shortcut_file, 0o755)
            print(f"✅ Desktop shortcut created: {shortcut_file}")
    
    except Exception as e:
        print(f"⚠️  Could not create desktop shortcut: {e}")

def test_magi_installation():
    """Test if MAGI can be imported and run"""
    print("
🧪 Testing MAGI installation...")
    
    try:
        # Check if magi-node-v2.py exists
        if not os.path.exists('magi-node-v2.py'):
            print("❌ magi-node-v2.py not found in current directory")
            return False
        
        # Test Python syntax
        result = subprocess.run([sys.executable, '-m', 'py_compile', 'magi-node-v2.py'], 
                              capture_output=True, text=True)

def main():
    """Main installation function"""
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please install Python 3.6+ and try again.")
        return False
    
    # Check if magi-node.py exists
    if not os.path.exists('magi-node.py'):
        print("❌ magi-node.py not found in current directory")
        print("Please run this installer from the MAGI directory")
        return False
    
    # Test installation
    if not test_installation():
        print("❌ MAGI installation test failed")
        return False
    
    # Get node choice
    node_name = get_node_choice()
    
    # Detect system and install accordingly
    system = detect_system()
    
    print(f"\n🚀 Installing MAGI {node_name} for {platform.system()}...")
    
    if system == 'linux':
        install_linux(node_name)
    elif system == 'windows':
        install_windows(node_name)
    elif system == 'darwin':
        install_macos(node_name)
    else:
        print(f"⚠️  Unknown system: {system}. Using fallback installation.")
        install_fallback(node_name)
    
    # Create desktop shortcut
    create_desktop_shortcut(node_name)
    
    # Final instructions
    print(f"""
🎉 MAGI {node_name} Installation Complete!
═══════════════════════════════════════════════════════════════

🚀 MAGI is now installed and ready to run
🌐 Dashboard URL: http://localhost:8081
📁 Installation directory: {Path.cwd()}

🔧 Next steps:
   1. Start MAGI using the created launcher
   2. Open the dashboard in your browser
   3. Install on other nodes in your network
   
🧙‍♂️ The MAGI system awaits your command!
""")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation error: {e}")
        sys.exit(1)
