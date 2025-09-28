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
    
    echo.
    echo Copying files to release directory...
    
    REM Copy main executable
    echo Copying executable...
    if exist "dist\AirCheck.exe" (
        copy "dist\AirCheck.exe" "!RELEASE_DIR!\"
        if errorlevel 1 echo ERROR: Failed to copy AirCheck.exe
    ) else (
        echo ERROR: dist\AirCheck.exe not found!
    )
    
    REM Copy database to main directory
    echo Copying database...
    set DB_PATH=..\..\data\airspaces.db
    if exist "!DB_PATH!" (
        copy "!DB_PATH!" "!RELEASE_DIR!\"
        if errorlevel 1 echo ERROR: Failed to copy airspaces.db
    ) else (
        echo ERROR: Database not found at !DB_PATH!
    )
    
    REM Create data directory and copy AIXM file
    echo Creating data directory...
    mkdir "!RELEASE_DIR!\data"
    
    echo Copying AIXM file for database rebuilds...
    set AIXM_PATH=..\..\data\AIXM4.5_all_FR_OM_2025-10-02.xml
    if exist "!AIXM_PATH!" (
        copy "!AIXM_PATH!" "!RELEASE_DIR!\data\"
        if errorlevel 1 echo ERROR: Failed to copy AIXM file
    ) else (
        echo ERROR: AIXM file not found at !AIXM_PATH!
    )
    
    REM Copy profile correction scripts
    echo Copying profile correction scripts...
    set PROFILE_DIR=..\..\navpro\profile-correction
    
    if exist "!PROFILE_DIR!\kml_profile_viewer.py" (
        copy "!PROFILE_DIR!\kml_profile_viewer.py" "!RELEASE_DIR!\"
        if errorlevel 1 echo ERROR: Failed to copy kml_profile_viewer.py
    ) else (
        echo ERROR: kml_profile_viewer.py not found in !PROFILE_DIR!
    )
    
    if exist "!PROFILE_DIR!\kml_profile_corrector.py" (
        copy "!PROFILE_DIR!\kml_profile_corrector.py" "!RELEASE_DIR!\"
        if errorlevel 1 echo ERROR: Failed to copy kml_profile_corrector.py
    ) else (
        echo ERROR: kml_profile_corrector.py not found in !PROFILE_DIR!
    )
    
    if exist "!PROFILE_DIR!\aviation_utils.py" (
        copy "!PROFILE_DIR!\aviation_utils.py" "!RELEASE_DIR!\"
        if errorlevel 1 echo ERROR: Failed to copy aviation_utils.py
    ) else (
        echo ERROR: aviation_utils.py not found in !PROFILE_DIR!
    )
    
    REM Create sample_data directory and copy sample KML files
    echo Creating sample_data directory...
    mkdir "!RELEASE_DIR!\sample_data"
    
    echo Copying sample KML files...
    set DATA_DIR=..\..\data
    
    REM Copy all KML files from data directory
    for %%f in ("!DATA_DIR!\*.kml") do (
        echo Copying %%~nxf...
        copy "%%f" "!RELEASE_DIR!\sample_data\"
        if errorlevel 1 echo ERROR: Failed to copy %%~nxf
    )
    
    REM Create instructions file
    echo Place your KML flight profiles in this folder > "!RELEASE_DIR!\sample_data\Place_KML_files_here.txt"
    
    REM Create launcher script
    echo Creating launcher script...
    echo @echo off > "!RELEASE_DIR!\Launch_AirCheck.bat"
    echo cd /d "%%~dp0" >> "!RELEASE_DIR!\Launch_AirCheck.bat"
    echo AirCheck.exe >> "!RELEASE_DIR!\Launch_AirCheck.bat"
    echo pause >> "!RELEASE_DIR!\Launch_AirCheck.bat"
    
    REM Verify the release package
    echo.
    echo ================================
    echo VERIFYING RELEASE PACKAGE
    echo ================================
    echo.
    echo Main directory contents:
    dir "!RELEASE_DIR!" /b
    echo.
    echo Data directory contents:
    if exist "!RELEASE_DIR!\data" (
        dir "!RELEASE_DIR!\data" /b
    ) else (
        echo ERROR: Data directory not found!
    )
    echo.
    echo Sample data contents:
    if exist "!RELEASE_DIR!\sample_data" (
        dir "!RELEASE_DIR!\sample_data" /b
    ) else (
        echo ERROR: Sample data directory not found!
    )
    echo.
    
    REM Check for critical files
    echo Checking critical files:
    if exist "!RELEASE_DIR!\AirCheck.exe" (echo ✓ AirCheck.exe) else (echo ✗ AirCheck.exe MISSING)
    if exist "!RELEASE_DIR!\airspaces.db" (echo ✓ airspaces.db) else (echo ✗ airspaces.db MISSING)
    if exist "!RELEASE_DIR!\kml_profile_viewer.py" (echo ✓ kml_profile_viewer.py) else (echo ✗ kml_profile_viewer.py MISSING)
    if exist "!RELEASE_DIR!\kml_profile_corrector.py" (echo ✓ kml_profile_corrector.py) else (echo ✗ kml_profile_corrector.py MISSING)
    if exist "!RELEASE_DIR!\aviation_utils.py" (echo ✓ aviation_utils.py) else (echo ✗ aviation_utils.py MISSING)
    if exist "!RELEASE_DIR!\data\AIXM4.5_all_FR_OM_2025-10-02.xml" (echo ✓ AIXM file) else (echo ✗ AIXM file MISSING)
    echo.
    
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