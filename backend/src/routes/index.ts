import { Express } from 'express';
import authRoutes from './auth';
import nodeRoutes from './nodes';
import metricsRoutes from './metrics';
import terminalRoutes from './terminal';
import configRoutes from './config';

export function setupRoutes(app: Express) {
  app.use('/api/auth', authRoutes);
  app.use('/api/nodes', nodeRoutes);
  app.use('/api/metrics', metricsRoutes);
  app.use('/api/terminal', terminalRoutes);
  app.use('/api/config', configRoutes);
}
