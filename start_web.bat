@echo off
echo ==============================================================
echo    Befree Statement Intelligence - Launching Full Stack
echo ==============================================================
echo 1. Launching FastAPI Backend (Port 8000)...
start "Befree Backend" cmd /k "python -m uvicorn server:app --port 8000 --host 0.0.0.0"

echo 2. Launching React Vite Frontend (Port 3000)...
cd frontend
start "Befree Frontend" cmd /k "npm run dev"

echo.
echo Application ready!
echo Open your browser to: http://localhost:3000
echo ==============================================================
pause
