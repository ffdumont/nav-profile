# 🛩️ Airspace Checker - Professional Flight Profile & Airspace Analysis Suite

⚠️ **IMPORTANT AVIATION SAFETY DISCLAIMER** ⚠️
> **FOR EDUCATIONAL AND FLIGHT PLANNING PURPOSES ONLY**
> 
> This software is NOT certified for use in actual flight operations. All information must be verified with official aeronautical publications and current NOTAMs before flight. The developers assume no responsibility for navigation decisions made using this software. Always comply with applicable aviation regulations and maintain proper flight planning procedures.

A comprehensive suite of aviation navigation tools for analyzing KML flight paths against French airspace data, with flight profile correction capabilities and professional Windows desktop application.

Suite complète d'outils de navigation aéronautique pour l'analyse de fichiers KML de vol contre les données d'espace aérien français, avec correction de profil de vol et application Windows professionnelle.

## 🚀 Quick Start

### Option 1: Windows Desktop Application (Recommended)
1. **Download**: Get `AirCheck_v1.0.x_Windows.zip` from `distribution/releases/`
2. **Extract**: Unzip to any folder (e.g., `C:\AirCheck\`)
3. **Run**: Double-click `AirCheck.exe` - No Python installation required!
4. **Enhanced**: Use `Launch_AirCheck.bat` for optimal experience

### Option 2: Profile Correction Tools
```bash
# Correct KML profile with realistic altitudes
python profile-correction/kml_profile_corrector.py input.kml -o corrected.kml

# Visualize corrected profile  
python profile-correction/kml_profile_viewer.py corrected.kml

# Batch processing
./scripts/kml_corrector.bat
./scripts/kml_viewer.bat
```

## 🏗️ Project Structure

```
nav-profile/
├── 🛩️ Airspace Checker Core Application
│   ├── navpro/
│   │   ├── navpro.py                   # Command-line interface
│   │   ├── navpro_gui.py               # Windows GUI application
│   │   ├── core/                       # Flight analysis engine
│   │   ├── data_processing/            # AIXM data processing
│   │   ├── utils/                      # General utilities
│   │   └── visualization/              # KML generation
│
├── ✈️ Profile Correction Tools
│   ├── profile-correction/
│   │   ├── kml_profile_corrector.py    # Universal profile corrector
│   │   ├── kml_profile_viewer.py       # Flight profile visualizer
│   │   └── aviation_utils.py           # Aviation utilities & APIs
│
├── 📋 Launch Scripts
│   ├── scripts/
│   │   ├── airchk.bat / airchk.ps1     # Airspace Checker launchers
│   │   ├── kml_corrector.bat           # KML corrector launcher
│   │   └── kml_viewer.bat              # KML viewer launcher
│
├── 📦 Distribution & Releases
│   ├── distribution/
│   │   ├── build_scripts/              # Build automation
│   │   ├── releases/                   # Windows release packages
│   │   │   ├── current/                # Latest release
│   │   │   │   ├── AirCheck.exe          # Standalone Windows app
│   │   │   │   └── Launch_AirCheck.bat   # Enhanced launcher
│   │   │   └── AirCheck_v1.0.x_Windows.zip
│   │   └── build/, dist/               # Build artifacts
│
├── 📁 Data & Documentation
│   ├── data/                           # Test data and databases
│   │   ├── *.kml                       # Sample flight profiles
│   │   ├── airspaces.db                # Processed airspace database
│   │   └── AIXM*.xml                   # Raw AIXM airspace data
│   └── docs/                           # Project documentation
```

## 🎯 Key Features

### 🛩️ Airspace Checker Analysis
- **Professional Windows GUI**: Clean, intuitive desktop application
- **Critical Airspace Detection**: Automatic highlighting of Class A, Prohibited (P), and Restricted (R) zones  
- **Google Earth Integration**: Auto-launch with organized KML folders by airspace type
- **Flight Path Support**: Both navigation routes and GPS traces (thousands of points)
- **Customizable Corridors**: Configurable vertical (±feet) and horizontal (±nautical miles) search
- **Real-time Analysis**: Live processing with progress indicators and status updates
- **Safety Warnings**: Clear identification of dangerous airspaces with actionable guidance

### ✈️ Profile Correction System
- **Universal Algorithm**: Works with any standard KML navigation file
- **Realistic Flight Profiles**: Applies aviation-standard climb/descent rates (500 ft/min)
- **Smart Final Approach**: Calculates optimal descent points for proper arrival altitude
- **Automatic Elevation**: Uses Open Elevation API for ground elevations at departure/arrival
- **Branch Analysis**: Clear table showing climb/descent requirements for each flight segment
- **Aviation-Standard Naming**: Descriptive waypoint names (e.g., `Climb_OXWW_3100`, `Descent_3100_LFFU`)
- **Interactive Visualization**: Matplotlib charts showing altitude vs distance profiles

## 📋 Usage Examples

### Airspace Checker GUI Workflow
1. **Launch**: Double-click `AirCheck.exe`
2. **Load Files**: 
   - Browse for AIXM XML airspace database
   - Select KML flight profile (route or trace)
   - Choose output directory
3. **Configure**: Set corridor height (±ft) and width (±NM)
4. **Analyze**: Click "List Airspace Crossings" for text analysis
5. **Visualize**: Click "Generate KML & Open in Google Earth"

### Profile Correction Workflow
```bash
# Step 1: Correct the flight profile
python profile-correction/kml_profile_corrector.py flight.kml -o corrected.kml \
  --climb-rate 500 --descent-rate 500 --ground-speed 120

# Step 2: Review the corrected profile
python profile-correction/kml_profile_viewer.py corrected.kml
```

## 📊 Profile Correction Example

**Branch Analysis Output:**
```
================================================================================
BRANCH ANALYSIS TABLE
================================================================================
Branch               Distance   Action
--------------------------------------------------------------------------------
Branch 1             3.5 NM     LFXU → MOR1V: CLIMB from 1079 ft to 1400 ft (+321 ft)
Branch 2             6.5 NM     MOR1V → PXSW: LEVEL at 1400 ft
Branch 3             7.8 NM     PXSW → HOLAN: CLIMB from 1400 ft to 1800 ft (+400 ft)
Branch 8             44.8 NM    BEVRO → LFFU: DESCENT from 3100 ft to 1548 ft (-1552 ft)
================================================================================
```

**Generated Points with Aviation-Standard Naming:**
```
Generated 14 corrected points:
  LFXU - LES MUREAUX: 1079 ft
  Climb_LFXU - LES MUREAUX_1400: 1400 ft    # Climb from LFXU to 1400 ft
  MOR1V: 1400 ft
  PXSW: 1400 ft
  Climb_PXSW_1800: 1800 ft                  # Climb from PXSW to 1800 ft
  HOLAN: 1800 ft
  ARNOU: 1800 ft
  Climb_ARNOU_2300: 2300 ft                 # Climb from ARNOU to 2300 ft
  OXWW: 2300 ft
  Climb_OXWW_3100: 3100 ft                  # Climb from OXWW to 3100 ft
  LFFF/OE: 3100 ft
  BEVRO: 3100 ft
  Descent_3100_LFFU - CHATEAUNEUF SUR CHER: 3100 ft  # Descent start point
  LFFU - CHATEAUNEAUX SUR CHER: 1548 ft              # Final destination
```

## ⚠️ Critical Airspace Detection

Airspace Checker automatically identifies and warns about dangerous airspaces:

**GUI Analysis Report Example:**
```
🛩️ FLIGHT PROFILE ANALYSIS REPORT
Flight: LFXU-LFFU.kml | Distance: 240.9 km | Altitude: 1400-3100 ft
Corridor: ±1000 ft, ±10.0 NM

⚠️  CRITICAL AIRSPACE WARNINGS ⚠️
3 CRITICAL AIRSPACE CROSSINGS DETECTED:

RESTRICTED AREAS (R) - Flight restrictions apply:
- LFR35A (R35A) at 33.2 km - Ground to 1500 ft
- LFR149B (R149B) at 128.7 km - Ground to 2000 ft

CLASS A AIRSPACE - IFR clearance required:
- PARIS TMA (CLAS A) at 89.1 km - 3500 ft to FL195

🔴 Review flight plan carefully - Critical airspace crossings detected
```

## 🛠️ Technical Details

### Algorithm Logic (Profile Corrector)
- **Branch Definition**: Flight segment between two consecutive waypoints
- **Target Altitude**: Uses altitude of first point in each branch (entry altitude)
- **Departure/Arrival**: Field elevation + 1000 ft (standard aviation practice)
- **Climb/Descent Rates**: Configurable (default: 500 fpm)
- **Final Approach Optimization**: Calculates descent point to arrive at exact destination altitude
- **Smart Descent Timing**: Aircraft descends "at the right time" rather than from segment start

### Naming Convention
- **Regular segments**: `<Action>_<waypoint_where_action_starts>_<target_altitude>`
  - Example: `Climb_PXSW_1800` = climb starting from PXSW waypoint to reach 1800 ft
- **Final approach**: `Descent_<starting_altitude>_<destination_waypoint>`
  - Example: `Descent_3100_LFFU` = descent from 3100 ft to destination

### Supported File Formats
- **Input**: KML navigation files (routes and GPS traces), AIXM XML airspace data
- **Output**: Corrected KML with realistic altitude profiles, organized Google Earth folders

## 📈 System Requirements & Performance

### Windows Desktop App
- **OS**: Windows 10/11 (64-bit)
- **Space**: 50MB free disk space
- **Memory**: 2GB RAM recommended
- **Optional**: Google Earth Pro for KML visualization

### Performance Metrics
- **Processing Speed**: ~240km flight analyzed in <5 seconds  
- **Memory Usage**: <100MB for full French airspace dataset
- **Database**: 5,035 French airspaces from AIXM 4.5
- **Accuracy**: Sub-meter geometric precision for corridor analysis

## 🏆 Recent Improvements

### v1.0+ Features
- ✅ **Complete Windows GUI**: Professional desktop application with file dialogs
- ✅ **Universal Profile Corrector**: Works with any standard navigation KML
- ✅ **Smart Final Approach**: Realistic descent profiles with proper timing
- ✅ **Aviation-Standard Naming**: Clear, descriptive waypoint names
- ✅ **Auto-Launch Google Earth**: Seamless visualization workflow
- ✅ **Critical Airspace Warnings**: Enhanced safety features with detailed explanations

### Profile Correction Enhancements
- ✅ **Removed Hardcoded Logic**: Universal algorithm replaces specific workarounds
- ✅ **Optimal Descent Points**: Calculates "descent at the right time" for final approach
- ✅ **Proper Point Sequencing**: Chronological order in Google Earth folders
- ✅ **Interactive Visualization**: Matplotlib charts with altitude profiles
- ✅ **Corrected Naming Logic**: Action points named after where the action starts

## 🛠️ Installation & Development

### For End Users
1. **Download**: Get the latest Windows release from `distribution/releases/`
2. **Extract**: Unzip and run `AirCheck.exe` - No Python installation required

### For Developers
```bash
# Clone repository
git clone https://github.com/ffdumont/nav-profile.git
cd nav-profile

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Test installation
airchk help
python profile-correction/kml_profile_corrector.py --help
```

## 📞 Support & Troubleshooting

### Common Issues
- **KML Format**: Standard navigation KML files work best
- **AIXM Data**: Requires valid AIXM 4.5 XML airspace database
- **Encoding**: UTF-8 recommended for international characters
- **Large Files**: GPS traces with thousands of points are fully supported
- **Memory**: 2GB RAM recommended for complex airspace analysis

### File Issues
- **Profile Corrector**: Works with any SDVFR/navigation KML file
- **Google Earth**: Uses default application if Google Earth Pro not installed
- **Progress Indicators**: Real-time status shows analysis progress

---

**NavPro** - Professional aviation navigation analysis for safe flight planning 🛩️

*Suite complète pour l'analyse professionnelle de navigation aéronautique et la planification sécurisée des vols*

## � Project Structure

```
nav-profile/
├── 🛩️ NavPro Core Application
│   ├── navpro.py                   # Command-line interface
│   ├── navpro_gui.py               # Windows GUI application
│   ├── core/                       # Flight analysis engine
│   ├── data_processing/            # AIXM data processing
│   ├── utils/                      # General utilities
│   └── visualization/              # KML generation
│
├── ✈️ Profile Correction Tools
│   └── profile-correction/
│       ├── kml_profile_corrector.py   # Universal profile corrector
│       ├── kml_profile_viewer.py      # Flight profile visualizer
│       └── aviation_utils.py          # Aviation utilities & APIs
│
├── 📋 Launch Scripts
│   └── scripts/
│       ├── navpro.bat / navpro.ps1    # NavPro launchers
│       ├── kml_corrector.bat          # KML corrector launcher
│       └── kml_viewer.bat             # KML viewer launcher
│
├── 📦 Distribution & Build
│   └── distribution/
│       ├── build_scripts/             # Build automation
│       ├── releases/                  # Release packages
│       └── build/, dist/              # Build artifacts
│
├── � Data & Documentation
│   ├── data/                          # Test data and databases
│   └── docs/                          # Project documentation
```

## � Quick Start

### NavPro Airspace Analysis
1. **Download**: Get the latest Windows release from `distribution/releases/`
2. **Extract**: Unzip to any folder  
3. **Run**: Double-click `AirCheck.exe` or use GUI with `python navpro_gui.py`

### Altitude Profile Correction
```bash
# Correct SDVFR flight profiles  
cd profile-correction
python kml_profile_corrector.py input.kml -o corrected.kml

# Visualize flight profiles
python kml_profile_viewer.py corrected.kml -o profile.png
```

## 📋 Fonctionnalités / Features

### NavPro - Airspace Analysis
- ✅ **KML flight path analysis** - Analyze navigation files against French airspace data
- ✅ **Airspace intersection detection** - Detect crossings with controlled airspace
- ✅ **3D corridor analysis** - Configurable altitude and lateral corridors
- ✅ **Compliance reporting** - Generate detailed compliance reports
- ✅ **Windows GUI application** - User-friendly graphical interface
- ✅ **Multiple output formats** - JSON, KML, detailed reports

### Profile Correction - Altitude Profiles  
- ✅ **Universal KML correction** - Works on any SDVFR KML file
- ✅ **Realistic flight profiles** - Branch-based climb/descent logic
- ✅ **Automatic terrain elevation** - API-based ground elevation retrieval
- ✅ **Departure/arrival convention** - Field elevation + 1000 ft standard
- ✅ **Configurable rates** - Customizable climb/descent rates (default 500 ft/min)
- ✅ **Profile visualization** - Generate flight profile charts with proper aviation units
- ✅ **Unreachable altitude detection** - Warn about impossible altitude targets

### Command Line (Advanced Users)

```bash
# Basic analysis with default corridor (±1000ft, ±10NM)
airchk profile flight.kml

# Custom corridor analysis  
airchk profile flight.kml --corridor-height 500 --corridor-width 5

# Export to JSON
airchk profile flight.kml --output analysis.json

# Show help
airchk help profile
```

## 📊 Example Output

### GUI Analysis Report
```
🛩️ FLIGHT PROFILE ANALYSIS REPORT
Flight: LFXU-LFFU.kml | Distance: 240.9 km | Altitude: 1400-3100 ft
Corridor: ±1000 ft, ±10.0 NM

SUMMARY: 53 airspaces found

⚠️  CRITICAL AIRSPACE WARNINGS ⚠️
3 CRITICAL AIRSPACE CROSSINGS DETECTED:

RESTRICTED AREAS (R) - Flight restrictions apply:
- LFR35A (R35A) at 33.2 km - Ground to 1500 ft
- LFR149B (R149B) at 128.7 km - Ground to 2000 ft

CLASS A AIRSPACE - IFR clearance required:
- PARIS TMA (CLAS A) at 89.1 km - 3500 ft to FL195

🔴 Review flight plan carefully - Critical airspace crossings detected

TMAS (11): ORLEANS 1.1, AVORD 1.1, PARIS 2, PARIS 3...
RAS (14): SEINE 1-6, PARIS SUD, PARIS NORD...  
RESTRICTED (2): LFR149B, LFR35A...
```

## 🏗️ Architecture

### Core Components

- **`fixed_airspace_query.py`**: 3-stage spatial query engine with STRtree indexing
- **`flight_profile.py`**: Flight path analysis with corridor generation  
- **`navpro.py`**: Professional CLI interface with subcommands
- **`production/aixm_query_service.py`**: AIXM XML data extraction and database management

### 3-Stage Query Process

1. **Stage 1**: STRtree bounding box filter (fast elimination)
2. **Stage 2**: Precise Shapely geometry intersection  
3. **Stage 3**: 3D altitude range validation with FL conversion

## 📁 Project Structure

```
nav-profile/
├── navpro.py                    # Main CLI tool
├── fixed_airspace_query.py      # Core 3D spatial query engine  
├── flight_profile.py            # Flight analysis with corridors
├── production/                  # Production modules
│   ├── aixm_query_service.py   # AIXM data processing
│   ├── kml_volume_service.py   # KML parsing utilities
│   └── config.py               # Configuration settings
├── data/
│   ├── airspaces.db            # SQLite airspace database
│   └── *.kml                   # Flight path files
└── README.md
```

## 🛠️ Installation / Installation

### Prerequisites / Prérequis
- Python 3.8+ 
- pip (Python package manager)

### For End Users / Pour les Utilisateurs Finaux
1. **Download pre-built release** - Get the latest Windows release from `distribution/releases/`
2. **Extract and run** - Unzip and double-click `NavPro.exe`

### For Developers / Pour les Développeurs

```bash
# Clone repository / Cloner le repository  
git clone https://github.com/ffdumont/nav-profile.git
cd nav-profile

# Create virtual environment / Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies / Installer les dépendances
pip install -r requirements.txt

# Test installation / Tester l'installation
python navpro.py help
python profile-correction/kml_profile_corrector.py --help
```

## 📖 Usage Guide

### Basic Commands

```bash
# Help system
python navpro.py help
python navpro.py help profile

# Analyze flight with defaults
python navpro.py profile data/flight.kml

# Custom corridor settings
python navpro.py profile flight.kml --corridor-height 1500 --corridor-width 15

# JSON output for integration
python navpro.py profile flight.kml --output results.json
```

### Corridor Parameters

- **`--corridor-height`**: Vertical tolerance in feet (default: ±1000 ft)
- **`--corridor-width`**: Horizontal tolerance in nautical miles (default: ±10 NM)
- **`--output`**: JSON file path for structured results

### Understanding Results

**Airspace Categories:**
- **TMAs**: Terminal Control Areas (Class A-E airspace around airports)
- **RAS**: Regulated Airspace Sectors (major traffic control zones)
- **Restricted**: Military/special use restrictions (LFR zones)
- **Control Zones**: Airport control zones
- **Other**: FIRs, sectors, and miscellaneous controlled airspace

**Key Metrics:**
- **Total Crossings**: Number of flight segment intersections with airspaces
- **Altitude Compliance**: Flight altitude vs airspace vertical limits
- **Geometric Precision**: Sub-meter accuracy using Shapely geometry

## 🔧 Technical Details

### Spatial Indexing Performance
- **Database Size**: 1,764 French airspaces from AIXM 4.5
- **Query Performance**: O(log n) with STRtree vs O(n) linear search
- **Memory Efficiency**: Lazy geometry loading and caching

### Coordinate Systems
- **Input**: WGS84 coordinates from KML files
- **Processing**: Geographic coordinates (lat/lon) with great circle distances
- **Corridors**: Nautical mile buffers around geodesic flight paths

### Flight Level Handling
```python
# Automatic conversion
FL65 → 6500 feet  # Flight Level 65
2100 FT → 2100 feet  # Direct feet values
```

## 🧪 Testing

Test with the provided sample flight:

```bash
# Full analysis
python navpro.py profile data/20250924_083633_LFXU-LFFU.kml

# Should detect: ORLEANS TMA, AVORD TMA, SEINE RAS, PARIS SUD
```

## 📈 Performance

- **Processing Speed**: ~240km flight analyzed in <5 seconds  
- **Memory Usage**: <100MB for full French airspace dataset
- **Accuracy**: Sub-meter geometric precision for corridor analysis

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)  
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- French AIXM airspace data from official aviation authorities
- Shapely library for high-performance spatial operations
- SQLite for efficient airspace data storage
- 4,433 boundaries with 17,721 coordinate vertices
- Complete operational data including altitudes and operating hours
- Support for all French airspace types (RAS, TMA, CTR, R, D, P, etc.)

## Features

- ✅ **Complete AIXM Processing** - Parse AIXM 4.5 XML files and extract all airspace data
- ✅ **SQLite Database Storage** - Structured storage with geometry support
- ✅ **Advanced Keyword Search** - Search by airspace names and codes with flexible options
- ✅ **3D KML Volume Generation** - Create Google Earth-compatible 3D airspace volumes
- ✅ **Rich Data Model** - Altitudes, operating hours, geometry, operational remarks
- ✅ **Multiple Interfaces** - Python API, command-line search, and NavPro tool
- ✅ **Multiple Output Formats** - Detailed and summary views, plus KML export
- ✅ **Production Ready** - Comprehensive documentation and validation

## Quick Start

```bash
# Navigate to production directory for search functionality
cd production

# Search for airspaces
python search_tool.py CHEVREUSE

# Get specific airspace details  
python search_tool.py --code LFPNFS2

# Summary view of airspace types
python search_tool.py --summary TMA

# Python API usage
python -c "from aixm_query_service import AirspaceQueryService; s = AirspaceQueryService(); print([r['name'] for r in s.search_by_keyword('CHEVREUSE')])"
```

```bash  
# NavPro - KML volume generation from root directory
cd ..

# List CHEVREUSE airspaces
python navpro.py --list "CHEVREUSE"

# Generate 3D KML volume for airspace ID
python navpro.py --id 4749

# Generate combined KML for multiple airspaces
python navpro.py --name "CHEVREUSE"

# PowerShell wrapper (Windows)
.\navpro.ps1 4749
```

## Project Structure

```
├── production/               # Main system components
│   ├── aixm_extractor.py          # AIXM XML extraction engine
│   ├── aixm_query_service.py      # Database query service with search capabilities
│   ├── kml_volume_service.py      # 3D KML volume generation service
│   ├── search_tool.py             # Command-line search interface
│   ├── config.py                  # Configuration settings
│   ├── validate_system.py         # System validation and testing
│   ├── check_db.py               # Database integrity checker
│   └── README.md                 # Additional technical documentation
├── navpro.py                # NavPro command-line tool (KML generation)
├── navpro.ps1               # PowerShell wrapper for NavPro (Windows)
├── data/                    # Data storage
│   ├── airspaces.db              # SQLite database (extracted data)
│   └── AIXM4.5_all_FR_OM_2025-10-02.xml  # Source AIXM XML file
├── .gitignore              # Git ignore patterns
└── README.md               # This comprehensive documentation
```

## First Time Setup
If the database doesn't exist, run the extractor:
```bash
cd production
python aixm_extractor.py
```
This processes the 43.7 MB XML file and creates the SQLite database with all airspace information.

## Database Schema

The system creates a SQLite database with the following main table:

### `airspaces` Table
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `code_id` | TEXT | Official airspace identifier (e.g., LFPNFS2) |
| `code_type` | TEXT | Airspace type (RAS, TMA, CTR, R, D, P, etc.) |
| `mid` | TEXT | AIXM message identifier |
| `name` | TEXT | Airspace name |
| `airspace_class` | TEXT | Airspace class |
| `activity_type` | TEXT | Activity type |
| `min_altitude` | INTEGER | Minimum altitude |
| `max_altitude` | INTEGER | Maximum altitude |
| `min_altitude_unit` | TEXT | Minimum altitude unit (FT, FL, etc.) |
| `max_altitude_unit` | TEXT | Maximum altitude unit |
| `local_type` | TEXT | Detailed type description |
| `operating_hours` | TEXT | Operating schedule |
| `operating_remarks` | TEXT | Additional operational information |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last modification time |

### Additional Tables
- `borders` - Airspace boundary information
- `vertices` - Geographic coordinate points for boundaries

## Search Capabilities

### Python API

#### Basic Usage
```python
from aixm_query_service import AirspaceQueryService

service = AirspaceQueryService()

# Search for airspaces containing keyword
results = service.search_by_keyword('CHEVREUSE')
print(f"Found {len(results)} airspaces")

for airspace in results:
    print(f"{airspace['code_id']}: {airspace['name']}")
    print(f"  Altitude: {airspace['altitude_display']}")
    print(f"  Type: {airspace['code_type']}")
```

#### API Methods

**`search_by_keyword(keyword, case_sensitive=False, limit=None)`**
Search airspaces by keyword in both names and codes.

**Parameters:**
- `keyword` (str): Search term
- `case_sensitive` (bool): Whether search is case-sensitive (default: False)
- `limit` (int): Maximum results to return (default: None for all)

**Returns:** List of dictionaries with complete airspace information

**`get_airspace_details(code_id)`**
Get complete details for a specific airspace by its code.

**`get_statistics()`**
Return database statistics and health information.

#### Advanced Search Options
```python
# Case-sensitive search
results = service.search_by_keyword('Paris', case_sensitive=True)

# Limit results
results = service.search_by_keyword('LFR', limit=10)

# Get specific airspace details
details = service.get_airspace_details('LFPNFS2')
if details:
    print(f"Operating hours: {details['operating_hours']}")
```

### Command-Line Interface

#### Basic Usage
```bash
python search_tool.py [OPTIONS] KEYWORD
```

#### Options
- `--code CODE` - Get details for specific airspace code
- `-s, --summary` - Show compact summary instead of detailed view
- `-l N, --limit N` - Limit results to N entries
- `-c, --case-sensitive` - Enable case-sensitive search

#### Examples
```bash
# Find all CHEVREUSE airspaces
python search_tool.py CHEVREUSE

# Summary of TMA areas
python search_tool.py --summary TMA

# First 5 LFR restricted areas
python search_tool.py -l 5 LFR

# Detailed info for specific airspace
python search_tool.py --code LFPNFS2

# Case-sensitive search
python search_tool.py -c Paris
```

## NavPro - Command Line Tool

**NavPro** is the comprehensive command-line interface for the nav-profile application, providing professional navigation services with a consistent subcommand structure.

### 🛩️ Features

- **Professional CLI**: Consistent subcommand structure (`navpro list`, `navpro generate`, `navpro stats`)
- **Airspace Search**: Find airspaces by name, ID, type, or list all with flexible filters
- **3D KML Generation**: Create Google Earth-compatible 3D airspace volumes with altitude extrusion
- **Batch Operations**: Process multiple airspaces individually or as combined files  
- **Database Statistics**: Comprehensive analysis of airspace coverage and geometry
- **Cross-Platform**: Python script with PowerShell wrapper for Windows users

### 🚀 Usage

#### Command Structure

NavPro uses a modern subcommand structure for consistency:

```bash
# List airspaces
python navpro.py list --name "CHEVREUSE"
python navpro.py list --type RAS --limit 10 --summary
python navpro.py list --id 4749 --verbose

# Generate KML volumes
python navpro.py generate --id 4749
python navpro.py generate --name "CHEVREUSE" --directory kml_output
python navpro.py generate --ids 4749 4750 4751 --output combined.kml

# Database statistics
python navpro.py stats
python navpro.py stats --detailed

# Help system
python navpro.py --help
python navpro.py help generate
```

#### PowerShell Wrapper (Windows)

```powershell
# List airspaces
.\navpro.ps1 list -Name "CHEVREUSE"
.\navpro.ps1 list -Type RAS -Limit 10 -Summary

# Generate KML volumes  
.\navpro.ps1 generate -Id 4749
.\navpro.ps1 generate -Name "CHEVREUSE" -Directory kml_output
.\navpro.ps1 generate -Ids 4749,4750,4751 -Output combined.kml

# Database statistics
.\navpro.ps1 stats -Detailed

# Help
.\navpro.ps1 -Help
.\navpro.ps1 help generate
```

### 📊 Examples

#### Listing Airspaces
```bash
# Find CHEVREUSE airspaces
$ python navpro.py list --name "CHEVREUSE"
🛩️ Initializing NavPro services...
✅ NavPro services initialized successfully
🔍 Searching airspaces...
✅ Found 4 airspace(s) matching pattern 'CHEVREUSE'

🏷️  CHEVREUSE 1 (ID: 4749)
   Type: RAS | Class: UNKNOWN
   Altitude: 0 FT to 2000 FT

# Summary format for quick overview
$ python navpro.py list --type RAS --limit 5 --summary
  2361 |    RAS | LFSTMZ003                [No geometry]
  2374 |    RAS | LFSRMZDN                 [No geometry] 
  2829 |    RAS | LFR175BZ2                [Geometry: 1 components]
```

#### Generating KML Volumes
```bash
# Single airspace
$ python navpro.py generate --id 4749
🛩️ Preparing KML generation...
� Generating KML for airspace ID 4749
   ✅ CHEVREUSE 1: CHEVREUSE_1_4749.kml (1410 bytes)

# Multiple airspaces with combined output  
$ python navpro.py generate --ids 4749 4750 4751
🎯 Generating KML for 3 airspace IDs
🔗 Generating combined KML file...
   ✅ Combined: combined_3_airspaces.kml (3988 bytes, 3 volumes)
```

#### Database Statistics
```bash
$ python navpro.py stats
� NavPro Database Statistics
==================================================
Total airspaces: 5035

Airspace Types:
     D-OTHER: 2228 airspaces
           R:  610 airspaces
         TMA:  510 airspaces
         RAS:  398 airspaces

🌍 KML Generation Capability:
  Ready for KML: 3549 airspaces
  3D volumes available for professional visualization
```

### 🌍 3D KML Output

NavPro generates KML files with proper 3D volume visualization:

- **Altitude Extrusion**: True 3D volumes from surface to ceiling altitude
- **AMSL Altitudes**: Proper Above Mean Sea Level altitude handling
- **Visual Styling**: Semi-transparent polygons with colored outlines
- **Metadata**: Detailed airspace information in descriptions

**Compatible with:**
- Google Earth (full 3D visualization)
- Google Maps (My Maps)
- Aviation flight planning software
- GIS applications

#### Example: CHEVREUSE 1
- **Volume**: Surface to 2000 ft AMSL (609.6 meters)
- **Type**: Restricted Area (RAS)
- **Geometry**: Polygon boundary with precise coordinates
- **Output**: 3D extruded volume for clear airspace visualization

### 📝 NavPro Command Reference

| Command | Description | Key Options |
|---------|-------------|-------------|
| `list` | Search and display airspaces | `--name`, `--id`, `--type`, `--all`, `--summary`, `--limit` |
| `generate` | Create 3D KML volumes | `--id`, `--ids`, `--name`, `--type`, `--output`, `--directory` |
| `stats` | Show database statistics | `--detailed` |
| `help` | Show detailed help | `<command>` for specific command help |

#### Global Options
- `--verbose, -v`: Show detailed output with progress information
- `--quiet, -q`: Minimal output mode for scripting
- `--help, -h`: Show help information

#### Advanced Generate Options  
- `--individual`: Generate separate files even for multiple airspaces
- `--combined-only`: Generate only combined file for multiple airspaces
- `--output, -o`: Custom output filename  
- `--directory, -d`: Custom output directory

### 🚀 Future NavPro Enhancements

NavPro is designed to expand with additional navigation services:

- **Route Planning**: Generate flight paths avoiding restricted areas
- **Obstacle Analysis**: Height clearance calculations  
- **Weather Integration**: METAR/TAF data overlay
- **NOTAM Services**: Temporary restriction updates
- **Chart Generation**: Custom navigation charts
- **Multi-format Export**: GPX, GeoJSON, Shapefile support

## Airspace Types

The database contains various types of French airspaces:

| Type | Description | Count (approx.) |
|------|-------------|-----------------|
| `RAS` | Radio Advisory Sector / Flight Information Sector | 398 |
| `TMA` | Terminal Control Area | 510 |
| `CTR` | Control Zone | 132 |
| `R` | Restricted Area | 610 |
| `D` | Danger Area | 124 |
| `P` | Prohibited Area | 114 |
| `CTA` | Control Area | 95 |
| `D-OTHER` | Other Danger Areas | 2228 |
| Others | Various specialized airspace types | ~1000 |

## Example Use Cases

### 1. Aviation Planning
```python
# Find all restricted areas in a region
service = AirspaceQueryService()
restricted = service.search_by_keyword('LFR', limit=50)

for area in restricted:
    if area['code_type'] == 'R':
        print(f"{area['code_id']}: {area['altitude_display']}")
```

### 2. Operational Information
```python
# Get operating hours for flight information sectors
chevreuse_sectors = service.search_by_keyword('CHEVREUSE')
for sector in chevreuse_sectors:
    print(f"{sector['name']}: {sector['operating_hours']}")
```

### 3. Airspace Analysis
```bash
# Quick overview of airspace types
python search_tool.py --summary TMA
python search_tool.py --summary CTR
python search_tool.py --summary R
```

### 4. Specific Airspace Lookup
```bash
# Find CHEVREUSE flight information sectors
python search_tool.py CHEVREUSE

# Get detailed operational information
python search_tool.py --code LFPNFS2
```

## System Validation

### Check Database Integrity
```bash
python check_db.py
```
Validates database structure and content integrity.

### Validate Complete System
```bash
python validate_system.py
```
Comprehensive system validation including extraction and query capabilities.

### Get Database Statistics
```python
from aixm_query_service import AirspaceQueryService

service = AirspaceQueryService()
stats = service.get_statistics()
print(f"Total airspaces: {stats['total_airspaces']}")
print(f"Geometry coverage: {stats['geometry_coverage']:.1f}%")
```

## Configuration

Edit `config.py` to customize:
- Database paths
- XML file locations  
- Extraction parameters
- Logging levels

## Data Quality & Performance

### Data Statistics
The system has successfully processed:
- **Source File:** AIXM4.5_all_FR_OM_2025-10-02.xml (43.7 MB)
- **Total Airspaces:** 5,035 airspaces extracted
- **Geometry Data:** 4,433 borders with 17,721 vertices
- **Complete Information:** Names, types, altitudes, operating hours for all applicable airspaces

### Performance
- **Processing Time:** ~30 seconds for full extraction
- **Memory Usage:** Efficient streaming XML processing
- **Database Size:** ~15 MB for 5,035 airspaces + geometry
- **Query Performance:** Indexed searches, sub-second responses

### Technical Notes
- SQLite database optimized for read operations
- Indexed searches on `code_id` and `name` fields
- Efficient geometry storage for boundary data
- Comprehensive validation of XML input
- Graceful handling of missing data fields

## Troubleshooting

### Common Issues

**Database not found:**
```bash
# Check if database exists
ls data/airspaces.db

# Re-extract if missing
cd production
python aixm_extractor.py
```

**Search returns no results:**
```python
# Check exact airspace code
service = AirspaceQueryService()
results = service.search_by_keyword('EXACT_CODE')
```

**Import errors:**
```bash
# Ensure you're in the correct directory
cd production
python search_tool.py CHEVREUSE
```

## API Reference

### Return Data Structure

Each airspace record contains:
```python
{
    'id': int,
    'code_id': str,           # Official identifier
    'name': str,              # Airspace name  
    'code_type': str,         # Type (RAS, TMA, etc.)
    'local_type': str,        # Detailed description
    'altitude_display': str,  # Formatted altitude range
    'min_altitude': int,      # Numeric minimum altitude
    'max_altitude': int,      # Numeric maximum altitude
    'min_altitude_unit': str, # Altitude unit (FT, FL, etc.)
    'max_altitude_unit': str,
    'operating_hours': str,   # Operating schedule
    'operating_remarks': str, # Additional info
    'airspace_class': str,    # Airspace class
    'activity_type': str,     # Activity type
    'border_count': int,      # Number of boundary segments
    'vertex_count': int,      # Number of coordinate points
    'created_at': str,        # Creation timestamp
    'updated_at': str         # Modification timestamp
}
```

## System Status

✅ **Production Ready** - Complete extraction, search, and KML generation system  
📊 **5,035 Airspaces Indexed** - Full French airspace coverage  
🌍 **3D KML Volumes** - Google Earth-compatible airspace visualization  
🗓️ **Data Current as of October 2, 2025** - Latest AIXM data  
🔍 **Full Search Capabilities Active** - Keyword and code search  
🛩️ **NavPro Command-Line Tool** - Professional airspace services  
⚡ **High Performance** - Sub-second query responses  
📚 **Comprehensive Documentation** - Complete usage guide  

## 📖 Documentation / Documentation

### Profile Correction
- `profile-correction/README_PROFILE_CORRECTOR.md` - Profile correction documentation
- `profile-correction/aviation_utils.py` - Aviation utilities API reference

### NavPro Core
- `docs/` - Complete project documentation
- `distribution/README_DIST.md` - Distribution and build guide
- `docs/GITHUB_RELEASE_GUIDE.md` - Release management guide

### Scripts and Tools
- Launch scripts in `scripts/` directory for easy access
- Batch files for Windows users
- PowerShell scripts with enhanced functionality

## 🤝 Contributing / Contribution

1. Fork the repository / Fork le repository
2. Create feature branch / Créer une branche feature (`git checkout -b feature/amazing-feature`)
3. Commit changes / Valider les changements (`git commit -m 'Add amazing feature'`)
4. Push branch / Pousser la branche (`git push origin feature/amazing-feature`)  
5. Open Pull Request / Ouvrir une Pull Request

## 📄 License

This project is designed for aviation data processing and analysis in France. Use in accordance with AIXM data licensing and aviation regulations.

Projet conçu pour le traitement et l'analyse de données d'aviation en France. Utilisation conforme aux licences de données AIXM et aux réglementations aéronautiques.