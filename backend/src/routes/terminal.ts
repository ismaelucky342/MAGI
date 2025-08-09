import express from 'express';
import { Request, Response } from 'express';

const router = express.Router();

// POST /api/terminal/:nodeId/connect - Establish terminal connection
router.post('/:nodeId/connect', (req: Request, res: Response) => {
  const { nodeId } = req.params;
  
  // Simulación - en producción esto establecería una conexión SSH/WebSocket
  const terminalUrls = {
    gaspar: 'http://192.168.1.100:7681',
    melchor: 'http://192.168.1.101:7682',
    baltasar: 'http://192.168.1.102:7683'
  };
  
  const url = terminalUrls[nodeId as keyof typeof terminalUrls];
  
  if (!url) {
    return res.status(404).json({ error: 'Node not found' });
  }
  
  res.json({
    success: true,
    terminalUrl: url,
    nodeId,
    protocol: 'ttyd',
    message: 'Terminal connection ready'
  });
});

// GET /api/terminal/:nodeId/status - Check terminal service status
router.get('/:nodeId/status', (req: Request, res: Response) => {
  const { nodeId } = req.params;
  
  // Simulación del estado del servicio
  res.json({
    nodeId,
    status: 'running',
    port: nodeId === 'gaspar' ? 7681 : nodeId === 'melchor' ? 7682 : 7683,
    uptime: Math.floor(Math.random() * 86400),
    connections: Math.floor(Math.random() * 5)
  });
});

// POST /api/terminal/:nodeId/command - Execute command (for simple commands)
router.post('/:nodeId/command', (req: Request, res: Response) => {
  const { nodeId } = req.params;
  const { command } = req.body;
  
  // Simulación - en producción esto ejecutaría el comando via SSH
  const simulatedOutput = {
    'ls': 'Desktop  Documents  Downloads  Music  Pictures  Videos',
    'pwd': `/home/admin`,
    'whoami': 'admin',
    'uptime': ' 15:42:33 up 3 days,  6:23,  2 users,  load average: 0.15, 0.12, 0.08',
    'df -h': `Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        20G   12G  7.2G  63% /
tmpfs           2.0G     0  2.0G   0% /dev/shm`,
    'free -h': `              total        used        free      shared  buff/cache   available
Mem:          8.0Gi       2.1Gi       4.2Gi       0.1Gi       1.7Gi       5.6Gi
Swap:         2.0Gi          0B       2.0Gi`
  };
  
  const output = simulatedOutput[command as keyof typeof simulatedOutput] || 
                `Command '${command}' executed on ${nodeId}\nOutput simulation not available for this command.`;
  
  res.json({
    nodeId,
    command,
    output,
    timestamp: new Date(),
    exitCode: 0
  });
});

export default router;
