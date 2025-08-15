# MAGI - Distributed Infrastructure Monitoring System
<img width="879" height="349" alt="image" src="https://github.com/user-attachments/assets/e8931265-f75d-458f-8076-8cb71392010b" />


A distributed monitoring system designed for managing and monitoring multiple nodes in local network infrastructures. MAGI provides real-time system metrics, service discovery, and remote management capabilities across networked devices.

## Architecture Overview

MAGI operates as a distributed monitoring solution where each node runs independently while maintaining communication with other nodes in the network. The system automatically discovers services and provides centralized monitoring through a web interface.

### Node Topology

```
    ┌─────────────────────────────────────────────────────────────────┐
    │                    MAGI DISTRIBUTED SYSTEM                     │
    └─────────────────────────────────────────────────────────────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
         ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
         │   GASPAR    │      │  MELCHIOR   │      │  BALTASAR   │
         │             │      │             │      │             │
         │   BACKUP    │◄────►│ MONITORING  │◄────►│ STREAMING   │
         │    NODE     │      │    NODE     │      │  AI & VRT   │
         │             │      │             │      │             │
         │ • Nextcloud │      │ • Home Asst │      │ • Jellyfin  │
         │ • Backups   │      │ • Monitor   │      │ • Plex      │
         │ • File Sync │      │ • Logs      │      │ • AI Models │
         │ • Archives  │      │ • Alerts    │      │ • VMs/LXC   │
         └─────────────┘      └─────────────┘      └─────────────┘
```

### Key Components

- **Node Agent**: Main monitoring service (`magi-node-v2.py`)
- **Power Management**: Energy state control (`power-save-mode.py`)
- **Universal Installer**: Unified deployment system (`magi-installer.py`)
- **Quick Installer**: Simple setup for development (`magi-quick-install.py`)
- **Web Interface**: Secure dashboard with authentication and REST API

## Features

- **Real-time Monitoring**: CPU, memory, disk, network, and temperature metrics
- **Service Discovery**: Automatic detection of running services (Nextcloud, Jellyfin, Docker, SSH, etc.)
- **Multi-node Communication**: Cross-node metrics aggregation and status reporting
- **Power Management**: Remote shutdown, reboot, and performance mode control
- **Security**: Web authentication, API keys, session management
- **Unified Configuration**: Single admin account across all nodes
- **REST API**: Comprehensive secured API for system integration
- **Web Dashboard**: Modern authenticated web interface for centralized management

## Node Specifications

### GASPAR - Backup & Storage Node
- **Primary Function**: Data backup, file synchronization, and storage management
- **Typical Services**: Nextcloud, File servers, Backup solutions, Archive systems, RAID management
- **Hardware Profile**: Maximum storage capacity, RAID configurations, High I/O performance
- **Network Usage**: Continuous sync operations, backup transfers, file sharing


### MELCHIOR - Monitoring & Home Assistant Node  
- **Primary Function**: System monitoring, home automation, and alert management
- **Typical Services**: Home Assistant, System monitors, Log aggregation, Alert systems, IoT coordination
- **Hardware Profile**: Always-on operation, Low-medium power, Reliable connectivity
- **Network Usage**: IoT device communication, sensor data, monitoring telemetry

### BALTASAR - Streaming, AI & Virtualization Node
- **Primary Function**: Media streaming, AI processing, and virtualization services
- **Typical Services**: Jellyfin, Plex, AI models, Virtual machines, Container orchestration
- **Hardware Profile**: High CPU/GPU performance, Large RAM, Hardware acceleration
- **Network Usage**: High bandwidth streaming, AI model inference, VM networking

## Quick Installation

### 🚀 Universal Installer (Recommended)
```bash
# Download unified installer
wget https://raw.githubusercontent.com/ismaelucky342/MAGI/main/magi-installer.py
chmod +x magi-installer.py

# Simple installation (development/testing)
python3 magi-installer.py

# Production installation (systemd service)
sudo python3 magi-installer.py
```

### 🔧 Quick Development Setup
```bash
# Clone repository
git clone https://github.com/ismaelucky342/MAGI.git
cd MAGI

# Quick setup without systemd
python3 magi-quick-install.py

# Or full installation with security
python3 magi-installer.py
```

### 📖 Installation Guide
For detailed installation options and configuration, see: [**INSTALLATION_GUIDE.md**](INSTALLATION_GUIDE.md)

## Deployment

### System Requirements
- **Operating System**: Linux (Ubuntu 18.04+, Debian 9+, CentOS 7+)
- **Python**: 3.6 or higher
- **Memory**: Minimum 256MB RAM
- **Storage**: 100MB available space
- **Network**: TCP port 8080 (configurable)

### Dependencies
- `psutil` - System and process utilities
- `requests` - HTTP library for node communication

### Service Management
```bash
# Check service status
sudo systemctl status magi-<node-name>

# Start/Stop service
sudo systemctl start magi-<node-name>
sudo systemctl stop magi-<node-name>

# Enable/Disable autostart
sudo systemctl enable magi-<node-name>
sudo systemctl disable magi-<node-name>

# View logs
sudo journalctl -u magi-<node-name> -f
```

## Configuration

### Node Configuration
Each node can be configured with a unique identifier:
```bash
python3 magi-node-v2.py <NODE_NAME>
```

### Network Configuration
- Default port: 8080
- Auto-discovery range: Local subnet
- Cross-node communication: HTTP REST API

## API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/metrics` | GET | System metrics (CPU, memory, disk, network) |
| `/api/services` | GET | Detected services and their status |
| `/api/power/mode` | POST | Change power management mode |
| `/api/system/shutdown` | POST | Schedule system shutdown |
| `/api/system/reboot` | POST | Schedule system reboot |
| `/api/system/sleep` | POST | Put system to sleep |
| `/api/nodes` | GET | List of discovered MAGI nodes |

### Authentication
✅ **Security implemented**: Web authentication with login/logout, API key protection, and session management.

**Default credentials are generated during installation and displayed upon completion.**

## Infrastructure Deployment

### Single Node Setup
```bash
# Install on single machine
python3 magi-installer.py
# Access via http://localhost:<assigned_port>
# Use credentials provided during installation
```

### Multi-Node Setup
```bash
# Install on each machine in network
for host in node1 node2 node3; do
    ssh $host "wget https://raw.githubusercontent.com/ismaelucky342/MAGI/main/magi-installer.py && python3 magi-installer.py"
done
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install psutil requests
EXPOSE 8080
CMD ["python3", "magi-node-v2.py", "docker-node"]
```

## Monitoring and Maintenance

### Log Monitoring
```bash
# Real-time logs
sudo journalctl -u magi-* -f

# Error analysis
sudo journalctl -u magi-* -p err
```

### Performance Tuning
- Adjust monitoring intervals in configuration
- Configure resource limits via systemd
- Optimize network discovery ranges

## Security Considerations

- **Network Isolation**: Deploy within trusted network segments
- **Firewall Rules**: Restrict access to monitoring ports
- **User Privileges**: Service runs with minimal required permissions
- **Log Security**: Ensure log files have appropriate permissions

## Troubleshooting

### Common Issues
- **Port conflicts**: Check if port 8080 is available
- **Permission errors**: Ensure service runs with appropriate privileges
- **Network discovery**: Verify firewall allows inter-node communication

### Debug Mode
```bash
python3 magi-node-v2.py <NODE_NAME> --debug
```

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
