#!/usr/bin/env pwsh
# Airspace Checker PowerShell Wrapper (Root level)
# Auto-detects and activates virtual environment if available

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = $ScriptDir
$VenvDir = Join-Path -Path $ProjectDir -ChildPath ".venv"
$PythonScript = Join-Path -Path $ProjectDir -ChildPath "navpro" | Join-Path -ChildPath "navpro.py"

# Check if virtual environment exists and use it
$VenvActivate = Join-Path -Path $VenvDir -ChildPath "Scripts" | Join-Path -ChildPath "Activate.ps1"
$VenvPython = Join-Path -Path $VenvDir -ChildPath "Scripts" | Join-Path -ChildPath "python.exe"

if (Test-Path $VenvActivate) {
    # Use venv Python
    $PythonExe = $VenvPython
} elseif (Test-Path $VenvPython) {
    # Fallback venv python without activation
    $PythonExe = $VenvPython
} else {
    # System Python fallback
    $PythonExe = "python"
}

# Execute the Python script with all arguments
& $PythonExe $PythonScript @Arguments