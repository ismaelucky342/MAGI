# MAGI - Distributed Node Monitoring System

<div align="center">
  <img src="./images/MAGI.png" alt="MAGI Logo" width="200"/>
  <h3>Multi-Node Monitoring & Management Interface</h3>
</div>

## Overview

MAGI is a distributed monitoring system designed to manage and monitor three specialized nodes:

- **🎬 Gaspar** - Multimedia server (Jellyfin, downloads, media storage)
- **💾 Melchor** - Backup and mass storage server  
- **🏠 Baltasar** - Home automation server (Home Assistant, IoT)

## Features

- **📊 Real-time Metrics** - CPU, RAM, disk, network, service status
- **🖥️ Web Terminal** - SSH access to any node via browser
- **🚨 Smart Alerts** - Visual and audio notifications for failures
- **🔄 Portable** - Deploy on any of the three nodes
- **🔒 Secure** - JWT authentication + SSH key management
- **📱 Responsive** - Works on desktop, tablet, and mobile

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for development)
- SSH access to all nodes

### Interactive Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd MAGI
```

2. **Launch the interactive menu:**
```bash
make menu
# or
./scripts/magi-menu.sh
```

3. **Quick setup with Makefile:**
```bash
make install    # Complete setup
make dev        # Start development
make start      # Start with Docker
make deploy     # Deploy to nodes
```

### Manual Setup

1. **Install and configure:**
```bash
make install
make setup
```

2. **Configure nodes:**
```bash
# Edit with your actual node information
nano config/nodes.json
```

3. **Start development:**
```bash
make dev
```

4. **Or start with Docker:**
```bash
make start
```

The interface will be available at `http://localhost:3000`

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

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security

- All SSH connections use key-based authentication
- Web interface requires JWT token authentication
- HTTPS enabled in production
- Rate limiting on API endpoints
- Input validation and sanitization

## Monitoring Endpoints

- **Health Check**: `GET /api/health`
- **Node Status**: `GET /api/nodes/:nodeId/status`
- **Metrics**: `GET /api/nodes/:nodeId/metrics`
- **Services**: `GET /api/nodes/:nodeId/services`

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

- Inspired by the MAGI system from Neon Genesis Evangelion
- Built for home lab enthusiasts and self-hosted infrastructure
