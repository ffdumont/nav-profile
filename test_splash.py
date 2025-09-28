#!/usr/bin/env python3
"""
Test splash screen functionality
"""

import sys
import tkinter as tk
import time
from pathlib import Path

# Add navpro to path
sys.path.insert(0, str(Path(__file__).parent / "navpro"))

from navpro.config_manager import config

def test_splash():
    """Test splash screen creation."""
    print("Testing splash screen...")
    
    # Create single root window
    root = tk.Tk()
    root.withdraw()  # Hide main window initially
    
    try:
        # Use Toplevel window for splash
        splash_window = tk.Toplevel(root)
        splash_window.title("AirCheck Test")
        splash_window.resizable(False, False)
        splash_window.overrideredirect(True)
        splash_window.attributes('-topmost', True)
        
        # Center splash screen
        width, height = 400, 180
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
        print(f"Config version: {version}")
        version_label = tk.Label(frame, text=f"Version {version}", font=('Arial', 10), bg='white', fg='#7F8C8D')
        version_label.pack()
        
        # Status
        status_var = tk.StringVar(value="Testing splash screen...")
        status_label = tk.Label(frame, textvariable=status_var, font=('Arial', 9), bg='white', fg='#34495E')
        status_label.pack(pady=10)
        
        # Force splash to appear
        splash_window.update_idletasks()
        splash_window.update()
        splash_window.lift()
        splash_window.focus_force()
        
        print("Splash window created, showing for 3 seconds...")
        time.sleep(3)
        
        splash_window.destroy()
        print("Splash test complete")
        
    except Exception as e:
        print(f"Splash screen error: {e}")
        import traceback
        traceback.print_exc()
    
    root.destroy()

if __name__ == "__main__":
    test_splash()