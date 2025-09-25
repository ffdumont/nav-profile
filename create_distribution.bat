@echo off
REM NavPro Distribution Package Creator
REM This script creates a complete distribution package for Windows

echo ========================================
echo NavPro Distribution Package Creator
echo ========================================
echo.

REM Create distribution directory
if exist "NavPro_Distribution" rmdir /s /q "NavPro_Distribution"
mkdir "NavPro_Distribution"

REM Copy executable
if exist "dist\navpro_gui.exe" (
    echo Copying executable...
    copy "dist\navpro_gui.exe" "NavPro_Distribution\NavPro.exe"
    echo ✓ NavPro.exe copied
) else (
    echo ❌ ERROR: navpro_gui.exe not found in dist folder!
    echo Please run build_gui.bat first.
    pause
    exit /b 1
)

REM Copy data files
if exist "data\airspaces.db" (
    echo Copying airspace database...
    mkdir "NavPro_Distribution\data"
    copy "data\airspaces.db" "NavPro_Distribution\data\"
    echo ✓ airspaces.db copied
) else (
    echo ⚠️  WARNING: airspaces.db not found - users will need to provide their own
)

REM Copy documentation
if exist "README_DIST.md" (
    echo Copying documentation...
    copy "README_DIST.md" "NavPro_Distribution\README.md"
    echo ✓ README.md copied
)

REM Create sample data folder with instructions
mkdir "NavPro_Distribution\sample_data"
echo Place your KML flight profiles in this folder > "NavPro_Distribution\sample_data\Place_KML_files_here.txt"

REM Create launch script
echo @echo off > "NavPro_Distribution\Launch_NavPro.bat"
echo cd /d "%%~dp0" >> "NavPro_Distribution\Launch_NavPro.bat"
echo NavPro.exe >> "NavPro_Distribution\Launch_NavPro.bat"
echo pause >> "NavPro_Distribution\Launch_NavPro.bat"

echo.
echo ========================================
echo DISTRIBUTION PACKAGE CREATED!
echo ========================================
echo.
echo Package contents:
dir /b "NavPro_Distribution"
echo.
echo Location: %cd%\NavPro_Distribution
echo.
echo To distribute:
echo 1. Zip the entire NavPro_Distribution folder
echo 2. Share with users
echo 3. Users run NavPro.exe or Launch_NavPro.bat
echo.
echo Prerequisites for users:
echo - Windows 10/11 (64-bit)
echo - Google Earth Pro (recommended)
echo - AIXM XML file (if not included)
echo - KML flight profiles
echo.
pause