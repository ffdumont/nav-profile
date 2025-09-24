#!/usr/bin/env python3
"""
3-Stage Airspace Query Engine
Stage 1: STRtree bounding box filtering
Stage 2: Precise boundary geometry check
Stage 3: Altitude filtering
"""
import sqlite3
import math
from typing import List, Dict, Tuple, Optional
from shapely.geometry import Point, Polygon, box
from shapely.strtree import STRtree
import xml.etree.ElementTree as ET

class AirspaceQueryEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Enable accessing columns by name
        
        # These will be populated by _build_spatial_index()
        self.bounding_boxes = []
        self.airspace_ids = []
        self.airspace_geometries = {}
        self.spatial_index = None
        
        self._build_spatial_index()
    
    def _build_spatial_index(self):
        """Build STRtree index from airspace bounding boxes and load geometries"""
        print("Building spatial index...")
        
        cursor = self.conn.execute("""
            SELECT DISTINCT a.id, a.name, a.code_id, a.airspace_class 
            FROM airspaces a 
            JOIN airspace_borders ab ON a.id = ab.airspace_id 
            JOIN border_vertices bv ON ab.id = bv.border_id
            ORDER BY a.id
        """)
        
        processed_airspaces = set()
        
        for row in cursor:
            airspace_id = row['id']
            if airspace_id in processed_airspaces:
                continue
                
            # Get all vertices for this airspace
            vertices = self._get_airspace_vertices(airspace_id)
            if not vertices:
                continue
                
            # Calculate bounding box
            lons = [v[0] for v in vertices]
            lats = [v[1] for v in vertices]
            
            min_lon, max_lon = min(lons), max(lons)
            min_lat, max_lat = min(lats), max(lats)
            
            # Create bounding box geometry
            bbox = box(min_lon, min_lat, max_lon, max_lat)
            
            # Store the polygon geometry for precise checking
            if len(vertices) >= 3:  # Valid polygon needs at least 3 vertices
                polygon = Polygon(vertices)
                self.airspace_geometries[airspace_id] = polygon
                
                self.bounding_boxes.append(bbox)
                self.airspace_ids.append(airspace_id)
                processed_airspaces.add(airspace_id)
        
        # Create STRtree spatial index
        if self.bounding_boxes:
            self.spatial_index = STRtree(self.bounding_boxes)
            print(f"Spatial index built for {len(self.bounding_boxes)} airspaces")
        else:
            print("Warning: No airspaces found for spatial indexing")
    
    def _get_airspace_vertices(self, airspace_id: int) -> List[Tuple[float, float]]:
        """Get all vertices for an airspace (handling circles and polygons)"""
        vertices = []
        
        # Get borders for this airspace
        cursor = self.conn.execute("""
            SELECT id, is_circle, circle_center_lat, circle_center_lon, circle_radius_km
            FROM airspace_borders 
            WHERE airspace_id = ?
            ORDER BY id
        """, (airspace_id,))
        
        for border in cursor:
            border_id = border['id']
            is_circle = border['is_circle']
            
            if is_circle:
                # Handle circular boundaries
                center_lat = border['circle_center_lat']
                center_lon = border['circle_center_lon']
                radius_km = border['circle_radius_km']
                
                if center_lat and center_lon and radius_km:
                    # Generate polygon approximation of circle
                    circle_vertices = self._generate_circle_vertices(
                        center_lat, center_lon, radius_km, num_points=32
                    )
                    vertices.extend(circle_vertices)
            else:
                # Handle polygon boundaries
                vertex_cursor = self.conn.execute("""
                    SELECT latitude, longitude 
                    FROM border_vertices 
                    WHERE border_id = ?
                    ORDER BY sequence_number
                """, (border_id,))
                
                for vertex in vertex_cursor:
                    if vertex['latitude'] and vertex['longitude']:
                        vertices.append((vertex['longitude'], vertex['latitude']))
        
        return vertices
    
    def _generate_circle_vertices(self, center_lat: float, center_lon: float, 
                                 radius_km: float, num_points: int = 32) -> List[Tuple[float, float]]:
        """Generate vertices for a circular boundary"""
        vertices = []
        
        # Convert radius to degrees (rough approximation)
        lat_degree_km = 110.574  # km per degree latitude
        lon_degree_km = 111.320 * math.cos(math.radians(center_lat))  # km per degree longitude at this latitude
        
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            
            # Calculate offset in km
            offset_lat_km = radius_km * math.sin(angle)
            offset_lon_km = radius_km * math.cos(angle)
            
            # Convert to degrees
            lat = center_lat + (offset_lat_km / lat_degree_km)
            lon = center_lon + (offset_lon_km / lon_degree_km)
            
            vertices.append((lon, lat))
        
        return vertices
    
    def query_airspaces_for_point(self, lon: float, lat: float, altitude_ft: float) -> List[Dict]:
        """3-stage filtering for a single point"""
        if not self.spatial_index:
            print("Warning: Spatial index not available")
            return []
            
        point = Point(lon, lat)
        results = []
        
        # STAGE 1: Fast bounding box query using STRtree
        potential_indices = list(self.spatial_index.query(point))
        print(f"Stage 1 (bbox): {len(potential_indices)} candidates for point ({lon:.4f}, {lat:.4f})")
        
        stage2_candidates = 0
        for idx in potential_indices:
            airspace_id = self.airspace_ids[idx]
            
            # STAGE 2: Precise boundary check
            if self._point_in_precise_boundary(airspace_id, point):
                stage2_candidates += 1
                
                # STAGE 3: Altitude check
                airspace_data = self._get_airspace_data(airspace_id)
                if self._altitude_in_range(altitude_ft, airspace_data):
                    results.append(airspace_data)
        
        print(f"Stage 2 (precise): {stage2_candidates} candidates")
        print(f"Stage 3 (altitude): {len(results)} final matches")
        
        return results
    
    def _point_in_precise_boundary(self, airspace_id: int, point: Point) -> bool:
        """Check if point is within precise airspace boundary"""
        if airspace_id in self.airspace_geometries:
            polygon = self.airspace_geometries[airspace_id]
            return polygon.contains(point)
        return False
    
    def _altitude_in_range(self, altitude_ft: float, airspace_data: Dict) -> bool:
        """Check vertical boundaries"""
        lower_ft = airspace_data.get('lower_limit_ft', 0)
        upper_ft = airspace_data.get('upper_limit_ft', float('inf'))
        
        if lower_ft is None:
            lower_ft = 0
        if upper_ft is None:
            upper_ft = float('inf')
            
        return lower_ft <= altitude_ft <= upper_ft
    
    def _get_airspace_data(self, airspace_id: int) -> Dict:
        """Get full airspace details including altitude limits"""
        cursor = self.conn.execute("""
            SELECT a.id, a.name, a.code_id, a.airspace_class, a.code_type,
                   vl.lower_limit_ft, vl.upper_limit_ft, vl.lower_limit_ref, vl.upper_limit_ref
            FROM airspaces a
            LEFT JOIN vertical_limits vl ON a.id = vl.airspace_id
            WHERE a.id = ?
        """, (airspace_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'name': row['name'],
                'code_id': row['code_id'],
                'airspace_class': row['airspace_class'],
                'code_type': row['code_type'],
                'lower_limit_ft': row['lower_limit_ft'],
                'upper_limit_ft': row['upper_limit_ft'],
                'lower_limit_ref': row['lower_limit_ref'],
                'upper_limit_ref': row['upper_limit_ref']
            }
        return {}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


class KMLFlightPathParser:
    """Parse KML flight path and extract coordinates with altitudes"""
    
    @staticmethod
    def parse_kml_coordinates(kml_file_path: str) -> List[Tuple[float, float, float]]:
        """Extract coordinates from KML file"""
        try:
            tree = ET.parse(kml_file_path)
            root = tree.getroot()
            
            # Find coordinates in the navigation LineString
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}
            
            # Look for LineString coordinates
            linestring = root.find('.//kml:LineString/kml:coordinates', ns)
            if linestring is not None:
                coords_text = linestring.text.strip()
                return KMLFlightPathParser._parse_coordinates_string(coords_text)
            
            print("No LineString coordinates found in KML")
            return []
            
        except Exception as e:
            print(f"Error parsing KML: {e}")
            return []
    
    @staticmethod
    def _parse_coordinates_string(coords_text: str) -> List[Tuple[float, float, float]]:
        """Parse coordinate string from KML"""
        coordinates = []
        
        # Remove extra whitespace and split by comma
        parts = coords_text.replace('\n', '').replace('\t', '').split(',')
        
        # Process in groups of 3 (lon, lat, alt)
        for i in range(0, len(parts) - 2, 3):
            try:
                lon = float(parts[i].strip())
                lat = float(parts[i + 1].strip())
                alt_m = float(parts[i + 2].strip())
                
                # Convert altitude from meters to feet
                alt_ft = alt_m * 3.28084
                
                coordinates.append((lon, lat, alt_ft))
            except (ValueError, IndexError) as e:
                print(f"Error parsing coordinate group at index {i}: {e}")
                continue
        
        return coordinates


def test_airspace_query():
    """Test the 3-stage airspace query system"""
    print("Testing 3-Stage Airspace Query Engine")
    print("=" * 50)
    
    # Initialize query engine
    engine = AirspaceQueryEngine('data/airspaces.db')
    
    # Parse flight path from KML
    flight_coordinates = KMLFlightPathParser.parse_kml_coordinates('data/20250924_083633_LFXU-LFFU.kml')
    
    if not flight_coordinates:
        print("Failed to parse flight coordinates from KML")
        return
    
    print(f"Parsed {len(flight_coordinates)} waypoints from KML")
    print("Flight path waypoints:")
    for i, (lon, lat, alt_ft) in enumerate(flight_coordinates):
        print(f"  {i+1}: ({lon:.4f}, {lat:.4f}) at {alt_ft:.0f} ft")
    
    print("\n" + "=" * 50)
    print("Testing airspace queries for each waypoint...")
    
    total_airspaces_found = set()
    
    for i, (lon, lat, alt_ft) in enumerate(flight_coordinates):
        print(f"\nWaypoint {i+1}: ({lon:.4f}, {lat:.4f}) at {alt_ft:.0f} ft")
        print("-" * 30)
        
        airspaces = engine.query_airspaces_for_point(lon, lat, alt_ft)
        
        if airspaces:
            print(f"Found {len(airspaces)} airspace(s):")
            for airspace in airspaces:
                print(f"  - {airspace['name']} ({airspace['code_id']}) - {airspace['airspace_class']}")
                print(f"    Altitude: {airspace['lower_limit_ft']}ft - {airspace['upper_limit_ft']}ft")
                total_airspaces_found.add(airspace['id'])
        else:
            print("No airspaces found at this point")
    
    print(f"\n" + "=" * 50)
    print(f"SUMMARY: Flight path crosses {len(total_airspaces_found)} unique airspace(s)")
    
    engine.close()


if __name__ == "__main__":
    test_airspace_query()