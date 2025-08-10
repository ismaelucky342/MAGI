#!/usr/bin/env python3
"""
🔥 MAGI Final Service Installer
Instala MAGI como servicio systemd con configuración automática
"""

import os
import sys
import platform
import subprocess
import shutil
import socket
from pathlib import Path

def print_banner():
    print("""
🔥 ═══════════════════════════════════════════════════════════════
    MAGI Service Installer - Production Ready
    
    Instalación completa como servicio del sistema
    Configuración automática de puerto e IP
═══════════════════════════════════════════════════════════════
""")

def get_local_ip():
    """Obtiene la IP local del sistema"""
    try:
        # Conectar a Google DNS para obtener la IP local
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "localhost"

def find_available_port():
    """Encuentra un puerto disponible evitando 8096 (Jellyfin)"""
    blocked_ports = [8096]  # Jellyfin
    
    for port in range(8080, 8090):
        if port in blocked_ports:
            continue
            
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    
    # Si no encuentra puerto, usar rango alto
    for port in range(9080, 9090):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    
    return 8080  # fallback

def get_node_choice():
    """Selección del nodo MAGI"""
    nodes = {
        "1": "GASPAR",
        "2": "MELCHIOR", 
        "3": "BALTASAR"
    }
    
    print("\n🎯 Selecciona tu nodo MAGI:")
    print("   1. GASPAR  - Multimedia & Entertainment")
    print("   2. MELCHIOR - Backup & Storage")
    print("   3. BALTASAR - Automation & Control")
    
    while True:
        choice = input("\nElige tu nodo (1-3): ").strip()
        if choice in nodes:
            return nodes[choice]
        print("❌ Opción inválida. Usa 1, 2 o 3.")

def install_dependencies():
    """Instala dependencias necesarias"""
    print("\n📦 Instalando dependencias...")
    
    # Verificar si psutil ya está instalado
    try:
        import psutil
        print("✅ psutil ya está instalado")
        return True
    except ImportError:
        pass
    
    # Intentar diferentes métodos de instalación
    install_methods = [
        # Método 1: pip del usuario
        [sys.executable, '-m', 'pip', 'install', '--user', 'psutil'],
        # Método 2: apt en Ubuntu/Debian
        ['apt', 'install', '-y', 'python3-psutil'],
        # Método 3: pip del sistema
        [sys.executable, '-m', 'pip', 'install', 'psutil'],
        # Método 4: pip3 directo
        ['pip3', 'install', 'psutil']
    ]
    
    for method in install_methods:
        try:
            print(f"   Intentando: {' '.join(method)}")
            result = subprocess.run(method, check=True, capture_output=True, text=True)
            
            # Verificar instalación
            try:
                import psutil
                print("✅ psutil instalado correctamente")
                return True
            except ImportError:
                continue
                
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"   ❌ Falló: {e}")
            continue
    
    print("❌ No se pudo instalar psutil automáticamente")
    print("💡 Instala manualmente: sudo apt install python3-psutil")
    return False

def update_magi_config(node_name, port):
    """Actualiza la configuración en magi-node-v2.py"""
    print(f"\n⚙️  Configurando MAGI para {node_name} en puerto {port}...")
    
    try:
        with open('magi-node-v2.py', 'r') as f:
            content = f.read()
        
        # Actualizar puerto
        content = content.replace('"port": 8080', f'"port": {port}')
        
        with open('magi-node-v2.py', 'w') as f:
            f.write(content)
        
        print("✅ Configuración actualizada")
        return True
    except Exception as e:
        print(f"❌ Error actualizando configuración: {e}")
        return False

def create_systemd_service(node_name, port, install_dir):
    """Crea el servicio systemd"""
    print(f"\n🔧 Creando servicio systemd...")
    
    # Verificar si el usuario magi existe
    user_exists = subprocess.run(['id', 'magi'], capture_output=True).returncode == 0
    user_line = "User=magi\nGroup=magi" if user_exists else "User=root"
    
    service_content = f"""[Unit]
Description=MAGI {node_name} Monitoring Node
After=network.target
Wants=network.target

[Service]
Type=simple
{user_line}
WorkingDirectory={install_dir}
ExecStart=/usr/bin/python3 {install_dir}/magi-node-v2.py {node_name}
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"""
    
    service_file = f"/etc/systemd/system/magi-{node_name.lower()}.service"
    
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        print(f"✅ Servicio creado: {service_file}")
        return service_file
    except PermissionError:
        print("❌ Necesitas permisos de administrador. Ejecuta con sudo.")
        return None
    except Exception as e:
        print(f"❌ Error creando servicio: {e}")
        return None

def setup_magi_user():
    """Crea usuario del sistema para MAGI"""
    print("\n👤 Configurando usuario del sistema...")
    
    try:
        # Verificar si el usuario ya existe
        result = subprocess.run(['id', 'magi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("ℹ️  Usuario 'magi' ya existe")
            return True
        
        # Crear usuario magi si no existe
        result = subprocess.run(['useradd', '-r', '-s', '/bin/false', '-d', '/opt/magi', 'magi'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Usuario 'magi' creado")
            return True
        else:
            print(f"⚠️  Error creando usuario: {result.stderr}")
            # Intentar continuar sin usuario dedicado
            print("ℹ️  Continuando con usuario root...")
            return True
            
    except Exception as e:
        print(f"⚠️  Error configurando usuario: {e}")
        print("ℹ️  Continuando con usuario root...")
        return True

def install_magi_files(node_name, install_dir):
    """Instala archivos MAGI en el directorio del sistema"""
    print(f"\n📁 Instalando archivos en {install_dir}...")
    
    try:
        # Crear directorio de instalación
        os.makedirs(install_dir, exist_ok=True)
        
        # Copiar archivos necesarios
        shutil.copy2('magi-node-v2.py', install_dir)
        shutil.copy2('power-save-mode.py', install_dir)
        shutil.copytree('images', f'{install_dir}/images', dirs_exist_ok=True)
        
        # Establecer permisos - verificar si usuario magi existe
        user_exists = subprocess.run(['id', 'magi'], capture_output=True).returncode == 0
        
        if user_exists:
            subprocess.run(['chown', '-R', 'magi:magi', install_dir], capture_output=True)
        else:
            print("ℹ️  Usando permisos de root (usuario magi no disponible)")
        
        subprocess.run(['chmod', '+x', f'{install_dir}/magi-node-v2.py'])
        
        print("✅ Archivos instalados correctamente")
        return True
    except Exception as e:
        print(f"❌ Error instalando archivos: {e}")
        return False

def enable_and_start_service(service_name):
    """Habilita e inicia el servicio"""
    print(f"\n🚀 Habilitando servicio {service_name}...")
    
    try:
        # Recargar systemd
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
        print("✅ Systemd recargado")
        
        # Habilitar servicio
        subprocess.run(['systemctl', 'enable', service_name], check=True)
        print("✅ Servicio habilitado para autoarranque")
        
        # Iniciar servicio
        result = subprocess.run(['systemctl', 'start', service_name], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Servicio iniciado correctamente")
            
            # Verificar estado
            status = subprocess.run(['systemctl', 'is-active', service_name], 
                                  capture_output=True, text=True)
            if status.stdout.strip() == 'active':
                print("✅ Servicio está activo y corriendo")
            else:
                print("⚠️  Servicio habilitado pero no está activo")
            
            return True
        else:
            print(f"❌ Error iniciando servicio: {result.stderr}")
            print("💡 Puedes iniciarlo manualmente: sudo systemctl start " + service_name)
            return True  # Consideramos éxito parcial
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error con el servicio: {e}")
        return False

def create_desktop_launcher(node_name, ip, port):
    """Crea lanzador en el escritorio"""
    print("\n🖥️  Creando acceso directo...")
    
    desktop_file = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=MAGI {node_name}
Comment=Acceder a MAGI {node_name} Dashboard
Exec=xdg-open http://{ip}:{port}
Icon=applications-internet
Terminal=false
Categories=Network;
"""
    
    try:
        desktop_path = Path.home() / "Desktop" / f"MAGI-{node_name}.desktop"
        with open(desktop_path, 'w') as f:
            f.write(desktop_file)
        
        os.chmod(desktop_path, 0o755)
        print(f"✅ Acceso directo creado: {desktop_path}")
    except Exception as e:
        print(f"⚠️  No se pudo crear el acceso directo: {e}")

def main():
    """Función principal de instalación"""
    if os.geteuid() != 0:
        print("❌ Este instalador necesita permisos de administrador.")
        print("Ejecuta: sudo python3 install-magi-service.py")
        return False
    
    print_banner()
    
    # Verificar archivos necesarios
    if not os.path.exists('magi-node-v2.py'):
        print("❌ magi-node-v2.py no encontrado")
        print("💡 Ejecuta el instalador desde el directorio MAGI")
        return False
    
    # Verificar si ya hay una instancia corriendo
    try:
        result = subprocess.run(['pgrep', '-f', 'magi-node-v2.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("⚠️  Detectada instancia MAGI corriendo. Deteniendo...")
            subprocess.run(['pkill', '-f', 'magi-node-v2.py'], capture_output=True)
    except:
        pass
    
    # Obtener configuración
    local_ip = get_local_ip()
    port = find_available_port()
    node_name = get_node_choice()
    install_dir = f"/opt/magi-{node_name.lower()}"
    
    print(f"\n📋 Configuración:")
    print(f"   Nodo: {node_name}")
    print(f"   IP: {local_ip}")
    print(f"   Puerto: {port}")
    print(f"   Directorio: {install_dir}")
    
    # Verificar si el servicio ya existe
    service_name = f"magi-{node_name.lower()}"
    service_exists = os.path.exists(f"/etc/systemd/system/{service_name}.service")
    if service_exists:
        print(f"\n⚠️  El servicio {service_name} ya existe.")
        choice = input("¿Desinstalar y reinstalar? (y/N): ").strip().lower()
        if choice == 'y':
            subprocess.run(['systemctl', 'stop', service_name], capture_output=True)
            subprocess.run(['systemctl', 'disable', service_name], capture_output=True)
            os.remove(f"/etc/systemd/system/{service_name}.service")
        else:
            print("❌ Instalación cancelada")
            return False
    
    input("\nPresiona Enter para continuar...")
    
    # Proceso de instalación
    steps = [
        ("Instalar dependencias", lambda: install_dependencies()),
        ("Configurar MAGI", lambda: update_magi_config(node_name, port)),
        ("Configurar usuario", lambda: setup_magi_user()),
        ("Instalar archivos", lambda: install_magi_files(node_name, install_dir)),
        ("Crear servicio", lambda: create_systemd_service(node_name, port, install_dir)),
        ("Iniciar servicio", lambda: enable_and_start_service(f"magi-{node_name.lower()}")),
    ]
    
    for step_name, step_func in steps:
        print(f"\n⚡ {step_name}...")
        if not step_func():
            print(f"❌ Falló: {step_name}")
            return False
    
    # Crear acceso directo
    create_desktop_launcher(node_name, local_ip, port)
    
    print(f"""
🎉 ═══════════════════════════════════════════════════════════════
    MAGI {node_name} INSTALADO CORRECTAMENTE
═══════════════════════════════════════════════════════════════

🌐 Accede a tu dashboard:
   http://{local_ip}:{port}

🔧 Gestión del servicio:
   sudo systemctl status magi-{node_name.lower()}
   sudo systemctl stop magi-{node_name.lower()}
   sudo systemctl start magi-{node_name.lower()}

📊 El servicio se iniciará automáticamente al arrancar el sistema.
""")
    
    return True

if __name__ == "__main__":
    main()
