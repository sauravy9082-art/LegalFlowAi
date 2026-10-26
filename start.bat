@echo off
echo ===================================================
echo   Starting LegalFlow AI (Ollama + Backend + Frontend)
echo ===================================================

:: 1. Ensure Ollama is running
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Ollama Engine...
    start "Ollama Engine (Port 11434)" cmd /c "ollama serve"
    timeout /t 3 >nul
)

:: 2. Start Backend
start "LegalFlow FastAPI Backend (Port 8080)" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload"
timeout /t 3 >nul

:: 3. Start Frontend
start "LegalFlow React Frontend (Port 3000)" cmd /k "cd frontend && node node_modules\vite\bin\vite.js --host 0.0.0.0 --port 3000"
echo Backend running on http://0.0.0.0:8080
echo Frontend running on http://0.0.0.0:3000
