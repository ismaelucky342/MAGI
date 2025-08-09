#!/bin/bash

# MAGI Setup Script
# Initializes the MAGI monitoring system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

create_env_files() {
    log_info "Creating environment files..."
    
    # Backend .env
    if [ ! -f "backend/.env" ]; then
        cp backend/.env.example backend/.env
        log_success "Created backend/.env"
        log_warning "Please review and update backend/.env with your settings"
    fi
    
    # Frontend .env
    if [ ! -f "frontend/.env" ]; then
        cat > frontend/.env << EOF
REACT_APP_API_URL=http://localhost:5000
REACT_APP_WS_URL=ws://localhost:5000
GENERATE_SOURCEMAP=false
EOF
        log_success "Created frontend/.env"
    fi
}

install_dependencies() {
    log_info "Installing dependencies..."
    
    # Root dependencies
    npm install
    
    # Backend dependencies
    cd backend
    npm install
    cd ..
    
    # Frontend dependencies
    cd frontend
    npm install
    cd ..
    
    log_success "Dependencies installed"
}

setup_configuration() {
    log_info "Setting up configuration..."
    
    if [ ! -f "config/nodes.json" ]; then
        cp config/nodes.example.json config/nodes.json
        log_success "Created config/nodes.json from example"
        log_warning "Please edit config/nodes.json with your actual node information"
    fi
}

generate_ssh_keys() {
    log_info "Checking SSH keys..."
    
    if [ ! -f ~/.ssh/id_rsa ]; then
        log_warning "No SSH key found. Generating new SSH key..."
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
        log_success "SSH key generated"
        log_info "Don't forget to copy your public key to your nodes:"
        log_info "ssh-copy-id admin@gaspar.local"
        log_info "ssh-copy-id admin@melchor.local"
        log_info "ssh-copy-id admin@baltasar.local"
    else
        log_success "SSH key found"
    fi
}

create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p data logs backend/logs frontend/build
    
    log_success "Directories created"
}

check_docker() {
    log_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first:"
        echo "curl -fsSL https://get.docker.com -o get-docker.sh"
        echo "sudo sh get-docker.sh"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first:"
        echo "sudo curl -L \"https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
        echo "sudo chmod +x /usr/local/bin/docker-compose"
        exit 1
    fi
    
    log_success "Docker and Docker Compose are installed"
}

setup_mDNS() {
    log_info "Setting up mDNS for local node discovery..."
    
    if command -v avahi-daemon &> /dev/null; then
        log_success "Avahi (mDNS) is already installed"
    else
        log_warning "Avahi (mDNS) is not installed. Installing..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y avahi-daemon avahi-utils
        elif command -v yum &> /dev/null; then
            sudo yum install -y avahi avahi-tools
        else
            log_warning "Could not install Avahi automatically. Please install manually."
            return
        fi
        
        sudo systemctl enable avahi-daemon
        sudo systemctl start avahi-daemon
        log_success "Avahi (mDNS) installed and started"
    fi
}

main() {
    echo -e "${BLUE}"
    echo "  __  __          _____ _____ "
    echo " |  \/  |   /\   / ____|_   _|"
    echo " | \  / |  /  \ | |  __  | |  "
    echo " | |\/| | / /\ \| | |_ | | |  "
    echo " | |  | |/ ____ \ |__| |_| |_ "
    echo " |_|  |_/_/    \_\_____|_____|"
    echo ""
    echo "MAGI Monitoring System Setup"
    echo "============================="
    echo -e "${NC}"
    
    log_info "Starting MAGI setup..."
    
    check_docker
    create_directories
    create_env_files
    setup_configuration
    install_dependencies
    generate_ssh_keys
    setup_mDNS
    
    log_success "MAGI setup completed!"
    echo ""
    log_info "Next steps:"
    echo "1. Edit config/nodes.json with your node information"
    echo "2. Update backend/.env with your settings"
    echo "3. Copy your SSH public key to all nodes"
    echo "4. Run 'npm run docker:up' to start the system"
    echo "5. Access the interface at http://localhost:3000"
    echo ""
    log_warning "Default login: admin/admin (change in production!)"
}

main "$@"
