#!/usr/bin/env python3
"""MAGI wrapper for MELCHIOR node (Monitoring & Home Assistant)
"""
import os
import sys

# Configuration for MELCHIOR
os.environ.setdefault('MAGI_PORT', '8082')
os.environ.setdefault('MAGI_BIND', '0.0.0.0')

# Security settings - Melchior as monitoring node has API enabled by default
os.environ.setdefault('MAGI_REQUIRE_LOGIN', 'true')
os.environ.setdefault('MAGI_REQUIRE_API_KEY', 'true')

# Production deployment should use:
# - /etc/magi/config.env for unified admin password and API key
# - systemd services with EnvironmentFile=/etc/magi/config.env
# - install_magi.sh script for proper setup

script = os.path.join(os.path.dirname(__file__), 'magi-node-v2.py')
if not os.path.exists(script):
    print('ERROR: magi-node-v2.py not found in the same folder')
    sys.exit(1)

os.execv(sys.executable, [sys.executable, script, 'MELCHIOR'])
