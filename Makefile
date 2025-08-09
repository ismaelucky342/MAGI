# MAGI Monitoring System - Makefile
# Centralizes installation, deployment, and management

.PHONY: help install setup build dev start stop clean deploy test frontend backend docker status logs menu first-time

# Colors for output
BLUE := \033[1;34m
GREEN := \033[1;32m
YELLOW := \033[1;33m
RED := \033[1;31m
NC := \033[0m

# Default target
.DEFAULT_GOAL := menu

## Display this help message
help:
	@echo -e "$(BLUE)MAGI Monitoring System$(NC)"
	@echo -e "$(BLUE)========================$(NC)"
	@echo ""
	@echo -e "$(YELLOW)📋 FLUJO RECOMENDADO PARA NUEVOS USUARIOS:$(NC)"
	@echo -e "$(GREEN)  make menu          # Menú interactivo (RECOMENDADO)$(NC)"
	@echo -e "$(GREEN)  make first-time    # Configuración completa automática$(NC)"
	@echo ""
	@echo -e "$(GREEN)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo -e "$(GREEN)Quick Start:$(NC)"
	@echo -e "  make menu        # Interactive management menu"
	@echo -e "  make first-time  # Complete setup (deps check + install + setup)"
	@echo -e "  make install     # Install dependencies only"
	@echo -e "  make dev         # Start development environment"
	@echo -e "  make deploy      # Deploy to production nodes"

## Install dependencies and setup environment
install: setup

## Interactive management menu (RECOMMENDED)
menu:
	@echo -e "$(GREEN)🧙‍♂️ Launching MAGI Interactive Menu...$(NC)"
	@./scripts/magi-menu.sh

## Complete first-time setup with dependency verification
first-time:
	@echo -e "$(YELLOW)🚀 Starting complete MAGI first-time setup...$(NC)"
	@echo -e "$(BLUE)Step 1: Checking dependencies and requirements...$(NC)"
	@./scripts/deps-manager.sh check || true
	@echo ""
	@echo -e "$(BLUE)Step 2: Running initial setup...$(NC)"
	@./scripts/setup.sh
	@echo ""
	@echo -e "$(GREEN)✅ First-time setup complete!$(NC)"
	@echo -e "$(YELLOW)Next: Run 'make dev' to start development or 'make menu' for more options$(NC)"
	@echo -e "$(GREEN)✓ Installation completed!$(NC)"

## Setup project (dependencies, config, directories)
setup:
	@echo -e "$(BLUE)Setting up MAGI...$(NC)"
	@./scripts/setup.sh

## Check system requirements and dependencies
check:
	@echo -e "$(BLUE)Checking requirements and dependencies...$(NC)"
	@./scripts/deps-manager.sh check

## Manage dependencies interactively
deps:
	@echo -e "$(BLUE)Opening dependencies manager...$(NC)"
	@./scripts/deps-manager.sh

## Install missing dependencies only
deps-install:
	@echo -e "$(BLUE)Installing missing dependencies...$(NC)"
	@./scripts/deps-manager.sh install

## Update all dependencies
deps-update:
	@echo -e "$(BLUE)Updating dependencies...$(NC)"
	@./scripts/deps-manager.sh update

## Clean and reinstall all dependencies
deps-clean:
	@echo -e "$(BLUE)Cleaning and reinstalling dependencies...$(NC)"
	@./scripts/deps-manager.sh clean

## Build all applications
build:
	@echo -e "$(BLUE)Building applications...$(NC)"
	@npm run build
	@echo -e "$(GREEN)✓ Build completed!$(NC)"

## Start development environment (frontend + backend)
dev:
	@echo -e "$(BLUE)Starting development environment...$(NC)"
	@echo -e "$(YELLOW)Frontend: http://localhost:3000$(NC)"
	@echo -e "$(YELLOW)Backend API: http://localhost:5000$(NC)"
	@npm run dev

## Start with Docker Compose
start:
	@echo -e "$(BLUE)Starting MAGI with Docker...$(NC)"
	@npm run docker:up
	@echo -e "$(GREEN)✓ MAGI started!$(NC)"
	@echo -e "$(YELLOW)Access: http://localhost:3000$(NC)"

## Stop Docker containers
stop:
	@echo -e "$(BLUE)Stopping MAGI...$(NC)"
	@npm run docker:down
	@echo -e "$(GREEN)✓ MAGI stopped!$(NC)"

## Start only frontend for UI testing
frontend:
	@echo -e "$(BLUE)Starting frontend only...$(NC)"
	@cd frontend && npm start

## Start only backend for API testing
backend:
	@echo -e "$(BLUE)Starting backend only...$(NC)"
	@cd backend && npm run dev

## Build Docker images
docker:
	@echo -e "$(BLUE)Building Docker images...$(NC)"
	@npm run docker:build
	@echo -e "$(GREEN)✓ Docker images built!$(NC)"

## Deploy to production nodes
deploy:
	@echo -e "$(BLUE)Deploying to production nodes...$(NC)"
	@./scripts/deploy-interactive.sh

## Deploy to specific node (usage: make deploy-node NODE=gaspar)
deploy-node:
	@echo -e "$(BLUE)Deploying to $(NODE)...$(NC)"
	@./scripts/deploy-all-nodes.sh $(NODE)

## Run tests
test:
	@echo -e "$(BLUE)Running tests...$(NC)"
	@cd backend && npm test
	@cd frontend && npm test
	@echo -e "$(GREEN)✓ Tests completed!$(NC)"

## Check system status
status:
	@echo -e "$(BLUE)Checking MAGI status...$(NC)"
	@./scripts/check-status.sh

## View logs
logs:
	@echo -e "$(BLUE)Showing MAGI logs...$(NC)"
	@docker-compose logs -f

## Clean build artifacts and containers
clean:
	@echo -e "$(BLUE)Cleaning up...$(NC)"
	@rm -rf frontend/build backend/dist node_modules/*/node_modules
	@docker-compose down -v --remove-orphans
	@docker system prune -f
	@echo -e "$(GREEN)✓ Cleanup completed!$(NC)"

## Show project info
info:
	@echo -e "$(BLUE)MAGI Project Information$(NC)"
	@echo -e "$(BLUE)========================$(NC)"
	@echo -e "Frontend: React + TypeScript"
	@echo -e "Backend:  Node.js + Express"
	@echo -e "Database: Redis"
	@echo -e "Metrics:  Node Exporter + Custom collectors"
	@echo -e "Terminal: ttyd (SSH over HTTP)"
	@echo -e ""
	@echo -e "$(GREEN)Nodes:$(NC)"
	@echo -e "  Gaspar   (192.168.1.100) - Multimedia Server"
	@echo -e "  Melchor  (192.168.1.101) - Backup & Storage"
	@echo -e "  Baltasar (192.168.1.102) - Home Automation"
