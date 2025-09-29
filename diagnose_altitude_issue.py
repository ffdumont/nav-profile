#!/usr/bin/env python3
"""
Diagnostic détaillé du problème de détection de la TMA AVORD 1.1
"""

import sqlite3

def analyze_avord_altitude_issue():
    """Analyser le problème d'altitude avec la TMA AVORD 1.1"""
    
    conn = sqlite3.connect('data/airspaces.db')
    conn.row_factory = sqlite3.Row
    
    # Get AVORD 1.1 details with altitude limits
    cursor = conn.execute("""
        SELECT a.id, a.name, a.code_type, a.airspace_class,
               vl.lower_limit_ft, vl.upper_limit_ft, vl.lower_limit_ref, vl.upper_limit_ref
        FROM airspaces a
        LEFT JOIN vertical_limits vl ON a.id = vl.airspace_id
        WHERE a.name LIKE 'AVORD 1.1%'
    """)
    
    print("🔍 DÉTAILS DE LA TMA AVORD 1.1:")
    print("=" * 60)
    
    for row in cursor:
        print(f"ID: {row['id']}")
        print(f"Nom: {row['name']}")
        print(f"Type: {row['code_type']}")
        print(f"Classe: {row['airspace_class']}")
        print(f"Limite inférieure: {row['lower_limit_ft']} ft (ref: {row['lower_limit_ref']})")
        print(f"Limite supérieure: {row['upper_limit_ft']} ft (ref: {row['upper_limit_ref']})")
        print()
    
    # Analyze the altitude of our flight in the AVORD area
    print("🛩️ ALTITUDE DU VOL DANS LA ZONE AVORD:")
    print("=" * 60)
    
    # From our corrected profile, the critical points are:
    critical_points = [
        ("BEVRO", 2.186213, 47.605899, 2900),  # Point 13
        ("Descent_BEVRO_2900", 2.357755, 46.945038, 2900),  # Point 14 (approximate)
        ("LFFU", 2.376944, 46.871111, 1548)  # Point 15
    ]
    
    for name, lon, lat, alt_ft in critical_points:
        print(f"{name}: ({lon:.6f}, {lat:.6f}) à {alt_ft} ft")
        
        # Check if this altitude is within AVORD 1.1 range
        if 2100 <= alt_ft <= 6500:
            status = "✅ DANS LA PLAGE"
        else:
            status = "❌ HORS PLAGE"
        
        print(f"  Altitude: {alt_ft} ft {status} (AVORD 1.1: 2100-6500 ft)")
        print()
    
    # Test specific points that showed "1 final matches" in the logs
    print("🎯 TEST DES POINTS CRITIQUES:")
    print("=" * 60)
    
    from navpro.core.spatial_query import AirspaceQueryEngine
    engine = AirspaceQueryEngine('data/airspaces.db')
    
    # Points where we saw "1 final matches" in the debug output
    test_points = [
        (2.2338, 47.4225, 2900),  # First point with matches
        (2.2825, 47.2349, 2900),  # Around peak crossing area
        (2.2985, 47.1734, 2900),  # Last point with matches
    ]
    
    for i, (lon, lat, alt) in enumerate(test_points, 1):
        print(f"Point test {i}: ({lon:.6f}, {lat:.6f}) à {alt} ft")
        
        airspaces = engine.query_airspaces_for_point(lon, lat, alt)
        
        avord_found = False
        for airspace in airspaces:
            if "avord" in airspace['name'].lower():
                avord_found = True
                print(f"  ✅ TROUVÉ: {airspace['name']} ({airspace['code_id']})")
                print(f"     Altitude airspace: {airspace['lower_limit_ft']}-{airspace['upper_limit_ft']} ft")
                print(f"     Références: {airspace.get('lower_limit_ref', 'N/A')}-{airspace.get('upper_limit_ref', 'N/A')}")
        
        if not avord_found:
            print(f"  ❌ AVORD 1.1 non trouvé dans les résultats")
        
        print(f"  Autres espaces trouvés: {len(airspaces)}")
        for airspace in airspaces[:3]:  # Show first 3
            if "avord" not in airspace['name'].lower():
                print(f"    - {airspace['name']} ({airspace['code_id']})")
        print()
    
    engine.close()
    conn.close()

def test_altitude_conversion():
    """Tester la conversion des altitudes Flight Level"""
    print("🔧 TEST DE CONVERSION DES ALTITUDES:")
    print("=" * 60)
    
    # Common Flight Level conversions
    conversions = [
        ("FL065", 6500),
        ("FL21", 2100),
        ("2100FT", 2100),
        ("6500FT", 6500),
    ]
    
    for original, expected_ft in conversions:
        print(f"{original} -> {expected_ft} ft")
    
    print("\n💡 Notre vol à 2900 ft devrait être détecté dans AVORD 1.1 (2100-6500 ft)")

if __name__ == "__main__":
    analyze_avord_altitude_issue()
    print("\n" + "=" * 80)
    test_altitude_conversion()