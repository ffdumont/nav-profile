#!/usr/bin/env python3
"""
Build script to create both GUI and CLI versions of AirCheck
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print("Output:")
            print(result.stdout)
    else:
        print(f"❌ {description} failed!")
        if result.stderr:
            print("Error:")
            print(result.stderr)
        if result.stdout:
            print("Output:")
            print(result.stdout)
        return False
    return True

def build_both_versions():
    """Build both GUI and CLI versions"""
    # Get script directory and project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Change to project root
    os.chdir(project_root)
    
    print("🚀 Building AirCheck GUI and CLI Versions")
    print(f"📁 Project root: {project_root}")
    print(f"📁 Build scripts: {script_dir}")
    
    # Clean build directories
    build_dir = script_dir / "build"
    dist_dir = script_dir / "dist"
    
    if build_dir.exists():
        print(f"🗑️ Cleaning build directory: {build_dir}")
        shutil.rmtree(build_dir)
    
    if dist_dir.exists():
        print(f"🗑️ Cleaning dist directory: {dist_dir}")
        shutil.rmtree(dist_dir)
    
    # Build GUI version
    gui_spec = script_dir / "aircheck_gui.spec"
    if not run_command([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--workpath", str(build_dir / "gui_work"),
        "--distpath", str(dist_dir / "gui"),
        str(gui_spec)
    ], "Building GUI version (AirCheck.exe)"):
        return False
    
    # Build CLI version
    cli_spec = script_dir / "aircheck_cli.spec"
    if not run_command([
        sys.executable, "-m", "PyInstaller", 
        "--clean",
        "--workpath", str(build_dir / "cli_work"),
        "--distpath", str(dist_dir / "cli"),
        str(cli_spec)
    ], "Building CLI version (AirCheckCLI.exe)"):
        return False
    
    # Create combined distribution directory
    combined_dist = script_dir / "AirCheck_Distribution"
    if combined_dist.exists():
        shutil.rmtree(combined_dist)
    
    combined_dist.mkdir(parents=True)
    
    print(f"\n📦 Creating combined distribution in: {combined_dist}")
    
    # Copy GUI executable
    gui_exe = dist_dir / "gui" / "AirCheck.exe"
    if gui_exe.exists():
        shutil.copy2(gui_exe, combined_dist / "AirCheck.exe")
        print("✅ Copied GUI executable: AirCheck.exe")
    else:
        print("❌ GUI executable not found!")
        return False
    
    # Copy CLI executable
    cli_exe = dist_dir / "cli" / "AirCheckCLI.exe"
    if cli_exe.exists():
        shutil.copy2(cli_exe, combined_dist / "AirCheckCLI.exe")
        print("✅ Copied CLI executable: AirCheckCLI.exe")
    else:
        print("❌ CLI executable not found!")
        return False
    
    # Copy data directory from GUI build (it should have all data files)
    gui_data = dist_dir / "gui" / "data"
    if gui_data.exists():
        shutil.copytree(gui_data, combined_dist / "data")
        print("✅ Copied data directory")
    
    # Create launcher scripts
    create_launcher_scripts(combined_dist)
    
    # Create README
    create_distribution_readme(combined_dist)
    
    print(f"\n🎉 Build completed successfully!")
    print(f"📁 Distribution directory: {combined_dist}")
    print(f"📄 Files created:")
    for file in combined_dist.rglob("*"):
        if file.is_file():
            print(f"   • {file.relative_to(combined_dist)}")
    
    return True

def create_launcher_scripts(dist_dir):
    """Create launcher scripts for both GUI and CLI"""
    
    # GUI launcher
    gui_launcher = dist_dir / "Launch_AirCheck_GUI.bat"
    gui_launcher.write_text("""@echo off
title AirCheck - Flight Profile Analysis Tool
echo Starting AirCheck GUI...
echo.
cd /d "%~dp0"
AirCheck.exe
pause
""")
    print("✅ Created GUI launcher: Launch_AirCheck_GUI.bat")
    
    # CLI launcher (opens command prompt)
    cli_launcher = dist_dir / "Launch_AirCheck_CLI.bat"
    cli_launcher.write_text("""@echo off
title AirCheck CLI - Command Line Interface
cd /d "%~dp0"
echo ========================================
echo AirCheck Command Line Interface
echo ========================================
echo.
echo Type "AirCheckCLI --help" to see available commands
echo Type "AirCheckCLI help" for detailed examples
echo.
cmd /k
""")
    print("✅ Created CLI launcher: Launch_AirCheck_CLI.bat")
    
    # Combined launcher (shows menu)
    combined_launcher = dist_dir / "Launch_AirCheck.bat"
    combined_launcher.write_text("""@echo off
title AirCheck - Choose Version
cd /d "%~dp0"

:menu
cls
echo ========================================
echo       AirCheck Flight Analysis Tool
echo ========================================
echo.
echo Choose your preferred interface:
echo.
echo 1. GUI Version (Graphical Interface)
echo 2. CLI Version (Command Line)
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo Starting GUI version...
    AirCheck.exe
    goto end
)
if "%choice%"=="2" (
    echo Starting CLI version...
    echo.
    echo Type "AirCheckCLI --help" for available commands
    echo.
    cmd /k AirCheckCLI
    goto end
)
if "%choice%"=="3" (
    goto end
)
echo Invalid choice. Please try again.
pause
goto menu

:end
""")
    print("✅ Created combined launcher: Launch_AirCheck.bat")

def create_distribution_readme(dist_dir):
    """Create README for the distribution"""
    readme_content = """# AirCheck - Flight Profile Analysis Tool

## Overview
AirCheck provides professional flight planning services including altitude profile correction, airspace analysis, and 3D visualization.

## Available Versions

### 1. GUI Version (AirCheck.exe)
**Best for:** Interactive use, visual analysis, beginners
- Graphical user interface
- Point-and-click operation  
- Visual progress indicators
- Integrated Google Earth launching

**To run:** Double-click `AirCheck.exe` or use `Launch_AirCheck_GUI.bat`

### 2. CLI Version (AirCheckCLI.exe)
**Best for:** Automation, scripting, batch processing, advanced users
- Command-line interface
- Scriptable operations
- Batch processing capabilities
- Integration with other tools

**To run:** Use `Launch_AirCheck_CLI.bat` or run `AirCheckCLI --help` from command prompt

## Quick Start

### For GUI Users:
1. Double-click `Launch_AirCheck_GUI.bat`
2. Select your AIXM XML file
3. Select your KML flight profile
4. Click "List Airspaces" or "View Airspaces in Google Earth"

### For CLI Users:
1. Open `Launch_AirCheck_CLI.bat` 
2. Type `AirCheckCLI --help` to see all commands
3. Example: `AirCheckCLI list --profile flight.kml`

## Common Commands (CLI)

```bash
# List airspaces crossed by a flight
AirCheckCLI list --profile flight.kml

# Generate KML visualization
AirCheckCLI generate --profile flight.kml

# Correct flight profile and analyze
AirCheckCLI list --fix-profile flight.kml

# Show database statistics
AirCheckCLI stats

# Get detailed help
AirCheckCLI help
```

## Data Directory
The data/ directory contains:
- airspaces.db: Airspace database
- input/: AIXM XML files
- samples/: Sample KML flight profiles
- output/: Generated analysis results

## Requirements
- Windows 7 or later
- No additional software required (self-contained executables)
- For Google Earth visualization: Google Earth Pro (optional)

## Aviation Safety Notice
WARNING: FOR EDUCATIONAL AND FLIGHT PLANNING PURPOSES ONLY
Always verify with official aeronautical publications before flight!

## Support
- GUI: Use the built-in help and status messages
- CLI: Run `AirCheckCLI help` for detailed examples and documentation
"""
    
    readme_file = dist_dir / "README.txt"
    readme_file.write_text(readme_content, encoding='utf-8')
    print("✅ Created README.txt")

if __name__ == "__main__":
    if build_both_versions():
        print("\n🎯 Both GUI and CLI versions built successfully!")
        sys.exit(0)
    else:
        print("\n❌ Build failed!")
        sys.exit(1)