import express from 'express';
import { Request, Response } from 'express';
import { exec } from 'child_process';
import { promisify } from 'util';

const router = express.Router();
const execAsync = promisify(exec);

// GET /api/nodes - Get all nodes
router.get('/', (req: Request, res: Response) => {
  const nodes = [
    {
      id: 'gaspar',
      name: 'Gaspar',
      description: 'Multimedia Center',
      ip: '192.168.1.100',
      status: 'online',
      lastSeen: new Date(),
      services: ['node_exporter', 'ttyd', 'jellyfin', 'plex'],
      metrics: {
        cpu: 45.2,
        memory: 68.5,
        disk: 34.7,
        uptime: 259200
      }
    },
    {
      id: 'melchor',
      name: 'Melchor',
      description: 'Backup & Storage',
      ip: '192.168.1.101',
      status: 'online',
      lastSeen: new Date(),
      services: ['node_exporter', 'ttyd', 'syncthing', 'restic'],
      metrics: {
        cpu: 23.1,
        memory: 42.3,
        disk: 78.9,
        uptime: 518400
      }
    },
    {
      id: 'baltasar',
      name: 'Baltasar',
      description: 'Home Automation',
      ip: '192.168.1.102',
      status: 'online',
      lastSeen: new Date(),
      services: ['node_exporter', 'ttyd', 'homeassistant', 'zigbee2mqtt'],
      metrics: {
        cpu: 12.8,
        memory: 35.7,
        disk: 45.2,
        uptime: 432000
      }
    }
  ];

  res.json(nodes);
});

// GET /api/nodes/:id - Get specific node
router.get('/:id', (req: Request, res: Response) => {
  const { id } = req.params;
  
  // Simulación - en producción esto vendría de una base de datos o servicio
  const nodeData = {
    gaspar: {
      id: 'gaspar',
      name: 'Gaspar',
      description: 'Multimedia Center',
      ip: '192.168.1.100',
      status: 'online',
      lastSeen: new Date(),
      services: ['node_exporter', 'ttyd', 'jellyfin', 'plex'],
      metrics: {
        cpu: 45.2,
        memory: 68.5,
        disk: 34.7,
        uptime: 259200
      },
      systemInfo: {
        os: 'Ubuntu 22.04',
        kernel: '5.15.0-76-generic',
        arch: 'x86_64'
      }
    },
    melchor: {
      id: 'melchor',
      name: 'Melchor',
      description: 'Backup & Storage',
      ip: '192.168.1.101',
      status: 'online',
      lastSeen: new Date(),
      services: ['node_exporter', 'ttyd', 'syncthing', 'restic'],
      metrics: {
        cpu: 23.1,
        memory: 42.3,
        disk: 78.9,
        uptime: 518400
      },
      systemInfo: {
        os: 'Debian 12',
        kernel: '6.1.0-10-amd64',
        arch: 'x86_64'
      }
    },
    baltasar: {
      id: 'baltasar',
      name: 'Baltasar',
      description: 'Home Automation',
      ip: '192.168.1.102',
      status: 'online',
      lastSeen: new Date(),
      services: ['node_exporter', 'ttyd', 'homeassistant', 'zigbee2mqtt'],
      metrics: {
        cpu: 12.8,
        memory: 35.7,
        disk: 45.2,
        uptime: 432000
      },
      systemInfo: {
        os: 'Ubuntu 22.04',
        kernel: '5.15.0-76-generic',
        arch: 'aarch64'
      }
    }
  };

  const node = nodeData[id as keyof typeof nodeData];
  
  if (!node) {
    return res.status(404).json({ error: 'Node not found' });
  }

  res.json(node);
});

// POST /api/nodes/:id/restart - Restart a node service
router.post('/:id/restart', (req: Request, res: Response) => {
  const { id } = req.params;
  const { service } = req.body;

  // Simulación - en producción esto ejecutaría comandos SSH
  console.log(`Restarting service ${service} on node ${id}`);
  
  res.json({ 
    success: true, 
    message: `Service ${service} restart initiated on ${id}` 
  });
});

// GET /api/nodes/ping/:ip - Check if node is reachable
router.get('/ping/:ip', async (req: Request, res: Response) => {
  const { ip } = req.params;
  
  try {
    // Usar ping para verificar si el nodo está en línea
    await execAsync(`ping -c 1 -W 2 ${ip}`);
    
    // Si llegamos aquí, el ping fue exitoso
    res.json({ 
      status: 'online',
      ip,
      timestamp: new Date(),
      responseTime: Math.floor(Math.random() * 50) + 1 // Simular tiempo de respuesta
    });
  } catch (error) {
    // Si el ping falla, el nodo está offline
    res.json({ 
      status: 'offline',
      ip,
      timestamp: new Date(),
      error: 'Node unreachable'
    });
  }
});

export default router;
