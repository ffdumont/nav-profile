#!/usr/bin/env python3
"""
Test version detection in GUI
"""

import sys
from pathlib import Path

# Add navpro to path
sys.path.insert(0, str(Path(__file__).parent / "navpro"))

print("Testing version detection...")

# Test 1: Direct import from __init__.py
try:
    from navpro import __version__
    print(f"navpro.__version__: {__version__}")
except ImportError as e:
    print(f"Failed to import navpro.__version__: {e}")

# Test 2: Version function
try:
    from navpro.version import get_version
    version = get_version()
    print(f"get_version(): {version}")
except ImportError as e:
    print(f"Failed to import version function: {e}")

# Test 3: Config manager
try:
    from navpro.config_manager import config
    config_version = config.get_value('APPLICATION', 'version', 'FALLBACK')
    print(f"config version: {config_version}")
except ImportError as e:
    print(f"Failed to import config: {e}")

# Test 4: How GUI module determines version
try:
    from navpro.config_manager import config
    
    # Import version information (same as GUI)
    try:
        from navpro.version import get_version
        VERSION = get_version()
        print(f"GUI VERSION (method 1): {VERSION}")
    except ImportError:
        try:
            from navpro import __version__
            VERSION = __version__
            print(f"GUI VERSION (method 2): {VERSION}")
        except ImportError:
            VERSION = config.get_value('APPLICATION', 'version', '1.2.4')
            print(f"GUI VERSION (fallback): {VERSION}")
            
    print(f"Final GUI VERSION: {VERSION}")
    
except Exception as e:
    print(f"Error in version detection: {e}")
    import traceback
    traceback.print_exc()