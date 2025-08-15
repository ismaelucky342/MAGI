# 🔥 MAGI - Guía de Instalación Consolidada

## 📋 Instaladores Disponibles

### 1. 🚀 **magi-installer.py** (RECOMENDADO)
**Instalador unificado con seguridad integrada**

#### Características:
- ✅ **Dos modos de instalación**: Simple y Servicio
- ✅ **Seguridad integrada**: Autenticación web + API keys
- ✅ **Configuración unificada**: Un solo admin para los 3 nodos
- ✅ **Selección automática**: Nodo y puerto automáticos
- ✅ **Credenciales seguras**: Generación automática de passwords

#### Uso:
```bash
# Instalación simple (desarrollo/pruebas)
python3 magi-installer.py

# Instalación como servicio (producción)
sudo python3 magi-installer.py
```

### 2. 🔧 **magi-quick-install.py** (DESARROLLO)
**Instalador simple sin servicios systemd**

#### Características:
- ✅ **Instalación rápida**: Solo dependencias básicas
- ✅ **Sin privilegios**: No requiere sudo
- ✅ **Detección automática**: Puerto disponible
- ⚠️ **Sin seguridad**: No incluye autenticación

#### Uso:
```bash
python3 magi-quick-install.py
```

---

## 🎯 ¿Qué Instalador Elegir?

### Para Desarrollo/Pruebas:
- **magi-installer.py** (modo simple) → Seguridad + facilidad
- **magi-quick-install.py** → Máxima simplicidad

### Para Producción:
- **magi-installer.py** (modo servicio) → Instalación completa con systemd

---

## 🔒 Seguridad Implementada

### Autenticación Web:
- ✅ Login obligatorio en interfaz web
- ✅ Sesiones seguras con timeout
- ✅ Logout funcional
- ✅ Admin único para los 3 nodos

### API Security:
- ✅ API Key obligatoria para endpoints
- ✅ Bearer token authentication
- ✅ Cross-node API access

### Variables de Entorno:
```bash
MAGI_REQUIRE_LOGIN=true
MAGI_ADMIN_PASSWORD=<generado_automáticamente>
MAGI_REQUIRE_API_KEY=true
MAGI_API_KEY=<generado_automáticamente>
```

---

## 📂 Archivos de Configuración

### Modo Servicio:
- **Configuración**: `/etc/magi/config.env`
- **Servicios systemd**: `/etc/systemd/system/magi-*.service`
- **Archivos**: `/opt/magi-<nodo>/`

### Modo Simple:
- **Configuración**: `./magi_config.env`
- **Scripts**: `./start-magi-<nodo>.sh`, `./stop-magi-<nodo>.sh`
- **Archivos**: Directorio actual

---

## 🚀 Comandos de Gestión

### Modo Servicio:
```bash
# Ver estado
sudo systemctl status magi-gaspar

# Iniciar/detener
sudo systemctl start magi-gaspar
sudo systemctl stop magi-gaspar

# Logs
sudo journalctl -u magi-gaspar -f
```

### Modo Simple:
```bash
# Iniciar
./start-magi-gaspar.sh

# Detener
./stop-magi-gaspar.sh
```

---

## 🌐 Acceso Web

Una vez instalado, accede a tu nodo MAGI:
- **URL**: `http://<tu_ip>:<puerto_asignado>`
- **Usuario**: `admin`
- **Password**: Se muestra al finalizar la instalación

---

## 🔧 Migración desde Instalaciones Anteriores

Si tienes instalaciones previas:

1. **Detener servicios existentes**:
   ```bash
   sudo systemctl stop magi-*
   sudo systemctl disable magi-*
   ```

2. **Limpiar archivos antiguos**:
   ```bash
   sudo rm /etc/systemd/system/magi-*.service
   sudo rm -rf /opt/magi-*
   ```

3. **Reinstalar con el nuevo instalador**:
   ```bash
   sudo python3 magi-installer.py
   ```

---

## ⚡ Funcionalidades por Nodo

### 🎭 GASPAR - Multimedia & Entertainment
- 📺 Gestión de contenido multimedia
- 🎵 Streaming de audio/video
- 🎮 Gaming y entretenimiento

### 📚 MELCHIOR - Backup & Storage
- 💾 Backup automático
- 📁 Gestión de almacenamiento
- 🔄 Sincronización de datos

### 🤖 BALTASAR - Automation & Control
- 🏠 Domótica y control
- 📊 Monitoreo de sistemas
- ⚙️ Automatización de tareas

---

## 🆘 Solución de Problemas

### Error de dependencias:
```bash
# Ubuntu/Debian
sudo apt install python3-psutil

# Arch Linux
sudo pacman -S python-psutil
```

### Puerto ocupado:
El instalador detecta automáticamente puertos disponibles evitando conflictos.

### Permisos insuficientes:
Para instalación como servicio, usar `sudo`.

---

## 📞 Soporte

Para problemas o dudas:
1. Revisar logs del servicio
2. Verificar configuración en `/etc/magi/config.env`
3. Comprobar estado de red y puertos
