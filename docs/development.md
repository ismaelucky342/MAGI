# MAGI Development Guide

## Quick Start

1. **Initial Setup**
```bash
./scripts/setup.sh
```

2. **Configure Nodes**
```bash
# Edit with your actual node information
nano config/nodes.json
```

3. **Start Development Environment**
```bash
npm run dev
```

4. **Access the Interface**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Default login: admin/admin

## Development Commands

### Full Stack Development
```bash
npm run dev                 # Start both frontend and backend
npm run build              # Build both applications
npm run docker:build       # Build Docker images
npm run docker:up          # Start with Docker Compose
npm run docker:down        # Stop Docker containers
```

### Backend Development
```bash
cd backend
npm run dev                # Start with hot reload
npm run build              # Build TypeScript
npm start                  # Start production build
npm test                   # Run tests
```

### Frontend Development
```bash
cd frontend
npm start                  # Start with hot reload
npm run build              # Build for production
npm test                   # Run tests
```

## Architecture Overview

```
MAGI/
├── frontend/              # React TypeScript application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── contexts/     # React contexts
│   │   ├── hooks/        # Custom React hooks
│   │   ├── services/     # API and utility services
│   │   ├── types/        # TypeScript type definitions
│   │   └── utils/        # Utility functions
│   ├── public/           # Static assets
│   └── Dockerfile        # Frontend container config
├── backend/              # Node.js Express API
│   ├── src/
│   │   ├── routes/       # API route handlers
│   │   ├── services/     # Business logic services
│   │   ├── middleware/   # Express middleware
│   │   ├── utils/        # Utility functions
│   │   └── types/        # TypeScript types
│   └── Dockerfile        # Backend container config
├── config/               # Configuration files
├── scripts/              # Automation scripts
└── docs/                 # Documentation
```

## Key Components

### Frontend
- **Dashboard**: Main monitoring interface with node cards
- **NodeDetail**: Detailed view of individual nodes
- **Terminal**: Web-based SSH terminal interface
- **Login**: Authentication interface
- **Settings**: Configuration management

### Backend
- **API Routes**: RESTful endpoints for data operations
- **WebSocket**: Real-time metrics and notifications
- **Metrics Collector**: Gathers data from node exporters
- **SSH Service**: Manages terminal connections
- **Redis**: Caching and session management

## Configuration

### Node Configuration (`config/nodes.json`)
```json
{
  "nodes": [
    {
      "id": "gaspar",
      "name": "Gaspar",
      "role": "Multimedia Server",
      "ip": "192.168.1.100",
      "services": [
        {
          "name": "jellyfin",
          "display_name": "Jellyfin",
          "port": 8096,
          "critical": true
        }
      ]
    }
  ]
}
```

### Environment Variables

**Backend (`.env`)**
```env
NODE_ENV=development
PORT=5000
JWT_SECRET=your-secret-key
REDIS_URL=redis://localhost:6379
```

**Frontend (`.env`)**
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_WS_URL=ws://localhost:5000
```

## Deployment

### Single Node (Development)
```bash
npm run docker:up
```

### Multiple Nodes (Production)
```bash
# Deploy to all nodes
./scripts/deploy-all-nodes.sh all

# Deploy to specific node
./scripts/deploy-all-nodes.sh gaspar
```

### Manual Node Setup
```bash
# Install Node Exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
sudo mv node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/

# Install ttyd for terminal access
sudo apt-get install ttyd
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/verify` - Token verification

### Nodes
- `GET /api/nodes` - List all nodes
- `GET /api/nodes/:id` - Get specific node
- `GET /api/nodes/:id/status` - Get node status

### Metrics
- `GET /api/metrics` - Get all metrics
- `GET /api/metrics/:nodeId` - Get node metrics

### Terminal
- `POST /api/terminal/:nodeId/create` - Create SSH session
- `GET /api/terminal/sessions` - List active sessions

## WebSocket Events

### Client → Server
- `join-room` - Join monitoring room
- `metrics-request` - Request metrics update

### Server → Client
- `metrics-update` - Real-time metrics data
- `node-status-change` - Node status updates
- `alert` - System alerts and notifications

## Monitoring Integration

### Node Exporter Metrics
- CPU usage and load average
- Memory usage and availability
- Disk usage and I/O statistics
- Network interface statistics
- System uptime and processes

### Service Health Checks
- HTTP endpoint monitoring
- Port connectivity checks
- Process status verification
- Custom health endpoints

## Security

### Authentication
- JWT-based session management
- Secure password hashing with bcrypt
- Rate limiting on login attempts
- Session timeout and cleanup

### SSH Access
- Key-based authentication only
- No password authentication
- Restricted user permissions
- Audit logging of terminal sessions

### Network Security
- HTTPS in production
- CORS configuration
- Input validation and sanitization
- SQL injection prevention (if database used)

## Troubleshooting

### Common Issues

**Cannot connect to nodes**
```bash
# Check network connectivity
ping 192.168.1.100

# Verify SSH access
ssh admin@gaspar.local

# Check if Node Exporter is running
curl http://192.168.1.100:9100/metrics
```

**WebSocket connection failed**
- Check if backend is running on correct port
- Verify firewall settings
- Check CORS configuration

**Authentication issues**
- Clear browser localStorage
- Check JWT_SECRET configuration
- Verify Redis connection

### Log Locations
- Backend logs: `backend/logs/magi.log`
- Frontend build logs: Browser console
- Docker logs: `docker-compose logs`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style
- TypeScript for all new code
- ESLint and Prettier for formatting
- Conventional commits for commit messages
- Comprehensive error handling

## License

MIT License - see LICENSE file for details
