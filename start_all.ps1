# BiliNote Development Environment Startup Script

Write-Host "Starting BiliNote development environment..." -ForegroundColor Green
Write-Host ""

# Get project root directory
$ProjectRoot = $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "BillNote_frontend"

# Read CONDA_ENV_NAME from .env file
$CondaEnvName = ""
$EnvFile = Join-Path $ProjectRoot ".env"
if (Test-Path $EnvFile) {
    $EnvContent = Get-Content $EnvFile
    foreach ($line in $EnvContent) {
        if ($line -match "^CONDA_ENV_NAME=([^#]*).*$") {
            $CondaEnvName = $matches[1].Trim()
            break
        }
    }
}

# Check if directories exist
if (!(Test-Path $BackendDir)) {
    Write-Host "Error: Backend directory not found at $BackendDir" -ForegroundColor Red
    exit 1
}

if (!(Test-Path $FrontendDir)) {
    Write-Host "Error: Frontend directory not found at $FrontendDir" -ForegroundColor Red
    exit 1
}

Write-Host "Starting backend server..." -ForegroundColor Yellow
Set-Location $BackendDir

# Start backend with or without conda environment
if ($CondaEnvName -and $CondaEnvName -ne "") {
    Write-Host "Activating conda environment '$CondaEnvName'..." -ForegroundColor Cyan
    $BackendProcess = Start-Process -FilePath "cmd" -ArgumentList "/k", "conda activate $CondaEnvName && python main.py" -PassThru -WindowStyle Normal
} else {
    Write-Host "No conda environment specified, starting without virtual environment..." -ForegroundColor Yellow
    $BackendProcess = Start-Process -FilePath "cmd" -ArgumentList "/k", "python main.py" -PassThru -WindowStyle Normal
}

Write-Host "Backend process started with PID: $($BackendProcess.Id)" -ForegroundColor Cyan

Start-Sleep -Seconds 2

Write-Host "Starting frontend server..." -ForegroundColor Yellow
Set-Location $FrontendDir

# Start frontend
$FrontendProcess = Start-Process -FilePath "cmd" -ArgumentList "/k", "pnpm dev" -PassThru -WindowStyle Normal

Write-Host "Frontend process started with PID: $($FrontendProcess.Id)" -ForegroundColor Cyan

Write-Host ""
Write-Host "Both frontend and backend servers are starting..." -ForegroundColor Green
Write-Host ""
Write-Host "Frontend will be available at: http://localhost:5173" -ForegroundColor Blue
Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Blue
Write-Host ""
Write-Host "You can close this window now. The servers will continue running in their respective windows." -ForegroundColor Green