import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <div className="magi-header">
          <h1>🧙‍♂️ MAGI</h1>
          <p>Magical Automation & General Intelligence</p>
          <small>Distributed Node Monitoring System</small>
        </div>
        
        <div className="node-grid">
          <div className="node-card">
            <h3>🎮 Gaspar</h3>
            <p>Multimedia Center</p>
            <span className="status online">192.168.1.100</span>
          </div>
          
          <div className="node-card">
            <h3>💾 Melchor</h3>
            <p>Backup & Storage</p>
            <span className="status online">192.168.1.101</span>
          </div>
          
          <div className="node-card">
            <h3>🏠 Baltasar</h3>
            <p>Home Automation</p>
            <span className="status online">192.168.1.102</span>
          </div>
        </div>
        
        <div className="quick-actions">
          <button className="action-btn">📊 Dashboard</button>
          <button className="action-btn">🖥️ Terminals</button>
          <button className="action-btn">⚙️ Settings</button>
        </div>
        
        <div className="footer">
          <p>✅ Sistema funcionando correctamente</p>
          <p>🎉 Todas las dependencias instaladas exitosamente</p>
          <p>🚀 Ready for development!</p>
        </div>
      </header>
    </div>
  );
}

export default App;
