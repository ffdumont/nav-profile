#!/usr/bin/env python3
"""
Correcteur spécialisé pour le vol LFXU-LFFU avec corrections manuelles
"""

from kml_altitude_corrector import KMLAltitudeCorrector
from aviation_utils import UnitConverter


def create_lfxu_lffu_corrector():
    """Crée un correcteur spécialisé pour le vol LFXU-LFFU"""
    corrector = KMLAltitudeCorrector()
    
    # Corrections spécifiques pour ce vol :
    # BEVRO devrait rester à 3100 ft (même altitude que LFFF/OE) au lieu de descendre à 2900 ft
    corrector.set_cruise_altitude("BEVRO", UnitConverter.feet_to_meters(3100))
    
    print("Correcteur spécialisé LFXU-LFFU créé avec les corrections suivantes:")
    print("- BEVRO: altitude de croisière forcée à 3100 ft (au lieu de 2900 ft)")
    
    return corrector


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python lfxu_lffu_corrector.py <fichier_kml_input> [fichier_kml_output]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace(".kml", "_corrected_manual.kml")
    
    # Créer le correcteur spécialisé
    corrector = create_lfxu_lffu_corrector()
    
    # Corriger le fichier
    corrector.correct_kml_file(input_file, output_file)
    
    print(f"\nCorrection terminée. Fichier sauvegardé: {output_file}")
    
    # Proposer une analyse comparative
    print("\nPour comparer les profils, exécutez:")
    print(f'python kml_analyzer.py --compare "{input_file}" "{output_file}" -o comparison.png')


if __name__ == "__main__":
    main()