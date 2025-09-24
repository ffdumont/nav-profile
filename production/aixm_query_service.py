#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service de requête pour les espaces aériens AIXM
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional

class AirspaceQueryService:
    """Service pour interroger les espaces aériens extraits"""
    
    def __init__(self, db_path: str = None):
        """Initialise le service avec la base de données"""
        if db_path is None:
            current_dir = Path(__file__).parent
            db_path = current_dir.parent / "data" / "airspaces.db"
        
        self.db_path = str(db_path)
        self._validate_database()

    def _validate_database(self):
        """Valide que la base de données existe"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if 'airspaces' not in tables:
                raise Exception("Table 'airspaces' manquante")
                
        except Exception as e:
            raise Exception(f"Erreur base de données: {e}")

    def search_airspaces(self, airspace_type: str = None, name_pattern: str = None) -> List[Dict]:
        """Recherche les espaces aériens"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM airspaces WHERE 1=1"
        params = []
        
        if airspace_type:
            query += " AND code_type = ?"
            params.append(airspace_type)
            
        if name_pattern:
            query += " AND name LIKE ?"
            params.append(f'%{name_pattern}%')
            
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def search_by_keyword(self, keyword: str, case_sensitive: bool = False, limit: int = None) -> List[Dict]:
        """
        Search airspaces by keyword with detailed information
        
        Args:
            keyword (str): Keyword to search for in airspace names
            case_sensitive (bool): Whether search should be case sensitive
            limit (int): Maximum number of results to return (None for all)
            
        Returns:
            List[Dict]: List of detailed airspace records matching the keyword
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build search query - search in both name AND code_id
        if case_sensitive:
            where_clause = "WHERE (name LIKE ? OR code_id LIKE ?)"
            search_pattern = f'%{keyword}%'
            params = [search_pattern, search_pattern]
        else:
            where_clause = "WHERE (UPPER(name) LIKE UPPER(?) OR UPPER(code_id) LIKE UPPER(?))"
            search_pattern = f'%{keyword}%'
            params = [search_pattern, search_pattern]
        
        # Get all columns available in the table
        cursor.execute("PRAGMA table_info(airspaces)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Build the main query
        query = f"""
        SELECT * FROM airspaces 
        {where_clause}
        ORDER BY name
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        raw_results = cursor.fetchall()
        
        # Convert to detailed dictionaries
        detailed_results = []
        for row in raw_results:
            airspace_data = dict(row)
            
            # Get geometry information if available
            airspace_id = airspace_data['id']
            
            # Check for borders/geometry
            try:
                cursor.execute("SELECT COUNT(*) as border_count FROM airspace_borders WHERE airspace_id = ?", (airspace_id,))
                border_count = cursor.fetchone()
                airspace_data['border_count'] = border_count[0] if border_count else 0
                
                if airspace_data['border_count'] > 0:
                    cursor.execute("""
                        SELECT COUNT(*) as vertex_count 
                        FROM border_vertices 
                        WHERE border_id IN (SELECT id FROM airspace_borders WHERE airspace_id = ?)
                    """, (airspace_id,))
                    vertex_count = cursor.fetchone()
                    airspace_data['vertex_count'] = vertex_count[0] if vertex_count else 0
                else:
                    airspace_data['vertex_count'] = 0
                    
            except sqlite3.OperationalError:
                # Tables don't exist
                airspace_data['border_count'] = 0
                airspace_data['vertex_count'] = 0
            
            # Format altitude information for display
            min_alt = airspace_data.get('min_altitude')
            max_alt = airspace_data.get('max_altitude')
            min_unit = airspace_data.get('min_altitude_unit', '')
            max_unit = airspace_data.get('max_altitude_unit', '')
            
            if min_alt is not None and max_alt is not None:
                airspace_data['altitude_display'] = f"{min_alt}-{max_alt} {max_unit}"
            elif min_alt is not None:
                airspace_data['altitude_display'] = f"{min_alt}+ {min_unit}"
            elif max_alt is not None:
                airspace_data['altitude_display'] = f"0-{max_alt} {max_unit}"
            else:
                airspace_data['altitude_display'] = "No altitude limits"
            
            detailed_results.append(airspace_data)
        
        conn.close()
        return detailed_results

    def get_airspace_details(self, code_id: str) -> Optional[Dict]:
        """
        Get complete details for a specific airspace by its code_id
        
        Args:
            code_id (str): The airspace code identifier
            
        Returns:
            Dict: Complete airspace information or None if not found
        """
        results = self.search_by_keyword(code_id, case_sensitive=True, limit=1)
        
        # Filter to exact match
        exact_matches = [r for r in results if r['code_id'] == code_id]
        return exact_matches[0] if exact_matches else None

    def get_statistics(self) -> Dict[str, any]:
        """Retourne les statistiques de la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM airspaces")
        total_airspaces = cursor.fetchone()[0]
        
        try:
            cursor.execute("""
                SELECT COUNT(DISTINCT a.id) 
                FROM airspaces a 
                JOIN airspace_borders ab ON a.id = ab.airspace_id 
                JOIN border_vertices bv ON ab.id = bv.border_id
            """)
            airspaces_with_geometry = cursor.fetchone()[0]
        except:
            airspaces_with_geometry = 0
        
        try:
            cursor.execute("SELECT COUNT(*) FROM border_vertices")
            total_vertices = cursor.fetchone()[0]
        except:
            total_vertices = 0
        
        conn.close()
        
        geometry_coverage = (airspaces_with_geometry / total_airspaces * 100) if total_airspaces > 0 else 0
        
        return {
            "total_airspaces": total_airspaces,
            "airspaces_with_geometry": airspaces_with_geometry,
            "geometry_coverage": geometry_coverage,
            "total_vertices": total_vertices
        }


if __name__ == "__main__":
    try:
        service = AirspaceQueryService()
        stats = service.get_statistics()
        print(f"✅ Service OK - {stats['total_airspaces']} espaces aériens")
    except Exception as e:
        print(f"❌ Erreur: {e}")