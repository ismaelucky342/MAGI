# 🧙‍♂️ MAGI Windows Installation Guide

## 🚀 Quick Installation (Recommended)

### Option 1: PowerShell (Modern Windows)
1. Open **PowerShell as Administrator**
2. Navigate to MAGI folder: `cd C:\path\to\MAGI`
3. Run installer: `.\Install-MAGI.ps1`
4. Follow the prompts
5. Done! 🎉

### Option 2: Simple Batch File
1. Double-click: `install-windows-simple.bat`
2. Choose your node (GASPAR/MELCHIOR/BALTASAR)
3. Follow the prompts
4. Done! 🎉

---

## 📋 Prerequisites

### Python Installation
1. Download Python from: https://python.org
2. **⚠️ IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify: Open Command Prompt and type `python --version`

### Windows Firewall (Optional)
- MAGI will try to configure firewall automatically
- If it fails, manually allow port 8081 in Windows Firewall

---

## 🎯 Choose Your Node

| Node | Purpose | Typical Use |
|------|---------|-------------|
| **GASPAR** | Multimedia & Entertainment | Media server, Plex, gaming PC |
| **MELCHIOR** | Backup & Storage | NAS, file server, backups |
| **BALTASAR** | Home Automation | IoT hub, smart home controller |

---

## 🚀 Starting MAGI

### Method 1: Desktop Shortcut
- Double-click **"Start-MAGI-[NODE].bat"** on desktop

### Method 2: Start Menu
- Start Menu → Programs → MAGI → Start-MAGI-[NODE]

### Method 3: PowerShell
```powershell
.\magi-service.ps1 start
```

### Method 4: Command Line
```cmd
python magi-node.py GASPAR
```

---

## 🌐 Accessing the Dashboard

### Method 1: Desktop Shortcut
- Double-click **"Open-MAGI-Dashboard.bat"** on desktop

### Method 2: Browser
- Open: http://localhost:8081

### Method 3: Network Access
- From other devices: http://[your-pc-ip]:8081

---

## 🔧 Management Commands

### PowerShell Management
```powershell
# Start MAGI
.\magi-service.ps1 start

# Stop MAGI
.\magi-service.ps1 stop

# Check status
.\magi-service.ps1 status
```

### Windows Services (Advanced)
If you installed with the full installer:
```cmd
# Start service
net start "MAGI_GASPAR"

# Stop service
net stop "MAGI_GASPAR"

# Check status
sc query "MAGI_GASPAR"
```

---

## 🏠 Auto-Start with Windows

MAGI can automatically start when Windows boots:

### Option 1: During Installation
- Choose "yes" when asked about auto-start

### Option 2: Manual Setup
1. Copy `Start-MAGI-[NODE].bat` to:
   `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`

### Option 3: Windows Service (Advanced)
- If installed as service, it will auto-start automatically

---

## 🐛 Troubleshooting

### Python Not Found
```cmd
# Check if Python is in PATH
python --version

# If not found, reinstall Python with "Add to PATH" checked
```

### Port Already in Use
```cmd
# Check what's using port 8081
netstat -an | findstr :8081

# Kill process if needed
taskkill /f /im python.exe
```

### Firewall Issues
1. Open Windows Firewall
2. Allow app through firewall
3. Add Python.exe or allow port 8081

### Permission Issues
- Run installer as Administrator
- Or use the simple installer (no admin needed)

---

## 📁 File Structure

After installation, you'll have:

```
MAGI/
├── magi-node.py              # Main MAGI application
├── Install-MAGI.ps1          # PowerShell installer
├── install-windows-simple.bat # Simple batch installer
├── Start-MAGI-[NODE].bat     # Node launcher
├── Open-MAGI-Dashboard.bat   # Dashboard opener
├── magi-service.ps1          # PowerShell service manager
└── README-Windows.md         # This file
```

---

## 🌐 Network Configuration

### Default Node IPs
- **GASPAR**: 192.168.1.100:8081
- **MELCHIOR**: 192.168.1.101:8081
- **BALTASAR**: 192.168.1.102:8081

### Custom Configuration
Edit `magi-node.py` and modify the CONFIG section:
```python
CONFIG = {
    "node_name": "GASPAR",
    "port": 8081,
    "other_nodes": [
        {"name": "GASPAR", "ip": "192.168.1.100", "port": 8081},
        {"name": "MELCHIOR", "ip": "192.168.1.101", "port": 8081},
        {"name": "BALTASAR", "ip": "192.168.1.102", "port": 8081}
    ]
}
```

---

## 🎮 Advanced Features

### Multiple Nodes on Same Machine
```cmd
# Start multiple nodes on different ports
python magi-node.py GASPAR
python magi-node.py MELCHIOR   # Will use port 8082
```

### Custom Port
Edit `magi-node.py` and change:
```python
"port": 8081,  # Change to your preferred port
```

### Windows Task Scheduler (Alternative to Service)
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start a program
5. Program: `python`
6. Arguments: `C:\path\to\MAGI\magi-node.py GASPAR`
7. Start in: `C:\path\to\MAGI`

---

## 🆘 Getting Help

### Check MAGI Status
```powershell
.\magi-service.ps1 status
```

### View Logs
- MAGI outputs logs to the console
- For service installation, check Windows Event Viewer

### Common Issues
1. **"Python not found"** → Reinstall Python with PATH option
2. **"Port already in use"** → Kill existing Python processes
3. **"Access denied"** → Run installer as Administrator
4. **"Dashboard won't open"** → Check Windows Firewall

### Reset Installation
1. Stop MAGI: `.\magi-service.ps1 stop`
2. Delete shortcuts from Desktop and Start Menu
3. Remove from Startup folder if added
4. Run installer again

---

## 🎉 Success!

If you see this in your terminal:
```
🧙‍♂️ MAGI GASPAR server started
📡 Access dashboard: http://localhost:8081
🌐 Network access: http://[your-ip]:8081
```

**Congratulations! MAGI is running successfully! 🎊**

Open http://localhost:8081 and enjoy your Evangelion-themed monitoring system!
