#!/bin/bash

# MAGI Dependencies Manager
# Comprehensive dependency checking and installation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

print_header() {
    echo -e "${BLUE}"
    echo "🔧 MAGI Dependencies Manager"
    echo "============================"
    echo -e "${NC}"
}

# Global variables to track status
REQUIREMENTS_MET=true
DEPS_INSTALLED=false

check_system_info() {
    echo -e "${CYAN}System Information:${NC}"
    echo "  OS: $(uname -s) $(uname -r)"
    echo "  Architecture: $(uname -m)"
    
    if command -v lsb_release &> /dev/null; then
        echo "  Distribution: $(lsb_release -d | cut -f2)"
    elif [ -f /etc/os-release ]; then
        echo "  Distribution: $(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2)"
    fi
    
    if command -v free &> /dev/null; then
        echo "  Memory: $(free -h | awk '/^Mem:/{print $2}') total"
    fi
    
    echo "  Disk space: $(df -h . | tail -n 1 | awk '{print $4}') available"
    echo ""
}

check_node_js() {
    log_info "Checking Node.js..."
    
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found"
        echo "Node.js 18+ is required for MAGI development"
        REQUIREMENTS_MET=false
        return 1
    fi
    
    NODE_VERSION=$(node --version | sed 's/v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
    
    if [ "$NODE_MAJOR" -ge 18 ]; then
        log_success "Node.js v$NODE_VERSION ✓"
    else
        log_error "Node.js v$NODE_VERSION (requires v18+)"
        REQUIREMENTS_MET=false
        return 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm not found"
        REQUIREMENTS_MET=false
        return 1
    fi
    
    NPM_VERSION=$(npm --version)
    log_success "npm v$NPM_VERSION ✓"
    
    # Check if npx is available
    if command -v npx &> /dev/null; then
        log_success "npx available ✓"
    else
        log_warning "npx not available"
    fi
    
    return 0
}

check_docker() {
    log_info "Checking Docker..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found"
        REQUIREMENTS_MET=false
        return 1
    fi
    
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | sed 's/,//')
    log_success "Docker $DOCKER_VERSION ✓"
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon not running"
        echo "Start with: sudo systemctl start docker"
        REQUIREMENTS_MET=false
        return 1
    fi
    
    log_success "Docker daemon running ✓"
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | sed 's/,//')
        log_success "Docker Compose $COMPOSE_VERSION ✓"
    elif docker compose version &> /dev/null; then
        COMPOSE_VERSION=$(docker compose version --short)
        log_success "Docker Compose (plugin) $COMPOSE_VERSION ✓"
    else
        log_error "Docker Compose not found"
        REQUIREMENTS_MET=false
        return 1
    fi
    
    return 0
}

check_optional_tools() {
    log_info "Checking optional tools..."
    
    # Git
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        log_success "Git $GIT_VERSION ✓"
    else
        log_warning "Git not found (recommended for development)"
    fi
    
    # curl
    if command -v curl &> /dev/null; then
        log_success "curl available ✓"
    else
        log_warning "curl not found (needed for some operations)"
    fi
    
    # wget
    if command -v wget &> /dev/null; then
        log_success "wget available ✓"
    else
        log_warning "wget not found (alternative to curl)"
    fi
    
    # rsync
    if command -v rsync &> /dev/null; then
        log_success "rsync available ✓"
    else
        log_warning "rsync not found (needed for deployment)"
    fi
    
    # ssh
    if command -v ssh &> /dev/null; then
        log_success "SSH client available ✓"
    else
        log_error "SSH client not found (required for node access)"
        REQUIREMENTS_MET=false
    fi
    
    # jq (for JSON processing)
    if command -v jq &> /dev/null; then
        log_success "jq available ✓"
    else
        log_warning "jq not found (helpful for config validation)"
    fi
}

check_project_dependencies() {
    log_info "Checking project dependencies..."
    
    # Check if we're in the right directory
    if [ ! -f "package.json" ]; then
        log_error "package.json not found - are you in the MAGI project directory?"
        return 1
    fi
    
    log_success "Project directory confirmed ✓"
    
    # Check root dependencies
    if [ -d "node_modules" ]; then
        log_success "Root node_modules exists ✓"
        
        # Check if package-lock.json exists
        if [ -f "package-lock.json" ]; then
            log_success "package-lock.json exists ✓"
        else
            log_warning "package-lock.json missing (run npm install)"
        fi
    else
        log_warning "Root node_modules missing"
        DEPS_INSTALLED=false
    fi
    
    # Check backend dependencies
    if [ -d "backend" ]; then
        if [ -d "backend/node_modules" ]; then
            log_success "Backend node_modules exists ✓"
        else
            log_warning "Backend node_modules missing"
            DEPS_INSTALLED=false
        fi
    fi
    
    # Check frontend dependencies
    if [ -d "frontend" ]; then
        if [ -d "frontend/node_modules" ]; then
            log_success "Frontend node_modules exists ✓"
        else
            log_warning "Frontend node_modules missing"
            DEPS_INSTALLED=false
        fi
    fi
    
    return 0
}

install_missing_dependencies() {
    log_info "Installing missing dependencies..."
    
    # Install root dependencies
    if [ ! -d "node_modules" ]; then
        log_info "Installing root dependencies..."
        if npm install; then
            log_success "Root dependencies installed ✓"
        else
            log_error "Failed to install root dependencies"
            return 1
        fi
    fi
    
    # Install backend dependencies
    if [ -d "backend" ] && [ ! -d "backend/node_modules" ]; then
        log_info "Installing backend dependencies..."
        cd backend
        if npm install; then
            log_success "Backend dependencies installed ✓"
        else
            log_error "Failed to install backend dependencies"
            cd ..
            return 1
        fi
        cd ..
    fi
    
    # Install frontend dependencies
    if [ -d "frontend" ] && [ ! -d "frontend/node_modules" ]; then
        log_info "Installing frontend dependencies..."
        cd frontend
        if npm install; then
            log_success "Frontend dependencies installed ✓"
        else
            log_error "Failed to install frontend dependencies"
            cd ..
            return 1
        fi
        cd ..
    fi
    
    DEPS_INSTALLED=true
    return 0
}

check_package_vulnerabilities() {
    log_info "Checking for security vulnerabilities..."
    
    # Check root package
    if [ -f "package-lock.json" ]; then
        if npm audit --audit-level=moderate; then
            log_success "No critical vulnerabilities found ✓"
        else
            log_warning "Vulnerabilities found - run 'npm audit fix' to resolve"
        fi
    fi
    
    # Check backend
    if [ -f "backend/package-lock.json" ]; then
        cd backend
        if npm audit --audit-level=moderate; then
            log_success "Backend: No critical vulnerabilities ✓"
        else
            log_warning "Backend vulnerabilities found"
        fi
        cd ..
    fi
    
    # Check frontend
    if [ -f "frontend/package-lock.json" ]; then
        cd frontend
        if npm audit --audit-level=moderate; then
            log_success "Frontend: No critical vulnerabilities ✓"
        else
            log_warning "Frontend vulnerabilities found"
        fi
        cd ..
    fi
}

show_installation_guide() {
    echo -e "${YELLOW}Installation Guide:${NC}"
    echo "==================="
    echo ""
    
    if ! command -v node &> /dev/null; then
        echo -e "${CYAN}Node.js Installation:${NC}"
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
    fi
    
    if ! command -v docker &> /dev/null; then
        echo -e "${CYAN}Docker Installation:${NC}"
        echo "1. Using Docker's convenience script:"
        echo "   curl -fsSL https://get.docker.com -o get-docker.sh"
        echo "   sudo sh get-docker.sh"
        echo "   sudo usermod -aG docker \$USER"
        echo ""
        echo "2. Manual installation (Ubuntu/Debian):"
        echo "   sudo apt-get update"
        echo "   sudo apt-get install docker.io docker-compose"
        echo ""
    fi
    
    echo -e "${CYAN}After installation:${NC}"
    echo "1. Log out and log back in (for Docker group changes)"
    echo "2. Run this script again to verify installation"
    echo "3. Use 'make install' to complete MAGI setup"
}

update_dependencies() {
    log_info "Updating dependencies..."
    
    # Update root dependencies
    log_info "Updating root dependencies..."
    npm update
    
    # Update backend dependencies
    if [ -d "backend" ]; then
        log_info "Updating backend dependencies..."
        cd backend && npm update && cd ..
    fi
    
    # Update frontend dependencies
    if [ -d "frontend" ]; then
        log_info "Updating frontend dependencies..."
        cd frontend && npm update && cd ..
    fi
    
    log_success "Dependencies updated ✓"
}

clean_dependencies() {
    log_info "Cleaning dependencies..."
    
    # Clean root
    rm -rf node_modules package-lock.json
    
    # Clean backend
    if [ -d "backend" ]; then
        rm -rf backend/node_modules backend/package-lock.json
    fi
    
    # Clean frontend
    if [ -d "frontend" ]; then
        rm -rf frontend/node_modules frontend/package-lock.json
    fi
    
    log_success "Dependencies cleaned ✓"
}

show_menu() {
    echo -e "${GREEN}Dependencies Manager Menu:${NC}"
    echo ""
    echo "  1) 🔍 Check all requirements"
    echo "  2) 📦 Install missing dependencies"
    echo "  3) 🔄 Update dependencies"
    echo "  4) 🧹 Clean and reinstall"
    echo "  5) 🔒 Check security vulnerabilities"
    echo "  6) 📖 Show installation guide"
    echo "  7) ℹ️  Show system information"
    echo "  0) 🚪 Exit"
    echo ""
}

main() {
    print_header
    
    if [ "$#" -eq 0 ]; then
        # Interactive mode
        while true; do
            show_menu
            echo -e "${CYAN}Select an option (0-7):${NC}"
            read -r choice
            
            case $choice in
                1)
                    check_system_info
                    check_node_js
                    check_docker
                    check_optional_tools
                    check_project_dependencies
                    
                    echo ""
                    if [ "$REQUIREMENTS_MET" = true ]; then
                        log_success "All requirements met! ✓"
                        if [ "$DEPS_INSTALLED" = false ]; then
                            echo "Run option 2 to install missing dependencies"
                        fi
                    else
                        log_error "Some requirements not met"
                        echo "Run option 6 for installation guide"
                    fi
                    ;;
                2)
                    install_missing_dependencies
                    ;;
                3)
                    update_dependencies
                    ;;
                4)
                    echo -e "${YELLOW}This will remove all node_modules and reinstall${NC}"
                    echo -e "${CYAN}Continue? (y/n):${NC}"
                    read -r response
                    if [[ "$response" =~ ^[Yy]$ ]]; then
                        clean_dependencies
                        install_missing_dependencies
                    fi
                    ;;
                5)
                    check_package_vulnerabilities
                    ;;
                6)
                    show_installation_guide
                    ;;
                7)
                    check_system_info
                    ;;
                0)
                    exit 0
                    ;;
                *)
                    log_error "Invalid option"
                    ;;
            esac
            
            echo ""
            echo "Press Enter to continue..."
            read
            clear
            print_header
        done
    else
        # Command line mode
        case "$1" in
            "check")
                check_system_info
                check_node_js
                check_docker
                check_optional_tools
                check_project_dependencies
                ;;
            "install")
                install_missing_dependencies
                ;;
            "update")
                update_dependencies
                ;;
            "clean")
                clean_dependencies
                install_missing_dependencies
                ;;
            "audit")
                check_package_vulnerabilities
                ;;
            "guide")
                show_installation_guide
                ;;
            *)
                echo "Usage: $0 {check|install|update|clean|audit|guide}"
                echo "Or run without arguments for interactive mode"
                ;;
        esac
    fi
}

# Check if running from correct directory
if [ ! -f "package.json" ] && [ "$1" != "guide" ]; then
    log_error "Please run this script from the MAGI project root directory"
    exit 1
fi

main "$@"
