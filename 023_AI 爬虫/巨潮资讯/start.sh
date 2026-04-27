#!/bin/bash
# CNINFO Announcement Crawler - Startup Script (Linux/Mac)

echo "=============================================="
echo "  CNINFO Announcement Crawler - Starting..."
echo "=============================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[Error] python3 not found. Please install Python 3.8+"
    exit 1
fi

# Install dependencies
echo "[1/2] Installing dependencies..."
pip3 install -r requirements.txt --break-system-packages -q

# Start server
echo "[2/2] Starting server..."
echo ""
echo "Server URL: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python3 server.py
