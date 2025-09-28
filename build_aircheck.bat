@echo off
echo ===============================================
echo AirCheck Build Script - New Architecture v1.2.4
echo ===============================================

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found in PATH
    pause
    exit /b 1
)

REM Check if PyInstaller is available
python -m PyInstaller --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "AirCheck.exe" del "AirCheck.exe"

REM Build the application using the new spec file
echo.
echo Building AirCheck application...
python -m PyInstaller --clean --noconfirm aircheck.spec

REM Check if build was successful
if not exist "dist\AirCheck.exe" (
    echo.
    echo Error: Build failed - executable not found
    pause
    exit /b 1
)

REM Create distribution package
echo.
echo Creating distribution package...

REM Create distribution directory with version
set VERSION=1.2.4
set DIST_DIR=AirCheck_v%VERSION%
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
mkdir "%DIST_DIR%"

REM Copy executable
copy "dist\AirCheck.exe" "%DIST_DIR%\"
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to copy executable
    pause
    exit /b 1
)

REM Copy configuration file
copy "config.ini" "%DIST_DIR%\"
if %ERRORLEVEL% neq 0 (
    echo Warning: Configuration file not found
)

REM Create data directory structure
mkdir "%DIST_DIR%\data"
mkdir "%DIST_DIR%\data\input"
mkdir "%DIST_DIR%\data\output"  
mkdir "%DIST_DIR%\data\samples"
mkdir "%DIST_DIR%\data\logs"

REM Copy database if it exists
if exist "data\airspaces.db" (
    copy "data\airspaces.db" "%DIST_DIR%\data\"
    echo Database copied to distribution
) else (
    echo Note: No database found - will be created on first AIXM import
)

REM Copy AIXM file if it exists
if exist "data\input\*.xml" (
    copy "data\input\*.xml" "%DIST_DIR%\data\input\"
    echo AIXM file copied to distribution
) else (
    echo Note: No AIXM file found in data\input\
)

REM Copy sample data if it exists
if exist "data\samples\*.kml" (
    copy "data\samples\*.kml" "%DIST_DIR%\data\samples\"
    echo Sample KML files copied
) else (
    echo Note: No sample files found
)

REM Profile correction modules are now bundled inside the executable
REM No need to copy external .py files
echo Profile correction modules bundled inside executable

REM Create documentation files
echo Creating distribution documentation...

REM Create README for distribution
(
echo AirCheck v%VERSION% - Flight Profile and Airspace Analysis Tool
echo.
echo INSTALLATION:
echo 1. Extract this folder to your desired location
echo 2. Run AirCheck.exe to start the application
echo.
echo FIRST RUN:
echo - The application will create necessary folders automatically
echo - Import your AIXM file using the "Import AIXM" button
echo - Place your KML flight profiles in the data\samples folder
echo.
echo FOLDER STRUCTURE:
echo - data\input\     - Place AIXM XML files here
echo - data\samples\   - Place KML flight profiles here  
echo - data\output\    - Generated analysis files
echo - data\logs\      - Application log files
echo.
echo For support, visit: https://github.com/[your-repo]
) > "%DIST_DIR%\README.txt"

REM Create launch batch file for convenience
(
echo @echo off
echo echo Starting AirCheck v%VERSION%...
echo start "" "AirCheck.exe"
) > "%DIST_DIR%\Launch_AirCheck.bat"

echo.
echo ===============================================
echo Build completed successfully!
echo ===============================================
echo.
echo Distribution created: %DIST_DIR%
echo Executable: %DIST_DIR%\AirCheck.exe
echo.
echo Files included:
dir "%DIST_DIR%" /b
echo.
echo Data structure:
dir "%DIST_DIR%\data" /b /s 2>nul || echo   (Data folders created, will be populated on first run)
echo.

REM Optional: Create ZIP package
set /p CREATE_ZIP="Create ZIP package? (y/n): "
if /i "%CREATE_ZIP%"=="y" (
    echo Creating ZIP package...
    powershell -Command "Compress-Archive -Path '%DIST_DIR%\*' -DestinationPath '%DIST_DIR%.zip' -Force"
    if exist "%DIST_DIR%.zip" (
        echo ZIP package created: %DIST_DIR%.zip
    ) else (
        echo Warning: Failed to create ZIP package
    )
)

REM Move to releases directory
if not exist "distribution\releases" mkdir "distribution\releases"
echo Moving release to distribution\releases...
if exist "%DIST_DIR%" move "%DIST_DIR%" "distribution\releases\"
if exist "%DIST_DIR%.zip" move "%DIST_DIR%.zip" "distribution\releases\"
if exist "distribution\releases\%DIST_DIR%" (
    echo ✅ Release moved to: distribution\releases\%DIST_DIR%
) else (
    echo ❌ Failed to move release directory
)

echo.
echo Build process complete!
pause