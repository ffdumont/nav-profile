# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for AirCheck CLI Application (Console Mode)
"""

import os
from pathlib import Path

# Get the project root directory
project_root = Path(SPECPATH).parent.parent.resolve()
navpro_path = project_root / "navpro"

# Define paths to include
data_files = [
    # Configuration file
    (str(project_root / "config.ini"), "."),
    
    # Version and module files
    (str(navpro_path / "__init__.py"), "navpro"),
    (str(navpro_path / "version.py"), "navpro"),
    
    # Data files will be handled by build script for better control
]

# Hidden imports for modules that might not be detected
hidden_imports = [
    'sqlite3',
    'xml.etree.ElementTree',
    'pathlib',
    'threading',
    'subprocess',
    'webbrowser',
    'navpro',
    'navpro.__init__',
    'navpro.version',
    'navpro.config_manager',
    'navpro.core.flight_analyzer',
    'navpro.core.query_engine',
    'navpro.core.spatial_query',
    'navpro.core.interpolation',
    'navpro.visualization.kml_generator',
    'navpro.visualization.kml_styling',
    'navpro.data_processing.aixm_extractor',
    'navpro.data_processing.aixm_query_service',
    'navpro.data_processing.database_utils',
    'navpro.utils.config',
    'navpro.utils.search',
    'navpro.utils.validation',
    'navpro.profile-correction.kml_profile_corrector',
    'navpro.profile-correction.aviation_utils',
    'navpro.profile-correction.kml_profile_viewer',
    # CLI-specific imports
    'colorama',
    'argparse',
]

# Analysis configuration
a = Analysis(
    [str(navpro_path / "navpro_cli.py")],  # CLI entry point
    pathex=[
        str(project_root),
        str(navpro_path),
        str(navpro_path / "profile-correction"),
    ],
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'matplotlib',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ archive
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Executable configuration for CLI (console mode)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AirCheckCLI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console mode for CLI
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path if you have one
)