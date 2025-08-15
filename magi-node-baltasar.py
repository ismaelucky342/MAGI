#!/usr/bin/env python3
"""MAGI wrapper for BALTASAR node (Streaming, AI & Virtualization)
"""
import os
import sys

# Configuration for BALTASAR
os.environ.setdefault('MAGI_PORT', '8083')
os.environ.setdefault('MAGI_BIND', '0.0.0.0')

# Security settings - Baltasar has API enabled for heavy compute coordination
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

os.execv(sys.executable, [sys.executable, script, 'BALTASAR'])
