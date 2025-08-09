import express from 'express';
import { Request, Response } from 'express';

const router = express.Router();

// GET /api/config - Get system configuration
router.get('/', (req: Request, res: Response) => {
  const config = {
    system: {
      name: 'MAGI Monitoring System',
      version: '1.0.0',
      description: 'Distributed monitoring for Gaspar, Melchor, and Baltasar nodes'
    },
    nodes: [
      {
        id: 'gaspar',
        name: 'Gaspar',
        ip: '192.168.1.100',
        services: ['jellyfin:8096', 'plex:32400', 'node_exporter:9100', 'ttyd:7681']
      },
      {
        id: 'melchor',
        name: 'Melchor',
        ip: '192.168.1.101',
        services: ['syncthing:8384', 'restic:8080', 'node_exporter:9100', 'ttyd:7682']
      },
      {
        id: 'baltasar',
        name: 'Baltasar',
        ip: '192.168.1.102',
        services: ['homeassistant:8123', 'zigbee2mqtt:8080', 'node_exporter:9100', 'ttyd:7683']
      }
    ],
    monitoring: {
      interval: 30,
      retention: '30d',
      alerting: true
    }
  };
  
  res.json(config);
});

// PUT /api/config - Update configuration
router.put('/', (req: Request, res: Response) => {
  const { config } = req.body;
  
  // Simulación - en producción esto actualizaría la configuración
  console.log('Updating configuration:', config);
  
  res.json({
    success: true,
    message: 'Configuration updated successfully'
  });
});

export default router;
