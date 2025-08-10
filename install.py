#!/usr/bin/env python3
"""
🧙‍♂️ MAGI Installation Script - Ultra-Simple Setup
One script to install them all. Zero dependencies. Maximum simplicity.
"""

import os
import sys
import platform
import subprocess
import shutil
import urllib.request

def print_banner():
    """Print MAGI installation banner"""
    print("""
🧙‍♂️ ═══════════════════════════════════════════════════════════════
    MAGI - Ultra-Simple Distributed Monitoring Installation
    
    The Three Wise Men of Home Lab Monitoring
    - GASPAR: Multimedia & Entertainment Node
    - MELCHIOR: Backup & Storage Node  
    - BALTASAR: Home Automation Node
═══════════════════════════════════════════════════════════════
""")

def check_python():
    """Check Python installation"""
    print("🐍 Checking Python installation...")
    
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 6):
        print(f"❌ Python {major}.{minor} detected. Python 3.6+ required.")
        print("Please install Python 3.6 or higher from https://python.org")
        return False
    
    print(f"✅ Python {major}.{minor} detected - Compatible!")
    return True

def get_system_info():
    """Get system information"""
    info = {
        "os": platform.system(),
        "architecture": platform.architecture()[0],
        "platform": platform.platform(),
        "python_version": platform.python_version()
    }
    
    print(f"🖥️  Operating System: {info['os']} ({info['architecture']})")
    print(f"🐍 Python Version: {info['python_version']}")
    return info

def create_service_script(node_name, install_dir):
    """Create system service script"""
    system = platform.system()
    
    if system == "Linux":
        create_systemd_service(node_name, install_dir)
    elif system == "Windows":
        create_windows_service(node_name, install_dir)
    elif system == "Darwin":  # macOS
        create_launchd_service(node_name, install_dir)

def create_systemd_service(node_name, install_dir):
    """Create systemd service for Linux"""
    service_content = f"""[Unit]
Description=MAGI {node_name} Monitoring Node
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'magi')}
WorkingDirectory={install_dir}
ExecStart=/usr/bin/python3 {install_dir}/magi-node.py {node_name}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    
    service_file = f"/tmp/magi-{node_name.lower()}.service"
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    print(f"📝 Created systemd service: {service_file}")
    print(f"   To install: sudo cp {service_file} /etc/systemd/system/")
    print(f"   To enable: sudo systemctl enable magi-{node_name.lower()}")
    print(f"   To start: sudo systemctl start magi-{node_name.lower()}")

def create_windows_service(node_name, install_dir):
    """Create Windows service batch file"""
    batch_content = f"""@echo off
title MAGI {node_name} Node
echo Starting MAGI {node_name} Node...
cd /d "{install_dir}"
python magi-node.py {node_name}
pause
"""
    
    batch_file = os.path.join(install_dir, f"start-magi-{node_name.lower()}.bat")
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    
    print(f"📝 Created Windows batch file: {batch_file}")
    print(f"   Double-click to start MAGI {node_name}")

def create_launchd_service(node_name, install_dir):
    """Create launchd service for macOS"""
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.magi.{node_name.lower()}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{install_dir}/magi-node.py</string>
        <string>{node_name}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{install_dir}</string>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
    
    plist_file = f"/tmp/com.magi.{node_name.lower()}.plist"
    with open(plist_file, 'w') as f:
        f.write(plist_content)
    
    print(f"📝 Created launchd plist: {plist_file}")
    print(f"   To install: cp {plist_file} ~/Library/LaunchAgents/")
    print(f"   To load: launchctl load ~/Library/LaunchAgents/com.magi.{node_name.lower()}.plist")

def setup_firewall_rules(port=8080):
    """Setup firewall rules for MAGI"""
    system = platform.system()
    
    print(f"🔥 Setting up firewall rules for port {port}...")
    
    if system == "Linux":
        print("   Linux firewall commands:")
        print(f"   sudo ufw allow {port}/tcp")
        print(f"   sudo iptables -A INPUT -p tcp --dport {port} -j ACCEPT")
    elif system == "Windows":
        print("   Windows firewall commands:")
        print(f"   netsh advfirewall firewall add rule name=\"MAGI\" dir=in action=allow protocol=TCP localport={port}")
    elif system == "Darwin":
        print("   macOS firewall: Allow through System Preferences > Security & Privacy")

def choose_node():
    """Interactive node selection"""
    nodes = {
        "1": ("GASPAR", "Multimedia & Entertainment Node"),
        "2": ("MELCHIOR", "Backup & Storage Node"),
        "3": ("BALTASAR", "Home Automation Node")
    }
    
    print("\n🎯 Choose your MAGI node:")
    for key, (name, description) in nodes.items():
        print(f"   {key}. {name} - {description}")
    
    while True:
        choice = input("\nEnter choice (1-3): ").strip()
        if choice in nodes:
            return nodes[choice][0]
        print("❌ Invalid choice. Please enter 1, 2, or 3.")

def get_network_config():
    """Get network configuration"""
    print("\n🌐 Network Configuration:")
    print("Current default IPs:")
    print("   GASPAR: 192.168.1.100:8080")
    print("   MELCHIOR: 192.168.1.101:8080")
    print("   BALTASAR: 192.168.1.102:8080")
    
    use_default = input("\nUse default network configuration? (y/n): ").lower()
    if use_default in ['y', 'yes', '']:
        return True
    
    print("ℹ️  You can manually edit magi-node.py after installation to customize IPs")
    return True

def install_magi():
    """Main installation function"""
    print_banner()
    
    # Check prerequisites
    if not check_python():
        return False
    
    system_info = get_system_info()
    
    # Get installation directory
    if platform.system() == "Windows":
        default_dir = "C:\\MAGI"
    else:
        default_dir = "/opt/magi"
    
    install_dir = input(f"\n📁 Installation directory [{default_dir}]: ").strip()
    if not install_dir:
        install_dir = default_dir
    
    # Create installation directory
    try:
        os.makedirs(install_dir, exist_ok=True)
        print(f"✅ Created installation directory: {install_dir}")
    except PermissionError:
        print(f"❌ Permission denied creating {install_dir}")
        print("Run as administrator/sudo or choose a different directory")
        return False
    
    # Choose node
    node_name = choose_node()
    
    # Network configuration
    get_network_config()
    
    # Copy magi-node.py to installation directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_file = os.path.join(current_dir, "magi-node.py")
    dest_file = os.path.join(install_dir, "magi-node.py")
    
    try:
        if os.path.exists(source_file):
            shutil.copy2(source_file, dest_file)
            print(f"✅ Copied magi-node.py to {dest_file}")
        else:
            print(f"❌ Source file magi-node.py not found in {current_dir}")
            return False
    except Exception as e:
        print(f"❌ Error copying file: {e}")
        return False
    
    # Make executable on Unix systems
    if platform.system() != "Windows":
        os.chmod(dest_file, 0o755)
    
    # Create service scripts
    create_service_script(node_name, install_dir)
    
    # Setup firewall
    setup_firewall_rules()
    
    # Final instructions
    print(f"""
🎉 MAGI {node_name} Installation Complete!
═══════════════════════════════════════════

📁 Installation Directory: {install_dir}
🚀 To start manually: python3 {dest_file} {node_name}
🌐 Web Interface: http://localhost:8080

📋 Next Steps:
1. Configure your network settings if needed
2. Set up firewall rules (see commands above)
3. Install service for auto-start (see commands above)
4. Repeat installation on other nodes

🧙‍♂️ The MAGI system awaits your command!
""")
    
    # Ask to start now
    start_now = input("Start MAGI node now? (y/n): ").lower()
    if start_now in ['y', 'yes']:
        print(f"\n🚀 Starting MAGI {node_name}...")
        try:
            subprocess.run([sys.executable, dest_file, node_name])
        except KeyboardInterrupt:
            print(f"\n🛑 MAGI {node_name} stopped")
    
    return True

def main():
    """Main function"""
    try:
        install_magi()
    except KeyboardInterrupt:
        print("\n🛑 Installation cancelled by user")
    except Exception as e:
        print(f"\n❌ Installation error: {e}")

if __name__ == "__main__":
    main()
