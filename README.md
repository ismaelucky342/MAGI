# 🔥 MAGI v2.0 - Sistema de Monitoreo Distribuido

Sistema de monitoreo inspirado en Evangelion para gestionar nodos de red doméstica.

## 🚀 Instalación Rápida (Linux)

```bash
sudo python3 install-magi-service.py
```

## ✨ Características

- 📊 **Monitoreo en tiempo real** - CPU, RAM, Disco, Red, Temperatura
- 🔋 **Gestión de energía** - Estados de ahorro automático
- 🌐 **Detección de nodos** - Comunicación entre nodos MAGI
- ⚙️ **Detección de servicios** - Nextcloud, Jellyfin, etc.
- 🎨 **Interfaz Evangelion** - Diseño negro con neones rojos
- 🔧 **Servicio systemd** - Arranque automático del sistema

## 🎯 Nodos Disponibles

- **GASPAR** - Multimedia & Entertainment
- **MELCHIOR** - Backup & Storage  
- **BALTASAR** - Automation & Control

## 🛠️ Gestión del Servicio

```bash
# Ver estado
sudo systemctl status magi-gaspar

# Reiniciar
sudo systemctl restart magi-gaspar

# Ver logs
sudo journalctl -u magi-gaspar -f
```

## 🌐 Acceso

El instalador proporciona automáticamente la URL de acceso con la IP de tu PC.

## 📁 Estructura Final

```
MAGI/
├── magi-node-v2.py          # Aplicación principal
├── power-save-mode.py       # Gestión de energía
├── install-magi-service.py  # Instalador de servicio
├── images/                  # Recursos gráficos
└── README.md               # Este archivo
```

## 🔧 Requisitos

- Python 3.6+
- psutil (se instala automáticamente)
- Permisos de administrador para la instalación

---

**Desarrollado para home lab con estética Evangelion** 🤖
