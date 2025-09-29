# AirCheck - Flight Profile Analysis Tool

## Overview
AirCheck provides professional flight planning services including altitude profile correction, airspace analysis, and 3D visualization.

## Available Versions

### 1. GUI Version (AirCheck.exe)
**Best for:** Interactive use, visual analysis, beginners
- Graphical user interface
- Point-and-click operation  
- Visual progress indicators
- Integrated Google Earth launching

**To run:** Double-click `AirCheck.exe` or use `Launch_AirCheck_GUI.bat`

### 2. CLI Version (AirCheckCLI.exe)
**Best for:** Automation, scripting, batch processing, advanced users
- Command-line interface
- Scriptable operations
- Batch processing capabilities
- Integration with other tools

**To run:** Use `Launch_AirCheck_CLI.bat` or run `AirCheckCLI --help` from command prompt

## Quick Start

### For GUI Users:
1. Double-click `Launch_AirCheck_GUI.bat`
2. Select your AIXM XML file
3. Select your KML flight profile
4. Click "List Airspaces" or "View Airspaces in Google Earth"

### For CLI Users:
1. Open `Launch_AirCheck_CLI.bat` 
2. Type `AirCheckCLI --help` to see all commands
3. Example: `AirCheckCLI list --profile flight.kml`

## Common Commands (CLI)

```bash
# List airspaces crossed by a flight
AirCheckCLI list --profile flight.kml

# Generate KML visualization
AirCheckCLI generate --profile flight.kml

# Correct flight profile and analyze
AirCheckCLI list --fix-profile flight.kml

# Show database statistics
AirCheckCLI stats

# Get detailed help
AirCheckCLI help
```

## Data Directory
The data/ directory contains:
- airspaces.db: Airspace database
- input/: AIXM XML files
- samples/: Sample KML flight profiles
- output/: Generated analysis results

## Requirements
- Windows 7 or later
- No additional software required (self-contained executables)
- For Google Earth visualization: Google Earth Pro (optional)

## Aviation Safety Notice
WARNING: FOR EDUCATIONAL AND FLIGHT PLANNING PURPOSES ONLY
Always verify with official aeronautical publications before flight!

## Support
- GUI: Use the built-in help and status messages
- CLI: Run `AirCheckCLI help` for detailed examples and documentation
