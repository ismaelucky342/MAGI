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
    log_info "Installing project dependencies..."
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        log_error "package.json not found! Are you in the correct directory?"
        return 1
    fi
    
    # Install root dependencies
    log_info "Installing root dependencies..."
    if npm install; then
        log_success "Root dependencies installed"
    else
        log_error "Failed to install root dependencies"
        return 1
    fi
    
    # Install backend dependencies
    if [ -d "backend" ]; then
        log_info "Installing backend dependencies..."
        cd backend
        if npm install; then
            log_success "Backend dependencies installed"
        else
            log_error "Failed to install backend dependencies"
            cd ..
            return 1
        fi
        cd ..
    fi
    
    # Install frontend dependencies
    if [ -d "frontend" ]; then
        log_info "Installing frontend dependencies..."
        cd frontend
        if npm install; then
            log_success "Frontend dependencies installed"
        else
            log_error "Failed to install frontend dependencies"
            cd ..
            return 1
        fi
        cd ..
    fi
    
    return 0
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

check_system_requirements() {
    log_info "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_success "Operating System: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_success "Operating System: macOS"
    else
        log_warning "Operating System: $OSTYPE (may not be fully supported)"
    fi
    
    # Check architecture
    ARCH=$(uname -m)
    if [[ "$ARCH" == "x86_64" || "$ARCH" == "amd64" ]]; then
        log_success "Architecture: $ARCH (supported)"
    elif [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
        log_success "Architecture: $ARCH (supported)"
    else
        log_warning "Architecture: $ARCH (may not be fully supported)"
    fi
    
    # Check available memory
    if command -v free &> /dev/null; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
        if [ "$MEMORY_GB" -ge 2 ]; then
            log_success "Memory: ${MEMORY_GB}GB (sufficient)"
        else
            log_warning "Memory: ${MEMORY_GB}GB (recommended: 2GB+)"
        fi
    fi
    
    # Check disk space
    DISK_SPACE=$(df -BG . | tail -n 1 | awk '{print $4}' | sed 's/G//')
    if [ "$DISK_SPACE" -ge 5 ]; then
        log_success "Disk space: ${DISK_SPACE}GB available (sufficient)"
    else
        log_warning "Disk space: ${DISK_SPACE}GB available (recommended: 5GB+)"
    fi
}

check_node_js() {
    log_info "Checking Node.js installation..."
    
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed!"
        echo ""
        echo "Install Node.js 18+ using one of these methods:"
        echo ""
        echo "1. Using Node Version Manager (recommended):"
        echo "   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
        echo "   source ~/.bashrc"
        echo "   nvm install 18"
        echo "   nvm use 18"
        echo ""
        echo "2. Using package manager:"
        if command -v apt-get &> /dev/null; then
            echo "   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
            echo "   sudo apt-get install -y nodejs"
        elif command -v yum &> /dev/null; then
            echo "   curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -"
            echo "   sudo yum install -y nodejs"
        elif command -v brew &> /dev/null; then
            echo "   brew install node@18"
        fi
        echo ""
        echo "3. Download from: https://nodejs.org/en/download/"
        echo ""
        log_warning "Please install Node.js and run this script again"
        return 1
    fi
    
    # Check Node.js version
    NODE_VERSION=$(node --version | sed 's/v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
    
    if [ "$NODE_MAJOR" -ge 18 ]; then
        log_success "Node.js: v$NODE_VERSION (compatible)"
    else
        log_error "Node.js: v$NODE_VERSION (requires v18+)"
        echo "Please upgrade Node.js to version 18 or higher"
        return 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed!"
        return 1
    fi
    
    NPM_VERSION=$(npm --version)
    log_success "npm: v$NPM_VERSION"
    
    return 0
}

check_docker() {
    log_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed!"
        echo ""
        echo "Install Docker using one of these methods:"
        echo ""
        echo "1. Using Docker's convenience script (recommended):"
        echo "   curl -fsSL https://get.docker.com -o get-docker.sh"
        echo "   sudo sh get-docker.sh"
        echo "   sudo usermod -aG docker \$USER"
        echo ""
        echo "2. Manual installation:"
        if command -v apt-get &> /dev/null; then
            echo "   sudo apt-get update"
            echo "   sudo apt-get install docker.io docker-compose"
        elif command -v yum &> /dev/null; then
            echo "   sudo yum install docker docker-compose"
        elif command -v brew &> /dev/null; then
            echo "   brew install docker docker-compose"
        fi
        echo ""
        echo "After installation, log out and log back in, then run this script again"
        return 1
    fi
    
    # Check Docker version
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | sed 's/,//')
    log_success "Docker: $DOCKER_VERSION"
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running!"
        echo "Start Docker with:"
        echo "  sudo systemctl start docker"
        echo "  sudo systemctl enable docker"
        return 1
    fi
    
    log_success "Docker daemon: Running"
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | sed 's/,//')
        log_success "Docker Compose: $COMPOSE_VERSION"
    elif docker compose version &> /dev/null; then
        COMPOSE_VERSION=$(docker compose version --short)
        log_success "Docker Compose (plugin): $COMPOSE_VERSION"
    else
        log_error "Docker Compose is not installed!"
        echo ""
        echo "Install Docker Compose:"
        echo "  sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
        echo "  sudo chmod +x /usr/local/bin/docker-compose"
        return 1
    fi
    
    return 0
}

install_dependencies() {
    log_info "Installing project dependencies..."
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        log_error "package.json not found! Are you in the correct directory?"
        return 1
    fi
    
    # Install root dependencies
    log_info "Installing root dependencies..."
    if npm install; then
        log_success "Root dependencies installed"
    else
        log_error "Failed to install root dependencies"
        return 1
    fi
    
    # Install backend dependencies
    if [ -d "backend" ]; then
        log_info "Installing backend dependencies..."
        cd backend
        if npm install; then
            log_success "Backend dependencies installed"
        else
            log_error "Failed to install backend dependencies"
            cd ..
            return 1
        fi
        cd ..
    fi
    
    # Install frontend dependencies
    if [ -d "frontend" ]; then
        log_info "Installing frontend dependencies..."
        cd frontend
        if npm install; then
            log_success "Frontend dependencies installed"
        else
            log_error "Failed to install frontend dependencies"
            cd ..
            return 1
        fi
        cd ..
    fi
    
    return 0
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
    
    # Check system requirements first
    if ! check_system_requirements; then
        log_error "System requirements check failed"
        exit 1
    fi
    
    # Check Node.js installation
    if ! check_node_js; then
        log_error "Node.js check failed"
        exit 1
    fi
    
    # Check Docker installation
    if ! check_docker; then
        log_error "Docker check failed"
        exit 1
    fi
    
    # Create necessary directories
    create_directories
    
    # Create environment files
    create_env_files
    
    # Setup configuration
    setup_configuration
    
    # Install dependencies
    if ! install_dependencies; then
        log_error "Dependencies installation failed"
        exit 1
    fi
    
    # Generate SSH keys if needed
    generate_ssh_keys
    
    # Setup mDNS
    setup_mDNS
    
    log_success "MAGI setup completed successfully!"
    echo ""
    log_info "Next steps:"
    echo "1. Edit config/nodes.json with your node information"
    echo "2. Update backend/.env with your settings"
    echo "3. Copy your SSH public key to all nodes:"
    echo "   ssh-copy-id admin@gaspar.local"
    echo "   ssh-copy-id admin@melchor.local"  
    echo "   ssh-copy-id admin@baltasar.local"
    echo "4. Run 'make dev' to start development or 'make start' for Docker"
    echo "5. Access the interface at http://localhost:3000"
    echo ""
    log_warning "Default login: admin/admin (change in production!)"
    echo ""
    log_info "Use 'make menu' for the interactive management interface"
}

main "$@"
