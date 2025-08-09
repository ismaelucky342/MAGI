#!/bin/bash

# MAGI Interactive Menu System
# Provides centralized management for the MAGI monitoring system

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Utility functions
press_enter() {
    echo ""
    echo -e "${YELLOW}Presiona Enter para continuar...${NC}"
    read -r
}

print_header() {
    clear
    echo -e "${PURPLE}╔═══════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                             MAGI Control Center                           ║${NC}"
    echo -e "${PURPLE}║                     ${CYAN}Distributed Node Monitoring System${NC}                    ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚═══════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo ""
}

print_menu() {
    echo -e "${YELLOW}🔧 VERIFICACIÓN Y DEPENDENCIAS${NC}"
    echo "  1) ✅ Verificar requisitos del sistema"
    echo "  2) 📋 Gestionar dependencias (npm, vulnerabilidades...)"
    echo "  3) 🔍 Diagnóstico completo del sistema"
    echo ""
    echo -e "${YELLOW}⚙️  CONFIGURACIÓN E INSTALACIÓN${NC}"
    echo "  4) 🚀 Configuración inicial del sistema"
    echo "  5) 📦 Instalar dependencias del proyecto"
    echo "  6) 🔑 Configurar claves SSH"
    echo ""
    echo -e "${YELLOW}💻 DESARROLLO${NC}"
    echo "  7) 🔄 Modo desarrollo (frontend + backend)"
    echo "  8) 🎯 Solo frontend (pruebas UI)"
    echo "  9) ⚙️  Solo backend (pruebas API)"
    echo "  10) 🔨 Construir aplicaciones"
    echo ""
    echo -e "${YELLOW}🐳 OPERACIONES DOCKER${NC}"
    echo "  11) 🏗️  Construir imágenes Docker"
    echo "  12) ▶️  Iniciar con Docker"
    echo "  13) ⏹️  Detener servicios Docker"
    echo ""
    echo -e "${YELLOW}🌍 DESPLIEGUE${NC}"
    echo "  14) 🚀 Desplegar en todos los nodos"
    echo "  15) 📡 Desplegar en nodo específico"
    echo "  16) 🔧 Configurar servicios de nodo"
    echo ""
    echo -e "${YELLOW}📊 MONITORIZACIÓN Y GESTIÓN${NC}"
    echo "  17) 📈 Verificar estado del sistema"
    echo "  18) 📜 Ver logs del sistema"
    echo "  19) 🧪 Ejecutar pruebas"
    echo ""
    echo -e "${YELLOW}🛠️  UTILIDADES${NC}"
    echo "  20) 🧹 Limpiar entorno"
    echo "  21) ℹ️  Información del proyecto"
    echo "  22) 🔑 Generar/gestionar claves SSH"
    echo ""
    echo -e "${RED}  0) 🚪 Salir${NC}"
    echo ""
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[ÉXITO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_title() {
    echo -e "${PURPLE}${BOLD}$1${NC}"
}

# Menu handlers - ORDEN CORREGIDO SEGÚN PRIORIDAD

# 1. VERIFICACIÓN Y DEPENDENCIAS (LO MÁS IMPORTANTE PRIMERO)
handle_check_requirements() {
    log_info "Verificando requisitos del sistema y dependencias..."
    echo ""
    
    # Verificar Node.js
    echo -e "${YELLOW}1. Verificando Node.js...${NC}"
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        echo -e "${GREEN}✓ Node.js encontrado: $NODE_VERSION${NC}"
    else
        echo -e "${RED}✗ Node.js no está instalado${NC}"
        echo -e "${YELLOW}  Instala desde: https://nodejs.org${NC}"
    fi
    
    # Verificar npm
    echo -e "${YELLOW}2. Verificando npm...${NC}"
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        echo -e "${GREEN}✓ npm encontrado: v$NPM_VERSION${NC}"
    else
        echo -e "${RED}✗ npm no está instalado${NC}"
        echo -e "${YELLOW}  Se instala automáticamente con Node.js${NC}"
    fi
    
    # Verificar Docker
    echo -e "${YELLOW}3. Verificando Docker...${NC}"
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | sed 's/,//')
        echo -e "${GREEN}✓ Docker encontrado: $DOCKER_VERSION${NC}"
        
        if docker info &> /dev/null; then
            echo -e "${GREEN}✓ Docker daemon está ejecutándose${NC}"
        else
            echo -e "${RED}✗ Docker daemon no está ejecutándose${NC}"
            echo -e "${YELLOW}  Ejecuta: sudo systemctl start docker${NC}"
        fi
    else
        echo -e "${RED}✗ Docker no está instalado${NC}"
        echo -e "${YELLOW}  Instala desde: https://docs.docker.com/get-docker/${NC}"
    fi
    
    # Verificar docker-compose
    echo -e "${YELLOW}4. Verificando Docker Compose...${NC}"
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | sed 's/,//')
        echo -e "${GREEN}✓ Docker Compose encontrado: $COMPOSE_VERSION${NC}"
    elif docker compose version &> /dev/null; then
        COMPOSE_VERSION=$(docker compose version --short)
        echo -e "${GREEN}✓ Docker Compose (plugin) encontrado: $COMPOSE_VERSION${NC}"
    else
        echo -e "${RED}✗ Docker Compose no está instalado${NC}"
    fi
    
    # Usar el deps-manager.sh para verificación adicional
    echo ""
    echo -e "${YELLOW}5. Ejecutando verificación avanzada...${NC}"
    ./scripts/deps-manager.sh check
    
    press_enter
}

handle_manage_dependencies() {
    log_info "Abriendo gestor de dependencias..."
    echo -e "${CYAN}Esto te permitirá verificar, actualizar y resolver problemas de dependencias${NC}"
    echo -e "${YELLOW}Recomendado: Ejecutar ANTES de instalar o desarrollar${NC}"
    echo ""
    ./scripts/deps-manager.sh
}

handle_system_diagnostic() {
    log_info "Ejecutando diagnóstico completo del sistema..."
    echo -e "${CYAN}Verificando todos los componentes del sistema...${NC}"
    echo ""
    
    echo -e "${YELLOW}1. Verificando Node.js y npm...${NC}"
    ./scripts/deps-manager.sh check
    echo ""
    
    echo -e "${YELLOW}2. Verificando Docker...${NC}"
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✓ Docker encontrado: $(docker --version)${NC}"
        if docker info &> /dev/null; then
            echo -e "${GREEN}✓ Docker daemon funcionando${NC}"
        else
            echo -e "${RED}✗ Docker daemon no está ejecutándose${NC}"
        fi
    else
        echo -e "${RED}✗ Docker no encontrado${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}3. Verificando estructura del proyecto...${NC}"
    for dir in frontend backend config scripts; do
        if [ -d "$dir" ]; then
            echo -e "${GREEN}✓ Directorio $dir existe${NC}"
        else
            echo -e "${RED}✗ Directorio $dir no encontrado${NC}"
        fi
    done
    
    echo ""
    echo -e "${YELLOW}4. Verificando archivos de configuración...${NC}"
    for file in package.json frontend/package.json backend/package.json; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✓ $file existe${NC}"
        else
            echo -e "${RED}✗ $file no encontrado${NC}"
        fi
    done
    
    press_enter
}

# 2. CONFIGURACIÓN E INSTALACIÓN
handle_initial_setup() {
    log_info "Ejecutando configuración inicial del sistema..."
    echo -e "${YELLOW}Esto verificará requisitos, instalará dependencias y configurará el entorno${NC}"
    echo ""
    echo -e "${CYAN}Pasos que se ejecutarán:${NC}"
    echo "  1. Verificar requisitos del sistema (Node.js, Docker, etc.)"
    echo "  2. Instalar dependencias npm"
    echo "  3. Crear archivos de configuración"
    echo "  4. Configurar claves SSH"
    echo "  5. Crear directorios necesarios"
    echo ""
    echo -e "${CYAN}¿Continuar con la configuración inicial? (y/N)${NC}"
    read -r confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        log_info "Iniciando configuración..."
        
        # Verificar que el script existe
        if [ ! -f "scripts/setup.sh" ]; then
            log_error "Script setup.sh no encontrado!"
            press_enter
            return 1
        fi
        
        # Hacer el script ejecutable
        chmod +x scripts/setup.sh
        
        # Ejecutar setup
        echo -e "${YELLOW}Ejecutando setup.sh...${NC}"
        if ./scripts/setup.sh; then
            log_success "¡Configuración inicial completada exitosamente!"
            echo ""
            echo -e "${GREEN}Próximos pasos recomendados:${NC}"
            echo "  • Revisar config/nodes.json con la información de tus nodos"
            echo "  • Ejecutar 'Verificar estado del sistema' para confirmar todo"
            echo "  • Probar modo desarrollo con 'Modo desarrollo'"
        else
            log_error "Error durante la configuración. Revisa los mensajes arriba."
            echo ""
            echo -e "${YELLOW}Posibles soluciones:${NC}"
            echo "  • Verifica que Node.js esté instalado (versión 18+)"
            echo "  • Verifica que Docker esté instalado y ejecutándose"
            echo "  • Ejecuta 'Gestionar dependencias' para resolver problemas específicos"
        fi
    else
        log_info "Configuración cancelada"
    fi
    press_enter
}

handle_install_deps() {
    log_info "Instalando dependencias del proyecto..."
    echo -e "${YELLOW}Esto puede tardar unos minutos...${NC}"
    echo ""
    
    # Verificar que estamos en el directorio correcto
    if [ ! -f "package.json" ]; then
        log_error "No se encontró package.json. ¿Estás en el directorio correcto?"
        press_enter
        return 1
    fi
    
    # Verificar que npm está instalado
    if ! command -v npm &> /dev/null; then
        log_error "npm no está instalado en el sistema!"
        echo ""
        echo -e "${YELLOW}Para instalar npm:${NC}"
        echo ""
        if command -v apt-get &> /dev/null; then
            echo "  sudo apt update && sudo apt install nodejs npm"
        elif command -v yum &> /dev/null; then
            echo "  sudo yum install nodejs npm"
        elif command -v pacman &> /dev/null; then
            echo "  sudo pacman -S nodejs npm"
        elif command -v brew &> /dev/null; then
            echo "  brew install node"
        else
            echo "  Instala Node.js desde: https://nodejs.org"
        fi
        echo ""
        echo -e "${CYAN}¿Quieres que intente instalar npm automáticamente? (y/N)${NC}"
        read -r install_npm
        
        if [[ "$install_npm" =~ ^[Yy]$ ]]; then
            log_info "Intentando instalar npm..."
            if command -v apt-get &> /dev/null; then
                sudo apt update && sudo apt install -y nodejs npm
            elif command -v yum &> /dev/null; then
                sudo yum install -y nodejs npm
            elif command -v pacman &> /dev/null; then
                sudo pacman -S --noconfirm nodejs npm
            else
                log_error "No se pudo detectar el gestor de paquetes. Instala manualmente."
                press_enter
                return 1
            fi
            
            if command -v npm &> /dev/null; then
                log_success "npm instalado correctamente!"
            else
                log_error "Error instalando npm"
                press_enter
                return 1
            fi
        else
            log_info "Instalación cancelada. Instala npm y vuelve a intentar."
            press_enter
            return 1
        fi
    fi
    
    echo -e "${CYAN}Opciones de instalación:${NC}"
    echo "  1) 🚀 Instalación completa (setup.sh)"
    echo "  2) 📦 Solo dependencias npm"
    echo "  3) 🔄 Reinstalación limpia"
    echo "  0) ↩️  Volver"
    echo ""
    echo -e "${CYAN}Selecciona una opción (0-3):${NC}"
    read -r choice
    
    case $choice in
        1)
            log_info "Ejecutando configuración completa..."
            if ./scripts/setup.sh; then
                log_success "Configuración completa exitosa!"
            else
                log_error "Error durante la configuración. Revisa los errores arriba."
            fi
            ;;
        2)
            log_info "Instalando solo dependencias npm..."
            
            # Instalar dependencias root
            echo -e "${YELLOW}Instalando dependencias root...${NC}"
            if npm install; then
                log_success "Dependencias root instaladas"
            else
                log_error "Error instalando dependencias root"
                press_enter
                return 1
            fi
            
            # Instalar dependencias backend
            if [ -d "backend" ]; then
                echo -e "${YELLOW}Instalando dependencias backend...${NC}"
                if (cd backend && npm install); then
                    log_success "Dependencias backend instaladas"
                else
                    log_error "Error instalando dependencias backend"
                fi
            fi
            
            # Instalar dependencias frontend
            if [ -d "frontend" ]; then
                echo -e "${YELLOW}Instalando dependencias frontend...${NC}"
                if (cd frontend && npm install); then
                    log_success "Dependencias frontend instaladas"
                else
                    log_error "Error instalando dependencias frontend"
                fi
            fi
            
            log_success "Instalación de dependencias completada!"
            ;;
        3)
            log_info "Realizando reinstalación limpia..."
            echo -e "${RED}Esto eliminará node_modules y reinstalará todo${NC}"
            echo -e "${CYAN}¿Continuar? (y/N):${NC}"
            read -r confirm
            
            if [[ "$confirm" =~ ^[Yy]$ ]]; then
                # Limpiar node_modules
                echo -e "${YELLOW}Limpiando node_modules...${NC}"
                rm -rf node_modules backend/node_modules frontend/node_modules
                rm -f package-lock.json backend/package-lock.json frontend/package-lock.json
                
                # Reinstalar
                echo -e "${YELLOW}Reinstalando dependencias...${NC}"
                if npm install && (cd backend && npm install) && (cd frontend && npm install); then
                    log_success "Reinstalación limpia completada!"
                else
                    log_error "Error durante la reinstalación"
                fi
            else
                log_info "Reinstalación cancelada"
            fi
            ;;
        0)
            return 0
            ;;
        *)
            log_error "Opción inválida"
            ;;
    esac
    
    press_enter
}

handle_configure_nodes() {
    log_info "Configurando acceso SSH a nodos..."
    ./scripts/setup-ssh.sh 2>/dev/null || {
        log_warning "Script setup-ssh.sh no encontrado. Configurando SSH manualmente..."
        if [ ! -f ~/.ssh/id_rsa ]; then
            echo -e "${YELLOW}Generando clave SSH...${NC}"
            ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
        fi
        echo -e "${CYAN}Copia tu clave pública a los nodos:${NC}"
        echo "ssh-copy-id admin@gaspar.local"
        echo "ssh-copy-id admin@melchor.local"
        echo "ssh-copy-id admin@baltasar.local"
    }
    press_enter
}

# 3. DESARROLLO
handle_development() {
    log_info "Iniciando modo desarrollo completo..."
    echo -e "${CYAN}Esto iniciará frontend (puerto 3000) y backend (puerto 3001)${NC}"
    echo -e "${YELLOW}Asegúrate de que las dependencias estén instaladas primero${NC}"
    make dev
    press_enter
}

handle_frontend_only() {
    log_info "Iniciando solo frontend para pruebas de UI..."
    echo -e "${CYAN}Frontend estará disponible en: http://localhost:3000${NC}"
    echo -e "${YELLOW}Nota: Las llamadas a la API fallarán sin el backend ejecutándose${NC}"
    echo ""
    cd frontend && npm start
}

handle_backend_only() {
    log_info "Iniciando solo servidor API backend..."
    echo -e "${CYAN}Backend API estará disponible en: http://localhost:3001${NC}"
    echo -e "${YELLOW}Úsalo para pruebas de API con herramientas como Postman${NC}"
    echo ""
    cd backend && npm run dev
}

handle_build() {
    log_info "Construyendo todas las aplicaciones..."
    make build
    press_enter
}

# 4. DOCKER
handle_docker_build() {
    log_info "Construyendo imágenes Docker..."
    make docker-build
    press_enter
}

handle_docker_start() {
    log_info "Iniciando servicios con Docker..."
    echo -e "${CYAN}Los servicios estarán disponibles en:${NC}"
    echo -e "${GREEN}  Frontend: http://localhost:3000${NC}"
    echo -e "${GREEN}  Backend:  http://localhost:3001${NC}"
    echo -e "${GREEN}  Redis:    localhost:6379${NC}"
    echo ""
    make docker-up
    press_enter
}

handle_docker_stop() {
    log_info "Deteniendo servicios Docker..."
    make docker-down
    press_enter
}

# 5. DESPLIEGUE
handle_deploy_all() {
    log_info "Desplegando en todos los nodos..."
    echo -e "${YELLOW}Esto desplegará MAGI en los tres nodos${NC}"
    echo -e "${CYAN}¿Continuar? (y/N)${NC}"
    read -r confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        ./scripts/deploy-all-nodes.sh
    else
        log_info "Despliegue cancelado"
    fi
    press_enter
}

handle_deploy_specific() {
    log_info "Seleccionar destino de despliegue:"
    echo ""
    echo "  1) gaspar   (192.168.1.100) - Multimedia"
    echo "  2) melchor  (192.168.1.101) - Backup & Storage"
    echo "  3) baltasar (192.168.1.102) - Domótica"
    echo ""
    echo -e "${CYAN}Selecciona nodo para desplegar (1-3):${NC}"
    read -r choice
    
    case $choice in
        1) node="gaspar" ;;
        2) node="melchor" ;;
        3) node="baltasar" ;;
        *) log_error "Opción inválida"; press_enter; return ;;
    esac
    
    log_info "Desplegando en $node..."
    ./scripts/deploy-all-nodes.sh "$node"
    press_enter
}

handle_setup_services() {
    log_info "Configurando servicios de nodo..."
    echo -e "${YELLOW}Esto instalará agentes de monitorización en todos los nodos${NC}"
    ./scripts/setup-node-services.sh 2>/dev/null || {
        log_warning "Script setup-node-services.sh no encontrado"
        log_info "Configura manualmente los servicios en cada nodo"
    }
    press_enter
}

# 6. MONITORIZACIÓN
handle_status() {
    log_info "Verificando estado del sistema..."
    ./scripts/check-status.sh 2>/dev/null || {
        log_info "Verificando estado manualmente..."
        echo ""
        echo -e "${YELLOW}Servicios locales:${NC}"
        if pgrep -f "npm.*start\|node.*server" > /dev/null; then
            echo -e "${GREEN}✓ Aplicación ejecutándose${NC}"
        else
            echo -e "${RED}✗ Aplicación no ejecutándose${NC}"
        fi
        
        if docker ps | grep -q magi; then
            echo -e "${GREEN}✓ Contenedores Docker ejecutándose${NC}"
        else
            echo -e "${YELLOW}⚠ Sin contenedores Docker activos${NC}"
        fi
    }
    press_enter
}

handle_logs() {
    log_info "Viendo logs del sistema..."
    echo -e "${CYAN}Selecciona fuente de logs:${NC}"
    echo "  1) Logs de Docker"
    echo "  2) Logs de aplicación"
    echo "  3) Logs del sistema"
    echo ""
    read -r choice
    
    case $choice in
        1) docker-compose logs -f ;;
        2) tail -f logs/*.log 2>/dev/null || echo "No se encontraron logs de aplicación" ;;
        3) journalctl -f -u magi* 2>/dev/null || echo "No se encontraron logs del sistema" ;;
        *) log_error "Opción inválida" ;;
    esac
    press_enter
}

handle_tests() {
    log_info "Ejecutando pruebas..."
    make test
    press_enter
}

# 7. UTILIDADES
handle_clean() {
    log_info "Limpiando entorno..."
    echo -e "${YELLOW}Esto eliminará archivos temporales y contenedores${NC}"
    echo -e "${CYAN}¿Continuar? (y/N)${NC}"
    read -r confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        make clean
    else
        log_info "Limpieza cancelada"
    fi
    press_enter
}

handle_info() {
    log_info "Información del Proyecto"
    echo ""
    echo -e "${CYAN}MAGI - Magical Automation & General Intelligence${NC}"
    echo -e "${YELLOW}Versión:${NC} 1.0.0"
    echo -e "${YELLOW}Descripción:${NC} Sistema de monitorización distribuida para nodos de home lab"
    echo ""
    echo -e "${CYAN}Componentes:${NC}"
    echo "  • React + TypeScript Frontend"
    echo "  • Node.js + Express Backend"
    echo "  • Redis Cache"
    echo "  • Docker Deployment"
    echo "  • SSH Terminal Access"
    echo "  • Métricas en tiempo real"
    echo ""
    echo -e "${CYAN}Nodos:${NC}"
    echo "  • Gaspar (Centro Multimedia)"
    echo "  • Melchor (Backup & Storage)"
    echo "  • Baltasar (Domótica)"
    echo ""
    echo -e "${CYAN}Flujo recomendado:${NC}"
    echo "  1. Verificar requisitos (opción 1)"
    echo "  2. Gestionar dependencias (opción 2)"
    echo "  3. Configuración inicial (opción 4)"
    echo "  4. Instalar dependencias (opción 5)"
    echo "  5. Modo desarrollo (opción 7)"
    press_enter
}

handle_ssh_keys() {
    log_info "Gestionando claves SSH..."
    if [ ! -f ~/.ssh/id_rsa ]; then
        echo -e "${YELLOW}No se encontró clave SSH. Generando nueva clave...${NC}"
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
        log_success "Clave SSH generada"
    else
        log_success "Clave SSH ya existe"
    fi
    
    echo ""
    echo -e "${CYAN}Clave Pública SSH:${NC}"
    cat ~/.ssh/id_rsa.pub
    echo ""
    echo -e "${YELLOW}Copia esta clave a ~/.ssh/authorized_keys de tus nodos${NC}"
    echo ""
    echo -e "${CYAN}Comandos para copiar:${NC}"
    echo "ssh-copy-id admin@gaspar.local"
    echo "ssh-copy-id admin@melchor.local"
    echo "ssh-copy-id admin@baltasar.local"
    press_enter
}

# Main menu loop
main() {
    while true; do
        print_header
        print_menu
        
        echo -e "${CYAN}Selecciona una opción (0-22):${NC}"
        read -r choice
        
        case $choice in
            1) handle_check_requirements ;;
            2) handle_manage_dependencies ;;
            3) handle_system_diagnostic ;;
            4) handle_initial_setup ;;
            5) handle_install_deps ;;
            6) handle_configure_nodes ;;
            7) handle_development ;;
            8) handle_frontend_only ;;
            9) handle_backend_only ;;
            10) handle_build ;;
            11) handle_docker_build ;;
            12) handle_docker_start ;;
            13) handle_docker_stop ;;
            14) handle_deploy_all ;;
            15) handle_deploy_specific ;;
            16) handle_setup_services ;;
            17) handle_status ;;
            18) handle_logs ;;
            19) handle_tests ;;
            20) handle_clean ;;
            21) handle_info ;;
            22) handle_ssh_keys ;;
            0) 
                echo -e "${GREEN}¡Gracias por usar MAGI!${NC}"
                exit 0
                ;;
            *)
                log_error "Opción inválida. Selecciona un número entre 0-22."
                press_enter
                ;;
        esac
    done
}

# Check if running from correct directory
if [ ! -f "package.json" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    log_error "Por favor ejecuta este script desde el directorio raíz del proyecto MAGI"
    exit 1
fi

# Make sure deps-manager.sh is executable
chmod +x scripts/deps-manager.sh 2>/dev/null

# Start the main menu
main
