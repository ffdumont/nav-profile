import sqlite3
import sys
from pathlib import Path

db_path = Path("../data/airspaces.db")
if not db_path.exists():
    print(f"❌ Database file not found: {db_path}")
    sys.exit(1)

print(f"📂 Checking database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"🗂️  Tables found: {tables}")
    
    # Get table info for each table
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   {table}: {count} rows")
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"     Columns: {columns}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")