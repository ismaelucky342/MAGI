import { Server } from 'socket.io';
import { Server as HttpServer } from 'http';

export function setupWebSocket(httpServer: HttpServer) {
  const io = new Server(httpServer, {
    cors: {
      origin: process.env.FRONTEND_URL || "http://localhost:3000",
      methods: ["GET", "POST"]
    }
  });

  io.on('connection', (socket) => {
    console.log('Client connected:', socket.id);

    // Handle node metrics subscription
    socket.on('subscribe:metrics', (nodeId: string) => {
      console.log(`Client ${socket.id} subscribed to metrics for ${nodeId}`);
      socket.join(`metrics:${nodeId}`);
      
      // Send initial metrics
      socket.emit('metrics:update', {
        nodeId,
        timestamp: new Date(),
        metrics: generateMockMetrics()
      });
    });

    // Handle node metrics unsubscription
    socket.on('unsubscribe:metrics', (nodeId: string) => {
      console.log(`Client ${socket.id} unsubscribed from metrics for ${nodeId}`);
      socket.leave(`metrics:${nodeId}`);
    });

    // Handle terminal session
    socket.on('terminal:connect', (nodeId: string) => {
      console.log(`Terminal connection request for ${nodeId}`);
      socket.join(`terminal:${nodeId}`);
      
      socket.emit('terminal:connected', {
        nodeId,
        message: `Connected to ${nodeId} terminal`
      });
    });

    socket.on('terminal:command', (data: { nodeId: string; command: string }) => {
      console.log(`Terminal command on ${data.nodeId}: ${data.command}`);
      
      // Simulate command execution
      const mockOutput = simulateCommand(data.command);
      
      socket.emit('terminal:output', {
        nodeId: data.nodeId,
        command: data.command,
        output: mockOutput,
        timestamp: new Date()
      });
    });

    socket.on('disconnect', () => {
      console.log('Client disconnected:', socket.id);
    });
  });

  // Send periodic metrics updates
  setInterval(() => {
    const nodes = ['gaspar', 'melchor', 'baltasar'];
    
    nodes.forEach(nodeId => {
      io.to(`metrics:${nodeId}`).emit('metrics:update', {
        nodeId,
        timestamp: new Date(),
        metrics: generateMockMetrics()
      });
    });
  }, 5000); // Every 5 seconds

  return io;
}

function generateMockMetrics() {
  return {
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
  };
}

function simulateCommand(command: string): string {
  const responses: { [key: string]: string } = {
    'ls': 'Desktop  Documents  Downloads  Music  Pictures  Videos',
    'pwd': '/home/admin',
    'whoami': 'admin',
    'date': new Date().toString(),
    'uptime': ' 15:42:33 up 3 days,  6:23,  2 users,  load average: 0.15, 0.12, 0.08',
    'ps aux': `USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1  225468  9768 ?        Ss   Aug06   0:02 /sbin/init
root         2  0.0  0.0      0     0 ?        S    Aug06   0:00 [kthreadd]
admin     1234  0.1  2.3 1234567 89012 ?        Sl   12:34   1:23 node server.js`,
    'df -h': `Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        20G   12G  7.2G  63% /
tmpfs           2.0G     0  2.0G   0% /dev/shm
/dev/sda2       100G   45G   50G  48% /home`,
    'free -h': `              total        used        free      shared  buff/cache   available
Mem:          8.0Gi       2.1Gi       4.2Gi       0.1Gi       1.7Gi       5.6Gi
Swap:         2.0Gi          0B       2.0Gi`,
    'systemctl status': `● system.slice
   Loaded: loaded
   Active: active since Mon 2024-08-06 09:15:33 UTC; 3 days ago`
  };

  return responses[command] || `bash: ${command}: command not found`;
}
