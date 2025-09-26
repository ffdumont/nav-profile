#!/usr/bin/env python3
"""
Visualiseur graphique de profils d'altitude KML
Affiche les profils d'altitude sous forme de graphiques avec noms et altitudes des points
Utilise les unités aéronautiques : pieds pour les altitudes, miles nautiques pour les distances
"""

import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import math
from typing import List, Tuple, Optional
import argparse
import os
from aviation_utils import UnitConverter


class KMLViewer:
    """Classe pour visualiser les profils d'altitude des fichiers KML"""
    
    def __init__(self):
        self.points = []
        self.distances = []
        self.cumulative_distances = []
        
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcule la distance orthodromique entre deux points en NM"""
        lat1, lon1 = math.radians(lat1), math.radians(lon1)
        lat2, lon2 = math.radians(lat2), math.radians(lon2)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Rayon de la Terre en km, puis conversion en NM
        R_km = 6371.0
        distance_km = R_km * c
        return UnitConverter.km_to_nautical_miles(distance_km)
    
    def parse_kml(self, kml_file: str) -> bool:
        """
        Parse un fichier KML et extrait les points de navigation
        
        Returns:
            True si le parsing a réussi, False sinon
        """
        try:
            tree = ET.parse(kml_file)
            root = tree.getroot()
            
            # Gérer les namespaces KML
            namespaces = {'kml': 'http://www.opengis.net/kml/2.2'}
            
            # Extraire la ligne de navigation principale
            navigation_coords = None
            for linestring in root.findall('.//kml:LineString', namespaces):
                coords_elem = linestring.find('kml:coordinates', namespaces)
                if coords_elem is not None:
                    navigation_coords = coords_elem.text.strip()
                    break
            
            if not navigation_coords:
                print("Aucune ligne de navigation trouvée dans le fichier KML")
                return False
            
            # Parser les coordonnées
            coords_list = navigation_coords.split(',')
            temp_points = []
            for i in range(0, len(coords_list), 3):
                if i + 2 < len(coords_list):
                    try:
                        lon = float(coords_list[i])
                        lat = float(coords_list[i + 1])
                        alt = float(coords_list[i + 2])
                        temp_points.append((f"Point_{i//3}", lon, lat, alt))
                    except ValueError:
                        continue
            
            # Récupérer les noms des points depuis les Placemark
            placemark_names = []
            for placemark in root.findall('.//kml:Placemark', namespaces):
                name_elem = placemark.find('kml:name', namespaces)
                if name_elem is not None and name_elem.text != "Navigation":
                    placemark_names.append(name_elem.text)
            
            # Associer les noms aux points
            self.points = []
            for i, (_, lon, lat, alt) in enumerate(temp_points):
                name = placemark_names[i] if i < len(placemark_names) else f"Point_{i}"
                self.points.append((name, lon, lat, alt))
            
            # Calculer les distances
            self.distances = []
            self.cumulative_distances = [0.0]
            
            for i in range(1, len(self.points)):
                prev_point = self.points[i-1]
                curr_point = self.points[i]
                
                dist = self.calculate_distance(prev_point[2], prev_point[1], 
                                             curr_point[2], curr_point[1])
                self.distances.append(dist)
                self.cumulative_distances.append(self.cumulative_distances[-1] + dist)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors du parsing du fichier KML: {e}")
            return False
    
    def plot_altitude_profile(self, output_file: Optional[str] = None, title: Optional[str] = None):
        """
        Crée un graphique du profil d'altitude
        
        Args:
            output_file: Fichier de sortie pour sauvegarder le graphique (optionnel)
            title: Titre personnalisé du graphique (optionnel)
        """
        if not self.points:
            print("Aucun point à afficher")
            return
        
        # Configuration du graphique
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Données pour le graphique (convertir altitudes en pieds)
        distances = self.cumulative_distances
        altitudes = [UnitConverter.meters_to_feet(point[3]) for point in self.points]
        names = [point[0] for point in self.points]
        
        # Tracer la ligne d'altitude
        ax.plot(distances, altitudes, 'b-', linewidth=2, label='Profil d\'altitude')
        ax.fill_between(distances, 0, altitudes, alpha=0.3, color='lightblue')
        
        # Marquer les points
        ax.scatter(distances, altitudes, c='red', s=80, zorder=5, label='Waypoints')
        
        # Ajouter les noms et altitudes des points
        max_alt = max(altitudes)
        min_alt = min(altitudes)
        alt_range = max_alt - min_alt
        
        for i, (name, _, _, alt) in enumerate(self.points):
            dist = distances[i]
            
            # Stratégie de positionnement intelligent des étiquettes
            # Alterner haut/bas mais ajuster selon la densité locale
            position_above = True
            
            # Vérifier s'il y a des points proches pour éviter les chevauchements
            if i > 0 and i < len(self.points) - 1:
                # Calculer les pentes locales pour déterminer le meilleur placement
                prev_alt = altitudes[i-1]
                next_alt = altitudes[i+1]
                
                # Si on est sur une pente montante, placer en bas
                if alt > prev_alt and alt < next_alt:
                    position_above = False
                # Si on est sur un pic, placer en haut
                elif alt > prev_alt and alt > next_alt:
                    position_above = True
                # Si on est dans un creux, placer en bas
                elif alt < prev_alt and alt < next_alt:
                    position_above = False
                # Sinon alterner selon l'index
                else:
                    position_above = i % 2 == 0
            else:
                position_above = i % 2 == 0
            
            # Calculer la position de l'étiquette (offset fixe en pieds)
            offset_y = 150  # Offset fixe de 150 pieds
            
            if position_above:
                text_y = alt + offset_y
                va_text = 'bottom'
            else:
                text_y = alt - offset_y
                va_text = 'top'
            
            # Créer une boîte pour le texte (plus petite)
            bbox_props = dict(boxstyle="round,pad=0.2", facecolor='white', 
                            edgecolor='gray', alpha=0.9)
            
            # Nom du point avec altitude intégrée (alt est déjà en pieds)
            label_text = f"{name}\n{alt:.0f} ft"
            
            ax.annotate(label_text, (dist, alt), xytext=(dist, text_y),
                       ha='center', va=va_text, fontsize=8, fontweight='bold',
                       bbox=bbox_props,
                       arrowprops=dict(arrowstyle='->', color='gray', lw=0.8, alpha=0.6))
            
            # Distance cumulative (en bas du graphique)
            if i > 0:
                ax.text(dist, min_alt - alt_range * 0.1, f'{dist:.1f} NM', 
                       ha='center', va='top', fontsize=7, color='darkgreen', 
                       alpha=0.8)
        
        # Configuration des axes
        ax.set_xlabel('Distance cumulative (NM)', fontsize=12)
        ax.set_ylabel('Altitude (ft)', fontsize=12)
        
        # Titre
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        else:
            ax.set_title('Profil d\'altitude de la route de navigation', fontsize=14, fontweight='bold')
        
        # Grille
        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        
        # Légende
        ax.legend(loc='upper right')
        
        # Ajuster les marges pour les annotations (en pieds)
        y_margin = 300  # Marge fixe de 300 pieds
        y_min = min_alt - y_margin
        y_max = max_alt + y_margin
        ax.set_ylim(y_min, y_max)
        
        # Information sur les distances
        total_distance = distances[-1] if distances else 0
        info_text = f'Distance totale: {total_distance:.1f} NM'
        if len(self.distances) > 0:
            avg_segment = np.mean(self.distances)
            info_text += f' | Distance moyenne entre points: {avg_segment:.1f} NM'
        
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        # Ajuster la mise en page
        plt.tight_layout()
        
        # Sauvegarder ou afficher
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Graphique sauvegardé: {output_file}")
        else:
            plt.show()
        
        return fig, ax
    
    def plot_comparison(self, kml_files: List[str], labels: List[str] = None, 
                       output_file: Optional[str] = None):
        """
        Compare plusieurs fichiers KML dans le même graphique
        
        Args:
            kml_files: Liste des fichiers KML à comparer
            labels: Labels pour chaque fichier (optionnel)
            output_file: Fichier de sortie (optionnel)
        """
        if not kml_files:
            print("Aucun fichier à comparer")
            return
        
        fig, ax = plt.subplots(figsize=(16, 10))
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
        
        max_distance = 0
        all_altitudes = []
        
        for i, kml_file in enumerate(kml_files):
            # Créer une nouvelle instance pour chaque fichier
            viewer = KMLViewer()
            if not viewer.parse_kml(kml_file):
                continue
            
            # Données du profil (convertir en unités aéronautiques)
            distances = viewer.cumulative_distances
            altitudes = [UnitConverter.meters_to_feet(point[3]) for point in viewer.points]
            names = [point[0] for point in viewer.points]
            
            color = colors[i % len(colors)]
            label = labels[i] if labels and i < len(labels) else os.path.basename(kml_file)
            
            # Tracer la ligne
            ax.plot(distances, altitudes, color=color, linewidth=2, 
                   label=label, marker='o', markersize=4)
            
            # Marquer les points du premier fichier seulement pour éviter l'encombrement
            if i == 0:
                for j, (name, _, _, alt) in enumerate(viewer.points):
                    dist = distances[j]
                    
                    # Positionnement intelligent des étiquettes (offset fixe en pieds converti en points)
                    # 1 pied ≈ 0.72 points d'affichage en moyenne (approximation)
                    feet_to_points = 0.8
                    if j < len(viewer.points) // 2:
                        # Première moitié : étiquettes en haut
                        offset_feet = 60  # 60 pieds au-dessus
                        xytext_offset = (3, offset_feet * feet_to_points)
                        va = 'bottom'
                    else:
                        # Deuxième moitié : étiquettes en bas
                        offset_feet = 60  # 60 pieds en dessous
                        xytext_offset = (3, -offset_feet * feet_to_points)
                        va = 'top'
                    
                    alt_ft = UnitConverter.meters_to_feet(viewer.points[j][3])
                    ax.annotate(f'{name}\n{alt_ft:.0f} ft', (dist, alt), 
                              xytext=xytext_offset, textcoords='offset points',
                              fontsize=7, ha='left', va=va,
                              bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                                       alpha=0.8, edgecolor=color),
                              arrowprops=dict(arrowstyle='->', color=color, lw=0.6, alpha=0.6))
            
            max_distance = max(max_distance, distances[-1] if distances else 0)
            all_altitudes.extend(altitudes)
        
        # Configuration des axes
        ax.set_xlabel('Distance cumulative (NM)', fontsize=12)
        ax.set_ylabel('Altitude (ft)', fontsize=12)
        ax.set_title('Comparaison des profils d\'altitude', fontsize=14, fontweight='bold')
        
        # Grille et légende
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')
        
        # Ajuster les limites (marges en pieds)
        if all_altitudes:
            y_margin = 150  # Marge fixe de 150 pieds
            ax.set_ylim(min(all_altitudes) - y_margin, max(all_altitudes) + y_margin)
        
        plt.tight_layout()
        
        # Sauvegarder ou afficher
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Graphique de comparaison sauvegardé: {output_file}")
        else:
            plt.show()
        
        return fig, ax
    
    def print_summary(self):
        """Affiche un résumé textuel du profil"""
        if not self.points:
            print("Aucun point chargé")
            return
        
        print("=" * 60)
        print("RÉSUMÉ DU PROFIL DE NAVIGATION")
        print("=" * 60)
        
        total_distance = self.cumulative_distances[-1] if self.cumulative_distances else 0
        min_alt_m = min(point[3] for point in self.points)
        max_alt_m = max(point[3] for point in self.points)
        min_alt_ft = UnitConverter.meters_to_feet(min_alt_m)
        max_alt_ft = UnitConverter.meters_to_feet(max_alt_m)
        
        print(f"Nombre de waypoints: {len(self.points)}")
        print(f"Distance totale: {total_distance:.1f} NM")
        print(f"Altitude minimale: {min_alt_ft:.0f} ft")
        print(f"Altitude maximale: {max_alt_ft:.0f} ft")
        print(f"Dénivelé: {max_alt_ft - min_alt_ft:.0f} ft")
        
        print("\nDÉTAIL DES WAYPOINTS:")
        print("-" * 60)
        print(f"{'Point':<30} {'Distance (NM)':<12} {'Altitude (ft)':<12}")
        print("-" * 60)
        
        for i, (name, lon, lat, alt) in enumerate(self.points):
            dist = self.cumulative_distances[i] if i < len(self.cumulative_distances) else 0
            alt_ft = UnitConverter.meters_to_feet(alt)
            print(f"{name:<30} {dist:>11.1f} {alt_ft:>11.0f}")
        
        if len(self.distances) > 0:
            print("\nDISTANCES ENTRE WAYPOINTS:")
            print("-" * 40)
            for i, dist in enumerate(self.distances):
                start_point = self.points[i][0]
                end_point = self.points[i+1][0]
                print(f"{start_point} → {end_point}: {dist:.1f} NM")
        
        print("=" * 60)


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Visualiser les profils d\'altitude des fichiers KML')
    parser.add_argument('kml_files', nargs='+', help='Fichier(s) KML à visualiser')
    parser.add_argument('-o', '--output', help='Fichier de sortie pour sauvegarder le graphique')
    parser.add_argument('-c', '--compare', action='store_true', 
                       help='Comparer plusieurs fichiers dans le même graphique')
    parser.add_argument('-s', '--summary', action='store_true', 
                       help='Afficher un résumé textuel')
    parser.add_argument('--title', help='Titre personnalisé du graphique')
    
    args = parser.parse_args()
    
    if args.compare and len(args.kml_files) > 1:
        # Mode comparaison
        viewer = KMLViewer()
        labels = [os.path.splitext(os.path.basename(f))[0] for f in args.kml_files]
        viewer.plot_comparison(args.kml_files, labels, args.output)
    
    else:
        # Mode fichier unique
        kml_file = args.kml_files[0]
        
        viewer = KMLViewer()
        if not viewer.parse_kml(kml_file):
            return 1
        
        if args.summary:
            viewer.print_summary()
        
        # Déterminer le titre
        title = args.title if args.title else f'Profil d\'altitude - {os.path.basename(kml_file)}'
        
        viewer.plot_altitude_profile(args.output, title)
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())