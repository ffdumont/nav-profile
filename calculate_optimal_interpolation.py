#!/usr/bin/env python3
"""
Calculer la distance d'interpolation optimale basée sur les points d'intersection
"""

import math

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

def calculate_optimal_interpolation():
    """Calculer la distance d'interpolation optimale"""
    
    print("📐 CALCUL DE L'INTERPOLATION OPTIMALE")
    print("=" * 60)
    
    # Points critiques de notre route
    bevro = (2.186213, 47.605899, 2900)
    lffu = (2.376944, 46.871111, 1548)
    
    # Points d'intersection avec AVORD 1.1
    intersection_1 = (2.276779841542191, 47.25699175176503)
    intersection_2 = (2.282769408916384, 47.23391704323968)
    
    print("🛩️ POINTS DE LA ROUTE:")
    print(f"  BEVRO: ({bevro[0]:.6f}, {bevro[1]:.6f})")
    print(f"  LFFU: ({lffu[0]:.6f}, {lffu[1]:.6f})")
    
    # Distance totale BEVRO-LFFU
    total_distance = haversine_distance(bevro[1], bevro[0], lffu[1], lffu[0])
    print(f"  Distance totale: {total_distance:.2f} km")
    
    print("\n🎯 POINTS D'INTERSECTION AVORD 1.1:")
    print(f"  Point 1: ({intersection_1[0]:.6f}, {intersection_1[1]:.6f})")
    print(f"  Point 2: ({intersection_2[0]:.6f}, {intersection_2[1]:.6f})")
    
    # Distance BEVRO -> Point d'intersection 1
    dist_to_int1 = haversine_distance(bevro[1], bevro[0], intersection_1[1], intersection_1[0])
    print(f"  Distance BEVRO -> Intersection 1: {dist_to_int1:.2f} km")
    
    # Distance entre les points d'intersection
    dist_between_intersections = haversine_distance(
        intersection_1[1], intersection_1[0], 
        intersection_2[1], intersection_2[0]
    )
    print(f"  Distance entre intersections: {dist_between_intersections:.2f} km")
    
    # Distance Point d'intersection 2 -> LFFU
    dist_int2_to_lffu = haversine_distance(intersection_2[1], intersection_2[0], lffu[1], lffu[0])
    print(f"  Distance Intersection 2 -> LFFU: {dist_int2_to_lffu:.2f} km") 
    
    print("\n💡 RECOMMANDATIONS D'INTERPOLATION:")
    
    # Pour détecter les intersections, il faut une interpolation plus fine que la plus petite distance critique
    min_critical_distance = min(dist_between_intersections, 
                               dist_to_int1 if dist_to_int1 < 10 else float('inf'),
                               dist_int2_to_lffu if dist_int2_to_lffu < 10 else float('inf'))
    
    recommended_distances = [
        dist_between_intersections / 5,  # 5 points dans la zone critique
        dist_between_intersections / 3,  # 3 points dans la zone critique
        dist_between_intersections / 2,  # 2 points dans la zone critique
    ]
    
    print(f"  Distance critique minimale: {min_critical_distance:.2f} km")
    print(f"  Pour 5 points dans la zone: {recommended_distances[0]:.2f} km")
    print(f"  Pour 3 points dans la zone: {recommended_distances[1]:.2f} km") 
    print(f"  Pour 2 points dans la zone: {recommended_distances[2]:.2f} km")
    
    # Recommandation finale
    final_recommendation = min(recommended_distances[1], 1.0)  # Max 1km
    
    print(f"\n🎯 RECOMMANDATION FINALE: {final_recommendation:.1f} km")
    print(f"  (vs 5.0 km par défaut = amélioration x{5.0/final_recommendation:.1f})")
    
    # Test de validation
    print(f"\n✅ VALIDATION:")
    num_points_with_5km = int(total_distance / 5.0) + 1
    num_points_with_rec = int(total_distance / final_recommendation) + 1
    
    print(f"  Points générés avec 5.0 km: {num_points_with_5km}")
    print(f"  Points générés avec {final_recommendation:.1f} km: {num_points_with_rec}")
    print(f"  Coût computationnel: x{num_points_with_rec/num_points_with_5km:.1f}")

if __name__ == "__main__":
    calculate_optimal_interpolation()