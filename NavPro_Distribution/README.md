# NavPro - Navigation Profile Analyzer

## Windows Distribution Package

A user-friendly Windows application for analyzing flight paths and generating KML visualizations with airspace crossings.

### 🎯 **Features**
- **Easy File Selection**: Browse for AIXM XML files and KML flight profiles
- **Customizable Corridors**: Set vertical (±feet) and horizontal (±nautical miles) search dimensions  
- **Critical Airspace Detection**: Automatic highlighting of Class A, Prohibited (P), and Restricted (R) zones
- **Organized KML Output**: Generates Google Earth-ready files with airspaces grouped by type
- **Google Earth Integration**: Automatically launches Google Earth Pro with generated KML files
- **No Terminal Required**: All output displayed in user-friendly GUI windows

### 📋 **Requirements**
- Windows 10/11 (64-bit)
- Google Earth Pro (recommended for KML viewing)
- AIXM XML airspace database file
- KML flight profile files (routes or traces)

### 📁 **Sample Files Included**
This distribution includes sample files to get you started immediately:

#### **sample_data/AIXM4.5_all_FR_OM_2025-10-02.xml**
- Complete French airspace database (AIXM 4.5 format)
- Contains TMAs, Restricted Areas, Class A airspace, Control Zones, and RAS sectors
- Ready to use with the application - no additional setup required

#### **sample_data/LFXU-LFFU-CORRECTED.kml**
- Sample flight route: Les Mureaux (LFXU) to Châteauneuf-sur-Cher (LFFU)  
- Corrected altitude profile with proper flight constraints
- Demonstrates critical airspace crossings (Class A, Restricted Areas)
- Perfect for testing all application features

#### **Quick Test:**
1. Launch NavPro
2. Select `sample_data/AIXM4.5_all_FR_OM_2025-10-02.xml` as AIXM file
3. Select `sample_data/LFXU-LFFU-CORRECTED.kml` as flight profile
4. Click "List Airspace Crossings" to see the analysis
5. Click "Generate KML" to create Google Earth visualization

### 🚀 **Quick Start**

#### 1. Install Google Earth Pro (Optional but Recommended)
- Download from: https://www.google.com/earth/versions/#earth-pro
- Install with default settings

#### 2. Run NavPro
- Double-click `navpro_gui.exe` 
- The application will launch with a clean, intuitive interface

#### 3. Load Your Files
- **AIXM XML File**: Click "Browse" to select your airspace database
- **KML Flight Profile**: Select your flight route or trace file
- **Output Directory**: Choose where to save generated KML files

#### 4. Configure Corridor
- **Height (±ft)**: Vertical search distance (default: 1000 feet)
- **Width (±NM)**: Horizontal search distance (default: 10 nautical miles)

#### 5. Analyze Flight
- **📋 List Airspace Crossings**: Shows all airspaces crossed with critical zone warnings
- **🌍 Generate KML & Open in Google Earth**: Creates organized KML and launches in Google Earth Pro

### ⚠️ **Critical Airspace Detection**
The application automatically identifies and highlights dangerous airspaces:
- **Class A**: High-altitude airspace requiring IFR clearance
- **Prohibited (P)**: Areas where flight is completely prohibited
- **Restricted (R)**: Areas with flight restrictions or special limitations

Critical airspaces are marked with `*** CRITICAL AIRSPACE ***` and listed in the warning summary.

### 📁 **File Structure**
```
NavPro/
├── navpro_gui.exe          # Main application executable
├── data/                   # Data files (if included)
│   └── airspaces.db       # Airspace database (required)
└── README.md              # This file
```

### 🔧 **Troubleshooting**

#### "Airspace database not found"
- Ensure `data/airspaces.db` exists in the same folder as the executable
- Or browse to select your AIXM XML file location

#### "Google Earth Pro not found"
- Install Google Earth Pro from the official Google website
- The KML file will still be generated and can be opened manually

#### "No airspace crossings found"  
- Check that your KML file contains valid flight coordinates
- Verify corridor dimensions aren't too restrictive (try increasing height/width)
- Ensure the flight path actually crosses airspace boundaries

### 📊 **KML Output Organization**
Generated KML files are organized into folders by airspace type:
- 🏢 **CTR** (Control Zones)
- 🛬 **TMA** (Terminal Maneuvering Areas)
- 📡 **RAS** (Radar Advisory Service)
- ⛔ **R** (Restricted Areas) 
- 🚫 **D** (Danger Areas)
- 🔒 **P** (Prohibited Areas)

Each folder contains the specific airspaces of that type crossed during the flight.

### 🆘 **Support**
For issues or questions:
1. Check the output window in the application for detailed error messages
2. Verify all input files are valid and accessible
3. Ensure Google Earth Pro is installed for automatic KML launching

### 📝 **Version Information**
- Version: 1.0
- Build Date: September 2025
- Python Version: 3.12
- Dependencies: Included in executable

---
*NavPro - Making flight planning safer and easier* ✈️