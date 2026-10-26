@echo off
echo Starting LegalFlow AI Frontend Dev Server on Port 3000...
cd /d "%~dp0frontend"
node node_modules\vite\bin\vite.js --host 127.0.0.1 --port 3000
pause
