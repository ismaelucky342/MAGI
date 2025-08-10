#!/usr/bin/env python3
"""
MAGI Windows Python Installer
Pure Python installer that works on Windows without .bat dependencies
"""

import os
import sys
import shutil
import subprocess
import json
import socket
import urllib.request
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import threading
import tempfile
import winreg
from pathlib import Path

# Configuration
MAGI_VERSION = "2.0.0"
DEFAULT_INSTALL_DIR = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'MAGI')

class MAGIWindowsInstaller:
    def __init__(self):
        self.install_dir = DEFAULT_INSTALL_DIR
        self.create_shortcuts = True
        self.auto_start = True
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
    def check_python_installation(self):
        """Check if Python is properly installed"""
        try:
            version = sys.version_info
            if version.major == 3 and version.minor >= 8:
                return True, f"Python {version.major}.{version.minor}.{version.micro}"
            else:
                return False, f"Python {version.major}.{version.minor} (requires 3.8+)"
        except:
            return False, "Python not found"
    
    def check_pip_installation(self):
        """Check if pip is available"""
        try:
            subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                         capture_output=True, check=True)
            return True
        except:
            return False
    
    def install_dependencies(self, progress_callback=None):
        """Install required Python packages"""
        if progress_callback:
            progress_callback("Installing Python dependencies...", 30)
        
        try:
            # Install psutil
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'psutil'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Failed to install psutil: {result.stderr}")
            
            if progress_callback:
                progress_callback("Dependencies installed successfully", 40)
            return True
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error installing dependencies: {e}", 40)
            return False
    
    def create_install_directory(self, progress_callback=None):
        """Create installation directory"""
        if progress_callback:
            progress_callback("Creating installation directory...", 50)
        
        try:
            os.makedirs(self.install_dir, exist_ok=True)
            return True
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error creating directory: {e}", 50)
            return False
    
    def copy_files(self, progress_callback=None):
        """Copy MAGI files to installation directory"""
        if progress_callback:
            progress_callback("Copying MAGI files...", 60)
        
        files_to_copy = [
            'magi-node-v2.py',
            'power-save-mode.py'
        ]
        
        try:
            for file in files_to_copy:
                src = os.path.join(self.script_dir, file)
                dst = os.path.join(self.install_dir, file)
                
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                else:
                    print(f"Warning: {file} not found, skipping")
            
            # Copy images directory if it exists
            images_src = os.path.join(self.script_dir, 'images')
            images_dst = os.path.join(self.install_dir, 'images')
            
            if os.path.exists(images_src):
                if os.path.exists(images_dst):
                    shutil.rmtree(images_dst)
                shutil.copytree(images_src, images_dst)
            
            return True
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error copying files: {e}", 60)
            return False
    
    def create_launcher_script(self, progress_callback=None):
        """Create Python launcher script"""
        if progress_callback:
            progress_callback("Creating launcher script...", 70)
        
        launcher_content = '''#!/usr/bin/env python3
"""
MAGI Node Launcher for Windows
Auto-detects configuration and starts MAGI node
"""

import os
import sys
import socket
import json
import importlib.util
import tkinter as tk
from tkinter import messagebox
import threading
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

class MAGILauncherGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MAGI Node Launcher")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Variables
        self.node_name = tk.StringVar(value=detect_node_name())
        self.port = tk.StringVar(value=str(find_available_port()))
        self.ip = tk.StringVar(value=get_local_ip())
        
        self.create_gui()
        
    def create_gui(self):
        # Header
        header = tk.Label(self.root, text="🧙 MAGI Node Launcher", 
                         font=("Arial", 16, "bold"))
        header.pack(pady=20)
        
        # Configuration frame
        config_frame = tk.LabelFrame(self.root, text="Configuration", padx=10, pady=10)
        config_frame.pack(pady=10, padx=20, fill="x")
        
        # Node name
        tk.Label(config_frame, text="Node Name:").grid(row=0, column=0, sticky="w", pady=5)
        node_combo = ttk.Combobox(config_frame, textvariable=self.node_name, 
                                 values=["GASPAR", "MELCHIOR", "BALTASAR"])
        node_combo.grid(row=0, column=1, sticky="ew", pady=5, padx=(10,0))
        
        # Port
        tk.Label(config_frame, text="Port:").grid(row=1, column=0, sticky="w", pady=5)
        port_entry = tk.Entry(config_frame, textvariable=self.port)
        port_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(10,0))
        
        # IP
        tk.Label(config_frame, text="IP Address:").grid(row=2, column=0, sticky="w", pady=5)
        ip_entry = tk.Entry(config_frame, textvariable=self.ip)
        ip_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=(10,0))
        
        config_frame.columnconfigure(1, weight=1)
        
        # Status frame
        status_frame = tk.LabelFrame(self.root, text="Status", padx=10, pady=10)
        status_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.status_text = tk.Text(status_frame, height=8, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.start_btn = tk.Button(button_frame, text="Start MAGI Node", 
                                  command=self.start_magi, 
                                  bg="#4CAF50", fg="white", 
                                  font=("Arial", 12, "bold"),
                                  width=15)
        self.start_btn.pack(side="left", padx=10)
        
        self.stop_btn = tk.Button(button_frame, text="Stop", 
                                 command=self.stop_magi,
                                 bg="#f44336", fg="white",
                                 font=("Arial", 12, "bold"),
                                 width=10, state="disabled")
        self.stop_btn.pack(side="left", padx=10)
        
        exit_btn = tk.Button(button_frame, text="Exit", 
                            command=self.root.quit,
                            width=10)
        exit_btn.pack(side="left", padx=10)
        
        self.add_status("MAGI Node Launcher Ready")
        self.add_status(f"Auto-detected: {self.node_name.get()}")
        self.add_status(f"Local IP: {self.ip.get()}")
        self.add_status(f"Available Port: {self.port.get()}")
        
    def add_status(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\\n")
        self.status_text.see(tk.END)
        self.root.update()
        
    def start_magi(self):
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        def run_magi():
            try:
                self.add_status(f"Starting MAGI Node: {self.node_name.get()}")
                self.add_status(f"Port: {self.port.get()}")
                
                # Set environment variables
                os.environ['MAGI_NODE_NAME'] = self.node_name.get()
                os.environ['MAGI_PORT'] = self.port.get()
                os.environ['MAGI_IP'] = self.ip.get()
                
                # Import and run MAGI
                sys.argv = ['magi_launcher.py', self.node_name.get()]
                
                spec = importlib.util.spec_from_file_location("magi_node", "magi-node-v2.py")
                magi_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(magi_module)
                
            except Exception as e:
                self.add_status(f"Error: {e}")
                self.start_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                
        thread = threading.Thread(target=run_magi, daemon=True)
        thread.start()
        
    def stop_magi(self):
        self.add_status("Stopping MAGI Node...")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        # Note: In a real implementation, you'd need a way to gracefully stop the server
        
    def run(self):
        self.root.mainloop()

def main():
    # Check if GUI is available
    try:
        app = MAGILauncherGUI()
        app.run()
    except:
        # Fall back to console mode
        print("🧙 Starting MAGI Node (Console Mode)")
        print("=" * 50)
        
        node_name = detect_node_name()
        local_ip = get_local_ip()
        port = find_available_port()
        
        print(f"🏷️  Node Name: {node_name}")
        print(f"🌐 Local IP: {local_ip}")
        print(f"🔌 Port: {port}")
        print("=" * 50)
        
        try:
            os.environ['MAGI_NODE_NAME'] = node_name
            os.environ['MAGI_PORT'] = str(port)
            os.environ['MAGI_IP'] = local_ip
            
            sys.argv = ['magi_launcher.py', node_name]
            
            spec = importlib.util.spec_from_file_location("magi_node", "magi-node-v2.py")
            magi_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(magi_module)
            
        except KeyboardInterrupt:
            print("\\n🛑 MAGI Node stopped by user")
        except Exception as e:
            print(f"❌ Error starting MAGI: {e}")

if __name__ == "__main__":
    main()
'''
        
        launcher_path = os.path.join(self.install_dir, 'magi_launcher.py')
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        return True
    
    def create_shortcuts(self, progress_callback=None):
        """Create desktop and start menu shortcuts"""
        if not self.create_shortcuts:
            return True
        
        if progress_callback:
            progress_callback("Creating shortcuts...", 80)
        
        try:
            # Create Python shortcut script
            shortcut_script = f'''
import subprocess
import os
import sys

# Change to MAGI directory
os.chdir(r"{self.install_dir}")

# Run MAGI launcher
subprocess.run([sys.executable, "magi_launcher.py"])
'''
            
            shortcut_path = os.path.join(self.install_dir, 'run_magi.py')
            with open(shortcut_path, 'w') as f:
                f.write(shortcut_script)
            
            # Create batch file for easier launching
            batch_content = f'''@echo off
cd /d "{self.install_dir}"
python magi_launcher.py
pause
'''
            
            batch_path = os.path.join(self.install_dir, 'MAGI_Node.bat')
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            
            # Try to create desktop shortcut using PowerShell
            try:
                desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
                shortcut_target = batch_path
                shortcut_link = os.path.join(desktop, 'MAGI Node.lnk')
                
                powershell_cmd = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_link}")
$Shortcut.TargetPath = "{shortcut_target}"
$Shortcut.WorkingDirectory = "{self.install_dir}"
$Shortcut.Save()
'''
                
                subprocess.run(['powershell', '-Command', powershell_cmd], 
                             capture_output=True, check=True)
                
            except Exception as e:
                print(f"Could not create desktop shortcut: {e}")
            
            return True
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error creating shortcuts: {e}", 80)
            return False
    
    def create_uninstaller(self, progress_callback=None):
        """Create uninstaller script"""
        if progress_callback:
            progress_callback("Creating uninstaller...", 90)
        
        uninstaller_content = f'''#!/usr/bin/env python3
"""
MAGI Node Uninstaller
"""

import os
import shutil
import tkinter as tk
from tkinter import messagebox

def uninstall_magi():
    try:
        # Remove installation directory
        install_dir = r"{self.install_dir}"
        if os.path.exists(install_dir):
            shutil.rmtree(install_dir)
        
        # Remove desktop shortcut
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        shortcut = os.path.join(desktop, 'MAGI Node.lnk')
        if os.path.exists(shortcut):
            os.remove(shortcut)
        
        messagebox.showinfo("Uninstall Complete", "MAGI Node has been uninstalled successfully!")
        return True
    except Exception as e:
        messagebox.showerror("Uninstall Error", f"Error during uninstallation: {{e}}")
        return False

def main():
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    result = messagebox.askyesno("MAGI Node Uninstaller", 
                                "Are you sure you want to uninstall MAGI Node?")
    
    if result:
        success = uninstall_magi()
        if success:
            root.quit()
    else:
        messagebox.showinfo("Cancelled", "Uninstallation cancelled.")
    
    root.destroy()

if __name__ == "__main__":
    main()
'''
        
        uninstaller_path = os.path.join(self.install_dir, 'uninstall_magi.py')
        with open(uninstaller_path, 'w', encoding='utf-8') as f:
            f.write(uninstaller_content)
        
        return True
    
    def perform_installation(self, progress_callback=None):
        """Perform the complete installation"""
        steps = [
            (self.install_dependencies, "Installing dependencies..."),
            (self.create_install_directory, "Creating installation directory..."),
            (self.copy_files, "Copying files..."),
            (self.create_launcher_script, "Creating launcher..."),
            (self.create_shortcuts, "Creating shortcuts..."),
            (self.create_uninstaller, "Creating uninstaller...")
        ]
        
        for i, (step_func, step_desc) in enumerate(steps):
            if progress_callback:
                progress = int((i / len(steps)) * 100)
                progress_callback(step_desc, progress)
            
            success = step_func(progress_callback)
            if not success:
                return False
        
        if progress_callback:
            progress_callback("Installation complete!", 100)
        
        return True

class MAGIInstallerGUI:
    def __init__(self):
        self.installer = MAGIWindowsInstaller()
        self.root = tk.Tk()
        self.root.title("MAGI Node Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        self.create_gui()
        
    def create_gui(self):
        # Header
        header = tk.Label(self.root, text="🧙 MAGI Node Installer", 
                         font=("Arial", 20, "bold"))
        header.pack(pady=20)
        
        # Version info
        version_label = tk.Label(self.root, text=f"Version {MAGI_VERSION}", 
                                font=("Arial", 12))
        version_label.pack()
        
        # Description
        desc = tk.Label(self.root, 
                       text="MAGI Distributed System Monitoring\\n"
                            "This installer will set up MAGI Node on your Windows system.",
                       font=("Arial", 11), justify="center")
        desc.pack(pady=20)
        
        # System check frame
        check_frame = tk.LabelFrame(self.root, text="System Check", padx=10, pady=10)
        check_frame.pack(pady=10, padx=20, fill="x")
        
        # Python check
        python_ok, python_info = self.installer.check_python_installation()
        python_status = "✅" if python_ok else "❌"
        tk.Label(check_frame, text=f"{python_status} Python: {python_info}").pack(anchor="w")
        
        # Pip check
        pip_ok = self.installer.check_pip_installation()
        pip_status = "✅" if pip_ok else "❌"
        tk.Label(check_frame, text=f"{pip_status} pip: {'Available' if pip_ok else 'Not found'}").pack(anchor="w")
        
        # Installation directory frame
        dir_frame = tk.LabelFrame(self.root, text="Installation Directory", padx=10, pady=10)
        dir_frame.pack(pady=10, padx=20, fill="x")
        
        dir_entry_frame = tk.Frame(dir_frame)
        dir_entry_frame.pack(fill="x")
        
        self.dir_var = tk.StringVar(value=self.installer.install_dir)
        dir_entry = tk.Entry(dir_entry_frame, textvariable=self.dir_var, font=("Courier", 9))
        dir_entry.pack(side="left", fill="x", expand=True)
        
        browse_btn = tk.Button(dir_entry_frame, text="Browse...", 
                              command=self.browse_directory)
        browse_btn.pack(side="right", padx=(10, 0))
        
        # Options frame
        options_frame = tk.LabelFrame(self.root, text="Options", padx=10, pady=10)
        options_frame.pack(pady=10, padx=20, fill="x")
        
        self.shortcuts_var = tk.BooleanVar(value=True)
        shortcuts_check = tk.Checkbutton(options_frame, text="Create desktop shortcut",
                                        variable=self.shortcuts_var)
        shortcuts_check.pack(anchor="w")
        
        # Progress frame
        progress_frame = tk.LabelFrame(self.root, text="Installation Progress", padx=10, pady=10)
        progress_frame.pack(pady=10, padx=20, fill="x")
        
        self.progress = ttk.Progressbar(progress_frame, length=500, mode='determinate')
        self.progress.pack(pady=5)
        
        self.status_label = tk.Label(progress_frame, text="Ready to install", 
                                    font=("Arial", 9))
        self.status_label.pack()
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.install_btn = tk.Button(button_frame, text="Install MAGI Node", 
                                    command=self.start_installation,
                                    bg="#4CAF50", fg="white", 
                                    font=("Arial", 12, "bold"),
                                    width=15)
        
        # Only enable install if system checks pass
        if python_ok and pip_ok:
            self.install_btn.config(state="normal")
        else:
            self.install_btn.config(state="disabled")
            
        self.install_btn.pack(side="left", padx=10)
        
        exit_btn = tk.Button(button_frame, text="Exit", 
                            command=self.root.quit,
                            width=10)
        exit_btn.pack(side="left", padx=10)
        
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.dir_var.get())
        if directory:
            self.dir_var.set(directory)
            self.installer.install_dir = directory
    
    def update_progress(self, status, value):
        """Update progress bar and status"""
        self.progress['value'] = value
        self.status_label.config(text=status)
        self.root.update()
        
    def start_installation(self):
        """Start installation in separate thread"""
        self.install_btn.config(state="disabled")
        self.installer.install_dir = self.dir_var.get()
        self.installer.create_shortcuts = self.shortcuts_var.get()
        
        def install_thread():
            success = self.installer.perform_installation(self.update_progress)
            
            if success:
                messagebox.showinfo("Installation Complete", 
                                  f"MAGI Node has been installed successfully!\\n\\n"
                                  f"Installation directory: {self.installer.install_dir}\\n\\n"
                                  "You can start MAGI Node from:\\n"
                                  "- Desktop shortcut (if created)\\n"
                                  f"- {self.installer.install_dir}\\\\magi_launcher.py\\n"
                                  f"- {self.installer.install_dir}\\\\MAGI_Node.bat")
                
                # Ask if user wants to start MAGI now
                start_now = messagebox.askyesno("Start MAGI?", 
                                              "Would you like to start MAGI Node now?")
                if start_now:
                    try:
                        launcher_path = os.path.join(self.installer.install_dir, 'magi_launcher.py')
                        subprocess.Popen([sys.executable, launcher_path], 
                                       cwd=self.installer.install_dir)
                    except Exception as e:
                        messagebox.showerror("Launch Error", f"Could not start MAGI: {e}")
                
            else:
                messagebox.showerror("Installation Failed", 
                                   "Installation failed. Please check the error messages and try again.")
            
            self.install_btn.config(state="normal")
        
        thread = threading.Thread(target=install_thread, daemon=True)
        thread.start()
    
    def run(self):
        self.root.mainloop()

def main():
    """Main function"""
    print("MAGI Windows Python Installer v" + MAGI_VERSION)
    print("=" * 50)
    
    # Check if we're running in a GUI environment
    try:
        app = MAGIInstallerGUI()
        app.run()
    except Exception as e:
        print(f"GUI not available, falling back to console mode: {e}")
        
        # Console installation
        installer = MAGIWindowsInstaller()
        
        print("\\nSystem Check:")
        python_ok, python_info = installer.check_python_installation()
        print(f"Python: {python_info}")
        
        pip_ok = installer.check_pip_installation()
        print(f"pip: {'Available' if pip_ok else 'Not found'}")
        
        if not python_ok or not pip_ok:
            print("\\n❌ System requirements not met. Please install Python 3.8+ with pip.")
            input("Press Enter to exit...")
            return
        
        print(f"\\nInstalling MAGI to: {installer.install_dir}")
        
        def console_progress(status, value):
            print(f"[{value:3d}%] {status}")
        
        success = installer.perform_installation(console_progress)
        
        if success:
            print("\\n✅ Installation completed successfully!")
            print(f"\\nTo start MAGI Node:")
            print(f"1. Open Command Prompt")
            print(f"2. cd \"{installer.install_dir}\"")
            print(f"3. python magi_launcher.py")
        else:
            print("\\n❌ Installation failed.")
        
        input("\\nPress Enter to exit...")

if __name__ == "__main__":
    main()
