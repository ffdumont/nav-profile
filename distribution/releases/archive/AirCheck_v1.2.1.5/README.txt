AirCheck v1.2.1.5 Release Package
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

NEW IN v1.2.1.5:
- Fixed profile correction import issues for packaged executable
- Added robust import fallback logic for KMLProfileCorrector module  
- Updated PyInstaller spec with hidden imports for profile-correction modules
- Fixed database rebuild import issues (from v1.2.1.4)
- Intelligent database path detection for development vs deployed environments
- All major features now work correctly in packaged executable:
  * Database rebuild from AIXM files
  * Profile correction and viewing
  * Flight analysis and KML generation

Installation:
1. Extract all files to a folder on your system
2. Ensure Google Earth Pro is installed
3. Run Launch_AirCheck.bat or AirCheck.exe directly

Note: The airspaces.db file in sample_data is required for the application to function properly.
All import issues have been resolved - database rebuild and profile correction should work correctly.

Version: 1.2.1.5
Build Date: September 27, 2025