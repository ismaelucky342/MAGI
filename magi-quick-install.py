#!/usr/bin/env python3
"""
🚀 MAGI Quick Install - Instalación rápida sin servicio
Para cuando el instalador completo falla
"""

import os
import sys
import subprocess
import socket

def get_local_ip():
    """Obtiene la IP local del sistema"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "localhost"

def find_available_port():
    """Encuentra un puerto disponible evitando 8096"""
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
    return 8080

def install_psutil():
    """Instala psutil de manera simple"""
    print("📦 Instalando psutil...")
    
    # Verificar si ya está instalado
    try:
        import psutil
        print("✅ psutil ya disponible")
        return True
    except ImportError:
        pass
    
    # Intentar instalación con apt
    try:
        subprocess.run(['apt', 'install', '-y', 'python3-psutil'], 
                      check=True, capture_output=True)
        print("✅ psutil instalado con apt")
        return True
    except:
        pass
    
    # Intentar con pip
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', 'psutil'], 
                      check=True, capture_output=True)
        print("✅ psutil instalado con pip")
        return True
    except:
        pass
    
    print("❌ No se pudo instalar psutil automáticamente")
    print("💡 Ejecuta manualmente: sudo apt install python3-psutil")
    return False

def main():
    print("""
🚀 ═══════════════════════════════════════════════════════════════
    MAGI Quick Install - Instalación Rápida
    
    Instala MAGI sin configurar como servicio
═══════════════════════════════════════════════════════════════
""")
    
    if not os.path.exists('magi-node-v2.py'):
        print("❌ magi-node-v2.py no encontrado")
        return False
    
    # Instalar dependencias
    if not install_psutil():
        print("❌ Instalación falló - dependencias no disponibles")
        return False
    
    # Obtener configuración
    local_ip = get_local_ip()
    port = find_available_port()
    
    print(f"\n📋 Configuración detectada:")
    print(f"   IP: {local_ip}")
    print(f"   Puerto: {port}")
    
    # Actualizar puerto en el archivo
    try:
        with open('magi-node-v2.py', 'r') as f:
            content = f.read()
        content = content.replace('"port": 8080', f'"port": {port}')
        with open('magi-node-v2.py', 'w') as f:
            f.write(content)
        print("✅ Configuración actualizada")
    except Exception as e:
        print(f"⚠️  No se pudo actualizar el puerto: {e}")
    
    print(f"""
🎉 ═══════════════════════════════════════════════════════════════
    MAGI LISTO PARA USAR
═══════════════════════════════════════════════════════════════

🚀 Para ejecutar MAGI:
   python3 magi-node-v2.py GASPAR

🌐 Accede desde:
   http://{local_ip}:{port}

💡 Para instalación completa como servicio:
   sudo python3 install-magi-service.py
""")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        # Ejecutar directamente MAGI
        os.system("python3 magi-node-v2.py GASPAR")
    else:
        main()
