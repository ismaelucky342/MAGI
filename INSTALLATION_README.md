# 🧙‍♂️ MAGI v2.0 - Configuración Unificada de Usuario Admin

## ✅ Cambios Implementados

### 🔑 **Usuario Admin Unificado**
- **Un solo usuario admin** para los 3 nodos (GASPAR, MELCHIOR, BALTASAR)
- **Configuración centralizada** en `/etc/magi/config.env`
- **Script de instalación** que configura todo automáticamente
- **Mismas credenciales** para acceder a cualquier nodo

### 📋 **Simplificación de Credenciales**
- ❌ Eliminado usuario "magi" 
- ❌ Eliminada variable `MAGI_USER_PASSWORD`
- ✅ Solo un usuario: **admin**
- ✅ Una variable: `MAGI_ADMIN_PASSWORD`

## 🚀 Instalación Automatizada

### **Opción 1: Instalación Interactiva**
```bash
sudo bash install_magi.sh
```
- Te pedirá password de admin (o generará uno automático)
- Generará API key automáticamente
- Configurará los 3 nodos con las mismas credenciales

### **Opción 2: Instalación No Interactiva**
```bash
sudo bash install_magi.sh --admin-password "MySecurePass123!" --non-interactive
```

### **Opción 3: Configuración Completa**
```bash
sudo bash install_magi.sh \
  --admin-password "MySecurePass123!" \
  --api-key "magi-super-secret-key-2024" \
  --install-dir "/opt/magi" \
  --non-interactive
```

## 📁 Estructura Posterior a la Instalación

```
/opt/magi/                     # Archivos del programa
├── magi-node-v2.py          # Programa principal
├── magi-node-*.py           # Wrappers de nodos
├── setup_security.sh        # Scripts de seguridad
└── images/                   # Recursos web

/etc/magi/                     # Configuración
└── config.env               # Configuración unificada compartida

/etc/systemd/system/          # Servicios
├── magi-gaspar.service      # Servicio GASPAR (puerto 8081)
├── magi-melchior.service    # Servicio MELCHIOR (puerto 8082)
└── magi-baltasar.service    # Servicio BALTASAR (puerto 8083)
```

## 🔧 Configuración Unificada

### **Archivo `/etc/magi/config.env`:**
```bash
# MAGI v2.0 Configuration
# This file is shared by all MAGI nodes

# Admin credentials (same for all nodes)
export MAGI_REQUIRE_LOGIN=true
export MAGI_ADMIN_PASSWORD="generated-or-provided-password"

# API configuration  
export MAGI_REQUIRE_API_KEY=true
export MAGI_API_KEY="magi-generated-api-key"

# Network configuration
export MAGI_BIND="0.0.0.0"
```

### **Servicios systemd automáticos:**
Cada servicio usa `EnvironmentFile=/etc/magi/config.env` para cargar la configuración compartida.

## 🎯 Uso Después de la Instalación

### **Gestión de Servicios:**
```bash
# Iniciar todos los nodos
sudo systemctl start magi-{gaspar,melchior,baltasar}

# Habilitar autostart
sudo systemctl enable magi-{gaspar,melchior,baltasar}

# Ver estado
sudo systemctl status magi-gaspar
sudo systemctl status magi-melchior
sudo systemctl status magi-baltasar

# Ver logs en tiempo real
sudo journalctl -u magi-gaspar -f
```

### **Acceso Web Unificado:**
- 🌐 **GASPAR**: http://your-ip:8081 → login: `admin` / `password-configurado`
- 🌐 **MELCHIOR**: http://your-ip:8082 → login: `admin` / `password-configurado`
- 🌐 **BALTASAR**: http://your-ip:8083 → login: `admin` / `password-configurado`

**¡Las mismas credenciales funcionan en los 3 nodos!**

### **API Access:**
```bash
# Mismo API key para todos los nodos
API_KEY="$(grep MAGI_API_KEY /etc/magi/config.env | cut -d'"' -f2)"

curl -H "Authorization: Bearer $API_KEY" http://localhost:8081/api/metrics
curl -H "Authorization: Bearer $API_KEY" http://localhost:8082/api/metrics  
curl -H "Authorization: Bearer $API_KEY" http://localhost:8083/api/metrics
```

## 🔄 Migración desde Configuración Anterior

Si ya tenías nodos configurados manualmente:

### **1. Parar servicios existentes:**
```bash
sudo systemctl stop magi-*
```

### **2. Ejecutar instalación:**
```bash
sudo bash install_magi.sh --admin-password "your-preferred-password"
```

### **3. Iniciar nuevos servicios:**
```bash
sudo systemctl start magi-{gaspar,melchior,baltasar}
```

## 🛠️ Desarrollo/Testing Local

### **Para desarrollo sin sudo:**
```bash
# Configurar variables localmente
export MAGI_ADMIN_PASSWORD="dev123"
export MAGI_API_KEY="dev-key" 
export MAGI_REQUIRE_LOGIN=true

# Ejecutar nodos individuales
python3 magi-node-v2.py GASPAR
python3 magi-node-v2.py MELCHIOR  
python3 magi-node-v2.py BALTASAR
```

### **O usar wrappers:**
```bash
MAGI_ADMIN_PASSWORD="dev123" python3 magi-node-gaspar.py
MAGI_ADMIN_PASSWORD="dev123" python3 magi-node-melchior.py
MAGI_ADMIN_PASSWORD="dev123" python3 magi-node-baltasar.py
```

## ✅ Beneficios de la Nueva Configuración

1. **🔑 Gestión simplificada**: Un solo admin password para todo
2. **🔄 Configuración centralizada**: Cambiar password en un solo lugar
3. **⚙️ Instalación automática**: Script que configura todo
4. **🔧 Systemd integration**: Servicios profesionales con EnvironmentFile
5. **🛡️ Seguridad mantenida**: Misma protección, más simple de gestionar
6. **📋 Logs centralizados**: journalctl para todos los servicios

## 🎉 Resultado Final

El usuario admin ahora:
- ✅ Se configura **una sola vez** durante la instalación
- ✅ Es **el mismo** para los 3 nodos (GASPAR, MELCHIOR, BALTASAR)
- ✅ Se almacena en **configuración centralizada** (`/etc/magi/config.env`)
- ✅ Se puede cambiar **fácilmente** editando un solo archivo
- ✅ Es **seguro** y **profesional** con systemd services

¡La gestión de usuarios MAGI es ahora mucho más simple y unificada! 🧙‍♂️
