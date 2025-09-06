#!/bin/bash

echo "Starting BiliNote development environment..."
echo

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 后端目录
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/backend" && pwd)"
# 前端目录
FRONTEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/BillNote_frontend" && pwd)"

# 读取.env文件中的CONDA_ENV_NAME配置
CONDA_ENV_NAME=""
if [ -f "$PROJECT_ROOT/.env" ]; then
    CONDA_ENV_NAME=$(grep "^CONDA_ENV_NAME=" "$PROJECT_ROOT/.env" | cut -d'=' -f2 | tr -d '[:space:]')
fi

echo "Starting backend server..."
cd "$BACKEND_DIR"

if [ -n "$CONDA_ENV_NAME" ] && [ "$CONDA_ENV_NAME" != "" ]; then
    echo "Activating conda environment '$CONDA_ENV_NAME'..."
    gnome-terminal --title="Backend - FastAPI" -- bash -c "source ~/anaconda3/etc/profile.d/conda.sh && conda activate $CONDA_ENV_NAME && python main.py; exec bash" &
else
    echo "No conda environment specified, starting without virtual environment..."
    gnome-terminal --title="Backend - FastAPI" -- bash -c "python main.py; exec bash" &
fi

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