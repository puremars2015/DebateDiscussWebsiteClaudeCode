@echo off
echo Starting Debate Platform...
echo.

echo Starting Frontend Server (Port 8080)...
start "Frontend Server" powershell -Command "cd '%~dp0frontend'; python -m http.server 8080"

echo Waiting for frontend to start...
timeout /t 3 /nobreak > nul

echo Starting Backend Server (Port 5000)...
cd "%~dp0backend"
python app.py

pause