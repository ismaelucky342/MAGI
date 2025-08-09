import { Router, Request, Response } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { body, validationResult } from 'express-validator';
import { RedisClient } from '../services/redis';
import { logger } from '../utils/logger';

const router = Router();

// Default credentials (change in production)
const DEFAULT_USERNAME = 'admin';
const DEFAULT_PASSWORD_HASH = '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewThKhguyYOiZwPu'; // 'admin'

interface LoginRequest {
  username: string;
  password: string;
}

interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    username: string;
  };
}

// Login endpoint
router.post('/login', 
  [
    body('username').trim().isLength({ min: 1 }).escape(),
    body('password').isLength({ min: 1 })
  ],
  async (req: Request<{}, {}, LoginRequest>, res: Response) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Invalid input',
          errors: errors.array()
        });
      }

      const { username, password } = req.body;
      const redis = RedisClient.getInstance();

      // Check for too many failed attempts
      const failedAttempts = await redis.get(`failed_attempts:${username}`) || 0;
      const maxAttempts = parseInt(process.env.MAX_LOGIN_ATTEMPTS || '5');
      
      if (parseInt(failedAttempts.toString()) >= maxAttempts) {
        return res.status(429).json({
          success: false,
          message: 'Too many failed login attempts. Please try again later.'
        });
      }

      // Validate credentials
      if (username !== DEFAULT_USERNAME) {
        await redis.incr(`failed_attempts:${username}`);
        await redis.expire(`failed_attempts:${username}`, 900); // 15 minutes
        
        return res.status(401).json({
          success: false,
          message: 'Invalid credentials'
        });
      }

      const isValidPassword = await bcrypt.compare(password, DEFAULT_PASSWORD_HASH);
      if (!isValidPassword) {
        await redis.incr(`failed_attempts:${username}`);
        await redis.expire(`failed_attempts:${username}`, 900);
        
        return res.status(401).json({
          success: false,
          message: 'Invalid credentials'
        });
      }

      // Clear failed attempts on successful login
      await redis.del(`failed_attempts:${username}`);

      // Generate JWT token
      const token = jwt.sign(
        { 
          id: username,
          username: username,
          iat: Date.now()
        },
        process.env.JWT_SECRET || 'fallback-secret',
        { 
          expiresIn: process.env.JWT_EXPIRES_IN || '24h'
        }
      );

      // Store session in Redis
      const sessionKey = `session:${username}:${Date.now()}`;
      await redis.setex(sessionKey, 86400, JSON.stringify({
        username,
        loginTime: new Date().toISOString(),
        ip: req.ip
      }));

      logger.info(`User ${username} logged in successfully from ${req.ip}`);

      res.json({
        success: true,
        message: 'Login successful',
        token,
        user: {
          username,
          loginTime: new Date().toISOString()
        }
      });

    } catch (error) {
      logger.error('Login error:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error'
      });
    }
  }
);

// Logout endpoint
router.post('/logout', async (req: AuthenticatedRequest, res: Response) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (token) {
      // Add token to blacklist
      const redis = RedisClient.getInstance();
      const decoded = jwt.decode(token) as any;
      if (decoded?.exp) {
        const ttl = decoded.exp - Math.floor(Date.now() / 1000);
        if (ttl > 0) {
          await redis.setex(`blacklist:${token}`, ttl, 'true');
        }
      }
    }

    res.json({
      success: true,
      message: 'Logout successful'
    });

  } catch (error) {
    logger.error('Logout error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Verify token endpoint
router.get('/verify', async (req: Request, res: Response) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'No token provided'
      });
    }

    // Check if token is blacklisted
    const redis = RedisClient.getInstance();
    const isBlacklisted = await redis.get(`blacklist:${token}`);
    if (isBlacklisted) {
      return res.status(401).json({
        success: false,
        message: 'Token is invalid'
      });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback-secret') as any;
    
    res.json({
      success: true,
      user: {
        id: decoded.id,
        username: decoded.username
      }
    });

  } catch (error) {
    if (error instanceof jwt.JsonWebTokenError) {
      return res.status(401).json({
        success: false,
        message: 'Invalid token'
      });
    }
    
    logger.error('Token verification error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Change password endpoint
router.post('/change-password',
  [
    body('currentPassword').isLength({ min: 1 }),
    body('newPassword').isLength({ min: 6 }),
  ],
  async (req: AuthenticatedRequest, res: Response) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Invalid input',
          errors: errors.array()
        });
      }

      // This would typically update the user in a database
      // For now, we'll just return a success message
      res.json({
        success: true,
        message: 'Password change feature not yet implemented'
      });

    } catch (error) {
      logger.error('Change password error:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error'
      });
    }
  }
);

export default router;
