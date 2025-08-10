@echo off
title MAGI Node Portable Launcher
echo ================================================
echo 🧙 MAGI Node Portable v2.0.0
echo ================================================
echo Starting MAGI Node from current directory...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ first
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if MAGI files exist
if not exist "magi-node-v2.py" (
    echo ❌ magi-node-v2.py not found in current directory
    pause
    exit /b 1
)

REM Install dependencies if needed
echo 📦 Checking dependencies...
python -c "import psutil" 2>nul
if errorlevel 1 (
    echo Installing psutil...
    python -m pip install psutil
)

REM Create launcher if it doesn't exist
if not exist "magi_launcher.py" (
    echo Creating launcher...
    python -c "
import socket
import os
import sys

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def find_available_port(start_port=8080):
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
    hostname = socket.gethostname().upper()
    magi_nodes = ['GASPAR', 'MELCHIOR', 'BALTASAR']
    for node in magi_nodes:
        if node in hostname:
            return node
    try:
        ip = get_local_ip()
        last_octet = int(ip.split('.')[-1])
        if last_octet %% 3 == 0:
            return 'GASPAR'
        elif last_octet %% 3 == 1:
            return 'MELCHIOR'
        else:
            return 'BALTASAR'
    except:
        return 'GASPAR'

node_name = detect_node_name()
print(f'🧙 Starting MAGI Node: {node_name}')
sys.argv = ['portable', node_name]

import importlib.util
spec = importlib.util.spec_from_file_location('magi_node', 'magi-node-v2.py')
magi_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(magi_module)
"
) else (
    python magi_launcher.py
)
