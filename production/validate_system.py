#!/usr/bin/env python3
"""
Script de validation finale du système d'extraction AIXM
Teste tous les composants et vérifie l'intégrité des données
"""

import sys
from pathlib import Path
import sqlite3

# Ajouter le répertoire de production au path
production_dir = Path(__file__).parent
sys.path.insert(0, str(production_dir))

from config import validate_setup, DATABASE_FILE, AIXM_FILE
from aixm_query_service import AirspaceQueryService

def test_database_integrity():
    """Teste l'intégrité de la base de données"""
    print("🔍 Test de l'intégrité de la base de données...")
    
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Compter les enregistrements
        cursor.execute("SELECT COUNT(*) FROM airspaces")
        airspace_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM airspace_borders")
        border_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM border_vertices")
        vertex_count = cursor.fetchone()[0]
        
        # Vérifier la cohérence
        cursor.execute("SELECT COUNT(*) FROM airspaces WHERE has_geometry = 1")
        geometry_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"  ✅ Espaces aériens: {airspace_count:,}")
        print(f"  ✅ Bordures: {border_count:,}")
        print(f"  ✅ Sommets: {vertex_count:,}")
        print(f"  ✅ Avec géométrie: {geometry_count:,} ({geometry_count/airspace_count*100:.1f}%)")
        
        # Validation des attentes
        if airspace_count >= 5000 and vertex_count >= 15000 and geometry_count/airspace_count >= 0.7:
            print("  ✅ Intégrité des données VALIDÉE")
            return True
        else:
            print("  ❌ Données insuffisantes ou incomplètes")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur de base de données: {e}")
        return False

def test_query_service():
    """Teste le service de requête"""
    print("\n🔍 Test du service de requête...")
    
    try:
        service = AirspaceQueryService()
        
        # Test des statistiques
        stats = service.get_statistics()
        print(f"  ✅ Statistiques récupérées: {stats['total_airspaces']} espaces")
        
        # Test de recherche par type
        tma_results = service.search_airspaces(airspace_type='TMA')
        print(f"  ✅ Recherche TMA: {len(tma_results)} résultats")
        
        # Test de recherche géographique (région parisienne)
        paris_results = service.search_airspaces_in_area(48.5, 2.0, 49.0, 2.8)
        print(f"  ✅ Recherche géographique Paris: {len(paris_results)} résultats")
        
        # Test d'export de géométrie
        if tma_results:
            first_tma_id = tma_results[0]['gml_id']
            geom = service.export_geometries_as_wkt([first_tma_id])
            if geom:
                print(f"  ✅ Export géométrie WKT: {len(geom)} géométries")
            else:
                print("  ⚠️  Export géométrie: aucune géométrie trouvée")
        
        print("  ✅ Service de requête VALIDÉ")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur du service: {e}")
        return False

def test_coordinate_accuracy():
    """Teste la précision des coordonnées"""
    print("\n🔍 Test de la précision des coordonnées...")
    
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Vérifier les limites géographiques de la France
        cursor.execute("""
            SELECT 
                MIN(latitude) as min_lat,
                MAX(latitude) as max_lat,
                MIN(longitude) as min_lon,
                MAX(longitude) as max_lon,
                COUNT(*) as total_points
            FROM border_vertices
        """)
        
        min_lat, max_lat, min_lon, max_lon, total_points = cursor.fetchone()
        
        # Coordonnées approximatives de la France métropolitaine
        # Latitude: 41°N - 51°N, Longitude: -5°W - 10°E
        france_valid = (
            41 <= min_lat <= 51 and
            41 <= max_lat <= 51 and
            -5 <= min_lon <= 10 and
            -5 <= max_lon <= 10
        )
        
        print(f"  📍 Étendue géographique:")
        print(f"    Latitude: {min_lat:.3f}° à {max_lat:.3f}°")
        print(f"    Longitude: {min_lon:.3f}° à {max_lon:.3f}°")
        print(f"    Points total: {total_points:,}")
        
        if france_valid:
            print("  ✅ Coordonnées cohérentes avec la France")
        else:
            print("  ⚠️  Coordonnées hors limites attendues")
        
        # Vérifier les coordonnées invalides
        cursor.execute("""
            SELECT COUNT(*) FROM border_vertices 
            WHERE latitude < -90 OR latitude > 90 
               OR longitude < -180 OR longitude > 180
        """)
        
        invalid_count = cursor.fetchone()[0]
        if invalid_count == 0:
            print("  ✅ Aucune coordonnée invalide détectée")
        else:
            print(f"  ❌ {invalid_count} coordonnées invalides trouvées")
        
        conn.close()
        return france_valid and invalid_count == 0
        
    except Exception as e:
        print(f"  ❌ Erreur de validation des coordonnées: {e}")
        return False

def main():
    """Validation complète du système"""
    print("🚀 === VALIDATION FINALE DU SYSTÈME AIXM ===\n")
    
    # Tests de configuration
    config_ok = validate_setup()
    
    # Tests techniques
    db_ok = test_database_integrity()
    service_ok = test_query_service()
    coord_ok = test_coordinate_accuracy()
    
    # Résumé final
    print("\n" + "="*50)
    print("📊 RÉSUMÉ DE VALIDATION:")
    print(f"  Configuration: {'✅ OK' if config_ok else '❌ ÉCHEC'}")
    print(f"  Base de données: {'✅ OK' if db_ok else '❌ ÉCHEC'}")
    print(f"  Service requête: {'✅ OK' if service_ok else '❌ ÉCHEC'}")
    print(f"  Coordonnées: {'✅ OK' if coord_ok else '❌ ÉCHEC'}")
    
    all_ok = all([config_ok, db_ok, service_ok, coord_ok])
    
    print("\n🎯 STATUT FINAL:")
    if all_ok:
        print("🎉 SYSTÈME VALIDÉ - Prêt pour la production !")
        print("\nUtilisation:")
        print("  python demo_aixm_service.py  # Démonstration complète")
        print("  python config.py             # Vérification configuration")
        return 0
    else:
        print("❌ VALIDATION ÉCHOUÉE - Voir les erreurs ci-dessus")
        return 1

if __name__ == "__main__":
    sys.exit(main())