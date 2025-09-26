#!/usr/bin/env python3
"""
Programme utilitaire pour analyser et comparer les profils KML
"""

from kml_altitude_viewer import KMLViewer
from kml_altitude_corrector import KMLAltitudeCorrector
from aviation_utils import UnitConverter
import matplotlib.pyplot as plt


def analyze_kml_profile(kml_file):
    """Analyse détaillée d'un profil KML"""
    viewer = KMLViewer()
    if not viewer.parse_kml(kml_file):
        return
    
    print(f"\n{'='*80}")
    print(f"ANALYSE DÉTAILLÉE DU PROFIL: {kml_file}")
    print(f"{'='*80}")
    
    for i, (name, lon, lat, alt_m) in enumerate(viewer.points):
        alt_ft = UnitConverter.meters_to_feet(alt_m)
        
        if i > 0:
            prev_point = viewer.points[i-1]
            prev_alt_ft = UnitConverter.meters_to_feet(prev_point[3])
            alt_change = alt_ft - prev_alt_ft
            
            dist_nm = viewer.distances[i-1] if i-1 < len(viewer.distances) else 0
            
            status = "STABLE"
            if alt_change > 50:
                status = f"MONTÉE +{alt_change:.0f} ft"
            elif alt_change < -50:
                status = f"DESCENTE {alt_change:.0f} ft"
            
            print(f"{i:2d}. {name:<30} {alt_ft:5.0f} ft  {status:<20} (dist: {dist_nm:.1f} NM)")
        else:
            print(f"{i:2d}. {name:<30} {alt_ft:5.0f} ft  DÉPART")


def compare_profiles(original_file, corrected_file, output_image=None):
    """Compare deux profils KML"""
    viewer = KMLViewer()
    
    files = [original_file, corrected_file]
    labels = ["Original (SDVFR)", "Corrigé"]
    
    viewer.plot_comparison(files, labels, output_image)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyser et comparer les profils KML')
    parser.add_argument('--analyze', help='Analyser un fichier KML en détail')
    parser.add_argument('--compare', nargs=2, help='Comparer deux fichiers KML')
    parser.add_argument('-o', '--output', help='Fichier de sortie pour la comparaison')
    
    args = parser.parse_args()
    
    if args.analyze:
        analyze_kml_profile(args.analyze)
    
    if args.compare:
        compare_profiles(args.compare[0], args.compare[1], args.output)


if __name__ == "__main__":
    main()