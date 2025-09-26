@echo off
REM AirCheck Distribution Package Creator
REM This script creates a complete distribution package for Windows

echo ========================================
echo AirCheck Distribution Package Creator
echo ========================================
echo.

REM Create distribution directory
if exist "AirCheck_Distribution" rmdir /s /q "AirCheck_Distribution"
mkdir "AirCheck_Distribution"

REM Copy executable
if exist "dist\AirCheck.exe" (
    echo Copying executable...
    copy "dist\AirCheck.exe" "AirCheck_Distribution\AirCheck.exe"
    echo ✓ AirCheck.exe copied
) else (
    echo ❌ ERROR: AirCheck.exe not found in dist folder!
    echo Please run build_gui.bat first.
    pause
    exit /b 1
)

REM Copy data files
if exist "data\airspaces.db" (
    echo Copying airspace database...
    mkdir "AirCheck_Distribution\data"
    copy "data\airspaces.db" "AirCheck_Distribution\data\"
    echo ✓ airspaces.db copied
) else (
    echo ⚠️  WARNING: airspaces.db not found - users will need to provide their own
)

REM Copy documentation
if exist "README_DIST.md" (
    echo Copying documentation...
    copy "README_DIST.md" "AirCheck_Distribution\README.md"
    echo ✓ README.md copied
)

REM Create sample data folder with sample files
echo Copying sample files...
mkdir "AirCheck_Distribution\sample_data"

REM Copy corrected KML sample
if exist "LFXU-LFFU-CORRECTED.kml" (
    copy "LFXU-LFFU-CORRECTED.kml" "AirCheck_Distribution\sample_data\"
    echo ✓ Corrected KML sample copied
) else (
    echo ⚠ Warning: LFXU-LFFU-CORRECTED.kml not found
)

REM Copy AIXM sample database  
if exist "data\AIXM4.5_all_FR_OM_2025-10-02.xml" (
    copy "data\AIXM4.5_all_FR_OM_2025-10-02.xml" "AirCheck_Distribution\sample_data\"
    echo ✓ AIXM sample database copied
) else (
    echo ⚠ Warning: AIXM4.5_all_FR_OM_2025-10-02.xml not found in data folder
)

REM Copy additional KML samples if they exist
if exist "data\*.kml" (
    copy "data\*.kml" "AirCheck_Distribution\sample_data\"
    echo ✓ Additional KML samples copied
) else (
    echo Place your KML flight profiles in this folder > "AirCheck_Distribution\sample_data\Place_KML_files_here.txt"
)

REM Create launch script
echo @echo off > "AirCheck_Distribution\Launch_AirCheck.bat"
echo cd /d "%%~dp0" >> "AirCheck_Distribution\Launch_AirCheck.bat"
echo AirCheck.exe >> "AirCheck_Distribution\Launch_AirCheck.bat"
echo pause >> "AirCheck_Distribution\Launch_AirCheck.bat"

echo.
echo ========================================
echo DISTRIBUTION PACKAGE CREATED!
echo ========================================
echo.
echo Package contents:
dir /b "AirCheck_Distribution"
echo.
echo Location: %cd%\AirCheck_Distribution
echo.

REM Prompt for version number and create ZIP
set /p VERSION="Enter version number (e.g., 1.1.1): "
if not "%VERSION%"=="" (
    echo Creating ZIP archive...
    powershell "Compress-Archive -Path 'AirCheck_Distribution\*' -DestinationPath '..\releases\AirCheck_v%VERSION%.zip' -Force"
    if exist "..\releases\AirCheck_v%VERSION%.zip" (
        echo ✓ ZIP archive created: ..\releases\AirCheck_v%VERSION%.zip
    ) else (
        echo ❌ Failed to create ZIP archive
    )
    echo.
)

echo To distribute:
echo 1. Share the ZIP file: AirCheck_v%VERSION%.zip
echo 2. Or share the AirCheck_Distribution folder
echo 3. Users run AirCheck.exe or Launch_AirCheck.bat
echo.
echo Prerequisites for users:
echo - Windows 10/11 (64-bit)
echo - Google Earth Pro (recommended)
echo - AIXM XML file (if not included)
echo - KML flight profiles
echo.
pause