#!/bin/bash

echo "Starting BiliNote development environment..."
echo

# 后端目录
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/backend" && pwd)"
# 前端目录
FRONTEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/BillNote_frontend" && pwd)"

echo "Starting backend server..."
cd "$BACKEND_DIR"
gnome-terminal --title="Backend - FastAPI" -- bash -c "python main.py; exec bash" &

sleep 2

echo "Starting frontend server..."
cd "$FRONTEND_DIR"
gnome-terminal --title="Frontend - React" -- bash -c "pnpm dev; exec bash" &

echo
echo "Both frontend and backend servers are starting..."
echo
echo "Frontend will be available at: http://localhost:5173"
echo "Backend will be available at: http://localhost:8000"
echo
echo "You can close this window now."
read -p "Press Enter to continue..."