#!/usr/bin/env python3
"""
AIXM Airspace Extractor - Version finale avec géométrie complète
Basé sur l'extracteur fonctionnel, ajout de l'extraction des frontières
"""

import xml.etree.ElementTree as ET
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_coordinate_aixm(coord_str: str) -> Optional[float]:
    """Parse une coordonnée au format AIXM (DDMMSS.ssH ou DDDMMSS.ssH)"""
    if not coord_str:
        return None
    
    try:
        direction = coord_str[-1].upper()
        coord_value = coord_str[:-1]
        
        if len(coord_value) == 9:  # DDMMSS.ss
            degrees = int(coord_value[:2])
            minutes = int(coord_value[2:4])
            seconds = float(coord_value[4:])
        elif len(coord_value) == 10:  # DDDMMSS.ss
            degrees = int(coord_value[:3])
            minutes = int(coord_value[3:5])
            seconds = float(coord_value[5:])
        else:
            logger.warning(f"Format de coordonnée non reconnu: {coord_str}")
            return None
        
        decimal = degrees + minutes/60 + seconds/3600
        
        if direction in ['S', 'W']:
            decimal = -decimal
        
        return decimal
    
    except (ValueError, IndexError) as e:
        logger.error(f"Erreur lors du parsing de la coordonnée {coord_str}: {e}")
        return None

class AIXMExtractor:
    def __init__(self, xml_path: str, db_path: str):
        self.xml_path = Path(xml_path)
        self.db_path = Path(db_path)
        
        # Statistiques
        self.airspace_count = 0
        self.border_count = 0
        self.vertex_count = 0
        self.ase_elements_found = 0
        self.abd_elements_found = 0
        self.aseuid_found = 0
        self.valid_airspaces = 0
        
        # Mapping pour lier les espaces aux frontières
        # Utilisons le code_id comme clé de liaison simple
        self.airspace_mapping = {}  # code_id -> airspace_id
        self.processed_borders = set()  # Pour éviter les doublons
        
    def init_database(self):
        """Initialise la base de données avec le schéma"""
        conn = sqlite3.connect(self.db_path)
        
        conn.executescript("""
            -- Table principale des espaces aériens
            CREATE TABLE IF NOT EXISTS airspaces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_id TEXT NOT NULL,
                code_type TEXT,
                mid TEXT,
                name TEXT,
                airspace_class TEXT,
                activity_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Table des frontières d'espaces aériens
            CREATE TABLE IF NOT EXISTS airspace_borders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                airspace_id INTEGER NOT NULL,
                border_type TEXT DEFAULT 'STANDARD',
                is_circle BOOLEAN DEFAULT FALSE,
                circle_center_lat REAL,
                circle_center_lon REAL,
                circle_radius_km REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (airspace_id) REFERENCES airspaces(id) ON DELETE CASCADE
            );

            -- Table des vertices des frontières
            CREATE TABLE IF NOT EXISTS border_vertices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                border_id INTEGER NOT NULL,
                sequence_number INTEGER NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                path_type TEXT DEFAULT 'GRC',
                arc_center_lat REAL,
                arc_center_lon REAL,
                arc_radius_km REAL,
                arc_direction TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (border_id) REFERENCES airspace_borders(id) ON DELETE CASCADE
            );

            -- Table des limites verticales
            CREATE TABLE IF NOT EXISTS vertical_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                airspace_id INTEGER NOT NULL,
                lower_limit_ft INTEGER,
                lower_limit_ref TEXT,
                upper_limit_ft INTEGER,
                upper_limit_ref TEXT,
                unit_of_measure TEXT DEFAULT 'FT',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (airspace_id) REFERENCES airspaces(id) ON DELETE CASCADE
            );

            -- Index pour améliorer les performances
            CREATE INDEX IF NOT EXISTS idx_airspaces_code_id ON airspaces(code_id);
            CREATE INDEX IF NOT EXISTS idx_borders_airspace_id ON airspace_borders(airspace_id);
            CREATE INDEX IF NOT EXISTS idx_vertices_border_id ON border_vertices(border_id);
            CREATE INDEX IF NOT EXISTS idx_vertices_sequence ON border_vertices(border_id, sequence_number);
            CREATE INDEX IF NOT EXISTS idx_vertical_limits_airspace_id ON vertical_limits(airspace_id);
        """)
        
        conn.commit()
        conn.close()
        logger.info("Base de données initialisée")
    
    def extract_airspace_uid(self, ase_element) -> Optional[Dict[str, str]]:
        """Extrait les informations d'identification d'un élément Ase"""
        try:
            aseuid = ase_element.find('AseUid')
            if aseuid is not None:
                self.aseuid_found += 1
                
                uid_data = {}
                for field_map in [('mid', 'mid'), ('codeType', 'code_type'), ('codeId', 'code_id')]:
                    elem_name, dict_key = field_map
                    element = aseuid.find(elem_name)
                    if element is not None and element.text:
                        uid_data[dict_key] = element.text.strip()
                
                return uid_data
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction AseUid: {e}")
            return None
    
    def extract_altitude_info(self, ase_element) -> Dict[str, Optional[str]]:
        """Extrait les informations d'altitude d'un élément Ase"""
        altitude_info = {
            'min_altitude': None,
            'max_altitude': None,
            'min_altitude_unit': None,
            'max_altitude_unit': None
        }
        
        try:
            # Extract upper limit (maximum altitude)
            upper_val_elem = ase_element.find('valDistVerUpper')
            upper_uom_elem = ase_element.find('uomDistVerUpper')
            if upper_val_elem is not None and upper_val_elem.text:
                altitude_info['max_altitude'] = upper_val_elem.text.strip()
                if upper_uom_elem is not None and upper_uom_elem.text:
                    altitude_info['max_altitude_unit'] = upper_uom_elem.text.strip()
            
            # Extract lower limit (minimum altitude) 
            lower_val_elem = ase_element.find('valDistVerLower')
            lower_uom_elem = ase_element.find('uomDistVerLower')
            if lower_val_elem is not None and lower_val_elem.text:
                altitude_info['min_altitude'] = lower_val_elem.text.strip()
                if lower_uom_elem is not None and lower_uom_elem.text:
                    altitude_info['min_altitude_unit'] = lower_uom_elem.text.strip()
            
            return altitude_info
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des altitudes: {e}")
            return altitude_info
    
    def process_airspaces_pass1(self, conn: sqlite3.Connection):
        """Première passe : extraire tous les espaces aériens"""
        logger.info("=== PASSE 1: EXTRACTION DES ESPACES AÉRIENS ===")
        
        for event, elem in ET.iterparse(self.xml_path, events=('start', 'end')):
            if event == 'end' and (elem.tag == 'Ase' or elem.tag.endswith('}Ase')):
                self.ase_elements_found += 1
                
                uid_data = self.extract_airspace_uid(elem)
                altitude_data = self.extract_altitude_info(elem)
                
                if uid_data and 'code_id' in uid_data:
                    # Extract airspace name from txtName element
                    name_elem = elem.find('txtName')
                    airspace_name = name_elem.text.strip() if name_elem is not None and name_elem.text else uid_data.get('code_id')
                    
                    # Extract airspace class from codeClass element
                    class_elem = elem.find('codeClass')
                    airspace_class = class_elem.text.strip() if class_elem is not None and class_elem.text else 'UNKNOWN'
                    
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO airspaces (
                            code_id, code_type, mid, name, airspace_class
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        uid_data.get('code_id'),
                        uid_data.get('code_type'),
                        uid_data.get('mid'),
                        airspace_name,
                        airspace_class
                    ))
                    
                    airspace_id = cursor.lastrowid
                    
                    # Insert altitude information into vertical_limits table
                    if altitude_data.get('min_altitude') or altitude_data.get('max_altitude'):
                        cursor.execute("""
                            INSERT INTO vertical_limits (
                                airspace_id, lower_limit_ft, upper_limit_ft, 
                                lower_limit_ref, upper_limit_ref, unit_of_measure
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            airspace_id,
                            altitude_data.get('min_altitude'),
                            altitude_data.get('max_altitude'),
                            altitude_data.get('min_altitude_unit', 'FT'),
                            altitude_data.get('max_altitude_unit', 'FT'),
                            'FT'
                        ))
                    self.airspace_count += 1
                    self.valid_airspaces += 1
                    
                    # Stocker le mapping pour la passe 2
                    self.airspace_mapping[uid_data.get('code_id')] = airspace_id
                    
                    if self.valid_airspaces % 1000 == 0:
                        logger.info(f"Espaces aériens traités: {self.valid_airspaces}")
                
                elem.clear()
                
                if self.ase_elements_found % 1000 == 0:
                    conn.commit()
        
        conn.commit()
        logger.info(f"Passe 1 terminée: {self.valid_airspaces} espaces aériens extraits")
    
    def extract_border_reference(self, abd_element) -> Optional[str]:
        """Extrait la référence vers l'espace aérien depuis un élément Abd"""
        try:
            abduid = abd_element.find('AbdUid')
            if abduid is not None:
                # Chercher AseUid dans AbdUid
                aseuid = abduid.find('AseUid') 
                if aseuid is not None:
                    code_id_elem = aseuid.find('codeId')
                    if code_id_elem is not None and code_id_elem.text:
                        return code_id_elem.text.strip()
            return None
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de la référence Abd: {e}")
            return None
    
    def extract_vertices_from_abd(self, abd_element, border_id: int, conn: sqlite3.Connection):
        """Extrait les vertices d'un élément Abd"""
        avx_elements = abd_element.findall('Avx')
        
        for avx in avx_elements:
            try:
                lat_elem = avx.find('geoLat')
                lon_elem = avx.find('geoLong')
                seq_elem = avx.find('noSeq')
                
                if lat_elem is not None and lon_elem is not None:
                    latitude = parse_coordinate_aixm(lat_elem.text) if lat_elem.text else None
                    longitude = parse_coordinate_aixm(lon_elem.text) if lon_elem.text else None
                    sequence = int(seq_elem.text) if seq_elem is not None and seq_elem.text else 1
                    
                    if latitude is not None and longitude is not None:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO border_vertices 
                            (border_id, sequence_number, latitude, longitude)
                            VALUES (?, ?, ?, ?)
                        """, (border_id, sequence, latitude, longitude))
                        
                        self.vertex_count += 1
            
            except Exception as e:
                logger.error(f"Erreur lors de l'extraction du vertex: {e}")
    
    def process_borders_pass2(self, conn: sqlite3.Connection):
        """Deuxième passe : extraire les frontières et leurs vertices"""
        logger.info("=== PASSE 2: EXTRACTION DES FRONTIÈRES ===")
        
        for event, elem in ET.iterparse(self.xml_path, events=('start', 'end')):
            if event == 'end' and (elem.tag == 'Abd' or elem.tag.endswith('}Abd')):
                self.abd_elements_found += 1
                
                # Extraire la référence vers l'espace aérien
                airspace_code_id = self.extract_border_reference(elem)
                
                if airspace_code_id and airspace_code_id in self.airspace_mapping:
                    airspace_id = self.airspace_mapping[airspace_code_id]
                    
                    # Éviter les doublons de frontières
                    border_key = f"{airspace_id}_{self.abd_elements_found}"
                    if border_key not in self.processed_borders:
                        # Créer la frontière
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO airspace_borders (airspace_id, border_type)
                            VALUES (?, ?)
                        """, (airspace_id, 'STANDARD'))
                        
                        border_id = cursor.lastrowid
                        self.border_count += 1
                        self.processed_borders.add(border_key)
                        
                        # Extraire les vertices de cette frontière
                        self.extract_vertices_from_abd(elem, border_id, conn)
                        
                        if self.border_count % 500 == 0:
                            logger.info(f"Frontières traitées: {self.border_count}, Vertices: {self.vertex_count}")
                
                elem.clear()
                
                if self.abd_elements_found % 1000 == 0:
                    conn.commit()
        
        conn.commit()
        logger.info(f"Passe 2 terminée: {self.border_count} frontières extraites, {self.vertex_count} vertices")
    
    def extract_complete_data(self):
        """Méthode principale d'extraction complète"""
        logger.info("Début de l'extraction complète des données AIXM")
        
        # Initialiser la base
        self.init_database()
        
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Passe 1: Espaces aériens
            self.process_airspaces_pass1(conn)
            
            # Passe 2: Frontières et vertices
            self.process_borders_pass2(conn)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction: {e}")
            conn.rollback()
        finally:
            conn.close()
        
        self.print_statistics()
    
    def print_statistics(self):
        """Affiche les statistiques d'extraction"""
        logger.info("=== STATISTIQUES D'EXTRACTION FINALE ===")
        logger.info(f"Éléments <Ase> trouvés: {self.ase_elements_found}")
        logger.info(f"Éléments <AseUid> trouvés: {self.aseuid_found}")
        logger.info(f"Espaces aériens valides extraits: {self.valid_airspaces}")
        logger.info(f"Éléments <Abd> trouvés: {self.abd_elements_found}")
        logger.info(f"Frontières créées: {self.border_count}")
        logger.info(f"Vertices créés: {self.vertex_count}")

def main():
    # Use relative paths based on the script location
    script_dir = Path(__file__).parent
    xml_path = script_dir.parent / "data" / "AIXM4.5_all_FR_OM_2025-10-02.xml"
    db_path = script_dir.parent / "data" / "airspaces.db"
    
    extractor = AIXMExtractor(str(xml_path), str(db_path))
    extractor.extract_complete_data()

if __name__ == "__main__":
    main()