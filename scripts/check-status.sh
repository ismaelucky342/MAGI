#!/bin/bash

# MAGI Status Checker
# Comprehensive status check for all MAGI components

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
    echo -e "${BLUE}MAGI System Status Check${NC}"
    echo "========================"
    echo ""
}

check_local_environment() {
    echo -e "${YELLOW}Local Environment:${NC}"
    
    # Check if project files exist
    if [ -f "package.json" ]; then
        echo -e "${GREEN}✓ Project files found${NC}"
    else
        echo -e "${RED}✗ Project files not found${NC}"
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        echo -e "${GREEN}✓ Node.js: $(node --version)${NC}"
    else
        echo -e "${RED}✗ Node.js not found${NC}"
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        echo -e "${GREEN}✓ npm: $(npm --version)${NC}"
    else
        echo -e "${RED}✗ npm not found${NC}"
    fi
    
    # Check Docker
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✓ Docker: $(docker --version | cut -d' ' -f3 | sed 's/,//')${NC}"
        
        # Check if Docker is running
        if docker info &> /dev/null; then
            echo -e "${GREEN}✓ Docker daemon: Running${NC}"
        else
            echo -e "${RED}✗ Docker daemon: Not running${NC}"
        fi
    else
        echo -e "${RED}✗ Docker not found${NC}"
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}✓ Docker Compose: $(docker-compose --version | cut -d' ' -f3 | sed 's/,//')${NC}"
    else
        echo -e "${RED}✗ Docker Compose not found${NC}"
    fi
    
    echo ""
}

check_docker_services() {
    echo -e "${YELLOW}Docker Services:${NC}"
    
    if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
        local services=$(docker-compose ps --services 2>/dev/null)
        if [ -n "$services" ]; then
            while IFS= read -r service; do
                local status=$(docker-compose ps "$service" 2>/dev/null | tail -n +3 | awk '{print $4}')
                if [[ "$status" == "Up" ]]; then
                    echo -e "${GREEN}✓ $service: Running${NC}"
                else
                    echo -e "${RED}✗ $service: $status${NC}"
                fi
            done <<< "$services"
        else
            echo -e "${YELLOW}⚠ No Docker services running${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Docker Compose not available or docker-compose.yml not found${NC}"
    fi
    
    echo ""
}

check_local_ports() {
    echo -e "${YELLOW}Local Port Status:${NC}"
    
    # Check port 3000 (Frontend)
    if ss -tuln | grep -q ":3000 "; then
        echo -e "${GREEN}✓ Port 3000: Frontend running${NC}"
    else
        echo -e "${RED}✗ Port 3000: Frontend not running${NC}"
    fi
    
    # Check port 5000 (Backend)
    if ss -tuln | grep -q ":5000 "; then
        echo -e "${GREEN}✓ Port 5000: Backend running${NC}"
        
        # Test backend health
        if curl -s -m 5 "http://localhost:5000/health" &> /dev/null; then
            echo -e "${GREEN}  ✓ Backend health check: OK${NC}"
        else
            echo -e "${YELLOW}  ⚠ Backend health check: Failed${NC}"
        fi
    else
        echo -e "${RED}✗ Port 5000: Backend not running${NC}"
    fi
    
    # Check port 6379 (Redis)
    if ss -tuln | grep -q ":6379 "; then
        echo -e "${GREEN}✓ Port 6379: Redis running${NC}"
    else
        echo -e "${RED}✗ Port 6379: Redis not running${NC}"
    fi
    
    echo ""
}

check_remote_nodes() {
    echo -e "${YELLOW}Remote Nodes:${NC}"
    
    local nodes=("gaspar:192.168.1.100" "melchor:192.168.1.101" "baltasar:192.168.1.102")
    
    for node_info in "${nodes[@]}"; do
        local node_name=$(echo "$node_info" | cut -d':' -f1)
        local node_ip=$(echo "$node_info" | cut -d':' -f2)
        
        echo -e "${CYAN}$node_name ($node_ip):${NC}"
        
        # Check ping
        if ping -c 1 -W 2 "$node_ip" &> /dev/null; then
            echo -e "${GREEN}  ✓ Network: Reachable${NC}"
            
            # Check SSH
            if timeout 5 ssh -i ~/.ssh/id_rsa -o ConnectTimeout=3 -o StrictHostKeyChecking=no admin@"$node_ip" "echo 'SSH OK'" &> /dev/null; then
                echo -e "${GREEN}  ✓ SSH: Accessible${NC}"
                
                # Check MAGI frontend
                if curl -s -m 3 "http://$node_ip:3000" &> /dev/null; then
                    echo -e "${GREEN}  ✓ MAGI Frontend: Running${NC}"
                else
                    echo -e "${RED}  ✗ MAGI Frontend: Not running${NC}"
                fi
                
                # Check MAGI backend
                if curl -s -m 3 "http://$node_ip:5000/health" &> /dev/null; then
                    echo -e "${GREEN}  ✓ MAGI Backend: Running${NC}"
                else
                    echo -e "${RED}  ✗ MAGI Backend: Not running${NC}"
                fi
                
                # Check Node Exporter
                if curl -s -m 3 "http://$node_ip:9100/metrics" | head -1 &> /dev/null; then
                    echo -e "${GREEN}  ✓ Node Exporter: Running${NC}"
                else
                    echo -e "${YELLOW}  ⚠ Node Exporter: Not accessible${NC}"
                fi
                
                # Check ttyd (terminal)
                local ttyd_port
                case $node_name in
                    "gaspar") ttyd_port="7681" ;;
                    "melchor") ttyd_port="7682" ;;
                    "baltasar") ttyd_port="7683" ;;
                esac
                
                if curl -s -m 3 "http://$node_ip:$ttyd_port" &> /dev/null; then
                    echo -e "${GREEN}  ✓ Terminal (ttyd): Running on port $ttyd_port${NC}"
                else
                    echo -e "${YELLOW}  ⚠ Terminal (ttyd): Not accessible on port $ttyd_port${NC}"
                fi
                
            else
                echo -e "${RED}  ✗ SSH: Not accessible${NC}"
            fi
        else
            echo -e "${RED}  ✗ Network: Not reachable${NC}"
        fi
        echo ""
    done
}

check_configuration() {
    echo -e "${YELLOW}Configuration:${NC}"
    
    # Check config file
    if [ -f "config/nodes.json" ]; then
        echo -e "${GREEN}✓ Node configuration: Found${NC}"
        
        # Validate JSON
        if command -v jq &> /dev/null; then
            if jq empty config/nodes.json 2>/dev/null; then
                echo -e "${GREEN}  ✓ JSON syntax: Valid${NC}"
                
                local node_count=$(jq '.nodes | length' config/nodes.json 2>/dev/null)
                echo -e "${GREEN}  ✓ Configured nodes: $node_count${NC}"
            else
                echo -e "${RED}  ✗ JSON syntax: Invalid${NC}"
            fi
        else
            echo -e "${YELLOW}  ⚠ jq not available for JSON validation${NC}"
        fi
    else
        echo -e "${RED}✗ Node configuration: Not found${NC}"
    fi
    
    # Check environment files
    if [ -f "backend/.env" ]; then
        echo -e "${GREEN}✓ Backend environment: Configured${NC}"
    else
        echo -e "${YELLOW}⚠ Backend environment: Using defaults${NC}"
    fi
    
    if [ -f "frontend/.env" ]; then
        echo -e "${GREEN}✓ Frontend environment: Configured${NC}"
    else
        echo -e "${YELLOW}⚠ Frontend environment: Using defaults${NC}"
    fi
    
    # Check SSH keys
    if [ -f ~/.ssh/id_rsa ]; then
        echo -e "${GREEN}✓ SSH private key: Found${NC}"
    else
        echo -e "${RED}✗ SSH private key: Not found${NC}"
    fi
    
    if [ -f ~/.ssh/id_rsa.pub ]; then
        echo -e "${GREEN}✓ SSH public key: Found${NC}"
    else
        echo -e "${RED}✗ SSH public key: Not found${NC}"
    fi
    
    echo ""
}

show_summary() {
    echo -e "${BLUE}Summary:${NC}"
    echo "========"
    
    # Count services
    local total_checks=0
    local passed_checks=0
    
    # This is a simplified summary - in a real implementation,
    # you'd track all the individual check results
    
    echo -e "${GREEN}MAGI System Status Check Completed${NC}"
    echo ""
    echo -e "${CYAN}Quick Access URLs:${NC}"
    echo "  Local Frontend:  http://localhost:3000"
    echo "  Local Backend:   http://localhost:5000"
    echo "  Gaspar MAGI:     http://192.168.1.100:3000"
    echo "  Melchor MAGI:    http://192.168.1.101:3000"
    echo "  Baltasar MAGI:   http://192.168.1.102:3000"
    echo ""
    echo -e "${CYAN}Terminal Access:${NC}"
    echo "  Gaspar Terminal:  http://192.168.1.100:7681"
    echo "  Melchor Terminal: http://192.168.1.101:7682"
    echo "  Baltasar Terminal: http://192.168.1.102:7683"
    echo ""
    echo -e "${YELLOW}Default credentials: admin/admin${NC}"
}

main() {
    print_header
    check_local_environment
    check_docker_services
    check_local_ports
    check_remote_nodes
    check_configuration
    show_summary
}

# Run the status check
main
