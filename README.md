# 🛩️ Nav Profile - Flight Path Analysis Suite

A comprehensive suite of tools for analyzing KML flight paths against French airspace data, with both navigation analysis and altitude profile correction capabilities.

## � Project Structure

```
nav-profile/
├── 🛩️ NavPro Core Application
│   ├── navpro.py           # Command-line version
│   ├── navpro_gui.py       # Windows GUI application
│   ├── core/               # Flight analysis engine
│   ├── data_processing/    # AIXM data processing
│   └── visualization/      # KML generation
│
├── ✈️ Altitude Correction Tools
│   └── altitude-correction/
│       ├── kml_altitude_corrector.py  # Main altitude corrector
│       ├── kml_altitude_viewer.py     # Graphical profile viewer
│       ├── aviation_utils.py          # Aviation utilities & APIs
│       └── kml_analyzer.py            # Profile analysis tools
│
├── 📦 Distribution & Build
│   └── distribution/
│       ├── build_scripts/    # Build automation
│       ├── releases/         # Release packages
│       └── dist/, build/     # Build artifacts
│
└── 📚 Documentation
    └── docs/                 # Project documentation
```

## � Quick Start

### NavPro Airspace Analysis
1. **Download**: Get the latest Windows release from `distribution/releases/`
2. **Extract**: Unzip to any folder  
3. **Run**: Double-click `NavPro.exe` or use GUI with `python navpro_gui.py`

### Altitude Profile Correction
```bash
# Correct SDVFR altitude profiles
cd altitude-correction
python kml_altitude_corrector.py input.kml -o corrected.kml

# Visualize altitude profiles  
python kml_altitude_viewer.py corrected.kml
```

### Command Line (Advanced Users)

```bash
# Basic analysis with default corridor (±1000ft, ±10NM)
python navpro.py profile flight.kml

# Custom corridor analysis  
python navpro.py profile flight.kml --corridor-height 500 --corridor-width 5

# Export to JSON
python navpro.py profile flight.kml --output analysis.json

# Show help
python navpro.py help profile
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

## 🛠️ Installation

```bash
# Clone repository
git clone [repo-url]
cd nav-profile

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install shapely sqlite3 xml.etree.ElementTree argparse json
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

## Installation & Setup

### System Requirements
- Python 3.8+
- SQLite 3.x
- Standard library dependencies only

### Installation Steps
1. Clone this repository
2. Navigate to the `production/` directory
3. Extract data: `python aixm_extractor.py` (if database doesn't exist)
4. Start searching: `python search_tool.py KEYWORD`

### First Time Setup
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

## License

This system is designed for aviation data processing and analysis. Use in accordance with AIXM data licensing and aviation regulations.