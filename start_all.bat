@echo off
echo ===================================================
echo   Starting LegalFlow AI Complete System
echo ===================================================

:: 1. Check & Start Ollama LLM Engine (Port 11434)
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/3] Starting Ollama Engine (Port 11434)...
    start "Ollama Engine (Port 11434)" cmd /c "ollama serve"
    timeout /t 3 >nul
) else (
    echo [1/3] Ollama Engine is already running.
)

:: 2. Ensure Port 8080 is dedicated to LegalFlow AI
echo [2/3] Starting LegalFlow Backend (Port 8080)...
start "LegalFlow Backend (Port 8080)" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload"
timeout /t 2 >nul

:: 3. Start React Frontend (Port 3000)
echo [3/3] Starting LegalFlow Frontend (Port 3000)...
start "LegalFlow Frontend (Port 3000)" cmd /k "cd /d %~dp0frontend && node node_modules\vite\bin\vite.js --host 0.0.0.0 --port 3000"

echo.
echo ===================================================
echo   All LegalFlow AI Services are Running!
echo   - Frontend: http://localhost:3000
echo   - Backend:  http://localhost:8080
echo   - Ollama:   http://localhost:11434 (llama3.2:latest)
echo ===================================================
pause
