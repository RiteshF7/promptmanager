#!/bin/bash
# Change to the directory where this script is located
cd "$(dirname "$0")"

echo "Stopping server..."

# Try to stop using the PID file first
if [ -f app.pid ]; then
    PID=$(cat app.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID 2>/dev/null
        echo "Server stopped (PID: $PID)"
        rm -f app.pid
        exit 0
    else
        rm -f app.pid
    fi
fi

# Fallback: find and kill process listening on port 5000
PID=$(lsof -ti:5000 2>/dev/null)
if [ -n "$PID" ]; then
    kill $PID 2>/dev/null
    echo "Server stopped (PID: $PID)"
else
    echo "No server process found on port 5000"
fi


