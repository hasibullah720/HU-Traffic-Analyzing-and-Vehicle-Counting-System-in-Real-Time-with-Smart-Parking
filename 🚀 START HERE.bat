@echo off
REM ===================================================
REM  HU Traffic Analyzing System - One-Click Launcher
REM ===================================================

title HU Traffic Analyzing System Launcher
color 0B

cls
echo.
echo  ╔═══════════════════════════════════════════════════════╗
echo  ║                                                       ║
echo  ║     HU TRAFFIC ANALYZING SYSTEM                       ║
echo  ║     Final Year Project - Quick Start                  ║
echo  ║                                                       ║
echo  ╚═══════════════════════════════════════════════════════╝
echo.
echo  [1] Starting system...
echo.

REM Activate conda environment
call C:\Users\HASIB_ULLAH\miniconda3\Scripts\activate.bat fyp >nul 2>&1

if errorlevel 1 (
    color 0C
    echo  [✗] ERROR: Could not activate conda environment 'fyp'
    echo.
    echo  Please ensure:
    echo    - Miniconda/Anaconda is installed
    echo    - Environment 'fyp' exists
    echo.
    echo  Run this to create environment:
    echo    conda create -n fyp python=3.11.14
    echo.
    pause
    exit /b 1
)

echo  [✓] Environment activated
echo.

REM Change to project directory
cd /d "%~dp0"

echo  [2] Launching application...
echo.
echo  ═══════════════════════════════════════════════════════
echo.

REM Run the application
python main_new.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo  ═══════════════════════════════════════════════════════
    echo.
    color 0E
    echo  [!] Application exited with errors
    echo.
    pause
) else (
    echo.
    echo  ═══════════════════════════════════════════════════════
    echo.
    echo  [✓] Application closed normally
    echo.
    timeout /t 3 >nul
)

exit
