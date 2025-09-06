@echo off
setlocal enabledelayedexpansion
title BiliNote Development Environment

echo Starting BiliNote development environment...
echo.

REM Read CONDA_ENV_NAME from .env file
set "CONDA_ENV_NAME="
if exist ".env" (
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        if "%%a"=="CONDA_ENV_NAME" (
            set "CONDA_ENV_NAME=%%b"
            REM Remove everything after # or space
            for /f "tokens=1" %%c in ("!CONDA_ENV_NAME!") do set "CONDA_ENV_NAME=%%c"
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
echo Frontend will be available at: http://localhost:5173
echo Backend will be available at: http://localhost:8000
echo.
echo You can close this window now.
pause