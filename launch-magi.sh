#!/bin/bash
# 🧙‍♂️ MAGI Launcher Script
cd "/home/nirmata/EngineerLife/MAGI"
echo "🧙‍♂️ Starting MAGI GASPAR..."
echo "🌐 Dashboard will open at: http://localhost:8081"
echo ""
sleep 2
xdg-open "http://localhost:8081" 2>/dev/null &
exit 0
