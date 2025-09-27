#!/usr/bin/env python3
"""
Enhanced build script for AirCheck GUI with automatic version management

Usage:
    python build_aircheck.py [version]
    
Examples:
    python build_aircheck.py 1.2.1
    python build_aircheck.py  # Uses current version
"""

import sys
import os
import re
import shutil
import subprocess
import argparse
import zipfile
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.append('../../')
sys.path.append('../../navpro')

def update_version(version):
    """Update version in both __init__.py and version.py"""
    
    # Update navpro/__init__.py
    init_file = Path('../../navpro/__init__.py')
    print(f"Updating version in {init_file}...")
    
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace version
    content = re.sub(r'__version__\s*=\s*["\'][\d.]+["\']', f'__version__ = "{version}"', content)
    
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Update navpro/version.py
    version_file = Path('../../navpro/version.py')
    print(f"Updating fallback version in {version_file}...")
    
    with open(version_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace fallback version
    content = re.sub(r'return\s+"[\d.]+"', f'return "{version}"', content)
    
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Version updated to {version} successfully!")

def get_current_version():
    """Get current version from the package"""
    try:
        import navpro
        return navpro.__version__
    except ImportError:
        print("Warning: Could not import navpro package")
        return "1.2.1"

def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning previous builds...")
    
    for dir_name in ['dist', 'build']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}")

def check_dependencies():
    """Check if required files exist"""
    airspaces_db = Path('../../data/airspaces.db')
    if not airspaces_db.exists():
        print(f"WARNING: {airspaces_db} not found!")
        print("The application may not work without the airspace database.")

def build_executable():
    """Run PyInstaller to build the executable"""
    print("Running PyInstaller...")
    
    try:
        result = subprocess.run(['pyinstaller', 'aircheck_gui.spec'], 
                              capture_output=True, text=True, check=True)
        print("PyInstaller completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller failed with error: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print("ERROR: PyInstaller not found. Please install it with: pip install pyinstaller")
        return False

def create_release_package(version):
    """Create a complete release package"""
    
    if not Path('dist/AirCheck.exe').exists():
        print("ERROR: AirCheck.exe not found in dist/")
        return False
    
    # Use the main releases directory for consistency
    releases_dir = Path('../releases')
    releases_dir.mkdir(exist_ok=True)
    
    # Create versioned release directory
    release_dir = releases_dir / f'AirCheck_v{version}'
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # Copy executable
    shutil.copy2('dist/AirCheck.exe', release_dir)
    
    # Copy database if it exists
    airspaces_db = Path('../../data/airspaces.db')
    if airspaces_db.exists():
        shutil.copy2(airspaces_db, release_dir)
    
    # Create sample_data directory
    sample_data_dir = release_dir / 'sample_data'
    sample_data_dir.mkdir()
    
    with open(sample_data_dir / 'Place_KML_files_here.txt', 'w') as f:
        f.write('Place your KML flight profiles in this folder\n')
    
    # Create launcher batch file
    launcher_content = '''@echo off 
cd /d "%~dp0" 
AirCheck.exe 
pause 
'''
    
    with open(release_dir / 'Launch_AirCheck.bat', 'w') as f:
        f.write(launcher_content)
    
    # Create README for the release
    readme_content = f'''# AirCheck v{version}

Airspace Checker - Flight Profile & Airspace Analyzer

## Contents
- AirCheck.exe - Main application
- airspaces.db - Airspace database 
- Launch_AirCheck.bat - Convenient launcher
- sample_data/ - Place your KML files here

## Usage
1. Double-click Launch_AirCheck.bat or run AirCheck.exe directly
2. Load your KML flight profiles from the sample_data folder
3. Select AIXM airspace data file
4. Analyze airspace violations and generate reports

## Requirements
- Windows 10/11
- Google Earth Pro (recommended for visualization)

Built on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
    
    with open(release_dir / 'README.md', 'w') as f:
        f.write(readme_content)
    
    # Create zip file in the releases directory
    zip_path = releases_dir / f'AirCheck_v{version}.zip'
    if zip_path.exists():
        zip_path.unlink()
        
    import zipfile
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in release_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(release_dir)
                zipf.write(file_path, arcname)
    
    # Update the current release symlink/copy
    current_dir = releases_dir / 'current'
    if current_dir.exists():
        shutil.rmtree(current_dir)
    shutil.copytree(release_dir, current_dir)
    
    print(f"Release package created: {release_dir}")
    print(f"Release zip created: {zip_path}")
    print(f"Current release updated: {current_dir}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Build AirCheck GUI with version management')
    parser.add_argument('version', nargs='?', help='Version number (e.g., 1.2.1)')
    parser.add_argument('--no-package', action='store_true', help='Skip creating release package')
    
    args = parser.parse_args()
    
    # Determine version
    if args.version:
        version = args.version
        print(f"Building AirCheck GUI v{version}...")
        update_version(version)
    else:
        version = get_current_version()
        print(f"Building AirCheck GUI v{version} (current version)...")
    
    print()
    
    # Check dependencies
    check_dependencies()
    print()
    
    # Clean build
    clean_build()
    print()
    
    # Build executable
    if not build_executable():
        sys.exit(1)
    
    print()
    print("="*50)
    print("BUILD SUCCESSFUL!")
    print("="*50)
    print()
    print(f"Executable created: dist/AirCheck.exe")
    print(f"Version: {version}")
    print()
    
    # Create release package
    if not args.no_package:
        if create_release_package(version):
            print()
            print("To distribute:")
            print(f"1. Use the complete package in: ../releases/AirCheck_v{version}/")
            print(f"2. Or use the zip file: ../releases/AirCheck_v{version}.zip")
            print("3. Current release updated in: ../releases/current/")
            print("4. Ensure target system has Google Earth Pro installed")
        else:
            print("Warning: Failed to create release package")
    
    print()
    print("Build complete!")

if __name__ == "__main__":
    main()