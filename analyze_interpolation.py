#!/usr/bin/env python3
"""
Outil pour déterminer le niveau d'interpolation optimal pour la détection des traversées d'espaces aériens
"""

import sqlite3
import math
from typing import List, Tuple, Dict
from shapely.geometry import Point, Polygon, LineString
from navpro.core.spatial_query import KMLFlightPathParser

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in km"""
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat/2) * math.sin(dlat/2) + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(dlon/2) * math.sin(dlon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def get_airspace_geometries_along_route(waypoints: List[Tuple[float, float, float]], 
                                      corridor_km: float = 50) -> Dict[int, Polygon]:
    """Récupérer toutes les géométries d'espaces aériens le long de la route"""
    
    conn = sqlite3.connect('data/airspaces.db')
    conn.row_factory = sqlite3.Row
    
    # Create route bounding box with corridor
    lons = [w[0] for w in waypoints]
    lats = [w[1] for w in waypoints]
    
    min_lon, max_lon = min(lons) - corridor_km/111.32, max(lons) + corridor_km/111.32
    min_lat, max_lat = min(lats) - corridor_km/111.32, max(lats) + corridor_km/111.32
    
    print(f"Zone de recherche: {min_lat:.3f}°-{max_lat:.3f}°N, {min_lon:.3f}°-{max_lon:.3f}°E")
    
    # Get airspaces in the area
    cursor = conn.execute("""
        SELECT DISTINCT a.id, a.name, a.code_type
        FROM airspaces a
        JOIN airspace_borders ab ON a.id = ab.airspace_id
        JOIN border_vertices bv ON ab.id = bv.border_id
        WHERE bv.latitude BETWEEN ? AND ?
        AND bv.longitude BETWEEN ? AND ?
        AND a.code_type NOT IN ('SECTOR', 'FIR')
    """, (min_lat, max_lat, min_lon, max_lon))
    
    airspaces = {}
    
    for row in cursor:
        airspace_id = row['id']
        
        # Get vertices for this airspace
        vertex_cursor = conn.execute("""
            SELECT bv.longitude, bv.latitude
            FROM airspace_borders ab
            JOIN border_vertices bv ON ab.id = bv.border_id
            WHERE ab.airspace_id = ?
            ORDER BY bv.sequence_number
        """, (airspace_id,))
        
        vertices = [(r['longitude'], r['latitude']) for r in vertex_cursor]
        
        if len(vertices) >= 3:
            try:
                polygon = Polygon(vertices)
                if polygon.is_valid:
                    airspaces[airspace_id] = {
                        'polygon': polygon,
                        'name': row['name'],
                        'type': row['code_type']
                    }
            except Exception as e:
                print(f"Erreur création polygone pour {row['name']}: {e}")
    
    conn.close()
    print(f"Espaces aériens trouvés: {len(airspaces)}")
    return airspaces

def calculate_segment_complexity(segment_start: Tuple[float, float, float], 
                               segment_end: Tuple[float, float, float],
                               airspaces: Dict[int, Dict]) -> Dict:
    """Calculer la complexité d'un segment de route"""
    
    lon1, lat1, alt1 = segment_start
    lon2, lat2, alt2 = segment_end
    
    # Distance du segment
    segment_distance = haversine_distance(lat1, lon1, lat2, lon2)
    
    # Créer la ligne du segment
    segment_line = LineString([(lon1, lat1), (lon2, lat2)])
    
    # Analyser les intersections potentielles
    intersecting_airspaces = []
    closest_distances = []
    
    for airspace_id, airspace_data in airspaces.items():
        polygon = airspace_data['polygon']
        
        # Vérifier intersection
        if segment_line.intersects(polygon):
            intersecting_airspaces.append({
                'id': airspace_id,
                'name': airspace_data['name'],
                'type': airspace_data['type']
            })
        
        # Distance minimale au polygone
        distance = segment_line.distance(polygon) * 111.32  # Convert to km
        closest_distances.append(distance)
    
    # Calculer la plus petite dimension des espaces aériens intersectés
    min_airspace_dimension = float('inf')
    for airspace_id, airspace_data in airspaces.items():
        if any(a['id'] == airspace_id for a in intersecting_airspaces):
            polygon = airspace_data['polygon']
            bounds = polygon.bounds
            width = (bounds[2] - bounds[0]) * 111.32
            height = (bounds[3] - bounds[1]) * 111.32
            dimension = min(width, height)
            min_airspace_dimension = min(min_airspace_dimension, dimension)
    
    return {
        'segment_distance_km': segment_distance,
        'intersecting_airspaces': len(intersecting_airspaces),
        'intersecting_details': intersecting_airspaces,
        'min_distance_to_airspace_km': min(closest_distances) if closest_distances else float('inf'),
        'min_airspace_dimension_km': min_airspace_dimension if min_airspace_dimension != float('inf') else None
    }

def recommend_interpolation_distance(waypoints: List[Tuple[float, float, float]]) -> Dict:
    """Recommander la distance d'interpolation optimale"""
    
    print("🔍 Analyse de la complexité de la route...")
    
    # Obtenir les espaces aériens le long de la route
    airspaces = get_airspace_geometries_along_route(waypoints)
    
    segment_analyses = []
    max_recommended_distance = 0
    critical_segments = []
    
    # Analyser chaque segment
    for i in range(len(waypoints) - 1):
        segment_start = waypoints[i]
        segment_end = waypoints[i + 1]
        
        analysis = calculate_segment_complexity(segment_start, segment_end, airspaces)
        segment_analyses.append(analysis)
        
        print(f"\n📏 Segment {i+1}: {analysis['segment_distance_km']:.1f} km")
        
        if analysis['intersecting_airspaces'] > 0:
            print(f"   🎯 {analysis['intersecting_airspaces']} intersection(s) d'espaces aériens:")
            for detail in analysis['intersecting_details']:
                print(f"      - {detail['name']} ({detail['type']})")
            
            # Recommandation basée sur la plus petite dimension
            if analysis['min_airspace_dimension_km']:
                # Utiliser 1/10 de la plus petite dimension comme distance d'interpolation
                recommended = analysis['min_airspace_dimension_km'] / 10
                max_recommended_distance = max(max_recommended_distance, recommended)
                
                print(f"   📐 Plus petite dimension d'espace aérien: {analysis['min_airspace_dimension_km']:.1f} km")
                print(f"   💡 Distance d'interpolation recommandée: {recommended:.1f} km")
                
                critical_segments.append({
                    'segment': i+1,
                    'recommended_distance': recommended,
                    'reason': f"Intersections avec {analysis['intersecting_airspaces']} espace(s) aérien(s)"
                })
        
        else:
            print(f"   ✅ Aucune intersection d'espace aérien")
            if analysis['min_distance_to_airspace_km'] < 10:
                print(f"   ⚠️  Proche d'un espace aérien: {analysis['min_distance_to_airspace_km']:.1f} km")
    
    # Calculs statistiques
    total_distance = sum(a['segment_distance_km'] for a in segment_analyses)
    avg_segment_length = total_distance / len(segment_analyses)
    total_intersections = sum(a['intersecting_airspaces'] for a in segment_analyses)
    
    # Recommandation finale
    if max_recommended_distance > 0:
        final_recommendation = min(max_recommended_distance, avg_segment_length / 5)
    else:
        # Pas d'intersections détectées, utiliser 1/5 de la longueur moyenne des segments
        final_recommendation = avg_segment_length / 5
    
    # Arrondir à des valeurs pratiques
    if final_recommendation <= 0.5:
        final_recommendation = 0.5
    elif final_recommendation <= 1.0:
        final_recommendation = 1.0
    elif final_recommendation <= 2.0:
        final_recommendation = 2.0
    elif final_recommendation <= 5.0:
        final_recommendation = 5.0
    else:
        final_recommendation = 10.0
    
    return {
        'total_distance_km': total_distance,
        'average_segment_length_km': avg_segment_length,
        'total_intersections': total_intersections,
        'critical_segments': critical_segments,
        'recommended_interpolation_distance_km': final_recommendation,
        'current_default_distance_km': 5.0,
        'improvement_factor': 5.0 / final_recommendation if final_recommendation > 0 else 1.0
    }

def analyze_route_interpolation(kml_file: str):
    """Analyser et recommander l'interpolation pour un fichier KML"""
    
    print(f"🛩️ Analyse d'interpolation pour: {kml_file}")
    print("=" * 80)
    
    # Parse flight path
    waypoints = KMLFlightPathParser.parse_kml_coordinates(kml_file)
    if not waypoints:
        print("❌ Impossible de lire le fichier KML")
        return
    
    print(f"📍 Points de la route: {len(waypoints)}")
    
    # Analyser et recommander
    recommendation = recommend_interpolation_distance(waypoints)
    
    print("\n" + "=" * 80)
    print("📊 RÉSULTATS DE L'ANALYSE")
    print("=" * 80)
    
    print(f"Distance totale: {recommendation['total_distance_km']:.1f} km")
    print(f"Longueur moyenne des segments: {recommendation['average_segment_length_km']:.1f} km")
    print(f"Intersections d'espaces aériens détectées: {recommendation['total_intersections']}")
    
    print(f"\n🎯 RECOMMANDATION:")
    print(f"Distance d'interpolation optimale: {recommendation['recommended_interpolation_distance_km']:.1f} km")
    print(f"Distance par défaut actuelle: {recommendation['current_default_distance_km']:.1f} km")
    
    if recommendation['improvement_factor'] > 1:
        print(f"✨ Amélioration suggérée: {recommendation['improvement_factor']:.1f}x plus précis")
        print(f"⚡ Impact performance: {recommendation['improvement_factor']:.1f}x plus de points d'interpolation")
    else:
        print("✅ La distance par défaut semble appropriée")
    
    if recommendation['critical_segments']:
        print(f"\n🚨 SEGMENTS CRITIQUES ({len(recommendation['critical_segments'])}):")
        for seg in recommendation['critical_segments']:
            print(f"   Segment {seg['segment']}: {seg['recommended_distance']:.1f} km - {seg['reason']}")
    
    print(f"\n💡 UTILISATION:")
    distance = recommendation['recommended_interpolation_distance_km']
    print(f"Modifiez le paramètre d'interpolation à {distance} km dans le code navpro/core/interpolation.py")
    print(f"ou utilisez --sample-distance {distance} si l'option est disponible en CLI")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python analyze_interpolation.py <fichier.kml>")
        sys.exit(1)
    
    kml_file = sys.argv[1]
    analyze_route_interpolation(kml_file)