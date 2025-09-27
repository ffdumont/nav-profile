AirCheck v1.2.1.4 Release Package
=====================================

This release contains:

Files:
- AirCheck.exe (main executable)
- Launch_AirCheck.bat (launcher script)

Sample Data (in sample_data folder):
- airspaces.db (airspace database - REQUIRED for operation)
- 20250926_165229_LFXU-LFFY.kml (LFXU to LFFY flight profile)
- AIXM4.5_all_FR_OM_2025-10-02.xml (AIXM airspace data for France)
- Place_KML_files_here.txt (placeholder for additional KML files)

NEW IN v1.2.1.4:
- Fixed database rebuild import issues for packaged executable
- Improved AIXM extractor import fallback logic
- Added debug messages for import troubleshooting
- Resolved sys variable scope issues
- PATCH: Fixed database path handling for deployed environments
- Database rebuild feature now works correctly in both development and packaged environments
- Intelligent database path detection (data/ vs sample_data/)

Installation:
1. Extract all files to a folder on your system
2. Ensure Google Earth Pro is installed
3. Run Launch_AirCheck.bat or AirCheck.exe directly

Note: The airspaces.db file in sample_data is required for the application to function properly.
The database rebuild feature should now work correctly when importing new AIXM files.

Version: 1.2.1.4
Build Date: September 27, 2025