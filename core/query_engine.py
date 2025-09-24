#!/usr/bin/env python3
"""
Fixed airspace query engine that handles Flight Levels correctly
"""
import sqlite3
import math
from typing import List, Dict, Tuple, Optional
from shapely.geometry import Point, Polygon, box
from shapely.strtree import STRtree
import xml.etree.ElementTree as ET

class FixedAirspaceQueryEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
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
    
    def find_airspaces_at_point(self, lat: float, lon: float, alt_ft: float, 
                                corridor_height_ft: int = 1000, corridor_width_km: float = 18.52) -> List[Dict]:
        """Find airspaces that contain or are within corridor of the given point"""
        point = Point(lon, lat)
        
        # Create buffer around point for corridor analysis  
        buffer_degrees = corridor_width_km / 111.32  # Rough conversion km to degrees at equator
        buffered_point = point.buffer(buffer_degrees)
        
        # Stage 1: Find potential airspaces using spatial index
        if not self.spatial_index:
            return []
            
        potential_indices = list(self.spatial_index.query(buffered_point))
        
        # Stage 2: Check precise geometry intersection
        intersecting_airspaces = []
        for idx in potential_indices:
            airspace_id = self.airspace_ids[idx]
            if airspace_id in self.airspace_geometries:
                geom = self.airspace_geometries[airspace_id]
                if geom.intersects(buffered_point):
                    intersecting_airspaces.append(airspace_id)
        
        # Stage 3: Get full airspace details and check altitude
        result_airspaces = []
        for airspace_id in intersecting_airspaces:
            airspace_data = self._get_airspace_details(airspace_id)
            if airspace_data and self._is_altitude_in_range(airspace_data, alt_ft, corridor_height_ft):
                result_airspaces.append(airspace_data)
                
        return result_airspaces
    
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
    
    def _convert_altitude_to_feet(self, value: Optional[int], reference: Optional[str]) -> float:
        """Convert altitude value to feet, handling Flight Levels"""
        if value is None:
            return 0.0 if reference == 'FT' else float('inf')
        
        if reference == 'FL':
            # Flight Level: FL65 = 6500 feet
            return value * 100
        elif reference == 'FT':
            return float(value)
        else:
            # Default to feet if unknown
            return float(value)
    
    def query_airspaces_for_point(self, lon: float, lat: float, altitude_ft: float, 
                                  debug: bool = False) -> List[Dict]:
        """3-stage filtering for a single point with fixed altitude handling"""
        if not self.spatial_index:
            print("Warning: Spatial index not available")
            return []
            
        point = Point(lon, lat)
        results = []
        
        # STAGE 1: Fast bounding box query using STRtree
        potential_indices = list(self.spatial_index.query(point))
        if debug:
            print(f"Stage 1 (bbox): {len(potential_indices)} candidates for point ({lon:.4f}, {lat:.4f})")
        
        stage2_candidates = []
        for idx in potential_indices:
            airspace_id = self.airspace_ids[idx]
            
            # STAGE 2: Precise boundary check
            if self._point_in_precise_boundary(airspace_id, point):
                stage2_candidates.append(airspace_id)
        
        if debug:
            print(f"Stage 2 (precise): {len(stage2_candidates)} candidates")
        
        # STAGE 3: Altitude check with corrected Flight Level handling
        for airspace_id in stage2_candidates:
            airspace_data = self._get_airspace_data(airspace_id)
            if self._altitude_in_range(altitude_ft, airspace_data):
                results.append(airspace_data)
        
        if debug:
            print(f"Stage 3 (altitude): {len(results)} final matches")
        
        return results
    
    def _point_in_precise_boundary(self, airspace_id: int, point: Point) -> bool:
        """Check if point is within precise airspace boundary"""
        if airspace_id in self.airspace_geometries:
            polygon = self.airspace_geometries[airspace_id]
            return polygon.contains(point)
        return False
    
    def _altitude_in_range(self, altitude_ft: float, airspace_data: Dict) -> bool:
        """Check vertical boundaries with correct Flight Level conversion"""
        lower_ft = airspace_data.get('lower_limit_ft_converted', 0)
        upper_ft = airspace_data.get('upper_limit_ft_converted', float('inf'))
        
        return lower_ft <= altitude_ft <= upper_ft
    
    def _get_airspace_data(self, airspace_id: int) -> Dict:
        """Get full airspace details including altitude limits with FL conversion"""
        cursor = self.conn.execute("""
            SELECT a.id, a.name, a.code_id, a.airspace_class, a.code_type,
                   vl.lower_limit_ft, vl.upper_limit_ft, vl.lower_limit_ref, vl.upper_limit_ref
            FROM airspaces a
            LEFT JOIN vertical_limits vl ON a.id = vl.airspace_id
            WHERE a.id = ?
        """, (airspace_id,))
        
        row = cursor.fetchone()
        if row:
            # Convert altitudes to feet
            lower_ft_converted = self._convert_altitude_to_feet(row['lower_limit_ft'], row['lower_limit_ref'])
            upper_ft_converted = self._convert_altitude_to_feet(row['upper_limit_ft'], row['upper_limit_ref'])
            
            return {
                'id': row['id'],
                'name': row['name'],
                'code_id': row['code_id'],
                'airspace_class': row['airspace_class'],
                'code_type': row['code_type'],
                'lower_limit_ft': row['lower_limit_ft'],
                'upper_limit_ft': row['upper_limit_ft'],
                'lower_limit_ref': row['lower_limit_ref'],
                'upper_limit_ref': row['upper_limit_ref'],
                'lower_limit_ft_converted': lower_ft_converted,
                'upper_limit_ft_converted': upper_ft_converted
            }
        return {}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def _get_airspace_details(self, airspace_id: int) -> Dict:
        """Get complete airspace details from database"""
        cursor = self.conn.execute("""
            SELECT a.id, a.name, a.code_id, a.airspace_class, a.code_type,
                   v.lower_limit_ft, v.upper_limit_ft, 
                   v.lower_limit_ref, v.upper_limit_ref
            FROM airspaces a
            LEFT JOIN vertical_limits v ON a.id = v.airspace_id
            WHERE a.id = ?
            LIMIT 1
        """, (airspace_id,))
        
        row = cursor.fetchone()
        if row:
            # Convert altitudes to feet
            lower_ft_converted = self._convert_altitude_to_feet(row['lower_limit_ft'], row['lower_limit_ref'])
            upper_ft_converted = self._convert_altitude_to_feet(row['upper_limit_ft'], row['upper_limit_ref'])
            
            return {
                'id': row['id'],
                'name': row['name'],
                'code_id': row['code_id'],
                'airspace_class': row['airspace_class'],
                'code_type': row['code_type'],
                'lower_limit_ft': row['lower_limit_ft'],
                'upper_limit_ft': row['upper_limit_ft'],
                'lower_limit_ref': row['lower_limit_ref'],
                'upper_limit_ref': row['upper_limit_ref'],
                'lower_limit_ft_converted': lower_ft_converted,
                'upper_limit_ft_converted': upper_ft_converted
            }
        return {}
    
    def _is_altitude_in_range(self, airspace_data: Dict, altitude_ft: float, corridor_height_ft: int) -> bool:
        """Check if altitude falls within airspace range (with corridor)"""
        lower_ft = airspace_data.get('lower_limit_ft_converted', 0)
        upper_ft = airspace_data.get('upper_limit_ft_converted', 99999)
        
        # Apply corridor tolerance
        altitude_min = altitude_ft - corridor_height_ft
        altitude_max = altitude_ft + corridor_height_ft
        
        # Check for overlap: airspace overlaps if any part of altitude range intersects
        return not (altitude_max < lower_ft or altitude_min > upper_ft)


def test_fixed_altitudes():
    """Test the fixed altitude handling"""
    print("Testing FIXED Altitude Handling (Flight Levels)")
    print("=" * 60)
    
    engine = FixedAirspaceQueryEngine('data/airspaces.db')
    
    # Test specific coordinates that should hit TMAs
    test_points = [
        # Orleans area - should now find ORLEANS TMAs
        (1.9, 47.9, 3000, "Orleans area"),
        (2.0, 47.8, 5000, "Orleans area higher"),
        
        # Avord area - should find AVORD TMAs  
        (2.6, 46.9, 4000, "Avord area"),
        (2.7, 47.0, 5000, "Avord area higher"),
        
        # Along the original flight path
        (2.0, 48.0, 3000, "Mid-route"),
        (2.0, 48.0, 8000, "Mid-route high"),
        (2.2, 47.4, 3000, "Near restricted area"),
    ]
    
    for lon, lat, alt, description in test_points:
        print(f"\nTesting {description}: ({lon:.1f}, {lat:.1f}) at {alt} ft")
        airspaces = engine.query_airspaces_for_point(lon, lat, alt, debug=True)
        
        if airspaces:
            print(f"  Found {len(airspaces)} airspace(s):")
            for airspace in airspaces:
                lower_conv = airspace.get('lower_limit_ft_converted', 0)
                upper_conv = airspace.get('upper_limit_ft_converted', float('inf'))
                lower_ref = airspace.get('lower_limit_ref', 'FT')
                upper_ref = airspace.get('upper_limit_ref', 'FT')
                
                print(f"    - {airspace['name']} ({airspace['code_id']}) - {airspace['code_type']}")
                print(f"      Original: {airspace['lower_limit_ft']}{lower_ref} - {airspace['upper_limit_ft']}{upper_ref}")
                print(f"      Converted: {lower_conv:.0f}ft - {upper_conv:.0f}ft")
        else:
            print("  No airspaces found")
    
    engine.close()

if __name__ == "__main__":
    test_fixed_altitudes()