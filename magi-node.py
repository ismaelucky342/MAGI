#!/usr/bin/env python3
"""
🧙‍♂️ MAGI Node Agent - Ultra-Simple Distributed Monitoring
One file to rule them all. No dependencies hell.
"""

import http.server
import socketserver
import json
import os
import platform
import subprocess
import urllib.request
import urllib.parse
import threading
import socket
import time
import psutil
import time
import socket
from datetime import datetime

# Configuration
CONFIG = {
    "node_name": "UNKNOWN",
    "port": 8082,
    "network": "192.168.1.0/24",
    "other_nodes": [
        {"name": "GASPAR", "ip": "192.168.1.100", "port": 8080},
        {"name": "MELCHIOR", "ip": "192.168.1.101", "port": 8080},
        {"name": "BALTASAR", "ip": "192.168.1.102", "port": 8080}
    ]
}

class MAGIHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for MAGI requests"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/metrics':
            self.serve_metrics()
        elif self.path == '/api/nodes':
            self.serve_nodes()
        elif self.path == '/api/info':
            self.serve_info()
        elif self.path.startswith('/api/discover'):
            self.serve_discovery()
        else:
            super().do_GET()
    
    def serve_dashboard(self):
        """Serve the main MAGI dashboard"""
        html = self.get_dashboard_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_metrics(self):
        """Serve system metrics as JSON"""
        metrics = get_system_metrics()
        self.send_json(metrics)
    
    def serve_nodes(self):
        """Serve information about other nodes"""
        nodes = discover_nodes()
        self.send_json(nodes)
    
    def serve_info(self):
        """Serve node information"""
        info = {
            "node_name": CONFIG["node_name"],
            "timestamp": datetime.now().isoformat(),
            "uptime": get_uptime(),
            "platform": platform.platform(),
            "python_version": platform.python_version()
        }
        self.send_json(info)
    
    def serve_discovery(self):
        """Serve discovery information"""
        discovery = {
            "status": "active",
            "node_name": CONFIG["node_name"],
            "services": ["metrics", "monitoring", "terminal"],
            "version": "1.0.0"
        }
        self.send_json(discovery)
    
    def send_json(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def get_dashboard_html(self):
        """Generate the MAGI dashboard HTML"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧙‍♂️ MAGI - {CONFIG['node_name']}</title>
    <style>
        {self.get_magi_css()}
    </style>
</head>
<body>
    <div id="magi-system">
        <header class="magi-header">
            <div class="system-info">
                <div>FILE: MAGI_SYS</div>
                <div>NODE: {CONFIG['node_name']}</div>
                <div>STATUS: ACTIVE</div>
                <div>PORT: {CONFIG['port']}</div>
            </div>
            <div class="central-display">
                <div class="magi-title">🧙‍♂️ MAGI</div>
                <div class="subtitle">Distributed Node Monitoring System</div>
                <div class="node-badge">{CONFIG['node_name']}</div>
            </div>
            <div class="status-indicator">
                <div class="system-status online">OPERATIONAL</div>
                <div class="timestamp" id="timestamp"></div>
            </div>
        </header>
        
        <main class="dashboard-grid">
            <!-- Connection & Remote Access Panel -->
            <section class="panel connection-panel">
                <h3>🔗 Remote Connection</h3>
                <div class="connection-info">
                    <div class="connection-item">
                        <span class="label">SSH Access:</span>
                        <span class="value" id="ssh-status">Checking...</span>
                    </div>
                    <div class="connection-item">
                        <span class="label">Web Terminal:</span>
                        <button class="terminal-btn" onclick="openTerminal()">Open Terminal</button>
                    </div>
                    <div class="connection-item">
                        <span class="label">Network IP:</span>
                        <span class="value" id="network-ip">Loading...</span>
                    </div>
                </div>
            </section>

            <!-- System Metrics Panel -->
            <section class="panel metrics-panel">
                <h3>📊 System Metrics</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">CPU</div>
                        <div class="metric-value" id="cpu">--</div>
                        <div class="metric-bar">
                            <div class="metric-fill" id="cpu-bar"></div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">RAM</div>
                        <div class="metric-value" id="ram">--</div>
                        <div class="metric-bar">
                            <div class="metric-fill" id="ram-bar"></div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">DISK</div>
                        <div class="metric-value" id="disk">--</div>
                        <div class="metric-bar">
                            <div class="metric-fill" id="disk-bar"></div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">NETWORK</div>
                        <div class="metric-value" id="network">--</div>
                        <div class="metric-details" id="network-details">--</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">TEMP</div>
                        <div class="metric-value" id="temperature">--</div>
                        <div class="metric-details" id="temp-details">--</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">POWER</div>
                        <div class="metric-value power-state" id="power-state">--</div>
                        <div class="metric-details" id="power-details">--</div>
                    </div>
                </div>
            </section>

            <!-- Network Nodes Panel -->
            <section class="panel nodes-panel">
                <h3>🌐 Network Nodes</h3>
                <div id="nodes-container">
                    <!-- Nodes will be populated by JavaScript -->
                </div>
            </section>

            <!-- Services Panel -->
            <section class="panel services-panel">
                <h3>⚙️ Available Services</h3>
                <div id="services-container">
                    <div class="service-item">
                        <span class="service-name">Loading services...</span>
                    </div>
                </div>
            </section>
        </main>
        
        <footer class="terminal-section">
            <div class="terminal-header">
                <span>SYSTEM LOGS</span>
                <button class="terminal-toggle" onclick="toggleTerminal()">▼</button>
            </div>
            <div class="terminal-content" id="terminal">
                <div class="log-line system">🧙‍♂️ MAGI_TERMINAL v2.0.0</div>
                <div class="log-line">
                    <span class="prompt">&gt;</span>
                    <span>[{{timestamp}}] MAGI System initialized on {CONFIG['node_name']}</span>
                </div>
                <div class="log-line">
                    <span class="prompt">&gt;</span>
                    <span>[{{timestamp}}] Monitoring services active</span>
                </div>
                <div class="log-line">
                    <span class="prompt">&gt;</span>
                    <span>[{{timestamp}}] Starting real-time monitoring...</span>
                </div>
                <div class="log-line power-save" id="power-log" style="display: none;">
                    <span class="prompt">&gt;</span>
                    <span>[{{timestamp}}] Dashboard initialized</span>
                </div>
            </div>
        </footer>
    </div>
    
    <script>
        {self.get_magi_js()}
    </script>
</body>
</html>"""
    
    def get_magi_css(self):
        """Return enhanced MAGI CSS styling with new layout and color states"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background: #000;
            color: #ff3333;
            overflow-x: hidden;
            height: 100vh;
        }
        
        #magi-system {
            height: 100vh;
            display: flex;
            flex-direction: column;
            border: 3px solid #ff3333;
            box-shadow: 0 0 20px rgba(255, 51, 51, 0.5);
        }
        
        .magi-header {
            background: rgba(255, 51, 51, 0.1);
            border-bottom: 2px solid #ff3333;
            padding: 15px 20px;
            display: grid;
            grid-template-columns: 1fr 2fr 1fr;
            align-items: center;
            height: 80px;
        }
        
        .system-info {
            font-size: 12px;
            line-height: 1.3;
        }
        
        .central-display {
            text-align: center;
        }
        
        .magi-title {
            font-size: 28px;
            font-weight: bold;
            text-shadow: 0 0 20px #ff3333;
            margin-bottom: 5px;
        }
        
        .subtitle {
            font-size: 12px;
            opacity: 0.8;
        }
        
        .node-badge {
            background: rgba(255, 51, 51, 0.3);
            border: 1px solid #ff3333;
            padding: 5px 15px;
            margin-top: 5px;
            display: inline-block;
            font-weight: bold;
        }
        
        .status-indicator {
            text-align: right;
            font-size: 12px;
        }
        
        .system-status {
            background: rgba(0, 255, 0, 0.3);
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 5px 10px;
            margin-bottom: 5px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        /* New Dashboard Grid Layout */
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: auto 1fr auto;
            gap: 15px;
            padding: 15px;
            flex: 1;
            overflow: hidden;
        }
        
        .panel {
            background: rgba(255, 51, 51, 0.05);
            border: 1px solid #ff3333;
            padding: 15px;
            overflow-y: auto;
        }
        
        .panel h3 {
            border-bottom: 1px solid #ff3333;
            padding-bottom: 10px;
            margin-bottom: 15px;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* Connection Panel */
        .connection-panel {
            grid-column: 1;
            grid-row: 1;
        }
        
        .connection-info {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .connection-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            background: rgba(255, 51, 51, 0.1);
            border: 1px solid rgba(255, 51, 51, 0.3);
        }
        
        .terminal-btn {
            background: rgba(255, 51, 51, 0.2);
            border: 1px solid #ff3333;
            color: #ff3333;
            padding: 5px 10px;
            cursor: pointer;
            font-family: inherit;
            font-size: 12px;
        }
        
        .terminal-btn:hover {
            background: rgba(255, 51, 51, 0.4);
        }
        
        /* Metrics Panel */
        .metrics-panel {
            grid-column: 1 / -1;
            grid-row: 2;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .metric-card {
            padding: 15px;
            background: rgba(255, 51, 51, 0.1);
            border: 1px solid rgba(255, 51, 51, 0.3);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            border-color: #ff3333;
            box-shadow: 0 0 10px rgba(255, 51, 51, 0.3);
        }
        
        .metric-label {
            font-size: 12px;
            margin-bottom: 8px;
            opacity: 0.8;
        }
        
        .metric-value {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .metric-details {
            font-size: 10px;
            opacity: 0.7;
            margin-top: 5px;
        }
        
        .metric-bar {
            height: 8px;
            background: rgba(255, 51, 51, 0.2);
            border: 1px solid #ff3333;
            position: relative;
            margin-top: 8px;
        }
        
        .metric-fill {
            height: 100%;
            background: #ff3333;
            transition: width 0.5s ease;
        }
        
        /* Power State Colors */
        .power-state.normal { color: #00ff00; }
        .power-state.power_save { color: #ffff00; }
        .power-state.low_power { color: #ffff00; }
        .power-state.offline { color: #ff0000; }
        .power-state.error { color: #ff6600; }
        
        /* Nodes Panel */
        .nodes-panel {
            grid-column: 2;
            grid-row: 1 / 3;
        }
        
        .node-card {
            margin-bottom: 10px;
            padding: 12px;
            border: 2px solid;
            background: rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            position: relative;
        }
        
        /* Node Status Colors */
        .node-card.online {
            border-color: #00ff00;
            background: rgba(0, 255, 0, 0.1);
            color: #00ff00;
        }
        
        .node-card.offline {
            border-color: #ff0000;
            background: rgba(255, 0, 0, 0.1);
            color: #ff0000;
        }
        
        .node-card.power_save {
            border-color: #ffff00;
            background: rgba(255, 255, 0, 0.1);
            color: #ffff00;
        }
        
        .node-card.error {
            border-color: #ff6600;
            background: rgba(255, 102, 0, 0.1);
            color: #ff6600;
        }
        
        .node-card.current {
            border-color: #00ffff;
            background: rgba(0, 255, 255, 0.1);
            color: #00ffff;
        }
        
        .node-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .node-info {
            font-size: 11px;
            opacity: 0.8;
        }
        
        .node-status-badge {
            position: absolute;
            top: 5px;
            right: 5px;
            padding: 2px 6px;
            font-size: 9px;
            border: 1px solid;
            background: rgba(0, 0, 0, 0.7);
        }
        
        /* Services Panel */
        .services-panel {
            grid-column: 1 / -1;
            grid-row: 3;
            max-height: 200px;
        }
        
        .service-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            margin-bottom: 5px;
            background: rgba(255, 51, 51, 0.1);
            border: 1px solid rgba(255, 51, 51, 0.3);
        }
        
        .service-name {
            font-weight: bold;
        }
        
        .service-status {
            padding: 2px 8px;
            border: 1px solid;
            font-size: 10px;
        }
        
        .service-status.running {
            background: rgba(0, 255, 0, 0.2);
            border-color: #00ff00;
            color: #00ff00;
        }
        
        .service-url {
            color: #00ffff;
            text-decoration: none;
            font-size: 10px;
        }
        
        .service-url:hover {
            text-decoration: underline;
        }
        
        /* Terminal Section */
        .terminal-section {
            background: rgba(0, 0, 0, 0.8);
            border-top: 2px solid #ff3333;
            height: 150px;
            display: flex;
            flex-direction: column;
        }
        
        .terminal-header {
            background: rgba(255, 51, 51, 0.2);
            padding: 8px 15px;
            border-bottom: 1px solid #ff3333;
            font-size: 12px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .terminal-toggle {
            background: none;
            border: none;
            color: #ff3333;
            font-family: inherit;
            cursor: pointer;
            padding: 0 5px;
        }
        
        .terminal-content {
            flex: 1;
            padding: 10px 15px;
            overflow-y: auto;
            font-size: 11px;
            line-height: 1.4;
        }
        
        .log-line {
            margin-bottom: 3px;
            display: flex;
            align-items: center;
        }
        
        .log-line.system {
            color: #00ffff;
            font-weight: bold;
        }
        
        .log-line.power-save {
            color: #ffff00;
        }
        
        .prompt {
            color: #00ff00;
            margin-right: 8px;
        }
        
        /* Responsive Design */
        @media (max-width: 1200px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
                grid-template-rows: auto auto 1fr auto;
            }
            
            .connection-panel {
                grid-column: 1;
                grid-row: 1;
            }
            
            .nodes-panel {
                grid-column: 1;
                grid-row: 2;
            }
            
            .metrics-panel {
                grid-column: 1;
                grid-row: 3;
            }
            
            .services-panel {
                grid-column: 1;
                grid-row: 4;
            }
        }
        
        /* Scrollbar Styling */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255, 51, 51, 0.1);
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 51, 51, 0.5);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 51, 51, 0.8);
        }
        """
        
        .node-badge {
            background: rgba(255, 51, 51, 0.3);
            border: 1px solid #ff3333;
            padding: 5px 15px;
            margin-top: 5px;
            display: inline-block;
            font-weight: bold;
        }
        
        .status-indicator {
            text-align: right;
            font-size: 12px;
        }
        
        .system-status {
            background: rgba(0, 255, 0, 0.3);
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 5px 10px;
            margin-bottom: 5px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 20px;
            padding: 20px;
            flex: 1;
            overflow: hidden;
        }
        
        .metrics-panel, .nodes-panel {
            background: rgba(255, 51, 51, 0.05);
            border: 1px solid #ff3333;
            padding: 15px;
            overflow-y: auto;
        }
        
        .metrics-panel h3, .nodes-panel h3 {
            border-bottom: 1px solid #ff3333;
            padding-bottom: 10px;
            margin-bottom: 15px;
            font-size: 14px;
        }
        
        .metric-card {
            margin-bottom: 15px;
            padding: 10px;
            background: rgba(255, 51, 51, 0.1);
            border: 1px solid rgba(255, 51, 51, 0.3);
        }
        
        .metric-label {
            font-size: 12px;
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .metric-bar {
            height: 8px;
            background: rgba(255, 51, 51, 0.2);
            border: 1px solid #ff3333;
            position: relative;
        }
        
        .metric-fill {
            height: 100%;
            background: #ff3333;
            transition: width 0.5s ease;
        }
        
        .node-card {
            margin-bottom: 10px;
            padding: 10px;
            border: 1px solid #ff3333;
            background: rgba(255, 51, 51, 0.05);
            transition: all 0.3s ease;
        }
        
        .node-card.offline {
            border-color: #666;
            background: rgba(100, 100, 100, 0.1);
            color: #999;
        }
        
        .node-card.online {
            border-color: #00ff00;
            background: rgba(0, 255, 0, 0.1);
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
        }
        
        .node-card.self {
            border-color: #ffff00;
            background: rgba(255, 255, 0, 0.1);
            box-shadow: 0 0 15px rgba(255, 255, 0, 0.3);
        }
        
        .node-card.port_open {
            border-color: #ff9900;
            background: rgba(255, 153, 0, 0.1);
        }
        
        .node-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }
        
        .node-name {
            font-weight: bold;
            font-size: 14px;
        }
        
        .node-status {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 3px;
            background: rgba(0, 0, 0, 0.5);
        }
        
        .node-details {
            font-size: 11px;
            color: #ccc;
            line-height: 1.3;
        }
        
        .response-time {
            color: #00ff00;
        }
        
        .response-time.slow {
            color: #ff9900;
        }
        
        .response-time.timeout {
            color: #ff3333;
        }
        
        .terminal-section {
            background: #000;
            border-top: 2px solid #ff3333;
            height: 150px;
            display: flex;
            flex-direction: column;
        }
        
        .terminal-header {
            background: rgba(255, 51, 51, 0.1);
            padding: 8px 15px;
            border-bottom: 1px solid #ff3333;
            font-size: 12px;
            font-weight: bold;
        }
        
        .terminal-content {
            flex: 1;
            padding: 10px 15px;
            overflow-y: auto;
            font-size: 12px;
            line-height: 1.4;
        }
        
        .log-line {
            margin-bottom: 2px;
            display: flex;
            align-items: center;
        }
        
        .log-line.system {
            color: #00ff00;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .prompt {
            color: #00ff00;
            margin-right: 5px;
        }
        """
    
    def get_magi_js(self):
        """Return enhanced MAGI JavaScript code"""
        return """
        // MAGI Enhanced Dashboard JavaScript
        let metricsInterval;
        let nodesInterval;
        let servicesInterval;
        let terminalCollapsed = false;
        
        function updateTimestamp() {
            const now = new Date();
            document.getElementById('timestamp').textContent = now.toLocaleString();
        }
        
        async function fetchMetrics() {
            try {
                const response = await fetch('/api/metrics');
                const metrics = await response.json();
                
                // Basic metrics
                document.getElementById('cpu').textContent = metrics.cpu + '%';
                document.getElementById('ram').textContent = metrics.memory.percentage + '%';
                document.getElementById('disk').textContent = metrics.disk.percentage + '%';
                
                // Progress bars
                document.getElementById('cpu-bar').style.width = metrics.cpu + '%';
                document.getElementById('ram-bar').style.width = metrics.memory.percentage + '%';
                document.getElementById('disk-bar').style.width = metrics.disk.percentage + '%';
                
                // Network metrics
                if (metrics.network) {
                    const networkEl = document.getElementById('network');
                    const detailsEl = document.getElementById('network-details');
                    networkEl.textContent = (metrics.network.mb_recv + metrics.network.mb_sent).toFixed(1) + ' MB';
                    detailsEl.textContent = `↓${metrics.network.mb_recv}MB ↑${metrics.network.mb_sent}MB`;
                }
                
                // Temperature
                if (metrics.temperature) {
                    const tempEl = document.getElementById('temperature');
                    const tempDetailsEl = document.getElementById('temp-details');
                    
                    const temps = Object.values(metrics.temperature);
                    if (temps.length > 0) {
                        const avgTemp = temps.reduce((a, b) => a + (b.current || 0), 0) / temps.length;
                        tempEl.textContent = Math.round(avgTemp) + '°C';
                        tempDetailsEl.textContent = `${temps.length} sensors`;
                        
                        // Color code temperature
                        if (avgTemp > 75) tempEl.style.color = '#ff0000';
                        else if (avgTemp > 60) tempEl.style.color = '#ffff00';
                        else tempEl.style.color = '#00ff00';
                    }
                }
                
                // Power state
                if (metrics.power_state) {
                    const powerEl = document.getElementById('power-state');
                    const powerDetailsEl = document.getElementById('power-details');
                    
                    powerEl.textContent = metrics.power_state.toUpperCase();
                    powerEl.className = `metric-value power-state ${metrics.power_state}`;
                    
                    const stateDescriptions = {
                        'normal': 'Full Performance',
                        'power_save': 'Power Saving Mode',
                        'low_power': 'Low Power Mode'
                    };
                    powerDetailsEl.textContent = stateDescriptions[metrics.power_state] || 'Unknown';
                }
                
                // Update services
                updateServices(metrics.services);
                
                // Memory details
                if (metrics.memory.total_gb) {
                    document.getElementById('ram').title = `${metrics.memory.used_gb}GB / ${metrics.memory.total_gb}GB`;
                }
                
                // Disk details
                if (metrics.disk.total_gb) {
                    document.getElementById('disk').title = `${metrics.disk.used_gb}GB / ${metrics.disk.total_gb}GB`;
                }
                
            } catch (error) {
                console.error('Error fetching metrics:', error);
                addTerminalLog('❌ Error fetching system metrics', 'error');
            }
        }
        
        function updateServices(services) {
            const container = document.getElementById('services-container');
            if (!services || Object.keys(services).length === 0) {
                container.innerHTML = '<div class="service-item"><span class="service-name">No services detected</span></div>';
                return;
            }
            
            container.innerHTML = '';
            
            Object.entries(services).forEach(([name, service]) => {
                const serviceDiv = document.createElement('div');
                serviceDiv.className = 'service-item';
                
                let urlHtml = '';
                if (service.url) {
                    urlHtml = `<a href="${service.url}" target="_blank" class="service-url">Open</a>`;
                }
                
                serviceDiv.innerHTML = `
                    <span class="service-name">${name.toUpperCase()}</span>
                    <div>
                        <span class="service-status ${service.status}">${service.status}</span>
                        ${service.port ? `<span style="font-size: 10px; margin-left: 5px;">:${service.port}</span>` : ''}
                        ${urlHtml}
                    </div>
                `;
                
                container.appendChild(serviceDiv);
            });
        }
        
        async function fetchNodes() {
            try {
                const response = await fetch('/api/nodes');
                const nodes = await response.json();
                
                const container = document.getElementById('nodes-container');
                container.innerHTML = '';
                
                nodes.forEach(node => {
                    const nodeCard = document.createElement('div');
                    let statusClass = node.status;
                    if (node.self) statusClass = 'current';
                    
                    nodeCard.className = `node-card ${statusClass}`;
                    
                    let statusText = node.status.toUpperCase();
                    if (node.self) statusText = 'CURRENT';
                    
                    let responseTimeHtml = '';
                    if (node.response_time >= 0) {
                        let timeClass = 'response-time';
                        if (node.response_time > 1000) timeClass += ' slow';
                        if (node.response_time > 3000) timeClass += ' timeout';
                        responseTimeHtml = `<div class="node-info">⚡ ${node.response_time}ms</div>`;
                    }
                    
                    let powerStateHtml = '';
                    if (node.power_state && node.power_state !== 'normal') {
                        powerStateHtml = `<div class="node-info">🔋 ${node.power_state}</div>`;
                    }
                    
                    nodeCard.innerHTML = `
                        <div class="node-status-badge">${statusText}</div>
                        <div class="node-name">${node.name}</div>
                        <div class="node-info">${node.ip}:${node.port}</div>
                        ${responseTimeHtml}
                        ${powerStateHtml}
                        <div class="node-info">Last: ${node.last_seen}</div>
                    `;
                    
                    container.appendChild(nodeCard);
                });
                
            } catch (error) {
                console.error('Error fetching nodes:', error);
                addTerminalLog('❌ Error fetching network nodes', 'error');
            }
        }
        
        function addTerminalLog(message, type = 'info') {
            const terminal = document.getElementById('terminal');
            const logLine = document.createElement('div');
            logLine.className = `log-line ${type}`;
            
            const timestamp = new Date().toLocaleTimeString();
            logLine.innerHTML = `
                <span class="prompt">&gt;</span>
                <span>[${timestamp}] ${message}</span>
            `;
            
            terminal.appendChild(logLine);
            terminal.scrollTop = terminal.scrollHeight;
            
            // Keep only last 50 log lines
            const lines = terminal.querySelectorAll('.log-line');
            if (lines.length > 50) {
                lines[0].remove();
            }
        }
        
        function toggleTerminal() {
            const content = document.querySelector('.terminal-content');
            const button = document.querySelector('.terminal-toggle');
            
            terminalCollapsed = !terminalCollapsed;
            
            if (terminalCollapsed) {
                content.style.display = 'none';
                button.textContent = '▲';
            } else {
                content.style.display = 'block';
                button.textContent = '▼';
            }
        }
        
        function openTerminal() {
            // For now, just add a log entry
            addTerminalLog('Terminal access requested - feature coming soon', 'info');
        }
        
        async function checkNetworkInfo() {
            try {
                // Get network IP (simplified)
                const ipEl = document.getElementById('network-ip');
                ipEl.textContent = window.location.hostname || 'localhost';
                
                // Check SSH status (simplified)
                const sshEl = document.getElementById('ssh-status');
                sshEl.textContent = 'Port 22';
                sshEl.style.color = '#ffff00'; // Assume available but unchecked
                
            } catch (error) {
                console.error('Error checking network info:', error);
            }
        }
        
        function startMonitoring() {
            updateTimestamp();
            checkNetworkInfo();
            
            // Initial fetch
            fetchMetrics();
            fetchNodes();
            
            // Set up intervals
            metricsInterval = setInterval(fetchMetrics, 5000);  // 5 seconds
            nodesInterval = setInterval(fetchNodes, 6000);      // 6 seconds
            
            // Update timestamp every second
            setInterval(updateTimestamp, 1000);
            
            // Add startup logs
            setTimeout(() => addTerminalLog('🧙‍♂️ Dashboard initialized'), 500);
            setTimeout(() => addTerminalLog('📡 Starting real-time monitoring...'), 1000);
            setTimeout(() => addTerminalLog('🌐 Network discovery active'), 1500);
        }
        
        function stopMonitoring() {
            if (metricsInterval) clearInterval(metricsInterval);
            if (nodesInterval) clearInterval(nodesInterval);
            if (servicesInterval) clearInterval(servicesInterval);
        }
        
        // Start monitoring when page loads
        document.addEventListener('DOMContentLoaded', startMonitoring);
        
        // Stop monitoring when page unloads
        window.addEventListener('beforeunload', stopMonitoring);
        """
                        ${responseTimeHtml}`;
                    
                    if (node.version) {
                        detailsHtml += `<div>🐍 Python ${node.version}</div>`;
                    }
                    
                    if (node.uptime && node.uptime !== 'unknown') {
                        detailsHtml += `<div>⏰ Uptime: ${node.uptime}</div>`;
                    }
                    
                    if (node.last_seen && node.last_seen !== 'never') {
                        const lastSeen = new Date(node.last_seen).toLocaleTimeString();
                        detailsHtml += `<div>👁️ Last: ${lastSeen}</div>`;
                    }
                    
                    detailsHtml += '</div>';
                    
                    nodeCard.innerHTML = `
                        <div class="node-header">
                            <div class="node-name">${node.name}</div>
                            <div class="node-status">${statusText}</div>
                        </div>
                        ${detailsHtml}
                    `;
                    container.appendChild(nodeCard);
                });
                
            } catch (error) {
                console.error('Error fetching nodes:', error);
                addLogLine('Failed to fetch node status');
            }
        }
        
        function addLogLine(message) {
            const terminal = document.getElementById('terminal');
            const logLine = document.createElement('div');
            logLine.className = 'log-line';
            logLine.innerHTML = `
                <span class="prompt">&gt;</span>
                <span>[${new Date().toLocaleTimeString()}] ${message}</span>
            `;
            terminal.appendChild(logLine);
            terminal.scrollTop = terminal.scrollHeight;
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            updateTimestamp();
            setInterval(updateTimestamp, 1000);
            
            fetchMetrics();
            metricsInterval = setInterval(fetchMetrics, 3000);
            
            fetchNodes();
            nodesInterval = setInterval(fetchNodes, 5000);
            
            addLogLine('Dashboard initialized');
            addLogLine('Starting real-time monitoring...');
        });
        """

def get_system_metrics():
    """Get enhanced system metrics including network, temperature, power state and services"""
    import psutil
    import time
    import glob
    import subprocess
    
    try:
        # CPU usage (average over 1 second)
        cpu_usage = int(psutil.cpu_percent(interval=1))
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_used = memory.used
        memory_total = memory.total
        memory_percentage = int(memory.percent)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percentage = int((disk.used / disk.total) * 100)
        
        # Network stats with speed calculation
        net_io = psutil.net_io_counters()
        network_usage = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "mb_sent": round(net_io.bytes_sent / (1024*1024), 2),
            "mb_recv": round(net_io.bytes_recv / (1024*1024), 2)
        }
        
        # Temperature monitoring
        temperatures = {}
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                for name, entries in temps.items():
                    for entry in entries:
                        temp_name = f"{name}_{entry.label}" if entry.label else name
                        temperatures[temp_name] = {
                            "current": entry.current,
                            "high": entry.high,
                            "critical": entry.critical
                        }
        except:
            # Fallback para sistemas sin sensores
            try:
                temp_files = glob.glob('/sys/class/thermal/thermal_zone*/temp')
                for i, temp_file in enumerate(temp_files):
                    with open(temp_file, 'r') as f:
                        temp_c = int(f.read().strip()) / 1000
                        temperatures[f"thermal_zone_{i}"] = {
                            "current": temp_c,
                            "high": 75,
                            "critical": 85
                        }
            except:
                temperatures["cpu"] = {"current": 45, "high": 75, "critical": 85}
        
        # Power management state detection
        power_state = "normal"
        try:
            # Check for power saving indicators
            cpu_freq = psutil.cpu_freq()
            if cpu_freq and cpu_freq.current < cpu_freq.max * 0.7:
                power_state = "power_save"
            
            # Check system load
            load_avg = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
            if load_avg < 0.5:
                power_state = "low_power"
        except:
            pass
        
        # Process count and services
        process_count = len(psutil.pids())
        
        # Detect running services
        services = detect_services()
        
        # Boot time / uptime
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        uptime_hours = int(uptime_seconds / 3600)
        
        return {
            "cpu": cpu_usage,
            "memory": {
                "used": memory_used,
                "total": memory_total,
                "percentage": memory_percentage,
                "available": memory.available,
                "used_gb": round(memory_used / (1024**3), 2),
                "total_gb": round(memory_total / (1024**3), 2)
            },
            "disk": {
                "used": disk.used,
                "total": disk.total,
                "percentage": disk_percentage,
                "free": disk.free,
                "used_gb": round(disk.used / (1024**3), 2),
                "total_gb": round(disk.total / (1024**3), 2)
            },
            "network": network_usage,
            "temperature": temperatures,
            "power_state": power_state,
            "services": services,
            "system": {
                "processes": process_count,
                "uptime_hours": uptime_hours,
                "boot_time": boot_time,
                "platform": platform.platform()
            },
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "node_status": "online"
        }
    except ImportError:
        # Fallback if psutil not available
        return get_system_metrics_fallback()
    except Exception as e:
        print(f"Error getting metrics: {e}")
        return get_system_metrics_fallback()

def detect_services():
    """Detect common services running on the system"""
    services = {}
    common_services = {
        "nextcloud": ["nginx", "apache2", "nextcloud"],
        "jellyfin": ["jellyfin"],
        "plex": ["plexmediaserver", "plex"],
        "docker": ["docker", "dockerd"],
        "ssh": ["sshd", "ssh"],
        "web": ["nginx", "apache2", "httpd"],
        "database": ["mysql", "postgresql", "mariadb"],
        "samba": ["smbd", "nmbd"],
        "ftp": ["vsftpd", "proftpd"],
        "vpn": ["openvpn", "wireguard"]
    }
    
    try:
        # Get running processes
        running_processes = [p.name().lower() for p in psutil.process_iter(['name'])]
        
        for service_name, process_names in common_services.items():
            service_running = any(proc in running_processes for proc in process_names)
            if service_running:
                # Try to get port info
                port = get_service_port(service_name)
                services[service_name] = {
                    "status": "running",
                    "port": port,
                    "url": f"http://localhost:{port}" if port else None
                }
    except Exception as e:
        print(f"Error detecting services: {e}")
    
    return services

def get_service_port(service_name):
    """Get default port for common services"""
    default_ports = {
        "nextcloud": 80,
        "jellyfin": 8096,
        "plex": 32400,
        "ssh": 22,
        "web": 80,
        "samba": 445,
        "ftp": 21
    }
    return default_ports.get(service_name)
    except ImportError:
        # Fallback if psutil not available - try manual methods
        return get_system_metrics_fallback()
    except Exception as e:
        print(f"Error getting metrics: {e}")
        return get_system_metrics_fallback()

def get_system_metrics_fallback():
    """Fallback system metrics without psutil"""
    try:
        # CPU usage - try different methods
        cpu_usage = 0
        try:
            # Linux method
            with open('/proc/loadavg', 'r') as f:
                load_avg = float(f.read().split()[0])
                cpu_usage = min(int(load_avg * 100), 100)
        except:
            try:
                # Alternative method using top
                result = subprocess.run(['top', '-bn1'], capture_output=True, text=True, timeout=3)
                for line in result.stdout.split('\n'):
                    if 'Cpu(s)' in line:
                        # Extract CPU usage from top output
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if '%us' in part:
                                cpu_usage = int(float(part.replace('%us,', '')))
                                break
                        break
            except:
                cpu_usage = 25  # Default fallback
        
        # Memory usage
        memory_total = 8000000000  # Default 8GB
        memory_used = 4000000000   # Default 4GB used
        memory_percentage = 50
        
        try:
            # Linux method
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                for line in meminfo.split('\n'):
                    if 'MemTotal:' in line:
                        memory_total = int(line.split()[1]) * 1024
                    elif 'MemAvailable:' in line:
                        memory_available = int(line.split()[1]) * 1024
                        memory_used = memory_total - memory_available
                        memory_percentage = int((memory_used / memory_total) * 100)
        except:
            pass
        
        # Disk usage
        disk_percentage = 35
        disk_total = 500000000000  # Default 500GB
        disk_used = 175000000000   # Default 175GB used
        
        try:
            # Try df command
            result = subprocess.run(['df', '/'], capture_output=True, text=True, timeout=3)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    disk_total = int(parts[1]) * 1024
                    disk_used = int(parts[2]) * 1024
                    disk_percentage = int(parts[4].replace('%', ''))
        except:
            pass
        
        return {
            "cpu": cpu_usage,
            "memory": {
                "used": memory_used,
                "total": memory_total,
                "percentage": memory_percentage,
                "available": memory_total - memory_used
            },
            "disk": {
                "used": disk_used,
                "total": disk_total,
                "percentage": disk_percentage,
                "free": disk_total - disk_used
            },
            "network": {
                "bytes_sent": 0,
                "bytes_recv": 0,
                "packets_sent": 0,
                "packets_recv": 0
            },
            "system": {
                "processes": 200,
                "uptime_hours": 24,
                "boot_time": time.time() - 86400
            },
            "timestamp": datetime.now().isoformat(),
            "node_status": "online"
        }
    except Exception as e:
        print(f"Fallback metrics error: {e}")
        return {
            "cpu": 0,
            "memory": {"used": 0, "total": 1, "percentage": 0, "available": 1},
            "disk": {"used": 0, "total": 1, "percentage": 0, "free": 1},
            "network": {"bytes_sent": 0, "bytes_recv": 0, "packets_sent": 0, "packets_recv": 0},
            "system": {"processes": 0, "uptime_hours": 0, "boot_time": 0},
            "timestamp": datetime.now().isoformat(),
            "node_status": "error"
        }

def get_uptime():
    """Get system uptime"""
    try:
        if platform.system() == "Windows":
            uptime_result = subprocess.run(['systeminfo'], capture_output=True, text=True)
            # Parse Windows systeminfo output
            return "Unknown (Windows)"
        else:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                uptime_hours = int(uptime_seconds / 3600)
                return f"{uptime_hours} hours"
    except:
        return "Unknown"

def discover_nodes():
    """Discover other MAGI nodes on the network with power state detection"""
    nodes = []
    current_node = CONFIG["node_name"]
    current_port = CONFIG["port"]
    
    for node_config in CONFIG["other_nodes"]:
        node_name = node_config["name"]
        node_ip = node_config["ip"]
        node_port = node_config["port"]
        
        # Skip self
        if node_name == current_node:
            # Get current node power state
            try:
                metrics = get_system_metrics()
                power_state = metrics.get("power_state", "normal")
                node_status = "power_save" if power_state in ["power_save", "low_power"] else "online"
            except:
                node_status = "online"
                
            nodes.append({
                "name": node_name,
                "ip": "localhost",
                "port": current_port,
                "status": node_status,
                "response_time": 0,
                "self": True,
                "last_seen": time.strftime("%Y-%m-%d %H:%M:%S"),
                "power_state": power_state if 'power_state' in locals() else "normal"
            })
            continue
        
        # Test connection to other nodes
        try:
            import socket
            start_time = time.time()
            
            # Try to connect to the node
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)  # 2 second timeout
            result = sock.connect_ex((node_ip, node_port))
            sock.close()
            
            response_time = int((time.time() - start_time) * 1000)  # milliseconds
            
            if result == 0:
                # Port is open, try to get node info and metrics
                try:
                    # Get basic info
                    url = f"http://{node_ip}:{node_port}/api/info"
                    req = urllib.request.Request(url, headers={'User-Agent': 'MAGI-Discovery'})
                    
                    with urllib.request.urlopen(req, timeout=3) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode())
                            
                            # Try to get metrics for power state
                            node_status = "online"
                            power_state = "normal"
                            try:
                                metrics_url = f"http://{node_ip}:{node_port}/api/metrics"
                                metrics_req = urllib.request.Request(metrics_url, headers={'User-Agent': 'MAGI-Discovery'})
                                with urllib.request.urlopen(metrics_req, timeout=2) as metrics_response:
                                    if metrics_response.status == 200:
                                        metrics_data = json.loads(metrics_response.read().decode())
                                        power_state = metrics_data.get("power_state", "normal")
                                        if power_state in ["power_save", "low_power"]:
                                            node_status = "power_save"
                            except:
                                pass
                                
                            nodes.append({
                                "name": node_name,
                                "ip": node_ip,
                                "port": node_port,
                                "status": node_status,
                                "response_time": response_time,
                                "self": False,
                                "last_seen": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "version": data.get("python_version", "unknown"),
                                "uptime": data.get("uptime", "unknown"),
                                "power_state": power_state
                            })
                        else:
                            raise Exception(f"HTTP {response.status}")
                except Exception as e:
                    # Port open but not MAGI service
                    nodes.append({
                        "name": node_name,
                        "ip": node_ip,
                        "port": node_port,
                        "status": "port_open",
                        "response_time": response_time,
                        "self": False,
                        "last_seen": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "error": str(e),
                        "power_state": "unknown"
                    })
            else:
                # Port closed/unreachable
                nodes.append({
                    "name": node_name,
                    "ip": node_ip,
                    "port": node_port,
                    "status": "offline",
                    "response_time": -1,
                    "self": False,
                    "last_seen": "never",
                    "error": "connection_refused",
                    "power_state": "offline"
                })
                
        except Exception as e:
            nodes.append({
                "name": node_name,
                "ip": node_ip,
                "port": node_port,
                "status": "error",
                "response_time": -1,
                "self": False,
                "last_seen": "never",
                "error": str(e),
                "power_state": "error"
            })
    
    return nodes

def setup_node():
    """Setup node configuration"""
    import sys
    
    if len(sys.argv) > 1:
        node_name = sys.argv[1].upper()
        if node_name in ["GASPAR", "MELCHIOR", "BALTASAR"]:
            CONFIG["node_name"] = node_name
            print(f"🧙‍♂️ MAGI Node '{node_name}' configured")
    
    if CONFIG["node_name"] == "UNKNOWN":
        CONFIG["node_name"] = input("Enter node name (GASPAR/MELCHIOR/BALTASAR): ").upper()

def main():
    """Main MAGI function"""
    print("🧙‍♂️ MAGI - Ultra-Simple Distributed Monitoring")
    print("=" * 50)
    
    setup_node()
    
    print(f"Node: {CONFIG['node_name']}")
    print(f"Port: {CONFIG['port']}")
    print(f"Platform: {platform.platform()}")
    print(f"Python: {platform.python_version()}")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("", CONFIG["port"]), MAGIHandler) as httpd:
            print(f"🚀 MAGI {CONFIG['node_name']} server started")
            print(f"📡 Access dashboard: http://localhost:{CONFIG['port']}")
            print(f"🌐 Network access: http://[your-ip]:{CONFIG['port']}")
            print("Press Ctrl+C to stop")
            print("=" * 50)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 MAGI {CONFIG['node_name']} server stopped")
    except Exception as e:
        print(f"❌ Error starting MAGI server: {e}")

if __name__ == "__main__":
    main()
