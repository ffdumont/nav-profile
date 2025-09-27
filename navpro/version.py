"""
Version management for Airspace Checker
"""

import os
import sys
from pathlib import Path

def get_version():
    """
    Get the version string for Airspace Checker.
    
    Prioritizes semantic versioning for user display:
    1. From package __version__ attribute (preferred for GUI)
    2. Fallback to default version
    """
    try:
        # Try to import from package - this is preferred for user display
        from . import __version__
        return __version__
    except (ImportError, AttributeError):
        pass
    
    # Fallback version
    return "1.2.1.1"

def get_dev_version():
    """
    Get development version with git info for CLI/development use.
    
    Returns git hash for development builds, semantic version for releases.
    """
    # First try to get the semantic version
    semantic_version = get_version()
    
    try:
        # Try to get version from git if we're in a git repository
        import subprocess
        git_dir = Path(__file__).parent.parent / ".git"
        if git_dir.exists():
            try:
                result = subprocess.run(
                    ["git", "describe", "--tags", "--always"],
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent.parent
                )
                if result.returncode == 0:
                    git_version = result.stdout.strip()
                    if git_version and git_version != semantic_version:
                        # If we have a different git version, return it for development
                        return git_version
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
    except ImportError:
        pass
    
    # Return semantic version as fallback
    return semantic_version

def get_version_info():
    """
    Get detailed version information including build info.
    """
    version = get_version()
    
    info = {
        "version": version,
        "name": "Airspace Checker",
        "description": "Flight Profile & Airspace Analysis Tool",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }
    
    # Add git commit info if available
    try:
        import subprocess
        git_dir = Path(__file__).parent.parent / ".git"
        if git_dir.exists():
            try:
                # Get commit hash
                result = subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent.parent
                )
                if result.returncode == 0:
                    info["commit"] = result.stdout.strip()
                
                # Get branch name
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent.parent
                )
                if result.returncode == 0:
                    info["branch"] = result.stdout.strip()
                    
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
    except ImportError:
        pass
    
    return info

# Make version easily importable
__version__ = get_version()