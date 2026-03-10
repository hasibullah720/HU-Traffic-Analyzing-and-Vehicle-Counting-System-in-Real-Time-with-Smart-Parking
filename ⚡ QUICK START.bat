@echo off
title HU Traffic System - Quick Launch
color 0B

echo.
echo ╔════════════════════════════════════════╗
echo ║  HU TRAFFIC ANALYZING SYSTEM           ║
echo ║  Quick Launch - GUI Mode               ║
echo ╚════════════════════════════════════════╝
echo.
echo Starting GUI...
echo.

cd /d "%~dp0"
python quick_start.py

if errorlevel 1 (
    echo.
    echo ✗ Error occurred!
    pause
)
