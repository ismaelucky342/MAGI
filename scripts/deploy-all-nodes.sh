#!/bin/bash

# MAGI Deployment Script
# Deploys MAGI monitoring system to all nodes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NODES=("gaspar" "melchor" "baltasar")
DEFAULT_USER="admin"
DEPLOY_PATH="/opt/magi"
SSH_KEY="~/.ssh/id_rsa"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking requirements..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if SSH key exists
    if [ ! -f "$SSH_KEY" ]; then
        log_warning "SSH key not found at $SSH_KEY"
        read -p "Enter path to SSH key: " SSH_KEY
        if [ ! -f "$SSH_KEY" ]; then
            log_error "SSH key not found at $SSH_KEY"
            exit 1
        fi
    fi
    
    log_success "Requirements check passed"
}

build_images() {
    log_info "Building Docker images..."
    docker-compose build
    log_success "Docker images built successfully"
}

deploy_to_node() {
    local node=$1
    local node_ip=$2
    local user=${3:-$DEFAULT_USER}
    
    log_info "Deploying to $node ($node_ip)..."
    
    # Check if node is reachable
    if ! ping -c 1 "$node_ip" &> /dev/null; then
        log_error "Node $node ($node_ip) is not reachable"
        return 1
    fi
    
    # Create deployment directory on remote node
    ssh -i "$SSH_KEY" "$user@$node_ip" "sudo mkdir -p $DEPLOY_PATH && sudo chown $user:$user $DEPLOY_PATH"
    
    # Copy project files
    rsync -avz --exclude='node_modules' --exclude='.git' --exclude='dist' \
          -e "ssh -i $SSH_KEY" \
          ./ "$user@$node_ip:$DEPLOY_PATH/"
    
    # Deploy on remote node
    ssh -i "$SSH_KEY" "$user@$node_ip" "cd $DEPLOY_PATH && docker-compose down && docker-compose up -d"
    
    log_success "Deployed to $node successfully"
}

setup_node_exporter() {
    local node=$1
    local node_ip=$2
    local user=${3:-$DEFAULT_USER}
    
    log_info "Setting up Node Exporter on $node..."
    
    ssh -i "$SSH_KEY" "$user@$node_ip" << 'EOF'
        # Install Node Exporter if not present
        if ! command -v node_exporter &> /dev/null; then
            wget -q https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
            tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
            sudo mv node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
            rm -rf node_exporter-1.6.1.linux-amd64*
            
            # Create systemd service
            sudo tee /etc/systemd/system/node_exporter.service > /dev/null << 'SERVICE'
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=nobody
Group=nobody
Type=simple
ExecStart=/usr/local/bin/node_exporter --web.listen-address=:9100

[Install]
WantedBy=multi-user.target
SERVICE

            sudo systemctl daemon-reload
            sudo systemctl enable node_exporter
            sudo systemctl start node_exporter
        fi
EOF
    
    log_success "Node Exporter setup completed on $node"
}

setup_ttyd() {
    local node=$1
    local node_ip=$2
    local user=${3:-$DEFAULT_USER}
    local port=$4
    
    log_info "Setting up ttyd on $node..."
    
    ssh -i "$SSH_KEY" "$user@$node_ip" << EOF
        # Install ttyd if not present
        if ! command -v ttyd &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y ttyd
            
            # Create systemd service
            sudo tee /etc/systemd/system/ttyd.service > /dev/null << 'SERVICE'
[Unit]
Description=ttyd
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/ttyd -p $port bash
Restart=on-failure

[Install]
WantedBy=multi-user.target
SERVICE

            sudo systemctl daemon-reload
            sudo systemctl enable ttyd
            sudo systemctl start ttyd
        fi
EOF
    
    log_success "ttyd setup completed on $node"
}

main() {
    log_info "Starting MAGI deployment..."
    
    # Check if config file exists
    if [ ! -f "config/nodes.json" ]; then
        log_info "Creating configuration from example..."
        cp config/nodes.example.json config/nodes.json
        log_warning "Please edit config/nodes.json with your node information before continuing"
        read -p "Press Enter when configuration is ready..."
    fi
    
    check_requirements
    build_images
    
    # Read node configuration and deploy
    # For now, we'll use hardcoded IPs - in a real scenario, parse from config/nodes.json
    
    case "$1" in
        "gaspar")
            deploy_to_node "gaspar" "192.168.1.100"
            setup_node_exporter "gaspar" "192.168.1.100"
            setup_ttyd "gaspar" "192.168.1.100" "$DEFAULT_USER" "7681"
            ;;
        "melchor")
            deploy_to_node "melchor" "192.168.1.101"
            setup_node_exporter "melchor" "192.168.1.101"
            setup_ttyd "melchor" "192.168.1.101" "$DEFAULT_USER" "7682"
            ;;
        "baltasar")
            deploy_to_node "baltasar" "192.168.1.102"
            setup_node_exporter "baltasar" "192.168.1.102"
            setup_ttyd "baltasar" "192.168.1.102" "$DEFAULT_USER" "7683"
            ;;
        "all")
            deploy_to_node "gaspar" "192.168.1.100"
            deploy_to_node "melchor" "192.168.1.101"
            deploy_to_node "baltasar" "192.168.1.102"
            
            setup_node_exporter "gaspar" "192.168.1.100"
            setup_node_exporter "melchor" "192.168.1.101"
            setup_node_exporter "baltasar" "192.168.1.102"
            
            setup_ttyd "gaspar" "192.168.1.100" "$DEFAULT_USER" "7681"
            setup_ttyd "melchor" "192.168.1.101" "$DEFAULT_USER" "7682"
            setup_ttyd "baltasar" "192.168.1.102" "$DEFAULT_USER" "7683"
            ;;
        *)
            echo "Usage: $0 {gaspar|melchor|baltasar|all}"
            exit 1
            ;;
    esac
    
    log_success "MAGI deployment completed!"
    log_info "Access the interface at http://NODE_IP:3000"
    log_info "Default credentials: admin/admin (change in production!)"
}

# Run main function with all arguments
main "$@"
