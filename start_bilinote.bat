@echo off
setlocal enabledelayedexpansion
title BiliNote Development Environment

echo Starting BiliNote development environment...
echo.

REM Read variables from .env file
set "CONDA_ENV_NAME="
set "BACKEND_PORT=8492"
set "VITE_FRONTEND_PORT=3015"

if exist ".env" (
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        if "%%a"=="CONDA_ENV_NAME" (
            set "CONDA_ENV_NAME=%%b"
            for /f "tokens=1" %%c in ("!CONDA_ENV_NAME!") do set "CONDA_ENV_NAME=%%c"
        )
        if "%%a"=="BACKEND_PORT" (
            set "BACKEND_PORT=%%b"
            for /f "tokens=1" %%c in ("!BACKEND_PORT!") do set "BACKEND_PORT=%%c"
        )
        if "%%a"=="VITE_FRONTEND_PORT" (
            set "VITE_FRONTEND_PORT=%%b"
            for /f "tokens=1" %%c in ("!VITE_FRONTEND_PORT!") do set "VITE_FRONTEND_PORT=%%c"
        )
    )
)

echo Starting backend server...
if defined CONDA_ENV_NAME (
    if not "%CONDA_ENV_NAME%"=="" (
        echo Activating conda environment '%CONDA_ENV_NAME%'...
        start "Backend - FastAPI" /D "%~dp0backend" cmd /k "call conda activate %CONDA_ENV_NAME% && python main.py"
    ) else (
        echo No conda environment specified, starting without virtual environment...
        start "Backend - FastAPI" /D "%~dp0backend" cmd /k "python main.py"
    )
) else (
    echo No conda environment specified, starting without virtual environment...
    start "Backend - FastAPI" /D "%~dp0backend" cmd /k "python main.py"
)

timeout /t 2 /nobreak >nul

echo Starting frontend server...
start "Frontend - React" /D "%~dp0BillNote_frontend" cmd /k "pnpm dev"

echo.
echo Both frontend and backend servers are starting...
echo.
echo Frontend will be available at: http://localhost:!VITE_FRONTEND_PORT!
echo Backend will be available at: http://localhost:!BACKEND_PORT!
echo.
echo You can close this window now.
pause
