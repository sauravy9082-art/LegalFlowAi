# LegalGuard AI - One-Click Launcher Script

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "            Starting LegalGuard AI System                   " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$ROOT_DIR = $PSScriptRoot

# 1. Start Backend FastAPI Server on Port 8080
Write-Host "[1/2] Launching Python FastAPI Backend on http://localhost:8080 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ROOT_DIR\backend'; python -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload"

Start-Sleep -Seconds 2

# 2. Start Frontend React Vite Server on Port 3000
Write-Host "[2/2] Launching React Frontend Server on http://localhost:3000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ROOT_DIR\frontend'; node node_modules\vite\bin\vite.js --host 127.0.0.1 --port 3000"

Start-Sleep -Seconds 3

# 3. Open Web Browser automatically
Write-Host "Opening LegalGuard AI in browser..." -ForegroundColor Yellow
Start-Process "http://localhost:3000"

Write-Host "LegalGuard AI is running!" -ForegroundColor Cyan
