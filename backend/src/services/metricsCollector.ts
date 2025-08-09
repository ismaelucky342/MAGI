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
