# Nav-Profile - AIXM Airspace System with 3D Visualization

A comprehensive navigation profile system for extracting, storing, querying, and visualizing AIXM (Aeronautical Information Exchange Model) airspace data with professional 3D KML volume generation.

## Overview

This system processes AIXM 4.5 XML files containing French airspace data (43.7 MB source file) and provides powerful search capabilities plus professional 3D airspace visualization through both Python API and command-line interfaces for aviation applications.

**Database Statistics:**
- 5,035 airspaces extracted and indexed
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