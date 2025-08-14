#!/bin/bash

# CMBAgent Service Control Script
BASE_DIR="/Users/chadiaitekioui/cmbagent-info"
SERVICE_SCRIPT="$BASE_DIR/scripts/optimized-auto-update.py"
LOG_FILE="$BASE_DIR/optimized_update.log"
PID_FILE="$BASE_DIR/service.pid"

function get_service_pid() {
    ps aux | grep "optimized-auto-update.py" | grep -v grep | awk '{print $2}'
}

function start_service() {
    local pid=$(get_service_pid)
    if [ -n "$pid" ]; then
        echo "🟡 Service is already running (PID: $pid)"
        return 1
    fi
    
    echo "🚀 Starting CMBAgent auto-update service..."
    cd "$BASE_DIR"
    nohup python3 "$SERVICE_SCRIPT" 10 > "$LOG_FILE" 2>&1 &
    local new_pid=$!
    echo $new_pid > "$PID_FILE"
    echo "✅ Service started (PID: $new_pid)"
    echo "📁 Log file: $LOG_FILE"
}

function stop_service() {
    local pid=$(get_service_pid)
    if [ -z "$pid" ]; then
        echo "🔴 Service is not running"
        return 1
    fi
    
    echo "🛑 Stopping CMBAgent auto-update service (PID: $pid)..."
    kill $pid
    rm -f "$PID_FILE"
    echo "✅ Service stopped"
}

function restart_service() {
    echo "🔄 Restarting CMBAgent auto-update service..."
    stop_service
    sleep 2
    start_service
}

function show_status() {
    local pid=$(get_service_pid)
    echo "=============================================="
    echo "CMBAgent Auto-Update Service Status"
    echo "=============================================="
    
    if [ -n "$pid" ]; then
        echo "🟢 Status: Running (PID: $pid)"
        echo "📁 Log file: $LOG_FILE"
        echo "⏰ Check interval: 10 minutes (optimized)"
        
        if [ -f "$LOG_FILE" ]; then
            echo ""
            echo "📋 Recent logs (last 5 lines):"
            echo "----------------------------------------------"
            tail -5 "$LOG_FILE"
        fi
    else
        echo "🔴 Status: Stopped"
    fi
    echo "=============================================="
}

function show_logs() {
    local lines=${1:-20}
    if [ -f "$LOG_FILE" ]; then
        echo "📋 Last $lines log entries:"
        echo "=============================================="
        tail -$lines "$LOG_FILE"
    else
        echo "📋 No log file found"
    fi
}

function show_help() {
    echo "CMBAgent Optimized Service Control"
    echo "Usage: $0 {start|stop|restart|status|logs [lines]|help}"
    echo ""
    echo "Commands:"
    echo "  start    - Start the auto-update service"
    echo "  stop     - Stop the auto-update service"
    echo "  restart  - Restart the auto-update service"
    echo "  status   - Show service status and recent logs"
    echo "  logs [n] - Show last n log lines (default: 20)"
    echo "  help     - Show this help message"
}

# Main script logic
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs $2
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        show_help
        exit 1
        ;;
esac
