#!/bin/bash
# Restart script for Neural Memory App (debug-test-001)
# Run this to restart the server with fresh database

echo "Stopping any existing server..."
pkill -f "server.py" 2>/dev/null || true

echo "Removing old database..."
rm -f /c/Users/kafsh/neural-memory-app-debug-test-001/data/memories.db

echo "Starting fresh server on port 8080..."
cd /c/Users/kafsh/neural-memory-app-debug-test-001
python server.py 8080 &

sleep 2
echo "Testing server..."
curl -s http://localhost:8080/health | python -m json.tool