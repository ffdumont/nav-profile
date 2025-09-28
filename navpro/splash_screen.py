"""
Splash Screen for AirCheck Application

Displays loading progress and initialization status during startup.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from pathlib import Path
from typing import Callable, Optional


class SplashScreen:
    """
    Splash screen with progress bar and status updates.
    """
    
    def __init__(self, title: str = "AirCheck", version: str = None):
        self.title = title
        # Get version from navpro package if not provided
        if version is None:
            try:
                from . import __version__
                self.version = __version__
            except ImportError:
                try:
                    import navpro
                    self.version = navpro.__version__
                except ImportError:
                    self.version = "1.2.5"  # Fallback
        else:
            self.version = version
        self.root = None
        self.progress_var = None
        self.status_var = None
        self.progress_bar = None
        self._startup_tasks = []
        self._current_task = 0
        self._total_tasks = 0
        
    def create_splash(self):
        """Create and configure the splash screen window."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide initially
        
        # Window configuration
        self.root.title("")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)  # Remove window decorations
        
        # Calculate center position
        width, height = 400, 250
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main frame with border
        main_frame = tk.Frame(self.root, bg='white', relief='raised', bd=2)
        main_frame.pack(fill='both', expand=True)
        
        # Title section
        title_frame = tk.Frame(main_frame, bg='white', height=80)
        title_frame.pack(fill='x', pady=(20, 10))
        title_frame.pack_propagate(False)
        
        # Application name
        title_label = tk.Label(
            title_frame, 
            text=self.title,
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(pady=(10, 0))
        
        # Version
        version_label = tk.Label(
            title_frame,
            text=f"Version {self.version}",
            font=('Arial', 10),
            bg='white',
            fg='#7f8c8d'
        )
        version_label.pack()
        
        # Progress section
        progress_frame = tk.Frame(main_frame, bg='white', height=80)
        progress_frame.pack(fill='x', padx=40, pady=20)
        progress_frame.pack_propagate(False)
        
        # Status label
        self.status_var = tk.StringVar(value="Initializing...")
        status_label = tk.Label(
            progress_frame,
            textvariable=self.status_var,
            font=('Arial', 10),
            bg='white',
            fg='#34495e'
        )
        status_label.pack(anchor='w', pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            length=320
        )
        self.progress_bar.pack(fill='x')
        
        # Footer
        footer_frame = tk.Frame(main_frame, bg='white', height=40)
        footer_frame.pack(fill='x', side='bottom')
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(
            footer_frame,
            text="Flight Profile Analysis Tool",
            font=('Arial', 9),
            bg='white',
            fg='#95a5a6'
        )
        footer_label.pack(pady=10)
        
        # Show the window
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.update()
        
    def add_startup_task(self, name: str, task_func: Callable, *args, **kwargs):
        """
        Add a startup task to be executed during splash screen.
        
        Args:
            name: Display name for the task
            task_func: Function to execute
            *args, **kwargs: Arguments for the task function
        """
        self.startup_tasks.append({
            'name': name,
            'func': task_func,
            'args': args,
            'kwargs': kwargs
        })
    
    def update_progress(self, progress: float, status: str = None):
        """
        Update progress bar and status.
        
        Args:
            progress: Progress percentage (0-100)
            status: Optional status message
        """
        def update_gui():
            if self.progress_var:
                self.progress_var.set(progress)
            
            if status and self.status_var:
                self.status_var.set(status)
            
            if self.root:
                self.root.update()
        
        # Ensure GUI updates happen in the main thread
        if self.root:
            self.root.after_idle(update_gui)
    
    def execute_startup_tasks(self, tasks: list = None):
        """
        Execute startup tasks with progress updates.
        
        Args:
            tasks: List of task dictionaries with 'name' and 'func' keys
        """
        if tasks is None:
            tasks = self._startup_tasks
            
        if not tasks:
            return
        
        total_tasks = len(tasks)
        
        for i, task in enumerate(tasks):
            # Update status
            task_name = task.get('name', f'Task {i+1}')
            self.update_progress((i / total_tasks) * 100, f"Loading {task_name}...")
            
            # Execute task
            try:
                task_func = task.get('func')
                if task_func and callable(task_func):
                    args = task.get('args', ())
                    kwargs = task.get('kwargs', {})
                    task_func(*args, **kwargs)
            except Exception as e:
                print(f"Error executing task '{task_name}': {e}")
            
            # Small delay for visual feedback
            time.sleep(0.1)
        
        # Final progress update
        self.update_progress(100, "Ready!")
        time.sleep(0.5)  # Brief pause before closing
    
    def show_with_tasks(self, tasks: list, timeout: int = 5000):
        """
        Show splash screen and execute tasks.
        
        Args:
            tasks: List of startup tasks
            timeout: Maximum time to show splash (milliseconds)
        """
        self.create_splash()
        
        def execute_tasks():
            self.execute_startup_tasks(tasks)
            # Schedule close after tasks complete
            self.root.after(1000, self.close)
        
        # Start task execution in background
        task_thread = threading.Thread(target=execute_tasks, daemon=True)
        task_thread.start()
        
        # Set timeout
        self.root.after(timeout, self.close)
        
        # Run the splash screen
        try:
            self.root.mainloop()
        except:
            pass
    
    def show_simple(self, timeout: int = 3000):
        """
        Show simple splash screen with timer.
        
        Args:
            timeout: Time to show splash (milliseconds)
        """
        self.create_splash()
        
        # Simple progress animation
        def animate_progress():
            for i in range(101):
                self.update_progress(i, "Loading application...")
                time.sleep(timeout / 100 / 1000)  # Convert to seconds
                if not self.root.winfo_exists():
                    return
            
        # Start animation in background
        animation_thread = threading.Thread(target=animate_progress, daemon=True)
        animation_thread.start()
        
        # Set timeout to close
        self.root.after(timeout, self.close)
        
        # Run the splash screen
        try:
            self.root.mainloop()
        except:
            pass
    
    def close(self):
        """Close the splash screen."""
        if self.root and self.root.winfo_exists():
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
    
    def is_showing(self) -> bool:
        """Check if splash screen is currently showing."""
        return self.root is not None and self.root.winfo_exists()


def show_splash_with_config(config_manager, tasks: list = None):
    """
    Show splash screen using configuration settings.
    
    Args:
        config_manager: ConfigManager instance
        tasks: Optional list of startup tasks
    """
    # Get configuration
    app_name = config_manager.get_value('APPLICATION', 'app_name', 'AirCheck')
    
    # Get version from navpro package instead of config (which may be outdated)
    try:
        from . import __version__
        version = __version__
    except ImportError:
        try:
            import navpro
            version = navpro.__version__
        except ImportError:
            version = config_manager.get_value('APPLICATION', 'version', '1.2.5')
    
    enable_splash = config_manager.get_bool('APPLICATION', 'enable_splash', True)
    timeout = config_manager.get_int('APPLICATION', 'splash_timeout', 3000)
    
    if not enable_splash:
        return
    
    # Create and show splash with dynamic version
    splash = SplashScreen(app_name, version)
    
    if tasks:
        splash.show_with_tasks(tasks, timeout)
    else:
        splash.show_simple(timeout)


if __name__ == "__main__":
    # Test splash screen
    def test_task(name):
        time.sleep(0.5)
        print(f"Executed {name}")
    
    tasks = [
        {'name': 'Configuration', 'func': test_task, 'args': ('Config',)},
        {'name': 'Database', 'func': test_task, 'args': ('Database',)},
        {'name': 'GUI Components', 'func': test_task, 'args': ('GUI',)},
    ]
    
    splash = SplashScreen("AirCheck", "1.2.4")
    splash.show_with_tasks(tasks)