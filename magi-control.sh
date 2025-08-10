#!/bin/bash
# 🧙‍♂️ MAGI Service Manager - Easy control of MAGI services

SERVICE_NAME="magi-gaspar"
DASHBOARD_URL="http://localhost:8081"

show_status() {
    echo "🧙‍♂️ MAGI Service Status"
    echo "====================="
    systemctl --user status $SERVICE_NAME --no-pager -l
    echo ""
    echo "🌐 Dashboard: $DASHBOARD_URL"
}

show_logs() {
    echo "🧙‍♂️ MAGI Live Logs (Ctrl+C to exit)"
    echo "=================================="
    journalctl --user -u $SERVICE_NAME -f
}

start_service() {
    echo "🚀 Starting MAGI service..."
    systemctl --user start $SERVICE_NAME
    sleep 2
    show_status
}

stop_service() {
    echo "🛑 Stopping MAGI service..."
    systemctl --user stop $SERVICE_NAME
    echo "✅ MAGI service stopped"
}

restart_service() {
    echo "🔄 Restarting MAGI service..."
    systemctl --user restart $SERVICE_NAME
    sleep 2
    show_status
}

open_dashboard() {
    echo "🌐 Opening MAGI dashboard..."
    xdg-open "$DASHBOARD_URL" 2>/dev/null &
    echo "✅ Dashboard should open in your browser"
}

show_help() {
    echo "🧙‍♂️ MAGI Service Manager"
    echo "======================"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  status    - Show service status"
    echo "  start     - Start MAGI service"
    echo "  stop      - Stop MAGI service"
    echo "  restart   - Restart MAGI service"
    echo "  logs      - Show live logs"
    echo "  open      - Open dashboard in browser"
    echo "  help      - Show this help"
    echo ""
    echo "🌐 Dashboard URL: $DASHBOARD_URL"
    echo "📋 Service name: $SERVICE_NAME"
}

case "$1" in
    status)
        show_status
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    logs)
        show_logs
        ;;
    open)
        open_dashboard
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        echo "🧙‍♂️ MAGI Service Manager"
        echo "======================"
        echo ""
        show_status
        echo ""
        echo "💡 Use '$0 help' for available commands"
        echo "🌐 Use '$0 open' to open dashboard"
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "💡 Use '$0 help' for available commands"
        exit 1
        ;;
esac
