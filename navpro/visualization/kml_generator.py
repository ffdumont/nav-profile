#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KML Volume Service for airspaces
Generates 3D KML volumes from airspace boundary geometry and altitude data
"""

import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import math
import sys
import os

# Add production directory to path for color config import
sys.path.insert(0, os.path.dirname(__file__))
from visualization.kml_styling import get_airspace_color, get_line_color, LINE_WIDTH


class KMLVolumeService:
    """Service to generate KML volumes for airspaces"""
    
    def __init__(self, db_path: str = None):
        """Initialize the service with the database"""
        if db_path is None:
            current_dir = Path(__file__).parent
            db_path = current_dir.parent / "data" / "airspaces.db"
        
        self.db_path = str(db_path)
        self._validate_database()

    def _validate_database(self):
        """Validate that the database exists and has required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            required_tables = ['airspaces', 'airspace_borders', 'border_vertices']
            for table in required_tables:
                if table not in tables:
                    raise Exception(f"Required table '{table}' missing")
                    
        except Exception as e:
            raise Exception(f"Database error: {e}")

    def _get_airspace_geometry(self, airspace_id: int) -> List[Dict]:
        """Get the complete geometry for an airspace"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all borders for this airspace
        cursor.execute("""
            SELECT * FROM airspace_borders 
            WHERE airspace_id = ? 
            ORDER BY id
        """, (airspace_id,))
        
        borders = cursor.fetchall()
        geometry_data = []
        
        for border in borders:
            border_dict = dict(border)
            
            if border_dict['is_circle']:
                # Handle circular boundaries
                geometry_data.append({
                    'type': 'circle',
                    'center_lat': border_dict['circle_center_lat'],
                    'center_lon': border_dict['circle_center_lon'],
                    'radius_km': border_dict['circle_radius_km']
                })
            else:
                # Get vertices for this border
                cursor.execute("""
                    SELECT * FROM border_vertices 
                    WHERE border_id = ? 
                    ORDER BY sequence_number
                """, (border_dict['id'],))
                
                vertices = [dict(row) for row in cursor.fetchall()]
                
                if vertices:
                    geometry_data.append({
                        'type': 'polygon',
                        'vertices': vertices
                    })
        
        conn.close()
        return geometry_data

    def _convert_altitude_to_meters(self, altitude: Optional[int], unit: Optional[str]) -> Optional[float]:
        """Convert altitude to meters based on unit"""
        if altitude is None or unit is None:
            return None
            
        if unit.upper() == 'FT':
            return altitude * 0.3048  # feet to meters
        elif unit.upper() == 'M':
            return float(altitude)
        elif unit.upper() == 'FL':
            return altitude * 100 * 0.3048  # flight level (hundreds of feet) to meters
        else:
            # Default to feet if unknown unit
            return altitude * 0.3048

    def _generate_circle_coordinates(self, center_lat: float, center_lon: float, 
                                   radius_km: float, num_points: int = 36) -> List[Tuple[float, float]]:
        """Generate coordinates for a circle"""
        coordinates = []
        earth_radius = 6371  # km
        
        for i in range(num_points + 1):  # +1 to close the polygon
            angle = 2 * math.pi * i / num_points
            
            # Calculate new lat/lon using spherical geometry
            lat_rad = math.radians(center_lat)
            lon_rad = math.radians(center_lon)
            
            # Bearing calculation
            new_lat_rad = math.asin(
                math.sin(lat_rad) * math.cos(radius_km / earth_radius) +
                math.cos(lat_rad) * math.sin(radius_km / earth_radius) * math.cos(angle)
            )
            
            new_lon_rad = lon_rad + math.atan2(
                math.sin(angle) * math.sin(radius_km / earth_radius) * math.cos(lat_rad),
                math.cos(radius_km / earth_radius) - math.sin(lat_rad) * math.sin(new_lat_rad)
            )
            
            coordinates.append((math.degrees(new_lat_rad), math.degrees(new_lon_rad)))
        
        return coordinates

    def _create_vertical_walls(self, coordinates: List[Tuple[float, float]], 
                             min_altitude_m: float, max_altitude_m: float) -> List[ET.Element]:
        """Create vertical wall polygons connecting top and bottom surfaces"""
        walls = []
        
        for i in range(len(coordinates) - 1):  # -1 because last coordinate equals first
            # Get two consecutive points
            lat1, lon1 = coordinates[i]
            lat2, lon2 = coordinates[i + 1]
            
            # Create a wall polygon (rectangular face between two consecutive edge points)
            wall_polygon = ET.Element('Polygon')
            wall_altitude_mode = ET.SubElement(wall_polygon, 'altitudeMode')
            wall_altitude_mode.text = 'absolute'
            
            wall_outer_boundary = ET.SubElement(wall_polygon, 'outerBoundaryIs')
            wall_linear_ring = ET.SubElement(wall_outer_boundary, 'LinearRing')
            wall_coord_elem = ET.SubElement(wall_linear_ring, 'coordinates')
            
            # Create wall coordinates (4 corners of rectangular wall)
            # Bottom-left, Bottom-right, Top-right, Top-left, Bottom-left (to close)
            wall_coords = [
                f"{lon1},{lat1},{min_altitude_m}",  # Bottom-left
                f"{lon2},{lat2},{min_altitude_m}",  # Bottom-right  
                f"{lon2},{lat2},{max_altitude_m}",  # Top-right
                f"{lon1},{lat1},{max_altitude_m}",  # Top-left
                f"{lon1},{lat1},{min_altitude_m}"   # Close the polygon
            ]
            
            wall_coord_elem.text = ' '.join(wall_coords)
            walls.append(wall_polygon)
            
        return walls

    def _create_kml_polygon(self, coordinates: List[Tuple[float, float]], 
                           min_altitude_m: Optional[float], max_altitude_m: Optional[float],
                           name: str, description: str, 
                           airspace_type: str = None, airspace_class: str = None) -> ET.Element:
        """Create a KML polygon element with altitude extrusion"""
        
        # Create Placemark
        placemark = ET.Element('Placemark')
        
        # Add name
        name_elem = ET.SubElement(placemark, 'name')
        name_elem.text = name
        
        # Add description
        desc_elem = ET.SubElement(placemark, 'description')
        desc_elem.text = description
        
        # Create Polygon or MultiGeometry for proper 3D volume representation
        if (min_altitude_m is not None and max_altitude_m is not None and 
            max_altitude_m > min_altitude_m):
            # Create MultiGeometry with top and bottom surfaces plus vertical walls for elevated airspace
            multigeometry = ET.SubElement(placemark, 'MultiGeometry')
            
            # Top surface at max altitude
            top_polygon = ET.SubElement(multigeometry, 'Polygon')
            top_altitude_mode = ET.SubElement(top_polygon, 'altitudeMode')
            top_altitude_mode.text = 'absolute'
            top_outer_boundary = ET.SubElement(top_polygon, 'outerBoundaryIs')
            top_linear_ring = ET.SubElement(top_outer_boundary, 'LinearRing')
            top_coord_elem = ET.SubElement(top_linear_ring, 'coordinates')
            top_coord_text = []
            for lat, lon in coordinates:
                top_coord_text.append(f"{lon},{lat},{max_altitude_m}")
            top_coord_elem.text = ' '.join(top_coord_text)
            
            # Bottom surface at min altitude  
            bottom_polygon = ET.SubElement(multigeometry, 'Polygon')
            bottom_altitude_mode = ET.SubElement(bottom_polygon, 'altitudeMode')
            bottom_altitude_mode.text = 'absolute'
            bottom_outer_boundary = ET.SubElement(bottom_polygon, 'outerBoundaryIs')
            bottom_linear_ring = ET.SubElement(bottom_outer_boundary, 'LinearRing')
            bottom_coord_elem = ET.SubElement(bottom_linear_ring, 'coordinates')
            bottom_coord_text = []
            # Reverse coordinate order for bottom surface (proper winding)
            for lat, lon in reversed(coordinates):
                bottom_coord_text.append(f"{lon},{lat},{min_altitude_m}")
            bottom_coord_elem.text = ' '.join(bottom_coord_text)
            
            # Add vertical walls connecting top and bottom surfaces
            wall_polygons = self._create_vertical_walls(coordinates, min_altitude_m, max_altitude_m)
            for wall in wall_polygons:
                multigeometry.append(wall)
            
        else:
            # Use traditional extrusion for ground-based or single-altitude airspaces
            polygon = ET.SubElement(placemark, 'Polygon')
            
            # Set altitude mode and extrusion
            altitude_mode = ET.SubElement(polygon, 'altitudeMode')
            altitude_mode.text = 'absolute'
            
            # Enable extrusion if we have a maximum altitude
            if max_altitude_m is not None and max_altitude_m > 0:
                extrude = ET.SubElement(polygon, 'extrude')
                extrude.text = '1'
            
            # Create outer boundary
            outer_boundary = ET.SubElement(polygon, 'outerBoundaryIs')
            linear_ring = ET.SubElement(outer_boundary, 'LinearRing')
            
            # Add coordinates - use max altitude for extrusion, or min altitude if no max
            coord_elem = ET.SubElement(linear_ring, 'coordinates')
            coord_text = []
            
            # Determine the altitude to use for coordinates
            if max_altitude_m is not None and max_altitude_m > 0:
                coordinate_altitude = max_altitude_m
            elif min_altitude_m is not None:
                coordinate_altitude = min_altitude_m
            else:
                coordinate_altitude = 0.0
            
            for lat, lon in coordinates:
                coord_text.append(f"{lon},{lat},{coordinate_altitude}")
            
            coord_elem.text = ' '.join(coord_text)
        
        # Add style for visualization using color configuration
        fill_color = get_airspace_color(airspace_type, airspace_class)
        line_color = get_line_color(fill_color)
        
        style = ET.SubElement(placemark, 'Style')
        poly_style = ET.SubElement(style, 'PolyStyle')
        
        color_elem = ET.SubElement(poly_style, 'color')
        color_elem.text = fill_color
        
        fill_elem = ET.SubElement(poly_style, 'fill')
        fill_elem.text = '1'
        
        outline_elem = ET.SubElement(poly_style, 'outline')
        outline_elem.text = '1'
        
        line_style = ET.SubElement(style, 'LineStyle')
        line_color_elem = ET.SubElement(line_style, 'color')
        line_color_elem.text = line_color
        line_width_elem = ET.SubElement(line_style, 'width')
        line_width_elem.text = str(LINE_WIDTH)
        
        return placemark

    def generate_airspace_kml(self, airspace_id: int) -> str:
        """Generate KML for a specific airspace"""
        # Get airspace details with altitude information
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.*, 
                   vl.lower_limit_ft, vl.upper_limit_ft, 
                   vl.lower_limit_ref, vl.upper_limit_ref, vl.unit_of_measure
            FROM airspaces a
            LEFT JOIN vertical_limits vl ON a.id = vl.airspace_id
            WHERE a.id = ?
        """, (airspace_id,))
        airspace_row = cursor.fetchone()
        
        if not airspace_row:
            raise ValueError(f"Airspace with ID {airspace_id} not found")
        
        airspace = dict(airspace_row)
        conn.close()
        
        # Convert altitudes to meters for coordinates
        min_altitude_m = self._convert_altitude_to_meters(
            airspace.get('lower_limit_ft'), 
            airspace.get('lower_limit_ref')
        )
        max_altitude_m = self._convert_altitude_to_meters(
            airspace.get('upper_limit_ft'), 
            airspace.get('upper_limit_ref')
        )
        
        # Create readable altitude strings for display
        min_alt_display = "Surface"
        max_alt_display = "Unlimited"
        
        if airspace.get('lower_limit_ft') is not None:
            if airspace.get('lower_limit_ref') == 'FL':
                min_alt_display = f"{airspace.get('lower_limit_ft') * 100} FT (FL{airspace.get('lower_limit_ft')})"
            else:
                min_alt_display = f"{airspace.get('lower_limit_ft')} {airspace.get('lower_limit_ref', 'FT')}"
        
        if airspace.get('upper_limit_ft') is not None:
            if airspace.get('upper_limit_ref') == 'FL':
                max_alt_display = f"{airspace.get('upper_limit_ft') * 100} FT (FL{airspace.get('upper_limit_ft')})"
            else:
                max_alt_display = f"{airspace.get('upper_limit_ft')} {airspace.get('upper_limit_ref', 'FT')}"
        
        # Get geometry
        geometry_data = self._get_airspace_geometry(airspace_id)
        
        if not geometry_data:
            raise ValueError(f"No geometry found for airspace {airspace_id}")
        
        # Create KML document
        kml = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        document = ET.SubElement(kml, 'Document')
        
        # Add document name and description
        doc_name = ET.SubElement(document, 'name')
        doc_name.text = f"Airspace: {airspace.get('name', 'Unknown')}"
        
        doc_desc = ET.SubElement(document, 'description')
        doc_desc.text = f"""
        Airspace Volume: {airspace.get('name', 'Unknown')}
        Class: {airspace.get('airspace_class', 'Unknown')}
        Type: {airspace.get('code_type', 'Unknown')}
        Min Altitude: {min_alt_display}
        Max Altitude: {max_alt_display}
        """
        
        # Process each geometry component
        for i, geom in enumerate(geometry_data):
            if geom['type'] == 'circle':
                coordinates = self._generate_circle_coordinates(
                    geom['center_lat'], 
                    geom['center_lon'], 
                    geom['radius_km']
                )
                
                # Create description with altitude info
                description = f"""Circular boundary with radius {geom['radius_km']} km
3D Volume: {min_alt_display} to {max_alt_display}
Altitude range: {min_alt_display} - {max_alt_display} AMSL"""
                
                # Create name with type and class info
                name_parts = [airspace.get('name', 'Unknown')]
                if airspace.get('code_type'):
                    name_parts.append(f"({airspace.get('code_type')})")
                if airspace.get('airspace_class') and airspace.get('airspace_class') != 'UNKNOWN':
                    name_parts.append(f"Class {airspace.get('airspace_class')}")
                placemark_name = " ".join(name_parts)
                
                placemark = self._create_kml_polygon(
                    coordinates, 
                    min_altitude_m, 
                    max_altitude_m,
                    placemark_name,
                    description,
                    airspace.get('code_type'),
                    airspace.get('airspace_class')
                )
                
                document.append(placemark)
                
            elif geom['type'] == 'polygon' and geom.get('vertices'):
                coordinates = []
                longitudes = []
                latitudes = []
                
                for vertex in geom['vertices']:
                    lat, lon = vertex['latitude'], vertex['longitude']
                    coordinates.append((lat, lon))
                    longitudes.append(lon)
                    latitudes.append(lat)
                
                # Initialize geometry note
                geometry_note = ""
                
                # Validate geometry - check for suspicious outliers
                if len(longitudes) > 3:
                    import statistics
                    lon_median = statistics.median(longitudes)
                    lat_median = statistics.median(latitudes)
                    
                    # Flag vertices that are more than 1 degree from median
                    outliers = []
                    filtered_coords = []
                    for i, (lat, lon) in enumerate(coordinates):
                        if abs(lon - lon_median) > 1.0 or abs(lat - lat_median) > 0.5:
                            outliers.append(f"({lon:.3f}, {lat:.3f})")
                        else:
                            filtered_coords.append((lat, lon))
                    
                    # If we have significant outliers, mention it in description
                    if outliers and len(filtered_coords) >= 3:
                        geometry_note = f"\nNote: {len(outliers)} outlier vertices excluded from geometry"
                        coordinates = filtered_coords  # Use filtered coordinates
                    elif outliers:
                        geometry_note = f"\nWarning: Geometry contains {len(outliers)} suspicious vertices"
                
                # Close the polygon if not already closed
                if coordinates and coordinates[0] != coordinates[-1]:
                    coordinates.append(coordinates[0])
                
                # Create description with altitude info
                description = f"""Polygon boundary with {len(coordinates)-1} vertices
3D Volume: {min_alt_display} to {max_alt_display}
Altitude range: {min_alt_display} - {max_alt_display} AMSL{geometry_note}"""
                
                # Create name with type and class info
                name_parts = [airspace.get('name', 'Unknown')]
                if airspace.get('code_type'):
                    name_parts.append(f"({airspace.get('code_type')})")
                if airspace.get('airspace_class') and airspace.get('airspace_class') != 'UNKNOWN':
                    name_parts.append(f"Class {airspace.get('airspace_class')}")
                placemark_name = " ".join(name_parts)
                
                placemark = self._create_kml_polygon(
                    coordinates, 
                    min_altitude_m, 
                    max_altitude_m,
                    placemark_name,
                    description,
                    airspace.get('code_type'),
                    airspace.get('airspace_class')
                )
                
                document.append(placemark)
        
        # Convert to string
        ET.indent(kml, space="  ")
        return ET.tostring(kml, encoding='unicode')

    def generate_multiple_airspaces_kml(self, airspace_ids: List[int], flight_name: str = None, 
                                      flight_coordinates: List[tuple] = None,
                                      flight_waypoints: List[tuple] = None, 
                                      show_intermediate_points: bool = False) -> str:
        """Generate KML for multiple airspaces organized by type into folders
        
        Args:
            airspace_ids: List of airspace IDs to include
            flight_name: Name of the flight path for document title
            flight_coordinates: List of (lon, lat, alt_ft) tuples for original flight path
            flight_waypoints: List of (name, lon, lat, alt_ft) tuples for waypoint names
            show_intermediate_points: Whether to show intermediate climb/descent points
        """
        # Create KML document
        kml = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        document = ET.SubElement(kml, 'Document')
        
        # Add document name - use flight name if provided
        doc_name = ET.SubElement(document, 'name')
        if flight_name:
            doc_name.text = f"{flight_name} - Airspace Profile ({len(airspace_ids)} airspaces)"
        else:
            doc_name.text = f"Multiple Airspaces ({len(airspace_ids)} airspaces)"
        
        # Group airspaces by type
        airspaces_by_type = {}
        
        # Get airspace details to group by type
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        for airspace_id in airspace_ids:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM airspaces WHERE id = ?", (airspace_id,))
            row = cursor.fetchone()
            
            if row:
                airspace_type = row['code_type'].upper() if row['code_type'] else 'OTHER'
                if airspace_type not in airspaces_by_type:
                    airspaces_by_type[airspace_type] = []
                airspaces_by_type[airspace_type].append({
                    'id': airspace_id,
                    'name': row['name'] if row['name'] else 'Unknown',
                    'type': airspace_type,
                    'class': row['airspace_class'] if row['airspace_class'] else 'UNKNOWN'
                })
        
        conn.close()
        
        # Create KML folders for each airspace type
        type_order = ['CTR', 'TMA', 'RAS', 'R', 'D', 'P', 'SECTOR', 'FIR', 'OTHER']
        
        for airspace_type in type_order:
            if airspace_type not in airspaces_by_type:
                continue
                
            airspaces = airspaces_by_type[airspace_type]
            
            # Create folder for this type
            folder = ET.SubElement(document, 'Folder')
            
            # Folder name with emoji and count
            folder_name = ET.SubElement(folder, 'name')
            type_emoji = {
                'CTR': '🏢', 'TMA': '🛬', 'RAS': '📡', 'R': '⛔', 
                'D': '🚫', 'P': '🔒', 'SECTOR': '📶', 'FIR': '🌍', 'OTHER': '❓'
            }
            emoji = type_emoji.get(airspace_type, '❓')
            folder_name.text = f"{emoji} {airspace_type} ({len(airspaces)} airspaces)"
            
            # Folder description
            folder_desc = ET.SubElement(folder, 'description')
            folder_desc.text = f"{airspace_type} airspaces encountered along flight path"
            
            # Add each airspace to this folder
            for airspace in airspaces:
                try:
                    single_kml_str = self.generate_airspace_kml(airspace['id'])
                    single_kml = ET.fromstring(single_kml_str)
                    
                    # Extract placemarks from single KML
                    single_doc = single_kml.find('.//{http://www.opengis.net/kml/2.2}Document')
                    if single_doc is not None:
                        for placemark in single_doc.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
                            folder.append(placemark)
                            
                except Exception as e:
                    print(f"Warning: Failed to generate KML for airspace {airspace['id']} ({airspace['name']}): {e}")
                    continue
        
        # Add flight path at the top level if coordinates are provided
        if flight_coordinates or flight_waypoints:
            # Determine which data to use for the flight path
            if flight_waypoints:
                # Use waypoints (corrected profile) - extract coordinates from waypoints
                waypoints_to_use = flight_waypoints
                coords_to_use = [(lon, lat, alt_ft) for name, lon, lat, alt_ft in flight_waypoints]
            else:
                # Fall back to coordinates (original profile)
                waypoints_to_use = [(f"WP{i+1:02d}", lon, lat, alt_ft) for i, (lon, lat, alt_ft) in enumerate(flight_coordinates)]
                coords_to_use = flight_coordinates
            
            # Filter intermediate climb/descent points if requested
            if not show_intermediate_points and waypoints_to_use:
                filtered_waypoints = []
                filtered_coords = []
                for i, (name, lon, lat, alt_ft) in enumerate(waypoints_to_use):
                    # Hide intermediate climb/descent points (those starting with "Climb_" or "Descent_")
                    if not (name.startswith("Climb_") or name.startswith("Descent_")):
                        filtered_waypoints.append((name, lon, lat, alt_ft))
                    # Always include coordinates in the flight path line (even for intermediate points)
                    # This ensures the flight path line includes all corrected altitude points
                waypoints_to_use = filtered_waypoints
                # coords_to_use remains unchanged to preserve complete flight path with intermediate points
            
            self._add_flight_path_to_kml(document, coords_to_use, flight_name or "Flight Path", waypoints_to_use)
        
        # Convert to string
        ET.indent(kml, space="  ")
        return ET.tostring(kml, encoding='unicode')

    def _add_flight_path_to_kml(self, document: ET.Element, flight_coordinates: List[tuple], 
                              flight_name: str, flight_waypoints: List[tuple] = None):
        """Add flight path LineString and waypoints to KML document with corrected KML styling
        
        Args:
            flight_coordinates: List of (lon, lat, alt_ft) tuples for route line
            flight_waypoints: List of (name, lon, lat, alt_ft) tuples for waypoint names
        """
        
        # Add styles first (yellow line and waypoint styles)
        self._add_flight_path_styles(document)
        
        # Create flight path folder
        flight_folder = ET.SubElement(document, 'Folder')
        folder_name = ET.SubElement(flight_folder, 'name')
        folder_name.text = f"✈️ {flight_name} Route"
        folder_desc = ET.SubElement(flight_folder, 'description')
        folder_desc.text = f"Flight route with {len(flight_coordinates)} waypoints"
        
        # Create flight path placemark (yellow line)
        placemark = ET.SubElement(flight_folder, 'Placemark')
        
        # Name
        name = ET.SubElement(placemark, 'name')
        name.text = flight_name
        
        # Description
        desc = ET.SubElement(placemark, 'description')
        desc.text = "Flight route"
        
        # Use yellow line style
        style_url = ET.SubElement(placemark, 'styleUrl')
        style_url.text = "#msn_ylw-line"
        
        # Create LineString geometry
        linestring = ET.SubElement(placemark, 'LineString')
        extrude = ET.SubElement(linestring, 'extrude')
        extrude.text = "1"
        tessellate = ET.SubElement(linestring, 'tessellate')
        tessellate.text = "1"
        altitude_mode = ET.SubElement(linestring, 'altitudeMode')
        altitude_mode.text = "absolute"
        
        # Build coordinates string: lon,lat,alt_meters 
        coordinates = ET.SubElement(linestring, 'coordinates')
        coord_strings = []
        for lon, lat, alt_ft in flight_coordinates:
            # Convert altitude from feet to meters for KML
            alt_m = alt_ft / 3.28084
            coord_strings.append(f"{lon},{lat},{alt_m}")
        
        coordinates.text = " ".join(coord_strings)
        
        # Add waypoint placemarks
        waypoints_to_display = flight_waypoints if flight_waypoints else [(f"WP{i+1:02d}", lon, lat, alt_ft) for i, (lon, lat, alt_ft) in enumerate(flight_coordinates)]
        
        for name, lon, lat, alt_ft in waypoints_to_display:
            waypoint_placemark = ET.SubElement(flight_folder, 'Placemark')
            
            # Use the actual waypoint name from corrected profile
            wp_name = ET.SubElement(waypoint_placemark, 'name')
            wp_name.text = name
            
            wp_desc = ET.SubElement(waypoint_placemark, 'description')
            wp_desc.text = f"{name} - {int(alt_ft)} ft"
            
            # Use yellow pushpin style
            wp_style_url = ET.SubElement(waypoint_placemark, 'styleUrl')
            wp_style_url.text = "#msn_ylw-pushpin"
            
            # Create Point geometry
            point = ET.SubElement(waypoint_placemark, 'Point')
            point_extrude = ET.SubElement(point, 'extrude')
            point_extrude.text = "1"
            point_alt_mode = ET.SubElement(point, 'altitudeMode')
            point_alt_mode.text = "absolute"
            
            point_coords = ET.SubElement(point, 'coordinates')
            alt_m = alt_ft / 3.28084
            point_coords.text = f"{lon},{lat},{alt_m}"
    
    def _add_flight_path_styles(self, document: ET.Element):
        """Add yellow line and pushpin styles for flight path"""
        # Yellow line style
        line_style = ET.SubElement(document, 'Style', id="msn_ylw-line")
        line_style_line = ET.SubElement(line_style, 'LineStyle')
        line_color = ET.SubElement(line_style_line, 'color')
        line_color.text = "ff00ffff"  # Yellow in KML AABBGGRR format
        line_width = ET.SubElement(line_style_line, 'width')
        line_width.text = "3"
        
        # Yellow pushpin style  
        pushpin_style = ET.SubElement(document, 'Style', id="msn_ylw-pushpin")
        pushpin_icon_style = ET.SubElement(pushpin_style, 'IconStyle')
        pushpin_scale = ET.SubElement(pushpin_icon_style, 'scale')
        pushpin_scale.text = "1.1"
        pushpin_icon = ET.SubElement(pushpin_icon_style, 'Icon')
        pushpin_href = ET.SubElement(pushpin_icon, 'href')
        pushpin_href.text = "http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png"
        pushpin_hotspot = ET.SubElement(pushpin_icon_style, 'hotSpot', x="20", y="2", xunits="pixels", yunits="pixels")

    def save_airspace_kml(self, airspace_id: int, output_path: str) -> str:
        """Generate and save KML file for an airspace"""
        kml_content = self.generate_airspace_kml(airspace_id)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(kml_content)
        
        return output_path

    def get_airspace_by_name(self, name_pattern: str) -> List[Dict]:
        """Get airspace details by name pattern"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Prioritize airspaces with known classes over UNKNOWN classes
        # This helps avoid duplicates where same airspace exists with and without class info
        cursor.execute("""
            SELECT a.*, 
                   vl.lower_limit_ft, vl.upper_limit_ft, 
                   vl.lower_limit_ref, vl.upper_limit_ref, vl.unit_of_measure
            FROM airspaces a
            LEFT JOIN vertical_limits vl ON a.id = vl.airspace_id
            WHERE a.name LIKE ? 
            ORDER BY 
                CASE WHEN a.airspace_class = 'UNKNOWN' OR a.airspace_class IS NULL THEN 1 ELSE 0 END,
                a.name, vl.lower_limit_ft, vl.upper_limit_ft
        """, (f'%{name_pattern}%',))
        
        results = [dict(row) for row in cursor.fetchall()]
        
        # Remove duplicates: if we have same name+type with different classes, 
        # keep only the one with known class
        filtered_results = []
        seen_combinations = set()
        
        for result in results:
            key = (result.get('name'), result.get('code_type'), 
                   result.get('lower_limit_ft'), result.get('upper_limit_ft'))
            
            if key not in seen_combinations:
                filtered_results.append(result)
                seen_combinations.add(key)
        
        conn.close()
        return filtered_results