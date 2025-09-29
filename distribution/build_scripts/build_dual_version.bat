@echo off
title AirCheck - Build GUI and CLI Versions
echo ========================================
echo AirCheck Dual Version Builder
echo ========================================
echo.
echo This will build both GUI and CLI versions of AirCheck
echo.
pause

cd /d "%~dp0"

echo Building both versions...
python build_dual_version.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Build completed successfully!
    echo ========================================
    echo.
    echo Distribution created in: AirCheck_Distribution\
    echo.
    echo Files created:
    echo   - AirCheck.exe         (GUI version)
    echo   - AirCheckCLI.exe      (CLI version)
    echo   - Launch_AirCheck.bat  (Menu launcher)
    echo   - README.txt           (Documentation)
    echo.
) else (
    echo.
    echo ========================================
    echo Build failed!
    echo ========================================
    echo Please check the error messages above.
)

pause