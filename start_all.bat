@echo off
title BiliNote Development Environment

echo Starting BiliNote development environment...
echo.

echo Starting backend server...
start "Backend - FastAPI" /D "%~dp0backend" cmd /k "python main.py"

timeout /t 2 /nobreak >nul

echo Starting frontend server...
start "Frontend - React" /D "%~dp0BillNote_frontend" cmd /k "pnpm dev"

echo.
echo Both frontend and backend servers are starting...
echo.
echo Frontend will be available at: http://localhost:5173
echo Backend will be available at: http://localhost:8000
echo.
echo You can close this window now.
pause