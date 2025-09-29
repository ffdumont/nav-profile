@echo off
title AirCheck - Choose Version
cd /d "%~dp0"

:menu
cls
echo ========================================
echo       AirCheck Flight Analysis Tool
echo ========================================
echo.
echo Choose your preferred interface:
echo.
echo 1. GUI Version (Graphical Interface)
echo 2. CLI Version (Command Line)
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo Starting GUI version...
    AirCheck.exe
    goto end
)
if "%choice%"=="2" (
    echo Starting CLI version...
    echo.
    echo Type "AirCheckCLI --help" for available commands
    echo.
    cmd /k AirCheckCLI
    goto end
)
if "%choice%"=="3" (
    goto end
)
echo Invalid choice. Please try again.
pause
goto menu

:end
