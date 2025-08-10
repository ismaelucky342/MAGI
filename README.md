### Instalación rápida en Windows

1. Abre PowerShell y navega a la carpeta del repositorio MAGI.
2. Ejecuta el script automatizado:
  ```powershell
  ./install-windows.ps1
  ```
3. Cuando termine, inicia la app con:
  ```powershell
  cd frontend
  npm run electron:start
  ```
4. ¡Listo! MAGI se abrirá como aplicación de escritorio.

## Desktop App (Electron)

MAGI puede ejecutarse como aplicación de escritorio en Linux y Windows usando Electron.

### Ejecución en modo app (desarrollo)

1. Instala dependencias adicionales:
  ```bash
  cd frontend
  npm install --save-dev electron electron-builder concurrently cross-env wait-on
  ```
2. Inicia la app de escritorio:
  ```bash
  npm run electron:start
  ```
  Esto abrirá la interfaz React en una ventana nativa.

### Empaquetar la app (producción)

1. Construye la app React:
  ```bash
  npm run build
  ```
2. Empaqueta la app de escritorio:
  ```bash
  npx electron-builder
  ```
  El instalador estará disponible en la carpeta `dist/`.

### Notas
- Puedes ejecutar la app en cualquier nodo (Baltasar, Gaspar o Melchor).
- La app puede convivir con la versión web y acceder a los mismos servicios backend.
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



