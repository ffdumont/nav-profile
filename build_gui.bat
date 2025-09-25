@echo off
REM Build script for NavPro GUI executable
REM This script creates a standalone Windows executable using PyInstaller

echo Building NavPro GUI executable...
echo.

REM Clean previous builds
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Check if we have the airspace database
if not exist "data\airspaces.db" (
    echo WARNING: data\airspaces.db not found!
    echo The application may not work without the airspace database.
    echo.
)

REM Build the executable
echo Running PyInstaller...
pyinstaller navpro_gui.spec

REM Check if build was successful
if exist "dist\NavPro.exe" (
    echo.
    echo ================================
    echo BUILD SUCCESSFUL!
    echo ================================
    echo.
    echo Executable created: dist\NavPro.exe
    echo.
    echo To distribute:
    echo 1. Copy the entire 'dist' folder
    echo 2. Ensure data\airspaces.db is included
    echo 3. Install Google Earth Pro on target system
    echo.
    pause
) else (
    echo.
    echo ================================
    echo BUILD FAILED!
    echo ================================
    echo Check the output above for errors.
    echo.
    pause
)