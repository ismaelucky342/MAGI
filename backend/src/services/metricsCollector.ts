import { logger } from '../utils/logger';

export interface MetricData {
  timestamp: number;
  value: number;
  node: string;
  metric: string;
}

export class MetricsCollector {
  private metrics: Map<string, MetricData[]> = new Map();

  constructor() {
    logger.info('MetricsCollector initialized');
  }

  public addMetric(node: string, metric: string, value: number): void {
    const key = `${node}:${metric}`;
    const data: MetricData = {
      timestamp: Date.now(),
      value,
      node,
      metric,
    };

    if (!this.metrics.has(key)) {
      this.metrics.set(key, []);
    }

    const metrics = this.metrics.get(key)!;
    metrics.push(data);

    // Keep only last 100 metrics per key
    if (metrics.length > 100) {
      metrics.shift();
    }
  }

  public getMetrics(node?: string, metric?: string): MetricData[] {
    if (node && metric) {
      const key = `${node}:${metric}`;
      return this.metrics.get(key) || [];
    }

    if (node) {
      const result: MetricData[] = [];
      for (const [key, data] of this.metrics) {
        if (key.startsWith(`${node}:`)) {
          result.push(...data);
        }
      }
      return result;
    }

    // Return all metrics
    const result: MetricData[] = [];
    for (const data of this.metrics.values()) {
      result.push(...data);
    }
    return result;
  }

  public getLatestMetrics(node?: string): Record<string, MetricData> {
    const result: Record<string, MetricData> = {};
    
    for (const [key, data] of this.metrics) {
      if (node && !key.startsWith(`${node}:`)) {
        continue;
      }
      
      if (data.length > 0) {
        const latest = data[data.length - 1];
        result[key] = latest;
      }
    }
    
    return result;
  }

  public clearMetrics(node?: string): void {
    if (node) {
      const keysToDelete = Array.from(this.metrics.keys()).filter(key => 
        key.startsWith(`${node}:`)
      );
      for (const key of keysToDelete) {
        this.metrics.delete(key);
      }
    } else {
      this.metrics.clear();
    }
  }
}
