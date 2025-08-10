#!/usr/bin/env python3
"""
MAGI Windows Installer - Simple Launcher
Just run this script to install MAGI on Windows
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the installer
from magi_windows_python_installer import main

if __name__ == "__main__":
    main()
