@echo off
echo ===================================================
echo   Starting Ollama LLM Service (Port 11434)
echo ===================================================

curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Ollama serve...
    start "Ollama Serve" "C:\Users\shiva\AppData\Local\Programs\Ollama\ollama.exe" serve
    timeout /t 3 >nul
    echo Ollama service started successfully!
) else (
    echo Ollama is ALREADY running and online on port 11434!
)

echo.
echo Verifying model availability:
"C:\Users\shiva\AppData\Local\Programs\Ollama\ollama.exe" list
echo.
echo You can now refresh your LegalFlow AI browser tab (http://localhost:3000).
pause
