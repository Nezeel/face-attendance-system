#!/bin/bash
# Quick launcher for Face Attendance System
# Usage: ./RUN.sh [app|admin]

cd "$(dirname "$0")"

if [ "$1" = "admin" ]; then
    # Launch with admin panel
    . .venv311/bin/activate
    python3 admin_launcher.py --admin
else
    # Launch normal app
    open dist/'Face Attendance System.app'
fi
