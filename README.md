# AIXM Airspace Database System

A comprehensive system for extracting, storing, and querying AIXM (Aeronautical Information Exchange Model) airspace data from XML files into a SQLite database.

## Overview

This system processes AIXM 4.5 XML files containing French airspace data (43.7 MB source file) and provides powerful search and query capabilities through both Python API and command-line interface for aviation applications.

**Database Statistics:**
- 5,035 airspaces extracted and indexed
- 4,433 boundaries with 17,721 coordinate vertices
- Complete operational data including altitudes and operating hours
- Support for all French airspace types (RAS, TMA, CTR, R, D, P, etc.)

## Features

- ✅ **Complete AIXM Processing** - Parse AIXM 4.5 XML files and extract all airspace data
- ✅ **SQLite Database Storage** - Structured storage with geometry support
- ✅ **Advanced Keyword Search** - Search by airspace names and codes with flexible options
- ✅ **Rich Data Model** - Altitudes, operating hours, geometry, operational remarks
- ✅ **Multiple Interfaces** - Python API and command-line tool
- ✅ **Multiple Output Formats** - Detailed and summary views
- ✅ **Production Ready** - Comprehensive documentation and validation

## Quick Start

```bash
# Navigate to production directory
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

## Project Structure

```
├── production/               # Main system components
│   ├── aixm_extractor.py          # AIXM XML extraction engine
│   ├── aixm_query_service.py      # Database query service with search capabilities
│   ├── search_tool.py             # Command-line search interface
│   ├── config.py                  # Configuration settings
│   ├── validate_system.py         # System validation and testing
│   ├── check_db.py               # Database integrity checker
│   └── README.md                 # Additional technical documentation
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

✅ **Production Ready** - Complete extraction and search system  
📊 **5,035 Airspaces Indexed** - Full French airspace coverage  
🗓️ **Data Current as of October 2, 2025** - Latest AIXM data  
🔍 **Full Search Capabilities Active** - Keyword and code search  
⚡ **High Performance** - Sub-second query responses  
📚 **Comprehensive Documentation** - Complete usage guide  

## License

This system is designed for aviation data processing and analysis. Use in accordance with AIXM data licensing and aviation regulations.