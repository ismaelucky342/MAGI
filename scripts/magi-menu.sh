#!/bin/bash

# MAGI Interactive Menu System
# Centralizes all MAGI operations with a user-friendly interface

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="MAGI"
VERSION="1.0.0"

# Functions
print_header() {
    clear
    echo -e "${BLUE}"
    echo "  __  __          _____ _____ "
    echo " |  \/  |   /\   / ____|_   _|"
    echo " | \  / |  /  \ | |  __  | |  "
    echo " | |\/| | / /\ \| | |_ | | |  "
    echo " | |  | |/ ____ \ |__| |_| |_ "
    echo " |_|  |_/_/    \_\_____|_____|"
    echo -e "${NC}"
    echo -e "${WHITE}$PROJECT_NAME Monitoring System v$VERSION${NC}"
    echo -e "${CYAN}Distributed monitoring for Gaspar, Melchor & Baltasar${NC}"
    echo "================================================="
    echo ""
}

print_menu() {
    echo -e "${GREEN}Main Menu:${NC}"
    echo ""
    echo -e "${YELLOW}📦 Installation & Setup${NC}"
    echo "  1) 🔧 Initial Setup (first time)"
    echo "  2) 📋 Check Requirements"
    echo "  3) 🗂️  Configure Nodes"
    echo ""
    echo -e "${YELLOW}🚀 Development${NC}"
    echo "  4) 💻 Start Development Environment"
    echo "  5) 🎨 Frontend Only (UI Testing)"
    echo "  6) ⚙️  Backend Only (API Testing)"
    echo "  7) 🔨 Build Applications"
    echo ""
    echo -e "${YELLOW}🐳 Docker Operations${NC}"
    echo "  8) 🏗️  Build Docker Images"
    echo "  9) ▶️  Start with Docker"
    echo "  10) ⏹️  Stop Docker Services"
    echo ""
    echo -e "${YELLOW}🌍 Deployment${NC}"
    echo "  11) 🚀 Deploy to All Nodes"
    echo "  12) 📡 Deploy to Specific Node"
    echo "  13) 🔧 Setup Node Services"
    echo ""
    echo -e "${YELLOW}📊 Monitoring & Management${NC}"
    echo "  14) 📈 Check System Status"
    echo "  15) 📜 View Logs"
    echo "  16) 🧪 Run Tests"
    echo ""
    echo -e "${YELLOW}🛠️  Utilities${NC}"
    echo "  17) 🧹 Clean Environment"
    echo "  18) ℹ️  Project Information"
    echo "  19) 🔑 Generate SSH Keys"
    echo ""
    echo -e "${RED}  0) 🚪 Exit${NC}"
    echo ""
}

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

press_enter() {
    echo ""
    echo -e "${CYAN}Press Enter to continue...${NC}"
    read
}

# Menu handlers
handle_initial_setup() {
    log_info "Running initial setup..."
    ./scripts/setup.sh
    log_success "Initial setup completed!"
    press_enter
}

handle_check_requirements() {
    log_info "Checking system requirements..."
    
    echo -e "${YELLOW}Checking Docker...${NC}"
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✓ Docker found: $(docker --version)${NC}"
    else
        echo -e "${RED}✗ Docker not found${NC}"
    fi
    
    echo -e "${YELLOW}Checking Docker Compose...${NC}"
    if command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}✓ Docker Compose found: $(docker-compose --version)${NC}"
    else
        echo -e "${RED}✗ Docker Compose not found${NC}"
    fi
    
    echo -e "${YELLOW}Checking Node.js...${NC}"
    if command -v node &> /dev/null; then
        echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"
    else
        echo -e "${RED}✗ Node.js not found${NC}"
    fi
    
    echo -e "${YELLOW}Checking npm...${NC}"
    if command -v npm &> /dev/null; then
        echo -e "${GREEN}✓ npm found: $(npm --version)${NC}"
    else
        echo -e "${RED}✗ npm not found${NC}"
    fi
    
    echo -e "${YELLOW}Checking SSH...${NC}"
    if [ -f ~/.ssh/id_rsa ]; then
        echo -e "${GREEN}✓ SSH key found${NC}"
    else
        echo -e "${YELLOW}⚠ SSH key not found (will be generated if needed)${NC}"
    fi
    
    press_enter
}

handle_configure_nodes() {
    log_info "Opening node configuration..."
    
    if [ ! -f config/nodes.json ]; then
        log_warning "Configuration file not found. Creating from example..."
        cp config/nodes.example.json config/nodes.json
    fi
    
    echo -e "${YELLOW}Current configuration:${NC}"
    cat config/nodes.json | jq '.nodes[] | {id: .id, name: .name, ip: .ip}' 2>/dev/null || cat config/nodes.json
    
    echo ""
    echo -e "${CYAN}Edit configuration? (y/n):${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} config/nodes.json
        log_success "Configuration updated!"
    fi
    
    press_enter
}

handle_dev_environment() {
    log_info "Starting development environment..."
    log_warning "This will start both frontend and backend in development mode"
    echo -e "${CYAN}Frontend will be available at: http://localhost:3000${NC}"
    echo -e "${CYAN}Backend API will be available at: http://localhost:5000${NC}"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop the development environment${NC}"
    echo ""
    npm run dev
}

handle_frontend_only() {
    log_info "Starting frontend only for UI testing..."
    echo -e "${CYAN}Frontend will be available at: http://localhost:3000${NC}"
    echo -e "${YELLOW}Note: Backend API calls will fail without backend running${NC}"
    echo ""
    cd frontend && npm start
}

handle_backend_only() {
    log_info "Starting backend only for API testing..."
    echo -e "${CYAN}Backend API will be available at: http://localhost:5000${NC}"
    echo -e "${CYAN}Health check: http://localhost:5000/health${NC}"
    echo ""
    cd backend && npm run dev
}

handle_build() {
    log_info "Building applications..."
    npm run build
    log_success "Build completed!"
    press_enter
}

handle_docker_build() {
    log_info "Building Docker images..."
    npm run docker:build
    log_success "Docker images built successfully!"
    press_enter
}

handle_docker_start() {
    log_info "Starting MAGI with Docker..."
    npm run docker:up
    echo ""
    log_success "MAGI started successfully!"
    echo -e "${CYAN}Access the interface at: http://localhost:3000${NC}"
    echo -e "${CYAN}Default credentials: admin/admin${NC}"
    press_enter
}

handle_docker_stop() {
    log_info "Stopping Docker services..."
    npm run docker:down
    log_success "Docker services stopped!"
    press_enter
}

handle_deploy_all() {
    log_info "Deploying to all nodes..."
    ./scripts/deploy-all-nodes.sh all
    press_enter
}

handle_deploy_specific() {
    echo -e "${YELLOW}Available nodes:${NC}"
    echo "  1) gaspar   (192.168.1.100) - Multimedia Server"
    echo "  2) melchor  (192.168.1.101) - Backup & Storage"
    echo "  3) baltasar (192.168.1.102) - Home Automation"
    echo ""
    echo -e "${CYAN}Select node to deploy to (1-3):${NC}"
    read -r choice
    
    case $choice in
        1) node="gaspar" ;;
        2) node="melchor" ;;
        3) node="baltasar" ;;
        *) log_error "Invalid choice"; press_enter; return ;;
    esac
    
    log_info "Deploying to $node..."
    ./scripts/deploy-all-nodes.sh "$node"
    press_enter
}

handle_setup_services() {
    log_info "Setting up node services (Node Exporter, ttyd)..."
    echo -e "${YELLOW}This will install and configure services on all nodes${NC}"
    echo -e "${CYAN}Continue? (y/n):${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        ./scripts/setup-node-services.sh
    fi
    press_enter
}

handle_status() {
    log_info "Checking system status..."
    
    echo -e "${YELLOW}Docker containers:${NC}"
    docker-compose ps 2>/dev/null || echo "Docker Compose not running"
    
    echo ""
    echo -e "${YELLOW}Node connectivity:${NC}"
    ping -c 1 192.168.1.100 &> /dev/null && echo -e "${GREEN}✓ Gaspar (192.168.1.100) - Online${NC}" || echo -e "${RED}✗ Gaspar (192.168.1.100) - Offline${NC}"
    ping -c 1 192.168.1.101 &> /dev/null && echo -e "${GREEN}✓ Melchor (192.168.1.101) - Online${NC}" || echo -e "${RED}✗ Melchor (192.168.1.101) - Offline${NC}"
    ping -c 1 192.168.1.102 &> /dev/null && echo -e "${GREEN}✓ Baltasar (192.168.1.102) - Online${NC}" || echo -e "${RED}✗ Baltasar (192.168.1.102) - Offline${NC}"
    
    press_enter
}

handle_logs() {
    log_info "Showing logs..."
    echo -e "${YELLOW}Press Ctrl+C to stop viewing logs${NC}"
    echo ""
    docker-compose logs -f
}

handle_tests() {
    log_info "Running tests..."
    if [ -d "backend" ]; then
        echo -e "${YELLOW}Running backend tests...${NC}"
        cd backend && npm test && cd ..
    fi
    if [ -d "frontend" ]; then
        echo -e "${YELLOW}Running frontend tests...${NC}"
        cd frontend && npm test -- --coverage --watchAll=false && cd ..
    fi
    log_success "Tests completed!"
    press_enter
}

handle_clean() {
    log_warning "This will remove all build artifacts and Docker containers"
    echo -e "${CYAN}Continue? (y/n):${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        log_info "Cleaning environment..."
        make clean
        log_success "Environment cleaned!"
    fi
    press_enter
}

handle_info() {
    echo -e "${BLUE}MAGI Project Information${NC}"
    echo -e "${BLUE}========================${NC}"
    echo -e "${YELLOW}Project:${NC} MAGI Monitoring System"
    echo -e "${YELLOW}Version:${NC} $VERSION"
    echo -e "${YELLOW}Frontend:${NC} React + TypeScript"
    echo -e "${YELLOW}Backend:${NC} Node.js + Express"
    echo -e "${YELLOW}Database:${NC} Redis"
    echo -e "${YELLOW}Metrics:${NC} Node Exporter + Custom collectors"
    echo -e "${YELLOW}Terminal:${NC} ttyd (SSH over HTTP)"
    echo ""
    echo -e "${GREEN}Target Nodes:${NC}"
    echo -e "  ${CYAN}Gaspar${NC}   (192.168.1.100) - Multimedia Server"
    echo -e "  ${CYAN}Melchor${NC}  (192.168.1.101) - Backup & Storage"
    echo -e "  ${CYAN}Baltasar${NC} (192.168.1.102) - Home Automation"
    echo ""
    echo -e "${GREEN}Ports:${NC}"
    echo -e "  Frontend: 3000"
    echo -e "  Backend:  5000"
    echo -e "  Redis:    6379"
    echo -e "  Metrics:  9100 (Node Exporter)"
    echo -e "  Terminal: 7681-7683 (ttyd)"
    press_enter
}

handle_ssh_keys() {
    log_info "SSH Key Management..."
    
    if [ -f ~/.ssh/id_rsa ]; then
        echo -e "${GREEN}✓ SSH key already exists${NC}"
        echo -e "${YELLOW}Public key:${NC}"
        cat ~/.ssh/id_rsa.pub
        echo ""
        echo -e "${CYAN}Copy public key to nodes? (y/n):${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo "Run these commands to copy your key to each node:"
            echo "  ssh-copy-id admin@gaspar.local"
            echo "  ssh-copy-id admin@melchor.local"
            echo "  ssh-copy-id admin@baltasar.local"
        fi
    else
        echo -e "${YELLOW}⚠ No SSH key found${NC}"
        echo -e "${CYAN}Generate new SSH key? (y/n):${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
            log_success "SSH key generated!"
            echo -e "${YELLOW}Don't forget to copy your public key to your nodes!${NC}"
        fi
    fi
    
    press_enter
}

# Main menu loop
main() {
    while true; do
        print_header
        print_menu
        
        echo -e "${CYAN}Select an option (0-19):${NC}"
        read -r choice
        
        case $choice in
            1) handle_initial_setup ;;
            2) handle_check_requirements ;;
            3) handle_configure_nodes ;;
            4) handle_dev_environment ;;
            5) handle_frontend_only ;;
            6) handle_backend_only ;;
            7) handle_build ;;
            8) handle_docker_build ;;
            9) handle_docker_start ;;
            10) handle_docker_stop ;;
            11) handle_deploy_all ;;
            12) handle_deploy_specific ;;
            13) handle_setup_services ;;
            14) handle_status ;;
            15) handle_logs ;;
            16) handle_tests ;;
            17) handle_clean ;;
            18) handle_info ;;
            19) handle_ssh_keys ;;
            0) 
                echo -e "${GREEN}Thank you for using MAGI!${NC}"
                exit 0
                ;;
            *)
                log_error "Invalid option. Please select a number between 0-19."
                press_enter
                ;;
        esac
    done
}

# Check if running from correct directory
if [ ! -f "package.json" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    log_error "Please run this script from the MAGI project root directory"
    exit 1
fi

# Start main menu
main
