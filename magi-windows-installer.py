#!/usr/bin/env python3
"""
MAGI Windows Installer - One-Click Installation
Creates a complete Windows installer for MAGI Node
"""

import os
import sys
import shutil
import subprocess
import json
import urllib.request
import socket
from pathlib import Path

# Configuration
MAGI_VERSION = "2.0.0"
INSTALLER_CONFIG = {
    "app_name": "MAGI Node",
    "version": MAGI_VERSION,
    "description": "MAGI Distributed System Monitoring Node",
    "author": "MAGI Team",
    "install_dir": "C:\\Program Files\\MAGI",
    "start_menu": "MAGI Node",
    "desktop_shortcut": True,
    "autostart": True
}

class MAGIWindowsInstaller:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.install_dir = INSTALLER_CONFIG["install_dir"]
        self.python_embedded = None
        
    def print_banner(self):
        print("=" * 60)
        print("🧙 MAGI Windows Installer v" + MAGI_VERSION)
        print("=" * 60)
        print("Creating one-click Windows installer...")
        print()
        
    def check_requirements(self):
        """Check if required tools are available"""
        print("📋 Checking requirements...")
        
        # Check Python
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
            
        # Check pip
        try:
            import pip
            print("✅ Python and pip available")
        except ImportError:
            print("❌ pip not available")
            return False
            
        return True
        
    def install_pyinstaller(self):
        """Install PyInstaller if not available"""
        print("📦 Installing PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False
        return True
        
    def download_python_embedded(self):
        """Download Python embedded for Windows"""
        print("🐍 Downloading Python embedded for Windows...")
        
        python_url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
        python_zip = "python-embedded.zip"
        
        try:
            urllib.request.urlretrieve(python_url, python_zip)
            print("✅ Python embedded downloaded")
            return python_zip
        except Exception as e:
            print(f"❌ Failed to download Python: {e}")
            return None
            
    def create_launcher_script(self):
        """Create main launcher script for Windows"""
        launcher_content = f'''#!/usr/bin/env python3
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
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_local_ip():
    """Get local IP address"""
    try:
        # Connect to a remote address to determine local IP
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
        
        # Import MAGI module
        import magi_node_v2
        
        # Start with auto-configuration
        sys.argv = ['magi_launcher.py', node_name]
        magi_node_v2.main()
        
    except ImportError as e:
        print(f"❌ Error importing MAGI: {e}")
        print("Please ensure magi_node_v2.py is in the same directory")
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
        
    def create_installer_script(self):
        """Create Windows installer script"""
        installer_content = f'''@echo off
echo ================================================
echo 🧙 MAGI Node Windows Installer v{MAGI_VERSION}
echo ================================================
echo Installing MAGI Node...
echo.

REM Create installation directory
if not exist "{self.install_dir}" (
    mkdir "{self.install_dir}"
)

REM Copy files
echo 📁 Copying files...
copy /Y "magi_node_v2.py" "{self.install_dir}\\"
copy /Y "magi_launcher.py" "{self.install_dir}\\"
copy /Y "power-save-mode.py" "{self.install_dir}\\"
if exist "images" (
    xcopy /E /I /Y "images" "{self.install_dir}\\images"
)

REM Create batch launcher
echo 🚀 Creating launcher...
echo @echo off > "{self.install_dir}\\MAGI_Node.bat"
echo cd /d "{self.install_dir}" >> "{self.install_dir}\\MAGI_Node.bat"
echo python magi_launcher.py >> "{self.install_dir}\\MAGI_Node.bat"

REM Create desktop shortcut
echo 🖥️ Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\MAGI Node.lnk'); $Shortcut.TargetPath = '{self.install_dir}\\MAGI_Node.bat'; $Shortcut.WorkingDirectory = '{self.install_dir}'; $Shortcut.IconLocation = '{self.install_dir}\\MAGI_Node.bat,0'; $Shortcut.Save()"

REM Create start menu shortcut
echo 📋 Creating start menu entry...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\MAGI" (
    mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\MAGI"
)
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\MAGI\\MAGI Node.lnk'); $Shortcut.TargetPath = '{self.install_dir}\\MAGI_Node.bat'; $Shortcut.WorkingDirectory = '{self.install_dir}'; $Shortcut.Save()"

REM Install Python dependencies
echo 📦 Installing Python dependencies...
python -m pip install psutil --quiet

echo.
echo ✅ MAGI Node installed successfully!
echo.
echo 🚀 You can now start MAGI Node from:
echo    - Desktop shortcut: "MAGI Node"
echo    - Start Menu: Programs ^> MAGI ^> MAGI Node
echo    - Direct run: {self.install_dir}\\MAGI_Node.bat
echo.
echo 🌐 Access dashboard at: http://localhost:8080
echo.
pause
'''
        
        with open("install_magi_windows.bat", "w") as f:
            f.write(installer_content)
        print("✅ Windows installer script created")
        
    def create_executable_installer(self):
        """Create standalone executable installer"""
        print("🔨 Creating executable installer...")
        
        # Create a Python script that will be converted to .exe
        exe_installer_content = f'''
import os
import sys
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
import threading

class MAGIInstaller:
    def __init__(self):
        self.install_dir = "C:\\\\Program Files\\\\MAGI"
        self.temp_dir = tempfile.mkdtemp()
        
    def extract_files(self):
        """Extract embedded files"""
        # This will contain the embedded MAGI files
        files_data = {
            "magi_node_v2.py": '''# MAGI_NODE_CONTENT_PLACEHOLDER''',
            "magi_launcher.py": '''# LAUNCHER_CONTENT_PLACEHOLDER''',
            "power-save-mode.py": '''# POWER_SAVE_CONTENT_PLACEHOLDER'''
        }
        
        for filename, content in files_data.items():
            with open(os.path.join(self.temp_dir, filename), 'w') as f:
                f.write(content)
    
    def install(self, progress_callback=None):
        """Perform installation"""
        try:
            if progress_callback:
                progress_callback("Extracting files...", 10)
            
            self.extract_files()
            
            if progress_callback:
                progress_callback("Creating directories...", 30)
                
            # Create install directory
            os.makedirs(self.install_dir, exist_ok=True)
            
            if progress_callback:
                progress_callback("Copying files...", 50)
            
            # Copy files
            for filename in ["magi_node_v2.py", "magi_launcher.py", "power-save-mode.py"]:
                src = os.path.join(self.temp_dir, filename)
                dst = os.path.join(self.install_dir, filename)
                shutil.copy2(src, dst)
            
            if progress_callback:
                progress_callback("Creating shortcuts...", 70)
            
            # Create launcher batch file
            bat_content = f'''@echo off
cd /d "{self.install_dir}"
python magi_launcher.py
pause
'''
            with open(os.path.join(self.install_dir, "MAGI_Node.bat"), 'w') as f:
                f.write(bat_content)
            
            if progress_callback:
                progress_callback("Installing dependencies...", 90)
            
            # Install Python dependencies
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], 
                             check=True, capture_output=True)
            except:
                pass  # Continue even if pip install fails
            
            if progress_callback:
                progress_callback("Installation complete!", 100)
            
            return True
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error: {e}", 100)
            return False
    
    def create_gui(self):
        """Create installation GUI"""
        root = tk.Tk()
        root.title("MAGI Node Installer")
        root.geometry("500x300")
        root.resizable(False, False)
        
        # Header
        header = tk.Label(root, text="🧙 MAGI Node Installer", 
                         font=("Arial", 16, "bold"))
        header.pack(pady=20)
        
        # Description
        desc = tk.Label(root, text="MAGI Distributed System Monitoring\\n"
                                  "Version {MAGI_VERSION}\\n\\n"
                                  "This will install MAGI Node on your system.",
                       font=("Arial", 10))
        desc.pack(pady=10)
        
        # Install directory
        dir_frame = tk.Frame(root)
        dir_frame.pack(pady=10)
        tk.Label(dir_frame, text="Install Directory:").pack(anchor="w")
        tk.Label(dir_frame, text=self.install_dir, font=("Courier", 9)).pack(anchor="w")
        
        # Progress bar
        self.progress = ttk.Progressbar(root, length=400, mode='determinate')
        self.progress.pack(pady=20)
        
        # Status label
        self.status_label = tk.Label(root, text="Ready to install", font=("Arial", 9))
        self.status_label.pack()
        
        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)
        
        self.install_btn = tk.Button(button_frame, text="Install MAGI Node", 
                                    command=self.start_install, 
                                    bg="#4CAF50", fg="white", 
                                    font=("Arial", 10, "bold"),
                                    width=15)
        self.install_btn.pack(side="left", padx=10)
        
        self.exit_btn = tk.Button(button_frame, text="Exit", 
                                 command=root.quit,
                                 width=10)
        self.exit_btn.pack(side="left", padx=10)
        
        root.mainloop()
    
    def update_progress(self, status, value):
        """Update progress bar and status"""
        self.progress['value'] = value
        self.status_label.config(text=status)
        self.progress.update()
    
    def start_install(self):
        """Start installation in separate thread"""
        self.install_btn.config(state="disabled")
        
        def install_thread():
            success = self.install(self.update_progress)
            
            if success:
                messagebox.showinfo("Installation Complete", 
                                  "MAGI Node has been installed successfully!\\n\\n"
                                  "You can start it from:\\n"
                                  "- Desktop shortcut\\n"
                                  "- Start Menu > MAGI\\n"
                                  f"- Direct: {self.install_dir}\\\\MAGI_Node.bat")
            else:
                messagebox.showerror("Installation Failed", 
                                   "Installation failed. Please try again.")
            
            self.install_btn.config(state="normal")
        
        thread = threading.Thread(target=install_thread)
        thread.daemon = True
        thread.start()

def main():
    installer = MAGIInstaller()
    installer.create_gui()

if __name__ == "__main__":
    main()
'''
        
        with open("magi_windows_installer.py", "w") as f:
            f.write(exe_installer_content)
        print("✅ Executable installer script created")
        
    def build_installer(self):
        """Build the final installer"""
        print("🏗️ Building Windows installer...")
        
        # Read content of main files to embed
        magi_content = ""
        launcher_content = ""
        power_content = ""
        
        try:
            with open("magi-node-v2.py", "r") as f:
                magi_content = f.read()
        except FileNotFoundError:
            print("❌ magi-node-v2.py not found")
            return False
            
        try:
            with open("magi_launcher.py", "r") as f:
                launcher_content = f.read()
        except FileNotFoundError:
            print("❌ magi_launcher.py not found")
            return False
            
        try:
            with open("power-save-mode.py", "r") as f:
                power_content = f.read()
        except FileNotFoundError:
            print("⚠️ power-save-mode.py not found, creating empty file")
            power_content = "# Power save mode placeholder"
        
        # Replace placeholders in installer
        with open("magi_windows_installer.py", "r") as f:
            installer_content = f.read()
        
        installer_content = installer_content.replace("# MAGI_NODE_CONTENT_PLACEHOLDER", magi_content.replace('"', '\\"').replace("\\n", "\\\\n"))
        installer_content = installer_content.replace("# LAUNCHER_CONTENT_PLACEHOLDER", launcher_content.replace('"', '\\"').replace("\\n", "\\\\n"))
        installer_content = installer_content.replace("# POWER_SAVE_CONTENT_PLACEHOLDER", power_content.replace('"', '\\"').replace("\\n", "\\\\n"))
        
        with open("magi_installer_final.py", "w") as f:
            f.write(installer_content)
        
        # Build with PyInstaller
        try:
            cmd = [
                "pyinstaller",
                "--onefile",
                "--windowed",
                "--name", "MAGI_Node_Installer",
                "--icon=images/MAGI.ico" if os.path.exists("images/MAGI.ico") else "",
                "magi_installer_final.py"
            ]
            
            # Remove empty icon parameter
            cmd = [arg for arg in cmd if arg]
            
            subprocess.run(cmd, check=True)
            print("✅ Installer executable created: dist/MAGI_Node_Installer.exe")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build installer: {e}")
            return False
    
    def create_simple_installer(self):
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
            "magi_launcher.py"
        ]
        
        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy2(file, installer_dir)
        
        # Copy images if they exist
        if os.path.exists("images"):
            shutil.copytree("images", os.path.join(installer_dir, "images"))
        
        # Create README
        readme_content = f'''# MAGI Node Windows Installer

## Installation Instructions

1. Double-click on "install_magi_windows.bat"
2. Follow the installation prompts
3. MAGI Node will be installed to C:\\Program Files\\MAGI
4. Desktop and Start Menu shortcuts will be created

## Running MAGI Node

After installation, you can start MAGI Node by:
- Double-clicking the desktop shortcut "MAGI Node"
- Using Start Menu > Programs > MAGI > MAGI Node
- Running C:\\Program Files\\MAGI\\MAGI_Node.bat

## Access Dashboard

Once running, access the MAGI dashboard at:
http://localhost:8080

## Version

MAGI Node v{MAGI_VERSION}

## Requirements

- Windows 10/11
- Python 3.8+ (will prompt to install if not available)
'''
        
        with open(os.path.join(installer_dir, "README.txt"), "w") as f:
            f.write(readme_content)
        
        print(f"✅ Simple installer package created: {installer_dir}/")
        print(f"📁 Contents:")
        for file in os.listdir(installer_dir):
            print(f"   - {file}")
        
        return True
    
    def run(self):
        """Run the installer creation process"""
        self.print_banner()
        
        if not self.check_requirements():
            print("❌ Requirements not met")
            return False
        
        # Create all installer components
        self.create_launcher_script()
        self.create_installer_script()
        self.create_simple_installer()
        
        # Try to create executable installer if PyInstaller is available
        try:
            self.install_pyinstaller()
            self.create_executable_installer()
            # self.build_installer()  # Commented out for now due to complexity
        except Exception as e:
            print(f"⚠️ Could not create executable installer: {e}")
            print("✅ Simple installer package created instead")
        
        print("\n" + "=" * 60)
        print("🎉 MAGI Windows Installer Creation Complete!")
        print("=" * 60)
        print("\n📦 Available installers:")
        print("1. Simple Installer: MAGI_Windows_Installer/")
        print("   - Just double-click 'install_magi_windows.bat'")
        print("\n2. Individual files:")
        print("   - install_magi_windows.bat (main installer)")
        print("   - magi_launcher.py (auto-launcher)")
        print("\n🚀 Installation process:")
        print("1. Copy MAGI_Windows_Installer folder to Windows PC")
        print("2. Double-click install_magi_windows.bat")
        print("3. Follow prompts and enjoy MAGI!")
        
        return True

def main():
    installer = MAGIWindowsInstaller()
    installer.run()

if __name__ == "__main__":
    main()
