@echo off
REM nAUDIT v3 - Launcher script
REM ========================================

echo ================================================
echo  nAUDIT v3 - Code Analysis Audit Tool
echo ================================================
echo.
echo Starting nAUDIT_v3.exe...
echo.

REM Activate virtual environment and run exe
cd /d "%~dp0"

if exist "dist\nAUDIT_v3.exe" (
    start "" "dist\nAUDIT_v3.exe"
    echo [OK] Application started
) else (
    echo [ERROR] nAUDIT_v3.exe not found!
    echo Please run: python build_exe_simple.py
    pause
)
