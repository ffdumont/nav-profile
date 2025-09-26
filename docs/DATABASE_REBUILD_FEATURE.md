# Automatic Database Rebuild Feature

## Overview
NavPro now automatically detects when a new AIRAC cycle is selected and offers to rebuild the airspace database to ensure data consistency.

## How It Works

### Automatic Detection
- When you select a different AIXM file using "Browse" button
- The system compares AIRAC effective dates between old and new files
- If dates differ, it prompts for database rebuild

### Database Status Checking
- On startup, checks if database exists and matches current AIRAC
- Shows status in welcome message:
  - ✅ Database ready (matches current AIRAC)
  - ⚠️ Database may be outdated (AIRAC mismatch)
  - ⚠️ Airspace database not found

### Manual Rebuild Option
- New "🔄 Rebuild Database" button in the GUI
- Allows manual database rebuild anytime
- Useful for troubleshooting or forcing rebuild

## Rebuild Process
1. **Detection**: System detects AIRAC change
2. **Confirmation**: User prompted to confirm rebuild
3. **Backup**: Old database removed
4. **Extraction**: New database built from AIXM data
5. **Completion**: Success message and ready for use

## Benefits
- **Data Consistency**: Database always matches selected AIRAC cycle
- **Automatic Updates**: No manual intervention needed for AIRAC changes
- **User Control**: Option to skip rebuild or do manual rebuild
- **Status Visibility**: Clear indication of database status

## Technical Details
- Uses AIXM effective date for AIRAC comparison
- Database rebuild runs in background thread (non-blocking GUI)
- Imports AIXMExtractor for database creation
- Handles errors gracefully with user feedback

## Usage Tips
- Always confirm rebuild when prompted for new AIRAC
- Use manual rebuild if database becomes corrupted
- Rebuild may take several minutes for large AIXM files
- Database file: `data/airspaces.db`