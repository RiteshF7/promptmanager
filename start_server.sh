#!/bin/bash
# Change to the directory where this script is located
cd "$(dirname "$0")"

# Run the Flask app in the background
nohup python3 app.py > app.log 2>&1 &

# Save the process ID
echo $! > app.pid

echo "Server started in background. PID: $(cat app.pid)"
echo "Logs are being written to app.log"


