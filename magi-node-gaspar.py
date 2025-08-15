#!/usr/bin/env python3
"""MAGI wrapper for GASPAR node (Backup & Storage)
Sets environment for port and node name then execs magi-node-v2.py
"""
import os
import sys

# Configuration for GASPAR
os.environ.setdefault('MAGI_PORT', '8081')
os.environ.setdefault('MAGI_BIND', '0.0.0.0')

# Security settings (will be overridden by /etc/magi/config.env in production)
os.environ.setdefault('MAGI_REQUIRE_LOGIN', 'true')
os.environ.setdefault('MAGI_REQUIRE_API_KEY', 'false')

# Production deployment should use:
# - /etc/magi/config.env for unified admin password and API key
# - systemd services with EnvironmentFile=/etc/magi/config.env
# - install_magi.sh script for proper setup

script = os.path.join(os.path.dirname(__file__), 'magi-node-v2.py')
if not os.path.exists(script):
    print('ERROR: magi-node-v2.py not found in the same folder')
    sys.exit(1)

# Exec the main script with node name argument
os.execv(sys.executable, [sys.executable, script, 'GASPAR'])
