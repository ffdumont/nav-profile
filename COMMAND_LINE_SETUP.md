# NavPro Command Line Setup

## Quick Start (Current Session)

You can run NavPro from the project root using:

```bash
# Windows Batch
.\navpro.bat list --fix-profile "data\LFXU-LFFU-2025-09-25-14-51-39.kml"

# PowerShell  
.\navpro.ps1 list --fix-profile "data\LFXU-LFFU-2025-09-25-14-51-39.kml"
```

## Permanent Setup (Add to PATH)

### Option 1: Automatic Setup
Run the setup script once:
```bash
.\setup_path.bat
```

### Option 2: Manual Setup
1. Add the project root folder to your Windows PATH environment variable
2. Restart your terminal  
3. Then use: `navpro list --fix-profile "path\to\flight.kml"`

## File Structure

The project has two navpro.bat files by design:

- **`navpro.bat` (root)**: Main wrapper - redirects to scripts folder
- **`scripts\navpro.bat`**: Actual launcher - handles venv activation and Python execution

This setup allows:
- Clean root-level access (`navpro` command)  
- Automatic virtual environment detection and activation
- Fallback to system Python if no venv exists
- Proper path resolution regardless of working directory

## Usage Examples

```bash
# Profile correction and analysis
navpro list --fix-profile "data\LFXU-LFFU-2025-09-25-14-51-39.kml"

# Generate KML for corrected profile  
navpro generate --fix-profile "data\LFXU-LFFU-2025-09-25-14-51-39.kml"

# Standard airspace search
navpro list --name "CHEVREUSE"

# Help
navpro help
```

## Features

✅ Automatic virtual environment activation  
✅ Works from any directory (when in PATH)  
✅ Proper argument passing  
✅ Fallback to system Python  
✅ Windows PowerShell and CMD compatibility