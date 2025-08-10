#!/usr/bin/env python3
"""
MAGI Node Launcher for Windows
Auto-detects configuration and starts MAGI node
"""

import os
import sys
import json
import socket
import subprocess
import time

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def find_available_port(start_port=8080):
    """Find available port starting from start_port"""
    for port in range(start_port, start_port + 20):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', port))
            sock.close()
            return port
        except OSError:
            continue
    return 8080

def detect_node_name():
    """Auto-detect node name based on hostname"""
    hostname = socket.gethostname().upper()
    
    # MAGI node names
    magi_nodes = ["GASPAR", "MELCHIOR", "BALTASAR"]
    
    # Check if hostname contains a MAGI node name
    for node in magi_nodes:
        if node in hostname:
            return node
            
    # Default based on IP last octet
    try:
        ip = get_local_ip()
        last_octet = int(ip.split('.')[-1])
        if last_octet % 3 == 0:
            return "GASPAR"
        elif last_octet % 3 == 1:
            return "MELCHIOR"
        else:
            return "BALTASAR"
    except:
        return "GASPAR"

def main():
    print("🧙 Starting MAGI Node...")
    print("=" * 50)
    
    # Auto-detect configuration
    node_name = detect_node_name()
    local_ip = get_local_ip()
    port = find_available_port()
    
    print(f"🏷️  Node Name: {node_name}")
    print(f"🌐 Local IP: {local_ip}")
    print(f"🔌 Port: {port}")
    print("=" * 50)
    
    # Import and start MAGI
    try:
        # Set environment
        os.environ['MAGI_NODE_NAME'] = node_name
        os.environ['MAGI_PORT'] = str(port)
        os.environ['MAGI_IP'] = local_ip
        
        # Start with auto-configuration
        sys.argv = ['magi_launcher.py', node_name]
        
        # Import the main module
        import importlib.util
        spec = importlib.util.spec_from_file_location("magi_node", "magi-node-v2.py")
        magi_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(magi_module)
        
    except ImportError as e:
        print(f"❌ Error importing MAGI: {e}")
        print("Please ensure magi-node-v2.py is in the same directory")
    except KeyboardInterrupt:
        print("\n🛑 MAGI Node stopped by user")
    except Exception as e:
        print(f"❌ Error starting MAGI: {e}")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
