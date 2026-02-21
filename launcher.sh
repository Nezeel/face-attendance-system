#!/bin/bash
# LAUNCHER - Opens Face Attendance System with various modes

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

print_usage() {
    echo "Face Attendance System Launcher"
    echo ""
    echo "Usage: ./launcher.sh [MODE]"
    echo ""
    echo "Modes:"
    echo "  (default)  - Opens bundled app"
    echo "  --dev      - Opens development version"
    echo "  --admin    - Opens app with admin panel"
    echo "  --help     - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./launcher.sh              # Opens bundled app"
    echo "  ./launcher.sh --dev        # Opens dev version"
    echo "  ./launcher.sh --admin      # Opens with admin"
    echo ""
}

case "$1" in
    --help|-h)
        print_usage
        ;;
    --dev)
        echo "🚀 Launching development version..."
        . .venv311/bin/activate
        python3 app.py
        ;;
    --admin)
        echo "🔐 Launching with admin panel..."
        . .venv311/bin/activate
        python3 admin_launcher.py --admin
        ;;
    *)
        echo "🎯 Launching Face Attendance System..."
        open dist/'Face Attendance System.app'
        sleep 1
        echo "✓ App is opening..."
        ;;
esac
