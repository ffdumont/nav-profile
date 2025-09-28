# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for AirCheck Application with new modular architecture
"""

import os
from pathlib import Path

# Get the project root directory
project_root = Path(SPECPATH).resolve()
navpro_path = project_root / "navpro"
profile_correction_path = project_root / "navpro" / "profile-correction"

# Define paths to include
data_files = [
    # Configuration file
    (str(project_root / "config.ini"), "."),
    
    # Version and module files
    (str(navpro_path / "__init__.py"), "navpro"),
    (str(navpro_path / "version.py"), "navpro"),
    
    # Data files (if they exist)
    (str(project_root / "data" / "airspaces.db"), "data"),
    (str(project_root / "data" / "input" / "*.xml"), "data/input"),
    (str(project_root / "data" / "samples" / "*.kml"), "data/samples"),
]

# Hidden imports for modules that might not be detected
hidden_imports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
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
    'navpro.splash_screen',
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
]

# Analysis configuration
a = Analysis(
    [str(project_root / "aircheck.py")],  # Main entry point
    pathex=[
        str(project_root),
        str(navpro_path),
        str(profile_correction_path),
    ],
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ archive
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Executable configuration
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AirCheck',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI mode
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path if you have one
)

# Optional: Create distribution directory
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='AirCheck'
# )