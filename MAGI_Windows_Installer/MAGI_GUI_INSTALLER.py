#!/usr/bin/env python3
"""
🧙 MAGI WINDOWS INSTALLER CON GUI 
================================
ESTE ES EL INSTALADOR CON BOTONES Y VENTANAS
Doble-click para instalar MAGI con interfaz gráfica
"""

import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import threading
import time

# Configuration
MAGI_VERSION = "2.0.0"
DEFAULT_INSTALL_DIR = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'MAGI')

class MAGIInstaller:
    def __init__(self):
        self.install_dir = DEFAULT_INSTALL_DIR
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
    def check_python(self):
        """Check Python version"""
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                return True, f"Python {version.major}.{version.minor}.{version.micro}"
            else:
                return False, f"Python {version.major}.{version.minor} (se requiere 3.8+)"
        except:
            return False, "Python no encontrado"
    
    def check_pip(self):
        """Check if pip works"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def install_dependencies(self, progress_callback=None):
        """Install required packages"""
        if progress_callback:
            progress_callback("Instalando dependencias Python...", 20)
        
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'psutil'], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                if progress_callback:
                    progress_callback("Dependencias instaladas correctamente", 30)
                return True
            else:
                if progress_callback:
                    progress_callback(f"Error instalando dependencias: {result.stderr[:100]}", 30)
                return False
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error: {str(e)[:100]}", 30)
            return False
    
    def create_install_directory(self, progress_callback=None):
        """Create installation directory"""
        if progress_callback:
            progress_callback("Creando directorio de instalación...", 40)
        
        try:
            os.makedirs(self.install_dir, exist_ok=True)
            return True
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error creando directorio: {e}", 40)
            return False
    
    def copy_files(self, progress_callback=None):
        """Copy MAGI files"""
        if progress_callback:
            progress_callback("Copiando archivos MAGI...", 60)
        
        files_to_copy = ['magi-node-v2.py', 'power-save-mode.py']
        
        try:
            for file in files_to_copy:
                src = os.path.join(self.script_dir, file)
                dst = os.path.join(self.install_dir, file)
                
                if os.path.exists(src):
                    shutil.copy2(src, dst)
            
            # Copy images if exist
            images_src = os.path.join(self.script_dir, 'images')
            if os.path.exists(images_src):
                images_dst = os.path.join(self.install_dir, 'images')
                if os.path.exists(images_dst):
                    shutil.rmtree(images_dst)
                shutil.copytree(images_src, images_dst)
            
            return True
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error copiando archivos: {e}", 60)
            return False
    
    def create_launcher(self, progress_callback=None):
        """Create launcher"""
        if progress_callback:
            progress_callback("Creando launcher...", 80)
        
        launcher_content = f'''import os
import sys
import socket
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading

def find_port():
    for port in range(8080, 8100):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', port))
            s.close()
            return port
        except:
            continue
    return 8080

def detect_node_name():
    hostname = socket.gethostname().upper()
    if "GASPAR" in hostname:
        return "GASPAR"
    elif "MELCHIOR" in hostname:
        return "MELCHIOR"
    elif "BALTASAR" in hostname:
        return "BALTASAR"
    else:
        return "GASPAR"

class MAGILauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧙 MAGI Node Launcher")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Variables
        self.node_name = tk.StringVar(value=detect_node_name())
        self.port = tk.StringVar(value=str(find_port()))
        self.running = False
        
        self.create_gui()
        
    def create_gui(self):
        # Header
        header = tk.Label(self.root, text="🧙 MAGI Node Launcher", 
                         font=("Arial", 18, "bold"), fg="darkblue")
        header.pack(pady=20)
        
        # Config frame
        config_frame = tk.LabelFrame(self.root, text="Configuración", padx=15, pady=15)
        config_frame.pack(pady=20, padx=20, fill="x")
        
        tk.Label(config_frame, text="Nodo MAGI:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        node_combo = ttk.Combobox(config_frame, textvariable=self.node_name, 
                                 values=["GASPAR", "MELCHIOR", "BALTASAR"], width=15)
        node_combo.grid(row=0, column=1, sticky="w", pady=5, padx=(10,0))
        
        tk.Label(config_frame, text="Puerto:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        port_entry = tk.Entry(config_frame, textvariable=self.port, width=18)
        port_entry.grid(row=1, column=1, sticky="w", pady=5, padx=(10,0))
        
        # Status
        self.status_label = tk.Label(self.root, text="✅ Listo para iniciar MAGI", 
                                    font=("Arial", 12), fg="green")
        self.status_label.pack(pady=20)
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.start_btn = tk.Button(button_frame, text="🚀 INICIAR MAGI", 
                                  command=self.start_magi,
                                  bg="#4CAF50", fg="white", 
                                  font=("Arial", 14, "bold"),
                                  width=15, height=2)
        self.start_btn.pack(side="left", padx=10)
        
        self.stop_btn = tk.Button(button_frame, text="🛑 DETENER", 
                                 command=self.stop_magi,
                                 bg="#f44336", fg="white",
                                 font=("Arial", 14, "bold"),
                                 width=12, height=2, state="disabled")
        self.stop_btn.pack(side="left", padx=10)
        
        # Access info
        info_label = tk.Label(self.root, text="Una vez iniciado, accede en:", 
                             font=("Arial", 10))
        info_label.pack(pady=(20,5))
        
        self.url_label = tk.Label(self.root, text=f"http://localhost:{{self.port.get()}}", 
                                 font=("Arial", 12, "bold"), fg="blue")
        self.url_label.pack()
        
    def start_magi(self):
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.running = True
        
        def run():
            try:
                os.chdir(r"{self.install_dir}")
                
                self.status_label.config(text=f"🚀 Iniciando {{self.node_name.get()}} en puerto {{self.port.get()}}...", fg="orange")
                self.root.update()
                
                # Update URL
                self.url_label.config(text=f"http://localhost:{{self.port.get()}}")
                
                # Start MAGI
                sys.argv = ["launcher", self.node_name.get()]
                
                # Set environment
                os.environ['MAGI_NODE_NAME'] = self.node_name.get()
                os.environ['MAGI_PORT'] = self.port.get()
                
                exec(open("magi-node-v2.py").read())
                
            except KeyboardInterrupt:
                self.status_label.config(text="🛑 MAGI detenido por el usuario", fg="red")
            except Exception as e:
                self.status_label.config(text=f"❌ Error: {{str(e)[:50]}}", fg="red")
                messagebox.showerror("Error", f"Error iniciando MAGI:\\n{{e}}")
            finally:
                self.start_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                self.running = False
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        
        # Update status after a moment
        self.root.after(2000, lambda: self.status_label.config(
            text=f"✅ MAGI {{self.node_name.get()}} ejecutándose en puerto {{self.port.get()}}", fg="green"
        ) if self.running else None)
    
    def stop_magi(self):
        self.running = False
        self.status_label.config(text="🛑 Deteniendo MAGI...", fg="orange")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        # Note: In a real implementation, you'd need to properly stop the server
    
    def run(self):
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{{width}}x{{height}}+{{x}}+{{y}}')
        
        self.root.mainloop()

if __name__ == "__main__":
    app = MAGILauncher()
    app.run()
'''
        
        try:
            launcher_path = os.path.join(self.install_dir, 'MAGI_Launcher.py')
            with open(launcher_path, 'w', encoding='utf-8') as f:
                f.write(launcher_content)
            
            # Create batch file for easy access
            batch_content = f'''@echo off
title MAGI Node Launcher
cd /d "{self.install_dir}"
python MAGI_Launcher.py
pause
'''
            
            batch_path = os.path.join(self.install_dir, 'MAGI_Launcher.bat')
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            
            return True, launcher_path, batch_path
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error creando launcher: {e}", 80)
            return False, None, None
    
    def create_shortcuts(self, batch_path, progress_callback=None):
        """Create desktop shortcut"""
        if progress_callback:
            progress_callback("Creando accesos directos...", 90)
        
        try:
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            
            shortcut_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{os.path.join(desktop, 'MAGI Node.lnk')}")
$Shortcut.TargetPath = "{batch_path}"
$Shortcut.Save()
'''
            
            subprocess.run(['powershell', '-Command', shortcut_script], 
                          capture_output=True, timeout=10)
            return True
        except:
            return False
    
    def install(self, progress_callback=None):
        """Perform installation"""
        steps = [
            (self.install_dependencies, 20),
            (self.create_install_directory, 40),
            (self.copy_files, 60),
            (self.create_launcher, 80),
        ]
        
        for step_func, progress in steps:
            success = step_func(progress_callback)
            if not success:
                return False
        
        # Create launcher and get paths
        success, launcher_path, batch_path = self.create_launcher(progress_callback)
        if not success:
            return False
        
        # Create shortcuts
        if batch_path:
            self.create_shortcuts(batch_path, progress_callback)
        
        if progress_callback:
            progress_callback("¡Instalación completada!", 100)
        
        return True

class MAGIInstallerGUI:
    def __init__(self):
        self.installer = MAGIInstaller()
        self.root = tk.Tk()
        self.root.title("🧙 MAGI Node - Instalador con GUI")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Make window stay visible
        self.root.attributes('-topmost', True)
        self.root.after(2000, lambda: self.root.attributes('-topmost', False))
        
        # Prevent accidental closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_gui()
        
    def create_gui(self):
        # Large header
        header = tk.Label(self.root, text="🧙 MAGI NODE", 
                         font=("Arial", 24, "bold"), fg="darkblue")
        header.pack(pady=20)
        
        subtitle = tk.Label(self.root, text="Instalador con Interfaz Gráfica", 
                           font=("Arial", 14), fg="gray")
        subtitle.pack()
        
        version_label = tk.Label(self.root, text=f"Versión {MAGI_VERSION}", 
                                font=("Arial", 12, "bold"))
        version_label.pack(pady=10)
        
        # Description
        desc = tk.Label(self.root, 
                       text="Sistema de Monitorización Distribuida MAGI\\n"
                            "Este instalador configurará MAGI en tu sistema Windows",
                       font=("Arial", 11), justify="center")
        desc.pack(pady=20)
        
        # System check
        check_frame = tk.LabelFrame(self.root, text="🔍 Verificación del Sistema", 
                                   padx=15, pady=15, font=("Arial", 10, "bold"))
        check_frame.pack(pady=20, padx=30, fill="x")
        
        python_ok, python_info = self.installer.check_python()
        python_status = "✅" if python_ok else "❌"
        tk.Label(check_frame, text=f"{python_status} Python: {python_info}", 
                font=("Arial", 10)).pack(anchor="w", pady=2)
        
        pip_ok = self.installer.check_pip()
        pip_status = "✅" if pip_ok else "❌"
        tk.Label(check_frame, text=f"{pip_status} pip: {'Disponible' if pip_ok else 'No encontrado'}", 
                font=("Arial", 10)).pack(anchor="w", pady=2)
        
        # Installation directory
        dir_frame = tk.LabelFrame(self.root, text="📁 Directorio de Instalación", 
                                 padx=15, pady=15, font=("Arial", 10, "bold"))
        dir_frame.pack(pady=20, padx=30, fill="x")
        
        dir_entry_frame = tk.Frame(dir_frame)
        dir_entry_frame.pack(fill="x")
        
        self.dir_var = tk.StringVar(value=self.installer.install_dir)
        dir_entry = tk.Entry(dir_entry_frame, textvariable=self.dir_var, 
                            font=("Arial", 9), width=50)
        dir_entry.pack(side="left", fill="x", expand=True)
        
        browse_btn = tk.Button(dir_entry_frame, text="📂 Examinar", 
                              command=self.browse_directory,
                              font=("Arial", 9))
        browse_btn.pack(side="right", padx=(10, 0))
        
        # Progress
        progress_frame = tk.LabelFrame(self.root, text="📊 Progreso de Instalación", 
                                      padx=15, pady=15, font=("Arial", 10, "bold"))
        progress_frame.pack(pady=20, padx=30, fill="x")
        
        self.progress = ttk.Progressbar(progress_frame, length=550, mode='determinate')
        self.progress.pack(pady=10)
        
        self.status_label = tk.Label(progress_frame, text="Listo para instalar MAGI", 
                                    font=("Arial", 10), fg="green")
        self.status_label.pack()
        
        # Big install button
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=30)
        
        self.install_btn = tk.Button(button_frame, text="🚀 INSTALAR MAGI NODE", 
                                    command=self.start_installation,
                                    bg="#4CAF50", fg="white", 
                                    font=("Arial", 16, "bold"),
                                    width=20, height=2)
        
        if python_ok and pip_ok:
            self.install_btn.config(state="normal")
        else:
            self.install_btn.config(state="disabled", bg="gray", 
                                   text="❌ REQUISITOS NO CUMPLIDOS")
            
        self.install_btn.pack(side="left", padx=10)
        
        exit_btn = tk.Button(button_frame, text="❌ Salir", 
                            command=self.on_closing,
                            font=("Arial", 12),
                            width=10, height=2)
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
        time.sleep(0.1)  # Small delay to see progress
        
    def start_installation(self):
        """Start installation"""
        self.install_btn.config(state="disabled", text="⏳ INSTALANDO...")
        self.installer.install_dir = self.dir_var.get()
        
        def install_thread():
            success = self.installer.install(self.update_progress)
            
            if success:
                self.status_label.config(text="✅ ¡INSTALACIÓN COMPLETADA!", fg="green")
                
                messagebox.showinfo("🎉 Instalación Exitosa", 
                                  f"¡MAGI Node se ha instalado correctamente!\\n\\n"
                                  f"📁 Ubicación: {self.installer.install_dir}\\n\\n"
                                  f"🚀 Para usar MAGI:\\n"
                                  f"• Busca 'MAGI Node' en el escritorio\\n"
                                  f"• O ejecuta: {self.installer.install_dir}\\\\MAGI_Launcher.bat\\n\\n"
                                  f"🌐 Acceso: http://localhost:8080")
                
                # Ask to start now
                start_now = messagebox.askyesno("🚀 Iniciar MAGI", 
                                              "¿Quieres iniciar MAGI Node ahora?")
                if start_now:
                    try:
                        launcher_path = os.path.join(self.installer.install_dir, 'MAGI_Launcher.py')
                        subprocess.Popen([sys.executable, launcher_path], 
                                       cwd=self.installer.install_dir)
                        messagebox.showinfo("✅ Iniciado", "MAGI Node se está iniciando...")
                    except Exception as e:
                        messagebox.showerror("❌ Error", f"No se pudo iniciar MAGI: {e}")
                
                self.root.quit()
                
            else:
                self.status_label.config(text="❌ Error en la instalación", fg="red")
                messagebox.showerror("❌ Error de Instalación", 
                                   "La instalación falló.\\n\\n"
                                   "Revisa los mensajes de error y prueba:\\n"
                                   "• Ejecutar como Administrador\\n"
                                   "• Verificar conexión a internet\\n"
                                   "• Reinstalar Python desde python.org")
                
                self.install_btn.config(state="normal", text="🔄 REINTENTAR INSTALACIÓN")
        
        thread = threading.Thread(target=install_thread, daemon=True)
        thread.start()
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askyesno("Salir", "¿Estás seguro de que quieres cerrar el instalador?"):
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.root.mainloop()

def main():
    """Main function with robust error handling"""
    try:
        print("🧙 Iniciando MAGI Installer GUI...")
        
        # Force GUI mode
        app = MAGIInstallerGUI()
        app.run()
        
    except ImportError as e:
        print(f"❌ Error importando tkinter: {e}")
        print("\\n💡 Solución:")
        print("1. Reinstala Python desde python.org")
        print("2. Durante la instalación, marca 'tcl/tk and IDLE'")
        print("3. O usa install_magi_simple.py (sin GUI)")
        input("\\nPresiona Enter para salir...")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        print("\\n🔧 Prueba:")
        print("1. Ejecutar como Administrador")
        print("2. Usar install_magi_simple.py")
        print("3. Verificar que Python está instalado correctamente")
        input("\\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
