#!/bin/bash
"""
🧙‍♂️ MAGI Service Installer - Make MAGI run forever
Creates systemd service and desktop shortcut
"""

# Configuration
MAGI_USER=$(whoami)
MAGI_HOME=$(pwd)
MAGI_NODE="GASPAR"
SERVICE_NAME="magi-${MAGI_NODE,,}"

echo "🧙‍♂️ MAGI Service Installer"
echo "=========================="
echo "User: $MAGI_USER"
echo "Directory: $MAGI_HOME"
echo "Node: $MAGI_NODE"
echo "Service: $SERVICE_NAME"
echo ""

# Ask for node name
read -p "Enter MAGI node name (GASPAR/MELCHIOR/BALTASAR) [$MAGI_NODE]: " input_node
if [[ ! -z "$input_node" ]]; then
    MAGI_NODE="$input_node"
    SERVICE_NAME="magi-${MAGI_NODE,,}"
fi

echo "🔧 Creating systemd service..."

# Create systemd service file
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=🧙‍♂️ MAGI $MAGI_NODE Monitoring Node
Documentation=https://github.com/ismaelucky342/MAGI
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$MAGI_USER
Group=$MAGI_USER
WorkingDirectory=$MAGI_HOME
ExecStart=/usr/bin/python3 $MAGI_HOME/magi-node.py $MAGI_NODE
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=magi-$MAGI_NODE

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$MAGI_HOME

# Environment
Environment=PYTHONUNBUFFERED=1
Environment=MAGI_NODE=$MAGI_NODE

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created: /etc/systemd/system/${SERVICE_NAME}.service"

# Reload systemd and enable service
echo "🔄 Enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}

echo "🚀 Starting service..."
sudo systemctl start ${SERVICE_NAME}

# Check status
echo "📊 Service status:"
sudo systemctl status ${SERVICE_NAME} --no-pager -l

echo ""
echo "🎯 Service commands:"
echo "   Start:   sudo systemctl start ${SERVICE_NAME}"
echo "   Stop:    sudo systemctl stop ${SERVICE_NAME}"
echo "   Restart: sudo systemctl restart ${SERVICE_NAME}"
echo "   Status:  sudo systemctl status ${SERVICE_NAME}"
echo "   Logs:    sudo journalctl -u ${SERVICE_NAME} -f"
echo ""

# Create desktop shortcut
echo "🖥️ Creating desktop shortcut..."

# Convert SVG to PNG for better compatibility
if command -v inkscape &> /dev/null; then
    inkscape "$MAGI_HOME/magi-icon.svg" --export-filename="$MAGI_HOME/magi-icon.png" --export-width=64 --export-height=64 2>/dev/null
    ICON_PATH="$MAGI_HOME/magi-icon.png"
elif command -v convert &> /dev/null; then
    convert "$MAGI_HOME/magi-icon.svg" -resize 64x64 "$MAGI_HOME/magi-icon.png" 2>/dev/null
    ICON_PATH="$MAGI_HOME/magi-icon.png"
else
    ICON_PATH="$MAGI_HOME/magi-icon.svg"
fi

# Create desktop entry
mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/magi-${MAGI_NODE,,}.desktop <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=🧙‍♂️ MAGI $MAGI_NODE
Comment=MAGI Distributed Monitoring System - $MAGI_NODE Node
Exec=xdg-open http://localhost:8081
Icon=$ICON_PATH
Terminal=false
Categories=System;Monitor;Network;
Keywords=magi;monitoring;system;distributed;
StartupNotify=true
EOF

# Make desktop file executable
chmod +x ~/.local/share/applications/magi-${MAGI_NODE,,}.desktop

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database ~/.local/share/applications/
fi

echo "✅ Desktop shortcut created: ~/.local/share/applications/magi-${MAGI_NODE,,}.desktop"

# Create desktop shortcut on desktop
if [[ -d ~/Desktop ]]; then
    cp ~/.local/share/applications/magi-${MAGI_NODE,,}.desktop ~/Desktop/
    chmod +x ~/Desktop/magi-${MAGI_NODE,,}.desktop
    echo "✅ Shortcut also added to Desktop"
fi

echo ""
echo "🎉 MAGI Service Installation Complete!"
echo "======================================"
echo ""
echo "🚀 MAGI $MAGI_NODE is now running as a system service"
echo "🌐 Access dashboard: http://localhost:8081"
echo "🖥️ Desktop shortcut: Look for '🧙‍♂️ MAGI $MAGI_NODE' in applications"
echo ""
echo "🔧 The service will:"
echo "   ✅ Start automatically on boot"
echo "   ✅ Restart if it crashes"
echo "   ✅ Run in the background"
echo "   ✅ Log to system journal"
echo ""
echo "🧙‍♂️ The MAGI system is now operational!"
