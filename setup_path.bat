@echo off
REM Setup NavPro PATH - Run this once to add NavPro to your PATH

set "NAVPRO_DIR=%~dp0"

REM Add to user PATH for current session
set "PATH=%NAVPRO_DIR%;%PATH%"
echo NavPro directory added to PATH for current session: %NAVPRO_DIR%

REM Add to permanent user PATH 
echo Adding NavPro to permanent user PATH...
for /f "skip=2 tokens=3*" %%a in ('reg query HKCU\Environment /v PATH 2^>nul') do set "USER_PATH=%%b"

REM Check if already in PATH
echo %USER_PATH% | findstr /C:"%NAVPRO_DIR%" > nul
if %ERRORLEVEL% EQU 0 (
    echo NavPro directory already in user PATH
) else (
    REM Add to user PATH
    if defined USER_PATH (
        reg add HKCU\Environment /v PATH /t REG_EXPAND_SZ /d "%USER_PATH%;%NAVPRO_DIR%" /f
    ) else (
        reg add HKCU\Environment /v PATH /t REG_EXPAND_SZ /d "%NAVPRO_DIR%" /f
    )
    echo NavPro added to permanent user PATH
    echo Please restart your terminal or run: refreshenv
)

echo.
echo Setup complete! You can now use 'navpro' from any directory.
echo Example: navpro list --fix-profile "path\to\flight.kml"
pause