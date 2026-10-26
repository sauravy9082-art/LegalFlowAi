@echo off
echo Starting LegalFlow AI FastAPI Backend Server on Port 8080...
cd /d "%~dp0backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
pause
