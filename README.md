# 🧙‍♂️ MAGI - Ultra-Simple Distributed Monitoring

**Distributed Node Monitoring System**

> Inspired by Evangelion's MAGI supercomputer system
> Ultra-simple, cross-platform, zero-dependency hell

## 🎯 Philosophy
- **One Python file per node** - No complex installations
- **Pure HTML/CSS/JS** - No frameworks, no build processes
- **Cross-platform** - Works on Linux, Windows, macOS out of the box
- **Self-contained** - Each node serves its own web interface

## 🏗️ Architecture

```
GASPAR (192.168.1.100:8080)    MELCHIOR (192.168.1.101:8080)    BALTASAR (192.168.1.102:8080)
├── magi-node.py               ├── magi-node.py                 ├── magi-node.py
├── web/                       ├── web/                         ├── web/
│   ├── index.html            │   ├── index.html              │   ├── index.html
│   ├── style.css             │   ├── style.css               │   ├── style.css
│   └── app.js                │   └── app.js                  │   └── app.js
└── config.json               └── config.json                 └── config.json
```

## 🚀 Quick Start

### 1. Install on each node (3 commands total):
```bash
# Download MAGI
curl -O https://raw.githubusercontent.com/tu-repo/MAGI/main/install.py
python install.py --node-name=GASPAR --ip=192.168.1.100

# Start MAGI
python magi-node.py
```

### 2. Access any node:
- GASPAR: http://192.168.1.100:8080
- MELCHIOR: http://192.168.1.101:8080  
- BALTASAR: http://192.168.1.102:8080

### 3. Central monitoring:
- Open any node's web interface
- It automatically discovers and connects to other nodes
- See all 3 nodes in one dashboard

## � Installation

### 🌟 Universal Installer (Recommended)
Works on **Linux**, **Windows**, and **macOS**:

```bash
# Download MAGI and run universal installer
python3 install-universal.py
```

### 🐧 Linux Installation

#### Option 1: User Service (No sudo required)
```bash
./install-user-service.sh
```

#### Option 2: System Service (Requires sudo)
```bash
./install-service.sh
```

#### Option 3: Manual
```bash
python3 magi-node.py GASPAR
```

### 🪟 Windows Installation

#### Option 1: PowerShell (Modern Windows)
```powershell
# Run as Administrator
.\Install-MAGI.ps1
```

#### Option 2: Simple Batch File
```cmd
# Double-click or run
install-windows-simple.bat
```

#### Option 3: Manual
```cmd
python magi-node.py GASPAR
```

### 🍎 macOS Installation

#### Option 1: Universal Installer
```bash
python3 install-universal.py
```

#### Option 2: Manual
```bash
python3 magi-node.py GASPAR
```

---

## 📋 Prerequisites

### All Platforms
- **Python 3.6+** with `pip`
- **Network connectivity** between nodes
- **Port 8081** available (configurable)

### Platform-Specific Downloads
- **Windows**: [Python.org](https://python.org) - ⚠️ Check "Add Python to PATH"
- **Linux**: Usually pre-installed, or `sudo apt install python3`
- **macOS**: `brew install python3` or [Python.org](https://python.org)

---

## 🔧 Features

- **Real-time metrics**: CPU, RAM, Disk, Network
- **System info**: OS, uptime, processes
- **Cross-node communication**: Each node can see others
- **Web terminal**: Execute commands remotely
- **Auto-discovery**: Nodes find each other automatically
- **Responsive UI**: Works on desktop and mobile

## 💻 Supported Platforms

- ✅ **Linux** (Ubuntu, CentOS, Arch, etc.)
- ✅ **Windows** (10, 11)  
- ✅ **macOS** (Intel, Apple Silicon)
- ✅ **Python 3.6+** (usually pre-installed)

---

*No npm. No node_modules. No build process. Just Python and HTML.* 🐍✨
# MAGI - Distributed Node Monitoring System

<div align="center">
  <img src="./images/MAGI.png" alt="MAGI Logo" width="200"/>
  <h3>Multi-Node Monitoring & Management Interface</h3>
</div>

## Overview


MAGI is a distributed monitoring system designed to manage and monitor three specialized nodes:

- **🤖 Baltasar** - Main AI & multimedia server (Jellyfin, AI workloads, high performance)
- **💾 Gaspar** - Backup and mass storage server
- **🏠 Melchor** - Home Assistant, IoT, and monitoring server

## Features

- **📊 Real-time Metrics** - CPU, RAM, disk, network, service status
- **🖥️ Web Terminal** - SSH access to any node via browser
- **🚨 Smart Alerts** - Visual and audio notifications for failures
- **🔄 Portable** - Deploy on any of the three nodes (Linux or Windows)
- **🔒 Secure** - JWT authentication + SSH key management
- **📱 Responsive** - Works on desktop, tablet, and mobile


## Quick Start (Linux & Windows)

### Prerequisites

- Docker & Docker Compose (recommended for all platforms)
- Node.js 18+ (for native development)
- SSH access to all nodes

### 1. Clone the repository
```bash
git clone <repository-url>
cd MAGI
```

### 2. Setup (Linux/macOS)
```bash
make install    # Complete setup
make dev        # Start development (frontend+backend)
make start      # Start with Docker
make deploy     # Deploy to nodes
```

### 2. Setup (Windows)

- If using WSL: Use the same Linux commands above.
- If using native Windows (PowerShell):
  1. Install Node.js and Docker Desktop for Windows.
  2. Run:
     ```powershell
     npm install
     cd backend; npm install; cd ..
     cd frontend; npm install; cd ..
     # To start backend:
     cd backend; npm run dev
     # To start frontend:
     cd frontend; npm start
     ```
  3. Or use Docker Compose:
     ```powershell
     docker-compose up --build
     ```

### 3. Configure nodes
Edit `config/nodes.json` with your actual node information.

### 4. Configuration of ports and IP

- The backend and frontend ports are configurable in the `.env` file:
  ```env
  PORT=5000         # Backend port
  FRONTEND_PORT=3000 # Frontend port
  HOST=0.0.0.0      # Listen on all interfaces (for remote access)
  ```
- To expose metrics on a specific port/IP, edit `.env` and restart the services.

### 5. Access the interface
The web interface will be available at `http://<your-ip>:<FRONTEND_PORT>` (default: `http://localhost:3000`).

### 6. Notes
- All commands/scripts are compatible with Linux, macOS, and WSL. For native Windows, use PowerShell equivalents or Docker Compose.
- For production, it is recommended to use Docker for maximum portability.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     GASPAR      │    │     MELCHOR     │    │    BALTASAR     │
│  (Multimedia)   │    │   (Backup)      │    │ (Home Auto)     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Jellyfin      │    │ • Rsync         │    │ • Home Assistant│
│ • Transmission  │    │ • Duplicity     │    │ • Node-RED      │
│ • Plex          │    │ • Nextcloud     │    │ • Zigbee2MQTT   │
│ • Node Exporter │    │ • Node Exporter │    │ • Node Exporter │
│ • MAGI Instance │    │ • MAGI Instance │    │ • MAGI Instance │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────────┐
                    │     MAGI INTERFACE      │
                    │                         │
                    │ • Real-time Dashboard   │
                    │ • SSH Terminal Access   │
                    │ • Metrics Collection    │
                    │ • Alert Management      │
                    │ • Service Control       │
                    └─────────────────────────┘
```

## Configuration

### Node Configuration

Edit `config/nodes.json`:

```json
{
  "nodes": [
    {
      "id": "gaspar",
      "name": "Gaspar",
      "role": "Multimedia Server",
      "ip": "192.168.1.100",
      "services": ["jellyfin", "transmission", "plex"],
      "metrics_port": 9100,
      "ssh": {
        "port": 22,
        "username": "admin"
      }
    }
  ]
}
```

### Environment Variables

Create `.env` files in both `backend/` and `frontend/` directories:

**Backend (.env):**
```env
NODE_ENV=production
PORT=5000
JWT_SECRET=your-super-secret-key
REDIS_URL=redis://localhost:6379
```

**Frontend (.env):**
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_WS_URL=ws://localhost:5000
```

## Development Commands

### Interactive Menu
```bash
make menu              # Launch interactive management menu
```

### Quick Commands
```bash
make help             # Show all available commands
make install          # Complete setup (first time)
make dev              # Start development environment
make start            # Start with Docker Compose
make stop             # Stop Docker services
make build            # Build applications
make deploy           # Interactive deployment menu
make status           # Check system status
make clean            # Clean environment
```

### Frontend & Backend
```bash
make frontend         # Start frontend only (UI testing)
make backend          # Start backend only (API testing)
make test             # Run all tests
make logs             # View Docker logs
```

### Deployment
```bash
make deploy                    # Interactive deployment
make deploy-node NODE=gaspar   # Deploy to specific node
./scripts/deploy-all-nodes.sh all  # Deploy to all nodes
```

## Development

### Project Structure

```
MAGI/
├── frontend/              # React TypeScript application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # API services
│   │   └── utils/        # Utilities
├── backend/              # Node.js Express API
│   ├── src/
│   │   ├── controllers/  # Route controllers
│   │   ├── services/     # Business logic
│   │   ├── middleware/   # Express middleware
│   │   └── utils/        # Utilities
├── docker/               # Docker configurations
├── config/               # Configuration files
├── scripts/              # Automation scripts
└── docs/                 # Documentation
```



