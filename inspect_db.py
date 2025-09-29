#!/usr/bin/env python3
"""
Inspecter la structure de la base de données
"""

import sqlite3

def inspect_database():
    conn = sqlite3.connect('data/airspaces.db')
    cursor = conn.cursor()
    
    # Get table schema
    print("Schema de border_vertices:")
    cursor.execute("PRAGMA table_info(border_vertices)")
    for row in cursor.fetchall():
        print(f"  {row}")
    
    print("\nSchema de airspace_borders:")
    cursor.execute("PRAGMA table_info(airspace_borders)")
    for row in cursor.fetchall():
        print(f"  {row}")
    
    # Sample data from border_vertices
    print("\nÉchantillon de border_vertices:")
    cursor.execute("SELECT * FROM border_vertices LIMIT 5")
    for row in cursor.fetchall():
        print(f"  {row}")
    
    conn.close()

if __name__ == "__main__":
    inspect_database()