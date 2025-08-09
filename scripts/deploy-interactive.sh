#!/bin/bash

# MAGI Interactive Deployment Script
# Provides a user-friendly interface for deployment options

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
NODES=("gaspar" "melchor" "baltasar")
DEFAULT_USER="admin"
DEPLOY_PATH="/opt/magi"

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
    clear
    echo -e "${BLUE}🚀 MAGI Deployment Manager${NC}"
    echo "=============================="
    echo ""
}

show_deployment_menu() {
    echo -e "${GREEN}Deployment Options:${NC}"
    echo ""
    echo "  1) 🌍 Deploy to All Nodes"
    echo "  2) 📡 Deploy to Specific Node"
    echo "  3) 🔧 Setup Node Services Only"
    echo "  4) 🧪 Test Deployment (dry run)"
    echo "  5) 📊 Check Node Status"
    echo "  0) 🚪 Back to Main Menu"
    echo ""
}

check_prerequisites() {
    log_info "Checking deployment prerequisites..."
    
    # Check if config exists
    if [ ! -f "config/nodes.json" ]; then
        log_error "Configuration file not found!"
        echo "Please run 'make setup' first or create config/nodes.json"
        return 1
    fi
    
    # Check if SSH key exists
    if [ ! -f ~/.ssh/id_rsa ]; then
        log_warning "SSH key not found!"
        echo -e "${CYAN}Generate SSH key now? (y/n):${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
            log_success "SSH key generated!"
            echo "Don't forget to copy your public key to your nodes:"
            echo "  ssh-copy-id admin@gaspar.local"
            echo "  ssh-copy-id admin@melchor.local"
            echo "  ssh-copy-id admin@baltasar.local"
            echo ""
            echo "Press Enter when done..."
            read
        else
            return 1
        fi
    fi
    
    # Check Docker images
    if ! docker images | grep -q "magi"; then
        log_warning "MAGI Docker images not found!"
        echo -e "${CYAN}Build Docker images now? (y/n):${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            log_info "Building Docker images..."
            npm run docker:build
            log_success "Docker images built!"
        else
            return 1
        fi
    fi
    
    log_success "Prerequisites check passed!"
    return 0
}

deploy_all_nodes() {
    log_info "Deploying to all nodes..."
    
    echo -e "${YELLOW}This will deploy MAGI to:${NC}"
    echo "  • Gaspar (192.168.1.100) - Multimedia Server"
    echo "  • Melchor (192.168.1.101) - Backup & Storage"  
    echo "  • Baltasar (192.168.1.102) - Home Automation"
    echo ""
    echo -e "${CYAN}Continue with deployment? (y/n):${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        ./scripts/deploy-all-nodes.sh all
        log_success "Deployment to all nodes completed!"
    else
        log_info "Deployment cancelled"
    fi
}

deploy_specific_node() {
    echo -e "${YELLOW}Available nodes:${NC}"
    echo "  1) 🎬 Gaspar   (192.168.1.100) - Multimedia Server"
    echo "  2) 💾 Melchor  (192.168.1.101) - Backup & Storage"
    echo "  3) 🏠 Baltasar (192.168.1.102) - Home Automation"
    echo ""
    echo -e "${CYAN}Select node to deploy to (1-3):${NC}"
    read -r choice
    
    case $choice in
        1) 
            node="gaspar"
            ip="192.168.1.100"
            description="Multimedia Server"
            ;;
        2) 
            node="melchor"
            ip="192.168.1.101"
            description="Backup & Storage"
            ;;
        3) 
            node="baltasar"
            ip="192.168.1.102"
            description="Home Automation"
            ;;
        *) 
            log_error "Invalid choice"
            return
            ;;
    esac
    
    echo ""
    echo -e "${YELLOW}Deploying to:${NC} $node ($ip) - $description"
    echo -e "${CYAN}Continue? (y/n):${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        # Test connectivity first
        if ping -c 1 "$ip" &> /dev/null; then
            log_success "Node $node is reachable"
            ./scripts/deploy-all-nodes.sh "$node"
            log_success "Deployment to $node completed!"
            
            echo ""
            echo -e "${GREEN}Access MAGI on $node at: http://$ip:3000${NC}"
        else
            log_error "Node $node ($ip) is not reachable"
        fi
    else
        log_info "Deployment cancelled"
    fi
}

setup_services_only() {
    echo -e "${YELLOW}This will setup Node Exporter and ttyd on all nodes${NC}"
    echo -e "${CYAN}Continue? (y/n):${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        log_info "Setting up services on all nodes..."
        
        # Setup services on each node
        for node in "${NODES[@]}"; do
            case $node in
                "gaspar") ip="192.168.1.100"; port="7681" ;;
                "melchor") ip="192.168.1.101"; port="7682" ;;
                "baltasar") ip="192.168.1.102"; port="7683" ;;
            esac
            
            if ping -c 1 "$ip" &> /dev/null; then
                log_info "Setting up services on $node..."
                
                # Setup Node Exporter
                ssh -i ~/.ssh/id_rsa admin@"$ip" << 'EOF'
if ! command -v node_exporter &> /dev/null; then
    wget -q https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
    tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
    sudo mv node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
    rm -rf node_exporter-1.6.1.linux-amd64*
    
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
    echo "Node Exporter installed and started"
else
    echo "Node Exporter already installed"
fi
EOF
                
                # Setup ttyd
                ssh -i ~/.ssh/id_rsa admin@"$ip" << EOF
if ! command -v ttyd &> /dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y ttyd
    
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
    echo "ttyd installed and started on port $port"
else
    echo "ttyd already installed"
fi
EOF
                
                log_success "Services setup completed on $node"
            else
                log_error "Node $node ($ip) is not reachable"
            fi
        done
        
        log_success "Service setup completed on all reachable nodes!"
    fi
}

test_deployment() {
    log_info "Testing deployment (dry run)..."
    
    echo -e "${YELLOW}Checking node connectivity:${NC}"
    for node in "${NODES[@]}"; do
        case $node in
            "gaspar") ip="192.168.1.100" ;;
            "melchor") ip="192.168.1.101" ;;
            "baltasar") ip="192.168.1.102" ;;
        esac
        
        if ping -c 1 "$ip" &> /dev/null; then
            echo -e "${GREEN}✓ $node ($ip) - Online${NC}"
            
            # Test SSH
            if ssh -i ~/.ssh/id_rsa -o ConnectTimeout=5 admin@"$ip" "echo 'SSH OK'" &> /dev/null; then
                echo -e "${GREEN}  ✓ SSH access working${NC}"
            else
                echo -e "${RED}  ✗ SSH access failed${NC}"
            fi
            
            # Test Node Exporter
            if curl -s -m 5 "http://$ip:9100/metrics" &> /dev/null; then
                echo -e "${GREEN}  ✓ Node Exporter accessible${NC}"
            else
                echo -e "${YELLOW}  ⚠ Node Exporter not accessible${NC}"
            fi
        else
            echo -e "${RED}✗ $node ($ip) - Offline${NC}"
        fi
        echo ""
    done
}

check_node_status() {
    log_info "Checking node status..."
    
    for node in "${NODES[@]}"; do
        case $node in
            "gaspar") ip="192.168.1.100"; desc="Multimedia Server" ;;
            "melchor") ip="192.168.1.101"; desc="Backup & Storage" ;;
            "baltasar") ip="192.168.1.102"; desc="Home Automation" ;;
        esac
        
        echo -e "${BLUE}$node ($ip) - $desc${NC}"
        
        if ping -c 1 "$ip" &> /dev/null; then
            echo -e "${GREEN}  ✓ Network: Online${NC}"
            
            # Check if MAGI is running
            if curl -s -m 5 "http://$ip:3000" &> /dev/null; then
                echo -e "${GREEN}  ✓ MAGI Frontend: Running${NC}"
            else
                echo -e "${RED}  ✗ MAGI Frontend: Not running${NC}"
            fi
            
            if curl -s -m 5 "http://$ip:5000/health" &> /dev/null; then
                echo -e "${GREEN}  ✓ MAGI Backend: Running${NC}"
            else
                echo -e "${RED}  ✗ MAGI Backend: Not running${NC}"
            fi
            
            # Check services via SSH
            if ssh -i ~/.ssh/id_rsa -o ConnectTimeout=5 admin@"$ip" "systemctl is-active node_exporter" &> /dev/null; then
                echo -e "${GREEN}  ✓ Node Exporter: Active${NC}"
            else
                echo -e "${YELLOW}  ⚠ Node Exporter: Inactive${NC}"
            fi
        else
            echo -e "${RED}  ✗ Network: Offline${NC}"
        fi
        echo ""
    done
}

main() {
    while true; do
        print_header
        show_deployment_menu
        
        echo -e "${CYAN}Select an option (0-5):${NC}"
        read -r choice
        
        case $choice in
            1)
                if check_prerequisites; then
                    deploy_all_nodes
                fi
                echo ""
                echo "Press Enter to continue..."
                read
                ;;
            2)
                if check_prerequisites; then
                    deploy_specific_node
                fi
                echo ""
                echo "Press Enter to continue..."
                read
                ;;
            3)
                setup_services_only
                echo ""
                echo "Press Enter to continue..."
                read
                ;;
            4)
                test_deployment
                echo ""
                echo "Press Enter to continue..."
                read
                ;;
            5)
                check_node_status
                echo ""
                echo "Press Enter to continue..."
                read
                ;;
            0)
                exit 0
                ;;
            *)
                log_error "Invalid option. Please select a number between 0-5."
                echo "Press Enter to continue..."
                read
                ;;
        esac
    done
}

# Check if running from correct directory
if [ ! -f "package.json" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    log_error "Please run this script from the MAGI project root directory"
    exit 1
fi

main
