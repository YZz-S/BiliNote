# BiliNote Development Environment Startup Script

Write-Host "Starting BiliNote development environment..." -ForegroundColor Green
Write-Host ""

# 获取项目根目录
$ProjectRoot = $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "BillNote_frontend"

# 检查目录是否存在
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

# 启动后端
$BackendProcess = Start-Process -FilePath "python" -ArgumentList "main.py" -PassThru -WindowStyle Normal

Write-Host "Backend process started with PID: $($BackendProcess.Id)" -ForegroundColor Cyan

Start-Sleep -Seconds 2

Write-Host "Starting frontend server..." -ForegroundColor Yellow
Set-Location $FrontendDir

# 启动前端
$FrontendProcess = Start-Process -FilePath "pnpm" -ArgumentList "dev" -PassThru -WindowStyle Normal

Write-Host "Frontend process started with PID: $($FrontendProcess.Id)" -ForegroundColor Cyan

Write-Host ""
Write-Host "Both frontend and backend servers are starting..." -ForegroundColor Green
Write-Host ""
Write-Host "Frontend will be available at: http://localhost:5173" -ForegroundColor Blue
Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Blue
Write-Host ""
Write-Host "You can close this window now. The servers will continue running in their respective windows." -ForegroundColor Green