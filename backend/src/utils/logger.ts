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
