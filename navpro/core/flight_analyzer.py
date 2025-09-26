#!/usr/bin/env python3
"""
Flight Profile Analysis Tool
Analyzes airspace crossings for KML flight paths with configurable corridor settings
"""
import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from core.query_engine import FixedAirspaceQueryEngine
from core.spatial_query import KMLFlightPathParser
from core.interpolation import interpolate_flight_path, haversine_distance
import math

class FlightProfileAnalyzer:
    def __init__(self, db_path: str, corridor_height_ft: int = 1000, corridor_width_nm: float = 10.0):
        """
        Initialize flight profile analyzer
        
        Args:
            db_path: Path to airspace database
            corridor_height_ft: Vertical corridor (+/- feet from flight altitude)
            corridor_width_nm: Horizontal corridor (nautical miles from flight path)
        """
        self.db_path = db_path
        self.corridor_height_ft = corridor_height_ft
        self.corridor_width_nm = corridor_width_nm
        self.corridor_width_km = corridor_width_nm * 1.852  # Convert NM to km
        
        self.engine = FixedAirspaceQueryEngine(db_path)
        
    def get_chronological_crossings(self, kml_path: str, sample_distance_km: float = 5.0) -> List[Dict]:
        """Get airspaces crossed chronologically along flight path with proper crossing detection"""
        # Parse flight path
        waypoints = KMLFlightPathParser.parse_kml_coordinates(kml_path)
        if not waypoints:
            raise ValueError(f"Failed to parse coordinates from {kml_path}")
        
        # Determine if this is a trace or route file and handle accordingly
        is_trace = KMLFlightPathParser.is_trace_file(kml_path)
        
        if is_trace:
            # For trace files, we already have dense data - thin it out for analysis
            sample_factor = max(1, len(waypoints) // 1000)  # Keep approximately 1000 points max
            if sample_factor > 1:
                sampled_waypoints = waypoints[::sample_factor]
                interpolated_points = sampled_waypoints
            else:
                interpolated_points = waypoints
        else:
            # For route files, interpolate between waypoints as before
            interpolated_points = interpolate_flight_path(waypoints, sample_distance_km)
        
        # Phase 1: Discovery - Use corridor to find all potentially relevant airspaces
        corridor_points = self._generate_corridor_points(interpolated_points)
        discovered_airspaces = {}
        
        # Test each corridor point to discover airspaces
        for i, (lon, lat, alt) in enumerate(corridor_points):
            airspaces = self.engine.query_airspaces_for_point(lon, lat, alt)
            for airspace in airspaces:
                airspace_id = airspace['id']
                if airspace_id not in discovered_airspaces:
                    discovered_airspaces[airspace_id] = airspace
        
        # Phase 2: Actual crossing detection - Check only nominal flight path
        first_crossings = {}
        
        # Test only the original flight path points (not corridor offsets)
        for i, (lon, lat, alt) in enumerate(interpolated_points):
            flight_progress = i / len(interpolated_points) if len(interpolated_points) > 1 else 0
            
            # Check which discovered airspaces are actually crossed by the nominal path
            airspaces = self.engine.query_airspaces_for_point(lon, lat, alt)
            
            # Record first encounter along nominal path
            for airspace in airspaces:
                airspace_id = airspace['id']
                if airspace_id not in first_crossings:
                    # Calculate approximate distance from start
                    if len(interpolated_points) > 1:
                        total_distance = self._calculate_total_distance([
                            (p[0], p[1], p[2]) for p in interpolated_points
                        ])
                        estimated_distance = total_distance * flight_progress
                    else:
                        estimated_distance = 0.0
                        
                    # Mark whether this is a nominal path crossing or just corridor-discovered
                    first_crossings[airspace_id] = {
                        'airspace': airspace,
                        'crossing_point': (lon, lat, alt),
                        'distance_km': estimated_distance,
                        'segment_index': i,
                        'is_actual_crossing': True  # This is from nominal path
                    }
        
        # Add corridor-only discoveries (not actual crossings) for completeness
        for airspace_id, airspace in discovered_airspaces.items():
            if airspace_id not in first_crossings:
                first_crossings[airspace_id] = {
                    'airspace': airspace,
                    'crossing_point': None,  # No actual crossing point
                    'distance_km': 0.0,  # Approximate
                    'segment_index': 999999,  # Sort to end
                    'is_actual_crossing': False  # Only discovered via corridor
                }
        
        # Sort by segment index to maintain chronological order
        crossings = list(first_crossings.values())
        crossings.sort(key=lambda x: x['segment_index'])
        
        return crossings
        
    def analyze_kml_flight(self, kml_path: str, sample_distance_km: float = 5.0) -> Dict:
        """Analyze a KML flight path for airspace crossings"""
        
        # Parse flight path
        waypoints = KMLFlightPathParser.parse_kml_coordinates(kml_path)
        if not waypoints:
            raise ValueError(f"Failed to parse coordinates from {kml_path}")
        
        # Determine if this is a trace or route file
        is_trace = KMLFlightPathParser.is_trace_file(kml_path)
        
        if is_trace:
            # For trace files, we already have dense data - thin it out for analysis
            print(f"Processing flight trace with {len(waypoints)} points")
            # Sample every Nth point to reduce processing time while maintaining accuracy
            sample_factor = max(1, len(waypoints) // 1000)  # Keep approximately 1000 points max
            if sample_factor > 1:
                sampled_waypoints = waypoints[::sample_factor]
                print(f"Sampled to {len(sampled_waypoints)} points (every {sample_factor} points)")
                interpolated_points = sampled_waypoints
            else:
                interpolated_points = waypoints
        else:
            # For route files, interpolate between waypoints as before
            print(f"Processing flight route with {len(waypoints)} waypoints")
            interpolated_points = interpolate_flight_path(waypoints, sample_distance_km)
        
        # Calculate flight statistics
        total_distance = self._calculate_total_distance(waypoints)
        altitudes = [alt for _, _, alt in interpolated_points]
        
        # Generate corridor points (flight path + surrounding area)
        corridor_points = self._generate_corridor_points(interpolated_points)
        
        print(f"Analyzing flight profile:")
        print(f"  Route: {len(waypoints)} waypoints, {len(interpolated_points)} interpolated points")
        print(f"  Distance: {total_distance:.1f} km")
        print(f"  Altitude: {min(altitudes):.0f}-{max(altitudes):.0f} ft (avg: {sum(altitudes)/len(altitudes):.0f} ft)")
        print(f"  Corridor: ±{self.corridor_height_ft} ft, ±{self.corridor_width_nm} NM")
        print(f"  Analyzing {len(corridor_points)} corridor points...")
        print()
        
        # Analyze airspaces
        crossed_airspaces = {}
        airspace_crossings = []
        
        for i, (lon, lat, alt_ft) in enumerate(corridor_points):
            if i % 50 == 0:
                print(f"  Processing point {i+1}/{len(corridor_points)}...")
            
            # Check altitude range within corridor
            min_alt = max(0, alt_ft - self.corridor_height_ft)
            max_alt = alt_ft + self.corridor_height_ft
            
            # Sample multiple altitudes in corridor
            test_altitudes = [min_alt, alt_ft, max_alt]
            if self.corridor_height_ft > 500:
                # Add intermediate altitudes for large corridors
                test_altitudes.extend([
                    alt_ft - self.corridor_height_ft // 2,
                    alt_ft + self.corridor_height_ft // 2
                ])
            
            for test_alt in test_altitudes:
                airspaces = self.engine.query_airspaces_for_point(lon, lat, test_alt)
                
                for airspace in airspaces:
                    airspace_id = airspace['id']
                    if airspace_id not in crossed_airspaces:
                        crossed_airspaces[airspace_id] = airspace
                    
                    airspace_crossings.append({
                        'point_index': i,
                        'coordinates': (lon, lat, alt_ft),
                        'test_altitude': test_alt,
                        'airspace': airspace
                    })
        
        # Categorize airspaces
        categorized_airspaces = self._categorize_airspaces(crossed_airspaces)
        
        # Generate report
        report = {
            'flight_info': {
                'kml_path': kml_path,
                'is_trace': is_trace,
                'waypoints': len(waypoints),
                'interpolated_points': len(interpolated_points),
                'corridor_points': len(corridor_points),
                'total_distance_km': total_distance,
                'altitude_range_ft': {
                    'min': min(altitudes),
                    'max': max(altitudes),
                    'avg': sum(altitudes) / len(altitudes)
                }
            },
            'corridor_settings': {
                'height_ft': self.corridor_height_ft,
                'width_nm': self.corridor_width_nm
            },
            'airspace_summary': {
                'total_unique_airspaces': len(crossed_airspaces),
                'total_crossings': len(airspace_crossings),
                'by_category': {category: len(airspaces) 
                               for category, airspaces in categorized_airspaces.items()}
            },
            'categorized_airspaces': categorized_airspaces
        }
        
        return report
    
    def _generate_corridor_points(self, flight_points: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
        """Generate points within the flight corridor"""
        corridor_points = []
        
        # Always include the original flight path
        corridor_points.extend(flight_points)
        
        # Add parallel tracks offset by corridor width
        if self.corridor_width_km > 0:
            # Generate offset points at regular intervals
            for i in range(len(flight_points) - 1):
                lon1, lat1, alt1 = flight_points[i]
                lon2, lat2, alt2 = flight_points[i + 1]
                
                # Calculate bearing of this segment
                bearing = self._calculate_bearing(lat1, lon1, lat2, lon2)
                
                # Generate perpendicular offsets
                offset_bearings = [bearing + 90, bearing - 90]  # Left and right
                
                for offset_bearing in offset_bearings:
                    # Offset by corridor width
                    offset_lat, offset_lon = self._offset_position(
                        lat1, lon1, offset_bearing, self.corridor_width_km
                    )
                    corridor_points.append((offset_lon, offset_lat, alt1))
        
        return corridor_points
    
    def _calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate bearing between two points in degrees"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlon_rad = math.radians(lon2 - lon1)
        
        y = math.sin(dlon_rad) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))
        
        bearing_rad = math.atan2(y, x)
        bearing_deg = math.degrees(bearing_rad)
        
        return (bearing_deg + 360) % 360
    
    def _offset_position(self, lat: float, lon: float, bearing: float, distance_km: float) -> Tuple[float, float]:
        """Calculate position offset by bearing and distance"""
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        bearing_rad = math.radians(bearing)
        
        # Earth radius in km
        R = 6371.0
        d_rad = distance_km / R
        
        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(d_rad) + 
            math.cos(lat_rad) * math.sin(d_rad) * math.cos(bearing_rad)
        )
        
        new_lon_rad = lon_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(d_rad) * math.cos(lat_rad),
            math.cos(d_rad) - math.sin(lat_rad) * math.sin(new_lat_rad)
        )
        
        return math.degrees(new_lat_rad), math.degrees(new_lon_rad)
    
    def _calculate_total_distance(self, waypoints: List[Tuple[float, float, float]]) -> float:
        """Calculate total flight distance in km"""
        total_distance = 0
        for i in range(len(waypoints) - 1):
            lat1, lon1, alt1 = waypoints[i][1], waypoints[i][0], waypoints[i][2]
            lat2, lon2, alt2 = waypoints[i+1][1], waypoints[i+1][0], waypoints[i+1][2]
            total_distance += haversine_distance(lat1, lon1, lat2, lon2)
        return total_distance
    
    def _categorize_airspaces(self, airspaces: Dict) -> Dict[str, List[Dict]]:
        """Categorize airspaces by type"""
        categories = {
            'TMAs': [],
            'RAS': [],  
            'Restricted': [],
            'Control_Zones': [],
            'Other': []
        }
        
        for airspace in airspaces.values():
            code_type = airspace.get('code_type', 'Unknown')
            
            if code_type == 'TMA':
                categories['TMAs'].append(airspace)
            elif code_type == 'RAS':
                categories['RAS'].append(airspace)
            elif code_type in ['R', 'P']:
                categories['Restricted'].append(airspace)
            elif code_type == 'CTR':
                categories['Control_Zones'].append(airspace)
            else:
                categories['Other'].append(airspace)
        
        # Sort each category by name
        for category in categories.values():
            category.sort(key=lambda x: x.get('name', ''))
        
        return categories
    
    def print_report(self, report: Dict):
        """Print a formatted report"""
        print("=" * 80)
        print("FLIGHT PROFILE ANALYSIS REPORT")
        print("=" * 80)
        
        # Flight info
        flight_info = report['flight_info']
        corridor = report['corridor_settings']
        
        print(f"Flight: {Path(flight_info['kml_path']).name}")
        print(f"Distance: {flight_info['total_distance_km']:.1f} km")
        print(f"Altitude: {flight_info['altitude_range_ft']['min']:.0f}-{flight_info['altitude_range_ft']['max']:.0f} ft")
        print(f"Corridor: ±{corridor['height_ft']} ft, ±{corridor['width_nm']} NM")
        print()
        
        # Summary
        summary = report['airspace_summary']
        print(f"SUMMARY:")
        print(f"  Total airspaces found: {summary['total_unique_airspaces']}")
        print(f"  Total crossing points: {summary['total_crossings']}")
        print()
        
        # By category
        categorized = report['categorized_airspaces']
        
        for category, airspaces in categorized.items():
            if not airspaces:
                continue
                
            print(f"{category.upper().replace('_', ' ')} ({len(airspaces)}):")
            print("-" * 50)
            
            for airspace in airspaces:
                lower_conv = airspace.get('lower_limit_ft_converted', 0)
                upper_conv = airspace.get('upper_limit_ft_converted', float('inf'))
                
                print(f"• {airspace['name']} ({airspace['code_id']})")
                print(f"  Type: {airspace.get('code_type', 'Unknown')} - Class: {airspace.get('airspace_class', 'Unknown')}")
                print(f"  Altitude: {lower_conv:.0f} - {upper_conv:.0f} ft")
            print()
    
    def save_report(self, report: Dict, output_path: str):
        """Save report to JSON file"""
        # Convert any non-serializable objects
        serializable_report = json.loads(json.dumps(report, default=str))
        
        with open(output_path, 'w') as f:
            json.dump(serializable_report, f, indent=2)
        
        print(f"Report saved to: {output_path}")
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.close()


def main():
    parser = argparse.ArgumentParser(description='Analyze flight profile for airspace crossings')
    parser.add_argument('command', choices=['analyze', 'list-settings'], help='Command to execute')
    parser.add_argument('kml_file', nargs='?', help='KML flight path file')
    parser.add_argument('--db', default='data/airspaces.db', help='Airspace database path')
    parser.add_argument('--corridor-height', type=int, default=1000, 
                       help='Vertical corridor height in feet (default: 1000)')
    parser.add_argument('--corridor-width', type=float, default=10.0,
                       help='Horizontal corridor width in nautical miles (default: 10.0)')
    parser.add_argument('--sample-distance', type=float, default=5.0,
                       help='Sample distance along path in km (default: 5.0)')
    parser.add_argument('--output', help='Output file for JSON report')
    parser.add_argument('--profile', action='store_true', help='Run flight profile analysis')
    
    args = parser.parse_args()
    
    if args.command == 'list-settings':
        print("Flight Profile Analysis Settings:")
        print("=" * 40)
        print(f"Default corridor height: {args.corridor_height} ft")
        print(f"Default corridor width: {args.corridor_width} NM")
        print(f"Default sample distance: {args.sample_distance} km")
        print(f"Database path: {args.db}")
        print()
        print("Usage examples:")
        print("  python flight_profile.py analyze flight.kml --profile")
        print("  python flight_profile.py analyze flight.kml --corridor-height 2000 --corridor-width 20")
        print("  python flight_profile.py analyze flight.kml --output report.json")
        return
    
    if args.command == 'analyze':
        if not args.kml_file:
            parser.error("KML file is required for analyze command")
        
        if not Path(args.kml_file).exists():
            print(f"Error: KML file not found: {args.kml_file}")
            return 1
        
        if not Path(args.db).exists():
            print(f"Error: Database not found: {args.db}")
            return 1
        
        # Initialize analyzer
        analyzer = FlightProfileAnalyzer(
            args.db, 
            corridor_height_ft=args.corridor_height,
            corridor_width_nm=args.corridor_width
        )
        
        try:
            # Analyze flight
            report = analyzer.analyze_kml_flight(args.kml_file, args.sample_distance)
            
            # Print report
            analyzer.print_report(report)
            
            # Save report if requested
            if args.output:
                analyzer.save_report(report, args.output)
            
        except Exception as e:
            print(f"Error analyzing flight: {e}")
            return 1
        finally:
            analyzer.close()
    
    return 0

if __name__ == "__main__":
    exit(main())