import express from 'express';
import { Request, Response } from 'express';

const router = express.Router();

// GET /api/metrics/:nodeId - Get metrics for a specific node
router.get('/:nodeId', (req: Request, res: Response) => {
  const { nodeId } = req.params;
  
  // Simulación de métricas en tiempo real
  const generateMetrics = () => ({
    timestamp: new Date(),
    cpu: {
      usage: Math.random() * 100,
      cores: 4,
      temperature: 40 + Math.random() * 30
    },
    memory: {
      used: Math.random() * 16,
      total: 16,
      percentage: Math.random() * 100
    },
    disk: {
      used: Math.random() * 1000,
      total: 1000,
      percentage: Math.random() * 100
    },
    network: {
      rx: Math.random() * 1000,
      tx: Math.random() * 500,
      packets_rx: Math.floor(Math.random() * 10000),
      packets_tx: Math.floor(Math.random() * 8000)
    },
    uptime: Math.floor(Math.random() * 1000000)
  });

  res.json(generateMetrics());
});

// GET /api/metrics/:nodeId/history - Get historical metrics
router.get('/:nodeId/history', (req: Request, res: Response) => {
  const { nodeId } = req.params;
  const { hours = 24 } = req.query;
  
  // Generar datos históricos simulados
  const historyData = [];
  const now = new Date();
  const pointCount = parseInt(hours as string) * 6; // Un punto cada 10 minutos
  
  for (let i = pointCount; i >= 0; i--) {
    const timestamp = new Date(now.getTime() - (i * 10 * 60 * 1000));
    historyData.push({
      timestamp,
      cpu: Math.random() * 100,
      memory: Math.random() * 100,
      disk: Math.random() * 100,
      network_rx: Math.random() * 1000,
      network_tx: Math.random() * 500
    });
  }
  
  res.json({
    nodeId,
    period: `${hours} hours`,
    data: historyData
  });
});

export default router;
