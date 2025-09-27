#!/usr/bin/env python3
"""
Release Management Utility for AirCheck/NavPro

This script helps manage releases, clean up old versions, and maintain 
a consistent release structure.
"""

import argparse
import shutil
from pathlib import Path
from datetime import datetime
import zipfile

def list_releases():
    """List all available releases"""
    releases_dir = Path('../releases')
    if not releases_dir.exists():
        print("No releases directory found")
        return
    
    print("Available Releases:")
    print("==================")
    
    # List zip files (final releases)
    zip_files = list(releases_dir.glob('*.zip'))
    zip_files.sort()
    
    print("\nZip Releases:")
    for zip_file in zip_files:
        stat = zip_file.stat()
        size_mb = stat.st_size / (1024 * 1024)
        modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        print(f"  {zip_file.name:<25} {size_mb:>8.1f} MB  {modified}")
    
    # List directories (working releases)
    dirs = [d for d in releases_dir.iterdir() if d.is_dir() and d.name != 'current']
    dirs.sort()
    
    print("\nDirectory Releases:")
    for dir_path in dirs:
        print(f"  {dir_path.name}")
    
    # Current release
    current = releases_dir / 'current'
    if current.exists():
        print(f"\nCurrent Release: {current.name}")

def clean_old_releases(keep=5):
    """Clean old releases, keeping only the most recent ones"""
    releases_dir = Path('../releases')
    if not releases_dir.exists():
        return
    
    print(f"Cleaning old releases (keeping {keep} most recent)...")
    
    # Clean old zip files
    zip_files = list(releases_dir.glob('AirCheck_v*.zip'))
    zip_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    for zip_file in zip_files[keep:]:
        print(f"Removing old zip: {zip_file.name}")
        zip_file.unlink()
    
    # Clean old directories (except current)
    dirs = [d for d in releases_dir.glob('AirCheck_v*') if d.is_dir()]
    dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    for dir_path in dirs[keep:]:
        print(f"Removing old directory: {dir_path.name}")
        shutil.rmtree(dir_path)

def archive_navpro_releases():
    """Move old NavPro releases to an archive folder"""
    releases_dir = Path('../releases')
    archive_dir = releases_dir / 'archive'
    
    navpro_files = list(releases_dir.glob('NavPro_v*.zip'))
    
    if not navpro_files:
        print("No NavPro releases found to archive")
        return
    
    archive_dir.mkdir(exist_ok=True)
    
    for navpro_file in navpro_files:
        dest = archive_dir / navpro_file.name
        print(f"Archiving: {navpro_file.name} -> archive/{navpro_file.name}")
        shutil.move(str(navpro_file), str(dest))
    
    print(f"Archived {len(navpro_files)} NavPro releases")

def create_release_info():
    """Create a release information file"""
    releases_dir = Path('../releases')
    
    # Get all AirCheck releases
    zip_files = list(releases_dir.glob('AirCheck_v*.zip'))
    zip_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    info_content = f"""# AirCheck Releases

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Release History

"""
    
    for zip_file in zip_files:
        stat = zip_file.stat()
        size_mb = stat.st_size / (1024 * 1024)
        modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        
        info_content += f"### {zip_file.stem}\n"
        info_content += f"- **File**: {zip_file.name}\n"
        info_content += f"- **Size**: {size_mb:.1f} MB\n"
        info_content += f"- **Date**: {modified}\n"
        
        # Try to get README content if available
        dir_path = releases_dir / zip_file.stem
        readme_path = dir_path / 'README.md'
        if readme_path.exists():
            info_content += f"- **Notes**: See {zip_file.stem}/README.md\n"
        
        info_content += "\n"
    
    with open(releases_dir / 'RELEASES.md', 'w') as f:
        f.write(info_content)
    
    print("Created releases information file: ../releases/RELEASES.md")

def main():
    parser = argparse.ArgumentParser(description='Release Management Utility')
    parser.add_argument('action', choices=['list', 'clean', 'archive', 'info'], 
                       help='Action to perform')
    parser.add_argument('--keep', type=int, default=5, 
                       help='Number of releases to keep when cleaning (default: 5)')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        list_releases()
    elif args.action == 'clean':
        clean_old_releases(args.keep)
    elif args.action == 'archive':
        archive_navpro_releases()
    elif args.action == 'info':
        create_release_info()

if __name__ == "__main__":
    main()