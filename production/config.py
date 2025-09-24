#!/usr/bin/env python3
"""
Configuration pour l'environnement de production
Chemins et paramètres pour le système d'extraction AIXM
"""

import os
from pathlib import Path

# Répertoire racine du projet
PROJECT_ROOT = Path(__file__).parent.parent
print(f"Répertoire racine du projet: {PROJECT_ROOT}")

# Chemins des données
DATA_DIR = PROJECT_ROOT / "data"
AIXM_FILE = DATA_DIR / "AIXM4.5_all_FR_OM_2025-10-02.xml"
DATABASE_FILE = DATA_DIR / "final_airspaces.db"

# Configuration de l'extraction
EXTRACTION_CONFIG = {
    "chunk_size": 1000,           # Taille des lots pour l'insertion
    "memory_limit_mb": 500,       # Limite mémoire pour le traitement
    "enable_debug": False,        # Mode debug (verbose)
    "validate_coordinates": True,  # Validation des coordonnées
}

# Configuration de l'API
API_CONFIG = {
    "default_limit": 1000,        # Limite par défaut des résultats
    "max_limit": 5000,           # Limite maximale des résultats
    "enable_caching": True,       # Cache des requêtes fréquentes
    "cache_ttl_seconds": 3600,   # Durée de vie du cache
}

# Validation des chemins
def validate_setup():
    """Valide que tous les fichiers nécessaires sont présents"""
    errors = []
    
    if not AIXM_FILE.exists():
        errors.append(f"Fichier AIXM manquant: {AIXM_FILE}")
    
    if not DATABASE_FILE.exists():
        errors.append(f"Base de données manquante: {DATABASE_FILE}")
    
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(exist_ok=True)
        print(f"Créé le répertoire data: {DATA_DIR}")
    
    if errors:
        print("ERREURS DE CONFIGURATION:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ Configuration validée - tous les fichiers sont présents")
    return True

if __name__ == "__main__":
    print("=== Configuration du Système d'Extraction AIXM ===")
    print(f"Fichier AIXM: {AIXM_FILE}")
    print(f"Base de données: {DATABASE_FILE}")
    print(f"Répertoire des données: {DATA_DIR}")
    
    if validate_setup():
        print("\n🚀 Système prêt à l'emploi")
    else:
        print("\n❌ Configuration incomplète - voir les erreurs ci-dessus")