@echo off
REM Airspace Checker Python Script Wrapper
REM Auto-detects and activates virtual environment if available

set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."
set "VENV_DIR=%PROJECT_DIR%\.venv"
set "PYTHON_SCRIPT=%PROJECT_DIR%\navpro\navpro.py"

REM Check if virtual environment exists and activate it
if exist "%VENV_DIR%\Scripts\activate.bat" (
    call "%VENV_DIR%\Scripts\activate.bat"
    python "%PYTHON_SCRIPT%" %*
) else (
    REM Fallback to system Python
    python "%PYTHON_SCRIPT%" %*
)