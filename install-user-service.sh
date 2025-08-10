#!/bin/bash
"""
🧙‍♂️ MAGI User Service Installer - No sudo required
Creates user-level systemd service and desktop shortcut
"""

# Configuration
MAGI_USER=$(whoami)
MAGI_HOME=$(pwd)
MAGI_NODE="GASPAR"
SERVICE_NAME="magi-${MAGI_NODE,,}"

echo "🧙‍♂️ MAGI User Service Installer (No sudo required)"
echo "=================================================="
echo "User: $MAGI_USER"
echo "Directory: $MAGI_HOME"
echo ""

# Ask for node name
read -p "Enter MAGI node name (GASPAR/MELCHIOR/BALTASAR) [$MAGI_NODE]: " input_node
if [[ ! -z "$input_node" ]]; then
    MAGI_NODE="$input_node"
    SERVICE_NAME="magi-${MAGI_NODE,,}"
fi

echo "🔧 Creating user systemd service..."

# Create user systemd directory
mkdir -p ~/.config/systemd/user

# Create user systemd service file
cat > ~/.config/systemd/user/${SERVICE_NAME}.service <<EOF
[Unit]
Description=🧙‍♂️ MAGI $MAGI_NODE Monitoring Node
Documentation=https://github.com/ismaelucky342/MAGI
After=graphical-session.target

[Service]
Type=simple
WorkingDirectory=$MAGI_HOME
ExecStart=/usr/bin/python3 $MAGI_HOME/magi-node.py $MAGI_NODE
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Environment
Environment=PYTHONUNBUFFERED=1
Environment=MAGI_NODE=$MAGI_NODE

[Install]
WantedBy=default.target
EOF

echo "✅ User service file created: ~/.config/systemd/user/${SERVICE_NAME}.service"

# Reload user systemd and enable service
echo "🔄 Enabling user service..."
systemctl --user daemon-reload
systemctl --user enable ${SERVICE_NAME}

# Enable lingering so service starts on boot
loginctl enable-linger $MAGI_USER

echo "🚀 Starting user service..."
systemctl --user start ${SERVICE_NAME}

# Check status
echo "📊 Service status:"
systemctl --user status ${SERVICE_NAME} --no-pager -l

echo ""
echo "🎯 User service commands:"
echo "   Start:   systemctl --user start ${SERVICE_NAME}"
echo "   Stop:    systemctl --user stop ${SERVICE_NAME}"
echo "   Restart: systemctl --user restart ${SERVICE_NAME}"
echo "   Status:  systemctl --user status ${SERVICE_NAME}"
echo "   Logs:    journalctl --user -u ${SERVICE_NAME} -f"
echo ""

# Create desktop shortcut
echo "🖥️ Creating desktop shortcut..."

# Create simple PNG icon if tools available
if command -v convert &> /dev/null && [[ -f "$MAGI_HOME/magi-icon.svg" ]]; then
    convert "$MAGI_HOME/magi-icon.svg" -resize 64x64 "$MAGI_HOME/magi-icon.png" 2>/dev/null
    ICON_PATH="$MAGI_HOME/magi-icon.png"
elif [[ -f "$MAGI_HOME/magi-icon.svg" ]]; then
    ICON_PATH="$MAGI_HOME/magi-icon.svg"
else
    # Use default system icon
    ICON_PATH="applications-system"
fi

# Create desktop entry
mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/magi-${MAGI_NODE,,}.desktop <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=🧙‍♂️ MAGI $MAGI_NODE
Comment=MAGI Distributed Monitoring - $MAGI_NODE Node Dashboard
Exec=xdg-open http://localhost:8081
Icon=$ICON_PATH
Terminal=false
Categories=System;Monitor;Network;
Keywords=magi;monitoring;system;evangelion;
StartupNotify=true
EOF

# Make desktop file executable
chmod +x ~/.local/share/applications/magi-${MAGI_NODE,,}.desktop

# Update desktop database if available
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
fi

echo "✅ Desktop shortcut created: ~/.local/share/applications/magi-${MAGI_NODE,,}.desktop"

# Create desktop shortcut on desktop if folder exists
if [[ -d ~/Desktop ]]; then
    cp ~/.local/share/applications/magi-${MAGI_NODE,,}.desktop ~/Desktop/
    chmod +x ~/Desktop/magi-${MAGI_NODE,,}.desktop
    echo "✅ Shortcut also added to Desktop folder"
fi

# Create a simple launcher script
cat > "$MAGI_HOME/launch-magi.sh" <<EOF
#!/bin/bash
# 🧙‍♂️ MAGI Launcher Script
cd "$MAGI_HOME"
echo "🧙‍♂️ Starting MAGI $MAGI_NODE..."
echo "🌐 Dashboard will open at: http://localhost:8081"
echo ""
sleep 2
xdg-open "http://localhost:8081" 2>/dev/null &
exit 0
EOF

chmod +x "$MAGI_HOME/launch-magi.sh"

echo ""
echo "🎉 MAGI User Service Installation Complete!"
echo "=========================================="
echo ""
echo "🚀 MAGI $MAGI_NODE is now running as a user service"
echo "🌐 Access dashboard: http://localhost:8081"
echo "🖥️ Desktop shortcut: Look for '🧙‍♂️ MAGI $MAGI_NODE' in applications menu"
echo "🖱️ Desktop icon: Double-click 'MAGI $MAGI_NODE' on desktop (if created)"
echo ""
echo "🔧 The service will:"
echo "   ✅ Start when you log in"
echo "   ✅ Restart if it crashes"
echo "   ✅ Run in the background"
echo "   ✅ No sudo permissions needed"
echo ""
echo "🧙‍♂️ The MAGI system is ready for operation!"
echo ""
echo "💡 Quick test: Click the desktop shortcut or run:"
echo "   $MAGI_HOME/launch-magi.sh"
