# MAGI Node Windows Installer v2.0.0

## 🚀 Installation Options

### Option 1: Python GUI Installer (RECOMMENDED)
1. Double-click "install_magi.py"
2. Follow the graphical installer
3. Choose installation directory and options
4. GUI will check system requirements automatically

### Option 2: Python Full Installer
1. Double-click "magi_windows_python_installer.py"
2. Complete GUI installer with all options

### Option 3: Batch Installer (Classic)
1. Double-click "install_magi_windows.bat" 
2. Follow command-line prompts

### Option 4: Portable Mode
1. Double-click "MAGI_Portable.bat"
2. Runs directly from current folder (no installation)

## 🖥️ Running MAGI Node

After installation, start MAGI Node by:
- Double-clicking the desktop shortcut "MAGI Node"
- Using Start Menu > Programs > MAGI > MAGI Node  
- Running the launcher: [Install_Dir]\magi_launcher.py
- Running batch file: [Install_Dir]\MAGI_Node.bat

## 🌐 Access Dashboard

Once running, access the MAGI dashboard at:
http://localhost:8080

The node will auto-detect its name (GASPAR/MELCHIOR/BALTASAR) and find an available port.

## 📋 Requirements

- Windows 10/11
- Python 3.8+ (download from https://www.python.org/downloads/)
- Internet connection for initial setup

## 🎯 What Gets Installed

- MAGI Node main application
- Auto-launcher with GUI
- Desktop shortcut (optional)
- Start Menu entry
- Uninstaller
- All required dependencies (psutil)

## 🔧 Troubleshooting

1. **Python not found**: Install Python from python.org
2. **Permission denied**: Run as Administrator
3. **Port already in use**: MAGI will auto-find an available port
4. **Dependencies missing**: Installer will auto-install psutil
5. **GUI doesn't work**: Try the batch installer instead

## � Features

- Auto-detection of node name based on hostname/IP
- Automatic port discovery
- Local IP detection
- GUI and console modes
- Clean uninstaller
- Portable mode option

## 🗑️ Uninstalling

- Use: [Install_Dir]\uninstall_magi.py
- OR manually delete installation directory

## 📞 Support

Visit: https://github.com/ismaelucky342/MAGI

Version: 2.0.0
Updated: 2025-08-10
Created: 2025-08-10
