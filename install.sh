#!/bin/bash

# MAGI - Instalación Simplificada
# Este script instala y configura todo el sistema MAGI de una vez

set -e  # Salir si cualquier comando falla

echo "🧙‍♂️ MAGI - Instalación Simplificada"
echo "=================================="
echo

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Función para instalar Node.js
install_nodejs() {
    echo "📦 Instalando Node.js..."
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y nodejs npm
    elif command_exists yum; then
        sudo yum install -y nodejs npm
    elif command_exists pacman; then
        sudo pacman -S nodejs npm
    else
        echo "❌ No se puede instalar Node.js automáticamente"
        echo "Por favor, instala Node.js manualmente desde https://nodejs.org"
        exit 1
    fi
}

# Función para instalar Docker
install_docker() {
    echo "🐳 Instalando Docker..."
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y docker.io docker-compose
        sudo systemctl enable docker
        sudo systemctl start docker
        sudo usermod -aG docker $USER
    elif command_exists yum; then
        sudo yum install -y docker docker-compose
        sudo systemctl enable docker
        sudo systemctl start docker
        sudo usermod -aG docker $USER
    else
        echo "❌ No se puede instalar Docker automáticamente"
        echo "Por favor, instala Docker manualmente"
        exit 1
    fi
}

# Verificar dependencias del sistema
echo "🔍 Verificando dependencias del sistema..."

# Verificar Node.js
if ! command_exists node; then
    echo "❌ Node.js no está instalado"
    read -p "¿Quieres instalar Node.js? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_nodejs
    else
        echo "❌ Node.js es requerido. Saliendo..."
        exit 1
    fi
else
    echo "✅ Node.js encontrado: $(node --version)"
fi

# Verificar npm
if ! command_exists npm; then
    echo "❌ npm no está instalado"
    install_nodejs
else
    echo "✅ npm encontrado: $(npm --version)"
fi

# Verificar Docker (opcional)
if ! command_exists docker; then
    echo "⚠️  Docker no está instalado"
    read -p "¿Quieres instalar Docker? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_docker
    else
        echo "⚠️  Docker no instalado. Podrás usar solo el modo desarrollo."
    fi
else
    echo "✅ Docker encontrado: $(docker --version)"
fi

echo
echo "🚀 Configurando proyecto MAGI..."

# Crear estructura de directorios si no existe
mkdir -p backend/src/{routes,middleware,services,utils}
mkdir -p frontend/src/{components,services,types,hooks}
mkdir -p scripts
mkdir -p docker

# Instalar dependencias del proyecto raíz
echo "📦 Instalando dependencias del proyecto raíz..."
npm install

# Instalar dependencias del backend
echo "📦 Instalando dependencias del backend..."
cd backend
npm install

# Crear archivos faltantes del backend
echo "🔧 Creando archivos de configuración del backend..."

# Crear rateLimiter.ts
cat > src/middleware/rateLimiter.ts << 'EOF'
import rateLimit from 'express-rate-limit';

export const rateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100, // límite de 100 requests por ventana por IP
  message: 'Demasiadas peticiones desde esta IP, intenta de nuevo más tarde.',
  standardHeaders: true,
  legacyHeaders: false,
});

export const strictRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 20,
  message: 'Límite de peticiones excedido para esta operación.',
});
EOF

# Crear redis.ts
cat > src/services/redis.ts << 'EOF'
import { createClient } from 'redis';
import { logger } from '../utils/logger';

export class RedisClient {
  private static instance: RedisClient;
  private client: any;

  private constructor() {
    this.client = createClient({
      url: process.env.REDIS_URL || 'redis://localhost:6379',
    });

    this.client.on('error', (err: any) => {
      logger.error('Redis Client Error', err);
    });

    this.client.on('connect', () => {
      logger.info('Redis Client Connected');
    });
  }

  public static getInstance(): RedisClient {
    if (!RedisClient.instance) {
      RedisClient.instance = new RedisClient();
    }
    return RedisClient.instance;
  }

  async connect() {
    try {
      await this.client.connect();
      logger.info('Connected to Redis');
    } catch (error) {
      logger.error('Failed to connect to Redis:', error);
    }
  }

  async get(key: string): Promise<string | null> {
    try {
      return await this.client.get(key);
    } catch (error) {
      logger.error('Redis GET error:', error);
      return null;
    }
  }

  async set(key: string, value: string, expireInSeconds?: number): Promise<boolean> {
    try {
      if (expireInSeconds) {
        await this.client.setEx(key, expireInSeconds, value);
      } else {
        await this.client.set(key, value);
      }
      return true;
    } catch (error) {
      logger.error('Redis SET error:', error);
      return false;
    }
  }

  async del(key: string): Promise<boolean> {
    try {
      await this.client.del(key);
      return true;
    } catch (error) {
      logger.error('Redis DEL error:', error);
      return false;
    }
  }

  async disconnect() {
    try {
      await this.client.disconnect();
      logger.info('Disconnected from Redis');
    } catch (error) {
      logger.error('Error disconnecting from Redis:', error);
    }
  }
}
EOF

# Crear metricsCollector.ts
cat > src/services/metricsCollector.ts << 'EOF'
import * as si from 'systeminformation';
import { logger } from '../utils/logger';

export interface SystemMetrics {
  cpu: number;
  memory: {
    used: number;
    total: number;
    free: number;
    percentage: number;
  };
  disk: {
    used: number;
    total: number;
    free: number;
    percentage: number;
  };
  network: {
    rx: number;
    tx: number;
  };
  uptime: number;
  timestamp: number;
}

export class MetricsCollector {
  private static instance: MetricsCollector;

  private constructor() {}

  public static getInstance(): MetricsCollector {
    if (!MetricsCollector.instance) {
      MetricsCollector.instance = new MetricsCollector();
    }
    return MetricsCollector.instance;
  }

  async collectSystemMetrics(): Promise<SystemMetrics> {
    try {
      const [cpu, mem, disk, network] = await Promise.all([
        si.currentLoad(),
        si.mem(),
        si.fsSize(),
        si.networkStats(),
      ]);

      const diskInfo = disk[0] || { used: 0, size: 0 };
      const networkInfo = network[0] || { rx_bytes: 0, tx_bytes: 0 };

      return {
        cpu: Math.round(cpu.currentLoad),
        memory: {
          used: mem.used,
          total: mem.total,
          free: mem.free,
          percentage: Math.round((mem.used / mem.total) * 100),
        },
        disk: {
          used: diskInfo.used,
          total: diskInfo.size,
          free: diskInfo.size - diskInfo.used,
          percentage: Math.round((diskInfo.used / diskInfo.size) * 100),
        },
        network: {
          rx: networkInfo.rx_bytes,
          tx: networkInfo.tx_bytes,
        },
        uptime: Math.round(si.time().uptime),
        timestamp: Date.now(),
      };
    } catch (error) {
      logger.error('Error collecting metrics:', error);
      throw error;
    }
  }

  async getNodeMetrics(nodeId: string): Promise<SystemMetrics> {
    // Por ahora devolvemos métricas simuladas
    // En el futuro esto se conectará vía SSH a los nodos reales
    return {
      cpu: Math.floor(Math.random() * 100),
      memory: {
        used: Math.floor(Math.random() * 8000000000),
        total: 8000000000,
        free: Math.floor(Math.random() * 2000000000),
        percentage: Math.floor(Math.random() * 100),
      },
      disk: {
        used: Math.floor(Math.random() * 500000000000),
        total: 1000000000000,
        free: Math.floor(Math.random() * 500000000000),
        percentage: Math.floor(Math.random() * 100),
      },
      network: {
        rx: Math.floor(Math.random() * 1000000),
        tx: Math.floor(Math.random() * 1000000),
      },
      uptime: Math.floor(Math.random() * 86400),
      timestamp: Date.now(),
    };
  }
}
EOF

# Crear logger.ts
cat > src/utils/logger.ts << 'EOF'
import { createWriteStream, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

enum LogLevel {
  ERROR = 0,
  WARN = 1,
  INFO = 2,
  DEBUG = 3,
}

class Logger {
  private logLevel: LogLevel;
  private logStream: any;

  constructor() {
    this.logLevel = this.parseLogLevel(process.env.LOG_LEVEL || 'info');
    
    // Crear directorio de logs si no existe
    const logDir = join(process.cwd(), 'logs');
    if (!existsSync(logDir)) {
      mkdirSync(logDir, { recursive: true });
    }

    // Crear stream de log
    const logFile = join(logDir, `magi-${new Date().toISOString().split('T')[0]}.log`);
    this.logStream = createWriteStream(logFile, { flags: 'a' });
  }

  private parseLogLevel(level: string): LogLevel {
    switch (level.toLowerCase()) {
      case 'error':
        return LogLevel.ERROR;
      case 'warn':
        return LogLevel.WARN;
      case 'info':
        return LogLevel.INFO;
      case 'debug':
        return LogLevel.DEBUG;
      default:
        return LogLevel.INFO;
    }
  }

  private formatMessage(level: string, message: string, meta?: any): string {
    const timestamp = new Date().toISOString();
    const metaString = meta ? ` ${JSON.stringify(meta)}` : '';
    return `[${timestamp}] ${level.toUpperCase()}: ${message}${metaString}`;
  }

  private log(level: LogLevel, levelName: string, message: string, meta?: any) {
    if (level <= this.logLevel) {
      const formattedMessage = this.formatMessage(levelName, message, meta);
      
      // Log a consola
      console.log(formattedMessage);
      
      // Log a archivo
      this.logStream.write(formattedMessage + '\n');
    }
  }

  error(message: string, meta?: any) {
    this.log(LogLevel.ERROR, 'error', message, meta);
  }

  warn(message: string, meta?: any) {
    this.log(LogLevel.WARN, 'warn', message, meta);
  }

  info(message: string, meta?: any) {
    this.log(LogLevel.INFO, 'info', message, meta);
  }

  debug(message: string, meta?: any) {
    this.log(LogLevel.DEBUG, 'debug', message, meta);
  }
}

export const logger = new Logger();
EOF

echo "✅ Backend configurado correctamente"

# Volver al directorio raíz
cd ..

# Instalar dependencias del frontend
echo "📦 Instalando dependencias del frontend..."
cd frontend

# Instalar dependencias básicas primero
npm install --legacy-peer-deps

# Crear archivo .env para deshabilitar ESLint temporalmente
echo "DISABLE_ESLINT_PLUGIN=true" > .env
echo "SKIP_PREFLIGHT_CHECK=true" >> .env

echo "✅ Frontend configurado correctamente"

# Volver al directorio raíz
cd ..

# Crear archivo .env principal
echo "🔧 Creando configuración de entorno..."
cat > .env << 'EOF'
# MAGI Configuration
NODE_ENV=development
PORT=5000
FRONTEND_PORT=3000

# Security
JWT_SECRET=magi-super-secret-key-change-in-production
SESSION_SECRET=magi-session-secret-change-in-production

# Database
REDIS_URL=redis://localhost:6379

# Nodes Configuration
GASPAR_HOST=192.168.1.10
MELCHOR_HOST=192.168.1.11
BALTASAR_HOST=192.168.1.12

# SSH Configuration
SSH_USERNAME=your-username
SSH_PRIVATE_KEY_PATH=/path/to/your/private/key

# Logging
LOG_LEVEL=info

# Development
DISABLE_ESLINT_PLUGIN=true
SKIP_PREFLIGHT_CHECK=true
EOF

echo
echo "🎉 ¡Instalación completada!"
echo "========================"
echo
echo "📋 Próximos pasos:"
echo "1. Edita el archivo .env con tu configuración específica"
echo "2. Ejecuta 'make dev' para iniciar el entorno de desarrollo"
echo "3. Visita http://localhost:3000 para ver la interfaz"
echo "4. La API estará disponible en http://localhost:5000"
echo
echo "🚀 Comandos útiles:"
echo "   make dev       - Iniciar entorno de desarrollo"
echo "   make build     - Construir para producción"
echo "   make docker    - Ejecutar con Docker"
echo "   make clean     - Limpiar dependencias"
echo
echo "🧙‍♂️ ¡MAGI está listo para usar!"
