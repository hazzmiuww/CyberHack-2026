#!/usr/bin/env pwsh
<#
.SYNOPSIS
    SIMA QC System - All-in-One Startup Script
    
.DESCRIPTION
    This script starts all components of the SIMA QC system:
    1. FastAPI Backend (Python)
    2. Edge Camera Detection (Python + YOLO)
    3. Next.js Dashboard (Node.js)
    
.NOTES
    Press Ctrl+C to stop all processes
#>

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SIMA QC System - Startup Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check prerequisites
Write-Host "[1/6] Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.8+" -ForegroundColor Red
    Write-Host "    Download: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✓ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js not found! Please install Node.js 24 LTS" -ForegroundColor Red
    Write-Host "    Download: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check pnpm
try {
    $pnpmVersion = pnpm --version 2>&1
    Write-Host "  ✓ pnpm: v$pnpmVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ pnpm not found! Installing..." -ForegroundColor Yellow
    corepack enable
    corepack prepare pnpm@latest --activate
    Write-Host "  ✓ pnpm installed" -ForegroundColor Green
}

# Install Python dependencies
Write-Host "`n[2/6] Installing Python dependencies..." -ForegroundColor Yellow
Set-Location backend
if (!(Test-Path "venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Gray
    python -m venv venv
}
Write-Host "  Activating virtual environment..." -ForegroundColor Gray
.\venv\Scripts\Activate.ps1
Write-Host "  Installing requirements..." -ForegroundColor Gray
pip install -q -r requirements.txt
Set-Location ..
Write-Host "  ✓ Python dependencies installed" -ForegroundColor Green

# Install Node.js dependencies
Write-Host "`n[3/6] Installing Node.js dependencies..." -ForegroundColor Yellow
if (!(Test-Path "node_modules")) {
    pnpm install
    Write-Host "  ✓ Node.js dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ✓ Node.js dependencies already installed" -ForegroundColor Green
}

# Check for YOLO model
Write-Host "`n[4/6] Checking YOLO model..." -ForegroundColor Yellow
if (!(Test-Path "best.pt")) {
    Write-Host "  ✗ YOLO model 'best.pt' not found!" -ForegroundColor Red
    Write-Host "    Please place your trained YOLO model as 'best.pt' in the root directory" -ForegroundColor Yellow
    exit 1
}
Write-Host "  ✓ YOLO model found" -ForegroundColor Green

# Start all processes
Write-Host "`n[5/6] Starting all services..." -ForegroundColor Yellow
Write-Host "  This will open 3 terminal windows:" -ForegroundColor Gray
Write-Host "    1. Backend API (FastAPI)" -ForegroundColor Gray
Write-Host "    2. Edge Camera (YOLO Detection)" -ForegroundColor Gray
Write-Host "    3. Dashboard (Next.js)" -ForegroundColor Gray

# Start Backend API
Write-Host "`n  Starting Backend API..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\venv\Scripts\Activate.ps1; python main.py"
Start-Sleep -Seconds 3

# Start Edge Camera
Write-Host "  Starting Edge Camera..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\backend\venv\Scripts\Activate.ps1; python edge_camera.py"
Start-Sleep -Seconds 2

# Start Dashboard
Write-Host "  Starting Dashboard..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; pnpm run dev"
Start-Sleep -Seconds 3

Write-Host "`n[6/6] All services started!" -ForegroundColor Green
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  System URLs:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "  Dashboard:    http://localhost:3000/qc-dashboard" -ForegroundColor White
Write-Host "  Network:      http://192.168.157.1:3000/qc-dashboard" -ForegroundColor White
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Press any key to stop all services..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "`nStopping all services..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.MainWindowTitle -match "python|pnpm"} | Stop-Process -Force
Write-Host "All services stopped.`n" -ForegroundColor Green
