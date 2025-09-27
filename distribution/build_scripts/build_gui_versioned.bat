@echo off
REM Enhanced Build script for AirCheck GUI executable with version management
REM Usage: build_gui_versioned.bat [version]
REM Example: build_gui_versioned.bat 1.2.1

setlocal enabledelayedexpansion

REM Get version parameter or use default
set VERSION=%1
if "%VERSION%"=="" (
    echo No version specified, using current version from code...
    for /f "tokens=*" %%i in ('python -c "import sys; sys.path.append('../../'); import navpro; print(navpro.__version__)"') do set VERSION=%%i
    echo Current version: !VERSION!
    echo.
) else (
    echo Building with version: %VERSION%
    echo.
    
    REM Update version in navpro/__init__.py
    echo Updating version in navpro/__init__.py...
    python -c "
import sys
import os
sys.path.append('../../')

# Read the file
with open('../../navpro/__init__.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace version
import re
content = re.sub(r'__version__\s*=\s*[\"''][\d.]+[\"'']', '__version__ = \"%VERSION%\"', content)

# Write back
with open('../../navpro/__init__.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Version updated successfully!')
"
    
    REM Update fallback version in version.py
    echo Updating fallback version in version.py...
    python -c "
import sys
import os
sys.path.append('../../')

# Read the file
with open('../../navpro/version.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace fallback version
import re
content = re.sub(r'return\s+[\"''][\d.]+[\"'']', 'return \"%VERSION%\"', content)

# Write back
with open('../../navpro/version.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fallback version updated successfully!')
"
    echo.
)

echo Building AirCheck GUI executable v!VERSION!...
echo.

REM Clean previous builds
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Check if we have the airspace database
if not exist "../../data/airspaces.db" (
    echo WARNING: ../../data/airspaces.db not found!
    echo The application may not work without the airspace database.
    echo.
)

REM Build the executable
echo Running PyInstaller...
pyinstaller aircheck_gui.spec

REM Check if build was successful
if exist "dist\AirCheck.exe" (
    echo.
    echo ================================
    echo BUILD SUCCESSFUL!
    echo ================================
    echo.
    echo Executable created: dist\AirCheck.exe
    echo Version: !VERSION!
    echo.
    echo To distribute:
    echo 1. Copy the entire 'dist' folder
    echo 2. Ensure data\airspaces.db is included
    echo 3. Install Google Earth Pro on target system
    echo.
    
    REM Optional: Create versioned output directory
    if not exist "releases" mkdir releases
    set RELEASE_DIR=releases\AirCheck_v!VERSION!
    if exist "!RELEASE_DIR!" rmdir /s /q "!RELEASE_DIR!"
    mkdir "!RELEASE_DIR!"
    copy "dist\AirCheck.exe" "!RELEASE_DIR!\"
    copy "../../data/airspaces.db" "!RELEASE_DIR!\"
    mkdir "!RELEASE_DIR!\sample_data"
    echo Place your KML flight profiles in this folder > "!RELEASE_DIR!\sample_data\Place_KML_files_here.txt"
    echo @echo off > "!RELEASE_DIR!\Launch_AirCheck.bat"
    echo cd /d "%%~dp0" >> "!RELEASE_DIR!\Launch_AirCheck.bat"
    echo AirCheck.exe >> "!RELEASE_DIR!\Launch_AirCheck.bat"
    echo pause >> "!RELEASE_DIR!\Launch_AirCheck.bat"
    
    echo.
    echo Release package created: !RELEASE_DIR!
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