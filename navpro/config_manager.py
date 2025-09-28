"""
Configuration Manager for AirCheck Application

Handles configuration loading and path management for both development
and production environments (PyInstaller bundles).
"""

import os
import sys
import configparser
from pathlib import Path
from typing import Optional, Dict, Any


class ConfigManager:
    """
    Configuration manager that provides unified access to application settings
    and handles path resolution for both development and production environments.
    """
    
    def __init__(self):
        self._config = configparser.ConfigParser()
        self._app_root = self._get_application_root()
        self._is_bundled = self._detect_bundle()
        self._data_root = self._get_data_root()
        self._load_config()
        
    def _get_application_root(self) -> Path:
        """Get the application root directory."""
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            return Path(sys.executable).parent
        else:
            # Running in development
            return Path(__file__).parent.parent
    
    def _detect_bundle(self) -> bool:
        """Detect if running in PyInstaller bundle."""
        return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    
    def _get_data_root(self) -> Path:
        """Get the data root directory."""
        if self._is_bundled:
            # In production, data folder is alongside the executable
            return self._app_root / "data"
        else:
            # In development, data folder is in project root
            return self._app_root / "data"
    
    def _load_config(self):
        """Load configuration from config.ini file."""
        config_path = self._app_root / "config.ini"
        
        if config_path.exists():
            self._config.read(config_path)
        else:
            # Use default configuration if file doesn't exist
            self._set_default_config()
    
    def _set_default_config(self):
        """Set default configuration values."""
        self._config.add_section('PATHS')
        self._config.set('PATHS', 'database_folder', 'data')
        self._config.set('PATHS', 'database_filename', 'airspaces.db')
        self._config.set('PATHS', 'input_data_folder', 'data/input')
        self._config.set('PATHS', 'output_data_folder', 'data/output')
        self._config.set('PATHS', 'sample_data_folder', 'data/samples')
        
        self._config.add_section('APPLICATION')
        self._config.set('APPLICATION', 'app_name', 'AirCheck')
        self._config.set('APPLICATION', 'version', '1.2.4')
        self._config.set('APPLICATION', 'splash_timeout', '3000')
        self._config.set('APPLICATION', 'enable_splash', 'true')
        
    @property
    def app_root(self) -> Path:
        """Get application root directory."""
        return self._app_root
    
    @property
    def data_root(self) -> Path:
        """Get data root directory."""
        return self._data_root
    
    @property
    def is_bundled(self) -> bool:
        """Check if running in PyInstaller bundle."""
        return self._is_bundled
    
    def get_path(self, section: str, key: str) -> Path:
        """
        Get a path from configuration, resolved relative to appropriate root.
        
        Args:
            section: Configuration section name
            key: Configuration key name
            
        Returns:
            Resolved Path object
        """
        try:
            relative_path = self._config.get(section, key)
            if section == 'PATHS':
                # Paths are relative to app root
                return self._app_root / relative_path
            else:
                return Path(relative_path)
        except (configparser.NoSectionError, configparser.NoOptionError):
            raise KeyError(f"Configuration key '{section}.{key}' not found")
    
    def get_database_path(self) -> Path:
        """Get the full path to the database file."""
        db_folder = self.get_path('PATHS', 'database_folder')
        db_filename = self._config.get('PATHS', 'database_filename')
        return db_folder / db_filename
    
    def get_input_data_path(self) -> Path:
        """Get the input data folder path."""
        return self.get_path('PATHS', 'input_data_folder')
    
    def get_output_data_path(self) -> Path:
        """Get the output data folder path."""
        return self.get_path('PATHS', 'output_data_folder')
    
    def get_sample_data_path(self) -> Path:
        """Get the sample data folder path."""
        return self.get_path('PATHS', 'sample_data_folder')
    
    def get_aixm_file_path(self) -> Path:
        """Get the full path to the AIXM file."""
        input_folder = self.get_input_data_path()
        aixm_filename = self._config.get('PATHS', 'aixm_filename', fallback='AIXM4.5_all_FR_OM_2025-10-02.xml')
        return input_folder / aixm_filename
    
    def get_value(self, section: str, key: str, fallback: Any = None) -> str:
        """
        Get a configuration value.
        
        Args:
            section: Configuration section name
            key: Configuration key name
            fallback: Default value if key not found
            
        Returns:
            Configuration value as string
        """
        return self._config.get(section, key, fallback=fallback)
    
    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """Get a configuration value as integer."""
        return self._config.getint(section, key, fallback=fallback)
    
    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get a configuration value as boolean."""
        return self._config.getboolean(section, key, fallback=fallback)
    
    def get_float(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get a configuration value as float."""
        return self._config.getfloat(section, key, fallback=fallback)
    
    def ensure_directories(self):
        """Ensure all configured directories exist."""
        directories = [
            self.get_path('PATHS', 'database_folder'),
            self.get_input_data_path(),
            self.get_output_data_path(),
            self.get_sample_data_path(),
        ]
        
        # Add logs directory if configured
        try:
            log_folder = self.get_path('LOGGING', 'log_folder')
            directories.append(log_folder)
        except KeyError:
            pass
        
        # Add temp directory if configured
        try:
            temp_folder = self.get_path('PATHS', 'temp_folder')
            directories.append(temp_folder)
        except KeyError:
            pass
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about current configuration."""
        return {
            'app_root': str(self.app_root),
            'data_root': str(self.data_root),
            'is_bundled': self.is_bundled,
            'database_path': str(self.get_database_path()),
            'input_data_path': str(self.get_input_data_path()),
            'output_data_path': str(self.get_output_data_path()),
            'sample_data_path': str(self.get_sample_data_path()),
            'config_sections': list(self._config.sections()),
        }


# Global configuration instance
config = ConfigManager()