# 文件名：start_server.ps1
# 功能说明：一键启动蓝图大师（生产环境模式）
# 核心功能：
# 1. 启动后端 Waitress 服务
# 2. 启动前端 Node Express 服务
# 3. 自动打开浏览器

$ErrorActionPreference = "Stop"

Write-Host "🚀 正在启动蓝图大师 (生产环境模式)..." -ForegroundColor Cyan

# 1. 检查前端是否已构建
$FrontendDist = Join-Path $PSScriptRoot "frontend\dist"
if (-not (Test-Path $FrontendDist)) {
    Write-Host "⚠️  检测到前端未构建，正在执行 npm run build..." -ForegroundColor Yellow
    Push-Location "frontend"
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Error "前端构建失败，请检查错误日志。"
    }
    Pop-Location
}

# 2. 启动后端服务 (后台运行)
Write-Host "📦 正在启动后端服务 (Port 5000)..." -ForegroundColor Green
$BackendScript = Join-Path $PSScriptRoot "backend\run_prod.py"
# 使用 Start-Process 在新窗口中运行后端，方便查看日志，或者使用 -WindowStyle Hidden 隐藏
Start-Process python -ArgumentList "$BackendScript" -WindowStyle Minimized

# 等待几秒确保后端启动
Start-Sleep -Seconds 3

# 3. 启动前端服务 (当前窗口运行，或者新窗口)
Write-Host "🌐 正在启动前端服务 (Port 8080)..." -ForegroundColor Green
$FrontendServer = Join-Path $PSScriptRoot "frontend\server.js"

Write-Host "`n✅ 服务已启动！" -ForegroundColor Cyan
Write-Host "👉 请访问: http://localhost:8080" -ForegroundColor Cyan
Write-Host "👉 公网访问请使用服务器IP: http://<Your-Server-IP>:8080" -ForegroundColor Cyan
Write-Host "`n(按 Ctrl+C 停止前端服务，后端服务需手动关闭窗口)" -ForegroundColor Gray

# 启动 Node 服务
node $FrontendServer
