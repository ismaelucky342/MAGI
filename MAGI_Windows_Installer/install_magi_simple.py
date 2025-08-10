#!/usr/bin/env python3
"""
MAGI Windows Simple Installer
Simplified version with better error handling and window persistence
"""

import os
import sys
import shutil
import subprocess
import time

def pause():
    """Pause and wait for user input"""
    input("\nPresiona Enter para continuar...")

def pause_on_error(message):
    """Show error and pause"""
    print(f"\n❌ ERROR: {message}")
    pause()

def check_python():
    """Check Python version"""
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor} - Se requiere Python 3.8+")
            return False
    except:
        print("❌ Python no encontrado")
        return False

def check_pip():
    """Check if pip works"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ pip disponible")
            return True
        else:
            print(f"❌ pip error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ pip no funciona: {e}")
        return False

def install_dependencies():
    """Install required packages"""
    print("\n📦 Instalando dependencias...")
    try:
        # Install psutil
        print("   Instalando psutil...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'psutil'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ psutil instalado correctamente")
            return True
        else:
            print(f"❌ Error instalando psutil: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout instalando dependencias")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def copy_files():
    """Copy MAGI files"""
    print("\n📁 Copiando archivos MAGI...")
    
    # Installation directory
    install_dir = "C:\\MAGI"
    
    try:
        # Create directory
        print(f"   Creando directorio: {install_dir}")
        os.makedirs(install_dir, exist_ok=True)
        
        # Files to copy
        files = ['magi-node-v2.py', 'power-save-mode.py', 'magi_launcher.py']
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        for file in files:
            src = os.path.join(script_dir, file)
            dst = os.path.join(install_dir, file)
            
            if os.path.exists(src):
                print(f"   Copiando {file}...")
                shutil.copy2(src, dst)
            else:
                print(f"   ⚠️ {file} no encontrado, omitiendo...")
        
        # Copy images if exist
        images_src = os.path.join(script_dir, 'images')
        if os.path.exists(images_src):
            images_dst = os.path.join(install_dir, 'images')
            print("   Copiando imágenes...")
            if os.path.exists(images_dst):
                shutil.rmtree(images_dst)
            shutil.copytree(images_src, images_dst)
        
        print(f"✅ Archivos copiados a {install_dir}")
        return install_dir
        
    except Exception as e:
        print(f"❌ Error copiando archivos: {e}")
        return None

def create_launcher(install_dir):
    """Create simple launcher"""
    print("\n🚀 Creando launcher...")
    
    try:
        # Simple Python launcher
        launcher_content = f'''import os
import sys
import socket

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

def main():
    print("🧙 Iniciando MAGI Node...")
    
    # Change to MAGI directory  
    os.chdir(r"{install_dir}")
    
    # Auto-detect node name
    hostname = socket.gethostname().upper()
    if "GASPAR" in hostname:
        node_name = "GASPAR"
    elif "MELCHIOR" in hostname:
        node_name = "MELCHIOR"
    elif "BALTASAR" in hostname:
        node_name = "BALTASAR"
    else:
        node_name = "GASPAR"  # default
    
    port = find_port()
    
    print(f"Nodo: {{node_name}}")
    print(f"Puerto: {{port}}")
    print("Accede en: http://localhost:{{port}}")
    print("-" * 40)
    
    # Set arguments and run
    sys.argv = ["launcher", node_name]
    
    try:
        exec(open("magi-node-v2.py").read())
    except KeyboardInterrupt:
        print("\\n🛑 MAGI detenido")
    except Exception as e:
        print(f"❌ Error: {{e}}")
        input("\\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
'''
        
        launcher_path = os.path.join(install_dir, 'start_magi.py')
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        # Create batch file too
        batch_content = f'''@echo off
title MAGI Node
cd /d "{install_dir}"
python start_magi.py
pause
'''
        
        batch_path = os.path.join(install_dir, 'MAGI.bat')
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        print("✅ Launcher creado")
        return launcher_path, batch_path
        
    except Exception as e:
        print(f"❌ Error creando launcher: {e}")
        return None, None

def create_desktop_shortcut(batch_path):
    """Create desktop shortcut"""
    print("\n🖥️ Creando acceso directo...")
    
    try:
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        
        # Create simple shortcut using PowerShell
        shortcut_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{os.path.join(desktop, 'MAGI Node.lnk')}")
$Shortcut.TargetPath = "{batch_path}"
$Shortcut.Save()
'''
        
        result = subprocess.run(['powershell', '-Command', shortcut_script], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Acceso directo creado en el escritorio")
        else:
            print(f"⚠️ No se pudo crear acceso directo: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️ Error creando acceso directo: {e}")

def main():
    """Main installation function"""
    print("=" * 60)
    print("🧙 MAGI Windows - Instalador Simple v2.1")
    print("=" * 60)
    print("Este instalador configurará MAGI en tu sistema Windows\n")
    
    try:
        # Step 1: Check Python
        print("1️⃣ Verificando Python...")
        if not check_python():
            print("\n💡 Solución:")
            print("   1. Descarga Python desde: https://www.python.org/downloads/")
            print("   2. Durante la instalación, marca 'Add Python to PATH'")
            print("   3. Reinicia el ordenador")
            print("   4. Ejecuta este instalador de nuevo")
            pause_on_error("Python no válido")
            return
        
        # Step 2: Check pip
        print("\n2️⃣ Verificando pip...")
        if not check_pip():
            print("\n💡 Solución:")
            print("   1. Reinstala Python desde python.org")
            print("   2. Asegúrate de marcar 'Add Python to PATH'")
            pause_on_error("pip no funciona")
            return
        
        # Step 3: Install dependencies
        print("\n3️⃣ Instalando dependencias...")
        if not install_dependencies():
            print("\n💡 Solución:")
            print("   1. Verifica tu conexión a internet")
            print("   2. Ejecuta como Administrador")
            print("   3. Intenta: pip install psutil")
            pause_on_error("Error instalando dependencias")
            return
        
        # Step 4: Copy files
        print("\n4️⃣ Copiando archivos...")
        install_dir = copy_files()
        if not install_dir:
            pause_on_error("Error copiando archivos")
            return
        
        # Step 5: Create launcher
        print("\n5️⃣ Configurando launcher...")
        launcher_path, batch_path = create_launcher(install_dir)
        if not launcher_path:
            pause_on_error("Error creando launcher")
            return
        
        # Step 6: Create shortcut
        print("\n6️⃣ Creando accesos directos...")
        if batch_path:
            create_desktop_shortcut(batch_path)
        
        # Success!
        print("\n" + "=" * 60)
        print("🎉 ¡INSTALACIÓN COMPLETADA!")
        print("=" * 60)
        print(f"📁 MAGI instalado en: {install_dir}")
        print(f"🚀 Para ejecutar MAGI:")
        print(f"   - Doble-click en 'MAGI Node' (escritorio)")
        print(f"   - O ejecuta: {batch_path}")
        print(f"🌐 Accede en: http://localhost:8080")
        print("=" * 60)
        
        # Ask if start now
        start_now = input("\n¿Quieres iniciar MAGI ahora? (s/N): ")
        if start_now.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            print("\n🚀 Iniciando MAGI...")
            try:
                os.chdir(install_dir)
                subprocess.run([sys.executable, 'start_magi.py'])
            except Exception as e:
                print(f"❌ Error iniciando MAGI: {e}")
                print(f"Puedes iniciarlo manualmente desde: {batch_path}")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Instalación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("\n🔧 Información para soporte:")
        print(f"   - Python: {sys.version}")
        print(f"   - SO: {os.name}")
        print(f"   - Directorio: {os.getcwd()}")
    
    finally:
        print("\n" + "=" * 60)
        pause()

if __name__ == "__main__":
    main()
