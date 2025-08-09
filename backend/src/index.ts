import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import morgan from 'morgan';
import dotenv from 'dotenv';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';

import { setupRoutes } from './routes';
import { setupWebSocket } from './websocket';
import { errorHandler, notFound } from './middleware/errorHandler';
import { rateLimiter } from './middleware/rateLimiter';
// import { RedisClient } from './services/redis';  // Comentado temporalmente
import { MetricsCollector } from './services/metricsCollector';
import { logger } from './utils/logger';

dotenv.config();

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

const PORT = process.env.PORT || 5000;
const HOST = process.env.HOST || '0.0.0.0';

// Middleware
app.use(helmet({
  crossOriginEmbedderPolicy: false,
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "ws:", "wss:"],
    },
  },
}));

app.use(cors({
  origin: process.env.NODE_ENV === 'production' 
    ? ['http://localhost:3000'] 
    : true,
  credentials: true
}));

app.use(compression());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Rate limiting
app.use('/api', rateLimiter);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: process.env.npm_package_version || '1.0.0'
  });
});

// API routes
setupRoutes(app);

// WebSocket setup
setupWebSocket(wss);

// Error handling
app.use(notFound);
app.use(errorHandler);

// Initialize services
async function initialize() {
  try {
    // Initialize Redis (commented out temporarily)
    // await RedisClient.getInstance().connect();
    // logger.info('Redis connected successfully');

    // Initialize metrics collector
    const metricsCollector = MetricsCollector.getInstance();
    // await metricsCollector.start();  // Comentado temporalmente
    logger.info('Metrics collector initialized');

    // Start server
    server.listen(PORT, HOST, () => {
      logger.info(`🚀 MAGI Backend server running on http://${HOST}:${PORT}`);
      logger.info(`Environment: ${process.env.NODE_ENV}`);
    });

  } catch (error) {
    logger.error('Failed to initialize server:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully');
  
  server.close(() => {
    logger.info('HTTP server closed');
  });

  try {
    // await RedisClient.getInstance().disconnect();  // Comentado temporalmente
    logger.info('Disconnected from Redis');
  } catch (error) {
    logger.error('Error disconnecting Redis:', error);
  }

  process.exit(0);
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received, shutting down gracefully');
  
  server.close(() => {
    logger.info('HTTP server closed');
  });

  try {
    // await RedisClient.getInstance().disconnect();  // Comentado temporalmente
    logger.info('Redis disconnected');
  } catch (error) {
    logger.error('Error disconnecting Redis:', error);
  }

  process.exit(0);
});

initialize();
