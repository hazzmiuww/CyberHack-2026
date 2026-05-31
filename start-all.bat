@echo off
REM SIMA QC System - All-in-One Startup Script (Windows Batch)
REM This script starts Backend API, Edge Camera, and Dashboard

echo.
echo ========================================
echo   SIMA QC System - Startup Script
echo ========================================
echo.

REM Check Python
echo [1/6] Checking prerequisites...
python --version >nul 2>&1
if errorlevel 1 (
    echo   X Python not found! Please install Python 3.8+
    echo     Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo   √ Python found

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo   X Node.js not found! Please install Node.js 24 LTS
    echo     Download: https://nodejs.org/
    pause
    exit /b 1
)
echo   √ Node.js found

REM Check pnpm
pnpm --version >nul 2>&1
if errorlevel 1 (
    echo   X pnpm not found! Installing...
    call corepack enable
    call corepack prepare pnpm@latest --activate
)
echo   √ pnpm found

REM Install Python dependencies
echo.
echo [2/6] Installing Python dependencies...
cd backend
if not exist venv (
    echo   Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
cd ..
echo   √ Python dependencies installed

REM Install Node.js dependencies
echo.
echo [3/6] Installing Node.js dependencies...
if not exist node_modules (
    call pnpm install
    echo   √ Node.js dependencies installed
) else (
    echo   √ Node.js dependencies already installed
)

REM Check YOLO model
echo.
echo [4/6] Checking YOLO model...
if not exist best.pt (
    echo   X YOLO model 'best.pt' not found!
    echo     Please place your trained YOLO model as 'best.pt' in the root directory
    pause
    exit /b 1
)
echo   √ YOLO model found

REM Start all processes
echo.
echo [5/6] Starting all services...
echo   This will open 3 terminal windows:
echo     1. Backend API (FastAPI)
echo     2. Edge Camera (YOLO Detection)
echo     3. Dashboard (Next.js)
echo.

REM Start Backend API
echo   Starting Backend API...
start "SIMA Backend API" cmd /k "cd /d %CD%\backend && venv\Scripts\activate.bat && python main.py"
timeout /t 3 /nobreak >nul

REM Start Edge Camera
echo   Starting Edge Camera...
start "SIMA Edge Camera" cmd /k "cd /d %CD% && backend\venv\Scripts\activate.bat && python edge_camera.py"
timeout /t 2 /nobreak >nul

REM Start Dashboard
echo   Starting Dashboard...
start "SIMA Dashboard" cmd /k "cd /d %CD% && pnpm run dev"
timeout /t 3 /nobreak >nul

echo.
echo [6/6] All services started!
echo.
echo ========================================
echo   System URLs:
echo ========================================
echo   Backend API:  http://localhost:8000
echo   Dashboard:    http://localhost:3000/qc-dashboard
echo   Network:      http://192.168.157.1:3000/qc-dashboard
echo ========================================
echo.
echo Press any key to stop all services...
pause >nul

echo.
echo Stopping all services...
taskkill /FI "WINDOWTITLE eq SIMA*" /F >nul 2>&1
echo All services stopped.
echo.
pause
