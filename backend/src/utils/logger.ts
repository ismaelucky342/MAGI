import fs from 'fs';
import path from 'path';

// Simple logger implementation
interface LogLevel {
  ERROR: number;
  WARN: number;
  INFO: number;
  DEBUG: number;
}

const LOG_LEVELS: LogLevel = {
  ERROR: 0,
  WARN: 1,
  INFO: 2,
  DEBUG: 3
};

class Logger {
  private logLevel: number;
  private logFile?: string;

  constructor() {
    const level = process.env.LOG_LEVEL?.toLowerCase() || 'info';
    this.logLevel = this.getLogLevel(level);
    this.logFile = process.env.LOG_FILE;
    
    // Ensure log directory exists
    if (this.logFile) {
      const logDir = path.dirname(this.logFile);
      if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true });
      }
    }
  }

  private getLogLevel(level: string): number {
    switch (level) {
      case 'error': return LOG_LEVELS.ERROR;
      case 'warn': return LOG_LEVELS.WARN;
      case 'info': return LOG_LEVELS.INFO;
      case 'debug': return LOG_LEVELS.DEBUG;
      default: return LOG_LEVELS.INFO;
    }
  }

  private formatMessage(level: string, message: string, ...args: any[]): string {
    const timestamp = new Date().toISOString();
    const formattedArgs = args.length > 0 ? ' ' + args.map(arg => 
      typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
    ).join(' ') : '';
    
    return `[${timestamp}] [${level.toUpperCase()}] ${message}${formattedArgs}`;
  }

  private writeLog(level: string, message: string, ...args: any[]): void {
    const formattedMessage = this.formatMessage(level, message, ...args);
    
    // Console output
    console.log(formattedMessage);
    
    // File output
    if (this.logFile) {
      fs.appendFileSync(this.logFile, formattedMessage + '\n');
    }
  }

  public error(message: string, ...args: any[]): void {
    if (this.logLevel >= LOG_LEVELS.ERROR) {
      this.writeLog('error', message, ...args);
    }
  }

  public warn(message: string, ...args: any[]): void {
    if (this.logLevel >= LOG_LEVELS.WARN) {
      this.writeLog('warn', message, ...args);
    }
  }

  public info(message: string, ...args: any[]): void {
    if (this.logLevel >= LOG_LEVELS.INFO) {
      this.writeLog('info', message, ...args);
    }
  }

  public debug(message: string, ...args: any[]): void {
    if (this.logLevel >= LOG_LEVELS.DEBUG) {
      this.writeLog('debug', message, ...args);
    }
  }
}

export const logger = new Logger();
