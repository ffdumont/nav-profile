#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NavPro GUI - Windows GUI Application for Navigation Profile Analysis
Provides easy          # Profile buttons (first row)
        profile_buttons_frame = ttk.Frame(buttons_frame)
        profile_buttons_frame.pack(pady=5)
        
        self.correct_btn = ttk.Button(profile_buttons_frame, text="🔧 Correct Profile", 
                                     command=self.correct_profile, style='Accent.TButton')
        self.correct_btn.pack(side=tk.LEFT, padx=10)elf.correct_btn = ttk.Button(profile_buttons_frame, text="🔧 Correct Profile", 
                                     command=self.correct_profile, style='Accent.TButton')
        self.correct_btn.pack(side=tk.LEFT, padx=10)
        
        self.view_profile_btn = ttk.Button(profile_buttons_frame, text="📊 View Profile", 
                                          command=self.view_profile)
        self.view_profile_btn.pack(side=tk.LEFT, padx=10)erface for AIXM processing and flight path analysis
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
import subprocess
import webbrowser
from pathlib import Path
import io
import contextlib

# Add the project directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import our core functionality
from core.flight_analyzer import FlightProfileAnalyzer
from visualization.kml_generator import KMLVolumeService


class NavProGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NavPro - Profile Corrector & Airspace Analyzer")
        self.root.geometry("900x800")
        self.root.minsize(700, 600)
        
        # Variables for file paths and settings
        self.aixm_file = tk.StringVar()
        self.kml_file = tk.StringVar()
        self.output_dir = tk.StringVar(value=str(Path.cwd() / "output"))
        self.corridor_height = tk.IntVar(value=500)  # Default 500 ft
        self.corridor_width = tk.DoubleVar(value=5.0)  # Default 5.0 NM
        
        # Profile correction settings
        self.enable_correction = tk.BooleanVar(value=True)
        self.climb_rate = tk.IntVar(value=500)  # ft/min
        self.descent_rate = tk.IntVar(value=500)  # ft/min
        self.ground_speed = tk.IntVar(value=100)  # kts
        
        # Track corrected file path
        self.corrected_kml_file = ""
        
        # Create GUI elements
        self.create_widgets()
        
        # Set default paths if files exist
        self.set_default_paths()
        
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="NavPro - Profile Corrector & Airspace Analyzer", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # AIXM File Selection
        ttk.Label(main_frame, text="AIXM XML File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.aixm_file, width=60).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_aixm).grid(row=1, column=2, padx=5)
        
        # KML File Selection
        ttk.Label(main_frame, text="KML Flight Profile:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.kml_file, width=60).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_kml).grid(row=2, column=2, padx=5)
        
        # Output Directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_dir, width=60).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=3, column=2, padx=5)
        
        # Corridor Settings Frame
        corridor_frame = ttk.LabelFrame(main_frame, text="Analysis Settings", padding="10")
        corridor_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        corridor_frame.columnconfigure(1, weight=1)
        corridor_frame.columnconfigure(3, weight=1)
        
        # Corridor dimensions
        ttk.Label(corridor_frame, text="Corridor Height (±ft):").grid(row=0, column=0, sticky=tk.W, padx=5)
        height_spin = ttk.Spinbox(corridor_frame, from_=0, to=10000, textvariable=self.corridor_height, width=10)
        height_spin.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(corridor_frame, text="Corridor Width (±NM):").grid(row=0, column=2, sticky=tk.W, padx=15)
        width_spin = ttk.Spinbox(corridor_frame, from_=0.0, to=50.0, increment=0.5, 
                                textvariable=self.corridor_width, width=10)
        width_spin.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Profile Correction Settings Frame
        correction_frame = ttk.LabelFrame(main_frame, text="Profile Correction Settings", padding="10")
        correction_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        correction_frame.columnconfigure(1, weight=1)
        correction_frame.columnconfigure(3, weight=1)
        correction_frame.columnconfigure(5, weight=1)
        
        # Enable profile correction checkbox
        ttk.Checkbutton(correction_frame, text="Enable Profile Correction", 
                       variable=self.enable_correction).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Climb rate
        ttk.Label(correction_frame, text="Climb Rate (ft/min):").grid(row=1, column=0, sticky=tk.W, padx=5)
        climb_spin = ttk.Spinbox(correction_frame, from_=100, to=2000, textvariable=self.climb_rate, width=10)
        climb_spin.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Descent rate
        ttk.Label(correction_frame, text="Descent Rate (ft/min):").grid(row=1, column=2, sticky=tk.W, padx=15)
        descent_spin = ttk.Spinbox(correction_frame, from_=100, to=2000, textvariable=self.descent_rate, width=10)
        descent_spin.grid(row=1, column=3, sticky=tk.W, padx=5)
        
        # Ground speed
        ttk.Label(correction_frame, text="Ground Speed (kts):").grid(row=1, column=4, sticky=tk.W, padx=15)
        speed_spin = ttk.Spinbox(correction_frame, from_=50, to=500, textvariable=self.ground_speed, width=10)
        speed_spin.grid(row=1, column=5, sticky=tk.W, padx=5)
        
        # Action Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        # Profile Correction and Visualization buttons (first row)
        profile_buttons_frame = ttk.Frame(buttons_frame)
        profile_buttons_frame.pack(pady=5)
        
        self.correct_btn = ttk.Button(profile_buttons_frame, text="� Correct Profile", 
                                     command=self.correct_profile, style='Accent.TButton')
        self.correct_btn.pack(side=tk.LEFT, padx=5)
        
        self.view_profile_btn = ttk.Button(profile_buttons_frame, text="📊 View Profile", 
                                          command=self.view_profile)
        self.view_profile_btn.pack(side=tk.LEFT, padx=10)
        
        # Airspace Analysis buttons (second row)  
        analysis_buttons_frame = ttk.Frame(buttons_frame)
        analysis_buttons_frame.pack(pady=5)
        
        self.list_btn = ttk.Button(analysis_buttons_frame, text="📋 List Airspaces", 
                                  command=self.list_airspaces, style='Accent.TButton')
        self.list_btn.pack(side=tk.LEFT, padx=10)
        
        self.generate_btn = ttk.Button(analysis_buttons_frame, text="🌍 View Airspaces in Google Earth", 
                                      command=self.generate_kml, style='Accent.TButton')
        self.generate_btn.pack(side=tk.LEFT, padx=10)
        
        # Output Text Area
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="5")
        output_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Configure main_frame row to expand
        main_frame.rowconfigure(7, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=2)
        
    def set_default_paths(self):
        """Set default file paths if files exist"""
        data_dir = Path("data")
        if data_dir.exists():
            # Look for AIXM file
            aixm_files = list(data_dir.glob("*.xml"))
            if aixm_files:
                self.aixm_file.set(str(aixm_files[0]))
            
            # Look for KML files
            kml_files = list(data_dir.glob("*.kml"))
            if kml_files:
                self.kml_file.set(str(kml_files[0]))
    
    def browse_aixm(self):
        """Browse for AIXM XML file"""
        filename = filedialog.askopenfilename(
            title="Select AIXM XML File",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
            initialdir="data" if Path("data").exists() else "."
        )
        if filename:
            self.aixm_file.set(filename)
    
    def browse_kml(self):
        """Browse for KML flight profile file"""
        filename = filedialog.askopenfilename(
            title="Select KML Flight Profile",
            filetypes=[("KML files", "*.kml"), ("All files", "*.*")],
            initialdir="data" if Path("data").exists() else "."
        )
        if filename:
            self.kml_file.set(filename)
    
    def browse_output(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get()
        )
        if directory:
            self.output_dir.set(directory)
    
    def log_output(self, message):
        """Add message to output text area"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update()
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)
    
    def validate_inputs(self):
        """Validate that required inputs are provided"""
        if not self.kml_file.get():
            messagebox.showerror("Error", "Please select a KML flight profile file.")
            return False
        
        if not os.path.exists(self.kml_file.get()):
            messagebox.showerror("Error", f"KML file not found: {self.kml_file.get()}")
            return False
        
        # Create output directory if it doesn't exist
        output_path = Path(self.output_dir.get())
        output_path.mkdir(parents=True, exist_ok=True)
        
        return True
    
    def correct_profile(self):
        """Run profile correction in a separate thread"""
        if not self.validate_inputs():
            return
        
        # Disable buttons and start progress
        self.disable_buttons()
        self.progress.start()
        self.status_var.set("Correcting flight profile...")
        self.clear_output()
        
        # Run in separate thread
        thread = threading.Thread(target=self._run_profile_correction)
        thread.daemon = True
        thread.start()
    
    def _run_profile_correction(self):
        """Run the actual profile correction"""
        try:
            # Add profile-correction directory to path
            profile_correction_dir = Path(__file__).parent.parent / "profile-correction"
            sys.path.insert(0, str(profile_correction_dir))
            
            from kml_profile_corrector import KMLProfileCorrector
            
            self.log_output(f"🔧 Correcting flight profile: {os.path.basename(self.kml_file.get())}")
            self.log_output(f"   Climb rate: {self.climb_rate.get()} ft/min")
            self.log_output(f"   Descent rate: {self.descent_rate.get()} ft/min")
            self.log_output(f"   Ground speed: {self.ground_speed.get()} kts")
            self.log_output("")
            
            # Initialize corrector
            corrector = KMLProfileCorrector(
                climb_rate_fpm=self.climb_rate.get(),
                descent_rate_fpm=self.descent_rate.get(),
                ground_speed_kts=self.ground_speed.get()
            )
            
            # Generate corrected file path
            kml_path = Path(self.kml_file.get())
            self.corrected_kml_file = str(kml_path.parent / f"{kml_path.stem}_corrected.kml")
            
            # Correct the profile
            success = corrector.correct_kml_file(self.kml_file.get(), self.corrected_kml_file)
            
            if success:
                self.log_output(f"✅ Profile correction completed successfully!")
                self.log_output(f"   Corrected file: {os.path.basename(self.corrected_kml_file)}")
                self.log_output("")
                
                # Enable corrected profile buttons
                self.root.after(0, self._enable_corrected_buttons)
                
                # Also generate airspaces if enabled
                if self.enable_correction.get():
                    self.log_output("🗺️ Generating airspace analysis for corrected profile...")
                    # The corrector already generates airspace KML automatically
                    airspace_file = str(kml_path.parent / f"{kml_path.stem}_corrected_airspaces.kml")
                    if os.path.exists(airspace_file):
                        self.log_output(f"✅ Airspace analysis saved: {os.path.basename(airspace_file)}")
                    
                self.log_output("🎯 Profile correction workflow complete!")
            else:
                self.log_output("❌ Profile correction failed")
                
        except Exception as e:
            self.log_output(f"❌ Error during profile correction: {str(e)}")
            import traceback
            self.log_output(traceback.format_exc())
        
        finally:
            self.root.after(0, self._analysis_complete)
    
    def view_profile(self):
        """Smart view profile - uses corrected profile if available and correction is enabled"""
        if not self.kml_file.get():
            messagebox.showerror("Error", "Please select a KML file first.")
            return
        
        # Choose which profile to view based on correction setting and availability
        if self.enable_correction.get() and self.corrected_kml_file:
            profile_file = self.corrected_kml_file
            profile_type = "corrected"
        else:
            profile_file = self.kml_file.get()
            profile_type = "original"
            
        self._view_profile(profile_file, profile_type)
    
    def _view_profile(self, kml_file, profile_type):
        """View profile using the enhanced profile viewer"""
        try:
            # Add profile-correction directory to path
            profile_correction_dir = Path(__file__).parent.parent / "profile-correction"
            sys.path.insert(0, str(profile_correction_dir))
            
            # Import and run the profile viewer
            import subprocess
            import sys
            
            viewer_script = profile_correction_dir / "kml_profile_viewer.py"
            cmd = [sys.executable, str(viewer_script), kml_file]
            
            self.log_output(f"📊 Opening {profile_type} profile visualization...")
            subprocess.Popen(cmd)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open profile viewer: {str(e)}")
    
    def disable_buttons(self):
        """Disable all action buttons during processing"""
        self.correct_btn.config(state='disabled')
        self.view_profile_btn.config(state='disabled')
        self.list_btn.config(state='disabled')
        self.generate_btn.config(state='disabled')
    
    def _enable_corrected_buttons(self):
        """Enable buttons that work with corrected profiles"""
        # No specific corrected-only buttons anymore - view_profile is smart
        pass
    
    def _analysis_complete(self):
        """Re-enable buttons after analysis is complete"""
        self.correct_btn.config(state='normal')
        self.view_profile_btn.config(state='normal')
        self.list_btn.config(state='normal')
        self.generate_btn.config(state='normal')
        self.progress.stop()
        self.status_var.set("Ready")
    
    def _display_airspace_list(self, crossings, prefix_emoji):
        """Helper method to display a list of airspace crossings"""
        for i, crossing in enumerate(crossings, 1):
            airspace = crossing['airspace']
            distance = crossing['distance_km']
            
            # Check for critical airspaces
            code_type = airspace.get('code_type', 'Unknown').upper()
            airspace_class = airspace.get('airspace_class', 'Unknown').upper()
            is_red_zone = (code_type in ['P', 'R'] or airspace_class == 'A')
            
            # Choose emoji based on airspace type
            if is_red_zone:
                type_emoji = "⛔"
            elif code_type in ['CTR']:
                type_emoji = "🏢"
            else:
                type_emoji = "🌐"
            
            warning = " *** CRITICAL AIRSPACE ***" if is_red_zone else ""
            
            self.log_output(f"{i:2d}. {prefix_emoji} {type_emoji} {airspace['name']} ({airspace.get('code_id', 'N/A')}){warning}")
            self.log_output(f"     Type: {code_type} - Class: {airspace_class}")
            
            # Altitude info
            lower_alt = airspace.get('lower_limit_ft_converted', airspace.get('lower_limit_ft', 'N/A'))
            upper_alt = airspace.get('upper_limit_ft_converted', airspace.get('upper_limit_ft', 'N/A'))
            self.log_output(f"     Altitude: {lower_alt} - {upper_alt} ft")
            self.log_output(f"     Distance: {distance:.1f} km from start")
            self.log_output("")
    
    def list_airspaces(self):
        """Run airspace listing analysis in a separate thread"""
        if not self.validate_inputs():
            return
        
        # Use corrected profile if available, otherwise original
        analysis_file = self.corrected_kml_file if self.corrected_kml_file and self.enable_correction.get() else self.kml_file.get()
        
        # Disable buttons and start progress
        self.disable_buttons()
        self.progress.start()
        self.status_var.set("Analyzing flight path...")
        self.clear_output()
        
        # Store analysis file for the thread
        self.analysis_file = analysis_file
        
        # Run in separate thread to avoid freezing GUI
        thread = threading.Thread(target=self._run_list_analysis)
        thread.daemon = True
        thread.start()
    
    def _run_list_analysis(self):
        """Run the actual airspace listing analysis"""
        try:
            analysis_file = getattr(self, 'analysis_file', self.kml_file.get())
            file_type = "corrected" if analysis_file != self.kml_file.get() else "original"
            
            self.log_output(f"🛩️ Analyzing {file_type} flight path: {os.path.basename(analysis_file)}")
            self.log_output(f"   Corridor: ±{self.corridor_height.get()} ft, ±{self.corridor_width.get()} NM")
            self.log_output("")
            
            # Initialize analyzer
            db_path = "data/airspaces.db"
            if not os.path.exists(db_path):
                self.log_output("❌ Error: Airspace database not found. Please ensure data/airspaces.db exists.")
                return
            
            analyzer = FlightProfileAnalyzer(
                db_path, 
                self.corridor_height.get(), 
                self.corridor_width.get()
            )
            
            # Get chronological crossings
            self.log_output("Building spatial index...")
            crossings = analyzer.get_chronological_crossings(analysis_file, sample_distance_km=5.0)
            
            if not crossings:
                self.log_output("❌ No airspace crossings found")
                return
            
            # Separate actual crossings from corridor-only discoveries
            actual_crossings = [c for c in crossings if c.get('is_actual_crossing', True)]
            corridor_only = [c for c in crossings if not c.get('is_actual_crossing', True)]
            
            self.log_output(f"📊 Flight Path Analysis Results:")
            self.log_output(f"   Total airspaces detected: {len(crossings)}")
            self.log_output(f"   Actually crossed by flight path: {len(actual_crossings)}")
            self.log_output(f"   Additional in corridor (±{self.corridor_height.get()} ft, ±{self.corridor_width.get()} NM): {len(corridor_only)}")
            self.log_output("")
            
            # Apply filtering to actual crossings
            filter_types = {'SECTOR', 'FIR', 'D-OTHER'}
            filtered_actual = []
            filtered_corridor = []
            actual_filtered_count = 0
            corridor_filtered_count = 0
            
            for crossing in actual_crossings:
                airspace = crossing['airspace']
                code_type = airspace.get('code_type', 'Unknown').upper()
                
                if code_type not in filter_types:
                    filtered_actual.append(crossing)
                else:
                    actual_filtered_count += 1
            
            for crossing in corridor_only:
                airspace = crossing['airspace']
                code_type = airspace.get('code_type', 'Unknown').upper()
                
                if code_type not in filter_types:
                    filtered_corridor.append(crossing)
                else:
                    corridor_filtered_count += 1
            
            total_filtered = actual_filtered_count + corridor_filtered_count
            
            self.log_output(f"✅ Analysis complete (filtered out {total_filtered} SECTOR/FIR/D-OTHER zones)")
            self.log_output(f"📋 Relevant airspaces: {len(filtered_actual)} actual crossings + {len(filtered_corridor)} corridor discoveries")
            self.log_output("")
            
            # Display actual crossings first
            if filtered_actual:
                self.log_output("🎯 ACTUAL FLIGHT PATH CROSSINGS (chronological order):")
                self.log_output("=" * 80)
                self._display_airspace_list(filtered_actual, "✈️")
                self.log_output("")
            
            # Display corridor-only discoveries
            if filtered_corridor:
                self.log_output(f"🔍 ADDITIONAL AIRSPACES IN CORRIDOR (±{self.corridor_height.get()} ft, ±{self.corridor_width.get()} NM):")
                self.log_output("=" * 80)
                self._display_airspace_list(filtered_corridor, "📡")
                self.log_output("")
            
            # Combine for critical analysis
            all_filtered = filtered_actual + filtered_corridor
            
            # Critical airspace warning
            red_zone_count = 0
            critical_airspaces = []
            
            for crossing in all_filtered:
                airspace = crossing['airspace']
                distance = crossing['distance_km']
            
            # Critical airspace warning
            if red_zone_count > 0:
                self.log_output(f"⚠️  WARNING: {red_zone_count} CRITICAL AIRSPACE CROSSING(S) DETECTED!")
                self.log_output("These airspaces may require special authorization or are prohibited:")
                
                for idx, critical in enumerate(critical_airspaces, 1):
                    if critical['type'] == 'R':
                        reason = "Restricted Area - Flight restrictions apply"
                    elif critical['type'] == 'P':
                        reason = "Prohibited Area - Flight prohibited"
                    elif critical['class'] == 'A':
                        reason = "Class A Airspace - IFR clearance required"
                    else:
                        reason = "Critical airspace"
                    
                    self.log_output(f"  {idx}. {critical['name']} ({critical['code_id']}) - {reason}")
                
                self.log_output("")
                self.log_output("Review flight plan carefully - these zones require special attention!")
            
            self.log_output(f"🏁 Analysis complete - {len(all_filtered)} relevant airspaces found along flight path")
            
        except Exception as e:
            self.log_output(f"❌ Error during analysis: {str(e)}")
            import traceback
            self.log_output(traceback.format_exc())
        
        finally:
            # Re-enable buttons and stop progress
            self.root.after(0, self._analysis_complete)
    
    def generate_kml(self):
        """Generate KML file and launch in Google Earth"""
        if not self.validate_inputs():
            return
        
        # Use corrected profile if available, otherwise original
        analysis_file = self.corrected_kml_file if self.corrected_kml_file and self.enable_correction.get() else self.kml_file.get()
        
        # Disable buttons and start progress
        self.disable_buttons()
        self.progress.start()
        self.status_var.set("Generating KML...")
        self.clear_output()
        
        # Store analysis file for the thread
        self.analysis_file = analysis_file
        
        # Run in separate thread
        thread = threading.Thread(target=self._run_kml_generation)
        thread.daemon = True
        thread.start()
    
    def _run_kml_generation(self):
        """Run the actual KML generation"""
        try:
            analysis_file = getattr(self, 'analysis_file', self.kml_file.get())
            file_type = "corrected" if analysis_file != self.kml_file.get() else "original"
            
            self.log_output(f"🛩️ Generating KML for {file_type} flight: {os.path.basename(analysis_file)}")
            self.log_output(f"   Corridor: ±{self.corridor_height.get()} ft, ±{self.corridor_width.get()} NM")
            self.log_output(f"   Output: {self.output_dir.get()}")
            self.log_output("")
            
            # Use existing generate functionality from navpro.py
            # This is similar to cmd_generate_profile but adapted for GUI
            
            # Initialize analyzer
            db_path = "data/airspaces.db"
            analyzer = FlightProfileAnalyzer(db_path, self.corridor_height.get(), self.corridor_width.get())
            
            self.log_output("Building spatial index...")
            crossings = analyzer.get_chronological_crossings(analysis_file, sample_distance_km=5.0)
            
            if not crossings:
                self.log_output("❌ No airspace crossings found - no KML files to generate")
                return
            
            # Use actual crossings for KML generation (more relevant than corridor discoveries)
            actual_crossings = [c for c in crossings if c.get('is_actual_crossing', True)]
            
            if not actual_crossings:
                self.log_output("❌ No actual flight path crossings found - using corridor discoveries")
                actual_crossings = crossings  # Fall back to all crossings
            
            # Filter crossings
            filter_types = {'SECTOR', 'FIR', 'D-OTHER'}
            filtered_crossings = [c for c in actual_crossings 
                                if c['airspace'].get('code_type', '').upper() not in filter_types]
            
            if not filtered_crossings:
                self.log_output("❌ No relevant airspace crossings after filtering")
                return
            
            # Get unique airspace IDs
            unique_ids = list({c['airspace']['id'] for c in filtered_crossings})
            
            self.log_output(f"✅ Found {len(crossings)} crossings across {len(unique_ids)} unique airspaces")
            self.log_output(">> Generating organized KML profile...")
            
            # Generate KML
            kml_service = KMLVolumeService(db_path)  # Pass the database path
            flight_name = os.path.splitext(os.path.basename(analysis_file))[0]
            output_file = Path(self.output_dir.get()) / f"flight_profile_{flight_name}_combined.kml"
            
            # Parse flight coordinates
            from core.spatial_query import KMLFlightPathParser
            flight_coordinates = KMLFlightPathParser.parse_kml_coordinates(analysis_file)
            
            # Generate organized KML
            self.log_output(f"   >> Creating organized profile KML: {output_file.name}")
            self.log_output(f"      >> Organizing airspaces into KML folders by type")
            
            kml_content = kml_service.generate_multiple_airspaces_kml(
                unique_ids,
                flight_name=flight_name,
                flight_coordinates=flight_coordinates
            )
            
            # Write KML file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(kml_content)
            
            self.log_output(f"      >> Organized profile KML saved: {output_file}")
            self.log_output("")
            self.log_output("=" * 60)
            self.log_output(f"🎉 KML generation complete!")
            self.log_output(f"   Profile: 1 organized KML file with {len(unique_ids)} airspaces")
            self.log_output(f"   Organization: Airspaces grouped by type in Google Earth folders")
            self.log_output(f"   File: {output_file}")
            
            # Launch in Google Earth
            self.log_output("")
            self.log_output("🌍 Launching Google Earth Pro...")
            self._launch_google_earth(str(output_file))
            
        except Exception as e:
            self.log_output(f"❌ Error during KML generation: {str(e)}")
            import traceback
            self.log_output(traceback.format_exc())
        
        finally:
            self.root.after(0, self._analysis_complete)
    
    def _launch_google_earth(self, kml_file):
        """Launch Google Earth Pro with the generated KML file"""
        try:
            # Common Google Earth Pro installation paths
            ge_paths = [
                r"C:\Program Files\Google\Google Earth Pro\client\googleearth.exe",
                r"C:\Program Files (x86)\Google\Google Earth Pro\client\googleearth.exe",
                r"C:\Users\{}\AppData\Local\Google\Google Earth Pro\client\googleearth.exe".format(os.getenv('USERNAME'))
            ]
            
            google_earth_exe = None
            for path in ge_paths:
                if os.path.exists(path):
                    google_earth_exe = path
                    break
            
            if google_earth_exe:
                subprocess.Popen([google_earth_exe, kml_file])
                self.log_output(f"✅ Launched Google Earth Pro with {os.path.basename(kml_file)}")
            else:
                self.log_output("⚠️  Google Earth Pro not found in standard locations.")
                self.log_output("   Please install Google Earth Pro or manually open the KML file:")
                self.log_output(f"   {kml_file}")
                
                # Try to open with default application
                try:
                    os.startfile(kml_file)
                    self.log_output("✅ Opened KML file with default application")
                except:
                    pass
                    
        except Exception as e:
            self.log_output(f"❌ Error launching Google Earth: {str(e)}")
            self.log_output(f"   KML file saved at: {kml_file}")


def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    
    # Configure ttk styles
    style = ttk.Style()
    # Use a modern theme if available
    available_themes = style.theme_names()
    if 'vista' in available_themes:
        style.theme_use('vista')
    elif 'clam' in available_themes:
        style.theme_use('clam')
    
    app = NavProGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()