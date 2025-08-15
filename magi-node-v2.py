#!/usr/bin/env python3
"""
🧙‍♂️ MAGI Node Agent - Ultra-Simple Distributed Monitoring v2.0
Enhanced with power management, services detection, and improved interface
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
import hashlib
import secrets
import base64
from http.cookies import SimpleCookie

# Configuration
CONFIG = {
    "node_name": "UNKNOWN",
    "port": 8080,
    "bind_address": "0.0.0.0",
    # If require_api_key is true, clients must present Authorization: Bearer <API_KEY>
    "require_api_key": False,
    "api_key": "changeme",
    # Web UI authentication
    "require_login": True,
    "login_users": {
        "admin": "changeme"  # Will be set during installation
    },
    "session_timeout": 3600,  # 1 hour
    "other_nodes": [
        {"name": "GASPAR", "ip": "127.0.0.1", "port": 8080},
        {"name": "MELCHIOR", "ip": "127.0.0.1", "port": 8081},
        {"name": "BALTASAR", "ip": "127.0.0.1", "port": 8082}
    ]
}

# Session management
ACTIVE_SESSIONS = {}
SESSION_CLEANUP_INTERVAL = 300  # 5 minutes

def cleanup_expired_sessions():
    """Clean up expired sessions"""
    current_time = time.time()
    timeout = CONFIG.get('session_timeout', 3600)
    
    expired_sessions = []
    for session_id, session in ACTIVE_SESSIONS.items():
        if current_time - session['last_access'] > timeout:
            expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        del ACTIVE_SESSIONS[session_id]
    
    if expired_sessions:
        print(f"Cleaned up {len(expired_sessions)} expired sessions")

def start_session_cleanup():
    """Start background session cleanup"""
    cleanup_expired_sessions()
    threading.Timer(SESSION_CLEANUP_INTERVAL, start_session_cleanup).start()

class MAGIHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle HTTP GET requests"""
        # Check web UI authentication for main page
        if self.path == "/" or self.path.startswith('/dashboard'):
            if CONFIG.get('require_login') and not self.check_session():
                self.serve_login_page()
                return
                
        # Enforce API auth for /api/ endpoints if enabled
        if CONFIG.get('require_api_key') and self.path.startswith('/api'):
            if not self.check_api_auth():
                return
                
        if self.path == "/":
            self.serve_main_page()
        elif self.path == "/login":
            self.serve_login_page()
        elif self.path == "/logout":
            self.handle_logout()
        elif self.path == "/api/metrics":
            self.serve_metrics()
        elif self.path == "/api/all-metrics":
            self.serve_all_metrics()
        elif self.path == "/api/stream":
            self.serve_stream()
        elif self.path == "/api/nodes":
            self.serve_nodes()
        elif self.path == "/api/services":
            self.serve_all_services()
        elif self.path == "/api/info":
            self.serve_info()
        elif self.path.startswith("/images/"):
            self.serve_image()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle HTTP POST requests for system control"""
        # Handle login requests
        if self.path == '/login':
            self.handle_login()
            return
            
        # Check web UI authentication for control endpoints
        if CONFIG.get('require_login') and not self.check_session():
            self.send_error(401, "Login required")
            return
            
        # Enforce API auth for POST endpoints if enabled
        if CONFIG.get('require_api_key') and self.path.startswith('/api'):
            if not self.check_api_auth():
                return
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return
        
        if self.path == '/api/power/mode':
            mode = data.get('mode')
            if mode:
                result = change_power_mode(mode)
                self.send_json(result)
            else:
                self.send_json({"status": "error", "message": "Power mode not specified"})
        
        elif self.path == '/api/system/shutdown':
            delay = data.get('delay', 60)  # default 60 seconds
            result = schedule_system_shutdown(delay)
            self.send_json(result)
        
        elif self.path == '/api/system/reboot':
            delay = data.get('delay', 60)  # default 60 seconds  
            result = schedule_system_reboot(delay)
            self.send_json(result)
        
        elif self.path == '/api/system/sleep':
            result = system_sleep()
            self.send_json(result)
        
        else:
            self.send_error(404, "Not Found")

    def check_api_auth(self):
        """Validate Authorization header when API key enforcement is enabled."""
        auth = self.headers.get('Authorization') or self.headers.get('authorization')
        if not auth:
            self.send_error(401, "Unauthorized: missing Authorization header")
            return False

        # Expect header 'Authorization: Bearer <key>'
        parts = auth.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            self.send_error(401, "Unauthorized: invalid Authorization format")
            return False

        token = parts[1]
        if token != CONFIG.get('api_key'):
            self.send_error(403, "Forbidden: invalid API key")
            return False

        return True
    
    def check_session(self):
        """Check if user has valid session"""
        if not CONFIG.get('require_login'):
            return True
            
        cookies = SimpleCookie(self.headers.get('Cookie', ''))
        session_id = cookies.get('magi_session')
        
        if not session_id:
            return False
            
        session_id = session_id.value
        session = ACTIVE_SESSIONS.get(session_id)
        
        if not session:
            return False
            
        # Check session timeout
        if time.time() - session['created'] > CONFIG.get('session_timeout', 3600):
            del ACTIVE_SESSIONS[session_id]
            return False
            
        # Update last access
        session['last_access'] = time.time()
        return True
    
    def create_session(self, username):
        """Create new session for user"""
        session_id = secrets.token_hex(32)
        ACTIVE_SESSIONS[session_id] = {
            'username': username,
            'created': time.time(),
            'last_access': time.time()
        }
        return session_id
    
    def handle_login(self):
        """Handle login form submission"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse form data
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]
            
            # Validate credentials
            users = CONFIG.get('login_users', {})
            if username in users and users[username] == password:
                # Create session
                session_id = self.create_session(username)
                
                # Redirect to dashboard with session cookie
                self.send_response(302)
                self.send_header('Location', '/')
                self.send_header('Set-Cookie', f'magi_session={session_id}; Path=/; HttpOnly; SameSite=Strict')
                self.end_headers()
            else:
                # Invalid credentials - show login page with error
                self.serve_login_page(error="Invalid username or password")
        except Exception as e:
            print(f"Login error: {e}")
            self.send_error(500, "Login error")
    
    def handle_logout(self):
        """Handle logout request"""
        cookies = SimpleCookie(self.headers.get('Cookie', ''))
        session_id = cookies.get('magi_session')
        
        if session_id:
            session_id = session_id.value
            if session_id in ACTIVE_SESSIONS:
                del ACTIVE_SESSIONS[session_id]
        
        # Redirect to login with expired cookie
        self.send_response(302)
        self.send_header('Location', '/login')
        self.send_header('Set-Cookie', 'magi_session=; Path=/; HttpOnly; SameSite=Strict; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
        self.end_headers()
    
    def serve_login_page(self, error=None):
        """Serve the login page"""
        error_html = f'<div class="error-message">{error}</div>' if error else ''
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>MAGI Login - {CONFIG['node_name']}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        {self.get_login_css()}
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-box">
            <div class="logo-section">
                <img src="/images/MAGI.png" alt="MAGI" class="login-logo" onerror="this.style.display='none'">
                <h1>MAGI LOGIN</h1>
                <p>Node: {CONFIG['node_name']}</p>
            </div>
            {error_html}
            <form method="POST" action="/login" class="login-form">
                <div class="input-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required autocomplete="username">
                </div>
                <div class="input-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required autocomplete="current-password">
                </div>
                <button type="submit" class="login-btn">ACCESS SYSTEM</button>
            </form>
            <div class="footer">
                <p>🔒 Secure Access Required</p>
                <p>MAGI v2.0 - Enhanced Distributed Monitoring</p>
            </div>
        </div>
    </div>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def get_login_css(self):
        """CSS for login page"""
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
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        
        .login-container {
            width: 100%;
            max-width: 400px;
            padding: 20px;
        }
        
        .login-box {
            background: rgba(255, 51, 51, 0.1);
            border: 2px solid #ff3333;
            border-radius: 8px;
            padding: 40px 30px;
            box-shadow: 0 0 30px rgba(255, 51, 51, 0.5);
            text-align: center;
        }
        
        .logo-section {
            margin-bottom: 30px;
        }
        
        .login-logo {
            height: 60px;
            margin-bottom: 15px;
            filter: drop-shadow(0 0 15px rgba(255, 51, 51, 0.8));
        }
        
        .logo-section h1 {
            font-size: 28px;
            font-weight: bold;
            text-shadow: 0 0 20px #ff3333;
            margin-bottom: 10px;
        }
        
        .logo-section p {
            font-size: 14px;
            opacity: 0.8;
            color: #00ff00;
        }
        
        .error-message {
            background: rgba(255, 0, 0, 0.2);
            border: 1px solid #ff0000;
            color: #ff0000;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .login-form {
            text-align: left;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        .input-group label {
            display: block;
            margin-bottom: 5px;
            font-size: 14px;
            color: #ff3333;
        }
        
        .input-group input {
            width: 100%;
            padding: 12px;
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid #ff3333;
            border-radius: 4px;
            color: #fff;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        
        .input-group input:focus {
            outline: none;
            border-color: #00ff00;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
        }
        
        .login-btn {
            width: 100%;
            padding: 15px;
            background: rgba(255, 51, 51, 0.2);
            border: 2px solid #ff3333;
            border-radius: 4px;
            color: #ff3333;
            font-family: 'Courier New', monospace;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .login-btn:hover {
            background: rgba(255, 51, 51, 0.3);
            color: #fff;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 51, 51, 0.4);
        }
        
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 51, 51, 0.3);
        }
        
        .footer p {
            font-size: 12px;
            opacity: 0.7;
            margin-bottom: 5px;
        }
        """
    
    def serve_main_page(self):
        """Serve the main MAGI dashboard"""
        html = self.get_magi_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_metrics(self):
        """Serve system metrics as JSON"""
        try:
            metrics = get_system_metrics()
        except Exception:
            metrics = get_system_metrics_fallback()
        self.send_json(metrics)
    
    def serve_all_metrics(self):
        """Serve aggregated metrics from all nodes as JSON"""
        try:
            all_metrics = gather_all_metrics()
            self.send_json(all_metrics)
        except Exception as e:
            self.send_error(500, f"Error gathering all metrics: {e}")
    
    def serve_stream(self):
        """Serve Server-Sent Events stream for real-time metrics"""
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Send initial data
            all_metrics = gather_all_metrics()
            data = json.dumps(all_metrics)
            self.wfile.write(f"data: {data}\n\n".encode('utf-8'))
            self.wfile.flush()
            
        except Exception as e:
            print(f"SSE stream error: {e}")
            self.send_error(500, f"Stream error: {e}")
    
    def create_simulated_metrics(self, node_name):
        """Create simulated metrics for demo purposes"""
        import random
        
        # Create realistic but fake metrics
        base_cpu = 20 if node_name == 'GASPAR' else 35 if node_name == 'MELCHIOR' else 50
        base_mem = 45 if node_name == 'GASPAR' else 60 if node_name == 'MELCHIOR' else 75
        
        return {
            "cpu": base_cpu + random.randint(-10, 15),
            "memory": {
                "percentage": base_mem + random.randint(-5, 10),
                "used": f"{random.randint(2, 8)} GB",
                "total": "16 GB"
            },
            "disk": {
                "percentage": random.randint(30, 80),
                "used": f"{random.randint(100, 800)} GB", 
                "total": "1 TB"
            },
            "network": {
                "upload": f"{random.randint(10, 100)} MB/s",
                "download": f"{random.randint(20, 200)} MB/s"
            },
            "temperature": {
                "CPU": {"current": random.randint(45, 75)},
                "GPU": {"current": random.randint(40, 85)}
            },
            "power_state": "normal",
            "services_count": random.randint(5, 15)
        }
    
    def serve_nodes(self):
        """Serve nodes discovery data"""
        try:
            nodes = discover_nodes()
            self.send_json(nodes)
        except Exception as e:
            self.send_error(500, f"Error discovering nodes: {e}")
    
    def serve_all_services(self):
        """Serve comprehensive services from all nodes"""
        try:
            all_services = {}
            nodes = discover_nodes()
            
            for node in nodes:
                node_name = node["name"]
                node_services = node.get("services", {})
                
                # Añadir información del nodo a cada servicio
                for service_name, service_info in node_services.items():
                    service_key = f"{service_name}@{node_name}"
                    all_services[service_key] = {
                        **service_info,
                        "node": node_name,
                        "node_ip": node["ip"],
                        "node_status": node["status"]
                    }
            
            self.send_json(all_services)
        except Exception as e:
            self.send_error(500, f"Error getting services: {e}")
    
    def handle_power_mode(self):
        """Handle power mode change requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            mode = data.get('mode', 'normal')
            result = change_power_mode(mode)
            
            self.send_json(result)
        except Exception as e:
            self.send_error(500, f"Error changing power mode: {e}")
    
    def handle_system_shutdown(self):
        """Handle system shutdown requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            delay = data.get('delay', 60)  # 60 seconds default
            result = schedule_system_shutdown(delay)
            
            self.send_json(result)
        except Exception as e:
            self.send_error(500, f"Error scheduling shutdown: {e}")
    
    def handle_system_reboot(self):
        """Handle system reboot requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            delay = data.get('delay', 60)  # 60 seconds default
            result = schedule_system_reboot(delay)
            
            self.send_json(result)
        except Exception as e:
            self.send_error(500, f"Error scheduling reboot: {e}")
    
    def handle_system_sleep(self):
        """Handle system sleep/suspend requests"""
        try:
            result = system_sleep()
            self.send_json(result)
        except Exception as e:
            self.send_error(500, f"Error putting system to sleep: {e}")
    
    def serve_info(self):
        """Serve node info as JSON"""
        info = {
            "node_name": CONFIG["node_name"],
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "uptime": "unknown"
        }
        self.send_json(info)
    
    def serve_image(self):
        """Serve images from the images directory"""
        try:
            # Extract filename from path
            filename = self.path.split('/')[-1]
            image_path = os.path.join(os.path.dirname(__file__), "images", filename)
            
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                # Determine content type
                if filename.endswith('.png'):
                    content_type = 'image/png'
                elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
                    content_type = 'image/jpeg'
                elif filename.endswith('.svg'):
                    content_type = 'image/svg+xml'
                else:
                    content_type = 'application/octet-stream'
                
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.send_header('Content-length', len(image_data))
                self.end_headers()
                self.wfile.write(image_data)
            else:
                self.send_error(404, "Image not found")
        except Exception as e:
            print(f"Error serving image: {e}")
            self.send_error(500, "Internal server error")
    
    def send_json(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def get_magi_html(self):
        """Generate complete MAGI HTML page"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>MAGI - {CONFIG['node_name']}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
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
                <div class="magi-title"><img src="/images/MAGI.png" alt="MAGI" class="magi-logo"></div>
                <div class="subtitle">Distributed Node Monitoring System</div>
            </div>
            <div class="status-indicator">
                <div class="system-status online">OPERATIONAL</div>
                <div class="timestamp" id="timestamp"></div>
                <button class="logout-btn" onclick="logout()">🔓 LOGOUT</button>
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
                        <span class="label">Network IP:</span>
                        <span class="value" id="network-ip">Loading...</span>
                    </div>
                </div>
            </section>

            <!-- System Metrics Panel -->
            <section class="panel metrics-panel">
                <h3>📊 Multi-Node System Metrics</h3>
                <div id="all-metrics-container">
                    <!-- Metrics for all nodes will be loaded here -->
                    <div class="loading-message">Loading multi-node metrics...</div>
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
                <div class="log-line system">⚡ MAGI_TERMINAL v2.0.0</div>
                <div class="log-line">
                    <span class="prompt">&gt;</span>
                    <span>[{time.strftime("%H:%M:%S")}] MAGI System initialized on {CONFIG['node_name']}</span>
                </div>
                <div class="log-line">
                    <span class="prompt">&gt;</span>
                    <span>[{time.strftime("%H:%M:%S")}] Enhanced monitoring active</span>
                </div>
                <div class="log-line">
                    <span class="prompt">&gt;</span>
                    <span>[{time.strftime("%H:%M:%S")}] Power management enabled</span>
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
        """Enhanced MAGI CSS with new layout and power states"""
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
        
        .system-info, .status-indicator {
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
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .magi-logo {
            height: 40px;
            width: auto;
            filter: drop-shadow(0 0 15px rgba(255, 51, 51, 0.8));
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
        }
        
        .logout-btn {
            background: rgba(255, 51, 51, 0.2);
            border: 1px solid #ff3333;
            color: #ff3333;
            padding: 5px 10px;
            margin-top: 5px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-size: 10px;
            border-radius: 3px;
            transition: all 0.3s ease;
        }
        
        .logout-btn:hover {
            background: rgba(255, 51, 51, 0.4);
            color: #fff;
            transform: translateY(-1px);
        }
        
        .system-status.online {
            background: rgba(0, 255, 0, 0.3);
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 5px 10px;
            margin-bottom: 5px;
        }
        
        /* Dashboard Grid Layout */
        .dashboard-grid {
            display: grid;
            grid-template-columns: 300px 1fr 280px;
            grid-template-rows: auto 1fr;
            gap: 15px;
            padding: 15px;
            flex: 1;
            overflow: hidden;
            min-height: 0;
        }
        
        .panel {
            background: rgba(255, 51, 51, 0.05);
            border: 1px solid #ff3333;
            padding: 15px;
            overflow-y: auto;
            min-height: 0;
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
            align-self: start;
            min-height: 120px;
        }
        
        .connection-info {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .connection-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 12px;
            background: rgba(255, 51, 51, 0.1);
            border: 1px solid rgba(255, 51, 51, 0.3);
            border-radius: 2px;
        }
        
        .connection-item .label {
            font-size: 12px;
            font-weight: bold;
        }
        
        .connection-item .value {
            font-size: 11px;
            color: #ffff00;
        }
        
        /* Metrics Panel */
        .metrics-panel {
            grid-column: 2;
            grid-row: 1 / 3;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
        }
        
        .metric-card {
            padding: 12px;
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
        
        /* Power Control Panel */
        .node-metrics-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }
        
        .node-metrics-card {
            background: rgba(0, 255, 136, 0.05);
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            min-height: 200px;
        }
        
        .node-metrics-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
        }
        
        .node-name {
            font-size: 18px;
            font-weight: bold;
            color: #00ff88;
        }
        
        .node-status {
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
        }
        
        .node-status.online {
            background: rgba(0, 255, 0, 0.2);
            color: #00ff00;
            border: 1px solid #00ff00;
        }
        
        .node-status.offline {
            background: rgba(255, 0, 0, 0.2);
            color: #ff0000;
            border: 1px solid #ff0000;
        }
        
        .node-metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .node-metric-item {
            background: rgba(0, 0, 0, 0.3);
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #444;
        }
        
        .node-metric-label {
            font-size: 10px;
            color: #888;
            margin-bottom: 3px;
        }
        
        .node-metric-value {
            font-size: 14px;
            font-weight: bold;
            color: #00ff88;
        }
        
        .node-metric-bar {
            width: 100%;
            height: 4px;
            background: #333;
            border-radius: 2px;
            margin-top: 3px;
            overflow: hidden;
        }
        
        .node-metric-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #88ff00);
            transition: width 0.5s ease;
        }
        
        .node-controls {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .node-control-btn {
            padding: 5px 8px;
            border: 1px solid #333;
            background: rgba(0, 255, 136, 0.1);
            color: #00ff88;
            border-radius: 4px;
            cursor: pointer;
            font-size: 10px;
            font-weight: bold;
            transition: all 0.3s ease;
            min-width: 60px;
            text-align: center;
        }
        
        .node-control-btn:hover {
            background: rgba(0, 255, 136, 0.2);
            border-color: #00ff88;
            transform: translateY(-1px);
        }
        
        .node-control-btn.performance {
            border-color: #ff4444;
            color: #ff4444;
            background: rgba(255, 68, 68, 0.1);
        }
        
        .node-control-btn.performance:hover {
            background: rgba(255, 68, 68, 0.2);
            border-color: #ff6666;
        }
        
        .node-control-btn.balanced {
            border-color: #ffaa00;
            color: #ffaa00;
            background: rgba(255, 170, 0, 0.1);
        }
        
        .node-control-btn.balanced:hover {
            background: rgba(255, 170, 0, 0.2);
            border-color: #ffcc44;
        }
        
        .node-control-btn.powersave {
            border-color: #00ff00;
            color: #00ff00;
            background: rgba(0, 255, 0, 0.1);
        }
        
        .node-control-btn.powersave:hover {
            background: rgba(0, 255, 0, 0.2);
            border-color: #44ff44;
        }
        
        .node-control-btn.sleep {
            border-color: #6666ff;
            color: #6666ff;
            background: rgba(102, 102, 255, 0.1);
        }
        
        .node-control-btn.sleep:hover {
            background: rgba(102, 102, 255, 0.2);
            border-color: #8888ff;
        }
        
        .node-control-btn.reboot {
            border-color: #ffaa00;
            color: #ffaa00;
            background: rgba(255, 170, 0, 0.1);
        }
        
        .node-control-btn.reboot:hover {
            background: rgba(255, 170, 0, 0.2);
            border-color: #ffcc44;
        }
        
        .node-control-btn.shutdown {
            border-color: #ff4444;
            color: #ff4444;
            background: rgba(255, 68, 68, 0.1);
        }
        
        .node-control-btn.shutdown:hover {
            background: rgba(255, 68, 68, 0.2);
            border-color: #ff6666;
        }
        .power-control-panel {
            grid-column: 1 / 4;
            grid-row: 3;
        }
        
        .power-controls {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 15px;
        }
        
        .power-mode-controls h4,
        .system-controls h4 {
            margin: 0 0 10px 0;
            color: #00ff88;
            font-size: 14px;
            text-align: center;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .power-btn, .system-btn {
            padding: 10px 15px;
            border: 2px solid #333;
            background: rgba(0, 255, 136, 0.1);
            color: #00ff88;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            transition: all 0.3s ease;
            min-width: 90px;
            text-align: center;
        }
        
        .power-btn:hover, .system-btn:hover {
            background: rgba(0, 255, 136, 0.2);
            border-color: #00ff88;
            transform: translateY(-2px);
        }
        
        .power-btn.performance {
            border-color: #ff4444;
            color: #ff4444;
            background: rgba(255, 68, 68, 0.1);
        }
        
        .power-btn.performance:hover {
            background: rgba(255, 68, 68, 0.2);
            border-color: #ff6666;
        }
        
        .power-btn.balanced {
            border-color: #ffaa00;
            color: #ffaa00;
            background: rgba(255, 170, 0, 0.1);
        }
        
        .power-btn.balanced:hover {
            background: rgba(255, 170, 0, 0.2);
            border-color: #ffcc44;
        }
        
        .power-btn.powersave {
            border-color: #00ff00;
            color: #00ff00;
            background: rgba(0, 255, 0, 0.1);
        }
        
        .power-btn.powersave:hover {
            background: rgba(0, 255, 0, 0.2);
            border-color: #44ff44;
        }
        
        .system-btn.sleep {
            border-color: #6666ff;
            color: #6666ff;
            background: rgba(102, 102, 255, 0.1);
        }
        
        .system-btn.sleep:hover {
            background: rgba(102, 102, 255, 0.2);
            border-color: #8888ff;
        }
        
        .system-btn.reboot {
            border-color: #ffaa00;
            color: #ffaa00;
            background: rgba(255, 170, 0, 0.1);
        }
        
        .system-btn.reboot:hover {
            background: rgba(255, 170, 0, 0.2);
            border-color: #ffcc44;
        }
        
        .system-btn.shutdown {
            border-color: #ff4444;
            color: #ff4444;
            background: rgba(255, 68, 68, 0.1);
        }
        
        .system-btn.shutdown:hover {
            background: rgba(255, 68, 68, 0.2);
            border-color: #ff6666;
        }
        
        /* Nodes Panel */
        .nodes-panel {
            grid-column: 3;
            grid-row: 1;
            align-self: start;
        }
        
        /* Services Panel */
        .services-panel {
            grid-column: 1 / 4;
            grid-row: 3;
            max-height: 200px;
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
            grid-column: 1 / 2;
            grid-row: 2;
            max-height: 200px;
        }
        
        .service-item {
            display: flex;
            flex-direction: column;
            padding: 10px;
            margin-bottom: 8px;
            background: rgba(255, 51, 51, 0.1);
            border: 1px solid rgba(255, 51, 51, 0.3);
            border-radius: 2px;
        }
        
        .service-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }
        
        .service-name {
            font-weight: bold;
            font-size: 12px;
        }
        
        .service-name.online {
            color: #00ff00;
        }
        
        .service-name.offline {
            color: #ff0000;
        }
        
        .service-name.power_save {
            color: #ffff00;
        }
        
        .service-node {
            font-size: 10px;
            opacity: 0.7;
            color: #00ffff;
        }
        
        .service-details {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }
        
        .service-status.running {
            background: rgba(0, 255, 0, 0.2);
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 2px 6px;
            font-size: 9px;
            border-radius: 2px;
        }
        
        .service-status.port_open {
            background: rgba(255, 165, 0, 0.2);
            border: 1px solid #ffa500;
            color: #ffa500;
            padding: 2px 6px;
            font-size: 9px;
            border-radius: 2px;
        }
        
        .service-description {
            font-size: 10px;
            opacity: 0.8;
            color: #cccccc;
        }
        
        .service-port {
            font-size: 9px;
            color: #00ffff;
            background: rgba(0, 255, 255, 0.1);
            padding: 1px 4px;
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 2px;
        }
        
        /* Terminal Section */
        .terminal-section {
            background: rgba(0, 0, 0, 0.8);
            border-top: 2px solid #ff3333;
            height: 120px;
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
        
        .prompt {
            color: #00ff00;
            margin-right: 8px;
        }
        
        /* Responsive */
        @media (max-width: 1400px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
                grid-template-rows: auto auto auto auto;
            }
            
            .connection-panel {
                grid-column: 1;
                grid-row: 1;
            }
            
            .nodes-panel {
                grid-column: 1;
                grid-row: 2;
                max-height: 200px;
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
        """

    def get_magi_js(self):
        """Enhanced MAGI JavaScript"""
        return """
        // MAGI Enhanced Dashboard JavaScript
        let metricsInterval;
        let nodesInterval;
        let terminalCollapsed = false;
        
        function updateTimestamp() {
            const now = new Date();
            document.getElementById('timestamp').textContent = now.toLocaleString();
        }
        
        async function fetchMetrics() {
            try {
                # Use ThreadingTCPServer so SSE and multiple requests won't block each other
                bind = CONFIG.get('bind_address', '') or ''
                with socketserver.ThreadingTCPServer((bind, CONFIG["port"]), MAGIHandler) as httpd:
                    print(f"🚀 MAGI {CONFIG['node_name']} server started (threaded)")
                    print(f"📡 Access dashboard: http://{bind or 'localhost'}:{CONFIG['port']}")
                    print(f"🌐 Network access: http://[your-ip]:{CONFIG['port']}")
                    if CONFIG.get('require_api_key'):
                        print("🔒 API key enforcement enabled. Use Authorization: Bearer <API_KEY>")
                    print("Press Ctrl+C to stop")
                    print("=" * 50)
                    httpd.serve_forever()
                addTerminalLog('❌ Error fetching system metrics');
            }
        }
        
        function updateAllMetrics(allMetrics) {
            const container = document.getElementById('all-metrics-container');
            
            if (!allMetrics || Object.keys(allMetrics).length === 0) {
                container.innerHTML = '<div class="loading-message">No metrics available</div>';
                return;
            }
            
            let html = '<div class="node-metrics-container">';
            
            for (const [nodeName, nodeData] of Object.entries(allMetrics)) {
                const isOnline = nodeData.status === 'online';
                const metrics = nodeData.metrics || {};
                
                html += `
                    <div class="node-metrics-card">
                        <div class="node-metrics-header">
                            <div class="node-name">${nodeName}</div>
                            <div class="node-status ${nodeData.status}">${nodeData.status.toUpperCase()}</div>
                        </div>`;
                
                if (isOnline) {
                    html += `
                        <div class="node-metrics-grid">
                            <div class="node-metric-item">
                                <div class="node-metric-label">CPU</div>
                                <div class="node-metric-value">${metrics.cpu || '--'}%</div>
                                <div class="node-metric-bar>
                                    <div class="node-metric-fill" style="width: ${metrics.cpu || 0}%"></div>
                                </div>
                            </div>
                            <div class="node-metric-item">
                                <div class="node-metric-label">RAM</div>
                                <div class="node-metric-value">${metrics.memory?.percentage || '--'}%</div>
                                <div class="node-metric-bar>
                                    <div class="node-metric-fill" style="width: ${metrics.memory?.percentage || 0}%"></div>
                                </div>
                            </div>
                            <div class="node-metric-item">
                                <div class="node-metric-label">DISK</div>
                                <div class="node-metric-value">${metrics.disk?.percentage || '--'}%</div>
                                <div class="node-metric-bar>
                                    <div class="node-metric-fill" style="width: ${metrics.disk?.percentage || 0}%"></div>
                                </div>
                            </div>
                            <div class="node-metric-item">
                                <div class="node-metric-label">TEMP</div>
                                <div class="node-metric-value">${getAverageTemp(metrics.temperature)}°C</div>
                            </div>
                        </div>
                        <div class="node-controls">
                            <button class="node-control-btn performance" onclick="changeNodePowerMode('${nodeName}', '${nodeData.ip}', ${nodeData.port}, 'performance')">🚀</button>
                            <button class="node-control-btn balanced" onclick="changeNodePowerMode('${nodeName}', '${nodeData.ip}', ${nodeData.port}, 'balanced')">⚖️</button>
                            <button class="node-control-btn powersave" onclick="changeNodePowerMode('${nodeName}', '${nodeData.ip}', ${nodeData.port}, 'powersave')">🔋</button>
                            <button class="node-control-btn sleep" onclick="confirmNodeSystemAction('${nodeName}', '${nodeData.ip}', ${nodeData.port}, 'sleep')">💤</button>
                            <button class="node-control-btn reboot" onclick="confirmNodeSystemAction('${nodeName}', '${nodeData.ip}', ${nodeData.port}, 'reboot')">🔄</button>
                            <button class="node-control-btn shutdown" onclick="confirmNodeSystemAction('${nodeName}', '${nodeData.ip}', ${nodeData.port}, 'shutdown')">⏻</button>
                        </div>`;
                } else {
                    html += `
                        <div style="text-align: center; padding: 20px; color: #ff4444;">
                            ❌ Node Offline<br>
                            <small>${nodeData.error || 'Connection failed'}</small>
                        </div>`;
                }
                
                html += '</div>';
            }
            
            html += '</div>';
            container.innerHTML = html;
        }
        
        function getAverageTemp(temperature) {
            if (!temperature) return '--';
            const temps = Object.values(temperature);
            if (temps.length === 0) return '--';
            const avgTemp = temps.reduce((a, b) => a + (b.current || 0), 0) / temps.length;
            return Math.round(avgTemp);
        }
        
        async function changeNodePowerMode(nodeName, nodeIp, nodePort, mode) {
            try {
                const response = await fetch(`http://${nodeIp}:${nodePort}/api/power/mode`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ mode: mode })
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    addTerminalLog(`✅ ${nodeName}: Power mode changed to ${mode}`);
                } else {
                    addTerminalLog(`⚠️ ${nodeName}: ${result.message}`);
                }
                
                // Refresh metrics after a short delay
                setTimeout(fetchMetrics, 1000);
                
            } catch (error) {
                addTerminalLog(`❌ ${nodeName}: Error changing power mode - ${error.message}`);
            }
        }
        
        function confirmNodeSystemAction(nodeName, nodeIp, nodePort, action) {
            const actionNames = {
                'sleep': 'put to sleep',
                'reboot': 'reboot',
                'shutdown': 'shutdown'
            };
            
            const actionName = actionNames[action] || action;
            
            if (confirm(`Are you sure you want to ${actionName} ${nodeName}?`)) {
                executeNodeSystemAction(nodeName, nodeIp, nodePort, action);
            }
        }
        
        async function executeNodeSystemAction(nodeName, nodeIp, nodePort, action) {
            try {
                const response = await fetch(`http://${nodeIp}:${nodePort}/api/system/${action}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ delay: 30 }) // 30 seconds delay
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    addTerminalLog(`✅ ${nodeName}: ${result.message}`);
                } else {
                    addTerminalLog(`❌ ${nodeName}: ${result.message}`);
                }
                
            } catch (error) {
                addTerminalLog(`❌ ${nodeName}: Error executing ${action} - ${error.message}`);
            }
        }
        
        function updateServices(services) {
            const container = document.getElementById('services-container');
            if (!services || Object.keys(services).length === 0) {
                container.innerHTML = '<div class="service-item"><span class="service-name">No services detected</span></div>';
                return;
            }
            
            container.innerHTML = '';
            
            Object.entries(services).forEach(([serviceKey, service]) => {
                const serviceDiv = document.createElement('div');
                serviceDiv.className = 'service-item';
                
                // Extraer nombre del servicio y nodo
                const [serviceName, nodeName] = serviceKey.includes('@') ? 
                    serviceKey.split('@') : [serviceKey, 'LOCAL'];
                
                // Determinar color según estado del nodo
                let nodeStatusClass = '';
                if (service.node_status === 'offline') nodeStatusClass = 'offline';
                else if (service.node_status === 'power_save') nodeStatusClass = 'power_save';
                else if (service.node_status === 'online') nodeStatusClass = 'online';
                
                // Construir HTML del servicio
                const portsHtml = service.ports && service.ports.length > 0 ? 
                    service.ports.map(port => `<span class="service-port">:${port}</span>`).join(' ') : '';
                
                const processIcon = service.process_detected ? '🟢' : '🔶';
                const statusText = service.status === 'running' ? 'RUNNING' : 'PORT OPEN';
                
                serviceDiv.innerHTML = `
                    <div class="service-header">
                        <span class="service-name ${nodeStatusClass}">${serviceName.toUpperCase()}</span>
                        <span class="service-node">@${nodeName}</span>
                    </div>
                    <div class="service-details">
                        <span class="service-status ${service.status}">${processIcon} ${statusText}</span>
                        <span class="service-description">${service.description || 'Service'}</span>
                        ${portsHtml}
                    </div>
                `;
                
                container.appendChild(serviceDiv);
            });
        }
        
        // Nueva función para obtener todos los servicios
        async function fetchAllServices() {
            try {
                const response = await fetch('/api/services');
                const services = await response.json();
                updateServices(services);
            } catch (error) {
                console.error('Error fetching services:', error);
                addTerminalLog('❌ Error fetching services');
            }
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
                        responseTimeHtml = `<div class="node-info">⚡ ${node.response_time}ms</div>`;
                    }
                    
                    let powerStateHtml = '';
                    if (node.power_state && node.power_state !== 'normal') {
                        powerStateHtml = `<div class="node-info">🔋 ${node.power_state}</div>`;
                    }
                    
                    // Mostrar servicios principales del nodo
                    let servicesHtml = '';
                    if (node.services && Object.keys(node.services).length > 0) {
                        const serviceCount = Object.keys(node.services).length;
                        const mainServices = Object.keys(node.services).slice(0, 2).join(', ');
                        servicesHtml = `<div class="node-info">⚙️ ${serviceCount} services</div>`;
                        if (mainServices) {
                            servicesHtml += `<div class="node-info" style="font-size: 9px;">📊 ${mainServices}</div>`;
                        }
                    }
                    
                    nodeCard.innerHTML = `
                        <div class="node-status-badge">${statusText}</div>
                        <div class="node-name">${node.name}</div>
                        <div class="node-info">${node.ip}:${node.port}</div>
                        ${responseTimeHtml}
                        ${powerStateHtml}
                        ${servicesHtml}
                        <div class="node-info">Last: ${node.last_seen}</div>
                    `;
                    
                    container.appendChild(nodeCard);
                });
                
            } catch (error) {
                console.error('Error fetching nodes:', error);
                addTerminalLog('❌ Error fetching network nodes');
            }
        }
        
        function addTerminalLog(message) {
            const terminal = document.getElementById('terminal');
            const logLine = document.createElement('div');
            logLine.className = 'log-line';
            
            const timestamp = new Date().toLocaleTimeString();
            logLine.innerHTML = `
                <span class="prompt">&gt;</span>
                <span>[${timestamp}] ${message}</span>
            `;
            
            terminal.appendChild(logLine);
            terminal.scrollTop = terminal.scrollHeight;
            
            // Keep only last 20 log lines
            const lines = terminal.querySelectorAll('.log-line');
            if (lines.length > 20) {
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
        
        // Power Management Functions
        async function changePowerMode(mode) {
            try {
                addTerminalLog(`🔄 Changing power mode to ${mode}...`);
                
                const response = await fetch('/api/power/mode', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ mode: mode })
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    addTerminalLog(`✅ ${result.message}`);
                } else {
                    addTerminalLog(`❌ Error: ${result.message}`);
                }
            } catch (error) {
                addTerminalLog(`❌ Error changing power mode: ${error}`);
            }
        }
        
        function confirmSystemAction(action) {
            const actionMessages = {
                'sleep': 'suspend the system',
                'reboot': 'reboot the system',
                'shutdown': 'shutdown the system'
            };
            
            const message = actionMessages[action] || 'perform this action';
            
            if (confirm(`Are you sure you want to ${message}?`)) {
                performSystemAction(action);
            }
        }
        
        async function performSystemAction(action) {
            try {
                let endpoint;
                let delay = 30; // 30 seconds delay for reboot/shutdown
                
                switch(action) {
                    case 'sleep':
                        endpoint = '/api/system/sleep';
                        addTerminalLog('💤 Putting system to sleep...');
                        break;
                    case 'reboot':
                        endpoint = '/api/system/reboot';
                        addTerminalLog(`🔄 Scheduling system reboot in ${delay} seconds...`);
                        break;
                    case 'shutdown':
                        endpoint = '/api/system/shutdown';
                        addTerminalLog(`⏻ Scheduling system shutdown in ${delay} seconds...`);
                        break;
                    default:
                        throw new Error('Invalid action');
                }
                
                const body = action === 'sleep' ? {} : { delay: delay };
                
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(body)
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    addTerminalLog(`✅ ${result.message}`);
                    
                    if (action === 'reboot' || action === 'shutdown') {
                        // Show countdown
                        setTimeout(() => {
                            addTerminalLog(`⚠️ System ${action} will occur in ${delay} seconds`);
                        }, 1000);
                    }
                } else {
                    addTerminalLog(`❌ Error: ${result.message}`);
                }
            } catch (error) {
                addTerminalLog(`❌ Error performing ${action}: ${error}`);
            }
        }
        
        function checkNetworkInfo() {
            const ipEl = document.getElementById('network-ip');
            ipEl.textContent = window.location.hostname || 'localhost';
            
            const sshEl = document.getElementById('ssh-status');
            sshEl.textContent = 'Port 22';
            sshEl.style.color = '#ffff00';
        }
        function startMonitoring() {
            updateTimestamp();
            checkNetworkInfo();

            // Try Server-Sent Events first
            if (window.EventSource) {
                try {
                    const es = new EventSource('/api/stream');
                    es.onmessage = function(e) {
                        try {
                            const data = JSON.parse(e.data);
                            updateAllMetrics(data);
                        } catch (err) {
                            console.error('SSE parse error', err);
                        }
                    };
                    es.onerror = function(ev) {
                        addTerminalLog('⚠️ SSE connection error, falling back to polling');
                        try { es.close(); } catch (e) {}
                        // fallback to polling
                        fetchMetrics();
                        metricsInterval = setInterval(fetchMetrics, 5000);
                    };

                    addTerminalLog('📡 Connected to SSE stream for real-time metrics');
                } catch (e) {
                    addTerminalLog('⚠️ SSE not available, using polling');
                    fetchMetrics();
                    metricsInterval = setInterval(fetchMetrics, 5000);
                }
            } else {
                // No EventSource support
                fetchMetrics();
                metricsInterval = setInterval(fetchMetrics, 5000);
            }

            // Always keep nodes and services updated
            fetchNodes();
            fetchAllServices();
            nodesInterval = setInterval(fetchNodes, 6000);
            servicesInterval = setInterval(fetchAllServices, 8000);

            // Update timestamp every second
            setInterval(updateTimestamp, 1000);

            // Add startup logs
            setTimeout(() => addTerminalLog('⚡ Dashboard initialized'), 500);
            setTimeout(() => addTerminalLog('📡 Real-time monitoring active'), 1000);
            setTimeout(() => addTerminalLog('🔋 Power management enabled'), 1500);
            setTimeout(() => addTerminalLog('⚙️ Enhanced service detection active'), 2000);
        }
        
        function logout() {
            if (confirm('Are you sure you want to logout?')) {
                window.location.href = '/logout';
            }
        }

        // Start monitoring when page loads
        document.addEventListener('DOMContentLoaded', startMonitoring);
        """

def change_power_mode(mode):
    """Change system power mode"""
    try:
        success = False
        
        # Try cpupower first
        if subprocess.run(['which', 'cpupower'], capture_output=True).returncode == 0:
            if mode == "performance":
                result = subprocess.run(['cpupower', 'frequency-set', '-g', 'performance'], 
                                     capture_output=True, check=False)
                success = result.returncode == 0
            elif mode == "powersave":
                result = subprocess.run(['cpupower', 'frequency-set', '-g', 'powersave'], 
                                     capture_output=True, check=False)
                success = result.returncode == 0
            elif mode == "balanced":
                result = subprocess.run(['cpupower', 'frequency-set', '-g', 'ondemand'], 
                                     capture_output=True, check=False)
                success = result.returncode == 0
        
        # Alternative method using sysfs
        if not success:
            try:
                governor_files = [
                    '/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor',
                    '/sys/devices/system/cpu/cpufreq/policy0/scaling_governor'
                ]
                
                governor_map = {
                    "performance": "performance",
                    "powersave": "powersave", 
                    "balanced": "ondemand"
                }
                
                target_governor = governor_map.get(mode)
                if target_governor:
                    for gov_file in governor_files:
                        try:
                            with open(gov_file, 'w') as f:
                                f.write(target_governor)
                            success = True
                            break
                        except (FileNotFoundError, PermissionError):
                            continue
            except Exception:
                pass
        
        if success:
            return {
                "status": "success",
                "message": f"Power mode changed to {mode}",
                "mode": mode
            }
        else:
            return {
                "status": "warning",
                "message": f"Power mode change requested ({mode}) but may require root privileges",
                "mode": mode
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error changing power mode: {e}"
        }

def schedule_system_shutdown(delay):
    """Schedule system shutdown"""
    try:
        subprocess.run(['shutdown', '-h', f'+{delay//60}'], check=True)
        return {
            "status": "success",
            "message": f"System shutdown scheduled in {delay} seconds",
            "action": "shutdown",
            "delay": delay
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Error scheduling shutdown: {e}"
        }

def schedule_system_reboot(delay):
    """Schedule system reboot"""
    try:
        subprocess.run(['shutdown', '-r', f'+{delay//60}'], check=True)
        return {
            "status": "success",
            "message": f"System reboot scheduled in {delay} seconds",
            "action": "reboot",
            "delay": delay
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Error scheduling reboot: {e}"
        }

def system_sleep():
    """Put system to sleep/suspend"""
    try:
        subprocess.run(['systemctl', 'suspend'], check=True)
        return {
            "status": "success",
            "message": "System going to sleep",
            "action": "sleep"
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Error putting system to sleep: {e}"
        }

def get_system_metrics():
    """Get enhanced system metrics including network, temperature, power state and services"""
    try:
        # CPU usage (average over 1 second)
        cpu_usage = int(psutil.cpu_percent(interval=1))
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percentage = int(memory.percent)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percentage = int((disk.used / disk.total) * 100)
        
        # Network stats
        net_io = psutil.net_io_counters()
        network_usage = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
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
            # Fallback temperature
            temperatures["cpu"] = {"current": 45, "high": 75, "critical": 85}
        
        # Power management state detection
        power_state = "normal"
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq and cpu_freq.current < cpu_freq.max * 0.7:
                power_state = "power_save"
            
            load_avg = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
            if load_avg < 0.5:
                power_state = "low_power"
        except:
            pass
        
        # Detect running services
        services = detect_services()
        
        # Boot time / uptime
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        uptime_hours = int(uptime_seconds / 3600)
        
        return {
            "cpu": cpu_usage,
            "memory": {
                "percentage": memory_percentage,
                "used_gb": round(memory.used / (1024**3), 2),
                "total_gb": round(memory.total / (1024**3), 2)
            },
            "disk": {
                "percentage": disk_percentage,
                "used_gb": round(disk.used / (1024**3), 2),
                "total_gb": round(disk.total / (1024**3), 2)
            },
            "network": network_usage,
            "temperature": temperatures,
            "power_state": power_state,
            "services": services,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "node_status": "online"
        }
    except Exception as e:
        print(f"Error getting metrics: {e}")
        return get_system_metrics_fallback()

def detect_services():
    """Detect comprehensive services running on the system"""
    services = {}

    # Common services with typical process names and ports
    service_definitions = {
        "nextcloud": {"processes": ["nginx", "apache2", "nextcloud", "php-fpm"], "ports": [80, 443, 8080], "description": "Cloud Storage"},
        "jellyfin": {"processes": ["jellyfin"], "ports": [8096, 8920], "description": "Media Server"},
        "plex": {"processes": ["plexmediaserver", "plex"], "ports": [32400], "description": "Media Server"},
        "emby": {"processes": ["emby", "embyserver"], "ports": [8096], "description": "Media Server"},
        "docker": {"processes": ["docker", "dockerd", "containerd"], "ports": [2375, 2376], "description": "Container Platform"},
        "ssh": {"processes": ["sshd", "ssh"], "ports": [22], "description": "Remote Access"},
        "web": {"processes": ["nginx", "apache2", "httpd", "lighttpd"], "ports": [80, 443, 8080, 8443], "description": "Web Server"},
        "database": {"processes": ["mysql", "mysqld", "postgresql", "postgres", "mariadb"], "ports": [3306, 5432], "description": "Database"},
        "samba": {"processes": ["smbd", "nmbd"], "ports": [139, 445], "description": "File Sharing"},
        "transmission": {"processes": ["transmission-daemon", "transmission"], "ports": [9091], "description": "Torrent Client"},
        "pihole": {"processes": ["pihole", "dnsmasq", "lighttpd"], "ports": [53, 80], "description": "DNS Filter"},
        "homeassistant": {"processes": ["homeassistant", "hass"], "ports": [8123], "description": "Home Automation"},
        "mqtt": {"processes": ["mosquitto", "mqtt"], "ports": [1883, 8883], "description": "IoT Messaging"},
        "vnc": {"processes": ["vncserver", "vnc", "x11vnc"], "ports": [5900, 5901], "description": "Remote Desktop"},
        "magi": {"processes": ["magi-node", "python3"], "ports": [8080, 8081, 8082], "description": "MAGI Monitor"}
    }

    try:
        running_processes = []
        for p in psutil.process_iter(['name', 'cmdline']):
            try:
                name = (p.info.get('name') or '').lower()
                cmdline = ' '.join(p.info.get('cmdline') or []).lower()
                running_processes.append((name, cmdline))
            except Exception:
                continue

        open_ports = set()
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr and conn.status == 'LISTEN':
                try:
                    open_ports.add(conn.laddr.port)
                except Exception:
                    continue

        for service_name, service_def in service_definitions.items():
            process_found = False
            for proc_name, cmdline in running_processes:
                if any(proc in proc_name or proc in cmdline for proc in service_def['processes']):
                    process_found = True
                    break

            port_found = any(port in open_ports for port in service_def['ports'])
            active_ports = [port for port in service_def['ports'] if port in open_ports]

            if process_found or port_found:
                services[service_name] = {
                    'status': 'running' if process_found else 'port_open',
                    'ports': active_ports if active_ports else service_def['ports'][:1],
                    'description': service_def['description'],
                    'process_detected': process_found,
                    'port_detected': port_found
                }

        additional_ports = {21: 'FTP', 25: 'SMTP', 53: 'DNS', 110: 'POP3', 143: 'IMAP', 993: 'IMAPS', 995: 'POP3S', 3389: 'RDP', 5432: 'PostgreSQL', 6379: 'Redis', 27017: 'MongoDB', 9200: 'Elasticsearch'}
        for port, svc in additional_ports.items():
            if port in open_ports and svc.lower() not in services:
                services[svc.lower()] = {
                    'status': 'port_open',
                    'ports': [port],
                    'description': svc,
                    'process_detected': False,
                    'port_detected': True
                }
    except Exception as e:
        print(f"Error detecting services: {e}")

    return services


def get_service_port(service_name):
    """Get default port for common services"""
    default_ports = {
        'nextcloud': 80,
        'jellyfin': 8096,
        'plex': 32400,
        'ssh': 22,
        'web': 80,
        'samba': 445
    }
    return default_ports.get(service_name)


def get_system_metrics_fallback():
    """Fallback system metrics without psutil"""
    return {
        'cpu': 42,
        'memory': {'percentage': 35, 'used_gb': 2.8, 'total_gb': 8.0},
        'disk': {'percentage': 60, 'used_gb': 120, 'total_gb': 200},
        'network': {'mb_sent': 45.2, 'mb_recv': 234.5},
        'temperature': {'cpu': {'current': 45}},
        'power_state': 'normal',
        'services': {},
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'node_status': 'online'
    }


def gather_all_metrics():
    """Collect metrics for local node and attempt to retrieve from other configured nodes."""
    all_metrics = {}

    # Local metrics
    try:
        local_metrics = get_system_metrics()
        all_metrics[CONFIG['node_name']] = {
            'status': 'online',
            'metrics': local_metrics,
            'ip': 'localhost',
            'port': CONFIG['port']
        }
    except Exception:
        all_metrics[CONFIG['node_name']] = {
            'status': 'online',
            'metrics': get_system_metrics_fallback(),
            'ip': 'localhost',
            'port': CONFIG['port']
        }

    demo_mode = os.environ.get('MAGI_DEMO_MODE', 'false').lower() == 'true'
    if demo_mode:
        # Simulate other nodes
        for i, node_name in enumerate(['GASPAR', 'MELCHIOR', 'BALTASAR']):
            if node_name == CONFIG['node_name']:
                continue
            sim_metrics = MAGIHandler.create_simulated_metrics(None, node_name)
            all_metrics[node_name] = {
                'status': 'online',
                'metrics': sim_metrics,
                'ip': f'192.168.1.{100 + i}',
                'port': 8080 + i
            }
        return all_metrics

    # Real discovery
    nodes = discover_nodes()
    for node in nodes:
        name = node.get('name')
        if name == CONFIG['node_name']:
            continue

        if node.get('status') not in ('online', 'power_save'):
            all_metrics[name] = {
                'status': node.get('status'),
                'error': 'node unreachable',
                'ip': node.get('ip'),
                'port': node.get('port', 'unknown')
            }
            continue

        node_ip = node.get('ip')
        node_port = node.get('port', 8080)

        try:
            url = f'http://{node_ip}:{node_port}/api/metrics'
            req = urllib.request.Request(url, headers={'User-Agent': 'MAGI-Discovery'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    metrics = json.loads(resp.read().decode())
                    all_metrics[name] = {
                        'status': 'online',
                        'metrics': metrics,
                        'ip': node_ip,
                        'port': node_port
                    }
                else:
                    all_metrics[name] = {
                        'status': 'error',
                        'error': f'HTTP {resp.status}',
                        'ip': node_ip,
                        'port': node_port
                    }
        except Exception as e:
            all_metrics[name] = {
                'status': 'offline',
                'error': str(e),
                'ip': node_ip,
                'port': node_port
            }

    return all_metrics


def discover_nodes():
    """Discover other MAGI nodes on the network with power state detection and services"""
    nodes = []
    current_node = CONFIG.get('node_name')
    current_port = CONFIG.get('port')

    for node_config in CONFIG.get('other_nodes', []):
        node_name = node_config.get('name')
        node_ip = node_config.get('ip')
        node_port = node_config.get('port')

        # Self case
        if node_name == current_node:
            try:
                metrics = get_system_metrics()
                power_state = metrics.get('power_state', 'normal')
                node_status = 'power_save' if power_state in ('power_save', 'low_power') else 'online'
                services = metrics.get('services', {})
            except Exception:
                node_status = 'online'
                power_state = 'normal'
                services = {}

            nodes.append({
                'name': node_name,
                'ip': 'localhost',
                'port': current_port,
                'status': node_status,
                'response_time': 0,
                'self': True,
                'last_seen': time.strftime('%Y-%m-%d %H:%M:%S'),
                'power_state': power_state,
                'services': services
            })
            continue

        # Test remote connectivity and try to fetch /api/metrics
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((node_ip, node_port))
            sock.close()
            response_time = int((time.time() - start_time) * 1000)

            if result == 0:
                node_status = 'online'
                power_state = 'normal'
                services = {}
                try:
                    url = f'http://{node_ip}:{node_port}/api/metrics'
                    req = urllib.request.Request(url, headers={'User-Agent': 'MAGI-Discovery'})
                    with urllib.request.urlopen(req, timeout=2) as response:
                        if response.status == 200:
                            metrics_data = json.loads(response.read().decode())
                            power_state = metrics_data.get('power_state', 'normal')
                            services = metrics_data.get('services', {})
                            if power_state in ('power_save', 'low_power'):
                                node_status = 'power_save'
                except Exception as e:
                    print(f'Error getting remote metrics from {node_name}: {e}')

                nodes.append({
                    'name': node_name,
                    'ip': node_ip,
                    'port': node_port,
                    'status': node_status,
                    'response_time': response_time,
                    'self': False,
                    'last_seen': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'power_state': power_state,
                    'services': services
                })
            else:
                nodes.append({
                    'name': node_name,
                    'ip': node_ip,
                    'port': node_port,
                    'status': 'offline',
                    'response_time': -1,
                    'self': False,
                    'last_seen': 'never',
                    'power_state': 'offline',
                    'services': {}
                })
        except Exception as e:
            nodes.append({
                'name': node_name,
                'ip': node_ip,
                'port': node_port,
                'status': 'error',
                'response_time': -1,
                'self': False,
                'last_seen': 'never',
                'power_state': 'error',
                'services': {}
            })

    return nodes


def ensure_api_key():
    """Abort startup if API key enforcement is enabled but api_key is default/empty."""
    if CONFIG.get('require_api_key'):
        key = CONFIG.get('api_key')
        if not key or key == 'changeme':
            raise RuntimeError('API key enforcement is enabled but MAGI API key is not set or still default (changeme). Set MAGI_API_KEY env or CONFIG["api_key"]')


def setup_node():
    """Setup node configuration and apply environment overrides."""
    import sys



    if len(sys.argv) > 1:
        node_name = sys.argv[1].upper()
        if node_name in ("GASPAR", "MELCHIOR", "BALTASAR"):
            CONFIG['node_name'] = node_name
            print(f"⚡ MAGI Node '{node_name}' configured")

    if CONFIG.get('node_name') == 'UNKNOWN':
        CONFIG['node_name'] = input('Enter node name (GASPAR/MELCHIOR/BALTASAR): ').upper()

    # Environment overrides (wrappers/systemd)
    try:
        env_port = os.environ.get('MAGI_PORT')
        if env_port:
            CONFIG['port'] = int(env_port)
    except Exception:
        pass

    env_bind = os.environ.get('MAGI_BIND')
    if env_bind:
        CONFIG['bind_address'] = env_bind

    env_require = os.environ.get('MAGI_REQUIRE_API_KEY')
    if env_require is not None:
        CONFIG['require_api_key'] = str(env_require).lower() in ('1', 'true', 'yes')

    env_key = os.environ.get('MAGI_API_KEY')
    if env_key:
        CONFIG['api_key'] = env_key

    # Login configuration
    env_require_login = os.environ.get('MAGI_REQUIRE_LOGIN')
    if env_require_login is not None:
        CONFIG['require_login'] = str(env_require_login).lower() in ('1', 'true', 'yes')
    
    env_admin_pass = os.environ.get('MAGI_ADMIN_PASSWORD')
    if env_admin_pass:
        CONFIG['login_users']['admin'] = env_admin_pass
    
    # Check if admin password is still default
    if CONFIG.get('require_login') and CONFIG['login_users']['admin'] == 'changeme':
        print("⚠️  WARNING: Admin password is still default. Set MAGI_ADMIN_PASSWORD environment variable.")

    if any([os.environ.get('MAGI_PORT'), os.environ.get('MAGI_BIND'), os.environ.get('MAGI_REQUIRE_API_KEY'), os.environ.get('MAGI_API_KEY'), os.environ.get('MAGI_REQUIRE_LOGIN'), os.environ.get('MAGI_ADMIN_PASSWORD')]):
        print('Applied environment configuration overrides:')
        print(f"  bind_address={CONFIG.get('bind_address')} port={CONFIG.get('port')} require_api_key={CONFIG.get('require_api_key')} require_login={CONFIG.get('require_login')}")


def main():
    """Main MAGI function"""
    print('⚡ MAGI v2.0 - Enhanced Distributed Monitoring')
    print('=' * 50)

    setup_node()

    print(f"Node: {CONFIG['node_name']}")
    print(f"Port: {CONFIG['port']}")
    print(f"Bind: {CONFIG.get('bind_address')}")
    print(f"Platform: {platform.platform()}")
    print(f"Python: {platform.python_version()}")
    print('=' * 50)

    # Safety check for API key
    try:
        ensure_api_key()
    except Exception as e:
        print(f'❌ Startup aborted: {e}')
        return
    
    # Start session cleanup if login is required
    if CONFIG.get('require_login'):
        start_session_cleanup()
        print('🔐 Session management started')

    try:
        with socketserver.ThreadingTCPServer((CONFIG.get('bind_address', ''), CONFIG['port']), MAGIHandler) as httpd:
            bind = CONFIG.get('bind_address') or '0.0.0.0'
            print(f"🚀 MAGI {CONFIG['node_name']} server started (threaded)")
            print(f"📡 Access dashboard: http://{bind}:{CONFIG['port']}")
            if CONFIG.get('require_api_key'):
                print('🔒 API key enforcement enabled. Use Authorization: Bearer <API_KEY>')
            print('Press Ctrl+C to stop')
            print('=' * 50)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 MAGI {CONFIG['node_name']} server stopped")
    except Exception as e:
        print(f"❌ Error starting MAGI server: {e}")


if __name__ == "__main__":
    main()
