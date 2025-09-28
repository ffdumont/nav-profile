#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AirCheck Application Entry Point

Main entry point for AirCheck application with splash screen
and proper configuration initialization.
"""

import sys
import tkinter as tk
import time
from pathlib import Path

# Add navpro to path
sys.path.insert(0, str(Path(__file__).parent / "navpro"))

from navpro.config_manager import config
from navpro.splash_screen import show_splash_with_config
from navpro.navpro_gui import AirspaceCheckerGUI


def initialize_application():
    """Initialize application components."""
    print("Initializing configuration...")
    
    # Ensure directories exist
    config.ensure_directories()
    
    # Set default AIXM file path if available
    aixm_path = config.get_aixm_file_path()
    if aixm_path.exists():
        print(f"Found AIXM file: {aixm_path}")
    else:
        print(f"AIXM file not found at: {aixm_path}")
    
    # Check database
    db_path = config.get_database_path()
    if db_path.exists():
        print(f"Database found: {db_path}")
    else:
        print(f"Database will be created at: {db_path}")
    
    print("Application initialized successfully")


def create_startup_tasks():
    """Create list of startup tasks for splash screen."""
    return [
        {
            'name': 'Configuration',
            'func': lambda: config.ensure_directories()
        },
        {
            'name': 'Application Setup',
            'func': initialize_application
        },
        {
            'name': 'GUI Components',
            'func': lambda: print("Loading GUI components...")
        }
    ]


def main():
    """Main application entry point."""
    try:
        # Initialize configuration first
        initialize_application()
        
        # Create root window first
        root = tk.Tk()
        root.withdraw()  # Hide main window initially
        
        # Show splash screen with startup tasks (simplified)
        splash_window = None
        if config.get_bool('APPLICATION', 'enable_splash', True):
            try:
                # Create splash as a separate root window (needed for PyInstaller)
                splash_window = tk.Tk()
                splash_window.title("AirCheck")
                splash_window.resizable(False, False)
                splash_window.overrideredirect(True)  # Remove window decorations
                splash_window.attributes('-topmost', True)  # Keep on top
                
                # Center splash screen
                width, height = 400, 180  # Increased height for log line
                screen_width = splash_window.winfo_screenwidth()
                screen_height = splash_window.winfo_screenheight()
                x = (screen_width - width) // 2
                y = (screen_height - height) // 2
                splash_window.geometry(f"{width}x{height}+{x}+{y}")
                
                # Splash content
                frame = tk.Frame(splash_window, bg='white', bd=2, relief='raised')
                frame.pack(fill='both', expand=True, padx=2, pady=2)
                
                # Title
                title_label = tk.Label(frame, text="AirCheck", font=('Arial', 16, 'bold'), bg='white', fg='#2C3E50')
                title_label.pack(pady=20)
                
                # Version
                version = config.get_value('APPLICATION', 'version', '1.2.4')
                version_label = tk.Label(frame, text=f"Version {version}", font=('Arial', 10), bg='white', fg='#7F8C8D')
                version_label.pack()
                
                # Status
                status_var = tk.StringVar(value="Initializing application...")
                status_label = tk.Label(frame, textvariable=status_var, font=('Arial', 9), bg='white', fg='#34495E')
                status_label.pack(pady=10)
                
                # Log line - clean professional styling
                log_label = tk.Label(frame, text="• Starting AirCheck application...", font=('Arial', 8), bg='white', fg='#2980B9', justify='left', anchor='w')
                log_label.pack(pady=(5, 10), padx=10, fill='x')
                
                # Keep the StringVar for compatibility (not used now)
                log_var = tk.StringVar(value="• Starting AirCheck application...")
                
                # Progress bar
                from tkinter import ttk
                progress_var = tk.DoubleVar(value=10)
                progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100, length=300)
                progress_bar.pack(pady=10)
                
                splash_window.update()
                splash_window.lift()  # Bring to front
                
                # Initial update with log
                update_splash = None  # Will be defined next
                
                def update_splash(progress, status, log_message=None):
                    if splash_window and splash_window.winfo_exists():
                        try:
                            progress_var.set(progress)
                            status_var.set(status)
                            if log_message:
                                log_label.config(text=log_message)
                            splash_window.update()
                        except Exception as e:
                            pass
                
                # Show initial log message
                update_splash(10, "Initializing application...", "• Starting AirCheck application...")
                
            except Exception as e:
                splash_window = None
                update_splash = lambda p, s, l=None: None
        else:
            update_splash = lambda p, s, l=None: None
        
        # Initialize the main application with progress updates
        if splash_window:
            update_splash(30, "Loading configuration...", "• Reading config.ini and database settings")
        
        if splash_window:
            update_splash(70, "Starting AirCheck GUI...", "• Initializing interface and loading AIXM data")
        
        app = AirspaceCheckerGUI(root)
        
        if splash_window:
            update_splash(100, "Ready!", "• Application startup complete - launching GUI")
            time.sleep(0.8)  # Brief pause to show "Ready!"
            try:
                splash_window.quit()
                splash_window.destroy()
            except:
                pass
        
        # Show main window
        root.deiconify()
        
        # Start the application
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()