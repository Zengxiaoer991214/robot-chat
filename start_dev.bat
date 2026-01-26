@echo off
setlocal
title AI Chat System Launcher
color 0A

echo ========================================================
echo        AI Group Chat System - One-Click Start
echo ========================================================
echo.

:: Get project root directory
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

:: Check if backend directory exists
if not exist "backend" (
    echo [ERROR] Backend directory not found!
    echo Current dir: %CD%
    pause
    exit /b
)

:: Check if frontend directory exists
if not exist "frontend" (
    echo [ERROR] Frontend directory not found!
    echo Current dir: %CD%
    pause
    exit /b
)

echo [1/2] Launching Backend Server (Port 8000)...
cd backend
:: Start backend in a new window
start "AI Chat Backend" cmd /k "title Backend Server && echo Starting Uvicorn... && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
cd /d "%PROJECT_ROOT%"

echo [2/2] Launching Frontend Server...
cd frontend
:: Start frontend in a new window
start "AI Chat Frontend" cmd /k "title Frontend Server && echo Starting Vite... && npm run dev"
cd /d "%PROJECT_ROOT%"

echo.
echo ========================================================
echo [SUCCESS] Services are launching in separate windows.
echo.
echo Please wait a few seconds for servers to initialize...
echo.
echo - Frontend Access: http://localhost:5173 (Check Frontend window)
echo - Backend Docs:    http://localhost:8000/docs
echo.
echo You can create Agents and Rooms once the UI loads.
echo ========================================================
echo.
pause
