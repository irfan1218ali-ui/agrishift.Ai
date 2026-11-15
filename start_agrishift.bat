@echo off
title AgriShift AI - Platform Launcher
chcp 65001 > nul
cd /d "%~dp0"

echo ======================================================================
echo                     AGRISHIFT AI - DESKTOP LAUNCHER
echo          Real Earth Observation ^& Agronomic Crop Rotation
echo ======================================================================
echo.

:: Detect virtual environment python or system python
set "VENV_PY=%~dp0.venv\Scripts\python.exe"

if exist "%VENV_PY%" (
    set "PY_CMD=%VENV_PY%"
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PY_CMD=python"
    ) else (
        echo [ERROR] Python was not found in .venv or system PATH.
        echo Please ensure Python 3.11+ is installed.
        echo.
        pause
        exit /b 1
    )
)

"%PY_CMD%" "%~dp0scripts\launch_desktop.py"

if %ERRORLEVEL% neq 0 (
    echo.
    echo Application exited with code %ERRORLEVEL%.
    pause
)
