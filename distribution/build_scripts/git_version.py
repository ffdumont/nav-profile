#!/usr/bin/env python3
"""
Git-based version management for AirCheck builds

This script can automatically determine version from Git tags or use manual version
"""

import subprocess
import sys
from pathlib import Path

def get_git_version():
    """Get version from Git tags"""
    try:
        # Try to get the latest tag
        result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                              capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        if result.returncode == 0:
            tag = result.stdout.strip()
            # Remove 'v' prefix if present
            if tag.startswith('v'):
                tag = tag[1:]
            return tag
        else:
            print("No Git tags found")
            return None
            
    except FileNotFoundError:
        print("Git not found")
        return None

def get_git_commit():
    """Get current Git commit hash"""
    try:
        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                              capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
            
    except FileNotFoundError:
        return None

def create_git_based_version():
    """Create a version string based on Git info"""
    
    git_version = get_git_version()
    git_commit = get_git_commit()
    
    if git_version:
        # Check if we're on the exact tag
        try:
            result = subprocess.run(['git', 'describe', '--exact-match', '--tags'], 
                                  capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            if result.returncode == 0:
                # We're on an exact tag
                return git_version
            else:
                # We're past a tag, add commit info
                if git_commit:
                    return f"{git_version}-dev+{git_commit}"
                else:
                    return f"{git_version}-dev"
                    
        except FileNotFoundError:
            pass
    
    # Fallback
    if git_commit:
        return f"dev-{git_commit}"
    else:
        return "dev"

if __name__ == "__main__":
    version = create_git_based_version()
    print(f"Git-based version: {version}")