#!/usr/bin/env python3
"""
KML Profile Corrector
Redesigned profile correction logic that works on any KML file without specific workarounds.

Logic:
- A branch is between 2 consecutive points in the KML
- Target altitude for each branch is the altitude of the first point (branch entry altitude)
- Departure/arrival altitude = field elevation + 1000 ft
- Calculate climb/descent needs based on altitude differences
- Create endOfClimb/endOfDescent points using configurable climb/descent rates (default 500 fpm)
"""

import xml.etree.ElementTree as ET
import re
import math
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from aviation_utils import UnitConverter, ElevationAPI, extract_airport_coordinates_from_kml


@dataclass
class KMLPoint:
    """Represents a navigation point with coordinates and metadata"""
    name: str
    longitude: float
    latitude: float
    altitude: float
    ground_elevation: Optional[float] = None
    
    def __str__(self):
        return f"{self.name} ({self.longitude:.6f}, {self.latitude:.6f}) @ {UnitConverter.format_altitude(self.altitude)}"


@dataclass
class Branch:
    """Represents a branch between two consecutive KML points"""
    start_point: KMLPoint
    end_point: KMLPoint
    target_altitude: float  # Target altitude for this branch (altitude of start point)
    distance_nm: float
    action: str  # "CLIMB", "DESCENT", or "LEVEL"
    altitude_change_ft: float
    end_of_action_point: Optional[Tuple[float, float, float]] = None  # (lon, lat, alt) if climb/descent needed
    is_unreachable: bool = False  # Flag for unreachable altitude
    unreachable_reason: str = ""  # Reason why unreachable
    
    def __str__(self):
        action_desc = ""
        if self.action == "CLIMB":
            # Calculate starting altitude for this branch
            if hasattr(self, '_start_altitude_ft'):
                start_alt_ft = self._start_altitude_ft
            else:
                start_alt_ft = UnitConverter.meters_to_feet(self.target_altitude) - self.altitude_change_ft
            target_alt_ft = UnitConverter.meters_to_feet(self.target_altitude)
            action_desc = f"CLIMB from {start_alt_ft:.0f} ft to {target_alt_ft:.0f} ft ({self.altitude_change_ft:+.0f} ft)"
        elif self.action == "DESCENT":
            # Calculate starting altitude for this branch
            if hasattr(self, '_start_altitude_ft'):
                start_alt_ft = self._start_altitude_ft
            else:
                start_alt_ft = UnitConverter.meters_to_feet(self.target_altitude) - self.altitude_change_ft
            target_alt_ft = UnitConverter.meters_to_feet(self.target_altitude)
            action_desc = f"DESCENT from {start_alt_ft:.0f} ft to {target_alt_ft:.0f} ft ({self.altitude_change_ft:+.0f} ft)"
        else:
            action_desc = f"LEVEL at {UnitConverter.meters_to_feet(self.target_altitude):.0f} ft"
        
        # Add warning if unreachable
        if self.is_unreachable:
            action_desc += f" ⚠️ UNREACHABLE: {self.unreachable_reason}"
            
        return f"{self.start_point.name} → {self.end_point.name}: {action_desc} ({self.distance_nm:.1f} NM)"


class KMLProfileCorrector:
    """KML profile corrector that works on any KML file"""
    
    def __init__(self, climb_rate_fpm: float = 500, descent_rate_fpm: float = 500, 
                 ground_speed_kts: float = 100, api_key: Optional[str] = None):
        """
        Initialize the profile corrector
        
        Args:
            climb_rate_fpm: Climb rate in feet per minute
            descent_rate_fpm: Descent rate in feet per minute  
            ground_speed_kts: Ground speed in knots for time calculations
            api_key: Optional API key for elevation services
        """
        self.climb_rate_fpm = climb_rate_fpm
        self.descent_rate_fpm = descent_rate_fpm
        self.ground_speed_kts = ground_speed_kts
        self.elevation_api = ElevationAPI()
        self.api_key = api_key
        
    def calculate_distance_nm(self, p1: KMLPoint, p2: KMLPoint) -> float:
        """Calculate great circle distance between two points in nautical miles"""
        lat1, lon1 = math.radians(p1.latitude), math.radians(p1.longitude)
        lat2, lon2 = math.radians(p2.latitude), math.radians(p2.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in km, then convert to NM
        R_km = 6371.0
        distance_km = R_km * c
        return UnitConverter.km_to_nautical_miles(distance_km)
    
    def interpolate_point(self, p1: KMLPoint, p2: KMLPoint, fraction: float) -> Tuple[float, float]:
        """Interpolate a geographic position between two points"""
        lon = p1.longitude + (p2.longitude - p1.longitude) * fraction
        lat = p1.latitude + (p2.latitude - p1.latitude) * fraction
        return lon, lat
    
    def parse_kml(self, kml_file: str) -> Tuple[List[KMLPoint], str]:
        """Parse KML file and extract navigation points"""
        # Read original file content first
        with open(kml_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        try:
            tree = ET.parse(kml_file)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"Warning: XML parsing error: {e}")
            print("Attempting to parse with namespace handling...")
            # Try to parse with explicit namespace registration
            try:
                ET.register_namespace('gx', 'http://www.google.com/kml/ext/2.2')
                tree = ET.parse(kml_file)
                root = tree.getroot()
            except ET.ParseError as e2:
                print(f"Failed to parse KML file: {e2}")
                return [], original_content
        
        namespaces = {
            'kml': 'http://www.opengis.net/kml/2.2',
            'gx': 'http://www.google.com/kml/ext/2.2'
        }
        points = []
        
        # Extract main navigation line coordinates
        navigation_coords = None
        for linestring in root.findall('.//kml:LineString', namespaces):
            coords_elem = linestring.find('kml:coordinates', namespaces)
            if coords_elem is not None:
                navigation_coords = coords_elem.text.strip()
                break
        
        if navigation_coords:
            # Parse navigation line coordinates  
            coords_list = navigation_coords.split(',')
            for i in range(0, len(coords_list), 3):
                if i + 2 < len(coords_list):
                    try:
                        lon = float(coords_list[i])
                        lat = float(coords_list[i + 1])
                        alt = float(coords_list[i + 2])
                        points.append(KMLPoint(f"Point_{i//3}", lon, lat, alt))
                    except ValueError:
                        continue
        
        # Get point names from Placemarks
        placemark_names = []
        for placemark in root.findall('.//kml:Placemark', namespaces):
            name_elem = placemark.find('kml:name', namespaces)
            if name_elem is not None and name_elem.text != "Navigation":
                placemark_names.append(name_elem.text)
        
        # Associate names with points
        for i, point in enumerate(points):
            if i < len(placemark_names):
                point.name = placemark_names[i]
        
        return points, original_content
    
    def get_ground_elevations(self, points: List[KMLPoint], original_content: str) -> Dict[str, float]:
        """Get ground elevations for departure/destination airports (first and last points only)"""
        if len(points) < 2:
            return {}
        
        # Only get elevation for departure (first) and destination (last) points
        departure_point = points[0]
        destination_point = points[-1]
        
        coords = {
            departure_point.name: (departure_point.latitude, departure_point.longitude),
            destination_point.name: (destination_point.latitude, destination_point.longitude)
        }
        
        print(f"Departure airfield: {departure_point.name}")
        print(f"Destination airfield: {destination_point.name}")
        
        return self.elevation_api.get_elevation_for_airports(coords, self.api_key)
    
    def analyze_branches(self, points: List[KMLPoint], ground_elevations: Dict[str, float]) -> List[Branch]:
        """
        Analyze branches between consecutive points and determine required actions
        
        Key logic:
        - Branch target altitude = altitude of first point (branch entry altitude)  
        - Departure altitude = field elevation + 1000 ft
        - Arrival altitude = field elevation + 1000 ft
        - Compare current altitude vs target to determine climb/descent need
        """
        if len(points) < 2:
            return []
        
        branches = []
        
        # Set corrected altitudes for departure and arrival points
        # Departure point (first point): field elevation + 1000 ft
        departure_elevation = ground_elevations.get(points[0].name, UnitConverter.feet_to_meters(500))  # Default 500m if unknown
        departure_altitude = departure_elevation + UnitConverter.feet_to_meters(1000)
        
        # Arrival point (last point): field elevation + 1000 ft  
        arrival_elevation = ground_elevations.get(points[-1].name, UnitConverter.feet_to_meters(500))  # Default 500m if unknown
        arrival_altitude = arrival_elevation + UnitConverter.feet_to_meters(1000)
        
        # Track current altitude as we progress through the flight
        current_altitude = departure_altitude
        
        # Analyze each branch
        for i in range(len(points) - 1):
            start_point = points[i]
            end_point = points[i + 1]
            
            # Branch target altitude is the altitude of the first point (start_point's original altitude)
            target_altitude = start_point.altitude
            
            # For the last branch, target altitude is the arrival altitude (field elevation + 1000 ft)
            if i == len(points) - 2:  # Last branch
                target_altitude = arrival_altitude
            
            # Calculate distance
            distance_nm = self.calculate_distance_nm(start_point, end_point)
            
            # Determine action needed
            altitude_diff_ft = UnitConverter.meters_to_feet(target_altitude - current_altitude)
            
            if abs(altitude_diff_ft) < 50:  # Less than 50 ft difference - consider level
                action = "LEVEL"
                altitude_change_ft = 0
            elif altitude_diff_ft > 0:
                action = "CLIMB" 
                altitude_change_ft = altitude_diff_ft
            else:
                action = "DESCENT"
                altitude_change_ft = altitude_diff_ft
            
            # Create branch
            branch = Branch(
                start_point=start_point,
                end_point=end_point, 
                target_altitude=target_altitude,
                distance_nm=distance_nm,
                action=action,
                altitude_change_ft=altitude_change_ft
            )
            
            # Store starting altitude for display purposes
            branch._start_altitude_ft = UnitConverter.meters_to_feet(current_altitude)
            
            # Calculate end of climb/descent point if needed
            if action in ["CLIMB", "DESCENT"]:
                rate_fpm = self.climb_rate_fpm if action == "CLIMB" else self.descent_rate_fpm
                time_needed_min = abs(altitude_change_ft) / rate_fpm
                distance_needed_nm = (self.ground_speed_kts / 60) * time_needed_min
                
                # Check if altitude change is achievable within the branch distance
                if distance_needed_nm >= distance_nm:
                    # Unreachable - not enough distance
                    branch.is_unreachable = True
                    achievable_change_ft = (distance_nm / (self.ground_speed_kts / 60)) * rate_fpm
                    if action == "CLIMB":
                        achievable_altitude_ft = UnitConverter.meters_to_feet(current_altitude) + achievable_change_ft
                        branch.unreachable_reason = f"Need {distance_needed_nm:.1f} NM but only {distance_nm:.1f} NM available. Max achievable: {achievable_altitude_ft:.0f} ft"
                    else:
                        achievable_altitude_ft = UnitConverter.meters_to_feet(current_altitude) - achievable_change_ft
                        branch.unreachable_reason = f"Need {distance_needed_nm:.1f} NM but only {distance_nm:.1f} NM available. Max achievable: {achievable_altitude_ft:.0f} ft"
                else:
                    # Calculate position where climb/descent ends
                    fraction = distance_needed_nm / distance_nm
                    end_lon, end_lat = self.interpolate_point(start_point, end_point, fraction)
                    branch.end_of_action_point = (end_lon, end_lat, target_altitude)
            
            branches.append(branch)
            
            # Update current altitude for next branch
            current_altitude = target_altitude
        
        return branches
    
    def print_branch_analysis_table(self, branches: List[Branch]):
        """Print a table showing branch analysis and actions"""
        print(f"\n{'='*80}")
        print("BRANCH ANALYSIS TABLE")
        print(f"{'='*80}")
        print(f"{'Branch':<20} {'Distance':<10} {'Action':<50}")
        print("-" * 80)
        
        unreachable_count = 0
        for i, branch in enumerate(branches, 1):
            branch_name = f"Branch {i}"
            distance_str = f"{branch.distance_nm:.1f} NM"
            
            if branch.is_unreachable:
                unreachable_count += 1
            
            print(f"{branch_name:<20} {distance_str:<10} {branch}")
        
        print("-" * 80)
        print(f"Total branches: {len(branches)}")
        if unreachable_count > 0:
            print(f"⚠️  WARNING: {unreachable_count} branches have UNREACHABLE altitude targets!")
            print("   Consider adjusting climb/descent rates or reviewing the flight profile.")
        print(f"{'='*80}")
    
    def correct_kml_file(self, input_file: str, output_file: str):
        """Main function to correct a KML file with the profile correction algorithm"""
        print(f"Processing KML file: {input_file}")
        print(f"Using climb rate: {self.climb_rate_fpm} ft/min")
        print(f"Using descent rate: {self.descent_rate_fpm} ft/min")
        print(f"Using ground speed: {self.ground_speed_kts} kts")
        
        # Parse KML
        points, original_content = self.parse_kml(input_file)
        print(f"\nExtracted {len(points)} points from KML:")
        for point in points:
            print(f"  {point}")
        
        # Get ground elevations
        print("\nRetrieving ground elevations...")
        ground_elevations = self.get_ground_elevations(points, original_content)
        
        for name, elevation in ground_elevations.items():
            print(f"Ground elevation for {name}: {UnitConverter.format_altitude(elevation)}")
        
        # Analyze branches  
        print("\nAnalyzing branches...")
        branches = self.analyze_branches(points, ground_elevations)
        
        # Print analysis table
        self.print_branch_analysis_table(branches)
        
        # TODO: Generate corrected KML content (to be implemented)
        print(f"\nNote: KML generation not yet implemented in this redesign.")
        print(f"This is the profile analysis.")


def main():
    """Main function for testing the KML profile corrector"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='KML profile corrector - works on any KML file')
    parser.add_argument('input_file', help='Input KML file')
    parser.add_argument('-o', '--output', help='Output corrected KML file (default: input_file_corrected.kml)')
    parser.add_argument('--climb-rate', type=float, default=500, help='Climb rate in ft/min (default: 500)')
    parser.add_argument('--descent-rate', type=float, default=500, help='Descent rate in ft/min (default: 500)')
    parser.add_argument('--ground-speed', type=float, default=100, help='Ground speed in knots (default: 100)')
    parser.add_argument('--api-key', help='API key for elevation services (optional)')
    
    args = parser.parse_args()
    
    # Set default output file if not specified
    if not args.output:
        base_name = os.path.splitext(args.input_file)[0] 
        args.output = f"{base_name}_corrected.kml"
    
    # Create corrector and process file
    corrector = KMLProfileCorrector(
        climb_rate_fpm=args.climb_rate,
        descent_rate_fpm=args.descent_rate,
        ground_speed_kts=args.ground_speed,
        api_key=args.api_key
    )
    
    corrector.correct_kml_file(args.input_file, args.output)


if __name__ == "__main__":
    main()