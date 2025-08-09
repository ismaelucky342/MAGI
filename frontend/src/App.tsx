import React, { useState, useEffect } from 'react';
import './App.css';

interface NodeData {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'error';
  ip: string;
  code: string;
}

const services = [
  { name: 'NODE EXPORTER:9100', status: 'error' },
  { name: 'WEB TERMINAL:7681', status: 'error' },
  { name: 'SSH PROXY:2222', status: 'error' },
  { name: 'METRICS API:5000', status: 'standby' },
  { name: 'REDIS CACHE:6379', status: 'error' }
];

const systemLogs = [
  '[9/8/2025, 16:42:37] CRITICAL: ALL NODES OFFLINE - EMERGENCY MODE ACTIVE',
  '[9/8/2025, 16:42:36] CRITICAL: ALL NODES OFFLINE - EMERGENCY MODE ACTIVE', 
  '[2025-08-09 15:30:01] MAGI SYSTEM INITIALIZED',
  '[2025-08-09 15:30:02] SCANNING NETWORK FOR NODES...',
  '[2025-08-09 15:30:03] GASPAR • 3 - CONNECTION FAILED',
  '[2025-08-09 15:30:04] MELCHIOR • 1 - CONNECTION FAILED',
  '[2025-08-09 15:30:05] BALTASAR • 2 - CONNECTION FAILED',
  '[2025-08-09 15:30:06] WARNING: ALL NODES OFFLINE',
  '[2025-08-09 15:30:07] ENTERING EMERGENCY MODE'
];

function App() {
  const [nodes, setNodes] = useState<NodeData[]>([
    {
      id: 'gaspar',
      name: 'GASPAR • 3',
      status: 'offline',
      ip: '192.168.1.100',
      code: '473'
    },
    {
      id: 'melchor', 
      name: 'MELCHIOR • 1',
      status: 'offline',
      ip: '192.168.1.101',
      code: '281'
    },
    {
      id: 'baltasar',
      name: 'BALTASAR • 2', 
      status: 'offline',
      ip: '192.168.1.102',
      code: '692'
    }
  ]);

  // Simular pings reales cada 3 segundos
  useEffect(() => {
    const checkNodes = async () => {
      try {
        const updatedNodes = await Promise.all(
          nodes.map(async (node) => {
            try {
              const response = await fetch(`/api/nodes/ping/${node.ip}`);
              const data = await response.json();
              return {
                ...node,
                status: data.reachable ? 'online' : 'offline'
              } as NodeData;
            } catch (error) {
              return {
                ...node,
                status: 'offline'
              } as NodeData;
            }
          })
        );
        setNodes(updatedNodes);
      } catch (error) {
        console.error('Error checking nodes:', error);
      }
    };

    // Verificar inmediatamente
    checkNodes();
    
    // Luego verificar cada 3 segundos
    const interval = setInterval(checkNodes, 3000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="magi-system" style={{
      height: '100vh',
      width: '100vw',
      backgroundColor: '#000',
      color: '#ff3333',
      border: '3px solid #ff3333',
      position: 'fixed',
      top: 0,
      left: 0,
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Header */}
      <div className="magi-header" style={{
        backgroundColor: 'rgba(255, 51, 51, 0.1)',
        borderBottom: '2px solid #ff3333',
        padding: '15px 20px',
        display: 'grid',
        gridTemplateColumns: '1fr 2fr 1fr',
        alignItems: 'center',
        height: '80px'
      }}>
        <div className="system-info" style={{ fontSize: '12px', color: '#ff3333' }}>
          <div>FILE: MAGI_SYS</div>
          <div>EXTENSION: 3023</div>
          <div>EX_MODE: OFF</div>
          <div>PRIORITY: AAA</div>
          <div>MAGI</div>
          <div>情報</div>
          <div>ノード詳細</div>
        </div>
        <div className="central-display" style={{ textAlign: 'center' }}>
          <img 
            src="/MAGI.png" 
            alt="MAGI" 
            className="magi-logo"
            style={{
              height: '50px',
              width: 'auto',
              filter: 'drop-shadow(0 0 20px #ff3333) drop-shadow(0 0 40px #ff3333) brightness(1.2) contrast(1.3)',
              animation: 'glow 2s ease-in-out infinite alternate',
              marginBottom: '5px'
            }}
          />
          <div className="subtitle" style={{ fontSize: '12px', color: '#ff3333', opacity: 0.8 }}>
            Distributed Node Monitoring System
          </div>
        </div>
        <div className="status-indicator" style={{ textAlign: 'right', fontSize: '12px' }}>
          <div className="system-status error" style={{
            backgroundColor: 'rgba(255, 51, 51, 0.3)',
            border: '1px solid #ff3333',
            padding: '5px 10px',
            color: '#ff3333',
            fontWeight: 'bold',
            marginBottom: '5px'
          }}>EMERGENCY MODE</div>
          <div className="timestamp" style={{ color: '#ff3333' }}>
            {new Date().toLocaleString()}
          </div>
        </div>
      </div>

      {/* Main Grid Layout */}
      <div className="main-grid" style={{
        display: 'grid',
        gridTemplateColumns: '1fr 300px',
        gap: '10px',
        padding: '20px',
        flex: 1,
        height: 'calc(100vh - 280px)',
        overflow: 'hidden'
      }}>
        {/* Left Panel - Node Details */}
        <div className="left-panel" style={{
          backgroundColor: 'rgba(255, 51, 51, 0.05)',
          border: '1px solid #ff3333',
          padding: '15px',
          color: '#ff3333',
          overflowY: 'auto'
        }}>
          <div className="panel-title" style={{
            fontSize: '14px',
            fontWeight: 'bold',
            textAlign: 'center',
            borderBottom: '1px solid #ff3333',
            paddingBottom: '10px',
            marginBottom: '15px',
            color: '#ff3333'
          }}>SELECT A NODE FOR DETAILS</div>
          <div className="panel-content">
            <div className="help-text">
              <div style={{ color: '#ff3333', marginBottom: '10px' }}>MAGI</div>
              <div style={{ color: '#ff3333', marginBottom: '10px' }}>SERVICES</div>
              {services.map((service, index) => (
                <div key={index} className="service-row" style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '8px 0',
                  borderBottom: '1px solid rgba(255, 51, 51, 0.2)',
                  fontSize: '12px',
                  color: '#ff3333'
                }}>
                  <span>{service.name}</span>
                  <span className={`status ${service.status}`} style={{
                    fontWeight: 'bold',
                    padding: '2px 8px',
                    borderRadius: '3px',
                    color: service.status === 'error' ? '#ff3333' : '#ffaa00',
                    backgroundColor: service.status === 'error' ? 'rgba(255, 51, 51, 0.2)' : 'rgba(255, 170, 0, 0.2)',
                    border: service.status === 'error' ? '1px solid #ff3333' : '1px solid #ffaa00'
                  }}>
                    {service.status.toUpperCase()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Panel - Nodes */}
        <div className="right-panel" style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '15px',
          overflowY: 'auto'
        }}>
          {nodes.map((node) => (
            <div key={node.id} className={`node-display ${node.status}`} style={{
              backgroundColor: 'rgba(255, 51, 51, 0.05)',
              border: '2px solid #ff3333',
              padding: '15px',
              transition: 'all 0.3s ease',
              color: '#ff3333',
              boxShadow: '0 0 10px rgba(255, 51, 51, 0.4)'
            }}>
              <div className="node-header" style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '5px'
              }}>
                <div className="node-name" style={{
                  fontSize: '16px',
                  fontWeight: 'bold',
                  color: '#ffffff'
                }}>{node.name}</div>
                <div className="node-ip" style={{
                  fontSize: '14px',
                  color: '#cccccc'
                }}>{node.ip}</div>
                <div className={`node-status ${node.status}`} style={{
                  fontSize: '12px',
                  fontWeight: 'bold',
                  padding: '3px 8px',
                  borderRadius: '3px',
                  width: 'fit-content',
                  color: '#ff3333',
                  backgroundColor: 'rgba(255, 51, 51, 0.2)',
                  border: '1px solid #ff3333'
                }}>
                  {node.status.toUpperCase()}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Terminal */}
      <div className="terminal-section" style={{
        backgroundColor: '#000000',
        borderTop: '2px solid #ff3333',
        height: '200px',
        display: 'flex',
        flexDirection: 'column',
        color: '#ff3333'
      }}>
        <div className="terminal-header" style={{
          backgroundColor: 'rgba(255, 51, 51, 0.1)',
          padding: '8px 15px',
          borderBottom: '1px solid #ff3333',
          fontSize: '12px',
          fontWeight: 'bold',
          color: '#ff3333'
        }}>
          <span>SYSTEM LOGS</span>
        </div>
        <div className="terminal-content" style={{
          flex: 1,
          padding: '10px 15px',
          overflowY: 'auto',
          fontSize: '12px',
          lineHeight: '1.4',
          color: '#ff3333'
        }}>
          <div className="terminal-line system" style={{
            color: '#00ff00',
            fontWeight: 'bold',
            marginBottom: '10px'
          }}>MAGI_TERMINAL v3.0.23</div>
          {systemLogs.map((log, index) => (
            <div key={index} className="terminal-line" style={{
              marginBottom: '2px',
              display: 'flex',
              alignItems: 'center',
              color: '#ff3333'
            }}>
              <span className="prompt" style={{
                color: '#00ff00',
                marginRight: '5px'
              }}>&gt;</span>
              <span className="log-text" style={{
                color: '#ff3333'
              }}>{log}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
