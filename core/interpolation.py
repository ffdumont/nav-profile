#!/usr/bin/env python3
"""
Enhanced flight path analyzer with interpolated points
"""
import math
from typing import List, Tuple
from core.spatial_query import AirspaceQueryEngine, KMLFlightPathParser

def interpolate_flight_path(coordinates: List[Tuple[float, float, float]], 
                          segment_distance_km: float = 5.0) -> List[Tuple[float, float, float]]:
    """
    Interpolate points along flight path segments with smart altitude constraint handling
    
    Args:
        coordinates: List of (lon, lat, alt_ft) waypoints
        segment_distance_km: Distance between interpolated points in kilometers
    
    Returns:
        List of interpolated (lon, lat, alt_ft) points
    """
    if len(coordinates) < 2:
        return coordinates
    
    interpolated_points = []
    
    for i in range(len(coordinates) - 1):
        lon1, lat1, alt1 = coordinates[i]
        lon2, lat2, alt2 = coordinates[i + 1]
        
        # Add the starting point
        interpolated_points.append((lon1, lat1, alt1))
        
        # Calculate distance between waypoints
        distance_km = haversine_distance(lat1, lon1, lat2, lon2)
        
        if distance_km <= segment_distance_km:
            # Segment is short enough, no interpolation needed
            continue
        
        # Calculate number of intermediate points needed
        num_segments = max(1, int(distance_km / segment_distance_km))
        
        # Smart altitude constraint detection
        altitude_profile = _determine_altitude_profile(alt1, alt2, i, coordinates)
        
        # Log altitude constraint detection for debugging
        if altitude_profile == 'constrained':
            print(f"[CONSTRAINT] Altitude constraint detected: {alt1:.0f} ft -> {alt2:.0f} ft (maintaining {alt1:.0f} ft for segment)")
        elif altitude_profile == 'stepped':
            print(f"[STEP CLIMB] Step climb detected: {alt1:.0f} ft -> {alt2:.0f} ft")
        
        # Interpolate points along the segment
        for j in range(1, num_segments):
            ratio = j / num_segments
            
            # Linear interpolation for coordinates
            interp_lon = lon1 + ratio * (lon2 - lon1)
            interp_lat = lat1 + ratio * (lat2 - lat1)
            
            # Apply smart altitude interpolation based on detected profile
            interp_alt = _interpolate_altitude_with_constraints(alt1, alt2, ratio, altitude_profile)
            
            interpolated_points.append((interp_lon, interp_lat, interp_alt))
    
    # Add the final point
    if coordinates:
        interpolated_points.append(coordinates[-1])
    
    return interpolated_points


def _determine_altitude_profile(alt1: float, alt2: float, segment_index: int, 
                              all_coordinates: List[Tuple[float, float, float]]) -> str:
    """
    Determine the altitude profile type for a segment based on altitude constraints
    
    Returns:
        'linear' - normal climb/descent
        'constrained' - altitude constraint detected (maintain alt1)
        'stepped' - step climb/descent pattern
    """
    alt_change = abs(alt2 - alt1)
    
    # For small altitude changes (< 100ft), treat as linear
    if alt_change < 100:
        return 'linear'
    
    # For moderate altitude changes (100-800ft), treat as normal climb/descent
    if alt_change <= 800:
        return 'linear'
    
    # For larger altitude changes (>800ft), check if this is a constraint situation
    if alt_change > 800:
        # Look at the pattern to detect true constraints
        # True constraint: altitude should stay constant for a while, then change
        
        # Check if we have enough waypoints to analyze the pattern
        if len(all_coordinates) >= segment_index + 3:
            # Get the next altitude after this segment
            next_alt = all_coordinates[segment_index + 2][2] if segment_index + 2 < len(all_coordinates) else alt2
            
            # Pattern detection for constraints:
            # If alt1 is much lower than alt2, and next_alt continues at alt2 or higher,
            # this suggests a normal step climb pattern, not a constraint
            
            # Special case: If we're climbing significantly (>800ft) and the next waypoint
            # continues at the same altitude, this is likely a step climb to a new cruise altitude
            if alt2 > alt1 and abs(next_alt - alt2) < 200:  # Next waypoint stays roughly the same
                return 'stepped'  # Step climb to new cruise altitude
            
            # True constraint detection: would need more complex pattern analysis
            # For now, treat large altitude changes as stepped climbs
            return 'stepped'
    
    return 'linear'


def _interpolate_altitude_with_constraints(alt1: float, alt2: float, ratio: float, 
                                         profile_type: str) -> float:
    """
    Interpolate altitude based on the determined profile type
    """
    if profile_type == 'constrained':
        # For constrained segments, maintain the lower altitude for most of the segment
        # Only start climbing in the last 20% of the segment
        if ratio < 0.8:
            return alt1  # Maintain constraint altitude
        else:
            # Climb in the last 20% of the segment
            climb_ratio = (ratio - 0.8) / 0.2  # Scale to 0-1 for the climbing portion
            return alt1 + climb_ratio * (alt2 - alt1)
    
    elif profile_type == 'stepped':
        # For stepped climbs, make the altitude change gradually in the first part of the segment
        # This is more realistic than jumping at the midpoint
        if ratio < 0.3:
            # First 30% of segment: start the climb
            climb_ratio = ratio / 0.3  # Scale to 0-1 for the climbing portion
            return alt1 + climb_ratio * (alt2 - alt1)
        else:
            # Last 70% of segment: maintain the new altitude
            return alt2
    
    else:  # 'linear'
        # Standard linear interpolation
        return alt1 + ratio * (alt2 - alt1)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    
    return c * r

def analyze_complete_flight_path():
    """Analyze complete flight path with interpolated points"""
    print("Enhanced Flight Path Airspace Analysis")
    print("=" * 60)
    
    # Initialize query engine
    engine = AirspaceQueryEngine('data/airspaces.db')
    
    # Parse flight path from KML
    waypoints = KMLFlightPathParser.parse_kml_coordinates('data/20250924_083633_LFXU-LFFU.kml')
    
    if not waypoints:
        print("Failed to parse flight coordinates from KML")
        return
    
    print(f"Original waypoints: {len(waypoints)}")
    
    # Interpolate flight path with points every 5km
    interpolated_points = interpolate_flight_path(waypoints, segment_distance_km=5.0)
    print(f"Interpolated points: {len(interpolated_points)} (every ~5km)")
    
    # Calculate total flight distance
    total_distance = 0
    for i in range(len(waypoints) - 1):
        lat1, lon1, alt1 = waypoints[i][1], waypoints[i][0], waypoints[i][2]
        lat2, lon2, alt2 = waypoints[i+1][1], waypoints[i+1][0], waypoints[i+1][2]
        total_distance += haversine_distance(lat1, lon1, lat2, lon2)
    
    print(f"Total flight distance: {total_distance:.1f} km")
    print()
    
    # Analyze airspaces along the flight path
    print("Analyzing airspaces along flight path...")
    print("-" * 60)
    
    crossed_airspaces = {}  # id -> airspace data
    airspace_crossings = []  # List of (point_index, airspace_data) tuples
    
    for i, (lon, lat, alt_ft) in enumerate(interpolated_points):
        if i % 10 == 0 or i == len(interpolated_points) - 1:  # Progress indicator
            print(f"Processing point {i+1}/{len(interpolated_points)}...")
        
        airspaces = engine.query_airspaces_for_point(lon, lat, alt_ft)
        
        for airspace in airspaces:
            airspace_id = airspace['id']
            if airspace_id not in crossed_airspaces:
                crossed_airspaces[airspace_id] = airspace
                print(f"  NEW: {airspace['name']} ({airspace['code_id']}) - {airspace['airspace_class']}")
                print(f"       Altitude: {airspace['lower_limit_ft']}-{airspace['upper_limit_ft']} ft")
                print(f"       At point: ({lon:.4f}, {lat:.4f}) {alt_ft:.0f} ft")
            
            airspace_crossings.append((i, airspace))
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    print(f"Total unique airspaces crossed: {len(crossed_airspaces)}")
    print(f"Total crossing points: {len(airspace_crossings)}")
    
    if crossed_airspaces:
        print("\nCrossed Airspaces:")
        print("-" * 40)
        for airspace_id, airspace in crossed_airspaces.items():
            # Count how many points are in this airspace
            points_in_airspace = sum(1 for _, a in airspace_crossings if a['id'] == airspace_id)
            
            print(f"• {airspace['name']} ({airspace['code_id']})")
            print(f"  Class: {airspace['airspace_class']}")
            print(f"  Type: {airspace.get('code_type', 'Unknown')}")
            print(f"  Altitude: {airspace['lower_limit_ft']}-{airspace['upper_limit_ft']} ft")
            print(f"  Flight points in airspace: {points_in_airspace}")
            print()
    else:
        print("No airspaces found along the flight path.")
        print("This could indicate:")
        print("- Flight path avoids controlled airspace (good VFR planning)")
        print("- Flight altitudes are between airspace layers")
        print("- Possible issues with airspace data or altitude references")
    
    # Show altitude distribution of flight
    altitudes = [alt for _, _, alt in interpolated_points]
    print(f"\nFlight altitude range: {min(altitudes):.0f} - {max(altitudes):.0f} ft")
    print(f"Average altitude: {sum(altitudes)/len(altitudes):.0f} ft")
    
    engine.close()

def test_specific_locations():
    """Test some specific locations known to have airspaces"""
    print("\nTesting specific locations with known airspaces...")
    print("-" * 60)
    
    engine = AirspaceQueryEngine('data/airspaces.db')
    
    # Test points near major airports
    test_points = [
        (2.5487, 49.0097, 2000, "Charles de Gaulle area"),
        (2.3794, 48.7233, 2000, "Orly area"),
        (2.3522, 48.8566, 1500, "Paris center"),
        (1.9417, 48.9986, 500, "LFXU at low altitude"),
    ]
    
    for lon, lat, alt, description in test_points:
        print(f"\nTesting {description}: ({lon:.4f}, {lat:.4f}) at {alt} ft")
        airspaces = engine.query_airspaces_for_point(lon, lat, alt)
        print(f"Found {len(airspaces)} airspace(s):")
        for airspace in airspaces[:5]:  # Show first 5
            print(f"  - {airspace['name']} ({airspace['code_id']})")
            print(f"    {airspace['lower_limit_ft']}-{airspace['upper_limit_ft']} ft")
    
    engine.close()

if __name__ == "__main__":
    analyze_complete_flight_path()
    test_specific_locations()