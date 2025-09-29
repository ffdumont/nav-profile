# AirCheck v1.3.0 Release Notes

## 🚀 Major Release: Dual Distribution Architecture

### Release Date: September 29, 2025

---

## 🎯 **What's New in v1.3.0**

### **🔥 Major Feature: Dual Distribution System**

**For the first time, AirCheck is available in two complementary versions:**

#### **🖥️ GUI Version (`AirCheck.exe`)**
- **Best for:** Interactive users, visual analysis, beginners
- Professional graphical interface with splash screen
- Point-and-click operation
- Visual progress indicators  
- Integrated Google Earth launching
- Real-time status updates and colored output

#### **💻 CLI Version (`AirCheckCLI.exe`)**  
- **Best for:** Automation, scripting, batch processing, power users
- Full command-line interface with all GUI functionality
- Scriptable operations for workflow integration
- Batch processing capabilities
- Perfect for automation and server deployments
- No GUI dependencies

### **🛠️ Architecture Improvements**

#### **Clean Entry Points**
- **`aircheck.py`**: Single professional GUI launcher with splash screen
- **`navpro_gui.py`**: Pure GUI class (removed redundant main() function)
- **`navpro_cli.py`**: Full-featured CLI application

#### **Unified Splash Screen Experience**
- Both GUI entry points now use the same professional AirCheck splash screen
- Consistent branding and user experience
- Enhanced progress tracking and status messages

#### **Enhanced Build System**
- **Dual build infrastructure**: Build GUI-only, CLI-only, or both
- **Automated packaging**: Single command creates complete distribution
- **Professional launchers**: Easy-to-use batch scripts for both versions

---

## 🎁 **Distribution Package Contents**

### **Executables**
- **`AirCheck.exe`** (46MB): Complete GUI application
- **`AirCheckCLI.exe`** (30MB): Full CLI tool

### **Launchers**
- **`Launch_AirCheck.bat`**: Interactive menu to choose GUI or CLI
- **`Launch_AirCheck_GUI.bat`**: Direct GUI launcher
- **`Launch_AirCheck_CLI.bat`**: CLI environment with help

### **Documentation**
- **`README.txt`**: Complete usage guide for both versions
- Detailed examples for GUI and CLI usage
- Quick start guides for different user types

---

## 💡 **User Benefits**

### **For Interactive Users**
- Same professional interface you know and love
- Enhanced splash screen experience
- No changes to existing workflows
- Better error handling and progress feedback

### **For Power Users & Developers**
- **Best of both worlds**: GUI for interactive work, CLI for automation
- **Scripting capabilities**: Integrate airspace analysis into your workflows
- **Batch processing**: Analyze multiple files automatically
- **CI/CD integration**: Use CLI version in automated pipelines

### **For System Administrators**
- **Flexible deployment**: Deploy GUI-only, CLI-only, or both
- **Server-friendly CLI**: No GUI dependencies for server deployments
- **Automation-ready**: Perfect for scheduled analysis jobs

---

## 🔧 **Technical Improvements**

### **Code Architecture**
- Eliminated redundant entry points
- Clean separation of GUI and CLI concerns
- Improved maintainability and testing
- Better error handling across both versions

### **Build System**
- **PyInstaller optimization**: Separate specs for GUI and CLI
- **Size optimization**: CLI version 35% smaller (no GUI dependencies)
- **Professional packaging**: Complete distribution creation automation

### **Performance**
- **Faster startup**: Optimized module loading
- **Reduced memory footprint**: CLI version uses minimal resources
- **Better error recovery**: More robust error handling

---

## 📖 **CLI Usage Examples**

### **Basic Commands**
```bash
# List airspaces crossed by flight
AirCheckCLI list --profile flight.kml

# Generate KML visualization  
AirCheckCLI generate --profile flight.kml

# Correct profile and analyze
AirCheckCLI list --fix-profile flight.kml

# Show database statistics
AirCheckCLI stats

# Get detailed help
AirCheckCLI help
```

### **Advanced Automation**
```bash
# Batch process multiple flights
for %%f in (*.kml) do AirCheckCLI list --profile "%%f" --output results.txt

# Generate reports with custom settings
AirCheckCLI list --profile flight.kml --corridor-height 1000 --filter-types ""

# Integration with other tools
AirCheckCLI generate --profile flight.kml | findstr "CRITICAL"
```

---

## 🔄 **Migration from v1.2.x**

### **Existing Users (No Action Required)**
- All existing workflows continue to work unchanged
- Same GUI interface and functionality
- Your data files and configurations are fully compatible

### **New CLI Users**
- Start with `AirCheckCLI --help` to explore available commands
- Use `Launch_AirCheck_CLI.bat` for guided getting started experience
- Refer to `README.txt` for detailed examples and best practices

---

## 🎯 **What's Coming Next**

### **Future Enhancements**
- Enhanced CLI output formats (JSON, XML, CSV)
- REST API interface for web integration
- Docker containers for cloud deployment
- Enhanced automation and reporting features

---

## 📋 **System Requirements**

- **Operating System**: Windows 7 or later
- **Memory**: 4GB RAM recommended
- **Storage**: 100MB free space for installation
- **Optional**: Google Earth Pro for KML visualization

---

## 🆘 **Support & Documentation**

### **GUI Version**
- Use built-in help and status messages
- Visual feedback and progress indicators guide you through operations

### **CLI Version**
- Run `AirCheckCLI help` for detailed examples and documentation
- `AirCheckCLI --help` for command reference
- All GUI functionality available via command line

### **General Support**
- Check `README.txt` for comprehensive usage guide
- Review release notes for latest features and improvements

---

## ⚠️ **Aviation Safety Notice**

**FOR EDUCATIONAL AND FLIGHT PLANNING PURPOSES ONLY**

Always verify results with official aeronautical publications before flight. AirCheck is designed to assist with flight planning but does not replace official navigation aids and procedures.

---

## 🏆 **Acknowledgments**

This release represents a significant milestone in making professional airspace analysis tools accessible to both interactive users and automation workflows. The dual distribution system provides unprecedented flexibility for different use cases while maintaining the professional quality and accuracy you expect from AirCheck.

---

**Happy Flying! ✈️**

*AirCheck Development Team*  
*Version 1.3.0 - September 29, 2025*